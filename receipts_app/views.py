import os
import uuid
import re
from datetime import datetime
from django.conf import settings
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import ReceiptFile, Receipt
from .serializers import ReceiptFileUploadSerializer, ReceiptSerializer
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

# Tesseract path (Windows-specific, change as per your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\niles\OneDrive\Desktop\Assignment\tesseract.exe'

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploaded_receipts')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------ Upload PDF ------------------
class UploadReceiptView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not uploaded_file.name.endswith('.pdf'):
            return Response({"error": "Only PDF files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        safe_file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, safe_file_name)

        with open(file_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        receipt_file = ReceiptFile.objects.create(
            file_name=safe_file_name,
            file_path=file_path,
            created_at=now(),
            updated_at=now(),
            file_size=uploaded_file.size
        )

        serializer = ReceiptFileUploadSerializer(receipt_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ------------------ Validate PDF ------------------
class ValidateReceiptView(APIView):
    def post(self, request):
        file_name = request.data.get('file_name')
        if not file_name:
            return Response({"error": "file_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receipt_file = ReceiptFile.objects.get(file_name=file_name)
        except ReceiptFile.DoesNotExist:
            return Response({"error": "File not found in database"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(receipt_file.file_path, 'rb') as f:
                PyPDF2.PdfReader(f)
            receipt_file.is_valid = True
            receipt_file.invalid_reason = ""
        except Exception as e:
            receipt_file.is_valid = False
            receipt_file.invalid_reason = str(e)

        receipt_file.save()
        return Response({
            "file_name": receipt_file.file_name,
            "is_valid": receipt_file.is_valid,
            "invalid_reason": receipt_file.invalid_reason
        }, status=status.HTTP_200_OK)

# ------------------ OCR & Extract Receipt Info ------------------
class ProcessReceiptView(APIView):
    def post(self, request):
        file_name = request.data.get("file_name")
        if not file_name:
            return Response({"error": "file_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receipt_file = ReceiptFile.objects.get(file_name=file_name)
        except ReceiptFile.DoesNotExist:
            return Response({"error": "File not found in database"}, status=status.HTTP_404_NOT_FOUND)

        if not receipt_file.is_valid:
            return Response({"error": "File is not a valid PDF"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            images = convert_from_path(receipt_file.file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)

            if not text.strip():
                return Response({"error": "OCR failed to extract text"}, status=status.HTTP_400_BAD_REQUEST)

            lines = [line.strip() for line in text.split('\n') if line.strip()]

            # Extract merchant
            merchant_match = re.search(r"(?:Merchant|Store|Vendor)[:\-]?\s*(.*)", text, re.IGNORECASE)
            merchant_name = merchant_match.group(1).strip() if merchant_match else (lines[0] if lines else "Unknown")

            # Extract total amount
            total_match = re.search(r"(Total|Amount)[:\-]?\s*\$?([\d.,]+)", text, re.IGNORECASE)
            total_amount = float(total_match.group(2).replace(',', '')) if total_match else 0.0

            # Extract date
            date_match = re.search(
                r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}|\d{2}-[A-Za-z]{3}-\d{4}|\d{2}\.\d{2}\.\d{4}|[A-Za-z]{3,9} \d{1,2}, \d{4})",
                text)
            purchased_at = None
            if date_match:
                raw_date = date_match.group(1)
                for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y-%m-%d", "%d.%m.%Y", "%b %d, %Y", "%B %d, %Y"):
                    try:
                        purchased_at = datetime.strptime(raw_date, fmt)
                        break
                    except ValueError:
                        continue

            # Extract currency
            currency_match = re.search(r'(\$|€|₹|£)', text)
            currency = currency_match.group(1) if currency_match else "Unknown"

            # Extract payment method
            payment_keywords = ['credit card', 'debit card', 'cash', 'upi', 'google pay', 'phonepe', 'paytm', 'wallet', 'net banking', 'bank transfer', 'cheque', 'paypal', 'credit', 'debit', 'cash on delivery', 'cod', 'emi', 'installment', 'cash', 'gift card', 'voucher', 'loyalty points', 'rewards points', 'cryptocurrency']
            payment_method = 'Unknown'
            for keyword in payment_keywords:
                if keyword.lower() in text.lower():
                    payment_method = keyword.title()
                    break

            # Save receipt
            receipt = Receipt.objects.create(
                merchant_name=merchant_name,
                total_amount=total_amount,
                purchased_at=purchased_at,
                file_path=receipt_file.file_path,
                currency=currency,
                payment_method=payment_method
            )

            receipt_file.is_processed = True
            receipt_file.save()

            return Response({
                "message": "Receipt processed successfully",
                "merchant": receipt.merchant_name,
                "amount": receipt.total_amount,
                "currency": receipt.currency,
                "payment_method": receipt.payment_method,
                "date": receipt.purchased_at
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------ View All Receipts ------------------
class ReceiptListView(ListAPIView):
    queryset = Receipt.objects.all().order_by('-created_at')
    serializer_class = ReceiptSerializer

# ------------------ View Receipt by ID ------------------
class ReceiptDetailView(RetrieveAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    lookup_field = 'id'

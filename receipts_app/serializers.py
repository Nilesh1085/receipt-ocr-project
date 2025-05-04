from rest_framework import serializers
from .models import ReceiptFile, Receipt

class ReceiptFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptFile
        fields = ['file_name', 'file_path']

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
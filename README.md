# OCR Receipt Processing API – Django Project

## 📌 Project Description

This Django-based REST API processes uploaded receipt PDFs, extracts information using Tesseract OCR, and stores details like Merchant Name, Date, and Total Amount into a SQLite database.

---

## 🏗️ Project Structure

- `receipt_project/`: Django project files  
- `receipts_app/`: OCR logic, models, views, serializers  
- `uploaded_receipts/`: Folder containing uploaded PDFs  
- `db.sqlite3`: Database with extracted receipt data  

---

## 📦 Requirements

- **Python 3.11.x**
- **Required Packages:**
    ```plaintext
    asgiref==3.8.1
    Django==5.2
    djangorestframework==3.16.0
    packaging==25.0
    pdf2image==1.17.0
    pillow==11.2.1
    PyPDF2==3.0.1
    pytesseract==0.3.13
    sqlparse==0.5.3
    tzdata==2025.2
    ```

- **Django Rest Framework** 3.x  
- **SQLite** (default database for development)

---

## ⚙️ Setup and Run Instructions

Follow the steps below to set up the project on your local machine.

1. **Clone the Repository**  
    ```bash
    git clone https://github.com/your-username/receipt_project.git
    cd receipt_project
    ```

2. **Create and Activate Virtual Environment**  
    ```bash
    python -m venv myenv
    myenv\scripts\activate 
    ```

3. **Install Dependencies**  
    ```bash
    pip install -r requirements.txt
    ```

4. **Run Migrations & Start Server**  
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

5. **Access the Application**  
    Open your browser and navigate to:  
    ```
    http://127.0.0.1:8000
    ```

---

## 🧪 API Usage (Test with Postman)

You can use Postman to test the following endpoints after running the server on `http://127.0.0.1:8000/`.

---

### 🔹 1. Upload Receipt PDF

**Endpoint:**  
`POST /upload/`

**URL:**  
`http://127.0.0.1:8000/upload/`

**Request Type:**  
`form-data`

**Key:** `file`  
**Value:** (Upload a PDF receipt)

✅ Sample Successful Response:

```json
{
  "file_name": "your_uploaded_file.pdf",
  "file_path": "your_file_path"
}
```

---

### 🔹 2. Validate Receipt

After uploading, validate the PDF content.

**Endpoint:**  
`POST /validate/`

**URL:**  
`http://127.0.0.1:8000/validate/`

**Request Body:**  
(JSON format)

```json
{
  "file_name": "your_uploaded_file.pdf"
}
```

✅ Sample Successful Response:

```json
{
  "file_name": "your_uploaded_file.pdf",
  "is_valid": true,
  "invalid_reason": ""
}
```

❌ Sample Failure Response (e.g., corrupted file):

```json
{
  "file_name": "bad_file.pdf",
  "is_valid": false,
  "invalid_reason": "PdfReadError: ... corrupted file ..."
}
```

---

### 🔹 3. Process Receipt via OCR

After validating the PDF content.

**Endpoint:**  
`POST /process/`

**URL:**  
`http://127.0.0.1:8000/process/`

**Request Body:**  
(JSON format)

```json
{
   "file_name": "your_uploaded_file.pdf"
}
```

✅ Sample Successful Response:

```json
{
  "message": "Receipt processed successfully",
  "merchant": "Supermart",
  "amount": 89.50,
  "date": "2024-11-20T00:00:00Z"
}
```

---

### 🔹 4. Receipt Retrieval APIs 

**Endpoint:**  
`GET /receipts`

**URL:**  
`http://127.0.0.1:8000/receipts/`

✅ Sample Successful Response:

```json
[
    {
        "id": 25,
        "purchased_at": "2024-08-01T00:00:00Z",
        "merchant_name": "Amazon",
        "total_amount": "191.92",
        "file_path": "C:\\Users\\niles\\OneDrive\\Desktop\\Assignment\\receipt_project\\uploaded_receipts\\8f775375-4675-4b5b-aa92-bc9ea92e88e2_1)receipt.pdf",
        "payment_method": "Credit Card",
        "currency": "$",
        "created_at": "2025-05-03T15:53:46.283694Z",
        "updated_at": "2025-05-03T15:53:46.283694Z"
    },
    {
        "id": 24,
        "purchased_at": "2024-08-02T00:00:00Z",
        "merchant_name": "Walmart",
        "total_amount": "194.48",
        "file_path": "C:\\Users\\niles\\OneDrive\\Desktop\\Assignment\\receipt_project\\uploaded_receipts\\a4dbd32e-55c2-43a9-8563-226ffb07e68a_2)receipt.pdf",
        "payment_method": "Cash",
        "currency": "$",
        "created_at": "2025-05-03T15:53:04.620753Z",
        "updated_at": "2025-05-03T15:53:04.620753Z"
    },
    {
        "id": 23,
        "purchased_at": "2024-08-03T00:00:00Z",
        "merchant_name": "Target",
        "total_amount": "208.62",
        "file_path": "C:\\Users\\niles\\OneDrive\\Desktop\\Assignment\\receipt_project\\uploaded_receipts\\48eebe64-0271-4a95-811b-c0804e64b545_3)receipt.pdf",
        "payment_method": "Credit Card",
        "currency": "$",
        "created_at": "2025-05-03T15:52:09.202735Z",
        "updated_at": "2025-05-03T15:52:09.202735Z"
    }
]
```

---

### 🔹 5. Get a specific receipt by ID

**Endpoint:**  
`GET /receipts/1`

**URL:**  
`http://127.0.0.1:8000/receipts/18/`

✅ Sample Successful Response:

```json
{
    "id": 18,
    "purchased_at": "2024-08-08T00:00:00Z",
    "merchant_name": "Adidas",
    "total_amount": "136.12",
    "file_path": "C:\\Users\\niles\\OneDrive\\Desktop\\Assignment\\receipt_project\\uploaded_receipts\\68dd22af-9b75-4603-83e5-074e014a0627_8)receipt.pdf",
    "payment_method": "Upi",
    "currency": "$",
    "created_at": "2025-05-03T15:46:05.471417Z",
    "updated_at": "2025-05-03T15:46:05.471417Z"
}
```

---
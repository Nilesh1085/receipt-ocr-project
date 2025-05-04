from django.db import models

# Receipt File Table
class ReceiptFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=1024)
    is_valid = models.BooleanField(default=False)
    invalid_reason = models.TextField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # Store file size
    # Add more fields as needed

    def __str__(self):
        return self.file_name

# Receipt Table for extracted data
class Receipt(models.Model):
    purchased_at = models.DateTimeField(null=True, blank=True)  # Date and time of purchase
    merchant_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    file_path = models.CharField(max_length=1024)
    payment_method = models.CharField(max_length=50, null=True, blank=True)  # Add payment method
    currency = models.CharField(max_length=10, null=True, blank=True)  # Add currency field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # def __str__(self):
    #     return self.merchant_name

    def __str__(self):
        return f"{self.merchant_name} - {self.total_amount}"

from django.db import models
from supplier.models import Order
from sku.models import ProductSKU

class Tailor(models.Model):
    name = models.CharField(max_length=255)
    specialties = models.CharField(max_length=255, help_text="e.g., Bridal, Suits")
    is_available = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    chest = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Alteration(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RECEIVED', 'Received'),
        ('IN_PROGRESS', 'In Progress'),
        ('READY', 'Ready for Pickup'),
        ('COMPLETED', 'Completed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='alterations')
    tailor = models.ForeignKey(Tailor, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.ForeignKey(ProductSKU, on_delete=models.CASCADE, null=True, blank=True)
    outfit_type = models.CharField(max_length=50)
    number_of_outfits = models.PositiveIntegerField(default=1)
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    predicted_pickup_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alteration {self.pk} - {self.status}"

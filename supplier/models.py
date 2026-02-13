from django.db import models
from core.models import Category
from django.conf import settings
import uuid


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RECEIVED', 'Received'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    outfit_type = models.CharField(max_length=50, help_text="e.g., LHG (Lehenga)")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.supplier.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255) # e.g., "Lehenga Blue"
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.description} ({self.quantity})"


# New models for secure supplier ordering flow
class SecureOrderLink(models.Model):
    """Admin creates this and shares the secure URL with supplier."""
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True, blank=True, on_delete=models.SET_NULL)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SecureLink {self.token} -> {self.supplier}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONFIRMED', 'Confirmed'),
        ('RECEIVED', 'Received'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    secure_link = models.ForeignKey(SecureOrderLink, null=True, blank=True, on_delete=models.SET_NULL)
    qr_code = models.ImageField(upload_to='po_qr_codes/', null=True, blank=True)

    def __str__(self):
        return f"PO-{self.pk} ({self.supplier.name})"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    outfit_type = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='po_item_images/', null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"POItem {self.pk} - {self.outfit_type} x{self.quantity}"

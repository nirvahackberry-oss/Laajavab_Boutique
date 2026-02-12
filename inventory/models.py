from django.db import models
from supplier.models import Order
from sku.models import ProductSKU

class Discrepancy(models.Model):
    TYPE_CHOICES = [
        ('MISSING', 'Missing'),
        ('EXTRA', 'Extra'),
        ('DAMAGED', 'Damaged'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.item_name} (Order {self.order.pk})"

class InventoryItem(models.Model):
    sku = models.OneToOneField(ProductSKU, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku.sku_code} - {self.quantity}"

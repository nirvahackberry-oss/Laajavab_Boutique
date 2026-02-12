from django.db import models
from core.models import Category, OutfitType
from supplier.models import Supplier, Order

class ProductSKU(models.Model):
    sku_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    outfit_type = models.ForeignKey(OutfitType, on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='skus')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    square_id = models.CharField(max_length=100, blank=True, null=True)
    variation_id = models.CharField(max_length=100, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sku_code or "Unknown SKU"

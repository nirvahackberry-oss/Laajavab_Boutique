from django.contrib import admin
from .models import ProductSKU

@admin.register(ProductSKU)
class ProductSKUAdmin(admin.ModelAdmin):
    list_display = ['sku_code', 'category', 'outfit_type', 'price', 'created_at']
    list_filter = ['category', 'outfit_type', 'created_at']
    search_fields = ['sku_code']
    readonly_fields = ['sku_code', 'barcode_image', 'created_at']

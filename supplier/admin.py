from django.contrib import admin
from .models import Supplier, Order, OrderItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'region']
    search_fields = ['name', 'email']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'category', 'outfit_type', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['order_sku', 'supplier__name']
    inlines = [OrderItemInline]

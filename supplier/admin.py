from django.contrib import admin
from .models import Supplier, Order, OrderItem, SecureOrderLink, PurchaseOrder, PurchaseOrderItem

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


@admin.register(SecureOrderLink)
class SecureOrderLinkAdmin(admin.ModelAdmin):
    list_display = ['token', 'supplier', 'created_by', 'used', 'created_at']
    readonly_fields = ['token', 'created_at']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [PurchaseOrderItemInline]

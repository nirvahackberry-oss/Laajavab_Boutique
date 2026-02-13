from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import InventoryItem, Discrepancy

@admin.register(InventoryItem)
class InventoryItemAdmin(ModelAdmin):
    list_display = ['sku', 'quantity', 'updated_at']
    search_fields = ['sku__sku_code']
    readonly_fields = ['updated_at']

@admin.register(Discrepancy)
class DiscrepancyAdmin(ModelAdmin):
    list_display = ['order', 'item_name', 'type', 'quantity', 'resolved', 'created_at']
    list_filter = ['type', 'resolved', 'created_at']
    search_fields = ['item_name', 'order__id']

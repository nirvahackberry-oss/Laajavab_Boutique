from rest_framework import serializers
from .models import Discrepancy, InventoryItem

class DiscrepancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discrepancy
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    sku_code = serializers.CharField(source='sku.sku_code', read_only=True)
    class Meta:
        model = InventoryItem
        fields = '__all__'

class InventoryListSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source='sku.sku_code', read_only=True)
    category = serializers.CharField(source='sku.category.name', read_only=True)
    outfit_type = serializers.CharField(source='sku.outfit_type.name', read_only=True)
    quantity_available = serializers.IntegerField(source='quantity', read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['sku', 'category', 'outfit_type', 'quantity_available']

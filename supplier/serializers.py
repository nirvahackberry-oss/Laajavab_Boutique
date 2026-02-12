from rest_framework import serializers
from .models import Supplier, Order, OrderItem
from core.serializers import CategorySerializer

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    supplier_details = SupplierSerializer(source='supplier', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

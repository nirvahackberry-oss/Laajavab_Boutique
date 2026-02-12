from rest_framework import serializers
from .models import ProductSKU
from core.serializers import CategorySerializer

class ProductSKUSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = ProductSKU
        fields = '__all__'

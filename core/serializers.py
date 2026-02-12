from rest_framework import serializers
from .models import Category, OutfitType

class CategorySerializer(serializers.ModelSerializer):
    prefix = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'

class OutfitTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)

    class Meta:
        model = OutfitType
        fields = '__all__'

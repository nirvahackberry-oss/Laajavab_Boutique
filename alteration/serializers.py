from rest_framework import serializers
from .models import Alteration, Tailor, Customer
from core.models import OutfitType

class TailorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tailor
        fields = '__all__'

class AlterationNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alteration
        fields = ['outfit_type', 'number_of_outfits', 'issue_description', 'status']

class CustomerSerializer(serializers.ModelSerializer):
    alterations = AlterationNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'email', 'alterations']

class AlterationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    tailor_name = serializers.CharField(source='tailor.name', read_only=True)
    
    class Meta:
        model = Alteration
        fields = '__all__'

class AlterationCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    outfit_type = serializers.IntegerField()
    number_of_outfits = serializers.IntegerField()
    issue_description = serializers.CharField()

    def create(self, validated_data):
        customer = Customer.objects.get(id=validated_data['customer_id'])
        outfit_type = OutfitType.objects.get(id=validated_data['outfit_type'])
        
        alteration = Alteration.objects.create(
            customer=customer,
            outfit_type=outfit_type.name,
            number_of_outfits=validated_data['number_of_outfits'],
            issue_description=validated_data['issue_description'],
            status='PENDING'
        )
        return alteration
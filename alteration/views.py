from typing import Type
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from .models import Alteration, Tailor, Customer
from .serializers import AlterationSerializer, TailorSerializer, CustomerSerializer, AlterationCreateSerializer
from .ai_service import AlterationPredictor
from core.models import OutfitType

def alteration_list(request):
    alterations = Alteration.objects.select_related('customer', 'tailor').all()
    return render(request, 'alteration/alteration_list.html', {'alterations': alterations})

def alteration_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        outfit_type_id = request.POST.get('outfit_type_id')
        number_of_outfits = request.POST.get('number_of_outfits')
        issue_description = request.POST.get('issue_description', '').strip()
        
        if not all([customer_id, outfit_type_id, number_of_outfits, issue_description]):
            context = {
                'error': 'All fields are required',
                'customers': Customer.objects.all(),
                'outfit_types': OutfitType.objects.all()
            }
            return render(request, 'alteration/alteration_create.html', context)
        
        customer = get_object_or_404(Customer, id=customer_id)
        outfit_type = get_object_or_404(OutfitType, id=outfit_type_id)
        
        Alteration.objects.create(
            customer=customer,
            outfit_type=outfit_type.name,
            number_of_outfits=number_of_outfits,
            issue_description=issue_description,
            status='PENDING'
        )
        return redirect('/alterations/')
    
    context = {
        'customers': Customer.objects.all(),
        'outfit_types': OutfitType.objects.all()
    }
    return render(request, 'alteration/alteration_create.html', context)

def alteration_edit(request, pk):
    alteration = get_object_or_404(Alteration, pk=pk)
    if request.method == 'POST':
        status_val = request.POST.get('status')
        issue_description = request.POST.get('issue_description', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if not all([status_val, issue_description]):
            return render(request, 'alteration/alteration_edit.html', {'alteration': alteration, 'error': 'Status and issue description are required'})
        
        alteration.status = status_val
        alteration.issue_description = issue_description
        alteration.notes = notes
        alteration.save()
        return redirect('/alterations/')
    
    return render(request, 'alteration/alteration_edit.html', {'alteration': alteration})

def alteration_delete(request, pk):
    alteration = get_object_or_404(Alteration, pk=pk)
    alteration.delete()
    return redirect('/alterations/')

def tailor_list(request):
    tailors = Tailor.objects.all()
    return render(request, 'alteration/tailor_list.html', {'tailors': tailors})

def tailor_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        specialties = request.POST.get('specialties', '').strip()
        phone = request.POST.get('phone', '').strip()
        is_available = request.POST.get('is_available') == '1'
        
        if not all([name, specialties]):
            return render(request, 'alteration/tailor_create.html', {'error': 'Name and specialties are required'})
        
        Tailor.objects.create(name=name, specialties=specialties, phone=phone, is_available=is_available)
        return redirect('/tailors/')
    
    return render(request, 'alteration/tailor_create.html')

def tailor_edit(request, pk):
    tailor = get_object_or_404(Tailor, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        specialties = request.POST.get('specialties', '').strip()
        phone = request.POST.get('phone', '').strip()
        is_available = request.POST.get('is_available') == '1'
        
        if not all([name, specialties]):
            return render(request, 'alteration/tailor_edit.html', {'tailor': tailor, 'error': 'Name and specialties are required'})
        
        tailor.name = name
        tailor.specialties = specialties
        tailor.phone = phone
        tailor.is_available = is_available
        tailor.save()
        return redirect('/tailors/')
    
    return render(request, 'alteration/tailor_edit.html', {'tailor': tailor})

def tailor_delete(request, pk):
    tailor = get_object_or_404(Tailor, pk=pk)
    tailor.delete()
    return redirect('/tailors/')

def customer_list(request):
    customers = Customer.objects.prefetch_related('alterations').all()
    return render(request, 'alteration/customer_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        chest = request.POST.get('chest', '').strip()
        waist = request.POST.get('waist', '').strip()
        length = request.POST.get('length', '').strip()
        
        if not all([name, phone_number]):
            return render(request, 'alteration/customer_create.html', {'error': 'Name and phone number are required'})
        
        Customer.objects.create(
            name=name,
            phone_number=phone_number,
            email=email or '',
            chest=chest or None,
            waist=waist or None,
            length=length or None
        )
        return redirect('/customers/')
    
    return render(request, 'alteration/customer_create.html')

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        chest = request.POST.get('chest', '').strip()
        waist = request.POST.get('waist', '').strip()
        length = request.POST.get('length', '').strip()
        
        if not all([name, phone_number]):
            return render(request, 'alteration/customer_edit.html', {'customer': customer, 'error': 'Name and phone number are required'})
        
        customer.name = name
        customer.phone_number = phone_number
        customer.email = email or ''
        customer.chest = chest or None
        customer.waist = waist or None
        customer.length = length or None
        customer.save()
        return redirect('/customers/')
    
    return render(request, 'alteration/customer_edit.html', {'customer': customer})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('/customers/')

class TailorViewSet(viewsets.ModelViewSet):
    queryset = Tailor.objects.all()
    serializer_class = TailorSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class AlterationViewSet(viewsets.ModelViewSet):
    queryset = Alteration.objects.all()
    serializer_class = AlterationSerializer

    def get_serializer_class(self) -> Type:
        if self.action == 'create':
            return AlterationCreateSerializer
        return AlterationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alteration = serializer.save()
        
        return Response({
            'id': alteration.id,
            'customer_id': alteration.customer.id,
            'outfit_type': request.data.get('outfit_type'),
            'number_of_outfits': alteration.number_of_outfits,
            'issue_description': alteration.issue_description
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        alteration = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        alteration.status = new_status
        alteration.save()
        
        return Response({'status': alteration.status}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='predict')
    def predict_pickup(self, request):
        outfit_type = request.data.get('outfit_type')
        tailor_id = request.data.get('tailor_id')
        
        if not outfit_type:
            return Response({'error': 'outfit_type required'}, status=status.HTTP_400_BAD_REQUEST)
        
        predictor = AlterationPredictor()
        pickup_date, confidence = predictor.predict_pickup_date(outfit_type, tailor_id)
        
        return Response({
            'predicted_pickup_date': pickup_date,
            'confidence_score': confidence,
            'outfit_type': outfit_type
        })
    
    @action(detail=True, methods=['get'], url_path='tag')
    def generate_tag(self, request, pk=None):
        alteration = self.get_object()
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.drawString(100, 750, f"Alteration ID: {alteration.id}")
        p.drawString(100, 730, f"Item: {alteration.issue_description}")
        p.drawString(100, 710, f"Customer: {alteration.customer.name}")
        p.drawString(100, 690, f"Status: {alteration.status}")
        if alteration.sku:
            p.drawString(100, 670, f"SKU: {alteration.sku.sku_code}")
        p.drawString(100, 650, f"Notes: {alteration.notes}")
        
        p.save()
        buffer.seek(0)
        
        return FileResponse(buffer, content_type='application/pdf', filename=f'tag_{alteration.id}.pdf')
    
    @action(detail=True, methods=['post'], url_path='notify')
    def notify_customer(self, request, pk=None):
        alteration = self.get_object()
        
        message = f"Hello {alteration.customer.name}, your {alteration.outfit_type} alteration is ready for pickup!"
        
        alteration.status = 'READY'
        alteration.save()
        
        return Response({
            'message': 'Customer notified successfully',
            'notification_sent': message,
            'customer_phone': alteration.customer.phone_number
        })

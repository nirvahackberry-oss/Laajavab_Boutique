from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from .models import ProductSKU
from .serializers import ProductSKUSerializer
from .utils import generate_barcode_image
from core.models import Category, OutfitType
from supplier.models import Supplier, Order
import datetime

def sku_list(request):
    skus = ProductSKU.objects.select_related('category', 'outfit_type', 'supplier').all()
    return render(request, 'sku/sku_list.html', {'skus': skus})

def sku_generate(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        outfit_type_id = request.POST.get('outfit_type_id')
        supplier_id = request.POST.get('supplier_id')
        order_id = request.POST.get('order_id')
        price = request.POST.get('price')
        
        if not all([category_id, outfit_type_id, supplier_id, order_id, price]):
            context = {
                'error': 'All fields are required',
                'categories': Category.objects.all(),
                'outfit_types': OutfitType.objects.all(),
                'suppliers': Supplier.objects.all(),
                'orders': Order.objects.all()
            }
            return render(request, 'sku/sku_generate.html', context)
        
        category = get_object_or_404(Category, id=category_id)
        outfit_type = get_object_or_404(OutfitType, id=outfit_type_id)
        supplier = get_object_or_404(Supplier, id=supplier_id)
        order = get_object_or_404(Order, id=order_id)
        
        sku = ProductSKU.objects.create(
            category=category,
            outfit_type=outfit_type,
            supplier=supplier,
            order=order,
            price=price,
            sku_code=None
        )
        
        now = datetime.datetime.now()
        yymm = now.strftime("%y%m")
        supplier_code = f"S{supplier.pk}"
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        order_seq = ProductSKU.objects.filter(created_at__gte=month_start).aggregate(Max('id'))['id__max'] or 0
        order_seq = f"{order_seq + 1:04d}"
        code = f"{category.prefix}-{outfit_type.code}-{supplier_code}-{yymm}-{order_seq}"
        
        sku.sku_code = code
        sku.save()
        
        from inventory.models import InventoryItem
        InventoryItem.objects.create(sku=sku, quantity=1)
        
        barcode_img = generate_barcode_image(code)
        sku.barcode_image.save(f"{code}.png", barcode_img, save=True)
        
        return redirect('/sku/')
    
    context = {
        'categories': Category.objects.all(),
        'outfit_types': OutfitType.objects.all(),
        'suppliers': Supplier.objects.all(),
        'orders': Order.objects.select_related('supplier').all()
    }
    return render(request, 'sku/sku_generate.html', context)

def sku_edit(request, pk):
    sku = get_object_or_404(ProductSKU, pk=pk)
    if request.method == 'POST':
        price = request.POST.get('price')
        if not price:
            return render(request, 'sku/sku_edit.html', {'sku': sku, 'error': 'Price is required'})
        
        sku.price = price
        sku.save()
        return redirect('/sku/')
    
    return render(request, 'sku/sku_edit.html', {'sku': sku})

def sku_delete(request, pk):
    sku = get_object_or_404(ProductSKU, pk=pk)
    sku.delete()
    return redirect('/sku/')

class ProductSKUViewSet(viewsets.ModelViewSet):
    queryset = ProductSKU.objects.all()
    serializer_class = ProductSKUSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_sku(self, request):
        input_data = request.data
        category_id = input_data.get('category_id')
        outfit_type_id = input_data.get('outfit_type_id')
        supplier_id = input_data.get('supplier_id')
        price = input_data.get('price')
        order_id = input_data.get('order_id')

        if not all([category_id, outfit_type_id, supplier_id, price, order_id]):
            return Response(
                {"error": "category_id, outfit_type_id, supplier_id, price, and order_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        category = get_object_or_404(Category, id=category_id)
        outfit_type = get_object_or_404(OutfitType, id=outfit_type_id)
        supplier = get_object_or_404(Supplier, id=supplier_id)
        order = get_object_or_404(Order, id=order_id)

        # Create SKU
        sku = ProductSKU.objects.create(
            category=category,
            outfit_type=outfit_type,
            supplier=supplier,
            order=order,
            price=price,
            sku_code=None
        )

        # Generate SKU Code: CAT-TYPE-SUP-YYMM-ORDSEQ
        now = datetime.datetime.now()
        yymm = now.strftime("%y%m")
        supplier_code = f"S{supplier.pk}"
        
        # Get order sequence for this month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        order_seq = ProductSKU.objects.filter(
            created_at__gte=month_start
        ).aggregate(Max('id'))['id__max'] or 0
        order_seq = f"{order_seq + 1:04d}"
        
        code = f"{category.prefix}-{outfit_type.code}-{supplier_code}-{yymm}-{order_seq}"
        
        sku.sku_code = code
        sku.save()

        # Create InventoryItem
        from inventory.models import InventoryItem
        InventoryItem.objects.create(sku=sku, quantity=1)

        # Generate Barcode Image
        barcode_img = generate_barcode_image(code)
        sku.barcode_image.save(f"{code}.png", barcode_img, save=True)

        return Response({
            "sku_code": sku.sku_code,
            "barcode_url": f"/api/v1/sku/{sku.pk}/barcode/"
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='barcode')
    def get_barcode(self, request, pk=None):
        sku = self.get_object()
        if not sku.barcode_image:
            barcode_img = generate_barcode_image(sku.sku_code)
            sku.barcode_image.save(f"{sku.sku_code}.png", barcode_img, save=True)
        
        from django.http import FileResponse
        return FileResponse(sku.barcode_image.open(), content_type='image/png')


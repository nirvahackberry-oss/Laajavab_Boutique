from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier, Order, OrderItem
from .serializers import SupplierSerializer, OrderSerializer, OrderItemSerializer

def supplier_list(request):
    suppliers = Supplier.objects.all()
    orders = Order.objects.select_related('supplier', 'category').all()[:10]
    return render(request, 'supplier/supplier_list.html', {'suppliers': suppliers, 'orders': orders})

def supplier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        region = request.POST.get('region', '').strip()
        
        if not all([name, email, region]):
            return render(request, 'supplier/supplier_create.html', {'error': 'All fields are required'})
        
        Supplier.objects.create(name=name, email=email, region=region)
        return redirect('/suppliers/')
    
    return render(request, 'supplier/supplier_create.html')

def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        region = request.POST.get('region', '').strip()
        
        if not all([name, email, region]):
            return render(request, 'supplier/supplier_edit.html', {'supplier': supplier, 'error': 'All fields are required'})
        
        supplier.name = name
        supplier.email = email
        supplier.region = region
        supplier.save()
        return redirect('/suppliers/')
    
    return render(request, 'supplier/supplier_edit.html', {'supplier': supplier})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('/suppliers/')

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'], url_path='discrepancy')
    def report_discrepancy(self, request):
        # Input: { "order_id": 22, "items": [ { "item_name": "...", "type": "MISSING", "qty": 2 } ] }
        order_id = request.data.get('order_id')
        items = request.data.get('items', [])

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        from inventory.models import Discrepancy
        
        created_discrepancies = []
        for item in items:
            discrepancy = Discrepancy.objects.create(
                order=order,
                item_name=item.get('item_name'),
                type=item.get('type'),
                quantity=item.get('qty', 0)
            )
            created_discrepancies.append(discrepancy.pk)
            
            # "Auto-generates supplier feedback record"
            # TODO: Implement Supplier Feedback logic if needed.
            # For now just logging discrepancy is what's requested in schema.

        return Response({
            "message": "Discrepancies reported", 
            "ids": created_discrepancies
        }, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

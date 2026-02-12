from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import Discrepancy, InventoryItem
from .serializers import DiscrepancySerializer, InventoryItemSerializer, InventoryListSerializer

def inventory_list(request):
    inventory = InventoryItem.objects.select_related('sku__category', 'sku__outfit_type').all()
    return render(request, 'inventory/inventory_list.html', {'inventory': inventory})

class DiscrepancyViewSet(viewsets.ModelViewSet):
    queryset = Discrepancy.objects.all()
    serializer_class = DiscrepancySerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related('sku__category', 'sku__outfit_type').all()
    serializer_class = InventoryItemSerializer

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return InventoryListSerializer
        return InventoryItemSerializer

    @action(detail=False, methods=['get'])
    def total(self, request):
        local_inventory = self.get_queryset()
        serializer = self.get_serializer(local_inventory, many=True)
        
        square_inventory = [
            {"sku": "SQ-ITEM-1", "qty": 10, "source": "Square"}
        ]
        
        return Response({
            "local": serializer.data,
            "square": square_inventory,
        })


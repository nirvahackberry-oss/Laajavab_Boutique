from django.urls import path, include
from rest_framework import routers
from core.views import CategoryViewSet, OutfitTypeViewSet
from sku.views import ProductSKUViewSet
from supplier.views import SupplierViewSet, OrderViewSet, OrderItemViewSet
from inventory.views import InventoryViewSet, DiscrepancyViewSet
from alteration.views import AlterationViewSet, TailorViewSet, CustomerViewSet

router = routers.DefaultRouter()
router.register(r'sku', ProductSKUViewSet, basename='sku')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'outfit-types', OutfitTypeViewSet, basename='outfit-type')

# Inventory routes
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'discrepancies', DiscrepancyViewSet, basename='discrepancy')

# Alteration routes
router.register(r'alterations', AlterationViewSet, basename='alteration')
router.register(r'tailors', TailorViewSet, basename='tailor')
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
    path('forecast/', include('forecasting.urls')),
]

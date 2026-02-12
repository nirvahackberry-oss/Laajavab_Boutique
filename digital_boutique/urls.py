from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('core.urls')),
    path('sku/', include('sku.urls')),
    path('inventory/', include('inventory.urls')),
    path('suppliers/', include('supplier.urls')),
    path('alterations/', include('alteration.urls')),
    path('tailors/', include('alteration.tailor_urls')),
    path('customers/', include('alteration.customer_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

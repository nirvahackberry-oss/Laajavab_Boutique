from django.urls import path
from . import views

app_name = 'supplier'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    # Public secure form for suppliers
    path('secure/<uuid:token>/', views.secure_order_form, name='secure_order_form'),
    path('po/<int:pk>/qr/', views.po_qr_view, name='po_qr'),
]

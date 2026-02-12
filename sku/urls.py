from django.urls import path
from . import views

urlpatterns = [
    path('', views.sku_list, name='sku_list'),
    path('generate/', views.sku_generate, name='sku_generate'),
    path('<int:pk>/edit/', views.sku_edit, name='sku_edit'),
    path('<int:pk>/delete/', views.sku_delete, name='sku_delete'),
]

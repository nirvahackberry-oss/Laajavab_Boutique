from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('outfit-types/', views.outfit_type_list, name='outfit_type_list'),
    path('outfit-types/create/', views.outfit_type_create, name='outfit_type_create'),
    path('outfit-types/<int:pk>/edit/', views.outfit_type_edit, name='outfit_type_edit'),
    path('outfit-types/<int:pk>/delete/', views.outfit_type_delete, name='outfit_type_delete'),
]

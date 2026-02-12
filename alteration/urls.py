from django.urls import path
from . import views

urlpatterns = [
    path('', views.alteration_list, name='alteration_list'),
    path('create/', views.alteration_create, name='alteration_create'),
    path('<int:pk>/edit/', views.alteration_edit, name='alteration_edit'),
    path('<int:pk>/delete/', views.alteration_delete, name='alteration_delete'),
]

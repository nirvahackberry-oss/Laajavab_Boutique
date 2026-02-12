from django.urls import path
from . import views

urlpatterns = [
    path('', views.tailor_list, name='tailor_list'),
    path('create/', views.tailor_create, name='tailor_create'),
    path('<int:pk>/edit/', views.tailor_edit, name='tailor_edit'),
    path('<int:pk>/delete/', views.tailor_delete, name='tailor_delete'),
]

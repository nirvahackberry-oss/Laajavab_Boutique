from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_forecast, name='generate_forecast'),
    path('', views.get_forecasts, name='get_forecasts'),
]
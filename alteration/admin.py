from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Alteration, Tailor, Customer

@admin.register(Tailor)
class TailorAdmin(ModelAdmin):
    list_display = ['name', 'specialties', 'is_available']
    list_filter = ['is_available', 'specialties']

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['name', 'phone_number', 'email']
    search_fields = ['name', 'phone_number']

@admin.register(Alteration)
class AlterationAdmin(ModelAdmin):
    list_display = ['id', 'customer', 'tailor', 'outfit_type', 'status', 'predicted_pickup_date']
    list_filter = ['status', 'outfit_type', 'created_at']
    search_fields = ['customer__name', 'issue_description']

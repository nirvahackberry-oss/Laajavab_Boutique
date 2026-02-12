from django.contrib import admin
from .models import Category, OutfitType

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix']
    search_fields = ['name', 'prefix']

@admin.register(OutfitType)
class OutfitTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

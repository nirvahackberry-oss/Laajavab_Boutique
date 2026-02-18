from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Alteration, Tailor, Customer


# ===============================
# Tailor Admin (Improved)
# ===============================
@admin.register(Tailor)
class TailorAdmin(ModelAdmin):
    list_display = ["name", "specialties", "phone", "is_available"]
    list_filter = ["is_available", "specialties"]
    search_fields = ["name", "specialties", "phone"]
    list_editable = ["is_available"]
    ordering = ["name"]
    list_per_page = 20

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (("name", "specialties"),),
            },
        ),
        (
            "Contact & Availability",
            {
                "fields": ("phone", "is_available"),
            },
        ),
    )


# ===============================
# Customer Admin (Improved)
# ===============================
@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ["name", "phone_number", "email"]
    search_fields = ["name", "phone_number", "email"]
    ordering = ["name"]
    list_per_page = 20

    fieldsets = (
        (
            "Basic Details",
            {
                "fields": ("name", "phone_number", "email"),
                
            },
        ),
        (
            "Body Measurements (in inches)",
            {
                "fields": (("chest", "waist", "length"),),
            },
        ),
    )


# ===============================
# Alteration Admin (Improved)
# ===============================
@admin.register(Alteration)
class AlterationAdmin(ModelAdmin):
    list_display = [
        "id",
        "customer",
        "tailor",
        "outfit_type",
        "status",
        "predicted_pickup_date",
        "created_at",
    ]

    list_filter = ["status", "outfit_type", "created_at", "tailor"]
    search_fields = ["customer__name", "issue_description", "tailor__name"]
    autocomplete_fields = ["customer", "tailor"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_per_page = 25

    fieldsets = (
        (
            "Customer & Tailor",
            {
                "fields": ("customer", "tailor"),
            },
        ),
        (
            "Alteration Details",
            {
                "fields": (
                    ("outfit_type", "status"),
                    "number_of_outfits",
                    "issue_description",
                    "notes",
                ),
            },
        ),
        (
            "Timeline",
            {
                "fields": ("predicted_pickup_date",),
            },
        ),
    )

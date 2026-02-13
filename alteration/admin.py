from django.contrib import admin
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Fieldset, ButtonHolder, Submit
from unfold.admin import ModelAdmin
from .models import Alteration, Tailor, Customer

# -----------------------------------------
# 1️⃣ Tailor Form with placeholders + layout
# -----------------------------------------
class TailorAdminForm(forms.ModelForm):
    class Meta:
        model = Tailor
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Placeholders for user-friendly input hints
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter full name'})
        self.fields['specialties'].widget.attrs.update({'placeholder': 'e.g., Bridal, Suits'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'e.g., +91 9876543210'})

        # Clean 2-column layout inside a titled section
        self.helper.layout = Layout(
            Fieldset("Tailor Details",
                Row(
                    Column("name", css_class="w-1/2 pr-2"),
                    Column("specialties", css_class="w-1/2 pl-2"),
                ),
                Row(
                    Column("phone", css_class="w-1/2 pr-2"),
                    Column("is_available", css_class="w-1/2 pl-2"),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Tailor', css_class='btn-primary')
            )
        )

# -----------------------------------------
# 2️⃣ Customer Form with layout + placeholders
# -----------------------------------------
class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # User hints for input fields
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter full name'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'e.g., +91 9876543210'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email address'})

        # Layout with sections and columns
        self.helper.layout = Layout(
            Fieldset("Customer Details",
                Row(
                    Column("name", css_class="w-1/2 pr-2"),
                    Column("phone_number", css_class="w-1/2 pl-2"),
                ),
                Field("email"),
            ),
            ButtonHolder(
                Submit('submit', 'Save Customer', css_class='btn-primary')
            )
        )

# -----------------------------------------
# 3️⃣ Alteration Form: sections + 2-col + save button
# -----------------------------------------
class AlterationAdminForm(forms.ModelForm):
    class Meta:
        model = Alteration
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset("Customer Info",
                Row(
                    Column("customer", css_class="w-1/2 pr-2"),
                    Column("tailor", css_class="w-1/2 pl-2"),
                ),
            ),
            Fieldset("Alteration Details",
                Row(
                    Column("outfit_type", css_class="w-1/2 pr-2"),
                    Column("status", css_class="w-1/2 pl-2"),
                ),
                Field("issue_description"),
                Field("predicted_pickup_date"),
            ),
            ButtonHolder(
                Submit('submit', 'Save Alteration', css_class='btn-primary')
            )
        )

# -----------------------------------------
# 4️⃣ Admin registration with Crispy forms
# -----------------------------------------
@admin.register(Tailor)
class TailorAdmin(ModelAdmin):
    form = TailorAdminForm
    list_display = ["name", "specialties", "phone", "is_available"]
    list_filter = ["is_available", "specialties"]
    search_fields = ["name", "specialties"]

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    form = CustomerAdminForm
    list_display = ["name", "phone_number", "email"]
    search_fields = ["name", "phone_number"]

@admin.register(Alteration)
class AlterationAdmin(ModelAdmin):
    form = AlterationAdminForm
    list_display = [
        "id",
        "customer",
        "tailor",
        "outfit_type",
        "status",
        "predicted_pickup_date",
    ]
    list_filter = ["status", "outfit_type", "created_at"]
    search_fields = ["customer__name", "issue_description"]





# from django.contrib import admin
# from unfold.admin import ModelAdmin
# from .models import Alteration, Tailor, Customer

# @admin.register(Tailor)
# class TailorAdmin(ModelAdmin):
#     list_display = ['name', 'specialties', 'is_available']
#     list_filter = ['is_available', 'specialties']

# @admin.register(Customer)
# class CustomerAdmin(ModelAdmin):
#     list_display = ['name', 'phone_number', 'email']
#     search_fields = ['name', 'phone_number']

# @admin.register(Alteration)
# class AlterationAdmin(ModelAdmin):
#     list_display = ['id', 'customer', 'tailor', 'outfit_type', 'status', 'predicted_pickup_date']
#     list_filter = ['status', 'outfit_type', 'created_at']
#     search_fields = ['customer__name', 'issue_description']

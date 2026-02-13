from datetime import timedelta

from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Supplier, Order, OrderItem, SecureOrderLink, PurchaseOrder, PurchaseOrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'region', 'create_secure_link_button']
    search_fields = ['name', 'email']

    @admin.display(description='Secure link')
    def create_secure_link_button(self, obj):
        url = f"{reverse('admin:supplier_secureorderlink_add')}?supplier={obj.pk}"
        return format_html('<a class="button" href="{}">Create secure form link</a>', url)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'category', 'outfit_type', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['order_sku', 'supplier__name']
    inlines = [OrderItemInline]


@admin.register(SecureOrderLink)
class SecureOrderLinkAdmin(admin.ModelAdmin):
    list_display = ['token', 'supplier', 'created_by', 'used', 'created_at', 'copy_url_button']
    readonly_fields = ['token', 'created_at', 'created_by', 'supplier', 'expires_at', 'secure_form_url']
    fields = ['supplier', 'created_by', 'expires_at', 'used', 'token', 'secure_form_url', 'created_at']
    list_select_related = ['supplier', 'created_by']

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        supplier_id = request.GET.get('supplier')
        if supplier_id:
            initial['supplier'] = supplier_id
        return initial

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields.pop('supplier', None)
            form.base_fields.pop('created_by', None)
            form.base_fields.pop('expires_at', None)
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            supplier_id = request.GET.get('supplier')
            if supplier_id:
                obj.supplier_id = supplier_id
            if not obj.supplier_id:
                self.message_user(
                    request,
                    'Please create secure links from a supplier row button so supplier is preselected.',
                    level=messages.ERROR,
                )
                return
            obj.created_by = request.user
            obj.expires_at = timezone.now() + timedelta(hours=24)
        super().save_model(request, obj, form, change)

    @admin.display(description='Secure form URL')
    def secure_form_url(self, obj):
        if not obj.pk:
            return 'Will be generated after save.'
        relative_url = reverse('supplier:secure_order_form', args=[obj.token])
        full_url = relative_url
        return format_html(
            '<div>'
            '<a href="{0}" target="_blank" id="secure-link-{1}">{0}</a> '
            '<button type="button" onclick="navigator.clipboard.writeText(document.getElementById(\'secure-link-{1}\').href)">Copy</button>'
            '</div>',
            full_url,
            obj.pk,
        )

    @admin.display(description='Copy URL')
    def copy_url_button(self, obj):
        relative_url = reverse('supplier:secure_order_form', args=[obj.token])
        return format_html(
            '<button type="button" onclick="navigator.clipboard.writeText(window.location.origin + \"{0}\")">Copy</button>',
            relative_url,
        )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Secure form URL')
    def secure_form_url(self, obj):
        relative_url = reverse('supplier:secure_order_form', args=[obj.token])
        return format_html(
            '<div>'
            '<a href="{0}" target="_blank" id="secure-link-{1}">{0}</a> '
            '<button type="button" onclick="navigator.clipboard.writeText(window.location.origin + \"{0}\")">Copy</button>'
            '</div>',
            relative_url,
            obj.pk,
        )

    @admin.display(description='Copy URL')
    def copy_url_button(self, obj):
        relative_url = reverse('supplier:secure_order_form', args=[obj.token])
        return format_html(
            '<button type="button" onclick="navigator.clipboard.writeText(window.location.origin + \"{0}\")">Copy</button>',
            relative_url,
        )


# PurchaseOrder is intentionally not registered in Django admin.
# Supplier order submission is done via supplier-facing secure form link only.

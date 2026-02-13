from datetime import timedelta

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Supplier, Order, OrderItem, SecureOrderLink


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'region', 'create_secure_link_button']
    search_fields = ['name', 'email']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:supplier_id>/create-secure-link/',
                self.admin_site.admin_view(self.create_secure_link_view),
                name='supplier_create_secure_link',
            ),
        ]
        return custom_urls + urls

    @admin.display(description='Secure link')
    def create_secure_link_button(self, obj):
        url = reverse('admin:supplier_create_secure_link', args=[obj.pk])
        return format_html('<a class="button" href="{}">Create & copy secure link</a>', url)

    def create_secure_link_view(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id)

        link = SecureOrderLink.objects.create(
            supplier=supplier,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        relative_url = reverse('supplier:secure_order_form', args=[link.token])

        self.message_user(
            request,
            format_html(
                'Secure link created for <strong>{}</strong>: '
                '<a href="{}" target="_blank" id="secure-link-new">{}</a> '
                '<button type="button" onclick="navigator.clipboard.writeText(window.location.origin + \'{}\')">Copy</button>',
                supplier.name,
                relative_url,
                relative_url,
                relative_url,
            ),
            level=messages.SUCCESS,
        )
        return HttpResponseRedirect(reverse('admin:supplier_supplier_changelist'))


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
    list_display = ['token', 'supplier', 'created_by', 'used', 'created_at', 'expires_at', 'copy_url_button']
    readonly_fields = ['token', 'supplier', 'created_by', 'expires_at', 'used', 'created_at', 'secure_form_url']
    fields = ['supplier', 'created_by', 'expires_at', 'used', 'token', 'secure_form_url', 'created_at']
    list_select_related = ['supplier', 'created_by']

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

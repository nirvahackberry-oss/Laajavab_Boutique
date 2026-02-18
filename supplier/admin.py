from datetime import timedelta

from django.contrib import admin
from unfold.admin import ModelAdmin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Supplier, Order, OrderItem, SecureOrderLink


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ['name', 'email', 'region']
    search_fields = ['name', 'email']
    readonly_fields = ['supplier_secure_form_url']

    def get_fields(self, request, obj=None):
        fields = ['name', 'email', 'region']
        if obj:
            fields.append('supplier_secure_form_url')
        return fields

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

    def _copy_js(self, relative_url):
        return (
            "return (function(){"
            f"const url=window.location.origin + '{relative_url}';"
            "const fallback=function(text){"
            "const ta=document.createElement('textarea');"
            "ta.value=text;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.left='-9999px';"
            "document.body.appendChild(ta);ta.focus();ta.select();"
            "let ok=false;try{ok=document.execCommand('copy');}catch(e){ok=false;}"
            "document.body.removeChild(ta);return ok;};"
            "if(navigator.clipboard && window.isSecureContext){"
            "navigator.clipboard.writeText(url).then(function(){window.alert('Link copied to clipboard.');}).catch(function(){if(!fallback(url)){window.prompt('Copy this link:',url);}});"
            "}else{if(!fallback(url)){window.prompt('Copy this link:',url);}else{window.alert('Link copied to clipboard.');}}"
            "return false;"
            "})();"
        )

    def _create_link_js(self, create_url, success_prefix):
        return (
            "return (async function(btn){"
            "if(btn.dataset.loading==='1'){return false;}"
            "btn.dataset.loading='1';"
            "const originalText=btn.textContent;"
            "btn.textContent='Creating...';"
            "try{"
            f"const response=await fetch('{create_url}',{{method:'POST',headers:{{'X-CSRFToken':(document.cookie.match(/csrftoken=([^;]+)/)||[])[1]||''}}}});"
            "const data=await response.json();"
            "if(!response.ok){throw new Error(data.error||'Unable to create secure link');}"
            "const url=data.url;"
            "const fallback=function(text){"
            "try{const ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');"
            "ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.focus();ta.select();"
            "const ok=document.execCommand('copy');document.body.removeChild(ta);return ok;}catch(e){return false;}};"
            "let copied=false;"
            "if(navigator.clipboard && window.isSecureContext){copied=await navigator.clipboard.writeText(url).then(()=>true).catch(()=>false);}"
            "if(!copied){copied=fallback(url);}"
            f"window.prompt((copied?'{success_prefix} copied:\\n':'{success_prefix} created (copy manually):\\n')+url,url);"
            "window.location.reload();"
            "}catch(err){window.alert(err.message);}"
            "finally{btn.dataset.loading='0';btn.textContent=originalText;}"
            "})(this);"
        )

    @admin.display(description='Secure link')
    def create_secure_link_button(self, obj):
        url = reverse('admin:supplier_create_secure_link', args=[obj.pk])
        return format_html(
            '<button type="button" class="button" onclick="{}">Create secure form link</button>',
            self._create_link_js(url, 'Secure link'),
        )

    @admin.display(description='Secure form URL')
    def supplier_secure_form_url(self, obj):
        create_url = reverse('admin:supplier_create_secure_link', args=[obj.pk])
        try:
            latest_link = SecureOrderLink.objects.filter(supplier_id=obj.pk).order_by('-created_at').first()
        except Exception:
            return format_html('<span style="color:#b94a48;">Unable to load secure link.</span>')

        if not latest_link:
            return format_html(
                '<div>'
                '<div style="margin-bottom:10px; color:#7a6859;">No secure link generated yet.</div>'
                '<div style="display:flex; gap:8px;"><button type="button" class="button" onclick="{}">Create secure form link</button></div>'
                '</div>',
                self._create_link_js(create_url, 'Secure link'),
            )

        relative_url = reverse('supplier:secure_order_form', args=[latest_link.token])
        return format_html(
            '<div>'
            '<div><a href="{0}" target="_blank" style="word-break:break-all;">{0}</a></div>'
            '<div style="margin-top:10px; display:flex; gap:8px;">'
            '<button type="button" class="button" onclick="{1}">Copy link</button>'
            '<button type="button" class="button" onclick="{2}">Generate new</button>'
            '</div>'
            '</div>',
            relative_url,
            self._copy_js(relative_url),
            self._create_link_js(create_url, 'New secure link'),
        )

    def create_secure_link_view(self, request, supplier_id):
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required.'}, status=405)

        supplier = get_object_or_404(Supplier, pk=supplier_id)
        link = SecureOrderLink.objects.create(
            supplier=supplier,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        relative_url = reverse('supplier:secure_order_form', args=[link.token])
        return JsonResponse({'url': request.build_absolute_uri(relative_url)})


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'supplier', 'category', 'outfit_type', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['order_sku', 'supplier__name']
    inlines = [OrderItemInline]


@admin.register(SecureOrderLink)
class SecureOrderLinkAdmin(ModelAdmin):
# class SecureOrderLinkAdmin(admin.ModelAdmin):
    list_display = ['token', 'supplier', 'created_by', 'used', 'created_at', 'expires_at', 'copy_url_button']
    readonly_fields = ['token', 'supplier', 'created_by', 'expires_at', 'used', 'created_at']
    fields = ['supplier', 'created_by', 'expires_at', 'used', 'token', 'created_at']
    list_select_related = ['supplier', 'created_by']

    def has_add_permission(self, request):
        return False

    @admin.display(description='Copy URL')
    def copy_url_button(self, obj):
        is_expired = bool(obj.expires_at and obj.expires_at < timezone.now())
        if is_expired:
            return format_html('<button type="button" class="button" disabled title="Link expired">Copy</button>')

        relative_url = reverse('supplier:secure_order_form', args=[obj.token])
        copy_js = (
            "return (async function(){"
            f"const url=window.location.origin + '{relative_url}';"
            "const fallback=function(text){try{const ta=document.createElement('textarea');"
            "ta.value=text;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.left='-9999px';"
            "document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand('copy');"
            "document.body.removeChild(ta);return ok;}catch(e){return false;}};"
            "let copied=false;"
            "if(navigator.clipboard && window.isSecureContext){copied=await navigator.clipboard.writeText(url).then(()=>true).catch(()=>false);}"
            "if(!copied){copied=fallback(url);}"
            "if(copied){window.alert('Link copied to clipboard.');}else{window.prompt('Copy this link:',url);}"
            "return false;"
            "})();"
        )
        return format_html('<button type="button" class="button" onclick="{}">Copy</button>', copy_js)


# PurchaseOrder is intentionally not registered in Django admin.
# Supplier order submission is done via supplier-facing secure form link only.

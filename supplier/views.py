from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.core.files.base import ContentFile
from datetime import timedelta
from django.core.mail import send_mail
import io
import uuid

import qrcode
from .models import Supplier, Order, OrderItem, SecureOrderLink, PurchaseOrder, PurchaseOrderItem
from .serializers import SupplierSerializer, OrderSerializer, OrderItemSerializer


def supplier_list(request):
    suppliers = Supplier.objects.all()
    orders = Order.objects.select_related('supplier', 'category').all()[:10]
    return render(request, 'supplier/supplier_list.html', {'suppliers': suppliers, 'orders': orders})


def supplier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        region = request.POST.get('region', '').strip()

        if not all([name, email, region]):
            return render(request, 'supplier/supplier_create.html', {'error': 'All fields are required'})

        Supplier.objects.create(name=name, email=email, region=region)
        return redirect('/suppliers/')

    return render(request, 'supplier/supplier_create.html')


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        region = request.POST.get('region', '').strip()

        if not all([name, email, region]):
            return render(request, 'supplier/supplier_edit.html', {'supplier': supplier, 'error': 'All fields are required'})

        supplier.name = name
        supplier.email = email
        supplier.region = region
        supplier.save()
        return redirect('/suppliers/')

    return render(request, 'supplier/supplier_edit.html', {'supplier': supplier})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('/suppliers/')


def secure_order_form(request, token):
    # public supplier-facing form accessed via secure token
    link = SecureOrderLink.objects.select_related('supplier').filter(token=token).first()
    if not link:
        return render(request, 'supplier/link_invalid.html', status=404)
    # optional expiry check
    if link.expires_at and link.expires_at < timezone.now():
        return render(request, 'supplier/link_expired.html', {'link': link})

    if request.method == 'POST':
        # supplier: either linked or create from submitted info
        supplier = link.supplier
        if not supplier:
            name = request.POST.get('supplier_name')
            email = request.POST.get('supplier_email')
            region = request.POST.get('supplier_region', '')
            supplier = Supplier.objects.create(name=name or 'Unknown', email=email or '', region=region)

        po = PurchaseOrder.objects.create(supplier=supplier, secure_link=link)

        outfit_type = request.POST.get('outfit_type')
        category_id = request.POST.get('category')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', '0') or 0)
        price = request.POST.get('price') or '0'

        category = None
        if category_id:
            from core.models import Category
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                category = None

        item = PurchaseOrderItem.objects.create(
            purchase_order=po,
            outfit_type=outfit_type or '',
            category=category,
            size=size or '',
            quantity=quantity,
            price=price or '0'
        )

        # handle image
        image = request.FILES.get('image')
        if image:
            item.image.save(image.name, image)

        # generate simple SKU
        item.sku = f"SKU-{po.pk or 'X'}-{item.pk}"
        item.save()

        # generate unique QR per submitted form/PO.
        # Encode a scan URL (not raw JSON) so scanner opens browser directly.
        submission_ref = uuid.uuid4().hex
        scan_url = request.build_absolute_uri(
            reverse('supplier:po_qr', args=[po.pk]) + f'?ref={submission_ref}'
        )

        qr_img = qrcode.make(scan_url)
        buffer = io.BytesIO()
        qr_img.save(buffer, 'PNG')
        buffer.seek(0)
        po.qr_code.save(f'po_{po.pk}_qr_{submission_ref}.png', ContentFile(buffer.read()))
        po.save()

        # mark link used
        link.used = True
        link.save()

        return redirect(reverse('supplier:po_qr', args=[po.pk]))

    # GET
    from core.models import Category
    categories = Category.objects.all()
    supplier = link.supplier
    return render(request, 'supplier/order_form.html', {'link': link, 'categories': categories, 'supplier': supplier})


def po_qr_view(request, pk):
    po = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier").prefetch_related(
            "items__category"
        ),
        pk=pk,
    )
    ref = request.GET.get("ref", "").strip()

    if request.method == "POST":
        action_name = request.POST.get("action")
        posted_ref = request.POST.get("ref", "").strip()

        if action_name == "verify":
            po.status = "APPROVED"
            po.approved_at = timezone.now()
            po.approved_by = request.user if request.user.is_authenticated else None
            po.save(update_fields=["status", "approved_at", "approved_by"])
            messages.success(request, "Order approved successfully.")

        elif action_name == "reject":
            po.status = "REJECTED"
            po.save(update_fields=["status"])
            messages.error(request, "Order rejected.")

        elif action_name == "modify":
            po.status = "UNDER_REVIEW"
            po.save(update_fields=["status"])
            messages.info(request, "Order marked for modification.")

        elif action_name == "discrepancy":
            po.is_discrepancy = True
            po.save(update_fields=["is_discrepancy"])
            messages.warning(request, "Order marked for discrepancy review.")

        target = reverse("supplier:po_qr", args=[po.pk])
        if posted_ref:
            target = f"{target}?ref={posted_ref}"
        return redirect(target)

    latest_item = (
        PurchaseOrderItem.objects.filter(purchase_order=po).order_by("-id").first()
    )
    scan_details = None
    if ref:
        scan_details = {
            "submission_ref": ref,
            "po_id": po.pk,
            "supplier_id": po.supplier.pk,
            "created_at": po.created_at,
            "outfit_type": latest_item.outfit_type if latest_item else "-",
            "size": latest_item.size if latest_item else "-",
            "quantity": latest_item.quantity if latest_item else "-",
            "price": latest_item.price if latest_item else "-",
            "url": request.build_absolute_uri(reverse("supplier:po_qr", args=[po.pk])),
        }

    return render(
        request,
        "supplier/po_qr.html",
        {
            "po": po,
            "scan_details": scan_details,
            "show_scan_actions": bool(ref),
            "ref": ref,
        },
    )


@login_required
def generate_sku_for_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if po.status != "APPROVED":
        messages.error(request, "Only approved orders can generate SKUs.")
        return redirect("supplier:po_qr", pk=pk)

    import random
    import string

    items = PurchaseOrderItem.objects.filter(purchase_order=po)
    for item in items:
        if not item.sku:
            random_suffix = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
            item.sku = f"SKU-{po.pk:04d}-{item.pk:03d}-{random_suffix}"
            item.sku_generated_at = timezone.now()
            item.save()

    po.status = "SKU_GENERATED"
    po.save(update_fields=["status"])
    messages.success(request, f"SKUs generated for {items.count()} items.")
    return redirect("supplier:po_qr", pk=pk)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'], url_path='discrepancy')
    def report_discrepancy(self, request):
        # Input: { "order_id": 22, "items": [ { "item_name": "...", "type": "MISSING", "qty": 2 } ] }
        order_id = request.data.get('order_id')
        items = request.data.get('items', [])

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        from inventory.models import Discrepancy

        created_discrepancies = []
        for item in items:
            discrepancy = Discrepancy.objects.create(
                order=order,
                item_name=item.get('item_name'),
                type=item.get('type'),
                quantity=item.get('qty', 0)
            )
            created_discrepancies.append(discrepancy.pk)

        return Response({
            "message": "Discrepancies reported",
            "ids": created_discrepancies
        }, status=status.HTTP_201_CREATED)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


@login_required
def create_secure_link(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)

    if request.method == "POST":
        expires_in_days = int(request.POST.get("expires_in_days", 7))

        link = SecureOrderLink.objects.create(
            supplier=supplier,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(days=expires_in_days),
        )

        secure_url = request.build_absolute_uri(
            reverse("supplier:secure_order_form", args=[link.token])
        )

        send_mail(
            subject=f"Order Form - {request.user}",
            message=f"Click here to submit your purchase order: {secure_url}\n\nThis link will expire in {expires_in_days} days.",
            from_email="admin@boutique.com",
            recipient_list=[supplier.email],
            fail_silently=False,
        )

        messages.success(
            request, f"Secure link created and emailed to {supplier.email}"
        )
        return redirect("supplier:supplier_list")

    return render(request, "supplier/create_secure_link.html", {"supplier": supplier})

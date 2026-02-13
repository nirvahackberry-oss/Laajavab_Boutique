# Testing Supplier Order Form & QR Code

## Prerequisites
1. Run server: `python manage.py runserver`
2. Create a supplier (optional - form can create one)
3. Create at least one Category in admin or via API

## Step 1: Create Secure Order Link

### Option A: Django Admin
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to Supplier → Secure Order Links
3. Click "Add Secure Order Link"
4. Select a supplier (optional)
5. Set expiry date (optional)
6. Save
7. Copy the generated UUID token

### Option B: Django Shell
```python
python manage.py shell

from supplier.models import SecureOrderLink, Supplier
from datetime import timedelta
from django.utils import timezone

# Create link (with or without supplier)
supplier = Supplier.objects.first()  # or None
link = SecureOrderLink.objects.create(
    supplier=supplier,
    expires_at=timezone.now() + timedelta(days=7)
)
print(f"Token: {link.token}")
```

## Step 2: Access Order Form
Visit: `http://127.0.0.1:8000/suppliers/secure/<TOKEN>/`

Replace `<TOKEN>` with the UUID from Step 1.

Example: `http://127.0.0.1:8000/suppliers/secure/a1b2c3d4-e5f6-7890-abcd-ef1234567890/`

## Step 3: Fill Order Form
- If no supplier linked: Enter supplier name, email, region
- Select outfit type, category, size
- Enter quantity and price
- Upload image (optional)
- Click Submit

## Step 4: View QR Code
After submission, you'll be redirected to the QR code page showing:
- Purchase Order ID
- Supplier name
- Status
- QR code image (printable)

## Step 5: Access QR Page Directly
URL: `http://127.0.0.1:8000/suppliers/po/<PO_ID>/qr/`

Replace `<PO_ID>` with the purchase order ID.

## Quick Test Script
```python
# In Django shell
from supplier.models import SecureOrderLink, Supplier
from core.models import Category

# 1. Create test data
supplier = Supplier.objects.create(name="Test Supplier", email="test@example.com", region="North")
Category.objects.create(name="Bridal", prefix="BR")

# 2. Create secure link
link = SecureOrderLink.objects.create(supplier=supplier)
print(f"Visit: http://127.0.0.1:8000/suppliers/secure/{link.token}/")

# 3. After form submission, check PO
from supplier.models import PurchaseOrder
po = PurchaseOrder.objects.last()
print(f"QR Page: http://127.0.0.1:8000/suppliers/po/{po.pk}/qr/")
```

## Troubleshooting
- **Link expired**: Check `expires_at` field in SecureOrderLink
- **No categories**: Create at least one Category first
- **QR not showing**: Check MEDIA_URL and MEDIA_ROOT in settings.py
- **404 on QR**: Ensure URL pattern matches: `/suppliers/po/<id>/qr/`

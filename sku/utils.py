import datetime
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from .models import ProductSKU

def generate_sku_code(category_prefix, outfit_type):
    # Format: CAT-TYPE-YYMM-SEQ
    now = datetime.datetime.now()
    yymm = now.strftime("%y%m")
    
    # Get next sequence
    # For simplicity, we can use the ID of the new SKU. 
    # But since we need to return the SKU code *before* saving sometimes or *after*?
    # The API creates the SKU. So we can save first, then generate code, then save again.
    # Or find max ID and increment. Saving first is safer for concurrency (if locked) or just using ID.
    
    # We will create the object first with empty SKU, then update it.
    return f"{category_prefix}-{outfit_type}-{yymm}-XXXX" # Placeholder

def generate_barcode_image(sku_code):
    # Generate barcode
    rv = BytesIO()
    # Code128 is commonly used for alphanumeric
    code = Code128(sku_code, writer=ImageWriter())
    code.write(rv)
    return ContentFile(rv.getvalue(), f"{sku_code}.png")

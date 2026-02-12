# Development Guidelines

## Code Quality Standards

### File Structure Conventions
- **Empty __init__.py files**: All Django app packages and migration directories use empty `__init__.py` files for package initialization
- **Standard Django app structure**: Each app follows Django's standard layout with models.py, views.py, serializers.py, admin.py, tests.py
- **Migration directories**: Every app includes a migrations/ subdirectory with __init__.py for database schema versioning

### Naming Conventions
- **Model classes**: PascalCase (e.g., ProductSKU, OutfitType, OrderItem)
- **Model fields**: snake_case (e.g., sku_code, created_at, phone_number)
- **Serializer classes**: Model name + "Serializer" suffix (e.g., CategorySerializer, ProductSKUSerializer)
- **ViewSet classes**: Model name + "ViewSet" suffix (e.g., AlterationViewSet, SupplierViewSet)
- **URL patterns**: kebab-case for multi-word endpoints (e.g., 'outfit-types', 'order-items')
- **Router basenames**: kebab-case matching URL patterns (e.g., basename='outfit-type')

### Code Formatting
- **Line endings**: CRLF (Windows-style \r\n) used throughout the codebase
- **Imports organization**: Standard library → Django imports → Third-party → Local imports
- **String quotes**: Single quotes for strings, double quotes for docstrings
- **Indentation**: 4 spaces (Python standard)

## Django Model Patterns

### Model Field Standards
```python
# CharField with max_length always specified
name = models.CharField(max_length=255)

# Unique fields with help_text for documentation
prefix = models.CharField(max_length=10, unique=True, help_text="e.g., BR, CW, FW")

# ForeignKey with on_delete behavior explicitly defined
category = models.ForeignKey(Category, on_delete=models.CASCADE)
tailor = models.ForeignKey(Tailor, on_delete=models.SET_NULL, null=True, blank=True)

# DecimalField for monetary values
price = models.DecimalField(max_digits=10, decimal_places=2)

# Timestamps with auto_now_add and auto_now
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

# ImageField with upload_to directory
barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

# Boolean fields with default values
is_available = models.BooleanField(default=True)
```

### Status Choice Pattern
```python
# Define choices as class-level constants
STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('RECEIVED', 'Received'),
    ('IN_PROGRESS', 'In Progress'),
    ('READY', 'Ready for Pickup'),
    ('COMPLETED', 'Completed'),
]

# Use in CharField with choices parameter
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
```

### Model __str__ Methods
```python
# Always implement __str__ for admin and debugging
def __str__(self):
    return self.name  # For simple models

def __str__(self):
    return f"{self.name} ({self.prefix})"  # With additional context

def __str__(self):
    return f"Order {self.id} - {self.supplier.name}"  # For relational context
```

### Related Names
```python
# Use related_name for reverse relationships
order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='skus')
customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='alterations')
order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
```

## Django REST Framework Patterns

### Serializer Conventions
```python
# ModelSerializer with Meta class
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Read-only fields for auto-generated values
prefix = serializers.CharField(read_only=True)

# Nested serializers with source parameter
category_details = CategorySerializer(source='category', read_only=True)

# Related field serialization
customer_name = serializers.CharField(source='customer.name', read_only=True)

# Nested many-to-many or reverse relationships
items = OrderItemSerializer(many=True, read_only=True)
alterations = AlterationNestedSerializer(many=True, read_only=True)
```

### Custom Serializers for Creation
```python
# Separate serializer for create operations
class AlterationCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    outfit_type = serializers.IntegerField()
    
    def create(self, validated_data):
        # Custom creation logic
        customer = Customer.objects.get(id=validated_data['customer_id'])
        alteration = Alteration.objects.create(
            customer=customer,
            status='PENDING'
        )
        return alteration
```

### ViewSet Patterns
```python
# Standard ModelViewSet with queryset and serializer_class
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Dynamic serializer selection based on action
def get_serializer_class(self) -> Type:
    if self.action == 'create':
        return AlterationCreateSerializer
    return AlterationSerializer

# Custom create method with validation
def create(self, request, *args, **kwargs):
    name = request.data.get('name', '').strip()
    if not name:
        return Response(
            {"error": "name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    # Custom logic...
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### Custom Actions with @action Decorator
```python
# Custom endpoint with detail=True (requires pk)
@action(detail=True, methods=['get'], url_path='barcode')
def get_barcode(self, request, pk=None):
    sku = self.get_object()
    return FileResponse(sku.barcode_image.open(), content_type='image/png')

# Custom endpoint with detail=False (collection-level)
@action(detail=False, methods=['post'], url_path='generate')
def generate_sku(self, request):
    input_data = request.data
    # Processing logic...
    return Response(data, status=status.HTTP_201_CREATED)

# PATCH endpoint for partial updates
@action(detail=True, methods=['patch'], url_path='status')
def update_status(self, request, pk=None):
    alteration = self.get_object()
    new_status = request.data.get('status')
    alteration.status = new_status
    alteration.save()
    return Response({'status': alteration.status}, status=status.HTTP_200_OK)
```

## API Design Patterns

### URL Router Configuration
```python
# Use DefaultRouter for automatic URL generation
router = routers.DefaultRouter()

# Register viewsets with descriptive basenames
router.register(r'sku', ProductSKUViewSet, basename='sku')
router.register(r'outfit-types', OutfitTypeViewSet, basename='outfit-type')

# Include router URLs in urlpatterns
urlpatterns = [
    path('', include(router.urls)),
    path('forecast/', include('forecasting.urls')),
]
```

### Error Response Pattern
```python
# Consistent error response structure
return Response(
    {"error": "descriptive error message"},
    status=status.HTTP_400_BAD_REQUEST
)

# Validation in views before processing
if not all([category_id, outfit_type_id, supplier_id]):
    return Response(
        {"error": "category_id, outfit_type_id, and supplier_id are required"},
        status=status.HTTP_400_BAD_REQUEST
    )
```

### Success Response Pattern
```python
# Return created resource with 201 status
return Response(serializer.data, status=status.HTTP_201_CREATED)

# Return custom response data
return Response({
    'id': alteration.id,
    'status': alteration.status,
    'message': 'Operation successful'
}, status=status.HTTP_200_OK)
```

## Business Logic Patterns

### Auto-Generated Codes
```python
# Pattern: Extract prefix from name, ensure uniqueness with counter
base_prefix = ''.join([c for c in name if c.isalpha()])[:2].upper()

prefix = base_prefix
counter = 2
while Category.objects.filter(prefix=prefix).exists():
    prefix = f"{base_prefix}{counter}"
    counter += 1

category = Category.objects.create(name=name, prefix=prefix)
```

### SKU Code Generation Pattern
```python
# Format: CAT-TYPE-SUP-YYMM-SEQ
now = datetime.datetime.now()
yymm = now.strftime("%y%m")
supplier_code = f"S{supplier.pk}"

# Get sequence number for current month
month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
order_seq = ProductSKU.objects.filter(
    created_at__gte=month_start
).aggregate(Max('id'))['id__max'] or 0
order_seq = f"{order_seq + 1:04d}"

code = f"{category.prefix}-{outfit_type.code}-{supplier_code}-{yymm}-{order_seq}"
```

### Related Object Creation
```python
# Create related objects in same transaction
sku = ProductSKU.objects.create(
    category=category,
    outfit_type=outfit_type,
    price=price
)

# Create dependent object
from inventory.models import InventoryItem
InventoryItem.objects.create(sku=sku, quantity=1)
```

## Utility Patterns

### Barcode Generation
```python
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile

def generate_barcode_image(sku_code):
    rv = BytesIO()
    code = Code128(sku_code, writer=ImageWriter())
    code.write(rv)
    return ContentFile(rv.getvalue(), f"{sku_code}.png")

# Usage in views
barcode_img = generate_barcode_image(code)
sku.barcode_image.save(f"{code}.png", barcode_img, save=True)
```

### PDF Generation with ReportLab
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.http import FileResponse

buffer = BytesIO()
p = canvas.Canvas(buffer, pagesize=letter)

p.drawString(100, 750, f"Alteration ID: {alteration.id}")
p.drawString(100, 730, f"Customer: {alteration.customer.name}")

p.save()
buffer.seek(0)

return FileResponse(buffer, content_type='application/pdf', filename=f'tag_{alteration.id}.pdf')
```

### File Response Pattern
```python
# Return image files
from django.http import FileResponse
return FileResponse(sku.barcode_image.open(), content_type='image/png')

# Return PDF files
return FileResponse(buffer, content_type='application/pdf', filename='document.pdf')
```

## Type Hints and Documentation

### Type Annotations
```python
from typing import Type

# Method return type annotations
def get_serializer_class(self) -> Type:
    if self.action == 'create':
        return AlterationCreateSerializer
    return AlterationSerializer
```

### Help Text Documentation
```python
# Use help_text for field documentation
prefix = models.CharField(max_length=10, unique=True, help_text="e.g., BR, CW, FW")
outfit_type = models.CharField(max_length=50, help_text="e.g., LHG (Lehenga)")
specialties = models.CharField(max_length=255, help_text="e.g., Bridal, Suits")
```

## Service Layer Pattern

### AI/ML Service Classes
```python
# Encapsulate business logic in service classes
class AlterationPredictor:
    # Class-level configuration
    OUTFIT_TIMES = {
        'Bridal': 7,
        'Lehenga': 5,
        'Suit': 3,
    }
    
    def predict_pickup_date(self, outfit_type, tailor_id=None):
        base_days = self.OUTFIT_TIMES.get(outfit_type, 3)
        # Calculation logic...
        return pickup_date, confidence_score

# Usage in views
predictor = AlterationPredictor()
pickup_date, confidence = predictor.predict_pickup_date(outfit_type, tailor_id)
```

## Query Optimization

### Use get_object_or_404
```python
from django.shortcuts import get_object_or_404

# Prefer get_object_or_404 over try/except
category = get_object_or_404(Category, id=category_id)
outfit_type = get_object_or_404(OutfitType, id=outfit_type_id)
```

### Aggregate Queries
```python
from django.db.models import Max

# Use aggregation for calculations
max_id = ProductSKU.objects.filter(
    created_at__gte=month_start
).aggregate(Max('id'))['id__max'] or 0
```

## Testing Conventions
- Each app includes tests.py for unit tests
- Test files follow Django's standard testing structure
- Use Django's TestCase for database-dependent tests

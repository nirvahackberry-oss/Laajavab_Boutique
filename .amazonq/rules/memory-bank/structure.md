# Project Structure

## Directory Organization

### Root Level
```
Laajavab_Project/
├── alteration/          # Alteration services module
├── api/                 # API routing and endpoints
├── core/                # Core application functionality
├── digital_boutique/    # Django project configuration
├── forecasting/         # Demand forecasting module
├── inventory/           # Inventory management
├── sku/                 # SKU management
├── supplier/            # Supplier management
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Core Components

### digital_boutique/ (Project Configuration)
Main Django project directory containing:
- **settings.py**: Django configuration, database settings, installed apps
- **urls.py**: Root URL routing, admin and API path configuration
- **wsgi.py**: WSGI application entry point
- **asgi.py**: ASGI application entry point for async support

### api/ (API Layer)
Central API routing module:
- **urls.py**: Aggregates all app-specific API endpoints
- **views.py**: Shared API views and utilities
- Serves as the main entry point for RESTful API access

### core/ (Core Functionality)
Foundation module providing:
- **models.py**: Base models and shared entities (OutfitType, etc.)
- **serializers.py**: Core DRF serializers
- **views.py**: Core business logic views
- Shared functionality used across other modules

### sku/ (SKU Management)
Product identification and tracking:
- **models.py**: ProductSKU model with barcode support
- **serializers.py**: SKU data serialization
- **utils.py**: Barcode generation and SKU utilities
- **views.py**: SKU CRUD operations
- Handles product variants, barcodes, and outfit type associations

### inventory/ (Inventory Management)
Stock and inventory control:
- **models.py**: Inventory tracking models
- **serializers.py**: Inventory data serialization
- **views.py**: Inventory operations and queries
- Manages stock levels and product availability

### supplier/ (Supplier Management)
Supplier and order management:
- **models.py**: Supplier and Order models
- **serializers.py**: Supplier data serialization
- **views.py**: Supplier CRUD and order tracking
- Handles supplier relationships and purchase orders

### alteration/ (Alteration Services)
Customer alteration request handling:
- **models.py**: Alteration, Customer, and Tailor models
- **serializers.py**: Alteration data serialization
- **ai_service.py**: AI-powered service recommendations
- **views.py**: Alteration request processing
- Manages customer service and tailor assignments

### forecasting/ (Forecasting Module)
Demand prediction and analytics:
- **services.py**: Forecasting algorithms and logic
- **views.py**: Forecasting API endpoints
- **management/commands/**: Custom Django management commands
- Provides inventory prediction capabilities

## Architectural Patterns

### Django App Architecture
- **Modular Design**: Each business domain is a separate Django app
- **Separation of Concerns**: Models, views, serializers separated by responsibility
- **Reusable Components**: Core app provides shared functionality

### Database Layer
- **PostgreSQL Backend**: Relational database for data persistence
- **Django ORM**: Object-relational mapping for database operations
- **Migrations**: Version-controlled schema changes in each app's migrations/

### API Architecture
- **RESTful Design**: Resource-based API endpoints
- **Django REST Framework**: Serialization, authentication, and API views
- **Centralized Routing**: API app aggregates all endpoints
- **Filtering Support**: django-filter for query parameter filtering

### Component Relationships
```
api/ (Entry Point)
  ├── core/ (Shared Models & Logic)
  ├── sku/ (Product Identification)
  │    └── Uses: core.OutfitType
  ├── inventory/ (Stock Management)
  │    └── Uses: sku.ProductSKU
  ├── supplier/ (Supplier & Orders)
  │    └── Uses: sku.ProductSKU
  ├── alteration/ (Customer Service)
  │    └── Uses: ai_service for recommendations
  └── forecasting/ (Analytics)
       └── Uses: inventory, sku data
```

### Media Handling
- **MEDIA_ROOT**: Base directory for uploaded files
- **Barcode Images**: Stored via ProductSKU.barcode_image
- **Static Files**: Served in DEBUG mode via Django static file handling

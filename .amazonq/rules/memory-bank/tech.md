# Technology Stack

## Programming Languages
- **Python**: 3.10 or higher (primary language)
- **SQL**: PostgreSQL dialect for database operations

## Core Framework
- **Django**: 5.0+ (5.2.11 in use)
  - Web framework and ORM
  - Admin interface
  - Authentication and authorization
  - Migration system

## API Framework
- **Django REST Framework**: 3.16.1+
  - RESTful API development
  - Serialization and deserialization
  - API views and viewsets
  - Authentication and permissions

## Database
- **PostgreSQL**: 12 or higher
  - Primary database engine
  - Connection via psycopg2-binary
  - Database: laajavab_db
  - Default credentials: postgres/postgres
  - Host: localhost:5432

## Key Dependencies

### Data Processing
- **django-filter**: Query parameter filtering for APIs
- **Pillow**: Image processing and handling
- **python-barcode**: Barcode generation for SKUs

### Database Adapter
- **psycopg2-binary**: PostgreSQL adapter for Python

## Development Tools

### Project Management
- **manage.py**: Django's command-line utility
  - Run development server
  - Execute migrations
  - Create superusers
  - Custom management commands

### Configuration Files
- **requirements.txt**: Python package dependencies
- **pyproject.toml**: Python project metadata
- **pyrightconfig.json**: Python type checking configuration
- **uv.lock**: Dependency lock file

## Development Commands

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Running the Application
```bash
# Start development server
python manage.py runserver

# Server runs on http://127.0.0.1:8000/
# Admin interface: http://127.0.0.1:8000/admin/
# API endpoints: http://127.0.0.1:8000/api/
```

### Database Operations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Management Commands
```bash
# Access Django shell
python manage.py shell

# Run custom forecasting commands
python manage.py <forecasting_command>
```

## Environment Configuration

### Database Settings (settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'laajavab_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Installed Apps
- django.contrib.admin
- django.contrib.auth
- django.contrib.contenttypes
- django.contrib.sessions
- django.contrib.messages
- django.contrib.staticfiles
- rest_framework
- django_filters
- core
- sku
- inventory
- supplier
- alteration
- forecasting
- api

### Media Configuration
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## API Access
- **Base URL**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Format**: JSON (default)
- **Authentication**: Django session authentication (default)

## Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)
- Active PostgreSQL server on localhost:5432

# Laajavab Project

A Django REST Framework application for managing a digital boutique.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher

## Setup Instructions

### Start PostgreSQL
Ensure your Postgres server is running on localhost:5432

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

3. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- **alteration/**: Handles product alterations
- **api/**: API endpoints
- **core/**: Core application functionality
- **inventory/**: Inventory management
- **sku/**: SKU (Stock Keeping Unit) management
- **supplier/**: Supplier management
- **digital_boutique/**: Main project configuration

## Dependencies

- Django 5.2.11+
- Django REST Framework 3.16.1+
- PostgreSQL (via psycopg2-binary)
- Pillow (image handling)
- python-barcode (barcode generation)
- ReportLab (PDF generation)

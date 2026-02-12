import os
from django.core.management.base import BaseCommand
from django.db import connection
import pandas as pd

class Command(BaseCommand):
    help = 'Export sales data for demand forecasting'

    def handle(self, *args, **options):
        query = """
        SELECT 
            oi.size,
            c.name as category,
            oi.quantity,
            o.created_at::date as order_date,
            sku.price
        FROM supplier_orderitem oi
        JOIN supplier_order o ON oi.order_id = o.id
        JOIN core_category c ON o.category_id = c.id
        LEFT JOIN sku_productsku sku ON sku.category_id = c.id
        WHERE o.status = 'COMPLETED'
        ORDER BY o.created_at
        """
        
        df = pd.read_sql(query, connection)
        df.to_csv('sales_data.csv', index=False)
        self.stdout.write(f'Exported {len(df)} records to sales_data.csv')
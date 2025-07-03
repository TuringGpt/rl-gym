"""Seed sales metrics data

Revision ID: 006
Revises: 005
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import json

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Create connection
    connection = op.get_bind()
    
    # Generate sample sales metrics data
    base_date = datetime(2024, 1, 1)
    
    sales_metrics_data = []
    
    # Generate daily metrics for the past 30 days
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        next_date = current_date + timedelta(days=1)
        
        # Generate metrics for different buyer types
        for buyer_type in ['All', 'B2B', 'B2C']:
            unit_count = 150 if buyer_type == 'All' else (50 if buyer_type == 'B2B' else 100)
            order_count = 25 if buyer_type == 'All' else (8 if buyer_type == 'B2B' else 17)
            order_item_count = 30 if buyer_type == 'All' else (10 if buyer_type == 'B2B' else 20)
            
            # Add some randomness
            unit_count += (i * 3) % 50
            order_count += (i * 2) % 10
            order_item_count += (i * 2) % 15
            
            total_sales = unit_count * 25.99  # Average price per unit
            average_unit_price = total_sales / unit_count if unit_count > 0 else 0
            
            sales_metrics_data.append({
                'interval': f"{current_date.isoformat()}/{next_date.isoformat()}",
                'granularity': 'Day',
                'unit_count': unit_count,
                'order_item_count': order_item_count,
                'order_count': order_count,
                'average_unit_price': round(average_unit_price, 2),
                'total_sales': round(total_sales, 2),
                'currency_code': 'USD',
                'buyer_type': buyer_type,
                'marketplace_ids': json.dumps(['ATVPDKIKX0DER']),
                'asin': None,
                'sku': None,
                'period_start': current_date,
                'period_end': next_date,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
    
    # Generate hourly metrics for the past 24 hours
    for i in range(24):
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=i)
        next_hour = current_hour + timedelta(hours=1)
        
        unit_count = 6 + (i % 10)
        order_count = 2 + (i % 3)
        order_item_count = 3 + (i % 5)
        
        total_sales = unit_count * 28.99
        average_unit_price = total_sales / unit_count if unit_count > 0 else 0
        
        sales_metrics_data.append({
            'interval': f"{current_hour.isoformat()}/{next_hour.isoformat()}",
            'granularity': 'Hour',
            'unit_count': unit_count,
            'order_item_count': order_item_count,
            'order_count': order_count,
            'average_unit_price': round(average_unit_price, 2),
            'total_sales': round(total_sales, 2),
            'currency_code': 'USD',
            'buyer_type': 'All',
            'marketplace_ids': json.dumps(['ATVPDKIKX0DER']),
            'asin': None,
            'sku': None,
            'period_start': current_hour,
            'period_end': next_hour,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    # Generate ASIN-specific metrics
    asins = ['B07XJ8C8F7', 'B08N5WRWNW', 'B085QBXMVQ', 'B07Z3JBQG5', 'B08L6BQZM3']
    for asin in asins:
        for i in range(7):  # Past 7 days
            current_date = base_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            unit_count = 20 + (i * 2)
            order_count = 5 + (i % 3)
            order_item_count = 8 + (i % 4)
            
            total_sales = unit_count * 35.99
            average_unit_price = total_sales / unit_count if unit_count > 0 else 0
            
            sales_metrics_data.append({
                'interval': f"{current_date.isoformat()}/{next_date.isoformat()}",
                'granularity': 'Day',
                'unit_count': unit_count,
                'order_item_count': order_item_count,
                'order_count': order_count,
                'average_unit_price': round(average_unit_price, 2),
                'total_sales': round(total_sales, 2),
                'currency_code': 'USD',
                'buyer_type': 'All',
                'marketplace_ids': json.dumps(['ATVPDKIKX0DER']),
                'asin': asin,
                'sku': None,
                'period_start': current_date,
                'period_end': next_date,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
    
    # Insert sales metrics data
    if sales_metrics_data:
        # Build the INSERT statement
        insert_sql = """
            INSERT INTO sales_metrics (
                interval, granularity, unit_count, order_item_count, order_count,
                average_unit_price, total_sales, currency_code, buyer_type, marketplace_ids,
                asin, sku, period_start, period_end, created_at, updated_at
            ) VALUES (
                :interval, :granularity, :unit_count, :order_item_count, :order_count,
                :average_unit_price, :total_sales, :currency_code, :buyer_type, :marketplace_ids,
                :asin, :sku, :period_start, :period_end, :created_at, :updated_at
            )
        """
        
        # Execute the insert
        connection.execute(text(insert_sql), sales_metrics_data)
    
    print(f"✅ Inserted {len(sales_metrics_data)} sales metrics records")


def downgrade():
    # Create connection
    connection = op.get_bind()
    
    # Clear sales metrics data
    connection.execute(text("DELETE FROM sales_metrics"))
    
    print("🗑️  Cleared sales metrics data")
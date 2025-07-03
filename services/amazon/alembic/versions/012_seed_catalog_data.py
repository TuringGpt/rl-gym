"""seed catalog data

Revision ID: 012_seed_catalog_data
Revises: 011_add_catalog_apis_support
Create Date: 2025-03-07 18:31:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, JSON, DateTime
import json
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Define table references for bulk inserts
    catalog_categories = table('catalog_categories',
        column('product_category_id', String),
        column('marketplace_id', String),
        column('product_category_name', String),
        column('parent_category_id', String),
    )
    
    # Insert sample catalog categories
    categories_data = [
        # Electronics categories
        {
            'product_category_id': '172282',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Electronics',
            'parent_category_id': None
        },
        {
            'product_category_id': '1266092011',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Television & Video',
            'parent_category_id': '172282'
        },
        {
            'product_category_id': '172659',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Televisions',
            'parent_category_id': '1266092011'
        },
        {
            'product_category_id': '21489946011',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'QLED TVs',
            'parent_category_id': '172659'
        },
        {
            'product_category_id': '6463520011',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'OLED TVs',
            'parent_category_id': '172659'
        },
        # Home & Garden categories
        {
            'product_category_id': '468240',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Tools & Home Improvement',
            'parent_category_id': None
        },
        {
            'product_category_id': '493964',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Electronics',
            'parent_category_id': '468240'
        },
        # Luggage categories
        {
            'product_category_id': '15743231',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Luggage & Travel Gear',
            'parent_category_id': None
        },
        {
            'product_category_id': '15743241',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Luggage',
            'parent_category_id': '15743231'
        },
        {
            'product_category_id': '15743251',
            'marketplace_id': 'ATVPDKIKX0DER',
            'product_category_name': 'Carry-Ons',
            'parent_category_id': '15743241'
        }
    ]
    
    op.bulk_insert(catalog_categories, categories_data)
    
    # Update existing catalog items with enhanced data
    connection = op.get_bind()
    
    # Update Samsung TV item with comprehensive data
    samsung_tv_data = {
        'seller_id': 'A2EUQ1WTGCTBG2',
        'manufacturer': 'Samsung',
        'model_number': 'QN82Q60RAFXZA',
        'size_name': '82-Inch',
        'style_name': 'TV only',
        'product_category_id': '21489946011',
        'vendor_details': {
            'brandCode': 'SAMF9',
            'categoryCode': '50400100',
            'manufacturerCode': 'SAMF9',
            'manufacturerCodeParent': 'SAMF9',
            'productGroup': 'Home Entertainment',
            'replenishmentCategory': 'NEW_PRODUCT',
            'subcategoryCode': '50400150'
        },
        'identifiers': {
            'EAN': '0887276302195',
            'UPC': '887276302195',
            'GTIN': '00887276302195'
        },
        'images': [
            {
                'variant': 'MAIN',
                'link': 'https://m.media-amazon.com/images/I/91uohwV+k3L.jpg',
                'height': 1707,
                'width': 2560
            },
            {
                'variant': 'MAIN',
                'link': 'https://m.media-amazon.com/images/I/51DZzp3w3vL.jpg',
                'height': 333,
                'width': 500
            },
            {
                'variant': 'PT01',
                'link': 'https://m.media-amazon.com/images/I/81w2rTVShlL.jpg',
                'height': 2560,
                'width': 2560
            }
        ],
        'sales_rankings': [
            {
                'title': 'QLED TVs',
                'link': 'http://www.amazon.com/gp/bestsellers/electronics/21489946011',
                'rank': 113
            },
            {
                'title': 'Electronics',
                'link': 'http://www.amazon.com/gp/bestsellers/electronics',
                'rank': 72855
            }
        ],
        'dimensions': {
            'item': {
                'height': {'unit': 'inches', 'value': 41.4},
                'length': {'unit': 'inches', 'value': 2.4},
                'width': {'unit': 'inches', 'value': 72.4},
                'weight': {'unit': 'pounds', 'value': 107.6}
            },
            'package': {
                'height': {'unit': 'inches', 'value': 10.49999998929},
                'length': {'unit': 'inches', 'value': 79.9999999184},
                'width': {'unit': 'inches', 'value': 47.99999995104},
                'weight': {'unit': 'kilograms', 'value': 62.142}
            }
        },
        'browse_node_info': {
            'browse_nodes': [
                {
                    'displayName': 'QLED TVs',
                    'classificationId': '21489946011',
                    'parent': {
                        'displayName': 'Televisions',
                        'classificationId': '172659',
                        'parent': {
                            'displayName': 'Television & Video',
                            'classificationId': '1266092011',
                            'parent': {
                                'displayName': 'Electronics',
                                'classificationId': '172282'
                            }
                        }
                    }
                }
            ]
        }
    }
    
    connection.execute(
        sa.text("""
            UPDATE catalog_items 
            SET seller_id = :seller_id,
                manufacturer = :manufacturer,
                model_number = :model_number,
                size_name = :size_name,
                style_name = :style_name,
                product_category_id = :product_category_id,
                vendor_details = :vendor_details,
                identifiers = :identifiers,
                images = :images,
                sales_rankings = :sales_rankings,
                dimensions = :dimensions,
                browse_node_info = :browse_node_info
            WHERE asin = 'B07N4M94X4' AND marketplace_id = 'ATVPDKIKX0DER'
        """),
        {
            'seller_id': samsung_tv_data['seller_id'],
            'manufacturer': samsung_tv_data['manufacturer'],
            'model_number': samsung_tv_data['model_number'],
            'size_name': samsung_tv_data['size_name'],
            'style_name': samsung_tv_data['style_name'],
            'product_category_id': samsung_tv_data['product_category_id'],
            'vendor_details': json.dumps(samsung_tv_data['vendor_details']),
            'identifiers': json.dumps(samsung_tv_data['identifiers']),
            'images': json.dumps(samsung_tv_data['images']),
            'sales_rankings': json.dumps(samsung_tv_data['sales_rankings']),
            'dimensions': json.dumps(samsung_tv_data['dimensions']),
            'browse_node_info': json.dumps(samsung_tv_data['browse_node_info'])
        }
    )
    
    # Add more sample catalog items for different categories
    catalog_items = table('catalog_items',
        column('asin', String),
        column('marketplace_id', String),
        column('parent_asin', String),
        column('item_name', String),
        column('brand', String),
        column('classification', String),
        column('color', String),
        column('size', String),
        column('style', String),
        column('seller_id', String),
        column('manufacturer', String),
        column('model_number', String),
        column('size_name', String),
        column('style_name', String),
        column('product_category_id', String),
        column('vendor_details', JSON),
        column('identifiers', JSON),
        column('images', JSON),
        column('product_types', JSON),
        column('sales_rankings', JSON),
        column('browse_node_info', JSON),
        column('dimensions', JSON)
    )
    
    additional_items = [
        {
            'asin': 'B071VG5N9D',
            'marketplace_id': 'ATVPDKIKX0DER',
            'parent_asin': None,
            'item_name': 'Hardside Carry-On Spinner Suitcase Luggage',
            'brand': 'TravelPro',
            'classification': 'LUGGAGE',
            'color': 'Black',
            'size': 'Carry-On',
            'style': 'Hardside',
            'seller_id': 'A3EXEMPLO123',
            'manufacturer': 'TravelPro',
            'model_number': 'TP-HD-001',
            'size_name': 'Carry-On',
            'style_name': 'Hardside Spinner',
            'product_category_id': '15743251',
            'vendor_details': json.dumps({
                'brandCode': 'TRVPRO',
                'categoryCode': '15743251',
                'manufacturerCode': 'TRVPRO',
                'productGroup': 'Luggage & Travel Gear',
                'replenishmentCategory': 'STANDARD'
            }),
            'identifiers': json.dumps({
                'UPC': '123456789012',
                'EAN': '1234567890123'
            }),
            'images': json.dumps([
                {
                    'variant': 'MAIN',
                    'link': 'https://www.example.com/luggage.png',
                    'height': 500,
                    'width': 500
                }
            ]),
            'product_types': json.dumps(['LUGGAGE']),
            'sales_rankings': json.dumps([
                {
                    'title': 'Luggage',
                    'rank': 1250
                }
            ]),
            'browse_node_info': json.dumps({
                'browse_nodes': [
                    {
                        'displayName': 'Carry-Ons',
                        'classificationId': '15743251'
                    }
                ]
            }),
            'dimensions': json.dumps({
                'item': {
                    'height': {'unit': 'inches', 'value': 22},
                    'length': {'unit': 'inches', 'value': 14},
                    'width': {'unit': 'inches', 'value': 9},
                    'weight': {'unit': 'pounds', 'value': 8.5}
                }
            })
        }
    ]
    
    op.bulk_insert(catalog_items, additional_items)


def downgrade() -> None:
    # Remove the added catalog items
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM catalog_items WHERE asin = 'B071VG5N9D'")
    )
    
    # Reset Samsung TV data
    connection.execute(
        sa.text("""
            UPDATE catalog_items 
            SET seller_id = NULL,
                manufacturer = NULL,
                model_number = NULL,
                size_name = NULL,
                style_name = NULL,
                product_category_id = NULL,
                vendor_details = NULL
            WHERE asin = 'B07N4M94X4' AND marketplace_id = 'ATVPDKIKX0DER'
        """)
    )
    
    # Remove catalog categories
    connection.execute(
        sa.text("DELETE FROM catalog_categories")
    )
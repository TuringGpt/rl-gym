"""seed product fees data

Revision ID: 008
Revises: 007
Create Date: 2025-01-07 17:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Numeric, JSON, DateTime
import json
from decimal import Decimal

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    # Define the product_fees table structure for bulk insert
    product_fees_table = table('product_fees',
        column('seller_sku', String),
        column('asin', String),
        column('marketplace_id', String),
        column('seller_id', String),
        column('product_type', String),
        column('item_condition', String),
        column('fulfillment_fee', Numeric),
        column('referral_fee_rate', Numeric),
        column('storage_fee', Numeric),
        column('removal_fee', Numeric),
        column('disposal_fee', Numeric),
        column('return_processing_fee', Numeric),
        column('high_volume_listing_fee', Numeric),
        column('multichannel_fulfillment_fee', Numeric),
        column('weight', Numeric),
        column('dimensions', JSON),
        column('category', String)
    )
    
    # Sample product fees data
    fees_data = []
    
    # Electronics category
    electronics_products = [
        {"sku": "ELECTRONICS-001", "asin": "B08N5WRWNW", "weight": 1.5, "dims": {"length": 8, "width": 6, "height": 2}},
        {"sku": "ELECTRONICS-002", "asin": "B07XJ8C8F5", "weight": 2.3, "dims": {"length": 10, "width": 8, "height": 3}},
        {"sku": "PHONE-CASE-001", "asin": "B08L5B7J9K", "weight": 0.2, "dims": {"length": 6, "width": 3, "height": 0.5}},
        {"sku": "CABLE-USB-001", "asin": "B07F7WQZPK", "weight": 0.5, "dims": {"length": 5, "width": 4, "height": 1}},
        {"sku": "HEADPHONE-001", "asin": "B08PZHYWJS", "weight": 1.0, "dims": {"length": 9, "width": 7, "height": 4}},
    ]
    
    for product in electronics_products:
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'ATVPDKIKX0DER',
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'ELECTRONICS',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('3.50'),
            'referral_fee_rate': Decimal('0.0800'),  # 8% for electronics
            'storage_fee': Decimal('0.35'),
            'removal_fee': Decimal('0.50'),
            'disposal_fee': Decimal('0.25'),
            'return_processing_fee': Decimal('0.25'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('4.00'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Electronics'
        })
    
    # Home & Kitchen category
    home_products = [
        {"sku": "HOME-KITCHEN-001", "asin": "B08R3K9L2M", "weight": 3.0, "dims": {"length": 12, "width": 10, "height": 8}},
        {"sku": "KITCHEN-TOOL-001", "asin": "B07K9M8N3P", "weight": 1.2, "dims": {"length": 8, "width": 4, "height": 2}},
        {"sku": "STORAGE-BOX-001", "asin": "B08J7H5G4F", "weight": 2.5, "dims": {"length": 15, "width": 12, "height": 10}},
        {"sku": "KITCHEN-GADGET-001", "asin": "B07Y9W8V7U", "weight": 0.8, "dims": {"length": 6, "width": 4, "height": 3}},
        {"sku": "HOME-DECOR-001", "asin": "B08M4L3K2J", "weight": 1.8, "dims": {"length": 10, "width": 8, "height": 6}},
    ]
    
    for product in home_products:
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'ATVPDKIKX0DER',
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'HOME_AND_KITCHEN',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('4.20'),
            'referral_fee_rate': Decimal('0.1500'),  # 15% for home & kitchen
            'storage_fee': Decimal('0.45'),
            'removal_fee': Decimal('0.75'),
            'disposal_fee': Decimal('0.35'),
            'return_processing_fee': Decimal('0.50'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('5.50'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Home & Kitchen'
        })
    
    # Clothing category
    clothing_products = [
        {"sku": "CLOTHING-SHIRT-001", "asin": "B09F6G7H8I", "weight": 0.5, "dims": {"length": 10, "width": 8, "height": 1}},
        {"sku": "CLOTHING-PANTS-001", "asin": "B08D5E6F7G", "weight": 0.8, "dims": {"length": 12, "width": 10, "height": 2}},
        {"sku": "ACCESSORIES-001", "asin": "B07C4D5E6F", "weight": 0.3, "dims": {"length": 6, "width": 4, "height": 1}},
        {"sku": "SHOES-SNEAKER-001", "asin": "B08B3C4D5E", "weight": 1.5, "dims": {"length": 13, "width": 8, "height": 5}},
        {"sku": "CLOTHING-JACKET-001", "asin": "B09A2B3C4D", "weight": 1.2, "dims": {"length": 14, "width": 12, "height": 3}},
    ]
    
    for product in clothing_products:
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'ATVPDKIKX0DER',
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'CLOTHING',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('2.85'),
            'referral_fee_rate': Decimal('0.1700'),  # 17% for clothing
            'storage_fee': Decimal('0.25'),
            'removal_fee': Decimal('0.40'),
            'disposal_fee': Decimal('0.20'),
            'return_processing_fee': Decimal('0.30'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('3.50'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Clothing, Shoes & Jewelry'
        })
    
    # Books category
    books_products = [
        {"sku": "BOOK-FICTION-001", "asin": "B08Z9Y8X7W", "weight": 1.0, "dims": {"length": 9, "width": 6, "height": 1}},
        {"sku": "BOOK-TECH-001", "asin": "B07Y8X7W6V", "weight": 1.5, "dims": {"length": 10, "width": 7, "height": 2}},
        {"sku": "BOOK-COOKING-001", "asin": "B08X7W6V5U", "weight": 2.0, "dims": {"length": 11, "width": 8, "height": 2}},
        {"sku": "MAGAZINE-001", "asin": "B07W6V5U4T", "weight": 0.3, "dims": {"length": 11, "width": 8, "height": 0.3}},
        {"sku": "TEXTBOOK-001", "asin": "B08V5U4T3S", "weight": 3.0, "dims": {"length": 12, "width": 9, "height": 3}},
    ]
    
    for product in books_products:
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'ATVPDKIKX0DER',
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'BOOKS',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('1.95'),
            'referral_fee_rate': Decimal('0.1500'),  # 15% for books
            'storage_fee': Decimal('0.15'),
            'removal_fee': Decimal('0.30'),
            'disposal_fee': Decimal('0.10'),
            'return_processing_fee': Decimal('0.15'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('2.50'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Books'
        })
    
    # Sports & Outdoors category
    sports_products = [
        {"sku": "SPORTS-GEAR-001", "asin": "B09U4T3S2R", "weight": 2.5, "dims": {"length": 16, "width": 12, "height": 8}},
        {"sku": "FITNESS-EQUIPMENT-001", "asin": "B08T3S2R1Q", "weight": 5.0, "dims": {"length": 20, "width": 15, "height": 10}},
        {"sku": "OUTDOOR-TOOLS-001", "asin": "B07S2R1Q0P", "weight": 1.8, "dims": {"length": 12, "width": 8, "height": 4}},
        {"sku": "SPORTS-APPAREL-001", "asin": "B08R1Q0P9O", "weight": 0.6, "dims": {"length": 10, "width": 8, "height": 2}},
        {"sku": "CAMPING-GEAR-001", "asin": "B09Q0P9O8N", "weight": 3.2, "dims": {"length": 18, "width": 14, "height": 6}},
    ]
    
    for product in sports_products:
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'ATVPDKIKX0DER',
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'SPORTING_GOODS',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('5.25'),
            'referral_fee_rate': Decimal('0.1500'),  # 15% for sports
            'storage_fee': Decimal('0.55'),
            'removal_fee': Decimal('1.00'),
            'disposal_fee': Decimal('0.50'),
            'return_processing_fee': Decimal('0.75'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('6.75'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Sports & Outdoors'
        })
    
    # Add some Canadian marketplace data
    for i, product in enumerate(electronics_products[:3]):
        fees_data.append({
            'seller_sku': product["sku"],
            'asin': product["asin"],
            'marketplace_id': 'A2EUQ1WTGCTBG2',  # Canada
            'seller_id': 'A2Z8K9SELLER1',
            'product_type': 'ELECTRONICS',
            'item_condition': 'New',
            'fulfillment_fee': Decimal('4.50'),  # Higher fees in Canada
            'referral_fee_rate': Decimal('0.0800'),
            'storage_fee': Decimal('0.45'),
            'removal_fee': Decimal('0.65'),
            'disposal_fee': Decimal('0.35'),
            'return_processing_fee': Decimal('0.35'),
            'high_volume_listing_fee': Decimal('0.00'),
            'multichannel_fulfillment_fee': Decimal('5.50'),
            'weight': Decimal(str(product["weight"])),
            'dimensions': json.dumps(product["dims"]),
            'category': 'Electronics'
        })
    
    # Bulk insert the data
    op.bulk_insert(product_fees_table, fees_data)
    
    print(f"Inserted {len(fees_data)} product fees records")


def downgrade():
    # Delete all product fees data
    op.execute("DELETE FROM product_fees")
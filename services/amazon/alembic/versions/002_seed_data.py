"""Seed comprehensive Amazon SP-API data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta
import json

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert comprehensive seed data for Amazon SP-API mock."""
    
    # Get connection
    connection = op.get_bind()
    
    # Insert sellers
    sellers_data = [
        ('SELLER001', 'TechGadgets Pro', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER002', 'Home & Garden Essentials', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER003', 'Fashion Forward', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER004', 'Sports & Outdoors Co', 'A2EUQ1WTGCTBG2', 'CA', 'CAD'),
        ('SELLER005', 'Books & Media Store', 'A1PA6795UKMFR9', 'DE', 'EUR'),
        ('SELLER006', 'Baby & Kids World', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER007', 'Health & Beauty Plus', 'A13V1IB3VIYZZH', 'FR', 'EUR'),
        ('SELLER008', 'Automotive Solutions', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER009', 'Pet Supplies Central', 'ATVPDKIKX0DER', 'US', 'USD'),
        ('SELLER010', 'Kitchen & Dining Pro', 'A1F83G8C2ARO7P', 'UK', 'GBP')
    ]
    
    for seller_id, name, marketplace_id, country, currency in sellers_data:
        connection.execute(sa.text("""
            INSERT INTO sellers (seller_id, name, marketplace_id, country_code, currency_code, created_at, updated_at)
            VALUES (:seller_id, :name, :marketplace_id, :country, :currency, NOW(), NOW())
        """), {
            'seller_id': seller_id,
            'name': name,
            'marketplace_id': marketplace_id,
            'country': country,
            'currency': currency
        })
    
    # Insert catalog items (ASINs)
    catalog_items = [
        ('B08N5WRWNW', None, 'Wireless Bluetooth Headphones Premium', 'TechGadgets', 'Electronics', 'Black', 'Over-Ear', 'Premium'),
        ('B08M3K7J9L', None, 'Professional Garden Tool Set 12-Piece', 'GreenThumb', 'Tools', 'Green', 'Standard', 'Professional'),
        ('B08L8QXYZ1', None, 'Designer Leather Handbag', 'FashionForward', 'Handbags', 'Brown', 'Medium', 'Classic'),
        ('B08K9MNBVC', None, 'Running Shoes Athletic Performance', 'SportsCo', 'Shoes', 'Blue', '10', 'Athletic'),
        ('B08J7LKJHG', None, 'Programming Complete Guide Book Set', 'TechBooks', 'Books', 'Blue', 'Standard', 'Educational'),
        ('B08H5FDSA2', None, 'Baby Stroller Lightweight Compact', 'BabyWorld', 'Baby', 'Pink', 'Compact', 'Travel'),
        ('B08G4REWQ3', None, 'Skincare Set Anti-Aging Premium', 'BeautyPlus', 'Beauty', 'White', 'Set', 'Premium'),
        ('B08F3TYUI4', None, 'Car Phone Mount Magnetic Universal', 'AutoSolutions', 'Automotive', 'Black', 'Universal', 'Magnetic'),
        ('B08E2QWER5', None, 'Dog Food Premium Natural Organic', 'PetCentral', 'Pet Supplies', 'Natural', '5kg', 'Premium'),
        ('B08D1ASDF6', None, 'Kitchen Knife Set Professional Steel', 'KitchenPro', 'Kitchen', 'Silver', '6-Piece', 'Professional')
    ]
    
    for asin, parent_asin, item_name, brand, classification, color, size, style in catalog_items:
        dimensions = {
            "length": {"value": 10.5, "unit": "inches"},
            "width": {"value": 8.2, "unit": "inches"},
            "height": {"value": 3.1, "unit": "inches"}
        }
        identifiers = {
            "ean": ["1234567890123"],
            "upc": ["123456789012"]
        }
        images = [{
            "variant": "MAIN",
            "link": f"https://images-na.ssl-images-amazon.com/images/I/{asin}.jpg"
        }]
        
        connection.execute(sa.text("""
            INSERT INTO catalog_items (asin, parent_asin, item_name, brand, classification, color, size, style,
                                     dimensions, identifiers, images, marketplace_id, created_at, updated_at)
            VALUES (:asin, :parent_asin, :item_name, :brand, :classification, :color, :size, :style,
                    :dimensions, :identifiers, :images, 'ATVPDKIKX0DER', NOW(), NOW())
        """), {
            'asin': asin,
            'parent_asin': parent_asin,
            'item_name': item_name,
            'brand': brand,
            'classification': classification,
            'color': color,
            'size': size,
            'style': style,
            'dimensions': json.dumps(dimensions),
            'identifiers': json.dumps(identifiers),
            'images': json.dumps(images)
        })
    
    # Insert orders
    base_date = datetime.now() - timedelta(days=30)
    order_statuses = ['Pending', 'Unshipped', 'PartiallyShipped', 'Shipped', 'Delivered', 'Canceled']
    
    for i in range(50):  # 50 orders
        order_date = base_date + timedelta(days=i % 30, hours=i % 24, minutes=i % 60)
        order_id = f"111-1111111-111{i:04d}"
        seller_order_id = f"SO-2024-{i+1:04d}"
        status = order_statuses[i % len(order_statuses)]
        marketplace_id = ['ATVPDKIKX0DER', 'A2EUQ1WTGCTBG2', 'A1PA6795UKMFR9'][i % 3]
        
        buyer_info = [
            ('john.smith@example.com', 'John Smith', '123 Main St', 'Seattle', 'WA', '98101', 'US', '+1-206-555-0123'),
            ('jane.doe@example.com', 'Jane Doe', '456 Oak Ave', 'Portland', 'OR', '97201', 'US', '+1-503-555-0124'),
            ('bob.johnson@example.com', 'Bob Johnson', '789 Pine St', 'San Francisco', 'CA', '94102', 'US', '+1-415-555-0125'),
            ('alice.brown@example.com', 'Alice Brown', '321 Elm St', 'Los Angeles', 'CA', '90210', 'US', '+1-213-555-0126'),
            ('charlie.wilson@example.com', 'Charlie Wilson', '654 Cedar Ave', 'Denver', 'CO', '80202', 'US', '+1-303-555-0127')
        ]
        
        buyer = buyer_info[i % len(buyer_info)]
        order_total = round(29.99 + (i * 15.5) % 200, 2)
        
        connection.execute(sa.text("""
            INSERT INTO orders (
                amazon_order_id, seller_order_id, purchase_date, last_update_date, order_status,
                fulfillment_channel, sales_channel, order_channel, ship_service_level, marketplace_id,
                order_total, currency_code, number_of_items_shipped, number_of_items_unshipped,
                payment_method, buyer_email, buyer_name, shipping_address_name, shipping_address_line1,
                shipping_address_city, shipping_address_state, shipping_address_postal_code,
                shipping_address_country, shipping_address_phone, order_type, earliest_ship_date,
                latest_ship_date, earliest_delivery_date, latest_delivery_date, is_business_order,
                is_prime, is_premium_order, created_at, updated_at
            ) VALUES (
                :order_id, :seller_order_id, :purchase_date, :last_update_date, :order_status,
                'MFN', 'Amazon.com', 'Amazon.com', 'Standard', :marketplace_id,
                :order_total, 'USD', :items_shipped, :items_unshipped,
                'Other', :buyer_email, :buyer_name, :shipping_name, :shipping_line1,
                :shipping_city, :shipping_state, :shipping_postal, :shipping_country,
                :shipping_phone, 'StandardOrder', :earliest_ship, :latest_ship,
                :earliest_delivery, :latest_delivery, :is_business, :is_prime, :is_premium,
                NOW(), NOW()
            )
        """), {
            'order_id': order_id,
            'seller_order_id': seller_order_id,
            'purchase_date': order_date,
            'last_update_date': order_date + timedelta(hours=2),
            'order_status': status,
            'marketplace_id': marketplace_id,
            'order_total': order_total,
            'items_shipped': 1 if status in ['Shipped', 'Delivered'] else 0,
            'items_unshipped': 0 if status in ['Shipped', 'Delivered'] else 1,
            'buyer_email': buyer[0],
            'buyer_name': buyer[1],
            'shipping_name': buyer[1],
            'shipping_line1': buyer[2],
            'shipping_city': buyer[3],
            'shipping_state': buyer[4],
            'shipping_postal': buyer[5],
            'shipping_country': buyer[6],
            'shipping_phone': buyer[7],
            'earliest_ship': order_date + timedelta(days=1),
            'latest_ship': order_date + timedelta(days=3),
            'earliest_delivery': order_date + timedelta(days=3),
            'latest_delivery': order_date + timedelta(days=7),
            'is_business': i % 10 == 0,
            'is_prime': i % 3 == 0,
            'is_premium': i % 15 == 0
        })
        
        # Insert order items (1-3 items per order)
        items_count = (i % 3) + 1
        for j in range(items_count):
            item_id = f"{order_id.replace('-', '')}{j:02d}"
            sku_index = (i + j) % len(catalog_items)
            asin = catalog_items[sku_index][0]
            sku = f"SKU-{asin[-6:]}-{j:03d}"
            title = catalog_items[sku_index][2]
            quantity = (j % 2) + 1
            item_price = round(order_total / items_count, 2)
            
            connection.execute(sa.text("""
                INSERT INTO order_items (
                    order_item_id, amazon_order_id, seller_sku, asin, title, quantity_ordered,
                    quantity_shipped, item_price, shipping_price, item_tax, shipping_tax,
                    condition_id, condition_subtype_id, serial_number_required, is_transparency,
                    product_info, created_at, updated_at
                ) VALUES (
                    :item_id, :order_id, :sku, :asin, :title, :quantity,
                    :quantity_shipped, :item_price, :shipping_price, :item_tax, :shipping_tax,
                    'New', 'New', FALSE, FALSE, :product_info, NOW(), NOW()
                )
            """), {
                'item_id': item_id,
                'order_id': order_id,
                'sku': sku,
                'asin': asin,
                'title': title,
                'quantity': quantity,
                'quantity_shipped': quantity if status in ['Shipped', 'Delivered'] else 0,
                'item_price': item_price,
                'shipping_price': 0.00,
                'item_tax': round(item_price * 0.08, 2),
                'shipping_tax': 0.00,
                'product_info': json.dumps({"NumberOfItems": quantity})
            })
    
    # Insert inventory data
    for i, (asin, _, title, brand, _, _, _, _) in enumerate(catalog_items):
        sku = f"SKU-{asin[-6:]}-001"
        fnsku = f"X{i+1:03d}{asin[-4:]}"
        
        connection.execute(sa.text("""
            INSERT INTO inventory (
                seller_sku, fnsku, asin, condition_type, total_quantity, inbound_working_quantity,
                inbound_shipped_quantity, inbound_receiving_quantity, fulfillable_quantity,
                unfulfillable_quantity, reserved_quantity_total, reserved_quantity_pending_customer_order,
                reserved_quantity_pending_transshipment, reserved_quantity_fc_processing,
                researching_quantity_total, last_updated_time, product_name, created_at, updated_at
            ) VALUES (
                :sku, :fnsku, :asin, 'NewItem', :total_qty, :inbound_working, :inbound_shipped,
                :inbound_receiving, :fulfillable, :unfulfillable, :reserved_total, :reserved_pending,
                :reserved_transship, :reserved_fc, :researching, NOW(), :product_name, NOW(), NOW()
            )
        """), {
            'sku': sku,
            'fnsku': fnsku,
            'asin': asin,
            'total_qty': 100 + (i * 50),
            'inbound_working': 10 + (i * 2),
            'inbound_shipped': 5 + i,
            'inbound_receiving': 3 + i,
            'fulfillable': 80 + (i * 40),
            'unfulfillable': 2 + i,
            'reserved_total': 5 + i,
            'reserved_pending': 3 + i,
            'reserved_transship': 1,
            'reserved_fc': 1,
            'researching': 0,
            'product_name': title
        })
    
    # Insert listings
    for i, (asin, _, title, brand, classification, color, size, style) in enumerate(catalog_items):
        seller_id = f"SELLER{(i % 10) + 1:03d}"
        sku = f"SKU-{asin[-6:]}-001"
        
        attributes = {
            "condition_type": "new",
            "item_name": title,
            "brand_name": brand,
            "product_description": f"High-quality {title.lower()} from {brand}",
            "bullet_points": [
                f"Premium {classification.lower()}",
                f"Color: {color}",
                f"Size: {size}",
                "Fast shipping available"
            ],
            "manufacturer": brand,
            "item_type_keyword": classification.lower(),
            "color": color,
            "size": size,
            "material_type": ["Premium Material"],
            "item_dimensions": {
                "length": {"value": 10.5, "unit": "inches"},
                "width": {"value": 8.2, "unit": "inches"},
                "height": {"value": 3.1, "unit": "inches"}
            }
        }
        
        connection.execute(sa.text("""
            INSERT INTO listings (
                seller_id, seller_sku, asin, product_type, item_name, brand_name, description,
                bullet_points, manufacturer, part_number, attributes, status, submission_id,
                issues, created_date, last_updated_date, created_at, updated_at
            ) VALUES (
                :seller_id, :sku, :asin, :product_type, :item_name, :brand_name, :description,
                :bullet_points, :manufacturer, :part_number, :attributes, 'ACTIVE', :submission_id,
                '[]', NOW(), NOW(), NOW(), NOW()
            )
        """), {
            'seller_id': seller_id,
            'sku': sku,
            'asin': asin,
            'product_type': classification.upper(),
            'item_name': title,
            'brand_name': brand,
            'description': f"High-quality {title.lower()} from {brand}",
            'bullet_points': json.dumps(attributes["bullet_points"]),
            'manufacturer': brand,
            'part_number': f"PN-{asin}",
            'attributes': json.dumps(attributes),
            'submission_id': f"sub_{sku}_{int(datetime.now().timestamp())}"
        })
    
    # Insert product pricing
    for i, (asin, _, title, brand, _, _, _, _) in enumerate(catalog_items):
        sku = f"SKU-{asin[-6:]}-001"
        base_price = 29.99 + (i * 15.5)
        
        connection.execute(sa.text("""
            INSERT INTO product_pricing (
                seller_sku, asin, marketplace_id, item_condition, landed_price, listing_price,
                shipping_price, points_value, competitive_price_id, number_of_offer_listings,
                trade_in_value, created_at, updated_at
            ) VALUES (
                :sku, :asin, 'ATVPDKIKX0DER', 'New', :landed_price, :listing_price,
                :shipping_price, :points, :competitive_id, :offer_listings, :trade_in,
                NOW(), NOW()
            )
        """), {
            'sku': sku,
            'asin': asin,
            'landed_price': round(base_price, 2),
            'listing_price': round(base_price * 1.1, 2),
            'shipping_price': 0.00,
            'points': None,
            'competitive_id': f"CP{i+1:04d}",
            'offer_listings': 5 + (i % 15),
            'trade_in': round(base_price * 0.3, 2) if i % 3 == 0 else None
        })
    
    # Insert reports
    report_types = [
        'GET_MERCHANT_LISTINGS_ALL_DATA',
        'GET_FLAT_FILE_OPEN_LISTINGS_DATA',
        'GET_ORDER_REPORT_DATA_INVOICING',
        'GET_FLAT_FILE_ORDERS_RECONCILIATION_DATA',
        'GET_FBA_INVENTORY_RECONCILIATION_DATA',
        'GET_SALES_AND_TRAFFIC_REPORT',
        'GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT',
        'GET_AFN_INVENTORY_DATA'
    ]
    
    for i, report_type in enumerate(report_types):
        report_id = f"RPT-{i+1:03d}-2024"
        status = ['DONE', 'IN_PROGRESS', 'CANCELLED', 'FATAL'][i % 4]
        created_time = datetime.now() - timedelta(days=i*2)
        
        connection.execute(sa.text("""
            INSERT INTO reports (
                report_id, report_type, data_start_time, data_end_time, marketplace_ids,
                processing_status, created_time, processing_start_time, processing_end_time,
                report_document_id, report_document_url, report_options, created_at, updated_at
            ) VALUES (
                :report_id, :report_type, :data_start, :data_end, :marketplace_ids,
                :status, :created_time, :proc_start, :proc_end, :doc_id, :doc_url,
                :options, NOW(), NOW()
            )
        """), {
            'report_id': report_id,
            'report_type': report_type,
            'data_start': created_time - timedelta(days=30),
            'data_end': created_time,
            'marketplace_ids': 'ATVPDKIKX0DER',
            'status': status,
            'created_time': created_time,
            'proc_start': created_time + timedelta(minutes=5) if status != 'IN_QUEUE' else None,
            'proc_end': created_time + timedelta(minutes=15) if status == 'DONE' else None,
            'doc_id': f"DOC-{report_id}" if status == 'DONE' else None,
            'doc_url': f"https://mock-amazon-reports.s3.amazonaws.com/{report_id}.csv" if status == 'DONE' else None,
            'options': json.dumps({})
        })
    
    # Insert feeds
    feed_types = [
        'POST_PRODUCT_DATA',
        'POST_INVENTORY_AVAILABILITY_DATA',
        'POST_PRODUCT_PRICING_DATA',
        'POST_PRODUCT_IMAGE_DATA',
        'POST_PRODUCT_RELATIONSHIP_DATA',
        'POST_FLAT_FILE_INVLOADER_DATA'
    ]
    
    for i, feed_type in enumerate(feed_types):
        feed_id = f"FEED-{i+1:03d}-2024"
        status = ['DONE', 'IN_PROGRESS', 'CANCELLED'][i % 3]
        created_time = datetime.now() - timedelta(days=i)
        
        connection.execute(sa.text("""
            INSERT INTO feeds (
                feed_id, feed_type, marketplace_ids, created_time, processing_status,
                processing_start_time, processing_end_time, result_feed_document_id,
                feed_options, created_at, updated_at
            ) VALUES (
                :feed_id, :feed_type, :marketplace_ids, :created_time, :status,
                :proc_start, :proc_end, :result_doc_id, :options, NOW(), NOW()
            )
        """), {
            'feed_id': feed_id,
            'feed_type': feed_type,
            'marketplace_ids': 'ATVPDKIKX0DER',
            'created_time': created_time,
            'status': status,
            'proc_start': created_time + timedelta(minutes=2) if status != 'IN_QUEUE' else None,
            'proc_end': created_time + timedelta(minutes=10) if status == 'DONE' else None,
            'result_doc_id': f"RESULT-{feed_id}" if status == 'DONE' else None,
            'options': json.dumps({})
        })


def downgrade() -> None:
    """Remove seed data."""
    connection = op.get_bind()
    
    # Delete in reverse order due to foreign key constraints
    tables = [
        'notifications', 'finances', 'product_pricing', 'shipments', 'feeds',
        'reports', 'listings', 'inventory', 'order_items', 'orders',
        'catalog_items', 'sellers'
    ]
    
    for table in tables:
        connection.execute(sa.text(f"DELETE FROM {table}"))
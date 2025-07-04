"""
Database Reset Service for Amazon SP-API Mock Service
Handles resetting the database to initial seeded state
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import importlib
import sys
import os
from pathlib import Path
from sqlalchemy import text

logger = logging.getLogger(__name__)


class DatabaseResetService:
    """Service to reset database to initial seeded state."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # List of all tables in the correct order for deletion (respecting foreign key constraints)
        self.tables_to_clear = [
            # Child tables first (those with foreign keys)
            'order_items',
            'notifications',
            'finances', 
            'product_pricing',
            'product_fees',
            'shipments',
            'feeds',
            'reports',
            'listings',
            'inventory',
            'messages',
            'buyer_attributes',
            'messaging_actions',
            'invoice_documents',
            'invoice_exports',
            'invoices',
            'invoice_attributes',
            'sales_metrics',
            'catalog_categories',
            # Parent tables last
            'orders',
            'catalog_items',
            'sellers'
        ]
        
        # List of seed migration files in execution order
        self.seed_migrations = [
            '002_seed_data',
            '004_seed_invoices_data', 
            '006_seed_sales_data',
            '008_seed_product_fees_data',
            '010_seed_messaging_data',
            '012_seed_catalog_data'
        ]
    
    async def reset_to_initial_state(self) -> Dict[str, Any]:
        """Reset database to initial seeded state."""
        logger.info("Starting database reset to initial state...")
        
        start_time = datetime.now()
        results = {
            "start_time": start_time.isoformat(),
            "tables_cleared": [],
            "seed_migrations_executed": [],
            "total_records_inserted": 0,
            "errors": []
        }
        
        try:
            # Step 1: Clear all tables
            logger.info("Clearing all existing data...")
            cleared_tables = await self._clear_all_tables()
            results["tables_cleared"] = cleared_tables
            
            # Step 2: Re-execute seed migrations
            logger.info("Re-executing seed migrations...")
            migration_results = await self._execute_seed_migrations()
            results["seed_migrations_executed"] = migration_results
            
            # Step 3: Count total records
            total_records = await self._count_total_records()
            results["total_records_inserted"] = total_records
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = duration
            results["status"] = "success"
            
            logger.info(f"Database reset completed successfully in {duration:.2f} seconds")
            logger.info(f"Total records inserted: {total_records}")
            
            return results
            
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            results["errors"].append(str(e))
            results["status"] = "failed"
            raise e
    
    async def _clear_all_tables(self) -> List[str]:
        """Clear all tables in the correct order."""
        cleared_tables = []
        
        with self.db_manager.get_session() as session:
            try:
                # Disable foreign key checks temporarily (PostgreSQL)
                session.execute(text("SET session_replication_role = replica;"))
                
                for table_name in self.tables_to_clear:
                    try:
                        # Use TRUNCATE CASCADE for faster deletion
                        session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE;"))
                        cleared_tables.append(table_name)
                        logger.debug(f"Cleared table: {table_name}")
                    except Exception as e:
                        # If TRUNCATE fails, try DELETE
                        logger.warning(f"TRUNCATE failed for {table_name}, trying DELETE: {e}")
                        try:
                            session.execute(text(f"DELETE FROM {table_name};"))
                            cleared_tables.append(table_name)
                            logger.debug(f"Deleted from table: {table_name}")
                        except Exception as delete_error:
                            logger.error(f"Failed to clear table {table_name}: {delete_error}")
                
                # Re-enable foreign key checks
                session.execute(text("SET session_replication_role = DEFAULT;"))
                
                session.commit()
                logger.info(f"Successfully cleared {len(cleared_tables)} tables")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to clear tables: {e}")
                raise e
        
        return cleared_tables
    
    async def _execute_seed_migrations(self) -> List[Dict[str, Any]]:
        """Execute seed data insertion directly (not through migration files)."""
        migration_results = []
        
        try:
            # Execute seed data insertion methods directly
            with self.db_manager.get_session() as session:
                try:
                    # 1. Seed core data (equivalent to 002_seed_data.py)
                    logger.info("Inserting core seed data...")
                    await self._seed_core_data(session)
                    session.commit()  # Commit after each major section
                    logger.info("Core seed data committed")
                    migration_results.append({
                        "migration": "002_seed_data",
                        "status": "success",
                        "message": "Successfully inserted core seed data"
                    })
                    
                    # 2. Seed invoice data (equivalent to 004_seed_invoices_data.py)
                    logger.info("Inserting invoice seed data...")
                    await self._seed_invoice_data(session)
                    session.commit()  # Commit after each major section
                    logger.info("Invoice seed data committed")
                    migration_results.append({
                        "migration": "004_seed_invoices_data",
                        "status": "success",
                        "message": "Successfully inserted invoice seed data"
                    })
                    
                    # 3. Seed sales data (equivalent to 006_seed_sales_data.py)
                    logger.info("Inserting sales seed data...")
                    await self._seed_sales_data(session)
                    session.commit()  # Commit after each major section
                    logger.info("Sales seed data committed")
                    migration_results.append({
                        "migration": "006_seed_sales_data",
                        "status": "success",
                        "message": "Successfully inserted sales seed data"
                    })
                    
                    # 4. Seed messaging data (equivalent to 010_seed_messaging_data.py)
                    logger.info("Inserting messaging seed data...")
                    await self._seed_messaging_data(session)
                    session.commit()  # Commit after each major section
                    logger.info("Messaging seed data committed")
                    migration_results.append({
                        "migration": "010_seed_messaging_data",
                        "status": "success",
                        "message": "Successfully inserted messaging seed data"
                    })
                    
                    logger.info("All seed data inserted and committed successfully")
                    
                except Exception as e:
                    logger.error(f"Error during seed data insertion: {e}")
                    session.rollback()
                    # Add the failed migration to results
                    migration_results.append({
                        "migration": "seed_data_insertion",
                        "status": "failed",
                        "message": f"Failed during seed data insertion: {str(e)}"
                    })
                    raise e
                
        except Exception as e:
            logger.error(f"Failed to execute seed data insertion: {e}")
            raise e
        
        return migration_results
    
    async def _count_total_records(self) -> int:
        """Count total records across all tables."""
        total_records = 0
        
        with self.db_manager.get_session() as session:
            for table_name in self.tables_to_clear:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
                    count = result.scalar()
                    total_records += count
                    logger.debug(f"Table {table_name}: {count} records")
                except Exception as e:
                    logger.warning(f"Failed to count records in {table_name}: {e}")
        
        return total_records
    
    def get_reset_status(self) -> Dict[str, Any]:
        """Get current database status for reset verification."""
        status = {
            "database_health": self.db_manager.health_check(),
            "table_counts": {},
            "total_records": 0
        }
        
        try:
            with self.db_manager.get_session() as session:
                for table_name in self.tables_to_clear:
                    try:
                        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
                        count = result.scalar()
                        status["table_counts"][table_name] = count
                        status["total_records"] += count
                    except Exception as e:
                        status["table_counts"][table_name] = f"error: {str(e)}"
                        
        except Exception as e:
            status["error"] = f"Failed to get table counts: {str(e)}"
        
        return status
    
    async def _seed_core_data(self, session):
        """Insert core seed data (sellers, catalog items, orders, etc.)."""
        import json
        from datetime import timedelta
        
        logger.info("Starting core data insertion...")
        
        # Insert sellers
        logger.info("Inserting sellers...")
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
            session.execute(text("""
                INSERT INTO sellers (seller_id, name, marketplace_id, country_code, currency_code, created_at, updated_at)
                VALUES (:seller_id, :name, :marketplace_id, :country, :currency, NOW(), NOW())
            """), {
                'seller_id': seller_id,
                'name': name,
                'marketplace_id': marketplace_id,
                'country': country,
                'currency': currency
            })
        
        session.flush()  # Ensure sellers are written
        logger.info(f"Inserted {len(sellers_data)} sellers")
        
        # Insert catalog items (ASINs)
        logger.info("Inserting catalog items...")
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
            
            session.execute(text("""
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
        
        session.flush()  # Ensure catalog items are written
        logger.info(f"Inserted {len(catalog_items)} catalog items")
        
        # Insert sample orders
        logger.info("Inserting orders...")
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
            
            session.execute(text("""
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
                
                session.execute(text("""
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
        
        session.flush()  # Ensure orders and order items are written
        logger.info("Inserted orders and order items")
        
        # Insert inventory data
        logger.info("Inserting inventory data...")
        for i, (asin, _, title, brand, _, _, _, _) in enumerate(catalog_items):
            sku = f"SKU-{asin[-6:]}-001"
            fnsku = f"X{i+1:03d}{asin[-4:]}"
            
            session.execute(text("""
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
        
        session.flush()  # Ensure inventory data is written
        logger.info("Inserted inventory data")
        
        # Insert listings data
        logger.info("Inserting listings data...")
        for i, (asin, _, title, brand, _, _, _, _) in enumerate(catalog_items):
            sku = f"SKU-{asin[-6:]}-001"
            seller_id = sellers_data[i % len(sellers_data)][0]
            
            attributes = {
                "item_name": [{"language_tag": "en_US", "value": title, "marketplace_id": "ATVPDKIKX0DER"}],
                "brand": [{"language_tag": "en_US", "value": brand, "marketplace_id": "ATVPDKIKX0DER"}],
                "product_type": ["LUGGAGE"],
                "condition_type": ["new_new"],
                "list_price": [{"currency": "USD", "value": 99.99 + (i * 50), "marketplace_id": "ATVPDKIKX0DER"}],
                "bullet_point": [
                    {"language_tag": "en_US", "value": f"High quality {title.lower()}", "marketplace_id": "ATVPDKIKX0DER"},
                    {"language_tag": "en_US", "value": f"Premium {brand} product with excellent features", "marketplace_id": "ATVPDKIKX0DER"}
                ]
            }
            
            session.execute(text("""
                INSERT INTO listings (
                    seller_id, seller_sku, asin, product_type, item_name, brand_name,
                    attributes, status, created_date, last_updated_date, created_at, updated_at
                ) VALUES (
                    :seller_id, :sku, :asin, :product_type, :item_name, :brand_name,
                    :attributes, :status, :created_date, :last_updated_date, NOW(), NOW()
                )
            """), {
                'seller_id': seller_id,
                'sku': sku,
                'asin': asin,
                'product_type': 'LUGGAGE',
                'item_name': title,
                'brand_name': brand,
                'attributes': json.dumps(attributes),
                'status': 'ACTIVE',
                'created_date': datetime.now() - timedelta(days=30),
                'last_updated_date': datetime.now() - timedelta(days=5)
            })
        
        session.flush()  # Ensure listings data is written
        logger.info("Inserted listings data")
        
        logger.info("Core seed data inserted successfully")
    
    async def _seed_invoice_data(self, session):
        """Insert invoice seed data."""
        import json
        import uuid
        from datetime import timedelta
        
        # Insert invoice attributes
        invoice_attributes_data = [
            ('status', 'PENDING', 'Pending'),
            ('status', 'APPROVED', 'Approved'),
            ('status', 'REJECTED', 'Rejected'),
            ('status', 'CANCELLED', 'Cancelled'),
            ('status', 'PROCESSING', 'Processing'),
            ('invoice_type', 'TAX_INVOICE', 'Tax Invoice'),
            ('invoice_type', 'CREDIT_NOTE', 'Credit Note'),
            ('invoice_type', 'DEBIT_NOTE', 'Debit Note'),
            ('invoice_type', 'COMMERCIAL_INVOICE', 'Commercial Invoice'),
            ('transaction_identifier_name', 'ORDER_ID', 'Order ID'),
            ('transaction_identifier_name', 'SHIPMENT_ID', 'Shipment ID'),
            ('transaction_identifier_name', 'REFUND_ID', 'Refund ID'),
            ('transaction_identifier_name', 'ADJUSTMENT_ID', 'Adjustment ID'),
            ('transaction_type', 'SALE', 'Sale'),
            ('transaction_type', 'RETURN', 'Return'),
            ('transaction_type', 'REFUND', 'Refund'),
            ('transaction_type', 'ADJUSTMENT', 'Adjustment'),
        ]
        
        for attr_type, value, description in invoice_attributes_data:
            session.execute(text("""
                INSERT INTO invoice_attributes (attribute_type, value, description, created_at, updated_at)
                VALUES (:attr_type, :value, :description, :created_at, :updated_at)
            """), {
                'attr_type': attr_type,
                'value': value,
                'description': description,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        session.flush()  # Ensure invoice attributes are written
        logger.info("Inserted invoice attributes")
        
        # Generate sample invoices
        logger.info("Inserting invoices...")
        base_date = datetime.now() - timedelta(days=90)
        for i in range(50):
            invoice_id = f"INV-{i+1:05d}"
            invoice_date = base_date + timedelta(days=i * 2)
            
            invoice_types = ['TAX_INVOICE', 'CREDIT_NOTE', 'DEBIT_NOTE', 'COMMERCIAL_INVOICE']
            statuses = ['PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'PROCESSING']
            transaction_types = ['SALE', 'RETURN', 'REFUND', 'ADJUSTMENT']
            
            invoice_type = invoice_types[i % len(invoice_types)]
            status = statuses[i % len(statuses)]
            transaction_type = transaction_types[i % len(transaction_types)]
            
            transaction_ids = [
                {'name': 'ORDER_ID', 'id': f'ORDER-{i+1:05d}'},
                {'name': 'SHIPMENT_ID', 'id': f'SHIP-{i+1:05d}'}
            ]
            
            session.execute(text("""
                INSERT INTO invoices (id, date, error_code, external_invoice_id, gov_response,
                                    invoice_type, series, status, transaction_ids, transaction_type,
                                    created_at, updated_at)
                VALUES (:id, :date, :error_code, :external_invoice_id, :gov_response,
                        :invoice_type, :series, :status, :transaction_ids, :transaction_type,
                        :created_at, :updated_at)
            """), {
                'id': invoice_id,
                'date': invoice_date,
                'error_code': None if status != 'REJECTED' else f'ERR-{i+1:03d}',
                'external_invoice_id': f'EXT-{invoice_id}',
                'gov_response': f'GOV-RESPONSE-{i+1:05d}' if status == 'APPROVED' else None,
                'invoice_type': invoice_type,
                'series': f'SERIES-{(i % 10) + 1}',
                'status': status,
                'transaction_ids': json.dumps(transaction_ids),
                'transaction_type': transaction_type,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        session.flush()  # Ensure invoices are written
        logger.info("Inserted invoices")
        
        logger.info("Invoice seed data inserted successfully")
    
    async def _seed_sales_data(self, session):
        """Insert sales metrics seed data."""
        import json
        from datetime import timedelta
        
        base_date = datetime(2024, 1, 1)
        
        # Generate daily metrics for the past 30 days
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            for buyer_type in ['All', 'B2B', 'B2C']:
                unit_count = 150 if buyer_type == 'All' else (50 if buyer_type == 'B2B' else 100)
                order_count = 25 if buyer_type == 'All' else (8 if buyer_type == 'B2B' else 17)
                order_item_count = 30 if buyer_type == 'All' else (10 if buyer_type == 'B2B' else 20)
                
                unit_count += (i * 3) % 50
                order_count += (i * 2) % 10
                order_item_count += (i * 2) % 15
                
                total_sales = unit_count * 25.99
                average_unit_price = total_sales / unit_count if unit_count > 0 else 0
                
                session.execute(text("""
                    INSERT INTO sales_metrics (
                        interval, granularity, unit_count, order_item_count, order_count,
                        average_unit_price, total_sales, currency_code, buyer_type, marketplace_ids,
                        asin, sku, period_start, period_end, created_at, updated_at
                    ) VALUES (
                        :interval, :granularity, :unit_count, :order_item_count, :order_count,
                        :average_unit_price, :total_sales, :currency_code, :buyer_type, :marketplace_ids,
                        :asin, :sku, :period_start, :period_end, :created_at, :updated_at
                    )
                """), {
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
        
        session.flush()  # Ensure sales metrics are written
        logger.info("Inserted sales metrics")
        
        logger.info("Sales seed data inserted successfully")
    
    async def _seed_messaging_data(self, session):
        """Insert messaging seed data."""
        import json
        
        # Get some existing order IDs
        order_ids = [
            "111-1111111-1110000", "111-1111111-1110001", "111-1111111-1110002",
            "111-1111111-1110003", "111-1111111-1110004", "111-1111111-1110005",
            "111-1111111-1110006", "111-1111111-1110007", "111-1111111-1110008",
            "111-1111111-1110009"
        ]
        
        # Messaging actions data
        standard_actions = [
            ("confirmCustomizationDetails", "Confirm product customization details like size, color, or personalization"),
            ("confirmDeliveryDetails", "Confirm delivery instructions or address details"),
            ("confirmOrderDetails", "Confirm order specifications or requirements"),
            ("legalDisclosure", "Send required legal disclosures or compliance information")
        ]
        
        for i, order_id in enumerate(order_ids):
            marketplace_id = "ATVPDKIKX0DER" if i % 3 == 0 else "A2EUQ1WTGCTBG2" if i % 3 == 1 else "A1AM78C64UM0Y8"
            
            for action_name, description in standard_actions:
                session.execute(text("""
                    INSERT INTO messaging_actions (amazon_order_id, marketplace_id, action_name, is_available, description)
                    VALUES (:amazon_order_id, :marketplace_id, :action_name, :is_available, :description)
                """), {
                    'amazon_order_id': order_id,
                    'marketplace_id': marketplace_id,
                    'action_name': action_name,
                    'is_available': True,
                    'description': description
                })
        
        # Buyer attributes data
        locales = [
            {"locale": "en-US", "country": "US", "language": "en"},
            {"locale": "en-CA", "country": "CA", "language": "en"},
            {"locale": "fr-CA", "country": "CA", "language": "fr"},
            {"locale": "es-MX", "country": "MX", "language": "es"},
            {"locale": "en-GB", "country": "GB", "language": "en"},
            {"locale": "de-DE", "country": "DE", "language": "de"},
            {"locale": "fr-FR", "country": "FR", "language": "fr"},
            {"locale": "it-IT", "country": "IT", "language": "it"},
            {"locale": "es-ES", "country": "ES", "language": "es"},
            {"locale": "ja-JP", "country": "JP", "language": "ja"}
        ]
        
        for i, order_id in enumerate(order_ids):
            locale_info = locales[i % len(locales)]
            session.execute(text("""
                INSERT INTO buyer_attributes (amazon_order_id, locale, country_code, language_code)
                VALUES (:amazon_order_id, :locale, :country_code, :language_code)
            """), {
                'amazon_order_id': order_id,
                'locale': locale_info["locale"],
                'country_code': locale_info["country"],
                'language_code': locale_info["language"]
            })
        
        # Sample messages data
        messages_data = [
            {
                'amazon_order_id': order_ids[0],
                'message_type': 'confirmDeliveryDetails',
                'subject': 'Delivery Confirmation Required',
                'body': 'Hello! We need to confirm your delivery details for your recent order.',
                'status': 'sent',
                'sent_at': datetime(2024, 12, 15, 10, 30, 0)
            },
            {
                'amazon_order_id': order_ids[1],
                'message_type': 'confirmCustomizationDetails',
                'subject': 'Product Customization Confirmation',
                'body': 'Thank you for your order! We need to confirm the customization details.',
                'status': 'delivered',
                'sent_at': datetime(2024, 12, 16, 14, 15, 0)
            }
        ]
        
        for message in messages_data:
            session.execute(text("""
                INSERT INTO messages (amazon_order_id, message_type, subject, body, status, sent_at)
                VALUES (:amazon_order_id, :message_type, :subject, :body, :status, :sent_at)
            """), message)
        
        session.flush()  # Ensure messaging data is written
        logger.info("Inserted messaging data")
        
        logger.info("Messaging seed data inserted successfully")
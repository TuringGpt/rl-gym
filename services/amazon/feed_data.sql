-- Amazon Selling Partner API Mock Database Schema and Seed Data
-- This file creates tables and populates them with realistic mock data

-- Enable UUID extension if available (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS listings CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;

-- Create sellers table
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    marketplace_id VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    amazon_order_id VARCHAR(50) PRIMARY KEY,
    seller_order_id VARCHAR(50),
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    last_update_date TIMESTAMP WITH TIME ZONE NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    marketplace_id VARCHAR(20) NOT NULL,
    order_total DECIMAL(10, 2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    buyer_email VARCHAR(255),
    shipping_address_name VARCHAR(255),
    shipping_address_line1 TEXT,
    shipping_address_city VARCHAR(100),
    shipping_address_state VARCHAR(50),
    shipping_address_postal_code VARCHAR(20),
    shipping_address_country VARCHAR(2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE order_items (
    order_item_id VARCHAR(50) PRIMARY KEY,
    amazon_order_id VARCHAR(50) REFERENCES orders(amazon_order_id),
    seller_sku VARCHAR(100) NOT NULL,
    asin VARCHAR(20),
    title VARCHAR(500),
    quantity_ordered INTEGER NOT NULL,
    quantity_shipped INTEGER DEFAULT 0,
    item_price DECIMAL(10, 2),
    shipping_price DECIMAL(10, 2) DEFAULT 0,
    item_tax DECIMAL(10, 2) DEFAULT 0,
    shipping_tax DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory table
CREATE TABLE inventory (
    seller_sku VARCHAR(100) PRIMARY KEY,
    fnsku VARCHAR(20),
    asin VARCHAR(20),
    condition_type VARCHAR(20) DEFAULT 'NewItem',
    total_quantity INTEGER DEFAULT 0,
    inbound_working_quantity INTEGER DEFAULT 0,
    inbound_shipped_quantity INTEGER DEFAULT 0,
    inbound_receiving_quantity INTEGER DEFAULT 0,
    fulfillable_quantity INTEGER DEFAULT 0,
    unfulfillable_quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    last_updated_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create listings table
CREATE TABLE listings (
    seller_id VARCHAR(50) NOT NULL,
    seller_sku VARCHAR(100) NOT NULL,
    product_type VARCHAR(100),
    attributes JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (seller_id, seller_sku)
);

-- Create reports table
CREATE TABLE reports (
    report_id VARCHAR(50) PRIMARY KEY,
    report_type VARCHAR(100) NOT NULL,
    processing_status VARCHAR(20) DEFAULT 'IN_PROGRESS',
    created_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_start_time TIMESTAMP WITH TIME ZONE,
    processing_end_time TIMESTAMP WITH TIME ZONE,
    marketplace_ids TEXT,
    report_document_url TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_orders_purchase_date ON orders(purchase_date);
CREATE INDEX idx_orders_marketplace_id ON orders(marketplace_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_order_items_amazon_order_id ON order_items(amazon_order_id);
CREATE INDEX idx_order_items_seller_sku ON order_items(seller_sku);
CREATE INDEX idx_inventory_last_updated ON inventory(last_updated_time);
CREATE INDEX idx_listings_seller_id ON listings(seller_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_status ON reports(processing_status);

-- Insert mock sellers
INSERT INTO sellers (seller_id, name, marketplace_id) VALUES
('SELLER001', 'TechGadgets Pro', 'ATVPDKIKX0DER'),
('SELLER002', 'Home & Garden Essentials', 'ATVPDKIKX0DER'),
('SELLER003', 'Fashion Forward', 'ATVPDKIKX0DER'),
('SELLER004', 'Sports & Outdoors Co', 'ATVPDKIKX0DER'),
('SELLER005', 'Books & Media Store', 'ATVPDKIKX0DER'),
('SELLER006', 'Baby & Kids World', 'ATVPDKIKX0DER'),
('SELLER007', 'Health & Beauty Plus', 'ATVPDKIKX0DER'),
('SELLER008', 'Automotive Solutions', 'ATVPDKIKX0DER'),
('SELLER009', 'Pet Supplies Central', 'ATVPDKIKX0DER'),
('SELLER010', 'Kitchen & Dining Pro', 'ATVPDKIKX0DER');

-- Insert mock orders
INSERT INTO orders (amazon_order_id, seller_order_id, purchase_date, last_update_date, order_status, marketplace_id, order_total, buyer_email, shipping_address_name, shipping_address_line1, shipping_address_city, shipping_address_state, shipping_address_postal_code, shipping_address_country) VALUES
('111-1111111-1111111', 'SO-2024-001', '2024-01-15T10:30:00Z', '2024-01-15T10:30:00Z', 'Shipped', 'ATVPDKIKX0DER', 29.99, 'buyer1@example.com', 'John Smith', '123 Main St', 'Seattle', 'WA', '98101', 'US'),
('111-1111111-1111112', 'SO-2024-002', '2024-01-15T11:45:00Z', '2024-01-16T09:15:00Z', 'Pending', 'ATVPDKIKX0DER', 89.95, 'buyer2@example.com', 'Jane Doe', '456 Oak Ave', 'Portland', 'OR', '97201', 'US'),
('111-1111111-1111113', 'SO-2024-003', '2024-01-16T14:20:00Z', '2024-01-17T16:45:00Z', 'Shipped', 'ATVPDKIKX0DER', 149.99, 'buyer3@example.com', 'Bob Johnson', '789 Pine St', 'San Francisco', 'CA', '94102', 'US'),
('111-1111111-1111114', 'SO-2024-004', '2024-01-17T09:10:00Z', '2024-01-17T09:10:00Z', 'Unshipped', 'ATVPDKIKX0DER', 39.99, 'buyer4@example.com', 'Alice Brown', '321 Elm St', 'Los Angeles', 'CA', '90210', 'US'),
('111-1111111-1111115', 'SO-2024-005', '2024-01-18T16:30:00Z', '2024-01-19T08:20:00Z', 'Delivered', 'ATVPDKIKX0DER', 199.99, 'buyer5@example.com', 'Charlie Wilson', '654 Cedar Ave', 'Denver', 'CO', '80202', 'US'),
('111-1111111-1111116', 'SO-2024-006', '2024-01-19T13:15:00Z', '2024-01-19T13:15:00Z', 'Pending', 'ATVPDKIKX0DER', 24.99, 'buyer6@example.com', 'Diana Garcia', '987 Maple St', 'Austin', 'TX', '73301', 'US'),
('111-1111111-1111117', 'SO-2024-007', '2024-01-20T11:00:00Z', '2024-01-21T10:30:00Z', 'Shipped', 'ATVPDKIKX0DER', 79.99, 'buyer7@example.com', 'Frank Miller', '147 Birch Rd', 'Miami', 'FL', '33101', 'US'),
('111-1111111-1111118', 'SO-2024-008', '2024-01-21T15:45:00Z', '2024-01-21T15:45:00Z', 'Unshipped', 'ATVPDKIKX0DER', 119.99, 'buyer8@example.com', 'Grace Lee', '258 Spruce St', 'Chicago', 'IL', '60601', 'US'),
('111-1111111-1111119', 'SO-2024-009', '2024-01-22T12:20:00Z', '2024-01-23T14:10:00Z', 'Delivered', 'ATVPDKIKX0DER', 59.99, 'buyer9@example.com', 'Henry Davis', '369 Willow Ave', 'Boston', 'MA', '02101', 'US'),
('111-1111111-1111120', 'SO-2024-010', '2024-01-23T09:30:00Z', '2024-01-23T09:30:00Z', 'Pending', 'ATVPDKIKX0DER', 299.99, 'buyer10@example.com', 'Ivy Martinez', '741 Poplar St', 'Phoenix', 'AZ', '85001', 'US');

-- Insert mock order items
INSERT INTO order_items (order_item_id, amazon_order_id, seller_sku, asin, title, quantity_ordered, quantity_shipped, item_price, shipping_price, item_tax) VALUES
('11111111111111', '111-1111111-1111111', 'SKU-TG-001', 'B08N5WRWNW', 'Wireless Bluetooth Headphones', 1, 1, 29.99, 0.00, 2.40),
('11111111111112', '111-1111111-1111112', 'SKU-HG-002', 'B08M3K7J9L', 'Garden Tool Set', 1, 0, 89.95, 0.00, 7.20),
('11111111111113', '111-1111111-1111113', 'SKU-FF-003', 'B08L8QXYZ1', 'Designer Handbag', 1, 1, 149.99, 0.00, 12.00),
('11111111111114', '111-1111111-1111114', 'SKU-SO-004', 'B08K9MNBVC', 'Running Shoes', 1, 0, 39.99, 0.00, 3.20),
('11111111111115', '111-1111111-1111115', 'SKU-BM-005', 'B08J7LKJHG', 'Programming Book Set', 3, 3, 66.66, 0.00, 16.00),
('11111111111116', '111-1111111-1111116', 'SKU-BK-006', 'B08H5FDSA2', 'Baby Stroller', 1, 0, 24.99, 0.00, 2.00),
('11111111111117', '111-1111111-1111117', 'SKU-HB-007', 'B08G4REWQ3', 'Skincare Set', 1, 1, 79.99, 0.00, 6.40),
('11111111111118', '111-1111111-1111118', 'SKU-AS-008', 'B08F3TYUI4', 'Car Phone Mount', 2, 0, 59.995, 0.00, 9.60),
('11111111111119', '111-1111111-1111119', 'SKU-PS-009', 'B08E2QWER5', 'Dog Food Premium', 1, 1, 59.99, 0.00, 4.80),
('11111111111120', '111-1111111-1111120', 'SKU-KD-010', 'B08D1ASDF6', 'Kitchen Knife Set', 1, 0, 299.99, 0.00, 24.00);

-- Insert mock inventory
INSERT INTO inventory (seller_sku, fnsku, asin, condition_type, total_quantity, fulfillable_quantity, reserved_quantity) VALUES
('SKU-TG-001', 'X001ABCD1234', 'B08N5WRWNW', 'NewItem', 150, 145, 5),
('SKU-HG-002', 'X002EFGH5678', 'B08M3K7J9L', 'NewItem', 75, 70, 5),
('SKU-FF-003', 'X003IJKL9012', 'B08L8QXYZ1', 'NewItem', 25, 20, 5),
('SKU-SO-004', 'X004MNOP3456', 'B08K9MNBVC', 'NewItem', 200, 195, 5),
('SKU-BM-005', 'X005QRST7890', 'B08J7LKJHG', 'NewItem', 50, 45, 5),
('SKU-BK-006', 'X006UVWX1234', 'B08H5FDSA2', 'NewItem', 30, 25, 5),
('SKU-HB-007', 'X007YZAB5678', 'B08G4REWQ3', 'NewItem', 100, 95, 5),
('SKU-AS-008', 'X008CDEF9012', 'B08F3TYUI4', 'NewItem', 300, 290, 10),
('SKU-PS-009', 'X009GHIJ3456', 'B08E2QWER5', 'NewItem', 80, 75, 5),
('SKU-KD-010', 'X010KLMN7890', 'B08D1ASDF6', 'NewItem', 15, 10, 5),
('SKU-TG-011', 'X011OPQR1234', 'B08C9ZXCV7', 'NewItem', 120, 115, 5),
('SKU-HG-012', 'X012STUV5678', 'B08B8YXWV8', 'NewItem', 60, 55, 5),
('SKU-FF-013', 'X013WXYZ9012', 'B08A7WVUT9', 'NewItem', 40, 35, 5),
('SKU-SO-014', 'X014ABCD3456', 'B0896VUTS0', 'NewItem', 180, 175, 5),
('SKU-BM-015', 'X015EFGH7890', 'B0885UTSR1', 'NewItem', 35, 30, 5);

-- Insert mock listings
INSERT INTO listings (seller_id, seller_sku, product_type, attributes, status) VALUES
('SELLER001', 'SKU-TG-001', 'ELECTRONICS', '{"brand": "TechGadgets", "color": "Black", "connectivity": "Bluetooth"}', 'ACTIVE'),
('SELLER002', 'SKU-HG-002', 'HOME_AND_GARDEN', '{"material": "Steel", "piece_count": 12}', 'ACTIVE'),
('SELLER003', 'SKU-FF-003', 'FASHION', '{"brand": "FashionForward", "color": "Brown", "material": "Leather"}', 'ACTIVE'),
('SELLER004', 'SKU-SO-004', 'SPORTS', '{"brand": "SportsCo", "size": "10", "color": "Blue"}', 'ACTIVE'),
('SELLER005', 'SKU-BM-005', 'BOOKS', '{"author": "Programming Expert", "language": "English", "page_count": 500}', 'ACTIVE'),
('SELLER006', 'SKU-BK-006', 'BABY_PRODUCTS', '{"brand": "BabyWorld", "age_range": "0-3 years", "color": "Pink"}', 'INACTIVE'),
('SELLER007', 'SKU-HB-007', '美容HEALTH_AND_BEAUTY', '{"brand": "BeautyPlus", "skin_type": "All", "volume": "50ml"}', 'ACTIVE'),
('SELLER008', 'SKU-AS-008', 'AUTOMOTIVE', '{"brand": "AutoSolutions", "compatibility": "Universal", "material": "Plastic"}', 'ACTIVE'),
('SELLER009', 'SKU-PS-009', 'PET_SUPPLIES', '{"brand": "PetCentral", "pet_type": "Dog", "weight": "5kg"}', 'ACTIVE'),
('SELLER010', 'SKU-KD-010', 'KITCHEN', '{"brand": "KitchenPro", "piece_count": 6, "material": "Stainless Steel"}', 'ACTIVE');

-- Insert mock reports
INSERT INTO reports (report_id, report_type, processing_status, marketplace_ids, report_document_url) VALUES
('RPT-001-2024', 'GET_MERCHANT_LISTINGS_ALL_DATA', 'DONE', 'ATVPDKIKX0DER', 'https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/RPT-001-2024'),
('RPT-002-2024', 'GET_FLAT_FILE_OPEN_LISTINGS_DATA', 'DONE', 'ATVPDKIKX0DER', 'https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/RPT-002-2024'),
('RPT-003-2024', 'GET_ORDER_REPORT_DATA_INVOICING', 'IN_PROGRESS', 'ATVPDKIKX0DER', NULL),
('RPT-004-2024', 'GET_FLAT_FILE_ORDERS_RECONCILIATION_DATA', 'DONE', 'ATVPDKIKX0DER', 'https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/RPT-004-2024'),
('RPT-005-2024', 'GET_FBA_INVENTORY_RECONCILIATION_DATA', 'DONE', 'ATVPDKIKX0DER', 'https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/RPT-005-2024'),
('RPT-006-2024', 'GET_SALES_AND_TRAFFIC_REPORT', 'CANCELLED', 'ATVPDKIKX0DER', NULL),
('RPT-007-2024', 'GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT', 'FATAL', 'ATVPDKIKX0DER', NULL),
('RPT-008-2024', 'GET_VENDOR_DIRECT_FULFILLMENT_SHIPPING_LABELS', 'IN_QUEUE', 'ATVPDKIKX0DER', NULL);

-- Update report processing times for completed reports
UPDATE reports SET 
    processing_start_time = created_time + INTERVAL '5 minutes',
    processing_end_time = created_time + INTERVAL '15 minutes'
WHERE processing_status = 'DONE';

UPDATE reports SET 
    processing_start_time = created_time + INTERVAL '2 minutes'
WHERE processing_status = 'IN_PROGRESS';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at timestamps
CREATE TRIGGER update_sellers_updated_at BEFORE UPDATE ON sellers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_items_updated_at BEFORE UPDATE ON order_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO amazon_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO amazon_user;

-- Add some statistics for verification
SELECT 'Database setup completed successfully!' as message;
SELECT 'Sellers: ' || COUNT(*) as sellers_count FROM sellers;
SELECT 'Orders: ' || COUNT(*) as orders_count FROM orders;
SELECT 'Order Items: ' || COUNT(*) as order_items_count FROM order_items;
SELECT 'Inventory Items: ' || COUNT(*) as inventory_count FROM inventory;
SELECT 'Listings: ' || COUNT(*) as listings_count FROM listings;
SELECT 'Reports: ' || COUNT(*) as reports_count FROM reports;
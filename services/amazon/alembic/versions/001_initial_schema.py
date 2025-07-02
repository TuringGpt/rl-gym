"""Initial Amazon SP-API database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sellers table
    op.create_table('sellers',
        sa.Column('seller_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('marketplace_id', sa.String(20), nullable=False),
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('currency_code', sa.String(3), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('seller_id')
    )

    # Create orders table
    op.create_table('orders',
        sa.Column('amazon_order_id', sa.String(50), nullable=False),
        sa.Column('seller_order_id', sa.String(50), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_update_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('order_status', sa.String(50), nullable=False),
        sa.Column('fulfillment_channel', sa.String(10), nullable=True),
        sa.Column('sales_channel', sa.String(50), nullable=True),
        sa.Column('order_channel', sa.String(50), nullable=True),
        sa.Column('ship_service_level', sa.String(50), nullable=True),
        sa.Column('marketplace_id', sa.String(20), nullable=False),
        sa.Column('order_total', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency_code', sa.String(3), default='USD'),
        sa.Column('number_of_items_shipped', sa.Integer, default=0),
        sa.Column('number_of_items_unshipped', sa.Integer, default=0),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('buyer_email', sa.String(255), nullable=True),
        sa.Column('buyer_name', sa.String(255), nullable=True),
        sa.Column('buyer_county', sa.String(255), nullable=True),
        sa.Column('buyer_tax_info', sa.JSON, nullable=True),
        sa.Column('shipment_service_level_category', sa.String(50), nullable=True),
        sa.Column('shipping_address_name', sa.String(255), nullable=True),
        sa.Column('shipping_address_line1', sa.Text, nullable=True),
        sa.Column('shipping_address_line2', sa.Text, nullable=True),
        sa.Column('shipping_address_city', sa.String(100), nullable=True),
        sa.Column('shipping_address_state', sa.String(50), nullable=True),
        sa.Column('shipping_address_postal_code', sa.String(20), nullable=True),
        sa.Column('shipping_address_country', sa.String(2), nullable=True),
        sa.Column('shipping_address_phone', sa.String(30), nullable=True),
        sa.Column('order_type', sa.String(20), default='StandardOrder'),
        sa.Column('earliest_ship_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('latest_ship_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('earliest_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('latest_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_business_order', sa.Boolean, default=False),
        sa.Column('is_prime', sa.Boolean, default=False),
        sa.Column('is_premium_order', sa.Boolean, default=False),
        sa.Column('is_global_express_enabled', sa.Boolean, default=False),
        sa.Column('is_replacement_order', sa.Boolean, default=False),
        sa.Column('is_sold_by_ab', sa.Boolean, default=False),
        sa.Column('is_iba', sa.Boolean, default=False),
        sa.Column('is_ispu', sa.Boolean, default=False),
        sa.Column('is_access_point_order', sa.Boolean, default=False),
        sa.Column('has_automated_shipping_settings', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('amazon_order_id')
    )

    # Create order_items table
    op.create_table('order_items',
        sa.Column('order_item_id', sa.String(50), nullable=False),
        sa.Column('amazon_order_id', sa.String(50), nullable=False),
        sa.Column('seller_sku', sa.String(100), nullable=False),
        sa.Column('asin', sa.String(20), nullable=True),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('quantity_ordered', sa.Integer, nullable=False),
        sa.Column('quantity_shipped', sa.Integer, default=0),
        sa.Column('item_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('shipping_price', sa.Numeric(10, 2), default=0),
        sa.Column('item_tax', sa.Numeric(10, 2), default=0),
        sa.Column('shipping_tax', sa.Numeric(10, 2), default=0),
        sa.Column('shipping_discount', sa.Numeric(10, 2), default=0),
        sa.Column('shipping_discount_tax', sa.Numeric(10, 2), default=0),
        sa.Column('promotion_discount', sa.Numeric(10, 2), default=0),
        sa.Column('promotion_discount_tax', sa.Numeric(10, 2), default=0),
        sa.Column('cod_fee', sa.Numeric(10, 2), default=0),
        sa.Column('cod_fee_discount', sa.Numeric(10, 2), default=0),
        sa.Column('condition_id', sa.String(20), default='New'),
        sa.Column('condition_subtype_id', sa.String(20), default='New'),
        sa.Column('condition_note', sa.Text, nullable=True),
        sa.Column('scheduled_delivery_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_delivery_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('price_designation', sa.String(50), nullable=True),
        sa.Column('tax_collection', sa.JSON, nullable=True),
        sa.Column('serial_number_required', sa.Boolean, default=False),
        sa.Column('is_transparency', sa.Boolean, default=False),
        sa.Column('product_info', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('order_item_id'),
        sa.ForeignKeyConstraint(['amazon_order_id'], ['orders.amazon_order_id'], )
    )

    # Create inventory table
    op.create_table('inventory',
        sa.Column('seller_sku', sa.String(100), nullable=False),
        sa.Column('fnsku', sa.String(20), nullable=True),
        sa.Column('asin', sa.String(20), nullable=True),
        sa.Column('condition_type', sa.String(20), default='NewItem'),
        sa.Column('total_quantity', sa.Integer, default=0),
        sa.Column('inbound_working_quantity', sa.Integer, default=0),
        sa.Column('inbound_shipped_quantity', sa.Integer, default=0),
        sa.Column('inbound_receiving_quantity', sa.Integer, default=0),
        sa.Column('fulfillable_quantity', sa.Integer, default=0),
        sa.Column('unfulfillable_quantity', sa.Integer, default=0),
        sa.Column('reserved_quantity_total', sa.Integer, default=0),
        sa.Column('reserved_quantity_pending_customer_order', sa.Integer, default=0),
        sa.Column('reserved_quantity_pending_transshipment', sa.Integer, default=0),
        sa.Column('reserved_quantity_fc_processing', sa.Integer, default=0),
        sa.Column('researching_quantity_total', sa.Integer, default=0),
        sa.Column('researching_quantity_in_short_term', sa.Integer, default=0),
        sa.Column('researching_quantity_in_mid_term', sa.Integer, default=0),
        sa.Column('researching_quantity_in_long_term', sa.Integer, default=0),
        sa.Column('last_updated_time', sa.DateTime(timezone=True), default=sa.text('now()')),
        sa.Column('product_name', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('seller_sku')
    )

    # Create listings table
    op.create_table('listings',
        sa.Column('seller_id', sa.String(50), nullable=False),
        sa.Column('seller_sku', sa.String(100), nullable=False),
        sa.Column('asin', sa.String(20), nullable=True),
        sa.Column('product_type', sa.String(100), nullable=True),
        sa.Column('item_name', sa.String(500), nullable=True),
        sa.Column('brand_name', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('bullet_points', sa.JSON, nullable=True),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('part_number', sa.String(100), nullable=True),
        sa.Column('attributes', sa.JSON, default=dict),
        sa.Column('status', sa.String(20), default='ACTIVE'),
        sa.Column('submission_id', sa.String(100), nullable=True),
        sa.Column('issues', sa.JSON, default=list),
        sa.Column('created_date', sa.DateTime(timezone=True), default=sa.text('now()')),
        sa.Column('last_updated_date', sa.DateTime(timezone=True), default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('seller_id', 'seller_sku'),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.seller_id'], )
    )

    # Create catalog_items table
    op.create_table('catalog_items',
        sa.Column('asin', sa.String(20), nullable=False),
        sa.Column('parent_asin', sa.String(20), nullable=True),
        sa.Column('item_name', sa.String(500), nullable=True),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('classification', sa.String(100), nullable=True),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('style', sa.String(50), nullable=True),
        sa.Column('dimensions', sa.JSON, nullable=True),
        sa.Column('identifiers', sa.JSON, nullable=True),
        sa.Column('images', sa.JSON, nullable=True),
        sa.Column('product_types', sa.JSON, nullable=True),
        sa.Column('sales_rankings', sa.JSON, nullable=True),
        sa.Column('browse_node_info', sa.JSON, nullable=True),
        sa.Column('marketplace_id', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('asin', 'marketplace_id')
    )

    # Create reports table
    op.create_table('reports',
        sa.Column('report_id', sa.String(50), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('data_start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('marketplace_ids', sa.Text, nullable=True),
        sa.Column('processing_status', sa.String(20), default='IN_QUEUE'),
        sa.Column('created_time', sa.DateTime(timezone=True), default=sa.text('now()')),
        sa.Column('processing_start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('report_document_id', sa.String(100), nullable=True),
        sa.Column('report_document_url', sa.Text, nullable=True),
        sa.Column('report_options', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('report_id')
    )

    # Create feeds table
    op.create_table('feeds',
        sa.Column('feed_id', sa.String(50), nullable=False),
        sa.Column('feed_type', sa.String(100), nullable=False),
        sa.Column('marketplace_ids', sa.Text, nullable=True),
        sa.Column('created_time', sa.DateTime(timezone=True), default=sa.text('now()')),
        sa.Column('processing_status', sa.String(20), default='IN_QUEUE'),
        sa.Column('processing_start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result_feed_document_id', sa.String(100), nullable=True),
        sa.Column('feed_options', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('feed_id')
    )

    # Create shipments table
    op.create_table('shipments',
        sa.Column('shipment_id', sa.String(50), nullable=False),
        sa.Column('amazon_order_id', sa.String(50), nullable=False),
        sa.Column('seller_order_id', sa.String(50), nullable=True),
        sa.Column('shipment_status', sa.String(20), nullable=False),
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('carrier_code', sa.String(50), nullable=True),
        sa.Column('carrier_name', sa.String(100), nullable=True),
        sa.Column('shipping_method', sa.String(100), nullable=True),
        sa.Column('ship_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_arrival_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('package_dimensions', sa.JSON, nullable=True),
        sa.Column('package_weight', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('shipment_id'),
        sa.ForeignKeyConstraint(['amazon_order_id'], ['orders.amazon_order_id'], )
    )

    # Create product_pricing table
    op.create_table('product_pricing',
        sa.Column('seller_sku', sa.String(100), nullable=False),
        sa.Column('asin', sa.String(20), nullable=False),
        sa.Column('marketplace_id', sa.String(20), nullable=False),
        sa.Column('item_condition', sa.String(20), default='New'),
        sa.Column('landed_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('listing_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('shipping_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('points_value', sa.Integer, nullable=True),
        sa.Column('competitive_price_id', sa.String(20), nullable=True),
        sa.Column('number_of_offer_listings', sa.Integer, nullable=True),
        sa.Column('trade_in_value', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('seller_sku', 'asin', 'marketplace_id')
    )

    # Create finances table
    op.create_table('finances',
        sa.Column('financial_event_id', sa.String(50), nullable=False),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('financial_event_type', sa.String(50), nullable=False),
        sa.Column('amazon_order_id', sa.String(50), nullable=True),
        sa.Column('seller_order_id', sa.String(50), nullable=True),
        sa.Column('marketplace_name', sa.String(100), nullable=True),
        sa.Column('order_charge_list', sa.JSON, nullable=True),
        sa.Column('order_charge_adjustment_list', sa.JSON, nullable=True),
        sa.Column('shipment_fee_list', sa.JSON, nullable=True),
        sa.Column('shipment_fee_adjustment_list', sa.JSON, nullable=True),
        sa.Column('order_fee_list', sa.JSON, nullable=True),
        sa.Column('order_fee_adjustment_list', sa.JSON, nullable=True),
        sa.Column('direct_payment_list', sa.JSON, nullable=True),
        sa.Column('posted_date_range_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('posted_date_range_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('financial_event_id')
    )

    # Create notifications table
    op.create_table('notifications',
        sa.Column('notification_id', sa.String(50), nullable=False),
        sa.Column('notification_type', sa.String(100), nullable=False),
        sa.Column('payload_version', sa.String(10), nullable=False),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('payload', sa.JSON, nullable=False),
        sa.Column('notification_metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('notification_id')
    )

    # Create indexes for better performance
    op.create_index('idx_orders_purchase_date', 'orders', ['purchase_date'])
    op.create_index('idx_orders_marketplace_id', 'orders', ['marketplace_id'])
    op.create_index('idx_orders_status', 'orders', ['order_status'])
    op.create_index('idx_orders_last_update', 'orders', ['last_update_date'])
    op.create_index('idx_order_items_amazon_order_id', 'order_items', ['amazon_order_id'])
    op.create_index('idx_order_items_seller_sku', 'order_items', ['seller_sku'])
    op.create_index('idx_order_items_asin', 'order_items', ['asin'])
    op.create_index('idx_inventory_last_updated', 'inventory', ['last_updated_time'])
    op.create_index('idx_inventory_asin', 'inventory', ['asin'])
    op.create_index('idx_listings_seller_id', 'listings', ['seller_id'])
    op.create_index('idx_listings_asin', 'listings', ['asin'])
    op.create_index('idx_catalog_items_marketplace', 'catalog_items', ['marketplace_id'])
    op.create_index('idx_reports_type', 'reports', ['report_type'])
    op.create_index('idx_reports_status', 'reports', ['processing_status'])
    op.create_index('idx_reports_created_time', 'reports', ['created_time'])
    op.create_index('idx_feeds_type', 'feeds', ['feed_type'])
    op.create_index('idx_feeds_status', 'feeds', ['processing_status'])
    op.create_index('idx_shipments_order_id', 'shipments', ['amazon_order_id'])
    op.create_index('idx_shipments_status', 'shipments', ['shipment_status'])
    op.create_index('idx_pricing_asin', 'product_pricing', ['asin'])
    op.create_index('idx_pricing_marketplace', 'product_pricing', ['marketplace_id'])
    op.create_index('idx_finances_posted_date', 'finances', ['posted_date'])
    op.create_index('idx_finances_order_id', 'finances', ['amazon_order_id'])
    op.create_index('idx_notifications_type', 'notifications', ['notification_type'])
    op.create_index('idx_notifications_event_time', 'notifications', ['event_time'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_notifications_event_time')
    op.drop_index('idx_notifications_type')
    op.drop_index('idx_finances_order_id')
    op.drop_index('idx_finances_posted_date')
    op.drop_index('idx_pricing_marketplace')
    op.drop_index('idx_pricing_asin')
    op.drop_index('idx_shipments_status')
    op.drop_index('idx_shipments_order_id')
    op.drop_index('idx_feeds_status')
    op.drop_index('idx_feeds_type')
    op.drop_index('idx_reports_created_time')
    op.drop_index('idx_reports_status')
    op.drop_index('idx_reports_type')
    op.drop_index('idx_catalog_items_marketplace')
    op.drop_index('idx_listings_asin')
    op.drop_index('idx_listings_seller_id')
    op.drop_index('idx_inventory_asin')
    op.drop_index('idx_inventory_last_updated')
    op.drop_index('idx_order_items_asin')
    op.drop_index('idx_order_items_seller_sku')
    op.drop_index('idx_order_items_amazon_order_id')
    op.drop_index('idx_orders_last_update')
    op.drop_index('idx_orders_status')
    op.drop_index('idx_orders_marketplace_id')
    op.drop_index('idx_orders_purchase_date')

    # Drop tables
    op.drop_table('notifications')
    op.drop_table('finances')
    op.drop_table('product_pricing')
    op.drop_table('shipments')
    op.drop_table('feeds')
    op.drop_table('reports')
    op.drop_table('catalog_items')
    op.drop_table('listings')
    op.drop_table('inventory')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('sellers')
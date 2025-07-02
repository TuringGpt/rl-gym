"""
Database schemas for Amazon SP-API Mock Service
SQLAlchemy models matching the comprehensive database structure
"""

import sys
from pathlib import Path

from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_models import Base, TimestampMixin

class Seller(Base, TimestampMixin):
    """Seller model."""
    
    __tablename__ = "sellers"
    
    seller_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    marketplace_id = Column(String(20), nullable=False)
    country_code = Column(String(2), nullable=True)
    currency_code = Column(String(3), nullable=True)
    
    # Relationships
    listings = relationship("Listing", back_populates="seller", cascade="all, delete-orphan")

class Order(Base, TimestampMixin):
    """Order model."""
    
    __tablename__ = "orders"
    
    amazon_order_id = Column(String(50), primary_key=True)
    seller_order_id = Column(String(50))
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    last_update_date = Column(DateTime(timezone=True), nullable=False)
    order_status = Column(String(50), nullable=False)
    fulfillment_channel = Column(String(10), nullable=True)
    sales_channel = Column(String(50), nullable=True)
    order_channel = Column(String(50), nullable=True)
    ship_service_level = Column(String(50), nullable=True)
    marketplace_id = Column(String(20), nullable=False)
    order_total = Column(Numeric(10, 2))
    currency_code = Column(String(3), default="USD")
    number_of_items_shipped = Column(Integer, default=0)
    number_of_items_unshipped = Column(Integer, default=0)
    payment_method = Column(String(50), nullable=True)
    buyer_email = Column(String(255))
    buyer_name = Column(String(255))
    buyer_county = Column(String(255))
    buyer_tax_info = Column(JSON)
    shipment_service_level_category = Column(String(50))
    shipping_address_name = Column(String(255))
    shipping_address_line1 = Column(Text)
    shipping_address_line2 = Column(Text)
    shipping_address_city = Column(String(100))
    shipping_address_state = Column(String(50))
    shipping_address_postal_code = Column(String(20))
    shipping_address_country = Column(String(2))
    shipping_address_phone = Column(String(30))
    order_type = Column(String(20), default="StandardOrder")
    earliest_ship_date = Column(DateTime(timezone=True))
    latest_ship_date = Column(DateTime(timezone=True))
    earliest_delivery_date = Column(DateTime(timezone=True))
    latest_delivery_date = Column(DateTime(timezone=True))
    is_business_order = Column(Boolean, default=False)
    is_prime = Column(Boolean, default=False)
    is_premium_order = Column(Boolean, default=False)
    is_global_express_enabled = Column(Boolean, default=False)
    is_replacement_order = Column(Boolean, default=False)
    is_sold_by_ab = Column(Boolean, default=False)
    is_iba = Column(Boolean, default=False)
    is_ispu = Column(Boolean, default=False)
    is_access_point_order = Column(Boolean, default=False)
    has_automated_shipping_settings = Column(Boolean, default=False)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base, TimestampMixin):
    """Order item model."""
    
    __tablename__ = "order_items"
    
    order_item_id = Column(String(50), primary_key=True)
    amazon_order_id = Column(String(50), ForeignKey("orders.amazon_order_id"), nullable=False)
    seller_sku = Column(String(100), nullable=False)
    asin = Column(String(20))
    title = Column(String(500))
    quantity_ordered = Column(Integer, nullable=False)
    quantity_shipped = Column(Integer, default=0)
    item_price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2), default=0)
    item_tax = Column(Numeric(10, 2), default=0)
    shipping_tax = Column(Numeric(10, 2), default=0)
    shipping_discount = Column(Numeric(10, 2), default=0)
    shipping_discount_tax = Column(Numeric(10, 2), default=0)
    promotion_discount = Column(Numeric(10, 2), default=0)
    promotion_discount_tax = Column(Numeric(10, 2), default=0)
    cod_fee = Column(Numeric(10, 2), default=0)
    cod_fee_discount = Column(Numeric(10, 2), default=0)
    condition_id = Column(String(20), default="New")
    condition_subtype_id = Column(String(20), default="New")
    condition_note = Column(Text)
    scheduled_delivery_start_date = Column(DateTime(timezone=True))
    scheduled_delivery_end_date = Column(DateTime(timezone=True))
    price_designation = Column(String(50))
    tax_collection = Column(JSON)
    serial_number_required = Column(Boolean, default=False)
    is_transparency = Column(Boolean, default=False)
    product_info = Column(JSON)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")

class Inventory(Base, TimestampMixin):
    """Inventory model."""
    
    __tablename__ = "inventory"
    
    seller_sku = Column(String(100), primary_key=True)
    fnsku = Column(String(20))
    asin = Column(String(20))
    condition_type = Column(String(20), default="NewItem")
    total_quantity = Column(Integer, default=0)
    inbound_working_quantity = Column(Integer, default=0)
    inbound_shipped_quantity = Column(Integer, default=0)
    inbound_receiving_quantity = Column(Integer, default=0)
    fulfillable_quantity = Column(Integer, default=0)
    unfulfillable_quantity = Column(Integer, default=0)
    reserved_quantity_total = Column(Integer, default=0)
    reserved_quantity_pending_customer_order = Column(Integer, default=0)
    reserved_quantity_pending_transshipment = Column(Integer, default=0)
    reserved_quantity_fc_processing = Column(Integer, default=0)
    researching_quantity_total = Column(Integer, default=0)
    researching_quantity_in_short_term = Column(Integer, default=0)
    researching_quantity_in_mid_term = Column(Integer, default=0)
    researching_quantity_in_long_term = Column(Integer, default=0)
    last_updated_time = Column(DateTime(timezone=True), default=func.now())
    product_name = Column(String(500))

class Listing(Base, TimestampMixin):
    """Listing model."""
    
    __tablename__ = "listings"
    
    seller_id = Column(String(50), ForeignKey("sellers.seller_id"), primary_key=True)
    seller_sku = Column(String(100), primary_key=True)
    asin = Column(String(20))
    product_type = Column(String(100))
    item_name = Column(String(500))
    brand_name = Column(String(100))
    description = Column(Text)
    bullet_points = Column(JSON)
    manufacturer = Column(String(100))
    part_number = Column(String(100))
    attributes = Column(JSON, default=dict)
    status = Column(String(20), default="ACTIVE")
    submission_id = Column(String(100))
    issues = Column(JSON, default=list)
    created_date = Column(DateTime(timezone=True), default=func.now())
    last_updated_date = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    seller = relationship("Seller", back_populates="listings")

class CatalogItem(Base, TimestampMixin):
    """Catalog item model."""
    
    __tablename__ = "catalog_items"
    
    asin = Column(String(20), primary_key=True)
    marketplace_id = Column(String(20), primary_key=True)
    parent_asin = Column(String(20))
    item_name = Column(String(500))
    brand = Column(String(100))
    classification = Column(String(100))
    color = Column(String(50))
    size = Column(String(50))
    style = Column(String(50))
    dimensions = Column(JSON)
    identifiers = Column(JSON)
    images = Column(JSON)
    product_types = Column(JSON)
    sales_rankings = Column(JSON)
    browse_node_info = Column(JSON)

class Report(Base, TimestampMixin):
    """Report model."""
    
    __tablename__ = "reports"
    
    report_id = Column(String(50), primary_key=True)
    report_type = Column(String(100), nullable=False)
    data_start_time = Column(DateTime(timezone=True))
    data_end_time = Column(DateTime(timezone=True))
    marketplace_ids = Column(Text)
    processing_status = Column(String(20), default="IN_QUEUE")
    created_time = Column(DateTime(timezone=True), default=func.now())
    processing_start_time = Column(DateTime(timezone=True))
    processing_end_time = Column(DateTime(timezone=True))
    report_document_id = Column(String(100))
    report_document_url = Column(Text)
    report_options = Column(JSON)

class Feed(Base, TimestampMixin):
    """Feed model."""
    
    __tablename__ = "feeds"
    
    feed_id = Column(String(50), primary_key=True)
    feed_type = Column(String(100), nullable=False)
    marketplace_ids = Column(Text)
    created_time = Column(DateTime(timezone=True), default=func.now())
    processing_status = Column(String(20), default="IN_QUEUE")
    processing_start_time = Column(DateTime(timezone=True))
    processing_end_time = Column(DateTime(timezone=True))
    result_feed_document_id = Column(String(100))
    feed_options = Column(JSON)

class Shipment(Base, TimestampMixin):
    """Shipment model."""
    
    __tablename__ = "shipments"
    
    shipment_id = Column(String(50), primary_key=True)
    amazon_order_id = Column(String(50), ForeignKey("orders.amazon_order_id"), nullable=False)
    seller_order_id = Column(String(50))
    shipment_status = Column(String(20), nullable=False)
    tracking_number = Column(String(100))
    carrier_code = Column(String(50))
    carrier_name = Column(String(100))
    shipping_method = Column(String(100))
    ship_date = Column(DateTime(timezone=True))
    estimated_arrival_date = Column(DateTime(timezone=True))
    package_dimensions = Column(JSON)
    package_weight = Column(JSON)
    
    # Relationships
    order = relationship("Order", back_populates="shipments")

class ProductPricing(Base, TimestampMixin):
    """Product pricing model."""
    
    __tablename__ = "product_pricing"
    
    seller_sku = Column(String(100), primary_key=True)
    asin = Column(String(20), primary_key=True)
    marketplace_id = Column(String(20), primary_key=True)
    item_condition = Column(String(20), default="New")
    landed_price = Column(Numeric(10, 2))
    listing_price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2))
    points_value = Column(Integer)
    competitive_price_id = Column(String(20))
    number_of_offer_listings = Column(Integer)
    trade_in_value = Column(Numeric(10, 2))

class FinancialEvent(Base, TimestampMixin):
    """Financial event model."""
    
    __tablename__ = "finances"
    
    financial_event_id = Column(String(50), primary_key=True)
    posted_date = Column(DateTime(timezone=True))
    financial_event_type = Column(String(50), nullable=False)
    amazon_order_id = Column(String(50))
    seller_order_id = Column(String(50))
    marketplace_name = Column(String(100))
    order_charge_list = Column(JSON)
    order_charge_adjustment_list = Column(JSON)
    shipment_fee_list = Column(JSON)
    shipment_fee_adjustment_list = Column(JSON)
    order_fee_list = Column(JSON)
    order_fee_adjustment_list = Column(JSON)
    direct_payment_list = Column(JSON)
    posted_date_range_start = Column(DateTime(timezone=True))
    posted_date_range_end = Column(DateTime(timezone=True))

class Notification(Base, TimestampMixin):
    """Notification model."""
    
    __tablename__ = "notifications"
    
    notification_id = Column(String(50), primary_key=True)
    notification_type = Column(String(100), nullable=False)
    payload_version = Column(String(10), nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON, nullable=False)
    notification_metadata = Column(JSON)
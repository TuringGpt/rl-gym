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
    messaging_actions = relationship("MessagingAction", back_populates="order", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="order", cascade="all, delete-orphan")
    buyer_attributes = relationship("BuyerAttributes", back_populates="order", uselist=False, cascade="all, delete-orphan")

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
    seller_id = Column(String(50))
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    size_name = Column(String(50))
    style_name = Column(String(50))
    product_category_id = Column(String(100))
    vendor_details = Column(JSON)

class CatalogCategory(Base, TimestampMixin):
    """Catalog category model."""
    
    __tablename__ = "catalog_categories"
    
    product_category_id = Column(String(100), primary_key=True)
    marketplace_id = Column(String(20), primary_key=True)
    product_category_name = Column(String(200), nullable=False)
    parent_category_id = Column(String(100))

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

class ProductFees(Base, TimestampMixin):
    """Product fees model for Amazon Product Fees API."""
    
    __tablename__ = "product_fees"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_sku = Column(String(100))
    asin = Column(String(20))
    marketplace_id = Column(String(20), nullable=False)
    seller_id = Column(String(50), nullable=False)
    product_type = Column(String(100))
    item_condition = Column(String(20), default="New")
    fulfillment_fee = Column(Numeric(10, 2), default=0.00)
    referral_fee_rate = Column(Numeric(5, 4), default=0.15)  # As percentage (0.15 = 15%)
    storage_fee = Column(Numeric(10, 2), default=0.00)
    removal_fee = Column(Numeric(10, 2), default=0.00)
    disposal_fee = Column(Numeric(10, 2), default=0.00)
    return_processing_fee = Column(Numeric(10, 2), default=0.00)
    high_volume_listing_fee = Column(Numeric(10, 2), default=0.00)
    multichannel_fulfillment_fee = Column(Numeric(10, 2), default=0.00)
    weight = Column(Numeric(8, 2))  # Product weight in pounds
    dimensions = Column(JSON)  # {"length": x, "width": y, "height": z}
    category = Column(String(100))  # Product category for fee calculations

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

class Invoice(Base, TimestampMixin):
    """Invoice model."""
    
    __tablename__ = "invoices"
    
    id = Column(String(50), primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False)
    error_code = Column(String(100))
    external_invoice_id = Column(String(100))
    gov_response = Column(Text)
    invoice_type = Column(String(50), nullable=False)
    series = Column(String(50))
    status = Column(String(50), nullable=False)
    transaction_ids = Column(JSON)
    transaction_type = Column(String(50), nullable=False)
    
    # Relationships
    documents = relationship("InvoiceDocument", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceDocument(Base, TimestampMixin):
    """Invoice document model."""
    
    __tablename__ = "invoice_documents"
    
    document_id = Column(String(50), primary_key=True)
    invoice_id = Column(String(50), ForeignKey("invoices.id"), nullable=False)
    document_url = Column(Text, nullable=False)
    document_type = Column(String(50), default="PDF")
    file_size = Column(Integer)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="documents")

class InvoiceExport(Base, TimestampMixin):
    """Invoice export model."""
    
    __tablename__ = "invoice_exports"
    
    export_id = Column(String(50), primary_key=True)
    status = Column(String(50), nullable=False, default="REQUESTED")
    generate_export_started_at = Column(DateTime(timezone=True))
    generate_export_finished_at = Column(DateTime(timezone=True))
    invoices_document_ids = Column(JSON)
    error_message = Column(Text)
    request_filters = Column(JSON)

class InvoiceAttribute(Base, TimestampMixin):
    """Invoice attribute model for filtering options."""
    
    __tablename__ = "invoice_attributes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_type = Column(String(50), nullable=False)  # status, invoice_type, etc.
    value = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)

class SalesMetrics(Base, TimestampMixin):
    """Sales metrics model for aggregated sales data."""
    
    __tablename__ = "sales_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interval = Column(String(100), nullable=False)  # e.g., "2024-01-01T00:00:00Z/2024-01-01T01:00:00Z"
    granularity = Column(String(20), nullable=False)  # Hour, Day, Week, Month, Quarter, Year
    unit_count = Column(Integer, default=0)
    order_item_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    average_unit_price = Column(Numeric(10, 2), default=0.00)
    total_sales = Column(Numeric(10, 2), default=0.00)
    currency_code = Column(String(3), default="USD")
    buyer_type = Column(String(10), default="All")  # All, B2B, B2C
    marketplace_ids = Column(JSON)
    asin = Column(String(20))
    sku = Column(String(100))
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

class MessagingAction(Base, TimestampMixin):
    """Messaging action model for available message types per order."""
    
    __tablename__ = "messaging_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amazon_order_id = Column(String(50), ForeignKey("orders.amazon_order_id"), nullable=False)
    marketplace_id = Column(String(20), nullable=False)
    action_name = Column(String(100), nullable=False)  # confirmCustomizationDetails, negativeFeedbackRemoval, etc.
    is_available = Column(Boolean, default=True)
    description = Column(String(500))
    
    # Relationships
    order = relationship("Order", back_populates="messaging_actions")

class Message(Base, TimestampMixin):
    """Message model for buyer-seller communications."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amazon_order_id = Column(String(50), ForeignKey("orders.amazon_order_id"), nullable=False)
    message_type = Column(String(100), nullable=False)  # Same as action_name
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    status = Column(String(20), default="sent")  # sent, delivered, failed
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Relationships
    order = relationship("Order", back_populates="messages")

class BuyerAttributes(Base, TimestampMixin):
    """Buyer attributes model for messaging requirements."""
    
    __tablename__ = "buyer_attributes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amazon_order_id = Column(String(50), ForeignKey("orders.amazon_order_id"), nullable=False, unique=True)
    locale = Column(String(10), default="en-US")  # en-US, es-MX, fr-CA, etc.
    country_code = Column(String(2))
    language_code = Column(String(2))
    
    # Relationships
    order = relationship("Order", back_populates="buyer_attributes")
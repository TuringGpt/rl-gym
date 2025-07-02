"""
Database schemas for Amazon SP-API Mock Service
SQLAlchemy models matching the database structure
"""

import sys
from pathlib import Path

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_models import Base, TimestampMixin

class Seller(Base, TimestampMixin):
    """Seller model."""
    
    __tablename__ = "sellers"
    
    seller_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    marketplace_id = Column(String(20), nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="seller", cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="seller", cascade="all, delete-orphan")

class Order(Base, TimestampMixin):
    """Order model."""
    
    __tablename__ = "orders"
    
    amazon_order_id = Column(String(50), primary_key=True)
    seller_order_id = Column(String(50))
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    last_update_date = Column(DateTime(timezone=True), nullable=False)
    order_status = Column(String(50), nullable=False)
    marketplace_id = Column(String(20), nullable=False)
    order_total = Column(Numeric(10, 2))
    currency_code = Column(String(3), default="USD")
    buyer_email = Column(String(255))
    shipping_address_name = Column(String(255))
    shipping_address_line1 = Column(Text)
    shipping_address_city = Column(String(100))
    shipping_address_state = Column(String(50))
    shipping_address_postal_code = Column(String(20))
    shipping_address_country = Column(String(2))
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    seller = relationship("Seller", back_populates="orders")

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
    reserved_quantity = Column(Integer, default=0)
    last_updated_time = Column(DateTime(timezone=True), default=func.now())

class Listing(Base, TimestampMixin):
    """Listing model."""
    
    __tablename__ = "listings"
    
    seller_id = Column(String(50), ForeignKey("sellers.seller_id"), primary_key=True)
    seller_sku = Column(String(100), primary_key=True)
    product_type = Column(String(100))
    attributes = Column(JSON, default=dict)
    status = Column(String(20), default="ACTIVE")
    created_date = Column(DateTime(timezone=True), default=func.now())
    last_updated_date = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    seller = relationship("Seller", back_populates="listings")

class Report(Base, TimestampMixin):
    """Report model."""
    
    __tablename__ = "reports"
    
    report_id = Column(String(50), primary_key=True)
    report_type = Column(String(100), nullable=False)
    processing_status = Column(String(20), default="IN_PROGRESS")
    created_time = Column(DateTime(timezone=True), default=func.now())
    processing_start_time = Column(DateTime(timezone=True))
    processing_end_time = Column(DateTime(timezone=True))
    marketplace_ids = Column(Text)
    report_document_url = Column(Text)
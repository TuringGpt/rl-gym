"""
Base models for API Mock Gym services.
Provides common model patterns and mixins.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

# SQLAlchemy Base
Base = declarative_base()

class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    """Mixin for adding UUID primary key."""
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class MetadataMixin:
    """Mixin for adding metadata JSON field."""
    
    metadata = Column(JSON, default=dict)

# Base SQLAlchemy Model
class BaseDBModel(Base, TimestampMixin):
    """Base model for all database entities."""
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat() + "Z"
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Pydantic Base Models
class BaseAPIModel(BaseModel):
    """Base Pydantic model for API serialization."""
    
    class Config:
        from_attributes = True
        populate_by_name = True
        str_strip_whitespace = True
        validate_assignment = True

class TimestampModel(BaseAPIModel):
    """Base model with timestamp fields."""
    
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class PaginationRequest(BaseAPIModel):
    """Standard pagination request model."""
    
    limit: int = Field(default=50, ge=1, le=100, description="Number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    page: Optional[int] = Field(None, ge=1, description="Page number (alternative to offset)")

class PaginationResponse(BaseAPIModel):
    """Standard pagination response model."""
    
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Number of items per page")
    offset: int = Field(description="Number of items skipped")
    has_more: bool = Field(description="Whether there are more items")
    next_token: Optional[str] = Field(None, description="Token for next page")

class HealthResponse(BaseAPIModel):
    """Health check response model."""
    
    status: str = Field(description="Service status")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    timestamp: datetime = Field(description="Health check timestamp")
    database: Optional[Dict[str, Any]] = Field(None, description="Database health status")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency status")

class APIResponse(BaseAPIModel):
    """Generic API response wrapper."""
    
    success: bool = Field(description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

# Service-specific base models
class AmazonBaseModel(BaseAPIModel):
    """Base model for Amazon SP-API objects."""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class SlackBaseModel(BaseAPIModel):
    """Base model for Slack API objects."""
    
    class Config:
        extra = "allow"  # Slack API allows extra fields

class StripeBaseModel(BaseAPIModel):
    """Base model for Stripe API objects."""
    
    object: str = Field(description="Object type")
    id: str = Field(description="Unique identifier")
    created: int = Field(description="Creation timestamp")
    livemode: bool = Field(default=False, description="Whether in live mode")

class NotionBaseModel(BaseAPIModel):
    """Base model for Notion API objects."""
    
    object: str = Field(description="Object type")
    id: str = Field(description="Unique identifier")
    created_time: datetime = Field(description="Creation time")
    last_edited_time: datetime = Field(description="Last edited time")

# Common field types
class Address(BaseAPIModel):
    """Address model used across services."""
    
    name: Optional[str] = Field(None, description="Recipient name")
    line1: Optional[str] = Field(None, description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country code")

class Money(BaseAPIModel):
    """Money representation used across services."""
    
    amount: float = Field(description="Amount")
    currency: str = Field(default="USD", description="Currency code")

class Contact(BaseAPIModel):
    """Contact information model."""
    
    name: Optional[str] = Field(None, description="Contact name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")

class DateRange(BaseAPIModel):
    """Date range model for filtering."""
    
    start_date: datetime = Field(description="Start date")
    end_date: datetime = Field(description="End date")
    
    def validate_range(self):
        """Validate that start_date is before end_date."""
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")

# Utility classes
class FilterMixin:
    """Mixin for adding common filter methods to models."""
    
    @classmethod
    def apply_filters(cls, query, filters: Dict[str, Any]):
        """Apply filters to SQLAlchemy query."""
        for field, value in filters.items():
            if hasattr(cls, field) and value is not None:
                if isinstance(value, list):
                    query = query.filter(getattr(cls, field).in_(value))
                elif isinstance(value, dict):
                    # Handle range filters
                    if 'gte' in value:
                        query = query.filter(getattr(cls, field) >= value['gte'])
                    if 'lte' in value:
                        query = query.filter(getattr(cls, field) <= value['lte'])
                    if 'gt' in value:
                        query = query.filter(getattr(cls, field) > value['gt'])
                    if 'lt' in value:
                        query = query.filter(getattr(cls, field) < value['lt'])
                else:
                    query = query.filter(getattr(cls, field) == value)
        return query

class SearchMixin:
    """Mixin for adding search functionality."""
    
    @classmethod
    def search_fields(cls, query, search_term: str, fields: list):
        """Search across multiple text fields."""
        if not search_term or not fields:
            return query
        
        search_conditions = []
        for field in fields:
            if hasattr(cls, field):
                search_conditions.append(
                    getattr(cls, field).ilike(f"%{search_term}%")
                )
        
        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))
        
        return query

# Validation utilities
def validate_marketplace_id(marketplace_id: str) -> bool:
    """Validate Amazon marketplace ID format."""
    amazon_marketplaces = {
        "ATVPDKIKX0DER": "US",
        "A2EUQ1WTGCTBG2": "CA", 
        "A1PA6795UKMFR9": "DE",
        "APJ6JRA9NG5V4": "MX",
        "A1RKKUPIHCS9HS": "ES",
        "A13V1IB3VIYZZH": "FR",
        "A21TJRUUN4KGV": "IN",
        "A1F83G8C2ARO7P": "UK",
        "A1VC38T7YXB528": "JP",
        "ARBP9OOSHTCHU": "EG",
        "A2Q3Y263D00KWC": "BR"
    }
    return marketplace_id in amazon_marketplaces

def validate_currency_code(currency: str) -> bool:
    """Validate ISO 4217 currency code."""
    common_currencies = {
        "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD",
        "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW"
    }
    return currency.upper() in common_currencies

def validate_country_code(country: str) -> bool:
    """Validate ISO 3166-1 alpha-2 country code."""
    common_countries = {
        "US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "SE",
        "NO", "DK", "FI", "PL", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "LT",
        "LV", "EE", "IE", "PT", "GR", "CY", "MT", "LU", "JP", "AU", "NZ", "IN",
        "CN", "SG", "HK", "TW", "KR", "TH", "MY", "ID", "PH", "VN", "BR", "MX",
        "AR", "CL", "CO", "PE", "VE", "UY", "PY", "BO", "EC", "ZA", "EG", "MA",
        "NG", "KE", "GH", "TN", "DZ", "AO", "ET", "UG", "TZ", "MZ", "MG", "ZM"
    }
    return country.upper() in common_countries
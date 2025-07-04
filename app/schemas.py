from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# Request schemas
class ListingItemCreate(BaseModel):
    seller_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = 0
    status: Optional[str] = "ACTIVE"
    marketplace_ids: Optional[List[str]] = []


class ListingItemUpdate(BaseModel):
    seller_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    marketplace_ids: Optional[List[str]] = None


# Response schemas matching Amazon SP-API format
class ListingSummary(BaseModel):
    marketplace_id: str
    asin: Optional[str] = None
    product_type: str = "PRODUCT"
    status: str


class ListingAttributes(BaseModel):
    seller_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None


class ListingIssue(BaseModel):
    code: str
    message: str
    severity: str = "WARNING"


class ListingItemResponse(BaseModel):
    sku: str
    status: str
    summaries: List[ListingSummary]
    attributes: ListingAttributes
    issues: List[ListingIssue] = []


class ListingItemsSearchResponse(BaseModel):
    items: List[ListingItemResponse]
    pagination: Optional[Dict[str, Any]] = None


# Internal schemas
class ListingItemDB(BaseModel):
    id: int
    seller_id: str
    seller_name: Optional[str] = None
    sku: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    status: str
    marketplace_ids: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Error response schema
class ErrorResponse(BaseModel):
    errors: List[Dict[str, Any]]

"""
Listings-related Pydantic models for Amazon SP-API
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.base_models import AmazonBaseModel
from pydantic import Field

class ListingAttributes(AmazonBaseModel):
    """Listing attributes model."""
    condition_type: Optional[str] = "new"
    condition_note: Optional[str] = None
    price: Optional[Dict[str, Any]] = None
    quantity: Optional[int] = None
    handling_time: Optional[int] = None
    fulfillment_channel_type: Optional[str] = "DEFAULT"
    merchant_shipping_group: Optional[str] = None
    item_name: Optional[str] = None
    brand_name: Optional[str] = None
    product_description: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    item_type_keyword: Optional[str] = None
    catalog_number: Optional[str] = None
    search_terms: Optional[List[str]] = None
    platinum_keywords: Optional[List[str]] = None
    memorabilia: Optional[bool] = False
    autographed: Optional[bool] = False
    used_for: Optional[List[str]] = None
    item_dimensions: Optional[Dict[str, Any]] = None
    item_weight: Optional[Dict[str, Any]] = None
    package_dimensions: Optional[Dict[str, Any]] = None
    package_weight: Optional[Dict[str, Any]] = None
    shipping_weight: Optional[Dict[str, Any]] = None

class PatchOperation(AmazonBaseModel):
    """JSON Patch operation for listings."""
    op: str = Field(description="Operation type (add, remove, replace)")
    path: str = Field(description="JSON path to the field")
    value: Optional[Any] = Field(None, description="Value for the operation")

class ListingSubmission(AmazonBaseModel):
    """Listing submission model."""
    productType: str = Field(description="Product type")
    requirements: Optional[str] = "LISTING"
    attributes: Dict[str, Any] = Field(description="Listing attributes")

class ListingItem(AmazonBaseModel):
    """Listing item model."""
    sku: str
    productType: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = "ACTIVE"
    submissionId: Optional[str] = None

class ListingResponse(AmazonBaseModel):
    """Listing response model."""
    sku: str
    status: str
    submissionId: str
    issues: List[Dict[str, Any]] = []

class ListingRequest(AmazonBaseModel):
    """Listing request model."""
    productType: str
    requirements: Optional[str] = "LISTING"
    attributes: Dict[str, Any]

class ListingsItemResponse(AmazonBaseModel):
    """Get listings item response."""
    sku: str
    status: str
    attributeSets: Optional[List[Dict[str, Any]]] = None
    issues: Optional[List[Dict[str, Any]]] = None
    offers: Optional[List[Dict[str, Any]]] = None
    fulfillmentAvailability: Optional[List[Dict[str, Any]]] = None
    procurement: Optional[Dict[str, Any]] = None

# Common attribute structures
class PriceAttribute(AmazonBaseModel):
    """Price attribute structure."""
    Amount: float
    CurrencyCode: str = "USD"

class DimensionAttribute(AmazonBaseModel):
    """Dimension attribute structure."""
    Length: Optional[float] = None
    Width: Optional[float] = None
    Height: Optional[float] = None
    Unit: str = "inches"

class WeightAttribute(AmazonBaseModel):
    """Weight attribute structure."""
    Value: float
    Unit: str = "pounds"

# Product type specific attributes
class ElectronicsAttributes(ListingAttributes):
    """Electronics specific attributes."""
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    connectivity_technology: Optional[List[str]] = None
    special_features: Optional[List[str]] = None
    compatible_devices: Optional[List[str]] = None
    included_components: Optional[List[str]] = None
    batteries_required: Optional[bool] = False
    batteries_included: Optional[bool] = False

class ClothingAttributes(ListingAttributes):
    """Clothing specific attributes."""
    size_name: Optional[str] = None
    color_name: Optional[str] = None
    style_name: Optional[str] = None
    material_type: Optional[List[str]] = None
    care_instructions: Optional[str] = None
    fabric_type: Optional[str] = None
    sleeve_type: Optional[str] = None
    neck_style: Optional[str] = None
    closure_type: Optional[str] = None

class HomeKitchenAttributes(ListingAttributes):
    """Home & Kitchen specific attributes."""
    material: Optional[List[str]] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    style: Optional[str] = None
    finish_type: Optional[str] = None
    room_type: Optional[List[str]] = None
    assembly_required: Optional[bool] = False
    number_of_pieces: Optional[int] = None
    care_instructions: Optional[str] = None

class SportsAttributes(ListingAttributes):
    """Sports & Outdoors specific attributes."""
    sport_type: Optional[List[str]] = None
    age_range: Optional[str] = None
    skill_level: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[List[str]] = None
    team_name: Optional[str] = None
    league: Optional[str] = None
    season: Optional[str] = None

class BooksAttributes(ListingAttributes):
    """Books specific attributes."""
    author: Optional[List[str]] = None
    binding: Optional[str] = None
    edition: Optional[str] = None
    format: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    number_of_pages: Optional[int] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    reading_level: Optional[str] = None
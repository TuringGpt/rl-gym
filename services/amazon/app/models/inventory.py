"""
Inventory-related Pydantic models for Amazon SP-API
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.base_models import AmazonBaseModel
from pydantic import Field

class InventorySummary(AmazonBaseModel):
    """Inventory summary model."""
    asin: Optional[str] = None
    fnSku: Optional[str] = None
    sellerSku: Optional[str] = None
    condition: Optional[str] = "NewItem"
    inventoryDetails: Optional[dict] = None
    lastUpdatedTime: Optional[str] = None
    productName: Optional[str] = None
    totalQuantity: Optional[int] = 0

class InventoryDetails(AmazonBaseModel):
    """Detailed inventory information."""
    asin: Optional[str] = None
    fnSku: Optional[str] = None
    sellerSku: Optional[str] = None
    condition: Optional[str] = "NewItem"
    totalQuantity: Optional[int] = 0
    fulfillableQuantity: Optional[int] = 0
    inboundWorkingQuantity: Optional[int] = 0
    inboundShippedQuantity: Optional[int] = 0
    inboundReceivingQuantity: Optional[int] = 0
    reservedQuantity: Optional[dict] = None
    unfulfillableQuantity: Optional[int] = 0
    lastUpdatedTime: Optional[str] = None
    productName: Optional[str] = None

class InventorySummariesResponse(AmazonBaseModel):
    """Inventory summaries response."""
    payload: dict = Field(description="Inventory summaries payload")

class InventoryDetailsResponse(AmazonBaseModel):
    """Inventory details response."""
    payload: dict = Field(description="Inventory details payload")

class InventorySummaryResponse(AmazonBaseModel):
    """Single inventory summary response."""
    payload: InventorySummary

# Request models
class InventoryRequest(AmazonBaseModel):
    """Inventory request parameters."""
    granularityType: str = Field(default="Marketplace", description="Granularity type")
    granularityId: str = Field(description="Granularity ID (marketplace ID)")
    marketplaceIds: List[str] = Field(description="List of marketplace IDs")
    details: Optional[bool] = Field(default=False, description="Include details")
    startDateTime: Optional[str] = None
    sellerSkus: Optional[List[str]] = None
    nextToken: Optional[str] = None
    maxResults: Optional[int] = Field(default=50, ge=1, le=50)
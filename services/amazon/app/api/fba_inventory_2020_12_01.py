"""
Amazon FBA Inventory API v2020-12-01
Based on: https://developer-docs.amazon.com/sp-api/docs/fba-inventory-api-v1-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import Inventory
import sys
from pathlib import Path

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/fba/inventory/v1", tags=["FBA Inventory"])

# Response Models
class InventoryDetails(BaseModel):
    fulfillable_quantity: Optional[int] = None
    inbound_working_quantity: Optional[int] = None
    inbound_shipped_quantity: Optional[int] = None
    inbound_receiving_quantity: Optional[int] = None
    reserved_quantity: Optional[dict] = None
    unfulfillable_quantity: Optional[int] = None
    total_quantity: Optional[int] = None

class ResearchingQuantityEntry(BaseModel):
    name: str
    quantity: int

class ResearchingQuantity(BaseModel):
    total_researching_quantity: Optional[int] = None
    researching_quantity_breakdown: Optional[List[ResearchingQuantityEntry]] = None

class InventorySummary(BaseModel):
    asin: Optional[str] = None
    fn_sku: Optional[str] = None
    seller_sku: Optional[str] = None
    condition: Optional[str] = None
    inventory_details: Optional[InventoryDetails] = None
    last_updated_time: Optional[datetime] = None
    product_name: Optional[str] = None
    total_quantity: Optional[int] = None

class InventorySummariesResult(BaseModel):
    pagination: Optional[dict] = None
    inventory_summaries: List[InventorySummary]

class GetInventorySummariesResponse(BaseModel):
    payload: InventorySummariesResult
    errors: Optional[List[dict]] = None

@router.get("/summaries", response_model=GetInventorySummariesResponse)
async def get_inventory_summaries(
    granularity_type: str = Query(..., description="The granularity type for the inventory aggregation level"),
    granularity_id: str = Query(..., description="The granularity ID for the inventory aggregation level"),
    marketplace_ids: List[str] = Query(..., description="A list of marketplace identifiers"),
    details: bool = Query(False, description="true to return inventory summaries with additional summarized inventory details and quantities"),
    start_date_time: Optional[datetime] = Query(None, description="A start date and time in ISO8601 format"),
    seller_skus: Optional[List[str]] = Query(None, description="A list of seller SKUs for which to return inventory summaries"),
    next_token: Optional[str] = Query(None, description="String token returned in the response of your previous request"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of inventory summaries. The summaries returned depend on the presence or absence of the startDateTime, sellerSkus, and sellerSku parameters:

    - All inventory summaries with available details are returned when the startDateTime, sellerSkus, and sellerSku parameters are omitted.
    - When startDateTime is provided, the operation returns inventory summaries that have had inventory movement after (or at) a given startDateTime.
    - When the sellerSkus parameter is provided, the operation returns inventory summaries for only the specified sellerSkus.
    """
    
    try:
        query = db.query(Inventory)
        
        # Filter by seller SKUs if provided
        if seller_skus:
            query = query.filter(Inventory.seller_sku.in_(seller_skus))
        
        # Filter by date if provided
        if start_date_time:
            query = query.filter(Inventory.last_updated_time >= start_date_time)
        
        inventories = query.all()
        
        inventory_summaries = []
        for inv in inventories:
            reserved_quantity = {
                "total_reserved_quantity": inv.reserved_quantity_total,
                "pending_customer_order": inv.reserved_quantity_pending_customer_order,
                "pending_transshipment": inv.reserved_quantity_pending_transshipment,
                "fc_processing": inv.reserved_quantity_fc_processing
            } if details else None
            
            inventory_details = InventoryDetails(
                fulfillable_quantity=inv.fulfillable_quantity,
                inbound_working_quantity=inv.inbound_working_quantity,
                inbound_shipped_quantity=inv.inbound_shipped_quantity,
                inbound_receiving_quantity=inv.inbound_receiving_quantity,
                reserved_quantity=reserved_quantity,
                unfulfillable_quantity=inv.unfulfillable_quantity,
                total_quantity=inv.total_quantity
            ) if details else None
            
            summary = InventorySummary(
                asin=inv.asin,
                fn_sku=inv.fnsku,
                seller_sku=inv.seller_sku,
                condition=inv.condition_type,
                inventory_details=inventory_details,
                last_updated_time=inv.last_updated_time,
                product_name=inv.product_name,
                total_quantity=inv.total_quantity
            )
            inventory_summaries.append(summary)
        
        result = InventorySummariesResult(
            inventory_summaries=inventory_summaries,
            pagination={"next_token": None}  # Simplified pagination
        )
        
        return amazon_formatter.success_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summaries/{granularity_type}/{granularity_id}", response_model=GetInventorySummariesResponse)
async def get_inventory_summaries_by_granularity(
    granularity_type: str,
    granularity_id: str,
    marketplace_ids: List[str] = Query(..., description="A list of marketplace identifiers"),
    details: bool = Query(False, description="true to return inventory summaries with additional summarized inventory details and quantities"),
    start_date_time: Optional[datetime] = Query(None, description="A start date and time in ISO8601 format"),
    seller_skus: Optional[List[str]] = Query(None, description="A list of seller SKUs for which to return inventory summaries"),
    next_token: Optional[str] = Query(None, description="String token returned in the response of your previous request"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of inventory summaries. This operation filters inventory summaries based on the granularity type and ID provided.
    """
    
    # Same logic as above but with granularity filtering
    return await get_inventory_summaries(
        granularity_type=granularity_type,
        granularity_id=granularity_id,
        marketplace_ids=marketplace_ids,
        details=details,
        start_date_time=start_date_time,
        seller_skus=seller_skus,
        next_token=next_token,
        db=db
    )
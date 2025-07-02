"""
Amazon SP-API Listings 2021-08-01 endpoints
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Path as FastAPIPath
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.auth import get_amazon_user, require_amazon_scopes
from utils.response_formatter import amazon_formatter
from utils.rate_limiter import check_amazon_rate_limit

# Import local modules
from app.database.connection import get_db
from app.services.listing_service import ListingService
from app.models.listings import ListingRequest, ListingResponse

router = APIRouter()

@router.put("/items/{sellerId}/{sku}")
async def put_listings_item(
    request: Request,
    listing_data: ListingRequest,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = None,
    issueLocale: Optional[str] = None,
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::listings"]))
):
    """Create or update a listing."""
    await check_amazon_rate_limit(request)
    
    listing_service = ListingService(db)
    result = await listing_service.create_or_update_listing(
        seller_id=sellerId,
        sku=sku,
        product_type=listing_data.productType,
        attributes=listing_data.attributes,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else None
    )
    
    return amazon_formatter.listings_response(result)

@router.get("/items/{sellerId}/{sku}")
async def get_listings_item(
    request: Request,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = None,
    includedData: Optional[str] = None,
    issueLocale: Optional[str] = None,
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::listings"]))
):
    """Get listing details."""
    await check_amazon_rate_limit(request)
    
    listing_service = ListingService(db)
    listing = await listing_service.get_listing(
        seller_id=sellerId,
        sku=sku,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else None
    )
    
    if not listing:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Listing not found for SKU {sku}"
            ).body.decode()
        )
    
    return {
        "sku": sku,
        "status": listing.get("status", "ACTIVE"),
        "attributeSets": listing.get("attribute_sets", []),
        "issues": listing.get("issues", [])
    }

@router.delete("/items/{sellerId}/{sku}")
async def delete_listings_item(
    request: Request,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = None,
    issueLocale: Optional[str] = None,
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::listings"]))
):
    """Delete a listing."""
    await check_amazon_rate_limit(request)
    
    listing_service = ListingService(db)
    result = await listing_service.delete_listing(
        seller_id=sellerId,
        sku=sku,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else None
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Listing not found for SKU {sku}"
            ).body.decode()
        )
    
    return {
        "sku": sku,
        "status": "DELETED",
        "submissionId": result.get("submission_id"),
        "issues": []
    }
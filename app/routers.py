from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.session_manager import session_manager
from app.crud import create_listing_item, delete_listing_item, get_listing_item, get_listing_items, update_listing_item
from app.schemas import ListingAttributes, ListingItemCreate, ListingItemResponse, ListingItemUpdate, ListingItemsSearchResponse, ListingSummary
from .database import get_db, get_session_db
from .models import ListingItem

router = APIRouter()


def get_db_for_session(x_session_id: str = Header(..., alias="X-Session-ID")):
    """Get database session for required session ID from header"""
    # Validate session exists
    if not session_manager.session_exists(x_session_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session ID: {x_session_id}. Please create a session first using POST /sessions",
        )

    db = session_manager.get_session_db(x_session_id)
    try:
        yield db
    finally:
        db.close()


def convert_db_to_response(db_listing: ListingItem) -> ListingItemResponse:
    """Convert database model to API response format"""
    marketplace_ids = db_listing.get_marketplace_ids()

    # Create summaries for each marketplace
    summaries = []
    if marketplace_ids:
        for marketplace_id in marketplace_ids:
            summaries.append(
                ListingSummary(
                    marketplace_id=marketplace_id,
                    asin=f"B{db_listing.id:09d}",  # Mock ASIN
                    product_type="PRODUCT",
                    status=db_listing.status,
                )
            )
    else:
        # Default marketplace if none specified
        summaries.append(
            ListingSummary(
                marketplace_id="ATVPDKIKX0DER",  # US marketplace
                asin=f"B{db_listing.id:09d}",
                product_type="PRODUCT",
                status=db_listing.status,
            )
        )

    attributes = ListingAttributes(
        seller_name=db_listing.seller_name,
        title=db_listing.title,
        description=db_listing.description,
        price=db_listing.price,
        quantity=db_listing.quantity,
    )

    return ListingItemResponse(
        sku=db_listing.sku,
        status=db_listing.status,
        summaries=summaries,
        attributes=attributes,
        issues=[],
    )


@router.get("/listings/2021-08-01/items/{seller_id}/{sku}", response_model=ListingItemResponse)
def get_listings_item(
    seller_id: str,
    sku: str,
    marketplace_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db_for_session),
):
    """Get details about a listings item for a selling partner"""
    db_listing = get_listing_item(db, seller_id=seller_id, sku=sku)
    if db_listing is None:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": f"Listing not found for seller {seller_id} and SKU {sku}",
                        "details": "",
                    }
                ]
            },
        )

    return convert_db_to_response(db_listing)


@router.put("/listings/2021-08-01/items/{seller_id}/{sku}", response_model=ListingItemResponse)
def put_listings_item(
    seller_id: str,
    sku: str,
    listing: ListingItemCreate,
    db: Session = Depends(get_db_for_session),
):
    """Create or fully update a listings item"""
    db_listing = get_listing_item(db, seller_id=seller_id, sku=sku)

    if db_listing:
        # Update existing listing
        update_data = ListingItemUpdate(**listing.model_dump())
        db_listing = update_listing_item(db, db_listing, update_data)
    else:
        # Create new listing
        db_listing = create_listing_item(db, seller_id, sku, listing)

    return convert_db_to_response(db_listing)


@router.patch("/listings/2021-08-01/items/{seller_id}/{sku}", response_model=ListingItemResponse)
def patch_listings_item(
    seller_id: str,
    sku: str,
    listing: ListingItemUpdate,
    db: Session = Depends(get_db_for_session),
):
    """Partially update a listings item"""
    db_listing = get_listing_item(db, seller_id=seller_id, sku=sku)
    if db_listing is None:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": f"Listing not found for seller {seller_id} and SKU {sku}",
                        "details": "",
                    }
                ]
            },
        )

    db_listing = update_listing_item(db, db_listing, listing)
    return convert_db_to_response(db_listing)


@router.delete("/listings/2021-08-01/items/{seller_id}/{sku}")
def delete_listings_item(
    seller_id: str,
    sku: str,
    db: Session = Depends(get_db_for_session),
):
    """Delete a listings item"""
    db_listing = get_listing_item(db, seller_id=seller_id, sku=sku)
    if db_listing is None:
        raise HTTPException(
            status_code=404,
            detail={
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": f"Listing not found for seller {seller_id} and SKU {sku}",
                        "details": "",
                    }
                ]
            },
        )

    delete_listing_item(db, db_listing)
    return {"message": "Listing item deleted successfully"}


@router.get("/listings/2021-08-01/items", response_model=ListingItemsSearchResponse)
def search_listings_items(
    seller_id: Optional[str] = Query(None),
    seller_name: Optional[str] = Query(None, description="Search by seller name (partial match)"),
    title_search: Optional[str] = Query(None, description="Search in product title and description"),
    marketplace_ids: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_for_session),
):
    """Search for listings items with enhanced search capabilities"""
    db_listings = get_listing_items(
        db,
        seller_id=seller_id,
        seller_name=seller_name,
        title_search=title_search,
        marketplace_ids=marketplace_ids,
        status=status,
        skip=skip,
        limit=limit,
    )

    items = [convert_db_to_response(listing) for listing in db_listings]

    return ListingItemsSearchResponse(
        items=items, pagination={"total": len(items), "skip": skip, "limit": limit}
    )

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import ListingItem
from app.schemas import ListingItemCreate, ListingItemUpdate
from typing import List, Optional
import json


def get_listing_item(db: Session, seller_id: str, sku: str) -> Optional[ListingItem]:
    """Get a single listing item by seller_id and sku"""
    return db.query(ListingItem).filter(and_(ListingItem.seller_id == seller_id, ListingItem.sku == sku)).first()


def get_listing_items(
    db: Session,
    seller_id: Optional[str] = None,
    seller_name: Optional[str] = None,
    title_search: Optional[str] = None,
    marketplace_ids: Optional[List[str]] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ListingItem]:
    """Get multiple listing items with optional filters and search"""
    query = db.query(ListingItem)

    if seller_id:
        query = query.filter(ListingItem.seller_id == seller_id)

    if seller_name:
        query = query.filter(ListingItem.seller_name.ilike(f"%{seller_name}%"))

    if title_search:
        # Search in both title and description
        query = query.filter(
            or_(ListingItem.title.ilike(f"%{title_search}%"), ListingItem.description.ilike(f"%{title_search}%"))
        )

    if status:
        query = query.filter(ListingItem.status == status)

    if marketplace_ids:
        # Filter by marketplace_ids (JSON contains check)
        for marketplace_id in marketplace_ids:
            query = query.filter(ListingItem.marketplace_ids.contains(marketplace_id))

    return query.offset(skip).limit(limit).all()


def create_listing_item(db: Session, seller_id: str, sku: str, listing: ListingItemCreate) -> ListingItem:
    """Create a new listing item"""
    db_listing = ListingItem(
        seller_id=seller_id,
        seller_name=listing.seller_name,
        sku=sku,
        title=listing.title,
        description=listing.description,
        price=listing.price,
        quantity=listing.quantity,
        status=listing.status,
    )

    # Set marketplace_ids
    if listing.marketplace_ids:
        db_listing.set_marketplace_ids(listing.marketplace_ids)

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def update_listing_item(db: Session, db_listing: ListingItem, listing: ListingItemUpdate) -> ListingItem:
    """Update an existing listing item"""
    update_data = listing.model_dump(exclude_unset=True)

    # Handle marketplace_ids separately
    if "marketplace_ids" in update_data:
        marketplace_ids = update_data.pop("marketplace_ids")
        db_listing.set_marketplace_ids(marketplace_ids)

    # Update other fields
    for field, value in update_data.items():
        setattr(db_listing, field, value)

    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing_item(db: Session, db_listing: ListingItem) -> bool:
    """Delete a listing item (soft delete by setting status to INACTIVE)"""
    db_listing.status = "INACTIVE"
    db.commit()
    return True


def hard_delete_listing_item(db: Session, db_listing: ListingItem) -> bool:
    """Hard delete a listing item from database"""
    db.delete(db_listing)
    db.commit()
    return True

"""
Listing service for Amazon SP-API Mock
Handles listing-related business logic and database operations
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from app.database.schemas import Listing, Seller

class ListingService:
    """Service for handling listing operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_or_update_listing(self, seller_id: str, sku: str, 
                                     product_type: str, attributes: Dict[str, Any],
                                     marketplace_ids: List[str] = None) -> Dict[str, Any]:
        """Create or update a listing."""
        
        # Check if listing exists
        existing = self.db.query(Listing).filter(
            Listing.seller_id == seller_id,
            Listing.seller_sku == sku
        ).first()
        
        if existing:
            # Update existing listing
            existing.product_type = product_type
            existing.attributes = attributes
            existing.last_updated_date = datetime.utcnow()
            listing = existing
        else:
            # Create new listing
            listing = Listing(
                seller_id=seller_id,
                seller_sku=sku,
                product_type=product_type,
                attributes=attributes,
                status="ACTIVE",
                created_date=datetime.utcnow(),
                last_updated_date=datetime.utcnow()
            )
            self.db.add(listing)
        
        self.db.commit()
        
        return {
            "seller_sku": sku,
            "status": listing.status,
            "submission_id": f"sub_{sku}_{int(datetime.utcnow().timestamp())}"
        }
    
    async def get_listing(self, seller_id: str, sku: str, 
                         marketplace_ids: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get listing details."""
        
        listing = self.db.query(Listing).filter(
            Listing.seller_id == seller_id,
            Listing.seller_sku == sku
        ).first()
        
        if not listing:
            return None
        
        return {
            "seller_sku": listing.seller_sku,
            "product_type": listing.product_type,
            "status": listing.status,
            "attributes": listing.attributes,
            "created_date": listing.created_date.isoformat() + "Z",
            "last_updated_date": listing.last_updated_date.isoformat() + "Z",
            "attribute_sets": [
                {
                    "marketplace_id": "ATVPDKIKX0DER",  # Mock marketplace
                    "attributes": listing.attributes
                }
            ],
            "issues": [],  # Mock empty issues
            "offers": [
                {
                    "marketplace_id": "ATVPDKIKX0DER",
                    "sub_condition": "new",
                    "seller_sku": listing.seller_sku
                }
            ]
        }
    
    async def delete_listing(self, seller_id: str, sku: str,
                           marketplace_ids: List[str] = None) -> Optional[Dict[str, Any]]:
        """Delete a listing."""
        
        listing = self.db.query(Listing).filter(
            Listing.seller_id == seller_id,
            Listing.seller_sku == sku
        ).first()
        
        if not listing:
            return None
        
        # Instead of deleting, mark as inactive
        listing.status = "INACTIVE"
        listing.last_updated_date = datetime.utcnow()
        self.db.commit()
        
        return {
            "seller_sku": sku,
            "submission_id": f"del_{sku}_{int(datetime.utcnow().timestamp())}"
        }
    
    async def get_listings_by_seller(self, seller_id: str, 
                                   filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all listings for a seller."""
        
        query = self.db.query(Listing).filter(Listing.seller_id == seller_id)
        
        # Apply filters
        if filters:
            if "status" in filters:
                query = query.filter(Listing.status == filters["status"])
            if "product_type" in filters:
                query = query.filter(Listing.product_type == filters["product_type"])
        
        listings = query.all()
        
        results = []
        for listing in listings:
            listing_data = await self.get_listing(seller_id, listing.seller_sku)
            if listing_data:
                results.append(listing_data)
        
        return results
    
    async def update_listing_status(self, seller_id: str, sku: str, 
                                  status: str) -> Optional[Dict[str, Any]]:
        """Update listing status."""
        
        listing = self.db.query(Listing).filter(
            Listing.seller_id == seller_id,
            Listing.seller_sku == sku
        ).first()
        
        if not listing:
            return None
        
        listing.status = status
        listing.last_updated_date = datetime.utcnow()
        self.db.commit()
        
        return {
            "seller_sku": sku,
            "status": status,
            "last_updated": listing.last_updated_date.isoformat() + "Z"
        }
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
    
    async def patch_listing(self, seller_id: str, sku: str, patches: List[Dict[str, Any]],
                          marketplace_ids: List[str] = None) -> Dict[str, Any]:
        """Apply patch operations to a listing."""
        
        listing = self.db.query(Listing).filter(
            Listing.seller_id == seller_id,
            Listing.seller_sku == sku
        ).first()
        
        if not listing:
            return None
        
        # Apply patches
        for patch in patches:
            op = patch.get("op")
            path = patch.get("path", "")
            value = patch.get("value")
            
            if op == "add" or op == "replace":
                if path.startswith("/attributes/"):
                    attr_name = path.replace("/attributes/", "")
                    if not listing.attributes:
                        listing.attributes = {}
                    listing.attributes[attr_name] = value
                elif path == "/product_type":
                    listing.product_type = value
                elif path == "/item_name":
                    listing.item_name = value
            elif op == "remove":
                if path.startswith("/attributes/"):
                    attr_name = path.replace("/attributes/", "")
                    if listing.attributes and attr_name in listing.attributes:
                        del listing.attributes[attr_name]
        
        listing.last_updated_date = datetime.utcnow()
        self.db.commit()
        
        return {
            "seller_sku": sku,
            "status": "ACCEPTED",
            "submission_id": f"patch_{sku}_{int(datetime.utcnow().timestamp())}"
        }
    
    async def search_listings(self, seller_id: str, marketplace_ids: List[str],
                            included_data: List[str] = None, identifiers: List[str] = None,
                            identifiers_type: str = None, page_size: int = 10,
                            page_token: str = None, sort_by: str = None,
                            sort_order: str = "ASC") -> Dict[str, Any]:
        """Search for listings."""
        
        query = self.db.query(Listing).filter(Listing.seller_id == seller_id)
        
        # Apply filters
        if identifiers:
            if identifiers_type == "SKU":
                query = query.filter(Listing.seller_sku.in_(identifiers))
            elif identifiers_type == "ASIN":
                query = query.filter(Listing.asin.in_(identifiers))
        
        # Apply sorting
        if sort_by == "lastUpdatedDate":
            if sort_order == "DESC":
                query = query.order_by(Listing.last_updated_date.desc())
            else:
                query = query.order_by(Listing.last_updated_date.asc())
        else:
            query = query.order_by(Listing.seller_sku)
        
        # Apply pagination
        offset = 0
        if page_token:
            try:
                offset = int(page_token) * page_size
            except:
                offset = 0
        
        total_count = query.count()
        listings = query.offset(offset).limit(page_size).all()
        
        # Convert to response format
        result_listings = []
        for listing in listings:
            listing_data = {
                "sku": listing.seller_sku,
                "summaries": [
                    {
                        "marketplaceId": "ATVPDKIKX0DER",
                        "asin": listing.asin or f"MOCK{listing.seller_sku}",
                        "productType": listing.product_type or "UNKNOWN",
                        "conditionType": "new_new",
                        "status": ["BUYABLE"] if listing.status == "ACTIVE" else ["INACTIVE"],
                        "itemName": listing.item_name or f"Item {listing.seller_sku}",
                        "createdDate": listing.created_date.isoformat() + "Z" if listing.created_date else "",
                        "lastUpdatedDate": listing.last_updated_date.isoformat() + "Z" if listing.last_updated_date else ""
                    }
                ],
                "attributes": listing.attributes or {},
                "offers": [
                    {
                        "marketplaceId": "ATVPDKIKX0DER",
                        "offerType": "B2C",
                        "price": {
                            "currencyCode": "USD",
                            "amount": "100.00"
                        }
                    }
                ],
                "fulfillmentAvailability": [
                    {
                        "fulfillmentChannelCode": "DEFAULT",
                        "quantity": 100
                    }
                ],
                "issues": []
            }
            result_listings.append(listing_data)
        
        next_token = str(offset // page_size + 1) if len(listings) == page_size else None
        
        return {
            "total_count": total_count,
            "listings": result_listings,
            "next_token": next_token
        }
    
    async def get_listing_restrictions(self, asin: str, condition_type: str,
                                     seller_id: str, marketplace_ids: List[str],
                                     reason_locale: str = None) -> List[Dict[str, Any]]:
        """Get listing restrictions for an ASIN."""
        
        # Mock restrictions data - in reality this would check against Amazon's restriction database
        restrictions = []
        
        # Example restriction for certain conditions
        if condition_type in ["used_acceptable", "used_good"]:
            restrictions.append({
                "marketplaceId": marketplace_ids[0],
                "conditionType": condition_type,
                "reasons": [
                    {
                        "message": "You cannot list the product in this condition.",
                        "links": [
                            {
                                "resource": f"https://sellercentral.amazon.com/hz/approvalrequest/restrictions/approve?asin={asin}",
                                "verb": "GET",
                                "title": "Request Approval via Seller Central.",
                                "type": "text/html"
                            }
                        ]
                    }
                ]
            })
        
        return restrictions
    
    async def search_product_types(self, marketplace_ids: List[str],
                                 keywords: List[str] = None,
                                 item_name: str = None) -> Dict[str, Any]:
        """Search for product types."""
        
        # Mock product types data
        product_types = [
            {
                "name": "LUGGAGE",
                "displayName": "Luggage",
                "marketplaceIds": marketplace_ids
            },
            {
                "name": "TELEVISION",
                "displayName": "Television",
                "marketplaceIds": marketplace_ids
            },
            {
                "name": "ELECTRONICS",
                "displayName": "Electronics",
                "marketplaceIds": marketplace_ids
            }
        ]
        
        # Filter by keywords
        if keywords:
            filtered_types = []
            for product_type in product_types:
                for keyword in keywords:
                    if keyword.lower() in product_type["displayName"].lower():
                        filtered_types.append(product_type)
                        break
            product_types = filtered_types
        
        # Filter by item name
        if item_name:
            if "luggage" in item_name.lower():
                product_types = [pt for pt in product_types if pt["name"] == "LUGGAGE"]
            elif "tv" in item_name.lower() or "television" in item_name.lower():
                product_types = [pt for pt in product_types if pt["name"] == "TELEVISION"]
        
        return {
            "productTypes": product_types,
            "productTypeVersion": "LATEST"
        }
    
    async def get_product_type_definition(self, product_type: str, marketplace_ids: List[str],
                                        seller_id: str = None, product_type_version: str = "LATEST",
                                        requirements: str = "LISTING", requirements_enforced: str = "ENFORCED",
                                        locale: str = "DEFAULT") -> Dict[str, Any]:
        """Get product type definition."""
        
        # Mock product type definition
        definition = {
            "metaSchema": {
                "resource": "https://meta-schema-url",
                "verb": "GET",
                "checksum": "c7af9479ca7261645cea9db56c5f720d"
            },
            "schema": {
                "resource": "https://schema-url",
                "verb": "GET",
                "checksum": "c7af9479ca7261645cea9db56c5f720d"
            },
            "requirements": requirements,
            "requirementsEnforced": requirements_enforced,
            "propertyGroups": {
                "product_identity": {
                    "title": "Product Identity",
                    "description": "Information to uniquely identify your product (e.g., UPC, EAN, GTIN, Product Type, Brand)",
                    "propertyNames": [
                        "item_name",
                        "brand",
                        "external_product_id",
                        "gtin_exemption_reason",
                        "merchant_suggested_asin",
                        "product_type",
                        "product_category",
                        "product_subcategory",
                        "item_type_keyword"
                    ]
                }
            },
            "locale": "en_US" if locale == "DEFAULT" else locale,
            "marketplaceIds": marketplace_ids,
            "productType": product_type,
            "displayName": product_type.title(),
            "productTypeVersion": {
                "version": "UHqSqmb4FNUk=",
                "latest": True,
                "releaseCandidate": False
            }
        }
        
        return definition
"""
Amazon SP-API Listings 2021-08-01 endpoints
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Path as FastAPIPath, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

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

# Additional Models for new endpoints
class PatchOperation(BaseModel):
    op: str = Field(..., description="The operation to perform")
    path: Optional[str] = Field(None, description="The path to the field to modify")
    value: Optional[Any] = Field(None, description="The value to set")

class PatchListingRequest(BaseModel):
    patches: List[PatchOperation] = Field(..., description="List of patch operations")

class ListingSummary(BaseModel):
    marketplaceId: str
    asin: str
    productType: str
    conditionType: str
    status: List[str]
    itemName: str
    createdDate: str
    lastUpdatedDate: str
    mainImage: Optional[Dict[str, Any]] = None

class ListingOffer(BaseModel):
    marketplaceId: str
    offerType: str
    price: Dict[str, Any]
    audience: Optional[Dict[str, Any]] = None

class FulfillmentAvailability(BaseModel):
    fulfillmentChannelCode: str
    quantity: int

class ListingIssue(BaseModel):
    code: str
    message: str
    severity: str
    attributeNames: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    enforcements: Optional[Dict[str, Any]] = None

class ListingItem(BaseModel):
    sku: str
    summaries: Optional[List[ListingSummary]] = None
    attributes: Optional[Dict[str, Any]] = None
    offers: Optional[List[ListingOffer]] = None
    fulfillmentAvailability: Optional[List[FulfillmentAvailability]] = None
    issues: Optional[List[ListingIssue]] = None

class SearchListingsResponse(BaseModel):
    numberOfResults: int
    pagination: Dict[str, Any]
    items: List[ListingItem]

class RestrictionReason(BaseModel):
    message: str
    links: Optional[List[Dict[str, Any]]] = None

class ListingRestriction(BaseModel):
    marketplaceId: str
    conditionType: str
    reasons: List[RestrictionReason]

class ListingsRestrictionsResponse(BaseModel):
    restrictions: List[ListingRestriction]

class ProductType(BaseModel):
    name: str
    displayName: str
    marketplaceIds: List[str]

class ProductTypesResponse(BaseModel):
    productTypes: List[ProductType]
    productTypeVersion: str

class PropertyGroup(BaseModel):
    title: str
    description: str
    propertyNames: List[str]

class SchemaLink(BaseModel):
    resource: str
    verb: str
    checksum: Optional[str] = None

class ProductTypeDefinition(BaseModel):
    metaSchema: SchemaLink
    schema: SchemaLink
    requirements: str
    requirementsEnforced: str
    propertyGroups: Dict[str, PropertyGroup]
    locale: str
    marketplaceIds: List[str]
    productType: str
    displayName: str
    productTypeVersion: Dict[str, Any]

@router.put("/items/{sellerId}/{sku}")
async def put_listings_item(
    request: Request,
    listing_data: ListingRequest,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = Query(None, description="Comma-separated list of marketplace IDs"),
    includedData: Optional[str] = Query(None, description="A list of data sets to include"),
    issueLocale: Optional[str] = Query(None, description="A locale for localization of issues")
):
    """Create or update a listing."""
    
    listing_service = ListingService(db)
    result = await listing_service.create_or_update_listing(
        seller_id=sellerId,
        sku=sku,
        product_type=listing_data.productType,
        attributes=listing_data.attributes,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else ["ATVPDKIKX0DER"]
    )
    
    return {
        "sku": sku,
        "status": "ACCEPTED",
        "submissionId": result.get("submission_id"),
        "issues": []
    }

@router.get("/items/{sellerId}/{sku}")
async def get_listings_item(
    request: Request,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = Query(None, description="Comma-separated list of marketplace IDs"),
    includedData: Optional[str] = Query(None, description="A list of data sets to include"),
    issueLocale: Optional[str] = Query(None, description="A locale for localization of issues")
):
    """Get listing details."""
    
    listing_service = ListingService(db)
    listing = await listing_service.get_listing_detailed(
        seller_id=sellerId,
        sku=sku,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else ["ATVPDKIKX0DER"],
        included_data=includedData.split(",") if includedData else ["summaries"]
    )
    
    if not listing:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Listing not found for SKU {sku}"
            ).body.decode()
        )
    
    return listing

@router.delete("/items/{sellerId}/{sku}")
async def delete_listings_item(
    request: Request,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = Query(None, description="Comma-separated list of marketplace IDs"),
    issueLocale: Optional[str] = Query(None, description="A locale for localization of issues")
):
    """Delete a listing."""
    
    listing_service = ListingService(db)
    result = await listing_service.delete_listing(
        seller_id=sellerId,
        sku=sku,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else ["ATVPDKIKX0DER"]
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
        "status": "ACCEPTED",
        "submissionId": result.get("submission_id"),
        "issues": []
    }

@router.patch("/items/{sellerId}/{sku}")
async def patch_listings_item(
    request: Request,
    patch_data: PatchListingRequest,
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    sku: str = FastAPIPath(..., description="SKU"),
    db: Session = Depends(get_db),
    marketplaceIds: str = Query(None, description="Comma-separated list of marketplace IDs"),
    includedData: Optional[str] = Query(None, description="A list of data sets to include"),
    issueLocale: Optional[str] = Query(None, description="A locale for localization of issues")
):
    """Partially update a listing."""
    
    listing_service = ListingService(db)
    result = await listing_service.patch_listing(
        seller_id=sellerId,
        sku=sku,
        patches=patch_data.patches,
        marketplace_ids=marketplaceIds.split(",") if marketplaceIds else ["ATVPDKIKX0DER"]
    )
    
    return {
        "sku": sku,
        "status": "ACCEPTED",
        "submissionId": result.get("submission_id"),
        "issues": []
    }

@router.get("/items/{sellerId}", response_model=SearchListingsResponse)
async def search_listings_items(
    sellerId: str = FastAPIPath(..., description="Seller identifier"),
    marketplaceIds: str = Query(..., description="Comma-separated list of marketplace IDs"),
    includedData: Optional[str] = Query(None, description="A list of data sets to include"),
    identifiers: Optional[str] = Query(None, description="A list of item identifiers"),
    identifiersType: Optional[str] = Query(None, description="Type of identifiers provided"),
    pageSize: int = Query(10, ge=1, le=50, description="Number of results per page"),
    pageToken: Optional[str] = Query(None, description="Token for getting next set of results"),
    sortBy: Optional[str] = Query(None, description="Field to sort by"),
    sortOrder: Optional[str] = Query("ASC", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Search for listings items."""
    
    listing_service = ListingService(db)
    result = await listing_service.search_listings(
        seller_id=sellerId,
        marketplace_ids=marketplaceIds.split(","),
        included_data=includedData.split(",") if includedData else None,
        identifiers=identifiers.split(",") if identifiers else None,
        identifiers_type=identifiersType,
        page_size=pageSize,
        page_token=pageToken,
        sort_by=sortBy,
        sort_order=sortOrder
    )
    
    # Convert to response format
    items = []
    for listing in result["listings"]:
        # Build summaries
        summaries = []
        if listing.get("summaries"):
            for summary in listing["summaries"]:
                summaries.append(ListingSummary(**summary))
        
        # Build offers
        offers = []
        if listing.get("offers"):
            for offer in listing["offers"]:
                offers.append(ListingOffer(**offer))
        
        # Build fulfillment availability
        fulfillment_availability = []
        if listing.get("fulfillmentAvailability"):
            for fulfillment in listing["fulfillmentAvailability"]:
                fulfillment_availability.append(FulfillmentAvailability(**fulfillment))
        
        # Build issues
        issues = []
        if listing.get("issues"):
            for issue in listing["issues"]:
                issues.append(ListingIssue(**issue))
        
        items.append(ListingItem(
            sku=listing["sku"],
            summaries=summaries,
            attributes=listing.get("attributes"),
            offers=offers,
            fulfillmentAvailability=fulfillment_availability,
            issues=issues
        ))
    
    next_token = result.get("next_token")
    pagination = {"nextToken": next_token} if next_token else {}
    
    return SearchListingsResponse(
        numberOfResults=result.get("total_count", len(items)),
        pagination=pagination,
        items=items
    )

@router.get("/restrictions", response_model=ListingsRestrictionsResponse)
async def get_listings_restrictions(
    asin: str = Query(..., description="The Amazon Standard Identification Number (ASIN)"),
    conditionType: str = Query(..., description="The condition used to filter restrictions"),
    sellerId: str = Query(..., description="A selling partner identifier"),
    marketplaceIds: str = Query(..., description="Comma-separated list of marketplace IDs"),
    reasonLocale: Optional[str] = Query(None, description="A locale for reason text localization"),
    db: Session = Depends(get_db)
):
    """Get restrictions for a listing."""
    
    listing_service = ListingService(db)
    restrictions = await listing_service.get_listing_restrictions(
        asin=asin,
        condition_type=conditionType,
        seller_id=sellerId,
        marketplace_ids=marketplaceIds.split(","),
        reason_locale=reasonLocale
    )
    
    # Convert to response format
    restriction_list = []
    for restriction in restrictions:
        reasons = []
        for reason in restriction.get("reasons", []):
            reasons.append(RestrictionReason(**reason))
        
        restriction_list.append(ListingRestriction(
            marketplaceId=restriction["marketplaceId"],
            conditionType=restriction["conditionType"],
            reasons=reasons
        ))
    
    return ListingsRestrictionsResponse(restrictions=restriction_list)

# Product Type Definitions endpoints
@router.get("/definitions/productTypes", response_model=ProductTypesResponse)
async def search_definitions_product_types(
    marketplaceIds: str = Query(..., description="Comma-separated list of marketplace IDs"),
    keywords: Optional[str] = Query(None, description="A list of keywords to search product types"),
    itemName: Optional[str] = Query(None, description="The title of the item to get suggested product types"),
    db: Session = Depends(get_db)
):
    """Search for and return a list of Amazon product types."""
    
    listing_service = ListingService(db)
    product_types = await listing_service.search_product_types(
        marketplace_ids=marketplaceIds.split(","),
        keywords=keywords.split(",") if keywords else None,
        item_name=itemName
    )
    
    # Convert to response format
    product_type_list = []
    for product_type in product_types["productTypes"]:
        product_type_list.append(ProductType(**product_type))
    
    return ProductTypesResponse(
        productTypes=product_type_list,
        productTypeVersion=product_types.get("productTypeVersion", "LATEST")
    )

@router.get("/definitions/productTypes/{productType}", response_model=ProductTypeDefinition)
async def get_definitions_product_type(
    productType: str = FastAPIPath(..., description="The Amazon product type name"),
    marketplaceIds: str = Query(..., description="Comma-separated list of marketplace IDs"),
    sellerId: Optional[str] = Query(None, description="A selling partner identifier"),
    productTypeVersion: str = Query("LATEST", description="The version of the Amazon product type"),
    requirements: str = Query("LISTING", description="The requirements set for the Amazon product type"),
    requirementsEnforced: str = Query("ENFORCED", description="Identifies if the required attributes are enforced"),
    locale: str = Query("DEFAULT", description="Locale for retrieving display labels"),
    db: Session = Depends(get_db)
):
    """Retrieve an Amazon product type definition."""
    
    listing_service = ListingService(db)
    definition = await listing_service.get_product_type_definition(
        product_type=productType,
        marketplace_ids=marketplaceIds.split(","),
        seller_id=sellerId,
        product_type_version=productTypeVersion,
        requirements=requirements,
        requirements_enforced=requirementsEnforced,
        locale=locale
    )
    
    if not definition:
        raise HTTPException(status_code=404, detail="Product type definition not found")
    
    # Convert property groups
    property_groups = {}
    for group_name, group_data in definition.get("propertyGroups", {}).items():
        property_groups[group_name] = PropertyGroup(**group_data)
    
    return ProductTypeDefinition(
        metaSchema=SchemaLink(**definition["metaSchema"]),
        schema=SchemaLink(**definition["schema"]),
        requirements=definition["requirements"],
        requirementsEnforced=definition["requirementsEnforced"],
        propertyGroups=property_groups,
        locale=definition["locale"],
        marketplaceIds=definition["marketplaceIds"],
        productType=definition["productType"],
        displayName=definition["displayName"],
        productTypeVersion=definition["productTypeVersion"]
    )
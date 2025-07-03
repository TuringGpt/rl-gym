"""
Amazon Catalog Items API v0
Based on: https://developer-docs.amazon.com/sp-api/docs/catalog-items-api-v0-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import CatalogItem, CatalogCategory
from sqlalchemy import text
import sys
import json
from pathlib import Path as FilePath

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/catalog/v0", tags=["Catalog Items v0"])

# Response Models
class ProductCategory(BaseModel):
    ProductCategoryId: str
    ProductCategoryName: str
    parent: Optional[Dict[str, Any]] = None

class ListCatalogCategoriesResponse(BaseModel):
    payload: List[ProductCategory]
    errors: Optional[List[Dict[str, Any]]] = None

class CatalogItemSummary(BaseModel):
    marketplaceId: str
    asin: str
    productType: str
    conditionType: str
    status: List[str]
    itemName: str
    createdDate: str
    lastUpdatedDate: str
    mainImage: Optional[Dict[str, Any]] = None

class CatalogItemIdentifier(BaseModel):
    marketplaceId: str
    identifiers: List[Dict[str, str]]

class CatalogItemImage(BaseModel):
    marketplaceId: str
    images: List[Dict[str, Any]]

class CatalogItemProductType(BaseModel):
    marketplaceId: str
    productType: str

class CatalogItemSalesRank(BaseModel):
    marketplaceId: str
    ranks: List[Dict[str, Any]]

class CatalogItemVendorDetail(BaseModel):
    marketplaceId: str
    brandCode: Optional[str] = None
    categoryCode: Optional[str] = None
    manufacturerCode: Optional[str] = None
    manufacturerCodeParent: Optional[str] = None
    productGroup: Optional[str] = None
    replenishmentCategory: Optional[str] = None
    subcategoryCode: Optional[str] = None

class CatalogItemV0(BaseModel):
    asin: str
    identifiers: Optional[List[CatalogItemIdentifier]] = None
    images: Optional[List[CatalogItemImage]] = None
    productTypes: Optional[List[CatalogItemProductType]] = None
    salesRanks: Optional[List[CatalogItemSalesRank]] = None
    summaries: Optional[List[CatalogItemSummary]] = None
    variations: Optional[List[Dict[str, Any]]] = None
    vendorDetails: Optional[List[CatalogItemVendorDetail]] = None

class SearchCatalogItemsV0Response(BaseModel):
    numberOfResults: int
    pagination: Dict[str, Any]
    refinements: Dict[str, Any]
    items: List[CatalogItemV0]

@router.get("/categories", response_model=ListCatalogCategoriesResponse)
def list_catalog_categories(
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    db: Session = Depends(get_db)
):
    """
    Returns the parent categories to which an item can be assigned within the specified marketplace.
    """
    
    try:
        # Query categories from database
        categories = db.execute(
            text("""
            SELECT DISTINCT product_category_id, product_category_name, parent_category_id
            FROM catalog_categories
            WHERE marketplace_id = :marketplace_id
            ORDER BY product_category_name
            """),
            {"marketplace_id": marketplace_id}
        )
        categories = categories.fetchall()
        
        payload = []
        for category in categories:
            parent_info = {}
            if category.parent_category_id:
                parent_categories = db.execute(
                    text("""
                    SELECT product_category_id, product_category_name
                    FROM catalog_categories
                    WHERE product_category_id = :parent_id AND marketplace_id = :marketplace_id
                    """),
                    {"parent_id": category.parent_category_id, "marketplace_id": marketplace_id}
                )
                parent = parent_categories.fetchone()
                if parent:
                    parent_info = {
                        "ProductCategoryId": parent.product_category_id,
                        "ProductCategoryName": parent.product_category_name
                    }
            
            payload.append(ProductCategory(
                ProductCategoryId=category.product_category_id,
                ProductCategoryName=category.product_category_name,
                parent=parent_info if parent_info else None
            ))
        
        return ListCatalogCategoriesResponse(payload=payload)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items", response_model=SearchCatalogItemsV0Response)
def search_catalog_items_v0(
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    query: Optional[str] = Query(None, description="Keyword(s) to use to search for items in the catalog"),
    queryContextId: Optional[str] = Query(None, description="An identifier for the context within which the given search will be performed"),
    sellerId: Optional[str] = Query(None, description="A selling partner identifier"),
    includeData: Optional[List[str]] = Query(None, description="A list of data sets to include in the response"),
    pageSize: int = Query(10, ge=1, le=50, description="Number of results to return per page"),
    nextToken: Optional[str] = Query(None, description="A token to get the next set of results"),
    db: Session = Depends(get_db)
):
    """
    Searches for and returns a list of Amazon catalog items and associated information for a given marketplace.
    """
    
    try:
        # Build query
        base_query = """
            SELECT ci.*, cc.product_category_name
            FROM catalog_items ci
            LEFT JOIN catalog_categories cc ON ci.product_category_id = cc.product_category_id
            WHERE ci.marketplace_id = :marketplace_id
        """
        params = {"marketplace_id": marketplace_id}
        
        # Apply search filter
        if query:
            base_query += " AND (ci.item_name ILIKE :query OR ci.brand ILIKE :query)"
            params["query"] = f"%{query}%"
        
        # Apply seller filter
        if sellerId:
            base_query += " AND ci.seller_id = :seller_id"
            params["seller_id"] = sellerId
        
        # Count total results (simplified to avoid JSON column issues)
        count_query = """
            SELECT COUNT(ci.asin)
            FROM catalog_items ci
            LEFT JOIN catalog_categories cc ON ci.product_category_id = cc.product_category_id
            WHERE ci.marketplace_id = :marketplace_id
        """
        count_params = {"marketplace_id": marketplace_id}
        
        # Apply same filters as main query
        if query:
            count_query += " AND (ci.item_name ILIKE :query OR ci.brand ILIKE :query)"
            count_params["query"] = f"%{query}%"
        
        if sellerId:
            count_query += " AND ci.seller_id = :seller_id"
            count_params["seller_id"] = sellerId
        
        total_result = db.execute(text(count_query), count_params)
        total_count = total_result.fetchone()[0]
        
        # Apply pagination
        offset = 0
        if nextToken:
            try:
                offset = int(nextToken) * pageSize
            except:
                offset = 0
        
        base_query += f" ORDER BY ci.item_name LIMIT :limit OFFSET :offset"
        params.update({"limit": pageSize, "offset": offset})
        
        # Execute query
        result = db.execute(text(base_query), params)
        catalog_items = result.fetchall()
        
        # Convert to response format
        items = []
        for item in catalog_items:
            # Build summaries
            # Extract product type from JSON
            product_type = "UNKNOWN"
            if hasattr(item, 'product_types') and item.product_types:
                if isinstance(item.product_types, list) and len(item.product_types) > 0:
                    product_type = item.product_types[0].get('productType', 'UNKNOWN') if isinstance(item.product_types[0], dict) else str(item.product_types[0])
                elif isinstance(item.product_types, dict):
                    product_type = item.product_types.get('productType', 'UNKNOWN')
                    
            # Extract main image properly with JSON parsing
            main_image = None
            if hasattr(item, 'images') and item.images:
                # Parse JSON if it's a string
                images_data = item.images
                if isinstance(images_data, str):
                    try:
                        images_data = json.loads(images_data)
                    except json.JSONDecodeError:
                        images_data = []
                
                if isinstance(images_data, list) and len(images_data) > 0:
                    main_image = images_data[0] if isinstance(images_data[0], dict) else None
                elif isinstance(images_data, dict):
                    main_image = images_data
                    
            summaries = [CatalogItemSummary(
                marketplaceId=item.marketplace_id,
                asin=item.asin,
                productType=product_type,
                conditionType="new_new",
                status=["BUYABLE"],
                itemName=item.item_name or "",
                createdDate=item.created_at.isoformat() if hasattr(item, 'created_at') and item.created_at else "",
                lastUpdatedDate=item.updated_at.isoformat() if hasattr(item, 'updated_at') and item.updated_at else "",
                mainImage=main_image
            )]
            
            # Build identifiers with JSON parsing
            identifiers = []
            if item.identifiers:
                # Parse JSON if it's a string
                identifiers_data = item.identifiers
                if isinstance(identifiers_data, str):
                    try:
                        identifiers_data = json.loads(identifiers_data)
                    except json.JSONDecodeError:
                        identifiers_data = {}
                
                if isinstance(identifiers_data, dict):
                    identifier_list = []
                    for k, v in identifiers_data.items():
                        # Handle case where v might be a list
                        if isinstance(v, list):
                            for val in v:
                                identifier_list.append({"type": k, "identifier": str(val)})
                        else:
                            identifier_list.append({"type": k, "identifier": str(v)})
                    
                    identifiers.append(CatalogItemIdentifier(
                        marketplaceId=item.marketplace_id,
                        identifiers=identifier_list
                    ))
            
            # Build images with JSON parsing
            images = []
            if item.images:
                # Parse JSON if it's a string
                images_data = item.images
                if isinstance(images_data, str):
                    try:
                        images_data = json.loads(images_data)
                    except json.JSONDecodeError:
                        images_data = []
                
                if images_data:
                    images.append(CatalogItemImage(
                        marketplaceId=item.marketplace_id,
                        images=images_data
                    ))
            
            # Build product types
            product_types = []
            if hasattr(item, 'product_types') and item.product_types:
                if isinstance(item.product_types, list):
                    for pt in item.product_types:
                        if isinstance(pt, dict):
                            product_types.append(CatalogItemProductType(
                                marketplaceId=item.marketplace_id,
                                productType=pt.get('productType', 'UNKNOWN')
                            ))
                        else:
                            product_types.append(CatalogItemProductType(
                                marketplaceId=item.marketplace_id,
                                productType=str(pt)
                            ))
                elif isinstance(item.product_types, dict):
                    product_types.append(CatalogItemProductType(
                        marketplaceId=item.marketplace_id,
                        productType=item.product_types.get('productType', 'UNKNOWN')
                    ))
            
            # Build sales ranks with JSON parsing
            sales_ranks = []
            if item.sales_rankings:
                # Parse JSON if it's a string
                sales_data = item.sales_rankings
                if isinstance(sales_data, str):
                    try:
                        sales_data = json.loads(sales_data)
                    except json.JSONDecodeError:
                        sales_data = []
                
                if sales_data:
                    sales_ranks.append(CatalogItemSalesRank(
                        marketplaceId=item.marketplace_id,
                        ranks=sales_data
                    ))
            
            # Build vendor details with JSON parsing
            vendor_details = []
            if hasattr(item, 'vendor_details') and item.vendor_details:
                # Parse JSON if it's a string
                vendor_data = item.vendor_details
                if isinstance(vendor_data, str):
                    try:
                        vendor_data = json.loads(vendor_data)
                    except json.JSONDecodeError:
                        vendor_data = {}
                
                if vendor_data and isinstance(vendor_data, dict):
                    vendor_details.append(CatalogItemVendorDetail(
                        marketplaceId=item.marketplace_id,
                        **vendor_data
                    ))
            
            items.append(CatalogItemV0(
                asin=item.asin,
                identifiers=identifiers,
                images=images,
                productTypes=product_types,
                salesRanks=sales_ranks,
                summaries=summaries,
                vendorDetails=vendor_details
            ))
        
        # Build pagination
        next_token = str(offset // pageSize + 1) if len(items) == pageSize else None
        pagination = {"nextToken": next_token} if next_token else {}
        
        # Build refinements (simplified)
        refinements = {
            "brands": [],
            "categories": []
        }
        
        return SearchCatalogItemsV0Response(
            numberOfResults=total_count,
            pagination=pagination,
            refinements=refinements,
            items=items
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{asin}", response_model=CatalogItemV0)
def get_catalog_item_v0(
    asin: str,
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    includeData: Optional[List[str]] = Query(None, description="A list of data sets to include in the response"),
    db: Session = Depends(get_db)
):
    """
    Returns details about the item indicated by the specified ASIN.
    """
    
    try:
        # Query the item
        query = """
            SELECT ci.*, cc.product_category_name
            FROM catalog_items ci
            LEFT JOIN catalog_categories cc ON ci.product_category_id = cc.product_category_id
            WHERE ci.asin = :asin AND ci.marketplace_id = :marketplace_id
        """
        result = db.execute(text(query), {"asin": asin, "marketplace_id": marketplace_id})
        item = result.fetchone()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Extract product type from JSON
        product_type = "UNKNOWN"
        if hasattr(item, 'product_types') and item.product_types:
            if isinstance(item.product_types, list) and len(item.product_types) > 0:
                product_type = item.product_types[0].get('productType', 'UNKNOWN') if isinstance(item.product_types[0], dict) else str(item.product_types[0])
            elif isinstance(item.product_types, dict):
                product_type = item.product_types.get('productType', 'UNKNOWN')
                
        # Extract main image properly with JSON parsing
        main_image = None
        if hasattr(item, 'images') and item.images:
            # Parse JSON if it's a string
            images_data = item.images
            if isinstance(images_data, str):
                try:
                    images_data = json.loads(images_data)
                except json.JSONDecodeError:
                    images_data = []
            
            if isinstance(images_data, list) and len(images_data) > 0:
                main_image = images_data[0] if isinstance(images_data[0], dict) else None
            elif isinstance(images_data, dict):
                main_image = images_data
                
        # Build summaries
        summaries = [CatalogItemSummary(
            marketplaceId=item.marketplace_id,
            asin=item.asin,
            productType=product_type,
            conditionType="new_new",
            status=["BUYABLE"],
            itemName=item.item_name or "",
            createdDate=item.created_at.isoformat() if hasattr(item, 'created_at') and item.created_at else "",
            lastUpdatedDate=item.updated_at.isoformat() if hasattr(item, 'updated_at') and item.updated_at else "",
            mainImage=main_image
        )]
        
        # Build identifiers with JSON parsing
        identifiers = []
        if item.identifiers:
            # Parse JSON if it's a string
            identifiers_data = item.identifiers
            if isinstance(identifiers_data, str):
                try:
                    identifiers_data = json.loads(identifiers_data)
                except json.JSONDecodeError:
                    identifiers_data = {}
            
            if isinstance(identifiers_data, dict):
                identifier_list = []
                for k, v in identifiers_data.items():
                    # Handle case where v might be a list
                    if isinstance(v, list):
                        for val in v:
                            identifier_list.append({"type": k, "identifier": str(val)})
                    else:
                        identifier_list.append({"type": k, "identifier": str(v)})
                
                identifiers.append(CatalogItemIdentifier(
                    marketplaceId=item.marketplace_id,
                    identifiers=identifier_list
                ))
        
        # Build images with JSON parsing
        images = []
        if item.images:
            # Parse JSON if it's a string
            images_data = item.images
            if isinstance(images_data, str):
                try:
                    images_data = json.loads(images_data)
                except json.JSONDecodeError:
                    images_data = []
            
            if images_data:
                images.append(CatalogItemImage(
                    marketplaceId=item.marketplace_id,
                    images=images_data
                ))
        
        # Build product types
        product_types = []
        if hasattr(item, 'product_types') and item.product_types:
            if isinstance(item.product_types, list):
                for pt in item.product_types:
                    if isinstance(pt, dict):
                        product_types.append(CatalogItemProductType(
                            marketplaceId=item.marketplace_id,
                            productType=pt.get('productType', 'UNKNOWN')
                        ))
                    else:
                        product_types.append(CatalogItemProductType(
                            marketplaceId=item.marketplace_id,
                            productType=str(pt)
                        ))
            elif isinstance(item.product_types, dict):
                product_types.append(CatalogItemProductType(
                    marketplaceId=item.marketplace_id,
                    productType=item.product_types.get('productType', 'UNKNOWN')
                ))
        
        # Build sales ranks with JSON parsing
        sales_ranks = []
        if item.sales_rankings:
            # Parse JSON if it's a string
            sales_data = item.sales_rankings
            if isinstance(sales_data, str):
                try:
                    sales_data = json.loads(sales_data)
                except json.JSONDecodeError:
                    sales_data = []
            
            if sales_data:
                sales_ranks.append(CatalogItemSalesRank(
                    marketplaceId=item.marketplace_id,
                    ranks=sales_data
                ))
        
        # Build vendor details with JSON parsing
        vendor_details = []
        if hasattr(item, 'vendor_details') and item.vendor_details:
            # Parse JSON if it's a string
            vendor_data = item.vendor_details
            if isinstance(vendor_data, str):
                try:
                    vendor_data = json.loads(vendor_data)
                except json.JSONDecodeError:
                    vendor_data = {}
            
            if vendor_data and isinstance(vendor_data, dict):
                vendor_details.append(CatalogItemVendorDetail(
                    marketplaceId=item.marketplace_id,
                    **vendor_data
                ))
        
        return CatalogItemV0(
            asin=item.asin,
            identifiers=identifiers,
            images=images,
            productTypes=product_types,
            salesRanks=sales_ranks,
            summaries=summaries,
            vendorDetails=vendor_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
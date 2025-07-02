"""
Amazon Catalog Items API v2022-04-01
Based on: https://developer-docs.amazon.com/sp-api/docs/catalog-items-api-v2022-04-01-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import CatalogItem
import sys
from pathlib import Path as FilePath

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/catalog/2022-04-01", tags=["Catalog Items"])

# Response Models
class ItemIdentifier(BaseModel):
    identifier_type: str
    identifier: str

class ItemImage(BaseModel):
    variant: str
    link: str
    height: Optional[int] = None
    width: Optional[int] = None

class ItemDimensions(BaseModel):
    height: Optional[Dict[str, Any]] = None
    length: Optional[Dict[str, Any]] = None
    width: Optional[Dict[str, Any]] = None
    weight: Optional[Dict[str, Any]] = None

class ItemSalesRank(BaseModel):
    product_category_id: str
    rank: int
    display_group_ranks: Optional[List[Dict[str, Any]]] = None

class BrowseNodeInfo(BaseModel):
    browse_nodes: List[Dict[str, Any]]
    website_display_group: Optional[str] = None
    website_display_group_name: Optional[str] = None

class ItemSummaryByMarketplace(BaseModel):
    marketplace_id: str
    asin: str
    product_types: Optional[List[Dict[str, Any]]] = None
    sales_rankings: Optional[List[ItemSalesRank]] = None
    browse_node_info: Optional[BrowseNodeInfo] = None

class ItemAttributes(BaseModel):
    """Dynamic attributes based on product type"""
    pass

class Item(BaseModel):
    asin: str
    attributes: Optional[ItemAttributes] = None
    identifiers: Optional[List[ItemIdentifier]] = None
    images: Optional[List[ItemImage]] = None
    product_types: Optional[List[Dict[str, Any]]] = None
    sales_rankings: Optional[List[ItemSalesRank]] = None
    summaries: Optional[List[ItemSummaryByMarketplace]] = None
    browse_node_info: Optional[BrowseNodeInfo] = None
    dimensions: Optional[ItemDimensions] = None

class ItemSearchResults(BaseModel):
    number_of_results: int
    pagination: Dict[str, Any]
    refinements: Dict[str, Any]
    items: List[Item]

class SearchCatalogItemsResponse(BaseModel):
    items: List[Item]
    refinements: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None

class GetCatalogItemResponse(BaseModel):
    asin: str
    attributes: Optional[Dict[str, Any]] = None
    identifiers: Optional[List[ItemIdentifier]] = None
    images: Optional[List[ItemImage]] = None
    product_types: Optional[List[Dict[str, Any]]] = None
    sales_rankings: Optional[List[ItemSalesRank]] = None
    summaries: Optional[List[ItemSummaryByMarketplace]] = None
    browse_node_info: Optional[BrowseNodeInfo] = None
    dimensions: Optional[ItemDimensions] = None
    errors: Optional[List[Dict[str, Any]]] = None

@router.get("/items", response_model=SearchCatalogItemsResponse)
async def search_catalog_items(
    marketplace_ids: List[str] = Query(..., description="A list of marketplace identifiers"),
    identifiers: Optional[List[str]] = Query(None, description="A list of item identifiers used to identify items in the given marketplace"),
    identifiers_type: Optional[str] = Query(None, description="Type of identifiers provided"),
    included_data: Optional[List[str]] = Query(None, description="A list of data sets to include in the response"),
    locale: Optional[str] = Query(None, description="Locale for retrieving localized summaries"),
    seller_id: Optional[str] = Query(None, description="A selling partner identifier"),
    keywords: Optional[List[str]] = Query(None, description="A list of words to search the Amazon catalog for items"),
    brand_names: Optional[List[str]] = Query(None, description="A list of brand names to limit the search"),
    classification_ids: Optional[List[str]] = Query(None, description="A list of classification identifiers"),
    page_size: int = Query(10, description="Number of results to return per page"),
    page_token: Optional[str] = Query(None, description="A token to get the next set of results"),
    db: Session = Depends(get_db)
):
    """
    Search for and return a list of Amazon catalog items and associated information either by identifier or by keywords.
    """
    
    try:
        query = db.query(CatalogItem)
        
        # Filter by marketplace
        if marketplace_ids:
            query = query.filter(CatalogItem.marketplace_id.in_(marketplace_ids))
        
        # Filter by identifiers (ASINs)
        if identifiers:
            query = query.filter(CatalogItem.asin.in_(identifiers))
        
        # Filter by brand names
        if brand_names:
            query = query.filter(CatalogItem.brand.in_(brand_names))
        
        # Keyword search (simplified)
        if keywords:
            keyword_filter = None
            for keyword in keywords:
                condition = CatalogItem.item_name.ilike(f"%{keyword}%")
                if keyword_filter is None:
                    keyword_filter = condition
                else:
                    keyword_filter = keyword_filter | condition
            if keyword_filter is not None:
                query = query.filter(keyword_filter)
        
        # Apply pagination
        offset = 0
        if page_token:
            try:
                offset = int(page_token) * page_size
            except:
                offset = 0
        
        catalog_items = query.offset(offset).limit(page_size).all()
        
        items = []
        for catalog_item in catalog_items:
            # Convert database model to API response
            identifiers = []
            if catalog_item.identifiers:
                for id_type, id_value in catalog_item.identifiers.items():
                    identifiers.append(ItemIdentifier(
                        identifier_type=id_type,
                        identifier=id_value
                    ))
            
            images = []
            if catalog_item.images:
                for img in catalog_item.images:
                    images.append(ItemImage(
                        variant=img.get('variant', 'MAIN'),
                        link=img.get('link', ''),
                        height=img.get('height'),
                        width=img.get('width')
                    ))
            
            sales_rankings = []
            if catalog_item.sales_rankings:
                for rank in catalog_item.sales_rankings:
                    sales_rankings.append(ItemSalesRank(
                        product_category_id=rank.get('category_id', ''),
                        rank=rank.get('rank', 0)
                    ))
            
            summaries = [ItemSummaryByMarketplace(
                marketplace_id=catalog_item.marketplace_id,
                asin=catalog_item.asin,
                product_types=catalog_item.product_types,
                sales_rankings=sales_rankings,
                browse_node_info=BrowseNodeInfo(
                    browse_nodes=catalog_item.browse_node_info.get('browse_nodes', []) if catalog_item.browse_node_info else []
                ) if catalog_item.browse_node_info else None
            )]
            
            item = Item(
                asin=catalog_item.asin,
                identifiers=identifiers,
                images=images,
                product_types=catalog_item.product_types,
                sales_rankings=sales_rankings,
                summaries=summaries,
                browse_node_info=BrowseNodeInfo(
                    browse_nodes=catalog_item.browse_node_info.get('browse_nodes', []) if catalog_item.browse_node_info else []
                ) if catalog_item.browse_node_info else None,
                dimensions=ItemDimensions(
                    **catalog_item.dimensions
                ) if catalog_item.dimensions else None
            )
            items.append(item)
        
        next_token = str(offset // page_size + 1) if len(items) == page_size else None
        
        return SearchCatalogItemsResponse(
            items=items,
            pagination={"next_token": next_token} if next_token else {},
            refinements={}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{asin}", response_model=GetCatalogItemResponse)
async def get_catalog_item(
    asin: str = Path(..., description="The Amazon Standard Identification Number (ASIN) of the item"),
    marketplace_ids: List[str] = Query(..., description="A list of marketplace identifiers"),
    included_data: Optional[List[str]] = Query(None, description="A list of data sets to include in the response"),
    locale: Optional[str] = Query(None, description="Locale for retrieving localized summaries"),
    db: Session = Depends(get_db)
):
    """
    Retrieves details for an item in the Amazon catalog.
    """
    
    try:
        catalog_item = db.query(CatalogItem).filter(
            CatalogItem.asin == asin,
            CatalogItem.marketplace_id.in_(marketplace_ids)
        ).first()
        
        if not catalog_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Convert database model to API response
        identifiers = []
        if catalog_item.identifiers:
            for id_type, id_value in catalog_item.identifiers.items():
                identifiers.append(ItemIdentifier(
                    identifier_type=id_type,
                    identifier=id_value
                ))
        
        images = []
        if catalog_item.images:
            for img in catalog_item.images:
                images.append(ItemImage(
                    variant=img.get('variant', 'MAIN'),
                    link=img.get('link', ''),
                    height=img.get('height'),
                    width=img.get('width')
                ))
        
        sales_rankings = []
        if catalog_item.sales_rankings:
            for rank in catalog_item.sales_rankings:
                sales_rankings.append(ItemSalesRank(
                    product_category_id=rank.get('category_id', ''),
                    rank=rank.get('rank', 0)
                ))
        
        summaries = [ItemSummaryByMarketplace(
            marketplace_id=catalog_item.marketplace_id,
            asin=catalog_item.asin,
            product_types=catalog_item.product_types,
            sales_rankings=sales_rankings
        )]
        
        return GetCatalogItemResponse(
            asin=catalog_item.asin,
            attributes={"title": catalog_item.item_name, "brand": catalog_item.brand} if catalog_item.item_name else None,
            identifiers=identifiers,
            images=images,
            product_types=catalog_item.product_types,
            sales_rankings=sales_rankings,
            summaries=summaries,
            browse_node_info=BrowseNodeInfo(
                browse_nodes=catalog_item.browse_node_info.get('browse_nodes', []) if catalog_item.browse_node_info else []
            ) if catalog_item.browse_node_info else None,
            dimensions=ItemDimensions(
                **catalog_item.dimensions
            ) if catalog_item.dimensions else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
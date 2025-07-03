"""
Amazon Catalog Items API v2020-12-01
Based on: https://developer-docs.amazon.com/sp-api/docs/catalog-items-api-v2020-12-01-reference
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

router = APIRouter(prefix="/catalog/2020-12-01", tags=["Catalog Items 2020-12-01"])

# Response Models
class ItemIdentifier(BaseModel):
    type: str
    identifier: str

class ItemIdentifiersByMarketplace(BaseModel):
    marketplaceId: str
    identifiers: List[ItemIdentifier]

class ItemImage(BaseModel):
    variant: str
    link: str
    height: Optional[int] = None
    width: Optional[int] = None

class ItemImagesByMarketplace(BaseModel):
    marketplaceId: str
    images: List[ItemImage]

class ItemProductType(BaseModel):
    marketplaceId: str
    productType: str

class ItemSalesRank(BaseModel):
    title: str
    link: str
    rank: int

class ItemSalesRanksByMarketplace(BaseModel):
    marketplaceId: str
    ranks: List[ItemSalesRank]

class ItemSummary(BaseModel):
    marketplaceId: str
    brandName: Optional[str] = None
    browseNode: Optional[str] = None
    colorName: Optional[str] = None
    itemName: Optional[str] = None
    manufacturer: Optional[str] = None
    modelNumber: Optional[str] = None
    sizeName: Optional[str] = None
    styleName: Optional[str] = None

class ItemVariation(BaseModel):
    marketplaceId: str
    asins: List[str]
    type: str

class ItemVendorDetail(BaseModel):
    marketplaceId: str
    brandCode: Optional[str] = None
    categoryCode: Optional[str] = None
    manufacturerCode: Optional[str] = None
    manufacturerCodeParent: Optional[str] = None
    productGroup: Optional[str] = None
    replenishmentCategory: Optional[str] = None
    subcategoryCode: Optional[str] = None

class BrandRefinement(BaseModel):
    numberOfResults: int
    brandName: str

class CategoryRefinement(BaseModel):
    numberOfResults: int
    displayName: str
    classificationId: str

class SearchRefinements(BaseModel):
    brands: List[BrandRefinement]
    categories: List[CategoryRefinement]

class PaginationToken(BaseModel):
    nextToken: Optional[str] = None
    previousToken: Optional[str] = None

class Item(BaseModel):
    asin: str
    identifiers: Optional[List[ItemIdentifiersByMarketplace]] = None
    images: Optional[List[ItemImagesByMarketplace]] = None
    productTypes: Optional[List[ItemProductType]] = None
    salesRanks: Optional[List[ItemSalesRanksByMarketplace]] = None
    summaries: Optional[List[ItemSummary]] = None
    variations: Optional[List[ItemVariation]] = None
    vendorDetails: Optional[List[ItemVendorDetail]] = None

class SearchCatalogItemsResponse(BaseModel):
    numberOfResults: int
    pagination: PaginationToken
    refinements: SearchRefinements
    items: List[Item]

class GetCatalogItemResponse(BaseModel):
    asin: str
    identifiers: Optional[List[ItemIdentifiersByMarketplace]] = None
    images: Optional[List[ItemImagesByMarketplace]] = None
    productTypes: Optional[List[ItemProductType]] = None
    salesRanks: Optional[List[ItemSalesRanksByMarketplace]] = None
    summaries: Optional[List[ItemSummary]] = None
    variations: Optional[List[ItemVariation]] = None
    vendorDetails: Optional[List[ItemVendorDetail]] = None

@router.get("/items", response_model=SearchCatalogItemsResponse)
async def search_catalog_items_2020_12_01(
    marketplaceIds: List[str] = Query(..., description="A list of marketplace identifiers"),
    identifiers: Optional[List[str]] = Query(None, description="A list of item identifiers"),
    identifiersType: Optional[str] = Query(None, description="Type of identifiers provided"),
    includedData: Optional[List[str]] = Query(None, description="A list of data sets to include"),
    locale: Optional[str] = Query(None, description="Locale for retrieving localized summaries"),
    sellerId: Optional[str] = Query(None, description="A selling partner identifier"),
    keywords: Optional[List[str]] = Query(None, description="A list of words to search"),
    brandNames: Optional[List[str]] = Query(None, description="A list of brand names"),
    classificationIds: Optional[List[str]] = Query(None, description="A list of classification identifiers"),
    pageSize: int = Query(10, ge=1, le=50, description="Number of results per page"),
    pageToken: Optional[str] = Query(None, description="Token for getting next set of results"),
    db: Session = Depends(get_db)
):
    """
    Search for and return a list of Amazon catalog items and associated information for the given marketplace.
    """
    
    try:
        query = db.query(CatalogItem)
        
        # Filter by marketplace
        if marketplaceIds:
            query = query.filter(CatalogItem.marketplace_id.in_(marketplaceIds))
        
        # Filter by identifiers (ASINs)
        if identifiers:
            query = query.filter(CatalogItem.asin.in_(identifiers))
        
        # Filter by brand names
        if brandNames:
            query = query.filter(CatalogItem.brand.in_(brandNames))
        
        # Filter by seller
        if sellerId:
            query = query.filter(CatalogItem.seller_id == sellerId)
        
        # Keyword search
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
        
        # Count total results
        total_count = query.count()
        
        # Apply pagination
        offset = 0
        if pageToken:
            try:
                offset = int(pageToken) * pageSize
            except:
                offset = 0
        
        catalog_items = query.offset(offset).limit(pageSize).all()
        
        # Convert to response format
        items = []
        for catalog_item in catalog_items:
            # Build identifiers
            identifiers = []
            if catalog_item.identifiers:
                identifier_list = []
                for id_type, id_value in catalog_item.identifiers.items():
                    identifier_list.append(ItemIdentifier(
                        type=id_type,
                        identifier=id_value
                    ))
                identifiers.append(ItemIdentifiersByMarketplace(
                    marketplaceId=catalog_item.marketplace_id,
                    identifiers=identifier_list
                ))
            
            # Build images
            images = []
            if catalog_item.images:
                image_list = []
                for img in catalog_item.images:
                    image_list.append(ItemImage(
                        variant=img.get('variant', 'MAIN'),
                        link=img.get('link', ''),
                        height=img.get('height'),
                        width=img.get('width')
                    ))
                images.append(ItemImagesByMarketplace(
                    marketplaceId=catalog_item.marketplace_id,
                    images=image_list
                ))
            
            # Build product types
            product_types = []
            if catalog_item.product_type:
                product_types.append(ItemProductType(
                    marketplaceId=catalog_item.marketplace_id,
                    productType=catalog_item.product_type
                ))
            
            # Build sales ranks
            sales_ranks = []
            if catalog_item.sales_rankings:
                rank_list = []
                for rank in catalog_item.sales_rankings:
                    rank_list.append(ItemSalesRank(
                        title=rank.get('title', ''),
                        link=rank.get('link', ''),
                        rank=rank.get('rank', 0)
                    ))
                sales_ranks.append(ItemSalesRanksByMarketplace(
                    marketplaceId=catalog_item.marketplace_id,
                    ranks=rank_list
                ))
            
            # Build summaries
            summaries = []
            summaries.append(ItemSummary(
                marketplaceId=catalog_item.marketplace_id,
                brandName=catalog_item.brand,
                browseNode=catalog_item.browse_node_info.get('browse_node') if catalog_item.browse_node_info else None,
                itemName=catalog_item.item_name,
                manufacturer=catalog_item.manufacturer,
                modelNumber=catalog_item.model_number,
                sizeName=catalog_item.size_name,
                styleName=catalog_item.style_name
            ))
            
            # Build vendor details
            vendor_details = []
            if hasattr(catalog_item, 'vendor_details') and catalog_item.vendor_details:
                vendor_details.append(ItemVendorDetail(
                    marketplaceId=catalog_item.marketplace_id,
                    **catalog_item.vendor_details
                ))
            
            item = Item(
                asin=catalog_item.asin,
                identifiers=identifiers,
                images=images,
                productTypes=product_types,
                salesRanks=sales_ranks,
                summaries=summaries,
                vendorDetails=vendor_details
            )
            items.append(item)
        
        # Build pagination
        next_token = str(offset // pageSize + 1) if len(items) == pageSize else None
        pagination = PaginationToken(nextToken=next_token)
        
        # Build refinements (simplified)
        refinements = SearchRefinements(
            brands=[],
            categories=[]
        )
        
        return SearchCatalogItemsResponse(
            numberOfResults=total_count,
            pagination=pagination,
            refinements=refinements,
            items=items
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{asin}", response_model=GetCatalogItemResponse)
async def get_catalog_item_2020_12_01(
    asin: str = Path(..., description="The Amazon Standard Identification Number (ASIN)"),
    marketplaceIds: List[str] = Query(..., description="A list of marketplace identifiers"),
    includedData: Optional[List[str]] = Query(None, description="A list of data sets to include"),
    locale: Optional[str] = Query(None, description="Locale for retrieving localized summaries"),
    db: Session = Depends(get_db)
):
    """
    Retrieves details for an item in the Amazon catalog.
    """
    
    try:
        catalog_item = db.query(CatalogItem).filter(
            CatalogItem.asin == asin,
            CatalogItem.marketplace_id.in_(marketplaceIds)
        ).first()
        
        if not catalog_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Build identifiers
        identifiers = []
        if catalog_item.identifiers:
            identifier_list = []
            for id_type, id_value in catalog_item.identifiers.items():
                identifier_list.append(ItemIdentifier(
                    type=id_type,
                    identifier=id_value
                ))
            identifiers.append(ItemIdentifiersByMarketplace(
                marketplaceId=catalog_item.marketplace_id,
                identifiers=identifier_list
            ))
        
        # Build images
        images = []
        if catalog_item.images:
            image_list = []
            for img in catalog_item.images:
                image_list.append(ItemImage(
                    variant=img.get('variant', 'MAIN'),
                    link=img.get('link', ''),
                    height=img.get('height'),
                    width=img.get('width')
                ))
            images.append(ItemImagesByMarketplace(
                marketplaceId=catalog_item.marketplace_id,
                images=image_list
            ))
        
        # Build product types
        product_types = []
        if catalog_item.product_type:
            product_types.append(ItemProductType(
                marketplaceId=catalog_item.marketplace_id,
                productType=catalog_item.product_type
            ))
        
        # Build sales ranks
        sales_ranks = []
        if catalog_item.sales_rankings:
            rank_list = []
            for rank in catalog_item.sales_rankings:
                rank_list.append(ItemSalesRank(
                    title=rank.get('title', ''),
                    link=rank.get('link', ''),
                    rank=rank.get('rank', 0)
                ))
            sales_ranks.append(ItemSalesRanksByMarketplace(
                marketplaceId=catalog_item.marketplace_id,
                ranks=rank_list
            ))
        
        # Build summaries
        summaries = []
        summaries.append(ItemSummary(
            marketplaceId=catalog_item.marketplace_id,
            brandName=catalog_item.brand,
            browseNode=catalog_item.browse_node_info.get('browse_node') if catalog_item.browse_node_info else None,
            itemName=catalog_item.item_name,
            manufacturer=catalog_item.manufacturer,
            modelNumber=catalog_item.model_number,
            sizeName=catalog_item.size_name,
            styleName=catalog_item.style_name
        ))
        
        # Build vendor details
        vendor_details = []
        if hasattr(catalog_item, 'vendor_details') and catalog_item.vendor_details:
            vendor_details.append(ItemVendorDetail(
                marketplaceId=catalog_item.marketplace_id,
                **catalog_item.vendor_details
            ))
        
        return GetCatalogItemResponse(
            asin=catalog_item.asin,
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
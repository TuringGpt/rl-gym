"""
Amazon Product Pricing API v0
Based on: https://developer-docs.amazon.com/sp-api/docs/product-pricing-api-v0-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import ProductPricing
import sys
from pathlib import Path as FilePath

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/products/pricing/v0", tags=["Product Pricing"])

# Response Models
class MoneyType(BaseModel):
    currency_code: Optional[str] = None
    amount: Optional[float] = None

class Points(BaseModel):
    points_number: Optional[int] = None
    points_monetary_value: Optional[MoneyType] = None

class PriceType(BaseModel):
    landed_price: Optional[MoneyType] = None
    listing_price: Optional[MoneyType] = None
    shipping: Optional[MoneyType] = None
    points: Optional[Points] = None

class CompetitivePriceType(BaseModel):
    competitive_price_id: str
    price: PriceType
    condition: Optional[str] = None
    subcondition: Optional[str] = None
    offer_type: Optional[str] = None
    quantity_tier: Optional[int] = None
    quantity_discount_type: Optional[str] = None
    seller_id: Optional[str] = None
    belongs_to_requester: Optional[bool] = None

class NumberOfOfferListingsType(BaseModel):
    condition: str
    fulfillment_channel: str
    offer_count: int

class LowestPricedOffersType(BaseModel):
    condition: str
    fulfillment_channel: str
    landed_price: MoneyType
    listing_price: MoneyType
    shipping: MoneyType
    points: Optional[Points] = None

class BuyBoxPriceType(BaseModel):
    condition: str
    landed_price: Optional[MoneyType] = None
    listing_price: MoneyType
    shipping: Optional[MoneyType] = None
    points: Optional[Points] = None

class Product(BaseModel):
    identifiers: Dict[str, List[Dict[str, str]]]
    attribute_sets: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    competitive_pricing: Optional[Dict[str, Any]] = None
    sales_rankings: Optional[List[Dict[str, Any]]] = None
    offers: Optional[List[Dict[str, Any]]] = None

class GetPricingResponse(BaseModel):
    payload: List[Product]
    errors: Optional[List[Dict[str, Any]]] = None

class GetCompetitivePricingResponse(BaseModel):
    payload: List[Product]
    errors: Optional[List[Dict[str, Any]]] = None

class GetListingOffersResponse(BaseModel):
    payload: Dict[str, Any]
    errors: Optional[List[Dict[str, Any]]] = None

class GetItemOffersResponse(BaseModel):
    payload: Dict[str, Any]
    errors: Optional[List[Dict[str, Any]]] = None

@router.get("/pricing", response_model=GetPricingResponse)
async def get_pricing(
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    asins: Optional[List[str]] = Query(None, description="A list of up to twenty Amazon Standard Identification Number (ASIN) values"),
    skus: Optional[List[str]] = Query(None, description="A list of up to twenty seller SKU values"),
    item_type: str = Query(..., description="Indicates whether ASIN values or seller SKU values are used"),
    db: Session = Depends(get_db)
):
    """
    Returns pricing information for a seller's offer listings based on seller SKU or ASIN.
    """
    
    try:
        query = db.query(ProductPricing).filter(ProductPricing.marketplace_id == marketplace_id)
        
        if item_type.lower() == "asin" and asins:
            query = query.filter(ProductPricing.asin.in_(asins))
        elif item_type.lower() == "sku" and skus:
            query = query.filter(ProductPricing.seller_sku.in_(skus))
        else:
            raise HTTPException(status_code=400, detail="Invalid item_type or missing identifiers")
        
        pricing_records = query.all()
        
        products = []
        for record in pricing_records:
            # Build identifiers
            identifiers = {
                "MarketplaceASIN": [{"MarketplaceId": record.marketplace_id, "ASIN": record.asin}]
            }
            if record.seller_sku:
                identifiers["SKUIdentifier"] = [{"MarketplaceId": record.marketplace_id, "SellerId": "TEST_SELLER", "SellerSKU": record.seller_sku}]
            
            # Build competitive pricing
            competitive_pricing = None
            if record.listing_price:
                competitive_pricing = {
                    "CompetitivePrices": [
                        {
                            "CompetitivePriceId": record.competitive_price_id or "1",
                            "Price": {
                                "LandedPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(record.landed_price) if record.landed_price else float(record.listing_price)
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(record.listing_price)
                                },
                                "Shipping": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(record.shipping_price) if record.shipping_price else 0.0
                                }
                            },
                            "condition": record.item_condition,
                            "subcondition": "New",
                            "offerType": "NEW"
                        }
                    ],
                    "NumberOfOfferListings": [
                        {
                            "condition": record.item_condition,
                            "fulfillmentChannel": "AMAZON",
                            "OfferCount": record.number_of_offer_listings or 1
                        }
                    ],
                    "TradeInValue": {
                        "CurrencyCode": "USD",
                        "Amount": float(record.trade_in_value) if record.trade_in_value else 0.0
                    }
                }
            
            product = Product(
                identifiers=identifiers,
                competitive_pricing=competitive_pricing
            )
            products.append(product)
        
        return GetPricingResponse(payload=products)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitivePrice", response_model=GetCompetitivePricingResponse)
async def get_competitive_pricing(
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    asins: Optional[List[str]] = Query(None, description="A list of up to twenty Amazon Standard Identification Number (ASIN) values"),
    skus: Optional[List[str]] = Query(None, description="A list of up to twenty seller SKU values"),
    item_type: str = Query(..., description="Indicates whether ASIN values or seller SKU values are used"),
    customer_type: Optional[str] = Query(None, description="Indicates whether to request Consumer or Business offers"),
    db: Session = Depends(get_db)
):
    """
    Returns competitive pricing information for a seller's offer listings based on seller SKU or ASIN.
    """
    
    # Similar logic to get_pricing but focused on competitive data
    return await get_pricing(marketplace_id, asins, skus, item_type, db)

@router.get("/listings/{seller_sku}/offers", response_model=GetListingOffersResponse)
async def get_listing_offers(
    seller_sku: str = Path(..., description="A seller SKU value"),
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    item_condition: str = Query(..., description="Filters the offers by item condition"),
    customer_type: Optional[str] = Query(None, description="Indicates whether to request Consumer or Business offers"),
    db: Session = Depends(get_db)
):
    """
    Returns the lowest priced offers for a single SKU listing.
    """
    
    try:
        pricing_record = db.query(ProductPricing).filter(
            ProductPricing.seller_sku == seller_sku,
            ProductPricing.marketplace_id == marketplace_id,
            ProductPricing.item_condition == item_condition
        ).first()
        
        if not pricing_record:
            raise HTTPException(status_code=404, detail="SKU not found")
        
        # Build mock offers response
        payload = {
            "MarketplaceID": marketplace_id,
            "ASIN": pricing_record.asin,
            "SKU": seller_sku,
            "ItemCondition": item_condition,
            "Status": "Success",
            "Identifier": {
                "MarketplaceId": marketplace_id,
                "SKU": seller_sku
            },
            "Summary": {
                "TotalOfferCount": pricing_record.number_of_offer_listings or 1,
                "NumberOfOffers": [
                    {
                        "condition": item_condition,
                        "fulfillmentChannel": "AMAZON",
                        "OfferCount": pricing_record.number_of_offer_listings or 1
                    }
                ],
                "LowestPrices": [
                    {
                        "condition": item_condition,
                        "fulfillmentChannel": "AMAZON",
                        "LandedPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.landed_price) if pricing_record.landed_price else float(pricing_record.listing_price)
                        },
                        "ListingPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.listing_price)
                        },
                        "Shipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                        }
                    }
                ],
                "BuyBoxPrices": [
                    {
                        "condition": item_condition,
                        "LandedPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.landed_price) if pricing_record.landed_price else float(pricing_record.listing_price)
                        },
                        "ListingPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.listing_price)
                        },
                        "Shipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                        }
                    }
                ]
            },
            "Offers": [
                {
                    "SellerId": "TEST_SELLER",
                    "SubCondition": "new",
                    "SellerFeedbackRating": {
                        "SellerPositiveFeedbackRating": 98.0,
                        "FeedbackCount": 1000
                    },
                    "ShippingTime": {
                        "minimumHours": 24,
                        "maximumHours": 48,
                        "availabilityType": "NOW"
                    },
                    "ListingPrice": {
                        "CurrencyCode": "USD",
                        "Amount": float(pricing_record.listing_price)
                    },
                    "Shipping": {
                        "CurrencyCode": "USD",
                        "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                    },
                    "ShipsFrom": {
                        "Country": "US"
                    },
                    "IsFulfilledByAmazon": True,
                    "IsBuyBoxWinner": True,
                    "IsFeaturedMerchant": True
                }
            ]
        }
        
        return GetListingOffersResponse(payload=payload)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{asin}/offers", response_model=GetItemOffersResponse)
async def get_item_offers(
    asin: str = Path(..., description="The Amazon Standard Identification Number (ASIN) of the item"),
    marketplace_id: str = Query(..., description="A marketplace identifier"),
    item_condition: str = Query(..., description="Filters the offers by item condition"),
    customer_type: Optional[str] = Query(None, description="Indicates whether to request Consumer or Business offers"),
    db: Session = Depends(get_db)
):
    """
    Returns the lowest priced offers for a single item based on ASIN.
    """
    
    try:
        pricing_records = db.query(ProductPricing).filter(
            ProductPricing.asin == asin,
            ProductPricing.marketplace_id == marketplace_id,
            ProductPricing.item_condition == item_condition
        ).all()
        
        if not pricing_records:
            raise HTTPException(status_code=404, detail="ASIN not found")
        
        # Use the first record for summary data
        main_record = pricing_records[0]
        
        # Build mock offers response similar to get_listing_offers
        offers = []
        for record in pricing_records:
            offers.append({
                "SellerId": f"SELLER_{record.seller_sku[:5]}",
                "SubCondition": "new",
                "SellerFeedbackRating": {
                    "SellerPositiveFeedbackRating": 95.0 + (hash(record.seller_sku) % 5),
                    "FeedbackCount": 500 + (hash(record.seller_sku) % 1000)
                },
                "ShippingTime": {
                    "minimumHours": 24,
                    "maximumHours": 48,
                    "availabilityType": "NOW"
                },
                "ListingPrice": {
                    "CurrencyCode": "USD",
                    "Amount": float(record.listing_price)
                },
                "Shipping": {
                    "CurrencyCode": "USD",
                    "Amount": float(record.shipping_price) if record.shipping_price else 0.0
                },
                "ShipsFrom": {
                    "Country": "US"
                },
                "IsFulfilledByAmazon": True,
                "IsBuyBoxWinner": record == main_record,
                "IsFeaturedMerchant": record == main_record
            })
        
        payload = {
            "MarketplaceID": marketplace_id,
            "ASIN": asin,
            "ItemCondition": item_condition,
            "Status": "Success",
            "Identifier": {
                "MarketplaceId": marketplace_id,
                "ASIN": asin
            },
            "Summary": {
                "TotalOfferCount": len(offers),
                "NumberOfOffers": [
                    {
                        "condition": item_condition,
                        "fulfillmentChannel": "AMAZON",
                        "OfferCount": len(offers)
                    }
                ],
                "LowestPrices": [
                    {
                        "condition": item_condition,
                        "fulfillmentChannel": "AMAZON",
                        "LandedPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.landed_price) if main_record.landed_price else float(main_record.listing_price)
                        },
                        "ListingPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.listing_price)
                        },
                        "Shipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.shipping_price) if main_record.shipping_price else 0.0
                        }
                    }
                ]
            },
            "Offers": offers
        }
        
        return GetItemOffersResponse(payload=payload)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch request models
class BatchRequest(BaseModel):
    method: str = "GET"
    marketplace_id: str = Field(..., alias="MarketplaceId")
    item_condition: str = Field(..., alias="ItemCondition")
    customer_type: Optional[str] = Field("Consumer", alias="CustomerType")
    asin: Optional[str] = Field(None, alias="Asin")
    seller_sku: Optional[str] = Field(None, alias="SellerSKU")

class BatchRequestContainer(BaseModel):
    requests: List[BatchRequest]

class BatchResponse(BaseModel):
    headers: Dict[str, str]
    status: Dict[str, Any]
    body: Dict[str, Any]
    request: Dict[str, Any]

class BatchResponseContainer(BaseModel):
    responses: List[BatchResponse]

@router.post("/batches/products/pricing/v0/itemOffers", response_model=BatchResponseContainer)
async def get_item_offers_batch(
    request: BatchRequestContainer,
    db: Session = Depends(get_db)
):
    """
    Returns the lowest priced offers for a batch of items based on ASIN.
    """
    try:
        responses = []
        
        for req in request.requests:
            try:
                if not req.asin:
                    # Missing ASIN
                    response = BatchResponse(
                        headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                        status={"statusCode": 400, "reasonPhrase": "Bad Request"},
                        body={
                            "errors": [
                                {
                                    "code": "InvalidInput",
                                    "message": "ASIN is required for item offers batch request",
                                    "details": ""
                                }
                            ]
                        },
                        request={
                            "MarketplaceId": req.marketplace_id,
                            "ItemCondition": req.item_condition,
                            "CustomerType": req.customer_type,
                            "Asin": req.asin
                        }
                    )
                    responses.append(response)
                    continue
                
                # Get item offers for this ASIN
                pricing_records = db.query(ProductPricing).filter(
                    ProductPricing.asin == req.asin,
                    ProductPricing.marketplace_id == req.marketplace_id,
                    ProductPricing.item_condition == req.item_condition
                ).all()
                
                if not pricing_records:
                    # ASIN not found
                    response = BatchResponse(
                        headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                        status={"statusCode": 404, "reasonPhrase": "Not Found"},
                        body={
                            "errors": [
                                {
                                    "code": "InvalidASIN",
                                    "message": f"The ASIN '{req.asin}' was not found.",
                                    "details": ""
                                }
                            ]
                        },
                        request={
                            "MarketplaceId": req.marketplace_id,
                            "ItemCondition": req.item_condition,
                            "CustomerType": req.customer_type,
                            "Asin": req.asin
                        }
                    )
                    responses.append(response)
                    continue
                
                # Use the first record for summary data
                main_record = pricing_records[0]
                
                # Build offers similar to get_item_offers
                offers = []
                for record in pricing_records:
                    offers.append({
                        "MyOffer": record == main_record,
                        "offerType": "B2C",
                        "SubCondition": "new",
                        "SellerId": f"SELLER_{record.seller_sku[:5]}",
                        "ConditionNotes": "",
                        "SellerFeedbackRating": {
                            "SellerPositiveFeedbackRating": 95.0 + (hash(record.seller_sku) % 5),
                            "FeedbackCount": 500 + (hash(record.seller_sku) % 1000)
                        },
                        "ShippingTime": {
                            "minimumHours": 24,
                            "maximumHours": 48,
                            "availableDate": datetime.utcnow().date().isoformat(),
                            "availabilityType": "NOW"
                        },
                        "ListingPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(record.listing_price)
                        },
                        "Shipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(record.shipping_price) if record.shipping_price else 0.0
                        },
                        "ShipsFrom": {
                            "State": "WA",
                            "Country": "US"
                        },
                        "IsFulfilledByAmazon": True,
                        "PrimeInformation": {
                            "IsPrime": True,
                            "IsNationalPrime": True
                        },
                        "IsBuyBoxWinner": record == main_record,
                        "IsFeaturedMerchant": record == main_record
                    })
                
                payload = {
                    "MarketplaceID": req.marketplace_id,
                    "ASIN": req.asin,
                    "SKU": main_record.seller_sku,
                    "ItemCondition": req.item_condition,
                    "status": "Success",
                    "Identifier": {
                        "MarketplaceId": req.marketplace_id,
                        "ASIN": req.asin,
                        "SellerSKU": main_record.seller_sku,
                        "ItemCondition": req.item_condition
                    },
                    "Summary": {
                        "TotalOfferCount": len(offers),
                        "NumberOfOffers": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "OfferCount": len(offers)
                            }
                        ],
                        "LowestPrices": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "offerType": "B2C",
                                "quantityTier": 1,
                                "quantityDiscountType": "QUANTITY_DISCOUNT",
                                "LandedPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.landed_price) if main_record.landed_price else float(main_record.listing_price)
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.listing_price)
                                },
                                "Shipping": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.shipping_price) if main_record.shipping_price else 0.0
                                },
                                "Points": {
                                    "PointsNumber": main_record.points_value or 0,
                                    "PointsMonetaryValue": {
                                        "CurrencyCode": "USD",
                                        "Amount": (main_record.points_value or 0) * 0.01
                                    }
                                }
                            }
                        ],
                        "BuyBoxPrices": [
                            {
                                "condition": req.item_condition,
                                "offerType": "B2C",
                                "quantityTier": 1,
                                "quantityDiscountType": "QUANTITY_DISCOUNT",
                                "LandedPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.landed_price) if main_record.landed_price else float(main_record.listing_price)
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.listing_price)
                                },
                                "Shipping": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(main_record.shipping_price) if main_record.shipping_price else 0.0
                                },
                                "Points": {
                                    "PointsNumber": main_record.points_value or 0,
                                    "PointsMonetaryValue": {
                                        "CurrencyCode": "USD",
                                        "Amount": (main_record.points_value or 0) * 0.01
                                    }
                                },
                                "sellerId": f"SELLER_{main_record.seller_sku[:5]}"
                            }
                        ],
                        "ListPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.listing_price) * 1.2  # Mock list price
                        },
                        "CompetitivePriceThreshold": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.listing_price) * 0.95
                        },
                        "SuggestedLowerPricePlusShipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(main_record.listing_price) * 0.9
                        },
                        "SalesRankings": [
                            {
                                "ProductCategoryId": "electronics",
                                "Rank": 1000 + hash(req.asin) % 9000
                            }
                        ],
                        "BuyBoxEligibleOffers": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "OfferCount": len(offers)
                            }
                        ],
                        "OffersAvailableTime": datetime.utcnow().isoformat()
                    },
                    "Offers": offers
                }
                
                response = BatchResponse(
                    headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                    status={"statusCode": 200, "reasonPhrase": "OK"},
                    body={"payload": payload},
                    request={
                        "MarketplaceId": req.marketplace_id,
                        "ItemCondition": req.item_condition,
                        "CustomerType": req.customer_type,
                        "Asin": req.asin
                    }
                )
                responses.append(response)
                
            except Exception as e:
                # Handle individual request errors
                response = BatchResponse(
                    headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                    status={"statusCode": 500, "reasonPhrase": "Internal Server Error"},
                    body={
                        "errors": [
                            {
                                "code": "InternalError",
                                "message": str(e),
                                "details": ""
                            }
                        ]
                    },
                    request={
                        "MarketplaceId": req.marketplace_id,
                        "ItemCondition": req.item_condition,
                        "CustomerType": req.customer_type,
                        "Asin": req.asin
                    }
                )
                responses.append(response)
        
        return BatchResponseContainer(responses=responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batches/products/pricing/v0/listingOffers", response_model=BatchResponseContainer)
async def get_listing_offers_batch(
    request: BatchRequestContainer,
    db: Session = Depends(get_db)
):
    """
    Returns the lowest priced offers for a batch of SKU listings.
    """
    try:
        responses = []
        
        for req in request.requests:
            try:
                if not req.seller_sku:
                    # Missing SKU
                    response = BatchResponse(
                        headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                        status={"statusCode": 400, "reasonPhrase": "Bad Request"},
                        body={
                            "errors": [
                                {
                                    "code": "InvalidInput",
                                    "message": "SellerSKU is required for listing offers batch request",
                                    "details": ""
                                }
                            ]
                        },
                        request={
                            "MarketplaceId": req.marketplace_id,
                            "ItemCondition": req.item_condition,
                            "CustomerType": req.customer_type,
                            "SellerSKU": req.seller_sku
                        }
                    )
                    responses.append(response)
                    continue
                
                # Get listing offers for this SKU
                pricing_record = db.query(ProductPricing).filter(
                    ProductPricing.seller_sku == req.seller_sku,
                    ProductPricing.marketplace_id == req.marketplace_id,
                    ProductPricing.item_condition == req.item_condition
                ).first()
                
                if not pricing_record:
                    # SKU not found
                    response = BatchResponse(
                        headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                        status={"statusCode": 404, "reasonPhrase": "Not Found"},
                        body={
                            "errors": [
                                {
                                    "code": "InvalidSKU",
                                    "message": f"The SKU '{req.seller_sku}' was not found.",
                                    "details": ""
                                }
                            ]
                        },
                        request={
                            "MarketplaceId": req.marketplace_id,
                            "ItemCondition": req.item_condition,
                            "CustomerType": req.customer_type,
                            "SellerSKU": req.seller_sku
                        }
                    )
                    responses.append(response)
                    continue
                
                # Build similar response to get_listing_offers
                payload = {
                    "MarketplaceID": req.marketplace_id,
                    "ASIN": pricing_record.asin,
                    "SKU": req.seller_sku,
                    "ItemCondition": req.item_condition,
                    "status": "Success",
                    "Identifier": {
                        "MarketplaceId": req.marketplace_id,
                        "ASIN": pricing_record.asin,
                        "SellerSKU": req.seller_sku,
                        "ItemCondition": req.item_condition
                    },
                    "Summary": {
                        "TotalOfferCount": pricing_record.number_of_offer_listings or 1,
                        "NumberOfOffers": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "OfferCount": pricing_record.number_of_offer_listings or 1
                            }
                        ],
                        "LowestPrices": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "offerType": "B2C",
                                "quantityTier": 1,
                                "quantityDiscountType": "QUANTITY_DISCOUNT",
                                "LandedPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.landed_price) if pricing_record.landed_price else float(pricing_record.listing_price)
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.listing_price)
                                },
                                "Shipping": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                                },
                                "Points": {
                                    "PointsNumber": pricing_record.points_value or 0,
                                    "PointsMonetaryValue": {
                                        "CurrencyCode": "USD",
                                        "Amount": (pricing_record.points_value or 0) * 0.01
                                    }
                                }
                            }
                        ],
                        "BuyBoxPrices": [
                            {
                                "condition": req.item_condition,
                                "offerType": "B2C",
                                "quantityTier": 1,
                                "quantityDiscountType": "QUANTITY_DISCOUNT",
                                "LandedPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.landed_price) if pricing_record.landed_price else float(pricing_record.listing_price)
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.listing_price)
                                },
                                "Shipping": {
                                    "CurrencyCode": "USD",
                                    "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                                },
                                "Points": {
                                    "PointsNumber": pricing_record.points_value or 0,
                                    "PointsMonetaryValue": {
                                        "CurrencyCode": "USD",
                                        "Amount": (pricing_record.points_value or 0) * 0.01
                                    }
                                },
                                "sellerId": "TEST_SELLER"
                            }
                        ],
                        "ListPrice": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.listing_price) * 1.2
                        },
                        "CompetitivePriceThreshold": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.listing_price) * 0.95
                        },
                        "SuggestedLowerPricePlusShipping": {
                            "CurrencyCode": "USD",
                            "Amount": float(pricing_record.listing_price) * 0.9
                        },
                        "SalesRankings": [
                            {
                                "ProductCategoryId": "electronics",
                                "Rank": 1000 + hash(req.seller_sku) % 9000
                            }
                        ],
                        "BuyBoxEligibleOffers": [
                            {
                                "condition": req.item_condition,
                                "fulfillmentChannel": "Amazon",
                                "OfferCount": pricing_record.number_of_offer_listings or 1
                            }
                        ],
                        "OffersAvailableTime": datetime.utcnow().isoformat()
                    },
                    "Offers": [
                        {
                            "MyOffer": True,
                            "offerType": "B2C",
                            "SubCondition": "new",
                            "SellerId": "TEST_SELLER",
                            "ConditionNotes": "",
                            "SellerFeedbackRating": {
                                "SellerPositiveFeedbackRating": 98.0,
                                "FeedbackCount": 1000
                            },
                            "ShippingTime": {
                                "minimumHours": 24,
                                "maximumHours": 48,
                                "availableDate": datetime.utcnow().date().isoformat(),
                                "availabilityType": "NOW"
                            },
                            "ListingPrice": {
                                "CurrencyCode": "USD",
                                "Amount": float(pricing_record.listing_price)
                            },
                            "quantityDiscountPrices": [
                                {
                                    "quantityTier": 1,
                                    "quantityDiscountType": "QUANTITY_DISCOUNT",
                                    "listingPrice": {
                                        "CurrencyCode": "USD",
                                        "Amount": float(pricing_record.listing_price)
                                    }
                                }
                            ],
                            "Points": {
                                "PointsNumber": pricing_record.points_value or 0,
                                "PointsMonetaryValue": {
                                    "CurrencyCode": "USD",
                                    "Amount": (pricing_record.points_value or 0) * 0.01
                                }
                            },
                            "Shipping": {
                                "CurrencyCode": "USD",
                                "Amount": float(pricing_record.shipping_price) if pricing_record.shipping_price else 0.0
                            },
                            "ShipsFrom": {
                                "State": "WA",
                                "Country": "US"
                            },
                            "IsFulfilledByAmazon": True,
                            "PrimeInformation": {
                                "IsPrime": True,
                                "IsNationalPrime": True
                            },
                            "IsBuyBoxWinner": True,
                            "IsFeaturedMerchant": True
                        }
                    ]
                }
                
                response = BatchResponse(
                    headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                    status={"statusCode": 200, "reasonPhrase": "OK"},
                    body={"payload": payload},
                    request={
                        "MarketplaceId": req.marketplace_id,
                        "ItemCondition": req.item_condition,
                        "CustomerType": req.customer_type,
                        "SellerSKU": req.seller_sku
                    }
                )
                responses.append(response)
                
            except Exception as e:
                # Handle individual request errors
                response = BatchResponse(
                    headers={"Date": datetime.utcnow().isoformat(), "x-amzn-RequestId": f"batch-{hash(str(req))}"},
                    status={"statusCode": 500, "reasonPhrase": "Internal Server Error"},
                    body={
                        "errors": [
                            {
                                "code": "InternalError",
                                "message": str(e),
                                "details": ""
                            }
                        ]
                    },
                    request={
                        "MarketplaceId": req.marketplace_id,
                        "ItemCondition": req.item_condition,
                        "CustomerType": req.customer_type,
                        "SellerSKU": req.seller_sku
                    }
                )
                responses.append(response)
        
        return BatchResponseContainer(responses=responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
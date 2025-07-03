"""
Amazon Product Pricing API v2022-05-01
Based on: https://developer-docs.amazon.com/sp-api/docs/product-pricing-api-v2022-05-01-reference
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import ProductPricing
import sys
from pathlib import Path as FilePath
from datetime import datetime

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/products/pricing/2022-05-01", tags=["Product Pricing v2022-05-01"])

# Request Models
class PostalCode(BaseModel):
    country_code: str = Field(..., alias="countryCode")
    value: str = Field(..., alias="value")

class SampleLocation(BaseModel):
    postal_code: PostalCode = Field(..., alias="postalCode")

class SegmentDetails(BaseModel):
    sample_location: Optional[SampleLocation] = Field(None, alias="sampleLocation")

class Segment(BaseModel):
    segment_details: Optional[SegmentDetails] = Field(None, alias="segmentDetails")

class FeaturedOfferExpectedPriceRequest(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    sku: str = Field(..., alias="sku")
    segment: Optional[Segment] = Field(None, alias="segment")
    method: str = "GET"

class FeaturedOfferExpectedPriceBatchRequest(BaseModel):
    requests: List[FeaturedOfferExpectedPriceRequest]

class CompetitiveSummaryIncludedData(BaseModel):
    included_data: List[str] = Field(..., alias="includedData")
    method: str = "GET"

class CompetitiveSummaryRequest(BaseModel):
    marketplace_id: str = Field(..., alias="marketplaceId")
    asin: str = Field(..., alias="asin")
    included_data: Optional[List[str]] = Field(None, alias="includedData")
    method: str = "GET"

class CompetitiveSummaryBatchRequest(BaseModel):
    requests: List[CompetitiveSummaryRequest]

# Response Models
class MoneyType(BaseModel):
    amount: float
    currency_code: str = Field(..., alias="currencyCode")

class Points(BaseModel):
    points_number: int = Field(..., alias="pointsNumber")
    points_monetary_value: MoneyType = Field(..., alias="pointsMonetaryValue")

class OfferIdentifier(BaseModel):
    asin: str
    sku: Optional[str] = None
    marketplace_id: str = Field(..., alias="marketplaceId")
    fulfillment_type: str = Field(..., alias="fulfillmentType")
    seller_id: str = Field(..., alias="sellerId")

class Price(BaseModel):
    listing_price: MoneyType = Field(..., alias="listingPrice")
    shipping_price: Optional[MoneyType] = Field(None, alias="shippingPrice")
    points: Optional[Points] = None

class FeaturedOffer(BaseModel):
    offer_identifier: OfferIdentifier = Field(..., alias="offerIdentifier")
    condition: str
    price: Price

class FeaturedOfferExpectedPrice(BaseModel):
    listing_price: MoneyType = Field(..., alias="listingPrice")
    points: Optional[Points] = None

class FeaturedOfferExpectedPriceResult(BaseModel):
    featured_offer_expected_price: Optional[FeaturedOfferExpectedPrice] = Field(None, alias="featuredOfferExpectedPrice")
    result_status: str = Field(..., alias="resultStatus")
    competing_featured_offer: Optional[FeaturedOffer] = Field(None, alias="competingFeaturedOffer")
    current_featured_offer: Optional[FeaturedOffer] = Field(None, alias="currentFeaturedOffer")

class FeaturedOfferExpectedPriceResponseBody(BaseModel):
    offer_identifier: OfferIdentifier = Field(..., alias="offerIdentifier")
    featured_offer_expected_price_results: List[FeaturedOfferExpectedPriceResult] = Field(..., alias="featuredOfferExpectedPriceResults")

class BatchResponseStatus(BaseModel):
    status_code: int = Field(..., alias="statusCode")
    reason_phrase: str = Field(..., alias="reasonPhrase")

class FeaturedOfferExpectedPriceBatchResponseItem(BaseModel):
    request: Dict[str, Any]
    status: BatchResponseStatus
    headers: Dict[str, str]
    body: FeaturedOfferExpectedPriceResponseBody

class FeaturedOfferExpectedPriceBatchResponse(BaseModel):
    responses: List[FeaturedOfferExpectedPriceBatchResponseItem]

# Competitive Summary Models
class ShippingOption(BaseModel):
    shipping_option_type: str = Field(..., alias="shippingOptionType")
    price: MoneyType

class SegmentedFeaturedOffer(BaseModel):
    seller_id: str = Field(..., alias="sellerId")
    condition: str
    fulfillment_type: str = Field(..., alias="fulfillmentType")
    listing_price: MoneyType = Field(..., alias="listingPrice")
    shipping_options: List[ShippingOption] = Field(..., alias="shippingOptions")
    points: Optional[Points] = None
    featured_offer_segments: List[Dict[str, Any]] = Field(..., alias="featuredOfferSegments")

class FeaturedBuyingOption(BaseModel):
    buying_option_type: str = Field(..., alias="buyingOptionType")
    segmented_featured_offers: List[SegmentedFeaturedOffer] = Field(..., alias="segmentedFeaturedOffers")

class ReferencePrice(BaseModel):
    name: str
    price: MoneyType

class PrimeDetails(BaseModel):
    eligibility: str

class LowestPricedOffer(BaseModel):
    listing_price: MoneyType = Field(..., alias="listingPrice")
    shipping_options: List[ShippingOption] = Field(..., alias="shippingOptions")
    points: Optional[Points] = None
    prime_details: Optional[PrimeDetails] = Field(None, alias="primeDetails")
    sub_condition: str = Field(..., alias="subCondition")
    seller_id: str = Field(..., alias="sellerId")
    fulfillment_type: str = Field(..., alias="fulfillmentType")

class LowestPricedOffersGroup(BaseModel):
    lowest_priced_offers_input: Dict[str, str] = Field(..., alias="lowestPricedOffersInput")
    offers: List[LowestPricedOffer]

class CompetitiveSummaryResponseBody(BaseModel):
    asin: str
    marketplace_id: str = Field(..., alias="marketplaceId")
    featured_buying_options: Optional[List[FeaturedBuyingOption]] = Field(None, alias="featuredBuyingOptions")
    reference_prices: Optional[List[ReferencePrice]] = Field(None, alias="referencePrices")
    lowest_priced_offers: Optional[List[LowestPricedOffersGroup]] = Field(None, alias="lowestPricedOffers")

class CompetitiveSummaryBatchResponseItem(BaseModel):
    status: BatchResponseStatus
    body: CompetitiveSummaryResponseBody

class CompetitiveSummaryBatchResponse(BaseModel):
    responses: List[CompetitiveSummaryBatchResponseItem]

@router.post("/offer/featuredOfferExpectedPrice", response_model=FeaturedOfferExpectedPriceBatchResponse)
async def get_featured_offer_expected_price_batch(
    request: FeaturedOfferExpectedPriceBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Returns the set of responses that correspond to the batched list of up to 40 requests.
    """
    try:
        responses = []
        
        for req in request.requests:
            try:
                # Look up pricing data for this SKU
                pricing_record = db.query(ProductPricing).filter(
                    ProductPricing.seller_sku == req.sku,
                    ProductPricing.marketplace_id == req.marketplace_id
                ).first()
                
                if not pricing_record:
                    # SKU not found - return error response
                    error_response = FeaturedOfferExpectedPriceBatchResponseItem(
                        request={
                            "marketplaceId": req.marketplace_id,
                            "sku": req.sku
                        },
                        status=BatchResponseStatus(
                            status_code=400,
                            reason_phrase="Client Error"
                        ),
                        headers={},
                        body={
                            "errors": [
                                {
                                    "code": "INVALID_SKU",
                                    "message": "The requested SKU does not exist for the seller in the requested marketplace."
                                }
                            ]
                        }
                    )
                    responses.append(error_response)
                    continue
                
                # Build successful response
                offer_identifier = OfferIdentifier(
                    asin=pricing_record.asin,
                    sku=req.sku,
                    marketplace_id=req.marketplace_id,
                    fulfillment_type="AFN",
                    seller_id="MY_SELLER_ID"
                )
                
                # Calculate featured offer expected price (slightly lower than current listing)
                expected_listing_price = float(pricing_record.listing_price) * 0.95
                
                featured_offer_expected_price = FeaturedOfferExpectedPrice(
                    listing_price=MoneyType(
                        amount=expected_listing_price,
                        currency_code="USD"
                    ),
                    points=Points(
                        points_number=3,
                        points_monetary_value=MoneyType(
                            amount=0.03,
                            currency_code="USD"
                        )
                    )
                )
                
                # Build competing and current featured offers
                competing_offer = FeaturedOffer(
                    offer_identifier=OfferIdentifier(
                        asin=pricing_record.asin,
                        marketplace_id=req.marketplace_id,
                        fulfillment_type="AFN",
                        seller_id="OTHER_SELLER_ID"
                    ),
                    condition="New",
                    price=Price(
                        listing_price=MoneyType(
                            amount=float(pricing_record.listing_price),
                            currency_code="USD"
                        ),
                        shipping_price=MoneyType(
                            amount=0,
                            currency_code="USD"
                        ),
                        points=Points(
                            points_number=3,
                            points_monetary_value=MoneyType(
                                amount=0.03,
                                currency_code="USD"
                            )
                        )
                    )
                )
                
                result = FeaturedOfferExpectedPriceResult(
                    featured_offer_expected_price=featured_offer_expected_price,
                    result_status="VALID_FOEP",
                    competing_featured_offer=competing_offer,
                    current_featured_offer=competing_offer
                )
                
                response_body = FeaturedOfferExpectedPriceResponseBody(
                    offer_identifier=offer_identifier,
                    featured_offer_expected_price_results=[result]
                )
                
                success_response = FeaturedOfferExpectedPriceBatchResponseItem(
                    request={
                        "marketplaceId": req.marketplace_id,
                        "sku": req.sku,
                        "segment": req.segment.dict() if req.segment else None
                    },
                    status=BatchResponseStatus(
                        status_code=200,
                        reason_phrase="Success"
                    ),
                    headers={},
                    body=response_body
                )
                responses.append(success_response)
                
            except Exception as e:
                # Handle individual request errors
                error_response = FeaturedOfferExpectedPriceBatchResponseItem(
                    request={
                        "marketplaceId": req.marketplace_id,
                        "sku": req.sku
                    },
                    status=BatchResponseStatus(
                        status_code=500,
                        reason_phrase="Internal Server Error"
                    ),
                    headers={},
                    body={
                        "errors": [
                            {
                                "code": "InternalError",
                                "message": str(e)
                            }
                        ]
                    }
                )
                responses.append(error_response)
        
        return FeaturedOfferExpectedPriceBatchResponse(responses=responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items/competitiveSummary", response_model=CompetitiveSummaryBatchResponse)
async def get_competitive_summary(
    request: CompetitiveSummaryBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Returns the competitive summary response including featured buying options for a batch of requested ASINs.
    """
    try:
        responses = []
        
        for req in request.requests:
            try:
                # Look up pricing data for this ASIN
                pricing_records = db.query(ProductPricing).filter(
                    ProductPricing.asin == req.asin,
                    ProductPricing.marketplace_id == req.marketplace_id
                ).all()
                
                if not pricing_records:
                    # ASIN not found - still return success with empty data
                    response_body = CompetitiveSummaryResponseBody(
                        asin=req.asin,
                        marketplace_id=req.marketplace_id,
                        featured_buying_options=[],
                        reference_prices=[],
                        lowest_priced_offers=[]
                    )
                    
                    success_response = CompetitiveSummaryBatchResponseItem(
                        status=BatchResponseStatus(
                            status_code=200,
                            reason_phrase="Success"
                        ),
                        body=response_body
                    )
                    responses.append(success_response)
                    continue
                
                # Build featured buying options if requested
                featured_buying_options = []
                if not req.included_data or "featuredBuyingOptions" in req.included_data:
                    # Build segmented featured offers from pricing records
                    segmented_offers = []
                    for record in pricing_records[:2]:  # Limit to top 2 offers
                        segments = [
                            {
                                "customerMembership": "PRIME",
                                "segmentDetails": {
                                    "glanceViewWeightPercentage": 72,
                                    "sampleLocation": {
                                        "postalCode": {
                                            "countryCode": "US",
                                            "value": "12345"
                                        }
                                    }
                                }
                            },
                            {
                                "customerMembership": "NON_PRIME",
                                "segmentDetails": {
                                    "glanceViewWeightPercentage": 10,
                                    "sampleLocation": {
                                        "postalCode": {
                                            "countryCode": "US",
                                            "value": "67890"
                                        }
                                    }
                                }
                            }
                        ]
                        
                        segmented_offer = SegmentedFeaturedOffer(
                            seller_id=f"A{hash(record.seller_sku) % 1000000000:010d}",
                            condition="New",
                            fulfillment_type="MFN",
                            listing_price=MoneyType(
                                amount=float(record.listing_price),
                                currency_code="USD"
                            ),
                            shipping_options=[
                                ShippingOption(
                                    shipping_option_type="DEFAULT",
                                    price=MoneyType(
                                        amount=float(record.shipping_price) if record.shipping_price else 2.5,
                                        currency_code="USD"
                                    )
                                )
                            ],
                            points=Points(
                                points_number=3,
                                points_monetary_value=MoneyType(
                                    amount=0.03,
                                    currency_code="USD"
                                )
                            ),
                            featured_offer_segments=segments
                        )
                        segmented_offers.append(segmented_offer)
                    
                    featured_buying_option = FeaturedBuyingOption(
                        buying_option_type="New",
                        segmented_featured_offers=segmented_offers
                    )
                    featured_buying_options.append(featured_buying_option)
                
                # Build reference prices
                main_record = pricing_records[0]
                reference_prices = [
                    ReferencePrice(
                        name="CompetitivePriceThreshold",
                        price=MoneyType(
                            amount=float(main_record.listing_price),
                            currency_code="USD"
                        )
                    ),
                    ReferencePrice(
                        name="CompetitivePrice", 
                        price=MoneyType(
                            amount=float(main_record.listing_price) * 0.96,
                            currency_code="USD"
                        )
                    ),
                    ReferencePrice(
                        name="WasPrice",
                        price=MoneyType(
                            amount=float(main_record.listing_price) * 1.08,
                            currency_code="USD"
                        )
                    )
                ]
                
                # Build lowest priced offers
                lowest_priced_offers = []
                
                # New condition offers
                new_offers = []
                for record in pricing_records[:2]:
                    offer = LowestPricedOffer(
                        listing_price=MoneyType(
                            amount=float(record.listing_price),
                            currency_code="USD"
                        ),
                        shipping_options=[
                            ShippingOption(
                                shipping_option_type="DEFAULT",
                                price=MoneyType(
                                    amount=float(record.shipping_price) if record.shipping_price else 2.5,
                                    currency_code="USD"
                                )
                            )
                        ],
                        points=Points(
                            points_number=record.points_value or 50,
                            points_monetary_value=MoneyType(
                                amount=(record.points_value or 50) * 0.01,
                                currency_code="USD"
                            )
                        ),
                        prime_details=PrimeDetails(eligibility="REGIONAL"),
                        sub_condition="New",
                        seller_id=f"A{hash(record.seller_sku) % 1000000000:010d}",
                        fulfillment_type="MFN"
                    )
                    new_offers.append(offer)
                
                new_offers_group = LowestPricedOffersGroup(
                    lowest_priced_offers_input={
                        "itemCondition": "New",
                        "offerType": "Consumer"
                    },
                    offers=new_offers
                )
                lowest_priced_offers.append(new_offers_group)
                
                # Build response body
                response_body = CompetitiveSummaryResponseBody(
                    asin=req.asin,
                    marketplace_id=req.marketplace_id,
                    featured_buying_options=featured_buying_options,
                    reference_prices=reference_prices,
                    lowest_priced_offers=lowest_priced_offers
                )
                
                success_response = CompetitiveSummaryBatchResponseItem(
                    status=BatchResponseStatus(
                        status_code=200,
                        reason_phrase="Success"
                    ),
                    body=response_body
                )
                responses.append(success_response)
                
            except Exception as e:
                # Handle individual request errors
                error_response = CompetitiveSummaryBatchResponseItem(
                    status=BatchResponseStatus(
                        status_code=500,
                        reason_phrase="Internal Server Error"
                    ),
                    body={
                        "errors": [
                            {
                                "code": "InternalError",
                                "message": str(e)
                            }
                        ]
                    }
                )
                responses.append(error_response)
        
        return CompetitiveSummaryBatchResponse(responses=responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
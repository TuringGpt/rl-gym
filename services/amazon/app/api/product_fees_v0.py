"""
Amazon Product Fees API v0
Based on: https://developer-docs.amazon.com/sp-api/docs/product-fees-api-v0-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import ProductFees
import sys
from pathlib import Path as FilePath
from datetime import datetime

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/products/fees/v0", tags=["Product Fees"])

# Request Models
class MoneyType(BaseModel):
    currency_code: str = Field(..., alias="CurrencyCode")
    amount: float = Field(..., alias="Amount")

class Points(BaseModel):
    points_number: int = Field(..., alias="PointsNumber")
    points_monetary_value: MoneyType = Field(..., alias="PointsMonetaryValue")

class PriceToEstimateFees(BaseModel):
    listing_price: MoneyType = Field(..., alias="ListingPrice")
    shipping: Optional[MoneyType] = Field(None, alias="Shipping")
    points: Optional[Points] = Field(None, alias="Points")

class FeesEstimateRequest(BaseModel):
    marketplace_id: str = Field(..., alias="MarketplaceId")
    id_type: str = Field(..., alias="IdType")  # ASIN or SKU
    id_value: str = Field(..., alias="IdValue")
    is_amazon_fulfilled: bool = Field(..., alias="IsAmazonFulfilled")
    price_to_estimate_fees: PriceToEstimateFees = Field(..., alias="PriceToEstimateFees")
    seller_input_identifier: Optional[str] = Field(None, alias="SellerInputIdentifier")
    optional_fulfillment_program: Optional[str] = Field(None, alias="OptionalFulfillmentProgram")

class FeesEstimateByIdRequest(BaseModel):
    fees_estimate_requests: List[FeesEstimateRequest] = Field(..., alias="FeesEstimateRequests")

# Response Models
class FeesEstimateIdentifier(BaseModel):
    marketplace_id: str = Field(..., alias="MarketplaceId")
    seller_id: str = Field(..., alias="SellerId")
    id_type: str = Field(..., alias="IdType")
    id_value: str = Field(..., alias="IdValue")
    is_amazon_fulfilled: bool = Field(..., alias="IsAmazonFulfilled")
    price_to_estimate_fees: PriceToEstimateFees = Field(..., alias="PriceToEstimateFees")
    seller_input_identifier: Optional[str] = Field(None, alias="SellerInputIdentifier")
    optional_fulfillment_program: Optional[str] = Field(None, alias="OptionalFulfillmentProgram")

class FeeDetail(BaseModel):
    fee_type: str = Field(..., alias="FeeType")
    fee_amount: MoneyType = Field(..., alias="FeeAmount")
    fee_promotion: Optional[MoneyType] = Field(None, alias="FeePromotion")
    tax_amount: Optional[MoneyType] = Field(None, alias="TaxAmount")
    final_fee: MoneyType = Field(..., alias="FinalFee")
    included_fee_detail_list: Optional[List["FeeDetail"]] = Field(None, alias="IncludedFeeDetailList")

class FeesEstimate(BaseModel):
    time_of_fees_estimation: datetime = Field(..., alias="TimeOfFeesEstimation")
    total_fees_estimate: MoneyType = Field(..., alias="TotalFeesEstimate")
    fee_detail_list: List[FeeDetail] = Field(..., alias="FeeDetailList")

class Error(BaseModel):
    type: str = Field(..., alias="Type")
    code: str = Field(..., alias="Code")
    message: str = Field(..., alias="Message")
    detail: Optional[List[Any]] = Field(None, alias="Detail")

class FeesEstimateResult(BaseModel):
    status: str = Field(..., alias="Status")
    fees_estimate_identifier: Optional[FeesEstimateIdentifier] = Field(None, alias="FeesEstimateIdentifier")
    fees_estimate: Optional[FeesEstimate] = Field(None, alias="FeesEstimate")
    error: Optional[Error] = Field(None, alias="Error")

class GetMyFeesEstimateResponse(BaseModel):
    payload: FeesEstimateResult = Field(..., alias="payload")
    errors: Optional[List[Dict[str, Any]]] = Field(None, alias="errors")

class GetMyFeesEstimatesResponse(BaseModel):
    payload: List[FeesEstimateResult] = Field(..., alias="payload")
    errors: Optional[List[Dict[str, Any]]] = Field(None, alias="errors")

# Update forward references
FeeDetail.model_rebuild()

@router.post("/listings/{seller_sku}/feesEstimate", response_model=GetMyFeesEstimateResponse)
async def get_my_fees_estimate_for_sku(
    request: FeesEstimateRequest,
    seller_sku: str = Path(..., description="The seller SKU"),
    db: Session = Depends(get_db)
):
    """
    Returns the estimated fees for the item indicated by the specified seller SKU.
    """
    try:
        # Validate that the ID type matches endpoint
        if request.id_type.upper() != "SKU":
            raise HTTPException(status_code=400, detail="IdType must be 'SKU' for this endpoint")
        
        if request.id_value != seller_sku:
            raise HTTPException(status_code=400, detail="IdValue must match seller_sku path parameter")
        
        # Look up fee data from database
        fee_record = db.query(ProductFees).filter(
            ProductFees.seller_sku == seller_sku,
            ProductFees.marketplace_id == request.marketplace_id
        ).first()
        
        if not fee_record:
            # Return error result
            result = FeesEstimateResult(
                status="ClientError",
                error=Error(
                    type="InvalidInput",
                    code="InvalidSKU",
                    message=f"The SKU '{seller_sku}' was not found.",
                    detail=[]
                )
            )
        else:
            # Build successful response
            identifier = FeesEstimateIdentifier(
                marketplace_id=request.marketplace_id,
                seller_id=fee_record.seller_id,
                id_type="SKU",
                id_value=seller_sku,
                is_amazon_fulfilled=request.is_amazon_fulfilled,
                price_to_estimate_fees=request.price_to_estimate_fees,
                seller_input_identifier=request.seller_input_identifier,
                optional_fulfillment_program=request.optional_fulfillment_program
            )
            
            # Calculate fees based on listing price
            listing_price = request.price_to_estimate_fees.listing_price.amount
            referral_fee = round(listing_price * 0.15, 2)  # 15% referral fee
            fulfillment_fee = round(fee_record.fulfillment_fee, 2) if fee_record.fulfillment_fee else 2.50
            total_fees = referral_fee + fulfillment_fee
            
            fee_details = [
                FeeDetail(
                    fee_type="ReferralFee",
                    fee_amount=MoneyType(currency_code="USD", amount=referral_fee),
                    final_fee=MoneyType(currency_code="USD", amount=referral_fee)
                ),
                FeeDetail(
                    fee_type="FBAFees",
                    fee_amount=MoneyType(currency_code="USD", amount=fulfillment_fee),
                    final_fee=MoneyType(currency_code="USD", amount=fulfillment_fee)
                )
            ]
            
            fees_estimate = FeesEstimate(
                time_of_fees_estimation=datetime.utcnow(),
                total_fees_estimate=MoneyType(currency_code="USD", amount=total_fees),
                fee_detail_list=fee_details
            )
            
            result = FeesEstimateResult(
                status="Success",
                fees_estimate_identifier=identifier,
                fees_estimate=fees_estimate
            )
        
        return GetMyFeesEstimateResponse(payload=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items/{asin}/feesEstimate", response_model=GetMyFeesEstimateResponse)
async def get_my_fees_estimate_for_asin(
    request: FeesEstimateRequest,
    asin: str = Path(..., description="The Amazon Standard Identification Number (ASIN)"),
    db: Session = Depends(get_db)
):
    """
    Returns the estimated fees for the item indicated by the specified ASIN.
    """
    try:
        # Validate that the ID type matches endpoint
        if request.id_type.upper() != "ASIN":
            raise HTTPException(status_code=400, detail="IdType must be 'ASIN' for this endpoint")
        
        if request.id_value != asin:
            raise HTTPException(status_code=400, detail="IdValue must match asin path parameter")
        
        # Look up fee data from database
        fee_record = db.query(ProductFees).filter(
            ProductFees.asin == asin,
            ProductFees.marketplace_id == request.marketplace_id
        ).first()
        
        if not fee_record:
            # Return error result
            result = FeesEstimateResult(
                status="ClientError",
                error=Error(
                    type="InvalidInput",
                    code="InvalidASIN",
                    message=f"The ASIN '{asin}' was not found.",
                    detail=[]
                )
            )
        else:
            # Build successful response (similar logic to SKU endpoint)
            identifier = FeesEstimateIdentifier(
                marketplace_id=request.marketplace_id,
                seller_id=fee_record.seller_id,
                id_type="ASIN",
                id_value=asin,
                is_amazon_fulfilled=request.is_amazon_fulfilled,
                price_to_estimate_fees=request.price_to_estimate_fees,
                seller_input_identifier=request.seller_input_identifier,
                optional_fulfillment_program=request.optional_fulfillment_program
            )
            
            # Calculate fees
            listing_price = request.price_to_estimate_fees.listing_price.amount
            referral_fee = round(listing_price * 0.15, 2)
            fulfillment_fee = round(fee_record.fulfillment_fee, 2) if fee_record.fulfillment_fee else 2.50
            total_fees = referral_fee + fulfillment_fee
            
            fee_details = [
                FeeDetail(
                    fee_type="ReferralFee",
                    fee_amount=MoneyType(currency_code="USD", amount=referral_fee),
                    final_fee=MoneyType(currency_code="USD", amount=referral_fee)
                ),
                FeeDetail(
                    fee_type="FBAFees",
                    fee_amount=MoneyType(currency_code="USD", amount=fulfillment_fee),
                    final_fee=MoneyType(currency_code="USD", amount=fulfillment_fee)
                )
            ]
            
            fees_estimate = FeesEstimate(
                time_of_fees_estimation=datetime.utcnow(),
                total_fees_estimate=MoneyType(currency_code="USD", amount=total_fees),
                fee_detail_list=fee_details
            )
            
            result = FeesEstimateResult(
                status="Success",
                fees_estimate_identifier=identifier,
                fees_estimate=fees_estimate
            )
        
        return GetMyFeesEstimateResponse(payload=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feesEstimate", response_model=GetMyFeesEstimatesResponse)
async def get_my_fees_estimates(
    request: FeesEstimateByIdRequest,
    db: Session = Depends(get_db)
):
    """
    Returns the estimated fees for a list of products.
    """
    try:
        results = []
        
        for fee_request in request.fees_estimate_requests:
            try:
                # Look up fee data based on ID type
                if fee_request.id_type.upper() == "SKU":
                    fee_record = db.query(ProductFees).filter(
                        ProductFees.seller_sku == fee_request.id_value,
                        ProductFees.marketplace_id == fee_request.marketplace_id
                    ).first()
                elif fee_request.id_type.upper() == "ASIN":
                    fee_record = db.query(ProductFees).filter(
                        ProductFees.asin == fee_request.id_value,
                        ProductFees.marketplace_id == fee_request.marketplace_id
                    ).first()
                else:
                    # Invalid ID type
                    result = FeesEstimateResult(
                        status="ClientError",
                        error=Error(
                            type="InvalidInput",
                            code="InvalidIdType",
                            message=f"Invalid IdType: {fee_request.id_type}. Must be 'ASIN' or 'SKU'.",
                            detail=[]
                        )
                    )
                    results.append(result)
                    continue
                
                if not fee_record:
                    # Item not found
                    result = FeesEstimateResult(
                        status="ClientError",
                        error=Error(
                            type="InvalidInput",
                            code=f"Invalid{fee_request.id_type.upper()}",
                            message=f"The {fee_request.id_type.upper()} '{fee_request.id_value}' was not found.",
                            detail=[]
                        )
                    )
                else:
                    # Build successful response
                    identifier = FeesEstimateIdentifier(
                        marketplace_id=fee_request.marketplace_id,
                        seller_id=fee_record.seller_id,
                        id_type=fee_request.id_type.upper(),
                        id_value=fee_request.id_value,
                        is_amazon_fulfilled=fee_request.is_amazon_fulfilled,
                        price_to_estimate_fees=fee_request.price_to_estimate_fees,
                        seller_input_identifier=fee_request.seller_input_identifier,
                        optional_fulfillment_program=fee_request.optional_fulfillment_program
                    )
                    
                    # Calculate fees
                    listing_price = fee_request.price_to_estimate_fees.listing_price.amount
                    referral_fee = round(listing_price * 0.15, 2)
                    fulfillment_fee = round(fee_record.fulfillment_fee, 2) if fee_record.fulfillment_fee else 2.50
                    total_fees = referral_fee + fulfillment_fee
                    
                    fee_details = [
                        FeeDetail(
                            fee_type="ReferralFee",
                            fee_amount=MoneyType(currency_code="USD", amount=referral_fee),
                            final_fee=MoneyType(currency_code="USD", amount=referral_fee)
                        ),
                        FeeDetail(
                            fee_type="FBAFees",
                            fee_amount=MoneyType(currency_code="USD", amount=fulfillment_fee),
                            final_fee=MoneyType(currency_code="USD", amount=fulfillment_fee)
                        )
                    ]
                    
                    fees_estimate = FeesEstimate(
                        time_of_fees_estimation=datetime.utcnow(),
                        total_fees_estimate=MoneyType(currency_code="USD", amount=total_fees),
                        fee_detail_list=fee_details
                    )
                    
                    result = FeesEstimateResult(
                        status="Success",
                        fees_estimate_identifier=identifier,
                        fees_estimate=fees_estimate
                    )
                
                results.append(result)
                
            except Exception as e:
                # Handle individual request errors
                result = FeesEstimateResult(
                    status="ServerError",
                    error=Error(
                        type="InternalError",
                        code="InternalError",
                        message=str(e),
                        detail=[]
                    )
                )
                results.append(result)
        
        return GetMyFeesEstimatesResponse(payload=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
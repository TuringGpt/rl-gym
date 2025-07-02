"""
Amazon Finances API v0
Based on: https://developer-docs.amazon.com/sp-api/docs/finances-api-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import FinancialEvent
import sys
from pathlib import Path as FilePath

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/finances/v0", tags=["Finances"])

# Response Models
class Currency(BaseModel):
    currency_code: Optional[str] = None
    currency_amount: Optional[float] = None

class ChargeComponent(BaseModel):
    charge_type: Optional[str] = None
    charge_amount: Optional[Currency] = None

class FeeComponent(BaseModel):
    fee_type: Optional[str] = None
    fee_amount: Optional[Currency] = None

class Promotion(BaseModel):
    promotion_type: Optional[str] = None
    promotion_id: Optional[str] = None
    promotion_amount: Optional[Currency] = None

class DirectPayment(BaseModel):
    direct_payment_type: Optional[str] = None
    direct_payment_amount: Optional[Currency] = None

class ShipmentEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    seller_order_id: Optional[str] = None
    marketplace_name: Optional[str] = None
    order_charge_list: Optional[List[ChargeComponent]] = None
    order_charge_adjustment_list: Optional[List[ChargeComponent]] = None
    shipment_fee_list: Optional[List[FeeComponent]] = None
    shipment_fee_adjustment_list: Optional[List[FeeComponent]] = None
    order_fee_list: Optional[List[FeeComponent]] = None
    order_fee_adjustment_list: Optional[List[FeeComponent]] = None
    direct_payment_list: Optional[List[DirectPayment]] = None
    posted_date: Optional[datetime] = None
    shipment_item_list: Optional[List[Dict[str, Any]]] = None
    shipment_item_adjustment_list: Optional[List[Dict[str, Any]]] = None

class RefundEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    seller_order_id: Optional[str] = None
    marketplace_name: Optional[str] = None
    shipment_item_charge_list: Optional[List[ChargeComponent]] = None
    shipment_item_fee_list: Optional[List[FeeComponent]] = None
    order_fee_list: Optional[List[FeeComponent]] = None
    direct_payment_list: Optional[List[DirectPayment]] = None
    posted_date: Optional[datetime] = None
    refund_item_list: Optional[List[Dict[str, Any]]] = None

class GuaranteeClaimEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    seller_order_id: Optional[str] = None
    marketplace_name: Optional[str] = None
    posted_date: Optional[datetime] = None
    base_amount: Optional[Currency] = None
    tax_amount: Optional[Currency] = None
    fee_list: Optional[List[FeeComponent]] = None

class ChargebackEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    seller_order_id: Optional[str] = None
    marketplace_name: Optional[str] = None
    posted_date: Optional[datetime] = None
    base_amount: Optional[Currency] = None
    tax_amount: Optional[Currency] = None
    fee_list: Optional[List[FeeComponent]] = None

class PayWithAmazonEvent(BaseModel):
    seller_order_id: Optional[str] = None
    transaction_posted_date: Optional[datetime] = None
    business_object_type: Optional[str] = None
    sales_channel: Optional[str] = None
    charge: Optional[ChargeComponent] = None
    fee_list: Optional[List[FeeComponent]] = None
    payment_amount_type: Optional[str] = None
    amount_description: Optional[str] = None
    fulfillment_detail: Optional[str] = None

class ServiceProviderCreditEvent(BaseModel):
    provider_transaction_type: Optional[str] = None
    seller_order_id: Optional[str] = None
    marketplace_id: Optional[str] = None
    marketplace_country_code: Optional[str] = None
    seller_id: Optional[str] = None
    seller_store_name: Optional[str] = None
    provider_id: Optional[str] = None
    provider_store_name: Optional[str] = None

class RetrochargeEvent(BaseModel):
    retrocharge_event_type: Optional[str] = None
    amazon_order_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    base_amount: Optional[Currency] = None
    tax_amount: Optional[Currency] = None
    retrocharge_fee_list: Optional[List[FeeComponent]] = None

class RentalTransactionEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    rental_event_type: Optional[str] = None
    extension_length: Optional[int] = None
    posted_date: Optional[datetime] = None
    rental_charge_list: Optional[List[ChargeComponent]] = None
    rental_fee_list: Optional[List[FeeComponent]] = None
    marketplace_name: Optional[str] = None
    rental_initial_value: Optional[Currency] = None
    rental_reimbursement: Optional[Currency] = None
    rental_tax_withheld_list: Optional[List[Dict[str, Any]]] = None

class ProductAdsPaymentEvent(BaseModel):
    posted_date: Optional[datetime] = None
    transaction_type: Optional[str] = None
    invoice_id: Optional[str] = None
    base_value: Optional[Currency] = None
    tax_value: Optional[Currency] = None
    transaction_value: Optional[Currency] = None

class ServiceFeeEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    fee_reason: Optional[str] = None
    fee_list: Optional[List[FeeComponent]] = None
    seller_sku: Optional[str] = None
    fn_sku: Optional[str] = None
    fee_description: Optional[str] = None
    asin: Optional[str] = None

class DebtRecoveryEvent(BaseModel):
    debt_recovery_type: Optional[str] = None
    recovery_amount: Optional[Currency] = None
    over_payment_credit: Optional[Currency] = None
    debt_recovery_item_list: Optional[List[Dict[str, Any]]] = None
    charge_instrument_list: Optional[List[Dict[str, Any]]] = None

class LoanServicingEvent(BaseModel):
    loan_amount: Optional[Currency] = None
    source_business_event_type: Optional[str] = None

class AdjustmentEvent(BaseModel):
    adjustment_type: Optional[str] = None
    posted_date: Optional[datetime] = None
    adjustment_amount: Optional[Currency] = None
    adjustment_item_list: Optional[List[Dict[str, Any]]] = None

class SAFETReimbursementEvent(BaseModel):
    posted_date: Optional[datetime] = None
    safet_claim_id: Optional[str] = None
    reimbursed_amount: Optional[Currency] = None
    reason_code: Optional[str] = None
    safet_reimbursement_item_list: Optional[List[Dict[str, Any]]] = None

class SellerReviewEnrollmentPaymentEvent(BaseModel):
    posted_date: Optional[datetime] = None
    enrollment_id: Optional[str] = None
    parent_asin: Optional[str] = None
    fee_component: Optional[FeeComponent] = None
    charge_component: Optional[ChargeComponent] = None
    total_amount: Optional[Currency] = None

class FBALiquidationEvent(BaseModel):
    posted_date: Optional[datetime] = None
    original_removal_order_id: Optional[str] = None
    liquidation_proceeds_amount: Optional[Currency] = None
    liquidation_fee_amount: Optional[Currency] = None

class CouponPaymentEvent(BaseModel):
    posted_date: Optional[datetime] = None
    coupon_id: Optional[str] = None
    seller_coupon_description: Optional[str] = None
    clip_or_redemption_count: Optional[int] = None
    payment_event_id: Optional[str] = None

class ImagingServicesFeeEvent(BaseModel):
    imaging_request_billing_item_id: Optional[str] = None
    asin: Optional[str] = None
    posted_date: Optional[datetime] = None
    fee_list: Optional[List[FeeComponent]] = None

class NetworkComminglingTransactionEvent(BaseModel):
    transaction_type: Optional[str] = None
    posted_date: Optional[datetime] = None
    net_co_transaction_id: Optional[str] = None
    swap_reason: Optional[str] = None
    asin: Optional[str] = None
    marketplace_id: Optional[str] = None
    tax_exclusive_amount: Optional[Currency] = None
    tax_amount: Optional[Currency] = None

class AffordabilityExpenseEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    marketplace_id: Optional[str] = None
    transaction_type: Optional[str] = None
    base_expense: Optional[Currency] = None
    tax_type_cgst: Optional[Currency] = None
    tax_type_sgst: Optional[Currency] = None
    tax_type_igst: Optional[Currency] = None
    total_expense: Optional[Currency] = None

class AffordabilityExpenseReversalEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    marketplace_id: Optional[str] = None
    transaction_type: Optional[str] = None
    base_expense: Optional[Currency] = None
    tax_type_cgst: Optional[Currency] = None
    tax_type_sgst: Optional[Currency] = None
    tax_type_igst: Optional[Currency] = None
    total_expense: Optional[Currency] = None

class TrialShipmentEvent(BaseModel):
    amazon_order_id: Optional[str] = None
    financial_event_group_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    sku: Optional[str] = None
    fee_list: Optional[List[FeeComponent]] = None

class TDSReimbursementEvent(BaseModel):
    posted_date: Optional[datetime] = None
    tds_order_id: Optional[str] = None
    reimbursed_amount: Optional[Currency] = None

class AdhocDisbursementEvent(BaseModel):
    transaction_type: Optional[str] = None
    posted_date: Optional[datetime] = None
    transaction_amount: Optional[Currency] = None
    transaction_id: Optional[str] = None

class TaxWithholdingEvent(BaseModel):
    posted_date: Optional[datetime] = None
    base_amount: Optional[Currency] = None
    withheld_amount: Optional[Currency] = None
    tax_withholding_period: Optional[str] = None
    tax_withholding_description: Optional[str] = None
    tax_withholding_event_id: Optional[str] = None

class RemovalShipmentEvent(BaseModel):
    posted_date: Optional[datetime] = None
    order_id: Optional[str] = None
    transaction_type: Optional[str] = None
    removal_shipment_item_list: Optional[List[Dict[str, Any]]] = None

class CapacityReservationBillingEvent(BaseModel):
    transaction_type: Optional[str] = None
    posted_date: Optional[datetime] = None
    description: Optional[str] = None
    transaction_amount: Optional[Currency] = None

class FinancialEvents(BaseModel):
    shipment_event_list: Optional[List[ShipmentEvent]] = None
    refund_event_list: Optional[List[RefundEvent]] = None
    guarantee_claim_event_list: Optional[List[GuaranteeClaimEvent]] = None
    chargeback_event_list: Optional[List[ChargebackEvent]] = None
    pay_with_amazon_event_list: Optional[List[PayWithAmazonEvent]] = None
    service_provider_credit_event_list: Optional[List[ServiceProviderCreditEvent]] = None
    retrocharge_event_list: Optional[List[RetrochargeEvent]] = None
    rental_transaction_event_list: Optional[List[RentalTransactionEvent]] = None
    product_ads_payment_event_list: Optional[List[ProductAdsPaymentEvent]] = None
    service_fee_event_list: Optional[List[ServiceFeeEvent]] = None
    debt_recovery_event_list: Optional[List[DebtRecoveryEvent]] = None
    loan_servicing_event_list: Optional[List[LoanServicingEvent]] = None
    adjustment_event_list: Optional[List[AdjustmentEvent]] = None
    safet_reimbursement_event_list: Optional[List[SAFETReimbursementEvent]] = None
    seller_review_enrollment_payment_event_list: Optional[List[SellerReviewEnrollmentPaymentEvent]] = None
    fba_liquidation_event_list: Optional[List[FBALiquidationEvent]] = None
    coupon_payment_event_list: Optional[List[CouponPaymentEvent]] = None
    imaging_services_fee_event_list: Optional[List[ImagingServicesFeeEvent]] = None
    network_commingling_transaction_event_list: Optional[List[NetworkComminglingTransactionEvent]] = None
    affordability_expense_event_list: Optional[List[AffordabilityExpenseEvent]] = None
    affordability_expense_reversal_event_list: Optional[List[AffordabilityExpenseReversalEvent]] = None
    trial_shipment_event_list: Optional[List[TrialShipmentEvent]] = None
    tds_reimbursement_event_list: Optional[List[TDSReimbursementEvent]] = None
    adhoc_disbursement_event_list: Optional[List[AdhocDisbursementEvent]] = None
    tax_withholding_event_list: Optional[List[TaxWithholdingEvent]] = None
    removal_shipment_event_list: Optional[List[RemovalShipmentEvent]] = None
    capacity_reservation_billing_event_list: Optional[List[CapacityReservationBillingEvent]] = None

class ListFinancialEventsResponse(BaseModel):
    payload: FinancialEvents
    pagination: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None

class FinancialEventGroup(BaseModel):
    financial_event_group_id: Optional[str] = None
    processing_status: Optional[str] = None
    fund_transfer_status: Optional[str] = None
    original_total: Optional[Currency] = None
    converted_total: Optional[Currency] = None
    fund_transfer_date: Optional[datetime] = None
    trace_id: Optional[str] = None
    account_tail: Optional[str] = None
    beginning_balance: Optional[Currency] = None
    financial_event_group_start: Optional[datetime] = None
    financial_event_group_end: Optional[datetime] = None

class ListFinancialEventGroupsResponse(BaseModel):
    payload: List[FinancialEventGroup]
    pagination: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None

@router.get("/financialEventGroups", response_model=ListFinancialEventGroupsResponse)
async def list_financial_event_groups(
    max_results_per_page: Optional[int] = Query(100, description="The maximum number of results to return per page"),
    financial_event_group_started_before: Optional[datetime] = Query(None, description="A date used for selecting financial event groups that opened before (but not at) a specified date and time"),
    financial_event_group_started_after: Optional[datetime] = Query(None, description="A date used for selecting financial event groups that opened after (or at) a specified date and time"),
    next_token: Optional[str] = Query(None, description="A string token returned in the response of your previous request"),
    db: Session = Depends(get_db)
):
    """
    Returns financial event groups for a given date range.
    """
    
    try:
        # Mock financial event groups since we don't have a separate table for this
        financial_event_groups = [
            FinancialEventGroup(
                financial_event_group_id=f"GROUP_{i:05d}",
                processing_status="Closed",
                fund_transfer_status="Successful",
                original_total=Currency(currency_code="USD", currency_amount=1000.0 + i * 100),
                converted_total=Currency(currency_code="USD", currency_amount=1000.0 + i * 100),
                fund_transfer_date=datetime.now(),
                trace_id=f"TRACE_{i:010d}",
                account_tail="1234",
                beginning_balance=Currency(currency_code="USD", currency_amount=500.0),
                financial_event_group_start=datetime.now(),
                financial_event_group_end=datetime.now()
            ) for i in range(1, min(max_results_per_page + 1, 11))
        ]
        
        return ListFinancialEventGroupsResponse(
            payload=financial_event_groups,
            pagination={"next_token": None}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financialEventGroups/{event_group_id}/financialEvents", response_model=ListFinancialEventsResponse)
async def list_financial_events_by_group_id(
    event_group_id: str,
    max_results_per_page: Optional[int] = Query(100, description="The maximum number of results to return per page"),
    next_token: Optional[str] = Query(None, description="A string token returned in the response of your previous request"),
    db: Session = Depends(get_db)
):
    """
    Returns financial events for the specified financial event group.
    """
    
    try:
        # Get financial events from database
        financial_events = db.query(FinancialEvent).limit(max_results_per_page).all()
        
        shipment_events = []
        for event in financial_events:
            if event.financial_event_type == "Shipment":
                shipment_event = ShipmentEvent(
                    amazon_order_id=event.amazon_order_id,
                    seller_order_id=event.seller_order_id,
                    marketplace_name=event.marketplace_name,
                    posted_date=event.posted_date,
                    order_charge_list=[
                        ChargeComponent(
                            charge_type=charge.get("charge_type"),
                            charge_amount=Currency(
                                currency_code=charge.get("currency_code", "USD"),
                                currency_amount=charge.get("amount", 0.0)
                            )
                        ) for charge in event.order_charge_list or []
                    ],
                    shipment_fee_list=[
                        FeeComponent(
                            fee_type=fee.get("fee_type"),
                            fee_amount=Currency(
                                currency_code=fee.get("currency_code", "USD"),
                                currency_amount=fee.get("amount", 0.0)
                            )
                        ) for fee in event.shipment_fee_list or []
                    ]
                )
                shipment_events.append(shipment_event)
        
        financial_events_response = FinancialEvents(
            shipment_event_list=shipment_events if shipment_events else None
        )
        
        return ListFinancialEventsResponse(
            payload=financial_events_response,
            pagination={"next_token": None}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financialEvents", response_model=ListFinancialEventsResponse)
async def list_financial_events(
    max_results_per_page: Optional[int] = Query(100, description="The maximum number of results to return per page"),
    posted_after: Optional[datetime] = Query(None, description="A date used for selecting financial events posted after (or at) a specified date and time"),
    posted_before: Optional[datetime] = Query(None, description="A date used for selecting financial events posted before (but not at) a specified date and time"),
    next_token: Optional[str] = Query(None, description="A string token returned in the response of your previous request"),
    db: Session = Depends(get_db)
):
    """
    Returns financial events for the specified date range.
    """
    
    try:
        query = db.query(FinancialEvent)
        
        if posted_after:
            query = query.filter(FinancialEvent.posted_date >= posted_after)
        
        if posted_before:
            query = query.filter(FinancialEvent.posted_date < posted_before)
        
        financial_events = query.limit(max_results_per_page).all()
        
        shipment_events = []
        refund_events = []
        
        for event in financial_events:
            if event.financial_event_type == "Shipment":
                shipment_event = ShipmentEvent(
                    amazon_order_id=event.amazon_order_id,
                    seller_order_id=event.seller_order_id,
                    marketplace_name=event.marketplace_name,
                    posted_date=event.posted_date,
                    order_charge_list=[
                        ChargeComponent(
                            charge_type=charge.get("charge_type"),
                            charge_amount=Currency(
                                currency_code=charge.get("currency_code", "USD"),
                                currency_amount=charge.get("amount", 0.0)
                            )
                        ) for charge in event.order_charge_list or []
                    ],
                    shipment_fee_list=[
                        FeeComponent(
                            fee_type=fee.get("fee_type"),
                            fee_amount=Currency(
                                currency_code=fee.get("currency_code", "USD"),
                                currency_amount=fee.get("amount", 0.0)
                            )
                        ) for fee in event.shipment_fee_list or []
                    ]
                )
                shipment_events.append(shipment_event)
            elif event.financial_event_type == "Refund":
                refund_event = RefundEvent(
                    amazon_order_id=event.amazon_order_id,
                    seller_order_id=event.seller_order_id,
                    marketplace_name=event.marketplace_name,
                    posted_date=event.posted_date
                )
                refund_events.append(refund_event)
        
        financial_events_response = FinancialEvents(
            shipment_event_list=shipment_events if shipment_events else None,
            refund_event_list=refund_events if refund_events else None
        )
        
        return ListFinancialEventsResponse(
            payload=financial_events_response,
            pagination={"next_token": None}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
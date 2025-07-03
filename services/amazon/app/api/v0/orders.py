"""
Amazon SP-API Orders v0 endpoints
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.auth import get_amazon_user, require_amazon_scopes
from utils.response_formatter import amazon_formatter
from utils.rate_limiter import check_amazon_rate_limit

# Import local modules
from app.database.connection import get_db
from app.services.order_service import OrderService
from app.models.orders import OrderRequest, OrdersListResponse, OrderItemsListResponse

router = APIRouter()

@router.get("/orders")
async def get_orders(
    request: Request,
    db: Session = Depends(get_db),
    CreatedAfter: Optional[str] = Query(None, description="Orders created after this date"),
    CreatedBefore: Optional[str] = Query(None, description="Orders created before this date"),
    LastUpdatedAfter: Optional[str] = Query(None, description="Orders last updated after this date"),
    LastUpdatedBefore: Optional[str] = Query(None, description="Orders last updated before this date"),
    OrderStatuses: Optional[str] = Query(None, description="Comma-separated list of order statuses"),
    MarketplaceIds: Optional[str] = Query(None, description="Comma-separated list of marketplace IDs"),
    FulfillmentChannels: Optional[str] = Query(None, description="Comma-separated list of fulfillment channels"),
    PaymentMethods: Optional[str] = Query(None, description="Comma-separated list of payment methods"),
    BuyerEmail: Optional[str] = Query(None, description="Buyer email address"),
    SellerOrderId: Optional[str] = Query(None, description="Seller order ID"),
    MaxResultsPerPage: Optional[int] = Query(100, ge=1, le=100, description="Maximum results per page"),
    NextToken: Optional[str] = Query(None, description="Next token for pagination"),
    AmazonOrderIds: Optional[str] = Query(None, description="Comma-separated list of Amazon order IDs"),
    ActualFulfillmentSupplySourceId: Optional[str] = Query(None, description="Fulfillment supply source ID"),
    IsISPU: Optional[bool] = Query(None, description="Is in-store pickup"),
    StoreChainStoreId: Optional[str] = Query(None, description="Store chain store ID"),
    EarliestDeliveryDateBefore: Optional[str] = Query(None, description="Earliest delivery date before"),
    EarliestDeliveryDateAfter: Optional[str] = Query(None, description="Earliest delivery date after"),
    LatestDeliveryDateBefore: Optional[str] = Query(None, description="Latest delivery date before"),
    LatestDeliveryDateAfter: Optional[str] = Query(None, description="Latest delivery date after")
):
    """
    Get orders.
    
    Returns orders created or updated during the time frame that you specify.
    You can choose to get orders that are in any one of multiple order statuses.
    """
    
    # Parse filters
    filters = {}
    
    if CreatedAfter:
        filters["created_after"] = CreatedAfter
    if CreatedBefore:
        filters["created_before"] = CreatedBefore
    if LastUpdatedAfter:
        filters["last_updated_after"] = LastUpdatedAfter
    if LastUpdatedBefore:
        filters["last_updated_before"] = LastUpdatedBefore
    
    if OrderStatuses:
        filters["order_statuses"] = OrderStatuses.split(",")
    if MarketplaceIds:
        filters["marketplace_ids"] = MarketplaceIds.split(",")
    if FulfillmentChannels:
        filters["fulfillment_channels"] = FulfillmentChannels.split(",")
    if PaymentMethods:
        filters["payment_methods"] = PaymentMethods.split(",")
    
    if BuyerEmail:
        filters["buyer_email"] = BuyerEmail
    if SellerOrderId:
        filters["seller_order_id"] = SellerOrderId
    if AmazonOrderIds:
        filters["amazon_order_ids"] = AmazonOrderIds.split(",")
    
    if ActualFulfillmentSupplySourceId:
        filters["fulfillment_supply_source_id"] = ActualFulfillmentSupplySourceId
    if IsISPU is not None:
        filters["is_ispu"] = IsISPU
    if StoreChainStoreId:
        filters["store_chain_store_id"] = StoreChainStoreId
    
    if EarliestDeliveryDateBefore:
        filters["earliest_delivery_date_before"] = EarliestDeliveryDateBefore
    if EarliestDeliveryDateAfter:
        filters["earliest_delivery_date_after"] = EarliestDeliveryDateAfter
    if LatestDeliveryDateBefore:
        filters["latest_delivery_date_before"] = LatestDeliveryDateBefore
    if LatestDeliveryDateAfter:
        filters["latest_delivery_date_after"] = LatestDeliveryDateAfter
    
    # Get orders from service
    order_service = OrderService(db)
    result = await order_service.get_orders(
        filters=filters,
        max_results=MaxResultsPerPage,
        next_token=NextToken
    )
    
    # Format response according to Amazon SP-API format
    return amazon_formatter.orders_response(
        result["orders"],
        result.get("next_token")
    )

@router.get("/orders/{orderId}")
async def get_order(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get order details.
    
    Returns the order that you specify.
    """
    
    # Get order from service
    order_service = OrderService(db)
    order = await order_service.get_order_by_id(orderId)
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    # Format response
    return {
        "payload": order
    }

@router.get("/orders/{orderId}/orderItems")
async def get_order_items(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db),
    NextToken: Optional[str] = Query(None, description="Next token for pagination"),
    MaxResultsPerPage: Optional[int] = Query(100, ge=1, le=100, description="Maximum results per page")
):
    """
    Get order items.
    
    Returns detailed order item information for the order that you specify.
    """
    
    # Get order items from service
    order_service = OrderService(db)
    result = await order_service.get_order_items(
        orderId,
        max_results=MaxResultsPerPage,
        next_token=NextToken
    )
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    # Format response
    return amazon_formatter.order_items_response(
        result["order_items"],
        orderId,
        result.get("next_token")
    )

@router.get("/orders/{orderId}/buyerInfo")
async def get_order_buyer_info(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get buyer information.
    
    Returns buyer information for the order that you specify.
    """
    
    # Get buyer info from service
    order_service = OrderService(db)
    buyer_info = await order_service.get_order_buyer_info(orderId)
    
    if not buyer_info:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "BuyerEmail": buyer_info.get("buyer_email"),
            "BuyerName": buyer_info.get("buyer_name"),
            "BuyerCounty": buyer_info.get("buyer_county"),
            "BuyerTaxInfo": buyer_info.get("buyer_tax_info"),
            "PurchaseOrderNumber": buyer_info.get("purchase_order_number")
        }
    }

@router.get("/orders/{orderId}/address")
async def get_order_address(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get shipping address.
    
    Returns the shipping address for the order that you specify.
    """
    
    # Get shipping address from service
    order_service = OrderService(db)
    address = await order_service.get_order_address(orderId)
    
    if not address:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "ShippingAddress": address
        }
    }

@router.get("/orders/{orderId}/regulatedInfo")
async def get_order_regulated_info(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get regulated information.
    
    Returns regulated information for the order that you specify.
    """
    
    # Get regulated info from service
    order_service = OrderService(db)
    regulated_info = await order_service.get_order_regulated_info(orderId)
    
    if not regulated_info:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "RegulatedInformation": regulated_info.get("regulated_information", {}),
            "RequiresSignature": regulated_info.get("requires_signature", False)
        }
    }

@router.patch("/orders/{orderId}/shipment")
async def update_shipment_status(
    orderId: str,
    request: Request,
    shipment_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update shipment status.
    
    Updates (confirms) the status of the specified order.
    """
    
    # Update shipment status via service
    order_service = OrderService(db)
    result = await order_service.update_shipment_status(orderId, shipment_data)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "ConfirmationId": result.get("confirmation_id")
        }
    }

@router.patch("/orders/{orderId}/acknowledgment")
async def confirm_order(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Confirm order.
    
    Updates the acknowledgment status of the specified order.
    """
    
    # Confirm order via service
    order_service = OrderService(db)
    result = await order_service.confirm_order(orderId)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "Status": "Success"
        }
    }

@router.get("/orders/{orderId}/orderItems/buyerInfo")
async def get_order_items_buyer_info(
    orderId: str,
    request: Request,
    db: Session = Depends(get_db),
    NextToken: Optional[str] = Query(None, description="Next token for pagination"),
    MaxResultsPerPage: Optional[int] = Query(100, ge=1, le=100, description="Maximum results per page")
):
    """
    Get buyer information for order items.
    
    Returns buyer information for the order items in the order that you specify.
    """
    
    # Get order items buyer info from service
    order_service = OrderService(db)
    result = await order_service.get_order_items_buyer_info(
        orderId,
        max_results=MaxResultsPerPage,
        next_token=NextToken
    )
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "AmazonOrderId": orderId,
            "OrderItems": result["order_items"],
            "NextToken": result.get("next_token")
        }
    }

@router.post("/orders/{orderId}/shipment")
async def update_shipment_status(
    orderId: str,
    request: Request,
    shipment_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update shipment status.
    
    Updates the status of the specified order to ReadyForPickup or PickedUp.
    """
    
    # Update shipment status via service
    order_service = OrderService(db)
    result = await order_service.update_shipment_status(orderId, shipment_data)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    # Return 204 No Content for successful update
    return ""

@router.patch("/orders/{orderId}/regulatedInfo")
async def update_verification_status(
    orderId: str,
    request: Request,
    verification_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update verification status.
    
    Updates the verification status of the specified order.
    """
    
    # Update verification status via service
    order_service = OrderService(db)
    result = await order_service.update_verification_status(orderId, verification_data)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    # Return 204 No Content for successful update
    return ""

@router.post("/orders/{orderId}/shipmentConfirmation")
async def confirm_shipment(
    orderId: str,
    request: Request,
    confirmation_data: dict,
    db: Session = Depends(get_db)
):
    """
    Confirm shipment.
    
    Updates the shipment confirmation status for the specified order.
    """
    
    # Confirm shipment via service
    order_service = OrderService(db)
    result = await order_service.confirm_shipment(orderId, confirmation_data)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Order {orderId} not found"
            ).body.decode()
        )
    
    # Return 204 No Content for successful confirmation
    return ""
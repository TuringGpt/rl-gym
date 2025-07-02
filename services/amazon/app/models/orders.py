"""
Order-related Pydantic models for Amazon SP-API
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.base_models import AmazonBaseModel
from pydantic import Field

class Address(AmazonBaseModel):
    """Shipping address model."""
    Name: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    City: Optional[str] = None
    County: Optional[str] = None
    District: Optional[str] = None
    StateOrRegion: Optional[str] = None
    PostalCode: Optional[str] = None
    CountryCode: Optional[str] = None
    Phone: Optional[str] = None

class Money(AmazonBaseModel):
    """Money amount model."""
    CurrencyCode: str = Field(default="USD")
    Amount: str = Field(description="Monetary amount as string")

class OrderItem(AmazonBaseModel):
    """Order item model."""
    ASIN: Optional[str] = None
    SellerSKU: Optional[str] = None
    OrderItemId: str
    Title: Optional[str] = None
    QuantityOrdered: int
    QuantityShipped: Optional[int] = 0
    ProductInfo: Optional[dict] = None
    PointsGranted: Optional[dict] = None
    ItemPrice: Optional[Money] = None
    ShippingPrice: Optional[Money] = None
    ItemTax: Optional[Money] = None
    ShippingTax: Optional[Money] = None
    ShippingDiscount: Optional[Money] = None
    ShippingDiscountTax: Optional[Money] = None
    PromotionDiscount: Optional[Money] = None
    PromotionDiscountTax: Optional[Money] = None
    ConditionNote: Optional[str] = None
    ConditionId: Optional[str] = None
    ConditionSubtypeId: Optional[str] = None
    ScheduledDeliveryStartDate: Optional[str] = None
    ScheduledDeliveryEndDate: Optional[str] = None
    PriceDesignation: Optional[str] = None
    TaxCollection: Optional[dict] = None
    SerialNumberRequired: Optional[bool] = False
    IsTransparency: Optional[bool] = False

class Order(AmazonBaseModel):
    """Order model."""
    AmazonOrderId: str
    SellerOrderId: Optional[str] = None
    PurchaseDate: str
    LastUpdateDate: str
    OrderStatus: str
    FulfillmentChannel: Optional[str] = "MFN"
    SalesChannel: Optional[str] = None
    OrderChannel: Optional[str] = None
    ShipServiceLevel: Optional[str] = None
    OrderTotal: Optional[Money] = None
    NumberOfItemsShipped: Optional[int] = 0
    NumberOfItemsUnshipped: Optional[int] = 0
    PaymentExecutionDetail: Optional[List[dict]] = None
    PaymentMethod: Optional[str] = None
    PaymentMethodDetails: Optional[List[str]] = None
    MarketplaceId: Optional[str] = None
    ShipmentServiceLevelCategory: Optional[str] = None
    EasyShipShipmentStatus: Optional[str] = None
    CbaDisplayableShippingLabel: Optional[str] = None
    OrderType: Optional[str] = "StandardOrder"
    EarliestShipDate: Optional[str] = None
    LatestShipDate: Optional[str] = None
    EarliestDeliveryDate: Optional[str] = None
    LatestDeliveryDate: Optional[str] = None
    IsBusinessOrder: Optional[bool] = False
    IsPrime: Optional[bool] = False
    IsPremiumOrder: Optional[bool] = False
    IsGlobalExpressEnabled: Optional[bool] = False
    ReplacedOrderId: Optional[str] = None
    IsReplacementOrder: Optional[bool] = False
    PromiseResponseDueDate: Optional[str] = None
    IsEstimatedShipDateSet: Optional[bool] = False
    IsSoldByAB: Optional[bool] = False
    IsIBA: Optional[bool] = False
    DefaultShipFromLocationAddress: Optional[Address] = None
    BuyerInvoicePreference: Optional[str] = None
    BuyerTaxInformation: Optional[dict] = None
    FulfillmentInstruction: Optional[dict] = None
    IsISPU: Optional[bool] = False
    IsAccessPointOrder: Optional[bool] = False
    MarketplaceTaxInfo: Optional[dict] = None
    SellerDisplayName: Optional[str] = None
    ShippingAddress: Optional[Address] = None
    BuyerInfo: Optional[dict] = None
    AutomatedShippingSettings: Optional[dict] = None
    HasAutomatedShippingSettings: Optional[bool] = False
    ElectronicInvoiceStatus: Optional[str] = None

class OrdersListResponse(AmazonBaseModel):
    """Orders list response."""
    payload: dict = Field(description="Orders response payload")

class OrderItemsListResponse(AmazonBaseModel):
    """Order items list response."""
    payload: dict = Field(description="Order items response payload")

# Request models
class OrderRequest(AmazonBaseModel):
    """Order request parameters."""
    CreatedAfter: Optional[str] = None
    CreatedBefore: Optional[str] = None
    LastUpdatedAfter: Optional[str] = None
    LastUpdatedBefore: Optional[str] = None
    OrderStatuses: Optional[List[str]] = None
    MarketplaceIds: Optional[List[str]] = None
    FulfillmentChannels: Optional[List[str]] = None
    PaymentMethods: Optional[List[str]] = None
    BuyerEmail: Optional[str] = None
    SellerOrderId: Optional[str] = None
    MaxResultsPerPage: Optional[int] = Field(default=100, ge=1, le=100)
    NextToken: Optional[str] = None
    AmazonOrderIds: Optional[List[str]] = None
    ActualFulfillmentSupplySourceId: Optional[str] = None
    IsISPU: Optional[bool] = None
    StoreChainStoreId: Optional[str] = None
    EarliestDeliveryDateBefore: Optional[str] = None
    EarliestDeliveryDateAfter: Optional[str] = None
    LatestDeliveryDateBefore: Optional[str] = None
    LatestDeliveryDateAfter: Optional[str] = None

# Response models
class OrderResponse(AmazonBaseModel):
    """Single order response."""
    payload: Order

class OrderItemResponse(AmazonBaseModel):
    """Single order item response."""
    payload: OrderItem
"""
Order service for Amazon SP-API Mock
Handles order-related business logic and database operations
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from app.database.schemas import Order, OrderItem, Seller

class OrderService:
    """Service for handling order operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_orders(self, filters: Dict[str, Any], max_results: int = 100, 
                        next_token: str = None) -> Dict[str, Any]:
        """Get orders with filtering and pagination."""
        
        query = self.db.query(Order)
        
        # Apply filters
        if "created_after" in filters:
            query = query.filter(Order.purchase_date >= filters["created_after"])
        if "created_before" in filters:
            query = query.filter(Order.purchase_date <= filters["created_before"])
        if "last_updated_after" in filters:
            query = query.filter(Order.last_update_date >= filters["last_updated_after"])
        if "last_updated_before" in filters:
            query = query.filter(Order.last_update_date <= filters["last_updated_before"])
        
        if "order_statuses" in filters:
            query = query.filter(Order.order_status.in_(filters["order_statuses"]))
        if "marketplace_ids" in filters:
            query = query.filter(Order.marketplace_id.in_(filters["marketplace_ids"]))
        if "buyer_email" in filters:
            query = query.filter(Order.buyer_email == filters["buyer_email"])
        if "seller_order_id" in filters:
            query = query.filter(Order.seller_order_id == filters["seller_order_id"])
        if "amazon_order_ids" in filters:
            query = query.filter(Order.amazon_order_id.in_(filters["amazon_order_ids"]))
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        orders_query = query.offset(offset).limit(max_results)
        orders = orders_query.all()
        
        # Convert to dict format
        orders_data = []
        for order in orders:
            order_dict = self._format_order(order)
            orders_data.append(order_dict)
        
        # Calculate next token
        new_next_token = None
        if offset + max_results < total_count:
            new_next_token = str(offset + max_results)
        
        return {
            "orders": orders_data,
            "next_token": new_next_token,
            "total_count": total_count
        }
    
    async def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific order by ID."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        return self._format_order(order)
    
    async def get_order_items(self, order_id: str, max_results: int = 100,
                            next_token: str = None) -> Optional[Dict[str, Any]]:
        """Get order items for a specific order."""
        
        # First verify the order exists
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        if not order:
            return None
        
        # Get order items
        query = self.db.query(OrderItem).filter(OrderItem.amazon_order_id == order_id)
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        total_count = query.count()
        items_query = query.offset(offset).limit(max_results)
        items = items_query.all()
        
        # Convert to dict format
        items_data = []
        for item in items:
            item_dict = self._format_order_item(item)
            items_data.append(item_dict)
        
        # Calculate next token
        new_next_token = None
        if offset + max_results < total_count:
            new_next_token = str(offset + max_results)
        
        return {
            "order_items": items_data,
            "next_token": new_next_token,
            "total_count": total_count
        }
    
    async def get_order_buyer_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get buyer information for an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        return {
            "buyer_email": order.buyer_email,
            "buyer_name": order.shipping_address_name,
            "buyer_county": None,  # Mock data doesn't include this
            "buyer_tax_info": None,  # Mock data doesn't include this
            "purchase_order_number": order.seller_order_id
        }
    
    async def get_order_address(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get shipping address for an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        return {
            "Name": order.shipping_address_name,
            "AddressLine1": order.shipping_address_line1,
            "City": order.shipping_address_city,
            "StateOrRegion": order.shipping_address_state,
            "PostalCode": order.shipping_address_postal_code,
            "CountryCode": order.shipping_address_country
        }
    
    async def get_order_regulated_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get regulated information for an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        # Mock regulated information
        return {
            "regulated_information": {},
            "requires_signature": False
        }
    
    async def update_shipment_status(self, order_id: str, shipment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update shipment status for an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        # Update order status based on shipment data
        if shipment_data.get("status") == "shipped":
            order.order_status = "Shipped"
            order.last_update_date = datetime.utcnow()
            self.db.commit()
        
        return {
            "confirmation_id": f"conf_{order_id}_{int(datetime.utcnow().timestamp())}"
        }
    
    async def confirm_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Confirm/acknowledge an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        # Update order status
        if order.order_status == "Pending":
            order.order_status = "Unshipped"
            order.last_update_date = datetime.utcnow()
            self.db.commit()
        
        return {
            "status": "confirmed",
            "order_id": order_id
        }
    
    def _format_order(self, order: Order) -> Dict[str, Any]:
        """Format order for API response."""
        return {
            "AmazonOrderId": order.amazon_order_id,
            "SellerOrderId": order.seller_order_id,
            "PurchaseDate": order.purchase_date.isoformat() + "Z",
            "LastUpdateDate": order.last_update_date.isoformat() + "Z",
            "OrderStatus": order.order_status,
            "FulfillmentChannel": "MFN",  # Mock default
            "SalesChannel": "Amazon.com",  # Mock default
            "OrderChannel": "Amazon.com",  # Mock default
            "ShipServiceLevel": "Standard",  # Mock default
            "OrderTotal": {
                "CurrencyCode": order.currency_code or "USD",
                "Amount": str(order.order_total or 0)
            } if order.order_total else None,
            "NumberOfItemsShipped": 0,  # Would need to calculate from order items
            "NumberOfItemsUnshipped": 0,  # Would need to calculate from order items
            "MarketplaceId": order.marketplace_id,
            "ShipmentServiceLevelCategory": "Standard",
            "OrderType": "StandardOrder",
            "EarliestShipDate": order.purchase_date.isoformat() + "Z",
            "LatestShipDate": (order.purchase_date + timedelta(days=2)).isoformat() + "Z",
            "EarliestDeliveryDate": (order.purchase_date + timedelta(days=3)).isoformat() + "Z",
            "LatestDeliveryDate": (order.purchase_date + timedelta(days=7)).isoformat() + "Z",
            "IsBusinessOrder": False,
            "IsPrime": False,
            "IsPremiumOrder": False,
            "IsGlobalExpressEnabled": False,
            "IsReplacementOrder": False,
            "IsEstimatedShipDateSet": False,
            "IsSoldByAB": False,
            "IsIBA": False,
            "IsISPU": False,
            "IsAccessPointOrder": False,
            "HasAutomatedShippingSettings": False,
            "ShippingAddress": {
                "Name": order.shipping_address_name,
                "AddressLine1": order.shipping_address_line1,
                "City": order.shipping_address_city,
                "StateOrRegion": order.shipping_address_state,
                "PostalCode": order.shipping_address_postal_code,
                "CountryCode": order.shipping_address_country
            } if order.shipping_address_name else None
        }
    
    def _format_order_item(self, item: OrderItem) -> Dict[str, Any]:
        """Format order item for API response."""
        return {
            "ASIN": item.asin,
            "SellerSKU": item.seller_sku,
            "OrderItemId": item.order_item_id,
            "Title": item.title,
            "QuantityOrdered": item.quantity_ordered,
            "QuantityShipped": item.quantity_shipped or 0,
            "ItemPrice": {
                "CurrencyCode": "USD",
                "Amount": str(item.item_price or 0)
            } if item.item_price else None,
            "ShippingPrice": {
                "CurrencyCode": "USD", 
                "Amount": str(item.shipping_price or 0)
            } if item.shipping_price else None,
            "ItemTax": {
                "CurrencyCode": "USD",
                "Amount": str(item.item_tax or 0)
            } if item.item_tax else None,
            "ShippingTax": {
                "CurrencyCode": "USD",
                "Amount": str(item.shipping_tax or 0)
            } if item.shipping_tax else None,
            "ConditionId": "New",
            "ConditionSubtypeId": "New",
            "IsTransparency": False,
            "SerialNumberRequired": False,
            "ProductInfo": {
                "NumberOfItems": 1
            }
        }
    
    async def get_order_items_buyer_info(self, order_id: str, max_results: int = 100,
                                       next_token: str = None) -> Optional[Dict[str, Any]]:
        """Get buyer information for order items."""
        
        # First verify the order exists
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        if not order:
            return None
        
        # Get order items
        query = self.db.query(OrderItem).filter(OrderItem.amazon_order_id == order_id)
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        total_count = query.count()
        items_query = query.offset(offset).limit(max_results)
        items = items_query.all()
        
        # Convert to dict format with buyer info
        items_data = []
        for item in items:
            item_dict = {
                "OrderItemId": item.order_item_id,
                "BuyerCustomizedInfo": {
                    "CustomizedURL": "https://zme-caps.amazon.com/t/bR6qHkzSOxuB/J8nbWhze0Bd3DkajkOdY-XQbWkFralegp2sr_QZiKEE/1"
                },
                "GiftMessageText": "For you!",
                "GiftWrapPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "1.99"
                },
                "GiftWrapLevel": "Classic"
            }
            items_data.append(item_dict)
        
        # Calculate next token
        new_next_token = None
        if offset + max_results < total_count:
            new_next_token = str(offset + max_results)
        
        return {
            "order_items": items_data,
            "next_token": new_next_token,
            "total_count": total_count
        }
    
    async def update_verification_status(self, order_id: str, verification_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update verification status for regulated information."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        # Mock verification update - in reality this would update verification status
        order.last_update_date = datetime.utcnow()
        self.db.commit()
        
        return {
            "status": "updated",
            "order_id": order_id,
            "verification_status": verification_data.get("status", "verified")
        }
    
    async def confirm_shipment(self, order_id: str, confirmation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Confirm shipment for an order."""
        order = self.db.query(Order).filter(Order.amazon_order_id == order_id).first()
        
        if not order:
            return None
        
        # Update order status to shipped
        order.order_status = "Shipped"
        order.last_update_date = datetime.utcnow()
        self.db.commit()
        
        return {
            "status": "confirmed",
            "order_id": order_id,
            "confirmation_id": f"ship_conf_{order_id}_{int(datetime.utcnow().timestamp())}"
        }
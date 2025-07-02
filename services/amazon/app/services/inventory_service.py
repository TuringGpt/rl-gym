"""
Inventory service for Amazon SP-API Mock
Handles inventory-related business logic and database operations
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from app.database.schemas import Inventory

class InventoryService:
    """Service for handling inventory operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_inventory_summaries(self, marketplace_ids: List[str], 
                                    filters: Dict[str, Any], 
                                    next_token: str = None,
                                    max_results: int = 50) -> Dict[str, Any]:
        """Get inventory summaries."""
        
        query = self.db.query(Inventory)
        
        # Apply filters
        if "seller_skus" in filters:
            query = query.filter(Inventory.seller_sku.in_(filters["seller_skus"]))
        if "start_date" in filters:
            query = query.filter(Inventory.last_updated_time >= filters["start_date"])
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        total_count = query.count()
        inventory_query = query.offset(offset).limit(max_results)
        inventory_items = inventory_query.all()
        
        # Convert to summary format
        summaries = []
        for item in inventory_items:
            summary = self._format_inventory_summary(item)
            summaries.append(summary)
        
        # Calculate next token
        new_next_token = None
        if offset + max_results < total_count:
            new_next_token = str(offset + max_results)
        
        return {
            "summaries": summaries,
            "next_token": new_next_token,
            "total_count": total_count
        }
    
    async def get_inventory_details(self, marketplace_ids: List[str],
                                  filters: Dict[str, Any],
                                  next_token: str = None,
                                  max_results: int = 50) -> Dict[str, Any]:
        """Get detailed inventory information."""
        
        query = self.db.query(Inventory)
        
        # Apply filters
        if "seller_skus" in filters:
            query = query.filter(Inventory.seller_sku.in_(filters["seller_skus"]))
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        total_count = query.count()
        inventory_query = query.offset(offset).limit(max_results)
        inventory_items = inventory_query.all()
        
        # Convert to detailed format
        details = []
        for item in inventory_items:
            detail = self._format_inventory_details(item)
            details.append(detail)
        
        # Calculate next token
        new_next_token = None
        if offset + max_results < total_count:
            new_next_token = str(offset + max_results)
        
        return {
            "details": details,
            "next_token": new_next_token,
            "total_count": total_count
        }
    
    async def get_inventory_by_sku(self, seller_sku: str) -> Optional[Dict[str, Any]]:
        """Get inventory details for a specific SKU."""
        inventory = self.db.query(Inventory).filter(Inventory.seller_sku == seller_sku).first()
        
        if not inventory:
            return None
        
        return self._format_inventory_details(inventory)
    
    async def update_inventory(self, seller_sku: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update inventory for a specific SKU."""
        inventory = self.db.query(Inventory).filter(Inventory.seller_sku == seller_sku).first()
        
        if not inventory:
            return None
        
        # Update fields
        for field, value in updates.items():
            if hasattr(inventory, field):
                setattr(inventory, field, value)
        
        inventory.last_updated_time = datetime.utcnow()
        self.db.commit()
        
        return self._format_inventory_details(inventory)
    
    def _format_inventory_summary(self, inventory: Inventory) -> Dict[str, Any]:
        """Format inventory for summary response."""
        return {
            "asin": inventory.asin,
            "fnSku": inventory.fnsku,
            "sellerSku": inventory.seller_sku,
            "condition": inventory.condition_type,
            "inventoryDetails": {
                "fulfillableQuantity": inventory.fulfillable_quantity or 0,
                "inboundWorkingQuantity": inventory.inbound_working_quantity or 0,
                "inboundShippedQuantity": inventory.inbound_shipped_quantity or 0,
                "inboundReceivingQuantity": inventory.inbound_receiving_quantity or 0,
                "reservedQuantity": {
                    "totalReservedQuantity": inventory.reserved_quantity or 0,
                    "pendingCustomerOrderQuantity": 0,
                    "pendingTransshipmentQuantity": 0,
                    "fcProcessingQuantity": 0
                },
                "unfulfillableQuantity": inventory.unfulfillable_quantity or 0
            },
            "lastUpdatedTime": inventory.last_updated_time.isoformat() + "Z" if inventory.last_updated_time else None,
            "productName": f"Product for {inventory.seller_sku}",  # Mock product name
            "totalQuantity": inventory.total_quantity or 0
        }
    
    def _format_inventory_details(self, inventory: Inventory) -> Dict[str, Any]:
        """Format inventory for detailed response."""
        return {
            "asin": inventory.asin,
            "fnSku": inventory.fnsku,
            "sellerSku": inventory.seller_sku,
            "condition": inventory.condition_type,
            "totalQuantity": inventory.total_quantity or 0,
            "fulfillableQuantity": inventory.fulfillable_quantity or 0,
            "inboundWorkingQuantity": inventory.inbound_working_quantity or 0,
            "inboundShippedQuantity": inventory.inbound_shipped_quantity or 0,
            "inboundReceivingQuantity": inventory.inbound_receiving_quantity or 0,
            "reservedQuantity": {
                "totalReservedQuantity": inventory.reserved_quantity or 0,
                "pendingCustomerOrderQuantity": 0,
                "pendingTransshipmentQuantity": 0,
                "fcProcessingQuantity": 0
            },
            "unfulfillableQuantity": inventory.unfulfillable_quantity or 0,
            "lastUpdatedTime": inventory.last_updated_time.isoformat() + "Z" if inventory.last_updated_time else None,
            "productName": f"Product for {inventory.seller_sku}",  # Mock product name
            "researchingQuantity": {
                "totalResearchingQuantity": 0,
                "researchingQuantityBreakdown": []
            }
        }
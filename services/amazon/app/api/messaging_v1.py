"""
Amazon Messaging API v1
Based on: https://developer-docs.amazon.com/sp-api/docs/messaging-api-v1-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import MessagingAction, Message, BuyerAttributes, Order
import sys
from pathlib import Path as FilePath
from datetime import datetime

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/messaging/v1", tags=["Messaging"])

# Request Models
class MessageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    subject: Optional[str] = None
    body: str
    marketplace_ids: List[str] = Field(..., alias="marketplaceIds")

# Response Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: str

class ErrorResponse(BaseModel):
    errors: List[ErrorDetail]

class LinkItem(BaseModel):
    href: str
    name: Optional[str] = None

class ActionLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    schema_link: Optional[LinkItem] = Field(None, alias="schema")
    self: LinkItem

class EmbeddedAction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    links: ActionLinks = Field(..., alias="_links")

class MessagingLinks(BaseModel):
    actions: Optional[List[LinkItem]] = None
    self: LinkItem

class MessagingEmbedded(BaseModel):
    actions: List[EmbeddedAction]

class GetMessagingActionsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    links: MessagingLinks = Field(..., alias="_links")
    embedded: MessagingEmbedded = Field(..., alias="_embedded")

class BuyerInfo(BaseModel):
    locale: str

class GetAttributesResponse(BaseModel):
    buyer: BuyerInfo

# Service class for business logic
class MessagingService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_available_actions_for_order(self, amazon_order_id: str, marketplace_ids: List[str]) -> GetMessagingActionsResponse:
        """Get available messaging actions for an order."""
        
        # Check if order exists
        order = self.db.query(Order).filter(Order.amazon_order_id == amazon_order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get available actions for this order
        actions = self.db.query(MessagingAction).filter(
            MessagingAction.amazon_order_id == amazon_order_id,
            MessagingAction.is_available == True,
            MessagingAction.marketplace_id.in_(marketplace_ids)
        ).all()
        
        # Build HAL+JSON response
        action_links = []
        embedded_actions = []
        
        for action in actions:
            marketplace_param = f"marketplaceIds={marketplace_ids[0]}"
            action_href = f"/messaging/v1/orders/{amazon_order_id}/messages/{action.action_name}?{marketplace_param}"
            
            # Add to action links
            action_links.append(LinkItem(
                href=action_href,
                name=action.action_name
            ))
            
            # Add to embedded actions
            embedded_actions.append(EmbeddedAction(
                links=ActionLinks(
                    schema_link=LinkItem(
                        href=f"/messaging/v1/orders/{amazon_order_id}/messages/{action.action_name}/schema",
                        name=action.action_name
                    ),
                    self=LinkItem(
                        href=action_href,
                        name=action.action_name
                    )
                )
            ))
        
        self_href = f"/messaging/v1/orders/{amazon_order_id}?marketplaceIds={marketplace_ids[0]}"
        
        return GetMessagingActionsResponse(
            links=MessagingLinks(
                actions=action_links,
                self=LinkItem(href=self_href)
            ),
            embedded=MessagingEmbedded(
                actions=embedded_actions
            )
        )
    
    async def get_buyer_attributes(self, amazon_order_id: str, marketplace_ids: List[str]) -> GetAttributesResponse:
        """Get buyer attributes for an order."""
        
        # Check if order exists
        order = self.db.query(Order).filter(Order.amazon_order_id == amazon_order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get buyer attributes
        buyer_attrs = self.db.query(BuyerAttributes).filter(
            BuyerAttributes.amazon_order_id == amazon_order_id
        ).first()
        
        if not buyer_attrs:
            # Default attributes if none found
            return GetAttributesResponse(
                buyer=BuyerInfo(locale="en-US")
            )
        
        return GetAttributesResponse(
            buyer=BuyerInfo(locale=buyer_attrs.locale)
        )
    
    async def send_message(self, amazon_order_id: str, message_type: str, 
                          request: MessageRequest) -> Optional[ErrorResponse]:
        """Send a message to buyer."""
        
        # Check if order exists
        order = self.db.query(Order).filter(Order.amazon_order_id == amazon_order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if action is available
        action = self.db.query(MessagingAction).filter(
            MessagingAction.amazon_order_id == amazon_order_id,
            MessagingAction.action_name == message_type,
            MessagingAction.is_available == True,
            MessagingAction.marketplace_id.in_(request.marketplace_ids)
        ).first()
        
        if not action:
            return ErrorResponse(
                errors=[
                    ErrorDetail(
                        code="InvalidInput",
                        message=f"Message type '{message_type}' is not available for this order",
                        details=f"Order {amazon_order_id} does not support {message_type} messaging"
                    )
                ]
            )
        
        try:
            # Create message record
            message = Message(
                amazon_order_id=amazon_order_id,
                message_type=message_type,
                subject=request.subject or f"Message regarding your order {amazon_order_id}",
                body=request.body,
                status="sent",
                sent_at=datetime.utcnow()
            )
            
            self.db.add(message)
            self.db.commit()
            
            # Mark action as used (optional - can be left available for multiple messages)
            # action.is_available = False
            # self.db.commit()
            
            return None  # Success - no response body
            
        except Exception as e:
            self.db.rollback()
            return ErrorResponse(
                errors=[
                    ErrorDetail(
                        code="InternalError",
                        message="Failed to send message",
                        details=str(e)
                    )
                ]
            )

@router.get("/orders/{amazon_order_id}")
async def get_messaging_actions_for_order(
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    marketplace_ids: List[str] = Query(..., alias="marketplaceIds", description="A marketplace identifier"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of message types that are available for an order.
    """
    try:
        service = MessagingService(db)
        response = await service.get_available_actions_for_order(amazon_order_id, marketplace_ids)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{amazon_order_id}/attributes", response_model=GetAttributesResponse)
async def get_attributes(
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    marketplace_ids: List[str] = Query(..., alias="marketplaceIds", description="A marketplace identifier"),
    db: Session = Depends(get_db)
):
    """
    Returns buyer attributes required to send messages.
    """
    try:
        service = MessagingService(db)
        response = await service.get_buyer_attributes(amazon_order_id, marketplace_ids)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Message creation endpoints
@router.post("/orders/{amazon_order_id}/messages/confirmCustomizationDetails")
async def confirm_customization_details(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message to confirm customization details such as size, color, etc.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "confirmCustomizationDetails", request)
        
        if error_response:
            return error_response
        
        return {}  # Success response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/confirmDeliveryDetails")
async def create_confirm_delivery_details(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message to confirm delivery details.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "confirmDeliveryDetails", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/legalDisclosure")
async def create_legal_disclosure(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message providing legal disclosure information.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "legalDisclosure", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/negativeFeedbackRemoval")
async def create_negative_feedback_removal(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message to request removal of negative feedback.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "negativeFeedbackRemoval", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/confirmOrderDetails")
async def create_confirm_order_details(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message to confirm order details.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "confirmOrderDetails", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/confirmServiceDetails")
async def create_confirm_service_details(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message to confirm service details.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "confirmServiceDetails", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/amazonMotors")
async def create_amazon_motors(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message related to Amazon Motors.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "amazonMotors", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/warranty")
async def create_warranty(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a warranty-related message.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "warranty", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/digitalAccessKey")
async def create_digital_access_key(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a digital access key to the buyer.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "digitalAccessKey", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/unexpectedProblem")
async def create_unexpected_problem(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends a message about an unexpected problem.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "unexpectedProblem", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{amazon_order_id}/messages/invoice")
async def send_invoice(
    request: MessageRequest,
    amazon_order_id: str = Path(..., description="An Amazon order identifier"),
    db: Session = Depends(get_db)
):
    """
    Sends an invoice to the buyer.
    """
    try:
        service = MessagingService(db)
        error_response = await service.send_message(amazon_order_id, "invoice", request)
        
        if error_response:
            return error_response
            
        return {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
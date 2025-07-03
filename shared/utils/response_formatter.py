"""
Response formatter utilities for API Mock Gym services.
Provides consistent response formatting matching real API patterns.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging
import os
import json

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Base response formatter for all services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.include_debug = os.getenv("ENVIRONMENT", "development") == "development"
    
    def success_response(self, data: Any, status_code: int = 200, headers: Dict[str, str] = None) -> JSONResponse:
        """Format successful response."""
        response_data = {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if self.include_debug:
            response_data["debug"] = {
                "service": self.service_name,
                "status_code": status_code
            }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def error_response(self, error: str, message: str, status_code: int = 400, 
                      details: Dict[str, Any] = None, headers: Dict[str, str] = None) -> JSONResponse:
        """Format error response."""
        response_data = {
            "success": False,
            "error": {
                "code": error,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        if details:
            response_data["error"]["details"] = details
        
        if self.include_debug:
            response_data["debug"] = {
                "service": self.service_name,
                "status_code": status_code
            }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )

class AmazonResponseFormatter(ResponseFormatter):
    """Amazon Selling Partner API response formatter."""
    
    def __init__(self):
        super().__init__("amazon")
    
    def success_response(self, data: Any, status_code: int = 200, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Amazon SP-API successful response."""
        # Amazon SP-API uses a different format - no wrapper, direct data
        return JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def error_response(self, error: str, message: str, status_code: int = 400,
                      details: Dict[str, Any] = None, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Amazon SP-API error response."""
        response_data = {
            "errors": [
                {
                    "code": error,
                    "message": message,
                    "details": details or {}
                }
            ]
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def paginated_response(self, items: List[Any], next_token: str = None, 
                          total_count: int = None) -> Dict[str, Any]:
        """Format paginated response for Amazon SP-API."""
        response = {
            "payload": items
        }
        
        if next_token:
            response["pagination"] = {
                "NextToken": next_token
            }
        
        if total_count is not None:
            response["pagination"] = response.get("pagination", {})
            response["pagination"]["TotalCount"] = total_count
        
        return response
    
    def orders_response(self, orders: List[Dict[str, Any]], next_token: str = None) -> Dict[str, Any]:
        """Format orders API response."""
        return {
            "payload": {
                "Orders": orders,
                "NextToken": next_token,
                "CreatedBefore": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def order_items_response(self, order_items: List[Dict[str, Any]], 
                           amazon_order_id: str, next_token: str = None) -> Dict[str, Any]:
        """Format order items API response."""
        return {
            "payload": {
                "AmazonOrderId": amazon_order_id,
                "OrderItems": order_items,
                "NextToken": next_token
            }
        }
    
    def inventory_response(self, summaries: List[Dict[str, Any]], 
                          next_token: str = None) -> Dict[str, Any]:
        """Format inventory API response."""
        return {
            "payload": {
                "inventorySummaries": summaries,
                "pagination": {
                    "nextToken": next_token
                } if next_token else None
            }
        }
    
    def listings_response(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Format listings API response."""
        return {
            "sku": listing.get("seller_sku"),
            "status": listing.get("status", "ACTIVE"),
            "submissionId": f"submission-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "issues": []
        }
    
    def reports_response(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Format reports API response."""
        return {
            "payload": {
                "reportId": report.get("report_id"),
                "reportType": report.get("report_type"),
                "processingStatus": report.get("processing_status", "IN_PROGRESS"),
                "createdTime": report.get("created_time"),
                "processingStartTime": report.get("processing_start_time"),
                "processingEndTime": report.get("processing_end_time"),
                "reportDocumentId": report.get("report_document_url")
            }
        }

class SlackResponseFormatter(ResponseFormatter):
    """Slack API response formatter."""
    
    def __init__(self):
        super().__init__("slack")
    
    def success_response(self, data: Any, status_code: int = 200, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Slack API successful response."""
        response_data = {
            "ok": True,
            **data
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def error_response(self, error: str, message: str = None, status_code: int = 400, 
                      headers: Dict[str, str] = None) -> JSONResponse:
        """Format Slack API error response."""
        response_data = {
            "ok": False,
            "error": error
        }
        
        if message:
            response_data["message"] = message
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )

class StripeResponseFormatter(ResponseFormatter):
    """Stripe API response formatter."""
    
    def __init__(self):
        super().__init__("stripe")
    
    def success_response(self, data: Any, status_code: int = 200, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Stripe API successful response."""
        # Stripe returns data directly, no wrapper
        return JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def error_response(self, error_type: str, message: str, status_code: int = 400, 
                      param: str = None, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Stripe API error response."""
        response_data = {
            "error": {
                "type": error_type,
                "message": message,
                "request_id": f"req_mock_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            }
        }
        
        if param:
            response_data["error"]["param"] = param
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def list_response(self, data: List[Any], has_more: bool = False, 
                     url: str = "/v1/charges") -> Dict[str, Any]:
        """Format Stripe list response."""
        return {
            "object": "list",
            "data": data,
            "has_more": has_more,
            "url": url
        }

class NotionResponseFormatter(ResponseFormatter):
    """Notion API response formatter."""
    
    def __init__(self):
        super().__init__("notion")
    
    def success_response(self, data: Any, status_code: int = 200, headers: Dict[str, str] = None) -> JSONResponse:
        """Format Notion API successful response."""
        # Notion returns data directly
        return JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def error_response(self, error_code: str, message: str, status_code: int = 400, 
                      headers: Dict[str, str] = None) -> JSONResponse:
        """Format Notion API error response."""
        response_data = {
            "object": "error",
            "status": status_code,
            "code": error_code,
            "message": message,
            "request_id": f"mock-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {}
        )
    
    def paginated_response(self, results: List[Any], next_cursor: str = None, 
                          has_more: bool = False) -> Dict[str, Any]:
        """Format Notion paginated response."""
        response = {
            "object": "list",
            "results": results,
            "has_more": has_more
        }
        
        if next_cursor:
            response["next_cursor"] = next_cursor
        
        return response

# Global formatter instances
amazon_formatter = AmazonResponseFormatter()
slack_formatter = SlackResponseFormatter()
stripe_formatter = StripeResponseFormatter()
notion_formatter = NotionResponseFormatter()

# Exception handlers
def create_exception_handlers(formatter: ResponseFormatter):
    """Create exception handlers for a service."""
    
    async def http_exception_handler(request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return formatter.error_response(
            error=exc.detail.get("error", "HTTPException") if isinstance(exc.detail, dict) else "HTTPException",
            message=exc.detail.get("message", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail),
            status_code=exc.status_code,
            details=exc.detail if isinstance(exc.detail, dict) else None,
            headers=exc.headers
        )
    
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return formatter.error_response(
            error="InternalServerError",
            message="An internal server error occurred",
            status_code=500
        )
    
    return {
        HTTPException: http_exception_handler,
        Exception: general_exception_handler
    }

# Utility functions
def add_response_headers(response: JSONResponse, headers: Dict[str, str]) -> JSONResponse:
    """Add headers to response."""
    for key, value in headers.items():
        response.headers[key] = value
    return response

def format_datetime(dt: datetime) -> str:
    """Format datetime for API responses."""
    return dt.isoformat() + "Z"

def format_currency(amount: float, currency: str = "USD") -> Dict[str, Any]:
    """Format currency for API responses."""
    return {
        "amount": int(amount * 100),  # Convert to cents
        "currency": currency.lower()
    }
"""
Error models for API Mock Gym services.
Provides standardized error responses matching real API patterns.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Base error classes
class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    NETWORK = "network"
    DATA = "data"

class BaseError(BaseModel):
    """Base error model."""
    
    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM, description="Error severity")
    category: ErrorCategory = Field(description="Error category")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# Amazon SP-API Error Models
class AmazonError(BaseModel):
    """Amazon SP-API error format."""
    
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

class AmazonErrorResponse(BaseModel):
    """Amazon SP-API error response format."""
    
    errors: List[AmazonError] = Field(description="List of errors")

# Common Amazon SP-API errors
class AmazonErrorCodes:
    """Amazon SP-API error codes."""
    
    # Authentication errors
    INVALID_ACCESS_TOKEN = "InvalidAccessToken"
    ACCESS_DENIED = "AccessDenied"
    UNAUTHORIZED = "Unauthorized"
    
    # Rate limiting errors
    QUOTA_EXCEEDED = "QuotaExceeded"
    REQUEST_THROTTLED = "RequestThrottled"
    
    # Validation errors
    INVALID_PARAMETER = "InvalidParameter"
    INVALID_PARAMETER_VALUE = "InvalidParameterValue"
    MISSING_PARAMETER = "MissingParameter"
    MALFORMED_REQUEST = "MalformedRequest"
    
    # Business logic errors
    INVALID_ORDER_STATE = "InvalidOrderState"
    INVALID_MARKETPLACE = "InvalidMarketplace"
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    
    # System errors
    INTERNAL_SERVER_ERROR = "InternalServerError"
    SERVICE_UNAVAILABLE = "ServiceUnavailable"

# Slack API Error Models
class SlackError(BaseModel):
    """Slack API error format."""
    
    ok: bool = Field(default=False, description="Always false for errors")
    error: str = Field(description="Error code")
    message: Optional[str] = Field(None, description="Error message")

class SlackErrorCodes:
    """Slack API error codes."""
    
    # Authentication errors
    INVALID_AUTH = "invalid_auth"
    NOT_AUTHED = "not_authed"
    TOKEN_REVOKED = "token_revoked"
    
    # Rate limiting
    RATE_LIMITED = "rate_limited"
    
    # Permission errors
    MISSING_SCOPE = "missing_scope"
    NOT_IN_CHANNEL = "not_in_channel"
    
    # Validation errors
    INVALID_ARGUMENTS = "invalid_arguments"
    CHANNEL_NOT_FOUND = "channel_not_found"
    USER_NOT_FOUND = "user_not_found"
    
    # System errors
    INTERNAL_ERROR = "internal_error"
    FATAL_ERROR = "fatal_error"

# Stripe API Error Models
class StripeError(BaseModel):
    """Stripe API error format."""
    
    type: str = Field(description="Error type")
    code: Optional[str] = Field(None, description="Error code")
    message: str = Field(description="Error message")
    param: Optional[str] = Field(None, description="Parameter that caused error")
    request_id: Optional[str] = Field(None, description="Request ID")

class StripeErrorResponse(BaseModel):
    """Stripe API error response format."""
    
    error: StripeError = Field(description="Error details")

class StripeErrorTypes:
    """Stripe API error types."""
    
    # Card errors
    CARD_ERROR = "card_error"
    
    # Request errors
    INVALID_REQUEST_ERROR = "invalid_request_error"
    
    # Authentication errors
    AUTHENTICATION_ERROR = "authentication_error"
    
    # Rate limiting
    RATE_LIMIT_ERROR = "rate_limit_error"
    
    # System errors
    API_ERROR = "api_error"
    API_CONNECTION_ERROR = "api_connection_error"

# Notion API Error Models
class NotionError(BaseModel):
    """Notion API error format."""
    
    object: str = Field(default="error", description="Object type")
    status: int = Field(description="HTTP status code")
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    request_id: str = Field(description="Request ID")

class NotionErrorCodes:
    """Notion API error codes."""
    
    # Authentication errors
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    
    # Validation errors
    INVALID_JSON = "invalid_json"
    INVALID_REQUEST_URL = "invalid_request_url"
    INVALID_REQUEST = "invalid_request"
    VALIDATION_ERROR = "validation_error"
    
    # Rate limiting
    RATE_LIMITED = "rate_limited"
    
    # Business logic errors
    OBJECT_NOT_FOUND = "object_not_found"
    CONFLICT_ERROR = "conflict_error"
    
    # System errors
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

# HTTP Status Code Mappings
class HTTPStatusCodes:
    """HTTP status codes for different error types."""
    
    # Success
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # Server errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

# Error factory functions
def create_amazon_error(code: str, message: str, details: Dict[str, Any] = None) -> AmazonError:
    """Create Amazon SP-API error."""
    return AmazonError(
        code=code,
        message=message,
        details=details or {}
    )

def create_amazon_error_response(errors: List[AmazonError]) -> AmazonErrorResponse:
    """Create Amazon SP-API error response."""
    return AmazonErrorResponse(errors=errors)

def create_slack_error(error_code: str, message: str = None) -> SlackError:
    """Create Slack API error."""
    return SlackError(
        error=error_code,
        message=message
    )

def create_stripe_error(error_type: str, message: str, code: str = None, 
                       param: str = None) -> StripeError:
    """Create Stripe API error."""
    return StripeError(
        type=error_type,
        message=message,
        code=code,
        param=param,
        request_id=f"req_mock_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )

def create_notion_error(code: str, message: str, status: int = 400) -> NotionError:
    """Create Notion API error."""
    return NotionError(
        status=status,
        code=code,
        message=message,
        request_id=f"mock-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )

# Common error scenarios
class CommonErrors:
    """Factory class for common error scenarios."""
    
    @staticmethod
    def invalid_token(service: str = "amazon") -> BaseError:
        """Invalid authentication token error."""
        messages = {
            "amazon": "The access token provided is invalid or expired",
            "slack": "Invalid authentication token",
            "stripe": "Invalid API key provided",
            "notion": "Unauthorized - invalid token"
        }
        
        return BaseError(
            code="INVALID_TOKEN",
            message=messages.get(service, "Invalid authentication token"),
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION
        )
    
    @staticmethod
    def rate_limit_exceeded(service: str = "amazon", limit: int = 100) -> BaseError:
        """Rate limit exceeded error."""
        return BaseError(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit of {limit} requests exceeded",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RATE_LIMIT,
            details={"limit": limit, "service": service}
        )
    
    @staticmethod
    def validation_error(field: str, message: str) -> BaseError:
        """Validation error."""
        return BaseError(
            code="VALIDATION_ERROR",
            message=f"Validation failed for field '{field}': {message}",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            details={"field": field}
        )
    
    @staticmethod
    def resource_not_found(resource_type: str, resource_id: str) -> BaseError:
        """Resource not found error."""
        return BaseError(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} with ID '{resource_id}' not found",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )
    
    @staticmethod
    def internal_server_error(service: str = "unknown") -> BaseError:
        """Internal server error."""
        return BaseError(
            code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            details={"service": service}
        )

# Error response builders
def build_error_response(service: str, error: BaseError) -> Dict[str, Any]:
    """Build service-specific error response."""
    
    if service == "amazon":
        return create_amazon_error_response([
            create_amazon_error(error.code, error.message, error.details)
        ]).dict()
    
    elif service == "slack":
        return create_slack_error(error.code, error.message).dict()
    
    elif service == "stripe":
        stripe_error = create_stripe_error(
            error_type=error.category.value + "_error",
            message=error.message,
            code=error.code
        )
        return StripeErrorResponse(error=stripe_error).dict()
    
    elif service == "notion":
        status_map = {
            ErrorCategory.AUTHENTICATION: HTTPStatusCodes.UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: HTTPStatusCodes.FORBIDDEN,
            ErrorCategory.VALIDATION: HTTPStatusCodes.BAD_REQUEST,
            ErrorCategory.RATE_LIMIT: HTTPStatusCodes.TOO_MANY_REQUESTS,
            ErrorCategory.BUSINESS_LOGIC: HTTPStatusCodes.NOT_FOUND,
            ErrorCategory.SYSTEM: HTTPStatusCodes.INTERNAL_SERVER_ERROR
        }
        
        return create_notion_error(
            error.code,
            error.message,
            status_map.get(error.category, HTTPStatusCodes.BAD_REQUEST)
        ).dict()
    
    else:
        # Generic format
        return {
            "error": {
                "code": error.code,
                "message": error.message,
                "severity": error.severity.value,
                "category": error.category.value,
                "timestamp": error.timestamp.isoformat() + "Z",
                "details": error.details
            }
        }
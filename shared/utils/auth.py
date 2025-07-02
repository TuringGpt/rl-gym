"""
Authentication utilities for API Mock Gym services.
Provides JWT token generation and validation mimicking real API authentication patterns.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class AuthManager:
    """Manages authentication for mock API services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "mock-jwt-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        
    def generate_lwa_token(self, client_id: str, scopes: list = None) -> Dict[str, Any]:
        """Generate a mock LWA (Login with Amazon) token for Amazon SP-API."""
        if scopes is None:
            scopes = [
                "sellingpartnerapi::orders",
                "sellingpartnerapi::inventory", 
                "sellingpartnerapi::listings",
                "sellingpartnerapi::reports"
            ]
            
        payload = {
            "aud": client_id,
            "sub": f"mock-seller-{client_id}",
            "iss": "https://api.amazon.com",
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow(),
            "scope": " ".join(scopes),
            "token_type": "access_token",
            "client_id": client_id,
            "marketplace_ids": ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2", "A1PA6795UKMFR9"]  # US, CA, DE
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.jwt_expiration_hours * 3600,
            "scope": " ".join(scopes)
        }
    
    def generate_slack_token(self, team_id: str, user_id: str) -> Dict[str, Any]:
        """Generate a mock Slack token."""
        payload = {
            "team_id": team_id,
            "user_id": user_id,
            "scope": "channels:read,chat:write,users:read",
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow(),
            "token_type": "bot"
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "scope": "channels:read,chat:write,users:read",
            "bot_user_id": f"B{user_id}",
            "app_id": "A01234567890"
        }
    
    def generate_stripe_token(self, account_id: str = None) -> str:
        """Generate a mock Stripe API key."""
        prefix = "sk_test_" if os.getenv("ENVIRONMENT") == "development" else "sk_live_"
        mock_key = f"{prefix}mock_stripe_key_{''.join([str(ord(c)) for c in (account_id or 'default')])}"
        return mock_key[:32]  # Stripe keys are typically 32 chars
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """Extract current user from JWT token."""
        return self.verify_token(credentials.credentials)
    
    def require_scopes(self, required_scopes: list):
        """Decorator to require specific scopes."""
        def scope_checker(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            user_scopes = current_user.get("scope", "").split()
            
            for scope in required_scopes:
                if scope not in user_scopes:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required scope: {scope}"
                    )
            
            return current_user
        return scope_checker
    
    def create_mock_credentials(self, service_type: str) -> Dict[str, str]:
        """Create mock API credentials for testing."""
        credentials = {
            "amazon": {
                "client_id": os.getenv("LWA_CLIENT_ID", "amzn1.application-oa2-client.mock"),
                "client_secret": os.getenv("LWA_CLIENT_SECRET", "mock-client-secret"),
                "refresh_token": "Atzr|IwEBIA...",  # Mock refresh token
                "region": "us-east-1"
            },
            "slack": {
                "bot_token": "xoxb-mock-bot-token",
                "app_token": "xapp-mock-app-token",
                "signing_secret": "mock-signing-secret"
            },
            "stripe": {
                "publishable_key": "pk_test_mock_publishable_key",
                "secret_key": "sk_test_mock_secret_key",
                "webhook_secret": "whsec_mock_webhook_secret"
            },
            "notion": {
                "api_key": "secret_mock_notion_api_key",
                "oauth_token": "mock_oauth_token"
            }
        }
        
        return credentials.get(service_type, {})

# Global auth manager instances
amazon_auth = AuthManager("amazon")
slack_auth = AuthManager("slack")
stripe_auth = AuthManager("stripe")
notion_auth = AuthManager("notion")

# Dependency functions for FastAPI
def get_amazon_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current Amazon SP-API user."""
    return amazon_auth.get_current_user(credentials)

def get_slack_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current Slack user."""
    return slack_auth.get_current_user(credentials)

def require_amazon_scopes(scopes: list):
    """Require specific Amazon SP-API scopes."""
    return amazon_auth.require_scopes(scopes)

def require_slack_scopes(scopes: list):
    """Require specific Slack scopes."""
    return slack_auth.require_scopes(scopes)

# Mock token endpoint for testing
def create_mock_token_endpoint(auth_manager: AuthManager, service_type: str):
    """Create a mock token endpoint for a service."""
    from fastapi import APIRouter
    
    router = APIRouter()
    
    @router.post("/oauth/token")
    async def get_token(grant_type: str = "client_credentials", 
                       client_id: str = None,
                       client_secret: str = None):
        """Mock token endpoint."""
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="Missing client credentials")
        
        if service_type == "amazon":
            return auth_manager.generate_lwa_token(client_id)
        elif service_type == "slack":
            return auth_manager.generate_slack_token("T1234567890", "U1234567890")
        else:
            raise HTTPException(status_code=400, detail="Unsupported service type")
    
    return router
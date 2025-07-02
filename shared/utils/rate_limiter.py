"""
Rate limiter utilities for API Mock Gym services.
Implements realistic rate limiting patterns matching real API services.
"""

import redis
import asyncio
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self, redis_url: str = None, service_name: str = "default"):
        self.service_name = service_name
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info(f"Connected to Redis for {service_name} rate limiting")
        except Exception as e:
            logger.warning(f"Redis connection failed for {service_name}: {e}. Using in-memory fallback.")
            self.redis_client = None
            self._memory_store = {}
    
    def _get_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{self.service_name}:{identifier}:{window}"
    
    def _get_client_identifier(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Try to get from Authorization header first
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            return f"token:{hash(auth_header)}"
        
        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _redis_sliding_window(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Implement sliding window rate limiting with Redis."""
        now = int(time.time())
        pipeline = self.redis_client.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_count = results[1]
        
        remaining = max(0, limit - current_count - 1)
        reset_time = now + window
        
        return {
            "allowed": current_count < limit,
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": window if current_count >= limit else None
        }
    
    def _memory_sliding_window(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Implement sliding window rate limiting with in-memory storage."""
        now = int(time.time())
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Remove expired requests
        self._memory_store[key] = [
            req_time for req_time in self._memory_store[key] 
            if req_time > now - window
        ]
        
        current_count = len(self._memory_store[key])
        
        if current_count < limit:
            self._memory_store[key].append(now)
            allowed = True
        else:
            allowed = False
        
        remaining = max(0, limit - current_count - (1 if allowed else 0))
        reset_time = now + window
        
        return {
            "allowed": allowed,
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": window if not allowed else None
        }
    
    async def check_rate_limit(self, request: Request, limit: int, window: int = 60) -> Dict[str, Any]:
        """Check if request is within rate limits."""
        identifier = self._get_client_identifier(request)
        key = self._get_key(identifier, f"{window}s")
        
        try:
            if self.redis_client:
                result = await self._redis_sliding_window(key, limit, window)
            else:
                result = self._memory_sliding_window(key, limit, window)
            
            # Log rate limit status
            logger.debug(f"Rate limit check for {identifier}: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request on error to avoid blocking legitimate traffic
            return {
                "allowed": True,
                "limit": limit,
                "remaining": limit - 1,
                "reset": int(time.time()) + window,
                "retry_after": None
            }

class ServiceRateLimiter:
    """Service-specific rate limiters with realistic patterns."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.limiter = RateLimiter(service_name=service_name)
        self.rate_configs = self._get_service_rate_configs()
    
    def _get_service_rate_configs(self) -> Dict[str, Dict[str, int]]:
        """Get service-specific rate limit configurations."""
        return {
            "amazon": {
                # Amazon SP-API rate limits (requests per second)
                "orders": {"limit": 0.5, "window": 1},  # 0.5 RPS = 30 RPM
                "listings": {"limit": 5, "window": 1},  # 5 RPS
                "inventory": {"limit": 2, "window": 1},  # 2 RPS
                "reports": {"limit": 0.0167, "window": 1},  # 1 request per minute
                "default": {"limit": 100, "window": 60}  # 100 RPM default
            },
            "slack": {
                # Slack API rate limits
                "chat.postMessage": {"limit": 1, "window": 1},  # 1 RPS
                "channels.list": {"limit": 20, "window": 60},  # 20 RPM
                "users.list": {"limit": 20, "window": 60},  # 20 RPM
                "default": {"limit": 100, "window": 60}  # 100 RPM default
            },
            "stripe": {
                # Stripe API rate limits
                "charges": {"limit": 100, "window": 1},  # 100 RPS
                "customers": {"limit": 100, "window": 1},  # 100 RPS
                "subscriptions": {"limit": 100, "window": 1},  # 100 RPS
                "default": {"limit": 100, "window": 1}  # 100 RPS default
            },
            "notion": {
                # Notion API rate limits
                "pages": {"limit": 3, "window": 1},  # 3 RPS
                "databases": {"limit": 3, "window": 1},  # 3 RPS
                "search": {"limit": 3, "window": 1},  # 3 RPS
                "default": {"limit": 3, "window": 1}  # 3 RPS default
            }
        }
    
    def get_endpoint_config(self, endpoint: str) -> Dict[str, int]:
        """Get rate limit configuration for specific endpoint."""
        service_config = self.rate_configs.get(self.service_name, {})
        
        # Try exact match first
        if endpoint in service_config:
            return service_config[endpoint]
        
        # Try pattern matching
        for pattern, config in service_config.items():
            if pattern in endpoint:
                return config
        
        # Return default
        return service_config.get("default", {"limit": 100, "window": 60})
    
    async def check_endpoint_rate_limit(self, request: Request, endpoint: str) -> Dict[str, Any]:
        """Check rate limit for specific endpoint."""
        config = self.get_endpoint_config(endpoint)
        return await self.limiter.check_rate_limit(
            request, 
            limit=int(config["limit"] * config["window"]),  # Convert to requests per window
            window=config["window"]
        )

# Rate limiter middleware
def create_rate_limit_middleware(service_name: str):
    """Create rate limiting middleware for a service."""
    rate_limiter = ServiceRateLimiter(service_name)
    
    async def rate_limit_middleware(request: Request, call_next):
        """Rate limiting middleware function."""
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Skip if rate limiting is disabled
        if os.getenv("SIMULATE_RATE_LIMITS", "true").lower() != "true":
            return await call_next(request)
        
        # Extract endpoint name from path
        endpoint = request.url.path.split("/")[-1] if "/" in request.url.path else request.url.path
        
        # Check rate limit
        rate_info = await rate_limiter.check_endpoint_rate_limit(request, endpoint)
        
        if not rate_info["allowed"]:
            headers = {
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(rate_info["retry_after"])
            }
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "RateLimitExceeded",
                    "message": f"Rate limit exceeded for {service_name} API",
                    "limit": rate_info["limit"],
                    "reset": rate_info["reset"]
                },
                headers=headers
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response
    
    return rate_limit_middleware

# Service-specific rate limiters
amazon_rate_limiter = ServiceRateLimiter("amazon")
slack_rate_limiter = ServiceRateLimiter("slack")
stripe_rate_limiter = ServiceRateLimiter("stripe")
notion_rate_limiter = ServiceRateLimiter("notion")

# Dependency functions for FastAPI
async def check_amazon_rate_limit(request: Request):
    """Check Amazon SP-API rate limits."""
    endpoint = request.url.path.split("/")[-1]
    return await amazon_rate_limiter.check_endpoint_rate_limit(request, endpoint)

async def check_slack_rate_limit(request: Request):
    """Check Slack API rate limits."""
    endpoint = request.url.path.split("/")[-1]
    return await slack_rate_limiter.check_endpoint_rate_limit(request, endpoint)
"""
Amazon Selling Partner API Mock Service
Main FastAPI application entry point
"""

import os
import sys
import logging
from pathlib import Path

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# Import shared utilities
from utils.database import initialize_database
from utils.rate_limiter import create_rate_limit_middleware
from utils.response_formatter import amazon_formatter, create_exception_handlers
from utils.auth import create_mock_token_endpoint, amazon_auth

# Import Amazon-specific modules
from app.database.connection import db_manager
from app.api.v0 import orders, reports
from app.api import listings_2021_08_01, feeds_2021_06_30
from app.models import *  # Import all models to register them

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Amazon SP-API Mock Service...")
    
    try:
        # Initialize database
        db_manager.create_tables()
        logger.info("Database tables initialized")
        
        # Check database health
        health = db_manager.health_check()
        if health["status"] == "healthy":
            logger.info("Database connection verified")
        else:
            logger.warning(f"Database health check failed: {health}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise
    finally:
        logger.info("Shutting down Amazon SP-API Mock Service...")

# Create FastAPI application
app = FastAPI(
    title="Amazon Selling Partner API Mock",
    description="""
    Mock implementation of Amazon Selling Partner API for training language models.
    
    This service provides realistic API endpoints matching the actual Amazon SP-API:
    - Orders API (v0)
    - Listings API (2021-08-01)
    - Inventory API (v1)  
    - Reports API (2021-06-30)
    - Feeds API (2021-06-30)
    
    Features:
    - Authentic request/response patterns
    - Realistic mock data with proper relationships
    - Rate limiting matching Amazon's constraints
    - Proper authentication simulation
    - Error responses matching real API behavior
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiting middleware
rate_limit_middleware = create_rate_limit_middleware("amazon")
app.middleware("http")(rate_limit_middleware)

# Add exception handlers
exception_handlers = create_exception_handlers(amazon_formatter)
for exc_class, handler in exception_handlers.items():
    app.add_exception_handler(exc_class, handler)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    try:
        db_health = db_manager.health_check()
        
        return {
            "status": "healthy",
            "service": "amazon-sp-api-mock",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "database": db_health,
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "service": "amazon-sp-api-mock"
            }
        )

# Mock LWA token endpoint
token_router = create_mock_token_endpoint(amazon_auth, "amazon")
app.include_router(token_router, prefix="/auth", tags=["Authentication"])

# Include API routers
app.include_router(orders.router, prefix="/orders/v0", tags=["Orders"])
app.include_router(reports.router, prefix="/reports/2021-06-30", tags=["Reports"])
app.include_router(listings_2021_08_01.router, prefix="/listings/2021-08-01", tags=["Listings"])
app.include_router(feeds_2021_06_30.router, prefix="/feeds/2021-06-30", tags=["Feeds"])

# Inventory endpoints (inline for simplicity)
@app.get("/fba/inventory/v1/summaries", tags=["Inventory"])
async def get_inventory_summaries(
    request: Request,
    granularityType: str = "Marketplace",
    granularityId: str = "ATVPDKIKX0DER",
    marketplaceIds: str = "ATVPDKIKX0DER",
    details: bool = False,
    startDateTime: str = None,
    sellerSkus: str = None,
    nextToken: str = None,
    maxResults: int = 50
):
    """Get inventory summaries."""
    from app.services.inventory_service import InventoryService
    from utils.auth import get_amazon_user
    
    # Verify authentication
    current_user = get_amazon_user(request.headers.get("authorization", "").replace("Bearer ", ""))
    
    service = InventoryService()
    
    filters = {}
    if sellerSkus:
        filters["seller_skus"] = sellerSkus.split(",")
    if startDateTime:
        filters["start_date"] = startDateTime
    
    result = await service.get_inventory_summaries(
        marketplace_ids=marketplaceIds.split(","),
        filters=filters,
        next_token=nextToken,
        max_results=maxResults
    )
    
    return amazon_formatter.inventory_response(
        result["summaries"],
        result.get("next_token")
    )

@app.get("/fba/inventory/v1/details", tags=["Inventory"])
async def get_inventory_details(
    request: Request,
    marketplaceIds: str = "ATVPDKIKX0DER",
    sellerSkus: str = None,
    nextToken: str = None,
    maxResults: int = 50
):
    """Get detailed inventory information."""
    from app.services.inventory_service import InventoryService
    from utils.auth import get_amazon_user
    
    # Verify authentication
    current_user = get_amazon_user(request.headers.get("authorization", "").replace("Bearer ", ""))
    
    service = InventoryService()
    
    filters = {}
    if sellerSkus:
        filters["seller_skus"] = sellerSkus.split(",")
    
    result = await service.get_inventory_details(
        marketplace_ids=marketplaceIds.split(","),
        filters=filters,
        next_token=nextToken,
        max_results=max_results
    )
    
    return amazon_formatter.inventory_response(
        result["details"],
        result.get("next_token")
    )

# Admin endpoints for data generation (development only)
if os.getenv("ENVIRONMENT") == "development":
    @app.post("/admin/generate-mock-data", tags=["Admin"])
    async def generate_mock_data(
        orders: int = 100,
        products: int = 50,
        inventory_items: int = 200
    ):
        """Generate additional mock data (development only)."""
        try:
            from app.services.data_generator import DataGenerator
            
            generator = DataGenerator(db_manager)
            result = await generator.generate_all_data(
                orders_count=orders,
                products_count=products,
                inventory_count=inventory_items
            )
            
            return {
                "success": True,
                "generated": result,
                "message": "Mock data generated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to generate mock data: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate mock data: {str(e)}"
            )
    
    @app.get("/admin/database-info", tags=["Admin"])
    async def get_database_info():
        """Get database information (development only)."""
        return {
            "tables": db_manager.get_table_info(),
            "health": db_manager.health_check()
        }

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Amazon Selling Partner API Mock",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "orders": "/orders/v0",
            "inventory": "/fba/inventory/v1",
            "listings": "/listings/2021-08-01",
            "reports": "/reports/2021-06-30",
            "feeds": "/feeds/2021-06-30"
        },
        "authentication": "/auth/oauth/token"
    }

# Request logging middleware (development only)
if os.getenv("LOG_LEVEL") == "DEBUG":
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        logger.debug(f"Response: {response.status_code}")
        return response

# Response delay simulation (for testing)
response_delay = int(os.getenv("RESPONSE_DELAY_MS", "0"))
if response_delay > 0:
    import asyncio
    
    @app.middleware("http")
    async def simulate_delay(request: Request, call_next):
        await asyncio.sleep(response_delay / 1000)
        return await call_next(request)

if __name__ == "__main__":
    port = int(os.getenv("AMAZON_SERVICE_PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
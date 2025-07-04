from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import router
from app.testing.test_router import test_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Amazon SP-API Mock - Listings Items",
    description="A simple mock implementation of Amazon's Selling Partner API for Listings Items",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["Listings Items"])
app.include_router(test_router, tags=["Testing"])


@app.get("/")
def read_root():
    return {
        "message": "Amazon SP-API Mock - Listings Items API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "get_listing": "GET /listings/2021-08-01/items/{seller_id}/{sku}",
            "create_update_listing": "PUT /listings/2021-08-01/items/{seller_id}/{sku}",
            "patch_listing": "PATCH /listings/2021-08-01/items/{seller_id}/{sku}",
            "delete_listing": "DELETE /listings/2021-08-01/items/{seller_id}/{sku}",
            "search_listings": "GET /listings/2021-08-01/items",
        },
        "testing": {
            "description": "Testing workflow for validating Claude actions",
            "endpoints": {
                "list_test_flows": "GET /test/flows",
                "validate_flow": "GET /test/validate/{flow_id}",
                "reset_database": "POST /test/reset",
                "get_help": "GET /test/help",
            },
            "workflow": "1. Get test flows → 2. Ask Claude to perform action → 3. Validate result → 4. Reset DB",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "amazon-sp-api-mock"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.testing.test_router import test_router

from .database import engine, Base
from .routers import router
from app.sessions.router import session_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables and seed data
    print("Starting up: Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize seed data for the main database if needed
    try:
        from combined_seed_data import create_comprehensive_sample_data

        print("Seeding main database with sample data...")
        create_comprehensive_sample_data()
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Warning: Could not seed main database: {e}")

    yield

    # Shutdown: Clean up resources if needed
    print("Shutting down: Cleaning up resources...")
    engine.dispose()


# Create FastAPI app with lifespan
app = FastAPI(
    title="Amazon SP-API Mock - Listings Items",
    description="A simple mock implementation of Amazon's Selling Partner API for Listings Items with Required Session Headers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(session_router, tags=["Session Management"])
app.include_router(router, tags=["Listings Items"])
app.include_router(test_router, tags=["Testing"])


@app.get("/")
def read_root():
    return {
        "message": "Amazon SP-API Mock - Listings Items API with Required Session Headers",
        "version": "2.0.0",
        "docs": "/docs",
        "workflow": {
            "step_1": "Create session: POST /sessions",
            "step_2": "Use session ID in header: X-Session-ID: {session_id}",
            "step_3": "Make requests with required header",
        },
        "endpoints": {
            "create_session": "POST /sessions",
            "get_listing": "GET /listings/2021-08-01/items/{seller_id}/{sku} (requires X-Session-ID header)",
            "create_update_listing": "PUT /listings/2021-08-01/items/{seller_id}/{sku} (requires X-Session-ID header)",
            "patch_listing": "PATCH /listings/2021-08-01/items/{seller_id}/{sku} (requires X-Session-ID header)",
            "delete_listing": "DELETE /listings/2021-08-01/items/{seller_id}/{sku} (requires X-Session-ID header)",
            "search_listings": "GET /listings/2021-08-01/items (requires X-Session-ID header)",
        },
        "sessions": {
            "description": "Session-based data isolation with required headers",
            "creation": "POST /sessions auto-generates a random session ID",
            "usage": "All database operations require X-Session-ID header",
            "isolation": "Each session gets its own isolated database with seed data",
            "reuse": "Same session ID can be used across multiple requests",
        },
        "testing": {
            "description": "Testing workflow for validating Claude actions",
            "endpoints": {
                "list_test_flows": "GET /test/flows",
                "validate_flow": "GET /test/validate/{flow_id}",
                "reset_database": "POST /test/reset",
                "get_state": "GET /test/state",
                "get_help": "GET /test/help",
            },
            "workflow": "1. Create session → 2. Get test flows → 3. Ask Claude to perform action → 4. Validate result",
        },
        "features": {
            "required_headers": "X-Session-ID header required for all database operations",
            "auto_generated_ids": "Session IDs are randomly generated, not user-provided",
            "complete_isolation": "Each session gets its own isolated database",
            "session_reuse": "Same session can be used across multiple requests",
            "parallel_safe": "Multiple users/agents can work with different sessions",
        },
        "example": {
            "create_session": "curl -X POST http://localhost:8000/sessions",
            "use_session": "curl -H 'X-Session-ID: session_abc123' http://localhost:8000/listings/2021-08-01/items/SELLER001/LAPTOP-001",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "amazon-sp-api-mock"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

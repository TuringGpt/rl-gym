"""
Amazon SP-API Feeds 2021-06-30 endpoints
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.auth import get_amazon_user, require_amazon_scopes
from utils.response_formatter import amazon_formatter
from utils.rate_limiter import check_amazon_rate_limit

# Import local modules
from app.database.connection import get_db

router = APIRouter()

@router.post("/feeds")
async def create_feed(
    request: Request,
    feed_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::feeds"]))
):
    """Create a feed."""
    await check_amazon_rate_limit(request)
    
    # Mock feed creation
    feed_id = f"feed_{int(request.headers.get('x-request-id', '12345')[-5:])}"
    
    return {
        "payload": {
            "feedId": feed_id,
            "feedType": feed_data.get("feedType", "POST_PRODUCT_DATA"),
            "createdTime": "2024-01-01T00:00:00Z",
            "processingStatus": "IN_QUEUE"
        }
    }

@router.get("/feeds")
async def get_feeds(
    request: Request,
    db: Session = Depends(get_db),
    feedTypes: Optional[str] = Query(None),
    marketplaceIds: Optional[str] = Query(None),
    pageSize: Optional[int] = Query(10, ge=1, le=100),
    processingStatuses: Optional[str] = Query(None),
    createdSince: Optional[str] = Query(None),
    createdUntil: Optional[str] = Query(None),
    nextToken: Optional[str] = Query(None),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::feeds"]))
):
    """Get feeds."""
    await check_amazon_rate_limit(request)
    
    # Mock feeds response
    return {
        "payload": {
            "feeds": [
                {
                    "feedId": "feed_12345",
                    "feedType": "POST_PRODUCT_DATA",
                    "createdTime": "2024-01-01T00:00:00Z",
                    "processingStatus": "DONE"
                }
            ],
            "nextToken": None
        }
    }

@router.get("/feeds/{feedId}")
async def get_feed(
    feedId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::feeds"]))
):
    """Get feed details."""
    await check_amazon_rate_limit(request)
    
    return {
        "payload": {
            "feedId": feedId,
            "feedType": "POST_PRODUCT_DATA",
            "createdTime": "2024-01-01T00:00:00Z",
            "processingStatus": "DONE",
            "processingStartTime": "2024-01-01T00:01:00Z",
            "processingEndTime": "2024-01-01T00:05:00Z"
        }
    }

@router.delete("/feeds/{feedId}")
async def cancel_feed(
    feedId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::feeds"]))
):
    """Cancel feed."""
    await check_amazon_rate_limit(request)
    
    return {
        "payload": {
            "feedId": feedId,
            "processingStatus": "CANCELLED"
        }
    }
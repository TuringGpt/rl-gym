"""
Amazon Sales API v1
Based on: https://developer-docs.amazon.com/sp-api/docs/sales-api-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from app.database.connection import get_db, get_async_db
from app.database.schemas import SalesMetrics, Order, OrderItem
from app.services.sales_service import SalesService
import sys
from pathlib import Path as FilePath
import asyncio

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/sales/v1", tags=["Sales"])

# Request/Response Models
class Money(BaseModel):
    currency_code: str = Field(alias="currencyCode")
    amount: str

class OrderMetric(BaseModel):
    interval: str
    unit_count: int = Field(alias="unitCount")
    order_item_count: int = Field(alias="orderItemCount")
    order_count: int = Field(alias="orderCount")
    average_unit_price: Money = Field(alias="averageUnitPrice")
    total_sales: Money = Field(alias="totalSales")

class Error(BaseModel):
    code: str
    message: str
    details: Optional[str] = None

class GetOrderMetricsResponse(BaseModel):
    payload: List[OrderMetric]
    errors: List[Error] = []

# API Endpoints

@router.get("/orderMetrics", response_model=GetOrderMetricsResponse)
async def get_order_metrics(
    granularity: str = Query(..., description="Granularity for the aggregation (Hour, Day, Week, Month, Quarter, Year)"),
    buyer_type: str = Query("All", alias="buyerType", description="Filter by buyer type (All, B2B, B2C)"),
    first_day_of_week: str = Query("Monday", alias="firstDayOfWeek", description="First day of the week (Monday, Tuesday, etc.)"),
    start_date: Optional[datetime] = Query(None, alias="startDate", description="Start date for the report"),
    end_date: Optional[datetime] = Query(None, alias="endDate", description="End date for the report"),
    marketplace_ids: Optional[List[str]] = Query(None, alias="marketplaceIds", description="List of marketplace IDs"),
    asin: Optional[str] = Query(None, description="Filter by ASIN"),
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    db: Session = Depends(get_db)
):
    """
    Returns order metrics aggregated by the specified granularity and filters.
    
    This endpoint provides sales metrics including unit count, order count, 
    average unit price, and total sales aggregated by the specified time period.
    """
    try:
        # Validate granularity
        valid_granularities = ["Hour", "Day", "Week", "Month", "Quarter", "Year"]
        if granularity not in valid_granularities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid granularity. Must be one of: {', '.join(valid_granularities)}"
            )
        
        # Validate buyer type
        valid_buyer_types = ["All", "B2B", "B2C"]
        if buyer_type not in valid_buyer_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid buyer type. Must be one of: {', '.join(valid_buyer_types)}"
            )
        
        # Validate first day of week
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if first_day_of_week not in valid_days:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid first day of week. Must be one of: {', '.join(valid_days)}"
            )
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Initialize service
        service = SalesService(db)
        
        # Get order metrics
        metrics = await service.get_order_metrics(
            granularity=granularity,
            buyer_type=buyer_type,
            first_day_of_week=first_day_of_week,
            start_date=start_date,
            end_date=end_date,
            marketplace_ids=marketplace_ids,
            asin=asin,
            sku=sku
        )
        
        # Convert to response format
        order_metrics = []
        for metric in metrics:
            order_metric = OrderMetric(
                interval=metric.interval,
                unitCount=metric.unit_count,
                orderItemCount=metric.order_item_count,
                orderCount=metric.order_count,
                averageUnitPrice=Money(
                    currencyCode=metric.currency_code,
                    amount=str(metric.average_unit_price)
                ),
                totalSales=Money(
                    currencyCode=metric.currency_code,
                    amount=str(metric.total_sales)
                )
            )
            order_metrics.append(order_metric)
        
        return GetOrderMetricsResponse(
            payload=order_metrics,
            errors=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return GetOrderMetricsResponse(
            payload=[],
            errors=[Error(
                code="InternalError",
                message="An internal error occurred while processing the request",
                details=str(e)
            )]
        )

@router.get("/orderMetrics/summary", response_model=Dict[str, Any])
async def get_order_metrics_summary(
    buyer_type: str = Query("All", alias="buyerType", description="Filter by buyer type (All, B2B, B2C)"),
    start_date: Optional[datetime] = Query(None, alias="startDate", description="Start date for the report"),
    end_date: Optional[datetime] = Query(None, alias="endDate", description="End date for the report"),
    marketplace_ids: Optional[List[str]] = Query(None, alias="marketplaceIds", description="List of marketplace IDs"),
    db: Session = Depends(get_db)
):
    """
    Returns a summary of order metrics for the specified period.
    
    This endpoint provides high-level sales metrics including total sales,
    total orders, and average order value for the specified time period.
    """
    try:
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Initialize service
        service = SalesService(db)
        
        # Get summary metrics
        summary = await service.get_order_metrics_summary(
            buyer_type=buyer_type,
            start_date=start_date,
            end_date=end_date,
            marketplace_ids=marketplace_ids
        )
        
        return {
            "summary": summary,
            "period": {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
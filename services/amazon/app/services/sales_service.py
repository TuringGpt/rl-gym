"""
Sales Service for Amazon SP-API Mock Service
Handles business logic and async operations for sales metrics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select, func
from app.database.schemas import SalesMetrics, Order, OrderItem
import asyncio
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class SalesService:
    """Service class for handling sales operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_order_metrics(self,
                               granularity: str,
                               buyer_type: str = "All",
                               first_day_of_week: str = "Monday",
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               marketplace_ids: Optional[List[str]] = None,
                               asin: Optional[str] = None,
                               sku: Optional[str] = None) -> List[SalesMetrics]:
        """
        Get order metrics with specified filters and aggregation
        """
        try:
            # First, check if we have pre-computed metrics
            query = self.db.query(SalesMetrics)
            
            # Apply filters
            if start_date:
                query = query.filter(SalesMetrics.period_start >= start_date)
            if end_date:
                query = query.filter(SalesMetrics.period_end <= end_date)
            if granularity:
                query = query.filter(SalesMetrics.granularity == granularity)
            if buyer_type != "All":
                query = query.filter(SalesMetrics.buyer_type == buyer_type)
            if marketplace_ids:
                query = query.filter(SalesMetrics.marketplace_ids.contains(marketplace_ids))
            if asin:
                query = query.filter(SalesMetrics.asin == asin)
            if sku:
                query = query.filter(SalesMetrics.sku == sku)
            
            existing_metrics = query.all()
            
            # If no pre-computed metrics, generate them from order data
            if not existing_metrics:
                existing_metrics = await self._generate_metrics_from_orders(
                    granularity=granularity,
                    buyer_type=buyer_type,
                    first_day_of_week=first_day_of_week,
                    start_date=start_date,
                    end_date=end_date,
                    marketplace_ids=marketplace_ids,
                    asin=asin,
                    sku=sku
                )
            
            return existing_metrics
            
        except Exception as e:
            logger.error(f"Error getting order metrics: {e}")
            raise
    
    async def _generate_metrics_from_orders(self,
                                           granularity: str,
                                           buyer_type: str = "All",
                                           first_day_of_week: str = "Monday",
                                           start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None,
                                           marketplace_ids: Optional[List[str]] = None,
                                           asin: Optional[str] = None,
                                           sku: Optional[str] = None) -> List[SalesMetrics]:
        """
        Generate metrics from order data when pre-computed metrics don't exist
        """
        try:
            # Base query for orders
            query = self.db.query(Order).join(OrderItem)
            
            # Apply filters
            if start_date:
                query = query.filter(Order.purchase_date >= start_date)
            if end_date:
                query = query.filter(Order.purchase_date <= end_date)
            if marketplace_ids:
                query = query.filter(Order.marketplace_id.in_(marketplace_ids))
            if asin:
                query = query.filter(OrderItem.asin == asin)
            if sku:
                query = query.filter(OrderItem.seller_sku == sku)
            
            # Apply buyer type filter (simplified logic)
            if buyer_type == "B2B":
                query = query.filter(Order.is_business_order == True)
            elif buyer_type == "B2C":
                query = query.filter(Order.is_business_order == False)
            
            orders = query.all()
            
            # Generate time intervals based on granularity
            intervals = self._generate_time_intervals(
                granularity=granularity,
                start_date=start_date or datetime.now() - timedelta(days=30),
                end_date=end_date or datetime.now(),
                first_day_of_week=first_day_of_week
            )
            
            # Aggregate metrics for each interval
            metrics = []
            for interval_start, interval_end in intervals:
                interval_orders = [
                    order for order in orders
                    if interval_start <= order.purchase_date < interval_end
                ]
                
                if not interval_orders:
                    # Create empty metric for this interval
                    metric = SalesMetrics(
                        interval=f"{interval_start.isoformat()}/{interval_end.isoformat()}",
                        granularity=granularity,
                        unit_count=0,
                        order_item_count=0,
                        order_count=0,
                        average_unit_price=Decimal('0.00'),
                        total_sales=Decimal('0.00'),
                        currency_code="USD",
                        buyer_type=buyer_type,
                        marketplace_ids=marketplace_ids,
                        asin=asin,
                        sku=sku,
                        period_start=interval_start,
                        period_end=interval_end
                    )
                    metrics.append(metric)
                    continue
                
                # Calculate metrics for this interval
                total_units = 0
                total_order_items = 0
                total_orders = len(interval_orders)
                total_sales = Decimal('0.00')
                
                for order in interval_orders:
                    for item in order.order_items:
                        if asin and item.asin != asin:
                            continue
                        if sku and item.seller_sku != sku:
                            continue
                        
                        total_units += item.quantity_ordered
                        total_order_items += 1
                        if item.item_price:
                            total_sales += Decimal(str(item.item_price))
                
                average_unit_price = total_sales / total_units if total_units > 0 else Decimal('0.00')
                
                metric = SalesMetrics(
                    interval=f"{interval_start.isoformat()}/{interval_end.isoformat()}",
                    granularity=granularity,
                    unit_count=total_units,
                    order_item_count=total_order_items,
                    order_count=total_orders,
                    average_unit_price=average_unit_price,
                    total_sales=total_sales,
                    currency_code="USD",
                    buyer_type=buyer_type,
                    marketplace_ids=marketplace_ids,
                    asin=asin,
                    sku=sku,
                    period_start=interval_start,
                    period_end=interval_end
                )
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error generating metrics from orders: {e}")
            raise
    
    def _generate_time_intervals(self,
                                granularity: str,
                                start_date: datetime,
                                end_date: datetime,
                                first_day_of_week: str = "Monday") -> List[tuple]:
        """
        Generate time intervals based on granularity
        """
        intervals = []
        current = start_date
        
        while current < end_date:
            if granularity == "Hour":
                next_period = current + timedelta(hours=1)
            elif granularity == "Day":
                next_period = current + timedelta(days=1)
            elif granularity == "Week":
                # Calculate start of week based on first_day_of_week
                days_until_week_start = (current.weekday() - self._get_weekday_number(first_day_of_week)) % 7
                week_start = current - timedelta(days=days_until_week_start)
                next_period = week_start + timedelta(weeks=1)
            elif granularity == "Month":
                if current.month == 12:
                    next_period = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    next_period = current.replace(month=current.month + 1, day=1)
            elif granularity == "Quarter":
                quarter = ((current.month - 1) // 3) + 1
                if quarter == 4:
                    next_period = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    next_period = current.replace(month=quarter * 3 + 1, day=1)
            elif granularity == "Year":
                next_period = current.replace(year=current.year + 1, month=1, day=1)
            else:
                raise ValueError(f"Unsupported granularity: {granularity}")
            
            if next_period > end_date:
                next_period = end_date
            
            intervals.append((current, next_period))
            current = next_period
        
        return intervals
    
    def _get_weekday_number(self, day_name: str) -> int:
        """
        Get weekday number (0=Monday, 6=Sunday)
        """
        day_mapping = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }
        return day_mapping.get(day_name, 0)
    
    async def get_order_metrics_summary(self,
                                       buyer_type: str = "All",
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None,
                                       marketplace_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get summary of order metrics for the specified period
        """
        try:
            # Get daily metrics to calculate summary
            daily_metrics = await self.get_order_metrics(
                granularity="Day",
                buyer_type=buyer_type,
                start_date=start_date,
                end_date=end_date,
                marketplace_ids=marketplace_ids
            )
            
            if not daily_metrics:
                return {
                    "totalSales": {"currencyCode": "USD", "amount": "0.00"},
                    "totalOrders": 0,
                    "totalUnits": 0,
                    "averageOrderValue": {"currencyCode": "USD", "amount": "0.00"},
                    "averageUnitPrice": {"currencyCode": "USD", "amount": "0.00"}
                }
            
            # Calculate summary metrics
            total_sales = sum(metric.total_sales for metric in daily_metrics)
            total_orders = sum(metric.order_count for metric in daily_metrics)
            total_units = sum(metric.unit_count for metric in daily_metrics)
            
            average_order_value = total_sales / total_orders if total_orders > 0 else Decimal('0.00')
            average_unit_price = total_sales / total_units if total_units > 0 else Decimal('0.00')
            
            return {
                "totalSales": {"currencyCode": "USD", "amount": str(total_sales)},
                "totalOrders": total_orders,
                "totalUnits": total_units,
                "averageOrderValue": {"currencyCode": "USD", "amount": str(average_order_value)},
                "averageUnitPrice": {"currencyCode": "USD", "amount": str(average_unit_price)}
            }
            
        except Exception as e:
            logger.error(f"Error getting order metrics summary: {e}")
            raise
    
    async def create_sales_metric(self, metric_data: Dict[str, Any]) -> SalesMetrics:
        """
        Create a new sales metric record
        """
        try:
            metric = SalesMetrics(
                interval=metric_data['interval'],
                granularity=metric_data['granularity'],
                unit_count=metric_data['unit_count'],
                order_item_count=metric_data['order_item_count'],
                order_count=metric_data['order_count'],
                average_unit_price=metric_data['average_unit_price'],
                total_sales=metric_data['total_sales'],
                currency_code=metric_data.get('currency_code', 'USD'),
                buyer_type=metric_data.get('buyer_type', 'All'),
                marketplace_ids=metric_data.get('marketplace_ids'),
                asin=metric_data.get('asin'),
                sku=metric_data.get('sku'),
                period_start=metric_data['period_start'],
                period_end=metric_data['period_end']
            )
            
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            
            return metric
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sales metric: {e}")
            raise
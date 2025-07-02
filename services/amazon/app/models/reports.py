"""
Reports-related Pydantic models for Amazon SP-API
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.base_models import AmazonBaseModel
from pydantic import Field

class ReportRequest(AmazonBaseModel):
    """Report creation request."""
    reportType: str = Field(description="Report type")
    marketplaceIds: List[str] = Field(description="List of marketplace IDs")
    dataStartTime: Optional[str] = Field(None, description="Start date for report data")
    dataEndTime: Optional[str] = Field(None, description="End date for report data")
    reportOptions: Optional[Dict[str, str]] = Field(None, description="Additional report options")

class Report(AmazonBaseModel):
    """Report model."""
    reportId: str
    reportType: str
    dataStartTime: Optional[str] = None
    dataEndTime: Optional[str] = None
    marketplaceIds: Optional[List[str]] = None
    processingStatus: str = "IN_PROGRESS"
    processingStartTime: Optional[str] = None
    processingEndTime: Optional[str] = None
    reportDocumentId: Optional[str] = None
    createdTime: str

class ReportResponse(AmazonBaseModel):
    """Report response."""
    payload: Report

class ReportDocument(AmazonBaseModel):
    """Report document model."""
    reportDocumentId: str
    url: str
    encryptionDetails: Optional[Dict[str, Any]] = None
    compressionAlgorithm: Optional[str] = None

class ReportDocumentResponse(AmazonBaseModel):
    """Report document response."""
    payload: ReportDocument

class ReportsListResponse(AmazonBaseModel):
    """Reports list response."""
    payload: Dict[str, Any] = Field(description="Reports list payload")

# Report type definitions
class ReportTypes:
    """Amazon SP-API report types."""
    
    # Inventory reports
    GET_FLAT_FILE_OPEN_LISTINGS_DATA = "GET_FLAT_FILE_OPEN_LISTINGS_DATA"
    GET_MERCHANT_LISTINGS_ALL_DATA = "GET_MERCHANT_LISTINGS_ALL_DATA"
    GET_MERCHANT_LISTINGS_DATA = "GET_MERCHANT_LISTINGS_DATA"
    GET_MERCHANT_LISTINGS_INACTIVE_DATA = "GET_MERCHANT_LISTINGS_INACTIVE_DATA"
    GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT = "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT"
    GET_MERCHANT_LISTINGS_DATA_LITE = "GET_MERCHANT_LISTINGS_DATA_LITE"
    GET_MERCHANT_LISTINGS_DATA_LITER = "GET_MERCHANT_LISTINGS_DATA_LITER"
    GET_MERCHANT_CANCELLED_LISTINGS_DATA = "GET_MERCHANT_CANCELLED_LISTINGS_DATA"
    GET_MERCHANTS_LISTINGS_FYP_REPORT = "GET_MERCHANTS_LISTINGS_FYP_REPORT"
    GET_PAN_EU_OFFER_STATUS = "GET_PAN_EU_OFFER_STATUS"
    GET_MFN_PAN_EU_OFFER_STATUS = "GET_MFN_PAN_EU_OFFER_STATUS"
    GET_FLAT_FILE_GEO_OPPORTUNITIES = "GET_FLAT_FILE_GEO_OPPORTUNITIES"
    
    # Order reports
    GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING = "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING"
    GET_ORDER_REPORT_DATA_INVOICING = "GET_ORDER_REPORT_DATA_INVOICING"
    GET_ORDER_REPORT_DATA_TAX = "GET_ORDER_REPORT_DATA_TAX"
    GET_ORDER_REPORT_DATA_SHIPPING = "GET_ORDER_REPORT_DATA_SHIPPING"
    GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING = "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING"
    GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING = "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING"
    GET_FLAT_FILE_ORDER_REPORT_DATA_TAX = "GET_FLAT_FILE_ORDER_REPORT_DATA_TAX"
    GET_FLAT_FILE_ORDERS_RECONCILIATION_DATA = "GET_FLAT_FILE_ORDERS_RECONCILIATION_DATA"
    
    # Settlement reports
    GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"
    GET_V2_SETTLEMENT_REPORT_DATA_XML = "GET_V2_SETTLEMENT_REPORT_DATA_XML"
    GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2 = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2"
    
    # FBA reports
    GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"
    GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING"
    GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX"
    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE = "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE"
    GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA = "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA"
    GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA = "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA"
    
    # Inventory reports
    GET_AFN_INVENTORY_DATA = "GET_AFN_INVENTORY_DATA"
    GET_AFN_INVENTORY_DATA_BY_COUNTRY = "GET_AFN_INVENTORY_DATA_BY_COUNTRY"
    GET_FBA_INVENTORY_RECONCILIATION_DATA = "GET_FBA_INVENTORY_RECONCILIATION_DATA"
    GET_FBA_INVENTORY_AGED_DATA = "GET_FBA_INVENTORY_AGED_DATA"
    GET_FBA_INVENTORY_RECEIVED_DATA = "GET_FBA_INVENTORY_RECEIVED_DATA"
    GET_RESERVED_INVENTORY_DATA = "GET_RESERVED_INVENTORY_DATA"
    GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA = "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"
    GET_FBA_MYI_ALL_INVENTORY_DATA = "GET_FBA_MYI_ALL_INVENTORY_DATA"
    GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT = "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT"
    GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA = "GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA"
    GET_STRANDED_INVENTORY_LOADER_DATA = "GET_STRANDED_INVENTORY_LOADER_DATA"
    GET_FBA_INVENTORY_PLANNING_DATA = "GET_FBA_INVENTORY_PLANNING_DATA"
    
    # Performance reports
    GET_SELLER_FEEDBACK_DATA = "GET_SELLER_FEEDBACK_DATA"
    GET_V1_SELLER_PERFORMANCE_REPORT = "GET_V1_SELLER_PERFORMANCE_REPORT"
    
    # Sales reports
    GET_FLAT_FILE_SALES_TAX_DATA = "GET_FLAT_FILE_SALES_TAX_DATA"
    SC_VAT_TAX_REPORT = "SC_VAT_TAX_REPORT"
    GET_VAT_TRANSACTION_DATA = "GET_VAT_TRANSACTION_DATA"
    GET_GST_MTR_B2B_CUSTOM = "GET_GST_MTR_B2B_CUSTOM"
    GET_GST_MTR_B2C_CUSTOM = "GET_GST_MTR_B2C_CUSTOM"
    
    # Brand Analytics reports
    GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT = "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"
    GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT = "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"
    GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT = "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"
    
    # Vendor reports
    GET_VENDOR_DIRECT_FULFILLMENT_SHIPPING_LABELS = "GET_VENDOR_DIRECT_FULFILLMENT_SHIPPING_LABELS"
    GET_VENDOR_DIRECT_FULFILLMENT_INVOICING_LABELS = "GET_VENDOR_DIRECT_FULFILLMENT_INVOICING_LABELS"

class ProcessingStatus:
    """Report processing status values."""
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    FATAL = "FATAL"

# Request models for different endpoints
class GetReportsRequest(AmazonBaseModel):
    """Get reports request parameters."""
    reportTypes: Optional[List[str]] = None
    processingStatuses: Optional[List[str]] = None
    marketplaceIds: Optional[List[str]] = None
    pageSize: Optional[int] = Field(default=10, ge=1, le=100)
    createdSince: Optional[str] = None
    createdUntil: Optional[str] = None
    nextToken: Optional[str] = None

class CreateReportScheduleRequest(AmazonBaseModel):
    """Create report schedule request."""
    reportType: str
    marketplaceIds: List[str]
    reportOptions: Optional[Dict[str, str]] = None
    period: str = Field(description="Schedule period (NEVER, EVERY_15_MINUTES, EVERY_30_MINUTES, HOURLY, EVERY_2_HOURS, EVERY_4_HOURS, EVERY_8_HOURS, EVERY_12_HOURS, DAILY, EVERY_2_DAYS, EVERY_3_DAYS, WEEKLY, EVERY_14_DAYS, EVERY_15_DAYS, EVERY_30_DAYS)")
    nextReportCreationTime: Optional[str] = None

class ReportSchedule(AmazonBaseModel):
    """Report schedule model."""
    reportScheduleId: str
    reportType: str
    marketplaceIds: List[str]
    reportOptions: Optional[Dict[str, str]] = None
    period: str
    nextReportCreationTime: Optional[str] = None

class ReportScheduleResponse(AmazonBaseModel):
    """Report schedule response."""
    payload: ReportSchedule

class ReportSchedulesListResponse(AmazonBaseModel):
    """Report schedules list response."""
    payload: Dict[str, Any] = Field(description="Report schedules list payload")
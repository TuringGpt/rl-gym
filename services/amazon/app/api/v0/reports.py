"""
Amazon SP-API Reports 2021-06-30 endpoints
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.auth import get_amazon_user, require_amazon_scopes
from utils.response_formatter import amazon_formatter
from utils.rate_limiter import check_amazon_rate_limit

# Import local modules
from app.database.connection import get_db
from app.services.report_service import ReportService
from app.models.reports import ReportRequest, ReportResponse, ReportDocumentResponse

router = APIRouter()

@router.post("/reports")
async def create_report(
    request: Request,
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Create a report.
    
    Creates a report of the type that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Create report via service
    report_service = ReportService(db)
    report = await report_service.create_report(
        report_type=report_request.reportType,
        marketplace_ids=report_request.marketplaceIds,
        data_start_time=report_request.dataStartTime,
        data_end_time=report_request.dataEndTime,
        report_options=report_request.reportOptions
    )
    
    # Format response
    return amazon_formatter.reports_response(report)

@router.get("/reports")
async def get_reports(
    request: Request,
    db: Session = Depends(get_db),
    reportTypes: Optional[str] = Query(None, description="Comma-separated list of report types"),
    processingStatuses: Optional[str] = Query(None, description="Comma-separated list of processing statuses"),
    marketplaceIds: Optional[str] = Query(None, description="Comma-separated list of marketplace IDs"),
    pageSize: Optional[int] = Query(10, ge=1, le=100, description="Number of reports to return"),
    createdSince: Optional[str] = Query(None, description="Earliest report creation date"),
    createdUntil: Optional[str] = Query(None, description="Latest report creation date"),
    nextToken: Optional[str] = Query(None, description="Next token for pagination"),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Get reports.
    
    Returns report details (including the reportDocumentId, if available) for the reports that match the filters that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Parse filters
    filters = {}
    
    if reportTypes:
        filters["report_types"] = reportTypes.split(",")
    if processingStatuses:
        filters["processing_statuses"] = processingStatuses.split(",")
    if marketplaceIds:
        filters["marketplace_ids"] = marketplaceIds.split(",")
    if createdSince:
        filters["created_since"] = createdSince
    if createdUntil:
        filters["created_until"] = createdUntil
    
    # Get reports from service
    report_service = ReportService(db)
    result = await report_service.get_reports(
        filters=filters,
        page_size=pageSize,
        next_token=nextToken
    )
    
    # Format response
    return {
        "payload": {
            "reports": result["reports"],
            "nextToken": result.get("next_token")
        }
    }

@router.get("/reports/{reportId}")
async def get_report(
    reportId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Get report.
    
    Returns report details for the report that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Get report from service
    report_service = ReportService(db)
    report = await report_service.get_report_by_id(reportId)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Report {reportId} not found"
            ).body.decode()
        )
    
    # Format response
    return amazon_formatter.reports_response(report)

@router.delete("/reports/{reportId}")
async def cancel_report(
    reportId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Cancel report.
    
    Cancels the report that you specify. Only reports with processingStatus=IN_QUEUE can be cancelled.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Cancel report via service
    report_service = ReportService(db)
    result = await report_service.cancel_report(reportId)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Report {reportId} not found or cannot be cancelled"
            ).body.decode()
        )
    
    return {
        "payload": {
            "reportId": reportId,
            "processingStatus": "CANCELLED"
        }
    }

@router.get("/documents/{reportDocumentId}")
async def get_report_document(
    reportDocumentId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Get report document.
    
    Returns the information required for retrieving a report document's contents.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Get report document from service
    report_service = ReportService(db)
    document = await report_service.get_report_document(reportDocumentId)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Report document {reportDocumentId} not found"
            ).body.decode()
        )
    
    # Format response
    return {
        "payload": {
            "reportDocumentId": reportDocumentId,
            "url": document["url"],
            "encryptionDetails": document.get("encryption_details"),
            "compressionAlgorithm": document.get("compression_algorithm")
        }
    }

@router.post("/reportSchedules")
async def create_report_schedule(
    request: Request,
    schedule_request: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Create report schedule.
    
    Creates a report schedule of the type that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Create report schedule via service
    report_service = ReportService(db)
    schedule = await report_service.create_report_schedule(
        report_type=schedule_request["reportType"],
        marketplace_ids=schedule_request["marketplaceIds"],
        period=schedule_request["period"],
        report_options=schedule_request.get("reportOptions"),
        next_report_creation_time=schedule_request.get("nextReportCreationTime")
    )
    
    # Format response
    return {
        "payload": schedule
    }

@router.get("/reportSchedules")
async def get_report_schedules(
    request: Request,
    db: Session = Depends(get_db),
    reportTypes: Optional[str] = Query(None, description="Comma-separated list of report types"),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Get report schedules.
    
    Returns report schedule details that match the filters that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Parse filters
    filters = {}
    if reportTypes:
        filters["report_types"] = reportTypes.split(",")
    
    # Get report schedules from service
    report_service = ReportService(db)
    schedules = await report_service.get_report_schedules(filters)
    
    # Format response
    return {
        "payload": {
            "reportSchedules": schedules
        }
    }

@router.get("/reportSchedules/{reportScheduleId}")
async def get_report_schedule(
    reportScheduleId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Get report schedule.
    
    Returns report schedule details for the report schedule that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Get report schedule from service
    report_service = ReportService(db)
    schedule = await report_service.get_report_schedule_by_id(reportScheduleId)
    
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Report schedule {reportScheduleId} not found"
            ).body.decode()
        )
    
    # Format response
    return {
        "payload": schedule
    }

@router.delete("/reportSchedules/{reportScheduleId}")
async def cancel_report_schedule(
    reportScheduleId: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_amazon_scopes(["sellingpartnerapi::reports"]))
):
    """
    Cancel report schedule.
    
    Cancels the report schedule that you specify.
    """
    
    # Check rate limits
    await check_amazon_rate_limit(request)
    
    # Cancel report schedule via service
    report_service = ReportService(db)
    result = await report_service.cancel_report_schedule(reportScheduleId)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=amazon_formatter.error_response(
                "ResourceNotFound",
                f"Report schedule {reportScheduleId} not found"
            ).body.decode()
        )
    
    return {
        "payload": {
            "reportScheduleId": reportScheduleId,
            "status": "CANCELLED"
        }
    }
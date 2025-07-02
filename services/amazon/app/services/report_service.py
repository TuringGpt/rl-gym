"""
Report service for Amazon SP-API Mock
Handles report-related business logic and database operations
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from app.database.schemas import Report

class ReportService:
    """Service for handling report operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_report(self, report_type: str, marketplace_ids: List[str],
                          data_start_time: str = None, data_end_time: str = None,
                          report_options: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a new report."""
        
        report_id = f"RPT-{str(uuid.uuid4())[:8].upper()}-{datetime.now().year}"
        
        report = Report(
            report_id=report_id,
            report_type=report_type,
            processing_status="IN_QUEUE",
            created_time=datetime.utcnow(),
            marketplace_ids=",".join(marketplace_ids)
        )
        
        self.db.add(report)
        self.db.commit()
        
        # Simulate report processing
        await self._simulate_report_processing(report)
        
        return self._format_report(report)
    
    async def get_reports(self, filters: Dict[str, Any], page_size: int = 10,
                         next_token: str = None) -> Dict[str, Any]:
        """Get reports with filtering."""
        
        query = self.db.query(Report)
        
        # Apply filters
        if "report_types" in filters:
            query = query.filter(Report.report_type.in_(filters["report_types"]))
        if "processing_statuses" in filters:
            query = query.filter(Report.processing_status.in_(filters["processing_statuses"]))
        if "marketplace_ids" in filters:
            # Simple contains filter for marketplace IDs
            for marketplace_id in filters["marketplace_ids"]:
                query = query.filter(Report.marketplace_ids.contains(marketplace_id))
        if "created_since" in filters:
            query = query.filter(Report.created_time >= filters["created_since"])
        if "created_until" in filters:
            query = query.filter(Report.created_time <= filters["created_until"])
        
        # Handle pagination
        offset = 0
        if next_token:
            try:
                offset = int(next_token)
            except (ValueError, TypeError):
                offset = 0
        
        total_count = query.count()
        reports_query = query.offset(offset).limit(page_size)
        reports = reports_query.all()
        
        # Format reports
        reports_data = []
        for report in reports:
            report_dict = self._format_report(report)
            reports_data.append(report_dict)
        
        # Calculate next token
        new_next_token = None
        if offset + page_size < total_count:
            new_next_token = str(offset + page_size)
        
        return {
            "reports": reports_data,
            "next_token": new_next_token
        }
    
    async def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID."""
        report = self.db.query(Report).filter(Report.report_id == report_id).first()
        
        if not report:
            return None
        
        return self._format_report(report)
    
    async def cancel_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a report."""
        report = self.db.query(Report).filter(Report.report_id == report_id).first()
        
        if not report or report.processing_status not in ["IN_QUEUE", "IN_PROGRESS"]:
            return None
        
        report.processing_status = "CANCELLED"
        self.db.commit()
        
        return self._format_report(report)
    
    async def get_report_document(self, report_document_id: str) -> Optional[Dict[str, Any]]:
        """Get report document details."""
        # In a real implementation, this would fetch from document storage
        # For mock purposes, return a simulated document URL
        
        return {
            "url": f"https://mock-amazon-reports.s3.amazonaws.com/{report_document_id}.csv",
            "encryption_details": None,
            "compression_algorithm": None
        }
    
    async def create_report_schedule(self, report_type: str, marketplace_ids: List[str],
                                   period: str, report_options: Dict[str, str] = None,
                                   next_report_creation_time: str = None) -> Dict[str, Any]:
        """Create a report schedule."""
        schedule_id = f"schedule_{str(uuid.uuid4())[:8]}"
        
        # Mock schedule creation
        return {
            "reportScheduleId": schedule_id,
            "reportType": report_type,
            "marketplaceIds": marketplace_ids,
            "reportOptions": report_options or {},
            "period": period,
            "nextReportCreationTime": next_report_creation_time or (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
        }
    
    async def get_report_schedules(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get report schedules."""
        # Mock implementation
        return [
            {
                "reportScheduleId": "schedule_12345678",
                "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "marketplaceIds": ["ATVPDKIKX0DER"],
                "reportOptions": {},
                "period": "DAILY",
                "nextReportCreationTime": (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
            }
        ]
    
    async def get_report_schedule_by_id(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report schedule."""
        # Mock implementation
        if schedule_id.startswith("schedule_"):
            return {
                "reportScheduleId": schedule_id,
                "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "marketplaceIds": ["ATVPDKIKX0DER"],
                "reportOptions": {},
                "period": "DAILY",
                "nextReportCreationTime": (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
            }
        return None
    
    async def cancel_report_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a report schedule."""
        schedule = await self.get_report_schedule_by_id(schedule_id)
        if schedule:
            return {"reportScheduleId": schedule_id, "status": "CANCELLED"}
        return None
    
    async def _simulate_report_processing(self, report: Report):
        """Simulate report processing with some delay."""
        # For demo purposes, randomly set processing status
        import random
        
        # 80% chance of success, 20% chance of various states
        rand = random.random()
        
        if rand < 0.8:
            # Successful processing
            report.processing_status = "DONE"
            report.processing_start_time = datetime.utcnow()
            report.processing_end_time = datetime.utcnow() + timedelta(minutes=5)
            report.report_document_url = f"https://mock-amazon-reports.s3.amazonaws.com/{report.report_id}.csv"
        elif rand < 0.9:
            # Still in progress
            report.processing_status = "IN_PROGRESS"
            report.processing_start_time = datetime.utcnow()
        else:
            # Fatal error
            report.processing_status = "FATAL"
            report.processing_start_time = datetime.utcnow()
            report.processing_end_time = datetime.utcnow() + timedelta(minutes=1)
        
        self.db.commit()
    
    def _format_report(self, report: Report) -> Dict[str, Any]:
        """Format report for API response."""
        return {
            "reportId": report.report_id,
            "reportType": report.report_type,
            "dataStartTime": None,  # Would be set from request
            "dataEndTime": None,    # Would be set from request
            "marketplaceIds": report.marketplace_ids.split(",") if report.marketplace_ids else [],
            "processingStatus": report.processing_status,
            "processingStartTime": report.processing_start_time.isoformat() + "Z" if report.processing_start_time else None,
            "processingEndTime": report.processing_end_time.isoformat() + "Z" if report.processing_end_time else None,
            "reportDocumentId": report.report_document_url.split("/")[-1].replace(".csv", "") if report.report_document_url else None,
            "createdTime": report.created_time.isoformat() + "Z"
        }
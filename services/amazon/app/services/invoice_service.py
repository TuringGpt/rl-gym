"""
Invoice Service for Amazon SP-API Mock Service
Handles business logic and async operations for invoices
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select
from app.database.schemas import Invoice, InvoiceDocument, InvoiceExport, InvoiceAttribute
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)

class InvoiceService:
    """Service class for handling invoice operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_invoices_attributes(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all available invoice attributes for filtering
        """
        try:
            attributes = self.db.query(InvoiceAttribute).all()
            
            # Group attributes by type
            grouped_attributes = {
                'status': [],
                'invoice_type': [],
                'transaction_identifier_name': [],
                'transaction_type': []
            }
            
            for attr in attributes:
                if attr.attribute_type in grouped_attributes:
                    grouped_attributes[attr.attribute_type].append({
                        'description': attr.description,
                        'value': attr.value
                    })
            
            return grouped_attributes
            
        except Exception as e:
            logger.error(f"Error getting invoice attributes: {e}")
            raise
    
    async def get_invoice_document(self, document_id: str) -> Optional[InvoiceDocument]:
        """
        Get invoice document by ID
        """
        try:
            document = self.db.query(InvoiceDocument).filter(
                InvoiceDocument.document_id == document_id
            ).first()
            
            return document
            
        except Exception as e:
            logger.error(f"Error getting invoice document {document_id}: {e}")
            raise
    
    async def create_invoice_export(self, filters: Dict[str, Any] = None) -> str:
        """
        Create a new invoice export job
        """
        try:
            export_id = str(uuid.uuid4())
            
            export = InvoiceExport(
                export_id=export_id,
                status="REQUESTED",
                generate_export_started_at=datetime.now(),
                request_filters=filters or {}
            )
            
            self.db.add(export)
            self.db.commit()
            
            # Start background processing
            asyncio.create_task(self._process_export_async(export_id))
            
            return export_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice export: {e}")
            raise
    
    async def _process_export_async(self, export_id: str):
        """
        Process export in background
        """
        try:
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Update export status
            export = self.db.query(InvoiceExport).filter(
                InvoiceExport.export_id == export_id
            ).first()
            
            if export:
                export.status = "COMPLETED"
                export.generate_export_finished_at = datetime.now()
                export.invoices_document_ids = [
                    f"DOC_{uuid.uuid4()}",
                    f"DOC_{uuid.uuid4()}"
                ]
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error processing export {export_id}: {e}")
            # Update export with error
            try:
                export = self.db.query(InvoiceExport).filter(
                    InvoiceExport.export_id == export_id
                ).first()
                
                if export:
                    export.status = "FAILED"
                    export.error_message = str(e)
                    export.generate_export_finished_at = datetime.now()
                    self.db.commit()
            except Exception:
                pass
    
    async def get_invoice_exports(self, 
                                 next_token: Optional[str] = None,
                                 max_results: int = 100) -> tuple[List[InvoiceExport], Optional[str]]:
        """
        Get list of invoice exports with pagination
        """
        try:
            query = self.db.query(InvoiceExport)
            
            if next_token:
                # Simple pagination - in production, use cursor-based pagination
                offset = int(next_token) * max_results
                query = query.offset(offset)
            
            exports = query.limit(max_results).all()
            
            # Calculate next token
            next_token_value = None
            if len(exports) == max_results:
                current_page = int(next_token) if next_token else 0
                next_token_value = str(current_page + 1)
            
            return exports, next_token_value
            
        except Exception as e:
            logger.error(f"Error getting invoice exports: {e}")
            raise
    
    async def get_invoice_export(self, export_id: str) -> Optional[InvoiceExport]:
        """
        Get specific invoice export by ID
        """
        try:
            export = self.db.query(InvoiceExport).filter(
                InvoiceExport.export_id == export_id
            ).first()
            
            return export
            
        except Exception as e:
            logger.error(f"Error getting invoice export {export_id}: {e}")
            raise
    
    async def get_invoices(self,
                          statuses: Optional[List[str]] = None,
                          invoice_type: Optional[str] = None,
                          transaction_type: Optional[str] = None,
                          date_start: Optional[datetime] = None,
                          date_end: Optional[datetime] = None,
                          next_token: Optional[str] = None,
                          max_results: int = 100) -> tuple[List[Invoice], Optional[str]]:
        """
        Get invoices with filtering and pagination
        """
        try:
            query = self.db.query(Invoice)
            
            # Apply filters
            if statuses:
                query = query.filter(Invoice.status.in_(statuses))
            
            if invoice_type:
                query = query.filter(Invoice.invoice_type == invoice_type)
            
            if transaction_type:
                query = query.filter(Invoice.transaction_type == transaction_type)
            
            if date_start:
                query = query.filter(Invoice.date >= date_start)
            
            if date_end:
                query = query.filter(Invoice.date <= date_end)
            
            # Apply pagination
            if next_token:
                offset = int(next_token) * max_results
                query = query.offset(offset)
            
            invoices = query.limit(max_results).all()
            
            # Calculate next token
            next_token_value = None
            if len(invoices) == max_results:
                current_page = int(next_token) if next_token else 0
                next_token_value = str(current_page + 1)
            
            return invoices, next_token_value
            
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            raise
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Get specific invoice by ID
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            return invoice
            
        except Exception as e:
            logger.error(f"Error getting invoice {invoice_id}: {e}")
            raise
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Invoice:
        """
        Create a new invoice
        """
        try:
            invoice = Invoice(
                id=invoice_data['id'],
                date=invoice_data['date'],
                invoice_type=invoice_data['invoice_type'],
                status=invoice_data['status'],
                transaction_type=invoice_data['transaction_type'],
                external_invoice_id=invoice_data.get('external_invoice_id'),
                series=invoice_data.get('series'),
                transaction_ids=invoice_data.get('transaction_ids', []),
                error_code=invoice_data.get('error_code'),
                gov_response=invoice_data.get('gov_response')
            )
            
            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)
            
            return invoice
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice: {e}")
            raise
    
    async def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> Optional[Invoice]:
        """
        Update an existing invoice
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            if not invoice:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(invoice, key):
                    setattr(invoice, key, value)
            
            self.db.commit()
            self.db.refresh(invoice)
            
            return invoice
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating invoice {invoice_id}: {e}")
            raise
    
    async def delete_invoice(self, invoice_id: str) -> bool:
        """
        Delete an invoice
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            if not invoice:
                return False
            
            self.db.delete(invoice)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting invoice {invoice_id}: {e}")
            raise
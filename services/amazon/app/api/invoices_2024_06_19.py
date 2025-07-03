"""
Amazon Invoices API v2024-06-19
Based on: https://developer-docs.amazon.com/sp-api/docs/invoices-api-reference
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.database.connection import get_db, get_async_db
from app.database.schemas import Invoice, InvoiceExport, InvoiceDocument, InvoiceAttribute
from app.services.invoice_service import InvoiceService
import sys
from pathlib import Path as FilePath
import uuid
import asyncio

# Add shared directory to Python path
shared_path = FilePath(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.response_formatter import amazon_formatter

router = APIRouter(prefix="/tax/invoices/2024-06-19", tags=["Invoices"])

# Request/Response Models
class InvoiceOptionValue(BaseModel):
    description: str
    value: str

class InvoicesAttributes(BaseModel):
    invoice_status_options: List[InvoiceOptionValue] = Field(alias="invoiceStatusOptions")
    invoice_type_options: List[InvoiceOptionValue] = Field(alias="invoiceTypeOptions")
    transaction_identifier_name_options: List[InvoiceOptionValue] = Field(alias="transactionIdentifierNameOptions")
    transaction_type_options: List[InvoiceOptionValue] = Field(alias="transactionTypeOptions")

class GetInvoicesAttributesResponse(BaseModel):
    invoices_attributes: InvoicesAttributes = Field(alias="invoicesAttributes")

class InvoicesDocument(BaseModel):
    invoices_document_id: str = Field(alias="invoicesDocumentId")
    invoices_document_url: str = Field(alias="invoicesDocumentUrl")

class GetInvoicesDocumentResponse(BaseModel):
    invoices_document: InvoicesDocument = Field(alias="invoicesDocument")

class CreateInvoicesExportResponse(BaseModel):
    export_id: str = Field(alias="exportId")

class TransactionId(BaseModel):
    name: str
    id: str

class InvoiceDetails(BaseModel):
    date: datetime
    error_code: Optional[str] = Field(None, alias="errorCode")
    external_invoice_id: Optional[str] = Field(None, alias="externalInvoiceId")
    gov_response: Optional[str] = Field(None, alias="govResponse")
    id: str
    invoice_type: str = Field(alias="invoiceType")
    series: Optional[str] = None
    status: str
    transaction_ids: List[TransactionId] = Field(alias="transactionIds")
    transaction_type: str = Field(alias="transactionType")

class GetInvoicesResponse(BaseModel):
    invoices: List[InvoiceDetails]
    next_token: Optional[str] = Field(None, alias="nextToken")

class GetInvoiceResponse(BaseModel):
    invoice: InvoiceDetails

class ExportDetails(BaseModel):
    error_message: Optional[str] = Field(None, alias="errorMessage")
    export_id: str = Field(alias="exportId")
    generate_export_finished_at: Optional[datetime] = Field(None, alias="generateExportFinishedAt")
    generate_export_started_at: Optional[datetime] = Field(None, alias="generateExportStartedAt")
    invoices_document_ids: List[str] = Field(alias="invoicesDocumentIds")
    status: str

class GetInvoicesExportsResponse(BaseModel):
    exports: List[ExportDetails]
    next_token: Optional[str] = Field(None, alias="nextToken")

class GetInvoicesExportResponse(BaseModel):
    export: ExportDetails

# API Endpoints

@router.get("/attributes", response_model=GetInvoicesAttributesResponse)
async def get_invoices_attributes(
    db: Session = Depends(get_db)
):
    """
    Returns attributes that can be used to filter invoices.
    """
    try:
        service = InvoiceService(db)
        grouped_attributes = await service.get_invoices_attributes()
        
        status_options = [
            InvoiceOptionValue(description=attr['description'], value=attr['value'])
            for attr in grouped_attributes.get('status', [])
        ]
        
        type_options = [
            InvoiceOptionValue(description=attr['description'], value=attr['value'])
            for attr in grouped_attributes.get('invoice_type', [])
        ]
        
        transaction_name_options = [
            InvoiceOptionValue(description=attr['description'], value=attr['value'])
            for attr in grouped_attributes.get('transaction_identifier_name', [])
        ]
        
        transaction_type_options = [
            InvoiceOptionValue(description=attr['description'], value=attr['value'])
            for attr in grouped_attributes.get('transaction_type', [])
        ]
        
        # If no attributes in DB, return default values
        if not any(grouped_attributes.values()):
            status_options = [
                InvoiceOptionValue(description="Pending", value="PENDING"),
                InvoiceOptionValue(description="Approved", value="APPROVED"),
                InvoiceOptionValue(description="Rejected", value="REJECTED"),
                InvoiceOptionValue(description="Cancelled", value="CANCELLED")
            ]
            
            type_options = [
                InvoiceOptionValue(description="Tax Invoice", value="TAX_INVOICE"),
                InvoiceOptionValue(description="Credit Note", value="CREDIT_NOTE"),
                InvoiceOptionValue(description="Debit Note", value="DEBIT_NOTE")
            ]
            
            transaction_name_options = [
                InvoiceOptionValue(description="Order ID", value="ORDER_ID"),
                InvoiceOptionValue(description="Shipment ID", value="SHIPMENT_ID"),
                InvoiceOptionValue(description="Refund ID", value="REFUND_ID")
            ]
            
            transaction_type_options = [
                InvoiceOptionValue(description="Sale", value="SALE"),
                InvoiceOptionValue(description="Return", value="RETURN"),
                InvoiceOptionValue(description="Refund", value="REFUND")
            ]
        
        invoices_attributes = InvoicesAttributes(
            invoiceStatusOptions=status_options,
            invoiceTypeOptions=type_options,
            transactionIdentifierNameOptions=transaction_name_options,
            transactionTypeOptions=transaction_type_options
        )
        
        return GetInvoicesAttributesResponse(invoicesAttributes=invoices_attributes)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{invoices_document_id}", response_model=GetInvoicesDocumentResponse)
async def get_invoices_document(
    invoices_document_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns a link to download the invoice document.
    """
    try:
        service = InvoiceService(db)
        document = await service.get_invoice_document(invoices_document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Invoice document not found")
        
        invoices_document = InvoicesDocument(
            invoicesDocumentId=document.document_id,
            invoicesDocumentUrl=document.document_url
        )
        
        return GetInvoicesDocumentResponse(invoicesDocument=invoices_document)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exports", response_model=CreateInvoicesExportResponse)
async def create_invoices_export(
    request: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """
    Creates an invoice export job.
    """
    try:
        service = InvoiceService(db)
        export_id = await service.create_invoice_export(request)
        
        return CreateInvoicesExportResponse(exportId=export_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exports", response_model=GetInvoicesExportsResponse)
async def get_invoices_exports(
    next_token: Optional[str] = Query(None, description="Token for pagination"),
    max_results: Optional[int] = Query(100, description="Maximum number of results per page"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of invoice exports.
    """
    try:
        service = InvoiceService(db)
        exports, next_token_value = await service.get_invoice_exports(next_token, max_results)
        
        export_details = []
        for export in exports:
            export_detail = ExportDetails(
                exportId=export.export_id,
                status=export.status,
                generateExportStartedAt=export.generate_export_started_at,
                generateExportFinishedAt=export.generate_export_finished_at,
                invoicesDocumentIds=export.invoices_document_ids or [],
                errorMessage=export.error_message
            )
            export_details.append(export_detail)
        
        return GetInvoicesExportsResponse(
            exports=export_details,
            nextToken=next_token_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exports/{export_id}", response_model=GetInvoicesExportResponse)
async def get_invoices_export(
    export_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns details of a specific invoice export.
    """
    try:
        service = InvoiceService(db)
        export = await service.get_invoice_export(export_id)
        
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")
        
        export_detail = ExportDetails(
            exportId=export.export_id,
            status=export.status,
            generateExportStartedAt=export.generate_export_started_at,
            generateExportFinishedAt=export.generate_export_finished_at,
            invoicesDocumentIds=export.invoices_document_ids or [],
            errorMessage=export.error_message
        )
        
        return GetInvoicesExportResponse(export=export_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices", response_model=GetInvoicesResponse)
async def get_invoices(
    statuses: Optional[List[str]] = Query(None, description="Filter by invoice status"),
    invoice_type: Optional[str] = Query(None, description="Filter by invoice type"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    date_start: Optional[datetime] = Query(None, description="Filter by date range start"),
    date_end: Optional[datetime] = Query(None, description="Filter by date range end"),
    next_token: Optional[str] = Query(None, description="Token for pagination"),
    max_results: Optional[int] = Query(100, description="Maximum number of results per page"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of invoices based on the specified filters.
    """
    try:
        service = InvoiceService(db)
        invoices, next_token_value = await service.get_invoices(
            statuses=statuses,
            invoice_type=invoice_type,
            transaction_type=transaction_type,
            date_start=date_start,
            date_end=date_end,
            next_token=next_token,
            max_results=max_results
        )
        
        # Convert to response format
        invoice_details = []
        for invoice in invoices:
            transaction_ids = []
            if invoice.transaction_ids:
                for tid in invoice.transaction_ids:
                    transaction_ids.append(TransactionId(
                        name=tid.get("name", ""),
                        id=tid.get("id", "")
                    ))
            
            invoice_detail = InvoiceDetails(
                date=invoice.date,
                errorCode=invoice.error_code,
                externalInvoiceId=invoice.external_invoice_id,
                govResponse=invoice.gov_response,
                id=invoice.id,
                invoiceType=invoice.invoice_type,
                series=invoice.series,
                status=invoice.status,
                transactionIds=transaction_ids,
                transactionType=invoice.transaction_type
            )
            invoice_details.append(invoice_detail)
        
        return GetInvoicesResponse(
            invoices=invoice_details,
            nextToken=next_token_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices/{invoice_id}", response_model=GetInvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns details of a specific invoice.
    """
    try:
        service = InvoiceService(db)
        invoice = await service.get_invoice(invoice_id)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Convert transaction IDs
        transaction_ids = []
        if invoice.transaction_ids:
            for tid in invoice.transaction_ids:
                transaction_ids.append(TransactionId(
                    name=tid.get("name", ""),
                    id=tid.get("id", "")
                ))
        
        invoice_detail = InvoiceDetails(
            date=invoice.date,
            errorCode=invoice.error_code,
            externalInvoiceId=invoice.external_invoice_id,
            govResponse=invoice.gov_response,
            id=invoice.id,
            invoiceType=invoice.invoice_type,
            series=invoice.series,
            status=invoice.status,
            transactionIds=transaction_ids,
            transactionType=invoice.transaction_type
        )
        
        return GetInvoiceResponse(invoice=invoice_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
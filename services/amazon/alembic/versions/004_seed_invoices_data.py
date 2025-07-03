"""seed invoices data

Revision ID: 004
Revises: 003
Create Date: 2025-01-07 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta
import uuid
import json

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # Insert invoice attributes
    invoice_attributes_data = [
        # Status options
        ('status', 'PENDING', 'Pending'),
        ('status', 'APPROVED', 'Approved'),
        ('status', 'REJECTED', 'Rejected'),
        ('status', 'CANCELLED', 'Cancelled'),
        ('status', 'PROCESSING', 'Processing'),
        
        # Invoice type options
        ('invoice_type', 'TAX_INVOICE', 'Tax Invoice'),
        ('invoice_type', 'CREDIT_NOTE', 'Credit Note'),
        ('invoice_type', 'DEBIT_NOTE', 'Debit Note'),
        ('invoice_type', 'COMMERCIAL_INVOICE', 'Commercial Invoice'),
        
        # Transaction identifier name options
        ('transaction_identifier_name', 'ORDER_ID', 'Order ID'),
        ('transaction_identifier_name', 'SHIPMENT_ID', 'Shipment ID'),
        ('transaction_identifier_name', 'REFUND_ID', 'Refund ID'),
        ('transaction_identifier_name', 'ADJUSTMENT_ID', 'Adjustment ID'),
        
        # Transaction type options
        ('transaction_type', 'SALE', 'Sale'),
        ('transaction_type', 'RETURN', 'Return'),
        ('transaction_type', 'REFUND', 'Refund'),
        ('transaction_type', 'ADJUSTMENT', 'Adjustment'),
    ]
    
    for attr_type, value, description in invoice_attributes_data:
        connection.execute(
            sa.text("""
                INSERT INTO invoice_attributes (attribute_type, value, description, created_at, updated_at)
                VALUES (:attr_type, :value, :description, :created_at, :updated_at)
            """),
            {
                'attr_type': attr_type,
                'value': value,
                'description': description,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        )
    
    # Generate sample invoices
    base_date = datetime.now() - timedelta(days=90)
    
    invoice_data = []
    for i in range(50):
        invoice_id = f"INV-{i+1:05d}"
        invoice_date = base_date + timedelta(days=i * 2)
        
        # Rotate through different types and statuses
        invoice_types = ['TAX_INVOICE', 'CREDIT_NOTE', 'DEBIT_NOTE', 'COMMERCIAL_INVOICE']
        statuses = ['PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'PROCESSING']
        transaction_types = ['SALE', 'RETURN', 'REFUND', 'ADJUSTMENT']
        
        invoice_type = invoice_types[i % len(invoice_types)]
        status = statuses[i % len(statuses)]
        transaction_type = transaction_types[i % len(transaction_types)]
        
        # Generate transaction IDs
        transaction_ids = [
            {
                'name': 'ORDER_ID',
                'id': f'ORDER-{i+1:05d}'
            },
            {
                'name': 'SHIPMENT_ID',
                'id': f'SHIP-{i+1:05d}'
            }
        ]
        
        invoice_data.append({
            'id': invoice_id,
            'date': invoice_date,
            'error_code': None if status != 'REJECTED' else f'ERR-{i+1:03d}',
            'external_invoice_id': f'EXT-{invoice_id}',
            'gov_response': f'GOV-RESPONSE-{i+1:05d}' if status == 'APPROVED' else None,
            'invoice_type': invoice_type,
            'series': f'SERIES-{(i % 10) + 1}',
            'status': status,
            'transaction_ids': json.dumps(transaction_ids),
            'transaction_type': transaction_type,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    # Insert invoices
    for invoice in invoice_data:
        connection.execute(
            sa.text("""
                INSERT INTO invoices (id, date, error_code, external_invoice_id, gov_response, 
                                    invoice_type, series, status, transaction_ids, transaction_type, 
                                    created_at, updated_at)
                VALUES (:id, :date, :error_code, :external_invoice_id, :gov_response, 
                        :invoice_type, :series, :status, :transaction_ids, :transaction_type, 
                        :created_at, :updated_at)
            """),
            invoice
        )
    
    # Generate sample invoice documents
    document_data = []
    for i in range(30):  # Not all invoices have documents
        invoice_id = f"INV-{i+1:05d}"
        document_id = f"DOC-{i+1:05d}"
        
        document_data.append({
            'document_id': document_id,
            'invoice_id': invoice_id,
            'document_url': f'https://mock-amazon-docs.s3.amazonaws.com/invoices/{document_id}.pdf',
            'document_type': 'PDF',
            'file_size': 1024 * (i + 1),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    # Insert invoice documents
    for document in document_data:
        connection.execute(
            sa.text("""
                INSERT INTO invoice_documents (document_id, invoice_id, document_url, document_type, 
                                             file_size, created_at, updated_at)
                VALUES (:document_id, :invoice_id, :document_url, :document_type, 
                        :file_size, :created_at, :updated_at)
            """),
            document
        )
    
    # Generate sample invoice exports
    export_data = []
    for i in range(10):
        export_id = str(uuid.uuid4())
        started_at = datetime.now() - timedelta(hours=i * 2)
        finished_at = started_at + timedelta(minutes=30) if i < 7 else None
        
        export_data.append({
            'export_id': export_id,
            'status': 'COMPLETED' if finished_at else 'IN_PROGRESS',
            'generate_export_started_at': started_at,
            'generate_export_finished_at': finished_at,
            'invoices_document_ids': json.dumps([f'DOC-{j+1:05d}' for j in range(i*3, (i+1)*3)]),
            'error_message': None,
            'request_filters': json.dumps({'status': ['APPROVED'], 'invoice_type': 'TAX_INVOICE'}),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    # Insert invoice exports
    for export in export_data:
        connection.execute(
            sa.text("""
                INSERT INTO invoice_exports (export_id, status, generate_export_started_at, 
                                           generate_export_finished_at, invoices_document_ids, 
                                           error_message, request_filters, created_at, updated_at)
                VALUES (:export_id, :status, :generate_export_started_at, 
                        :generate_export_finished_at, :invoices_document_ids, 
                        :error_message, :request_filters, :created_at, :updated_at)
            """),
            export
        )


def downgrade():
    # Delete all seeded data
    connection = op.get_bind()
    
    connection.execute(sa.text("DELETE FROM invoice_documents"))
    connection.execute(sa.text("DELETE FROM invoice_exports"))
    connection.execute(sa.text("DELETE FROM invoices"))
    connection.execute(sa.text("DELETE FROM invoice_attributes"))
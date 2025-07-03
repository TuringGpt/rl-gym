"""add invoices tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-07 15:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create invoices table
    op.create_table('invoices',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('error_code', sa.String(length=100), nullable=True),
    sa.Column('external_invoice_id', sa.String(length=100), nullable=True),
    sa.Column('gov_response', sa.Text(), nullable=True),
    sa.Column('invoice_type', sa.String(length=50), nullable=False),
    sa.Column('series', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('transaction_ids', sa.JSON(), nullable=True),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create invoice_documents table
    op.create_table('invoice_documents',
    sa.Column('document_id', sa.String(length=50), nullable=False),
    sa.Column('invoice_id', sa.String(length=50), nullable=False),
    sa.Column('document_url', sa.Text(), nullable=False),
    sa.Column('document_type', sa.String(length=50), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.PrimaryKeyConstraint('document_id')
    )
    
    # Create invoice_exports table
    op.create_table('invoice_exports',
    sa.Column('export_id', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('generate_export_started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('generate_export_finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('invoices_document_ids', sa.JSON(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('request_filters', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('export_id')
    )
    
    # Create invoice_attributes table
    op.create_table('invoice_attributes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('attribute_type', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for better performance
    op.create_index('idx_invoices_status', 'invoices', ['status'])
    op.create_index('idx_invoices_type', 'invoices', ['invoice_type'])
    op.create_index('idx_invoices_date', 'invoices', ['date'])
    op.create_index('idx_invoices_transaction_type', 'invoices', ['transaction_type'])
    op.create_index('idx_invoice_exports_status', 'invoice_exports', ['status'])
    op.create_index('idx_invoice_attributes_type', 'invoice_attributes', ['attribute_type'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_invoice_attributes_type', table_name='invoice_attributes')
    op.drop_index('idx_invoice_exports_status', table_name='invoice_exports')
    op.drop_index('idx_invoices_transaction_type', table_name='invoices')
    op.drop_index('idx_invoices_date', table_name='invoices')
    op.drop_index('idx_invoices_type', table_name='invoices')
    op.drop_index('idx_invoices_status', table_name='invoices')
    
    # Drop tables
    op.drop_table('invoice_attributes')
    op.drop_table('invoice_exports')
    op.drop_table('invoice_documents')
    op.drop_table('invoices')
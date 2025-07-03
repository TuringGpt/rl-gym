"""Add sales metrics table

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create sales_metrics table
    op.create_table(
        'sales_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interval', sa.String(length=100), nullable=False),
        sa.Column('granularity', sa.String(length=20), nullable=False),
        sa.Column('unit_count', sa.Integer(), nullable=True),
        sa.Column('order_item_count', sa.Integer(), nullable=True),
        sa.Column('order_count', sa.Integer(), nullable=True),
        sa.Column('average_unit_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_sales', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency_code', sa.String(length=3), nullable=True),
        sa.Column('buyer_type', sa.String(length=10), nullable=True),
        sa.Column('marketplace_ids', sa.JSON(), nullable=True),
        sa.Column('asin', sa.String(length=20), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index('ix_sales_metrics_granularity', 'sales_metrics', ['granularity'])
    op.create_index('ix_sales_metrics_buyer_type', 'sales_metrics', ['buyer_type'])
    op.create_index('ix_sales_metrics_period_start', 'sales_metrics', ['period_start'])
    op.create_index('ix_sales_metrics_period_end', 'sales_metrics', ['period_end'])
    op.create_index('ix_sales_metrics_asin', 'sales_metrics', ['asin'])
    op.create_index('ix_sales_metrics_sku', 'sales_metrics', ['sku'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_sales_metrics_sku', table_name='sales_metrics')
    op.drop_index('ix_sales_metrics_asin', table_name='sales_metrics')
    op.drop_index('ix_sales_metrics_period_end', table_name='sales_metrics')
    op.drop_index('ix_sales_metrics_period_start', table_name='sales_metrics')
    op.drop_index('ix_sales_metrics_buyer_type', table_name='sales_metrics')
    op.drop_index('ix_sales_metrics_granularity', table_name='sales_metrics')
    
    # Drop table
    op.drop_table('sales_metrics')
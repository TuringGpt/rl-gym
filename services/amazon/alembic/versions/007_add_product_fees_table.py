"""add product fees table

Revision ID: 007
Revises: 006
Create Date: 2025-01-07 17:31:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create product_fees table
    op.create_table('product_fees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('seller_sku', sa.String(length=100), nullable=True),
        sa.Column('asin', sa.String(length=20), nullable=True),
        sa.Column('marketplace_id', sa.String(length=20), nullable=False),
        sa.Column('seller_id', sa.String(length=50), nullable=False),
        sa.Column('product_type', sa.String(length=100), nullable=True),
        sa.Column('item_condition', sa.String(length=20), nullable=True),
        sa.Column('fulfillment_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('referral_fee_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('storage_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('removal_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('disposal_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('return_processing_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('high_volume_listing_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('multichannel_fulfillment_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('weight', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('dimensions', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index('idx_product_fees_seller_sku', 'product_fees', ['seller_sku'])
    op.create_index('idx_product_fees_asin', 'product_fees', ['asin'])
    op.create_index('idx_product_fees_marketplace', 'product_fees', ['marketplace_id'])
    op.create_index('idx_product_fees_seller_marketplace', 'product_fees', ['seller_sku', 'marketplace_id'])
    op.create_index('idx_product_fees_asin_marketplace', 'product_fees', ['asin', 'marketplace_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_product_fees_asin_marketplace', table_name='product_fees')
    op.drop_index('idx_product_fees_seller_marketplace', table_name='product_fees')
    op.drop_index('idx_product_fees_marketplace', table_name='product_fees')
    op.drop_index('idx_product_fees_asin', table_name='product_fees')
    op.drop_index('idx_product_fees_seller_sku', table_name='product_fees')
    
    # Drop table
    op.drop_table('product_fees')
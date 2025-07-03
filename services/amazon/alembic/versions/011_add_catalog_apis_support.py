"""add catalog apis support

Revision ID: 011_add_catalog_apis_support
Revises: 010_seed_messaging_data
Create Date: 2025-03-07 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create catalog_categories table
    op.create_table('catalog_categories',
        sa.Column('product_category_id', sa.String(length=100), nullable=False),
        sa.Column('marketplace_id', sa.String(length=20), nullable=False),
        sa.Column('product_category_name', sa.String(length=200), nullable=False),
        sa.Column('parent_category_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('product_category_id', 'marketplace_id')
    )

    # Add new columns to catalog_items table
    op.add_column('catalog_items', sa.Column('seller_id', sa.String(length=50), nullable=True))
    op.add_column('catalog_items', sa.Column('manufacturer', sa.String(length=100), nullable=True))
    op.add_column('catalog_items', sa.Column('model_number', sa.String(length=100), nullable=True))
    op.add_column('catalog_items', sa.Column('size_name', sa.String(length=50), nullable=True))
    op.add_column('catalog_items', sa.Column('style_name', sa.String(length=50), nullable=True))
    op.add_column('catalog_items', sa.Column('product_category_id', sa.String(length=100), nullable=True))
    op.add_column('catalog_items', sa.Column('vendor_details', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove added columns from catalog_items
    op.drop_column('catalog_items', 'vendor_details')
    op.drop_column('catalog_items', 'product_category_id')
    op.drop_column('catalog_items', 'style_name')
    op.drop_column('catalog_items', 'size_name')
    op.drop_column('catalog_items', 'model_number')
    op.drop_column('catalog_items', 'manufacturer')
    op.drop_column('catalog_items', 'seller_id')
    
    # Drop catalog_categories table
    op.drop_table('catalog_categories')
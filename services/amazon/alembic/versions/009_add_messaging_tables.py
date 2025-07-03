"""add messaging tables

Revision ID: 009
Revises: 008
Create Date: 2025-01-07 17:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # Create messaging_actions table
    op.create_table('messaging_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('amazon_order_id', sa.String(length=50), nullable=False),
        sa.Column('marketplace_id', sa.String(length=20), nullable=False),
        sa.Column('action_name', sa.String(length=100), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['amazon_order_id'], ['orders.amazon_order_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('amazon_order_id', sa.String(length=50), nullable=False),
        sa.Column('message_type', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['amazon_order_id'], ['orders.amazon_order_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create buyer_attributes table
    op.create_table('buyer_attributes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('amazon_order_id', sa.String(length=50), nullable=False),
        sa.Column('locale', sa.String(length=10), nullable=True),
        sa.Column('country_code', sa.String(length=2), nullable=True),
        sa.Column('language_code', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['amazon_order_id'], ['orders.amazon_order_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('amazon_order_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_messaging_actions_order', 'messaging_actions', ['amazon_order_id'])
    op.create_index('idx_messaging_actions_marketplace', 'messaging_actions', ['marketplace_id'])
    op.create_index('idx_messaging_actions_available', 'messaging_actions', ['is_available'])
    op.create_index('idx_messages_order', 'messages', ['amazon_order_id'])
    op.create_index('idx_messages_type', 'messages', ['message_type'])
    op.create_index('idx_messages_status', 'messages', ['status'])
    op.create_index('idx_buyer_attributes_order', 'buyer_attributes', ['amazon_order_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_buyer_attributes_order', table_name='buyer_attributes')
    op.drop_index('idx_messages_status', table_name='messages')
    op.drop_index('idx_messages_type', table_name='messages')
    op.drop_index('idx_messages_order', table_name='messages')
    op.drop_index('idx_messaging_actions_available', table_name='messaging_actions')
    op.drop_index('idx_messaging_actions_marketplace', table_name='messaging_actions')
    op.drop_index('idx_messaging_actions_order', table_name='messaging_actions')
    
    # Drop tables
    op.drop_table('buyer_attributes')
    op.drop_table('messages')
    op.drop_table('messaging_actions')
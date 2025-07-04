from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base
import json


class ListingItem(Base):
    __tablename__ = "listings_items"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(String(50), nullable=False, index=True)
    seller_name = Column(String(200), index=True)  # New field for seller name
    sku = Column(String(100), nullable=False, index=True)
    title = Column(String(500))
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    quantity = Column(Integer, default=0)
    status = Column(String(20), default="ACTIVE")
    marketplace_ids = Column(Text)  # JSON array as string
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("seller_id", "sku", name="_seller_sku_uc"),)

    def get_marketplace_ids(self):
        """Parse marketplace_ids JSON string to list"""
        if self.marketplace_ids:
            try:
                return json.loads(self.marketplace_ids)
            except json.JSONDecodeError:
                return []
        return []

    def set_marketplace_ids(self, marketplace_list):
        """Convert marketplace_ids list to JSON string"""
        if marketplace_list:
            self.marketplace_ids = json.dumps(marketplace_list)
        else:
            self.marketplace_ids = None

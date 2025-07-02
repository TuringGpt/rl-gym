"""
Base SQLAlchemy models for the Amazon SP-API Mock Service
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# Create the base class for all models
Base = declarative_base()

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models"""
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
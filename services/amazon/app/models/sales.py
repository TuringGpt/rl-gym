"""
Sales models for Amazon SP-API Mock Service
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_models import Base, TimestampMixin

# Import models from schemas.py to avoid duplication
from app.database.schemas import SalesMetrics

# Re-export models for convenience
__all__ = [
    'SalesMetrics'
]
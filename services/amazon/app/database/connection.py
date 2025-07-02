"""
Database connection management for Amazon SP-API Mock Service
"""

import os
import sys
from pathlib import Path

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.database import DatabaseManager

# Initialize database manager for Amazon service
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

db_manager = DatabaseManager(DATABASE_URL, "amazon")

# Convenience function to get database session
def get_db():
    """Get database session for dependency injection."""
    with db_manager.get_session() as session:
        yield session

# Async version
async def get_async_db():
    """Get async database session for dependency injection."""
    async with db_manager.get_async_session() as session:
        yield session
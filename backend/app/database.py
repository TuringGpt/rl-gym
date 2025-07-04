from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import json

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./listings.db"

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Session-aware database dependency
def get_session_db(session_id: Optional[str] = None):
    """
    Get database session for a specific session ID
    If no session_id provided, uses default database
    """
    if session_id:
        from app.session_manager import session_manager

        db = session_manager.get_session_db(session_id)
        try:
            yield db
        finally:
            db.close()
    else:
        # Use default database
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

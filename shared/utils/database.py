"""
Database utilities for API Mock Gym services.
Provides database connection management and common operations.
"""

from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
import logging
from typing import Generator, Optional, Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str, service_name: str = "default"):
        self.database_url = database_url
        self.service_name = service_name
        self.engine = None
        self.SessionLocal = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        
        self._initialize_sync_db()
        self._initialize_async_db()
    
    def _initialize_sync_db(self):
        """Initialize synchronous database connection."""
        try:
            # Configure engine based on database type
            if "sqlite" in self.database_url:
                self.engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=os.getenv("LOG_LEVEL") == "DEBUG"
                )
            else:
                self.engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=os.getenv("LOG_LEVEL") == "DEBUG"
                )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Initialized sync database connection for {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize sync database for {self.service_name}: {e}")
            raise
    
    def _initialize_async_db(self):
        """Initialize asynchronous database connection."""
        try:
            # Convert sync URL to async URL
            async_url = self.database_url
            if async_url.startswith("postgresql://"):
                async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
            elif async_url.startswith("sqlite://"):
                async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://")
            
            if "sqlite" in async_url:
                self.async_engine = create_async_engine(
                    async_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=os.getenv("LOG_LEVEL") == "DEBUG"
                )
            else:
                self.async_engine = create_async_engine(
                    async_url,
                    pool_size=10,
                    max_overflow=20,
                    echo=os.getenv("LOG_LEVEL") == "DEBUG"
                )
            
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info(f"Initialized async database connection for {self.service_name}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize async database for {self.service_name}: {e}")
            self.async_engine = None
            self.AsyncSessionLocal = None
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get synchronous database session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    async def get_async_session(self) -> AsyncSession:
        """Get asynchronous database session."""
        if not self.AsyncSessionLocal:
            raise RuntimeError("Async database not initialized")
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database session error: {e}")
                raise
    
    def create_tables(self):
        """Create all tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Created tables for {self.service_name}")
        except Exception as e:
            logger.error(f"Failed to create tables for {self.service_name}: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info(f"Dropped tables for {self.service_name}")
        except Exception as e:
            logger.error(f"Failed to drop tables for {self.service_name}: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except Exception as e:
            logger.error(f"Failed to check table existence: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about tables."""
        try:
            inspector = inspect(self.engine)
            tables = {}
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                tables[table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "primary_key": col.get("primary_key", False)
                        }
                        for col in columns
                    ],
                    "indexes": [idx["name"] for idx in indexes],
                    "foreign_keys": [fk["name"] for fk in foreign_keys]
                }
            
            return tables
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {}
    
    def execute_sql_file(self, file_path: str):
        """Execute SQL file."""
        try:
            with open(file_path, 'r') as file:
                sql_content = file.read()
            
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with self.get_session() as session:
                for statement in statements:
                    session.execute(statement)
            
            logger.info(f"Executed SQL file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to execute SQL file {file_path}: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            with self.get_session() as session:
                result = session.execute("SELECT 1").fetchone()
                
            return {
                "status": "healthy",
                "database_url": self.database_url.split("@")[-1] if "@" in self.database_url else "unknown",
                "service": self.service_name,
                "tables": list(self.get_table_info().keys())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": self.service_name
            }

# Service-specific database managers
def create_database_manager(service_name: str) -> DatabaseManager:
    """Create database manager for a service."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(f"DATABASE_URL not set for {service_name} service")
    
    return DatabaseManager(database_url, service_name)

# FastAPI dependency for database sessions
def get_database_dependency(db_manager: DatabaseManager):
    """Create FastAPI dependency for database sessions."""
    def get_db():
        with db_manager.get_session() as session:
            yield session
    
    return get_db

def get_async_database_dependency(db_manager: DatabaseManager):
    """Create FastAPI dependency for async database sessions."""
    async def get_async_db():
        async with db_manager.get_async_session() as session:
            yield session
    
    return get_async_db

# Utility functions for data seeding
class DataSeeder:
    """Utility class for seeding database with mock data."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def seed_from_dict(self, model_class, data_list: list):
        """Seed data from list of dictionaries."""
        try:
            with self.db_manager.get_session() as session:
                for data in data_list:
                    # Check if record already exists (assuming 'id' field)
                    if hasattr(model_class, 'id') and 'id' in data:
                        existing = session.query(model_class).filter(
                            model_class.id == data['id']
                        ).first()
                        if existing:
                            continue
                    
                    record = model_class(**data)
                    session.add(record)
                
                session.commit()
                logger.info(f"Seeded {len(data_list)} records for {model_class.__name__}")
        
        except Exception as e:
            logger.error(f"Failed to seed data for {model_class.__name__}: {e}")
            raise
    
    def clear_table(self, model_class):
        """Clear all data from a table."""
        try:
            with self.db_manager.get_session() as session:
                session.query(model_class).delete()
                session.commit()
                logger.info(f"Cleared table {model_class.__name__}")
        except Exception as e:
            logger.error(f"Failed to clear table {model_class.__name__}: {e}")
            raise

# Database initialization helper
def initialize_database(service_name: str, create_tables: bool = True, 
                       seed_file_path: str = None) -> DatabaseManager:
    """Initialize database for a service."""
    db_manager = create_database_manager(service_name)
    
    if create_tables:
        db_manager.create_tables()
    
    if seed_file_path and os.path.exists(seed_file_path):
        db_manager.execute_sql_file(seed_file_path)
    
    return db_manager

# Connection string helpers
def build_postgres_url(host: str, port: int, database: str, 
                      username: str, password: str) -> str:
    """Build PostgreSQL connection URL."""
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def build_sqlite_url(file_path: str) -> str:
    """Build SQLite connection URL."""
    return f"sqlite:///{file_path}"
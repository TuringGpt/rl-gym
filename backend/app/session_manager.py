"""
Session Database Manager
Handles creation and management of isolated databases per session
"""

import os
import sqlite3
import uuid
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional, Set
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.database import Base
from datetime import datetime
import threading


class SessionDatabaseManager:
    """Manages isolated databases for each session"""

    def __init__(self, base_db_path: str = "listings.db", sessions_dir: str = "sessions"):
        self.base_db_path = base_db_path
        self.sessions_dir = sessions_dir
        self.active_sessions: Dict[str, dict] = {}
        self.engines: Dict[str, any] = {}
        self.session_makers: Dict[str, sessionmaker] = {}
        self._lock = threading.Lock()

        # Create sessions directory if it doesn't exist
        os.makedirs(self.sessions_dir, exist_ok=True)

    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{uuid.uuid4().hex[:12]}"

    def get_session_db_path(self, session_id: str) -> str:
        """Get the database file path for a session"""
        return os.path.join(self.sessions_dir, f"listings_{session_id}.db")

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        db_path = self.get_session_db_path(session_id)
        return os.path.exists(db_path)

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session with isolated database"""
        with self._lock:
            if session_id is None:
                session_id = self.generate_session_id()

            # Check if session already exists
            if self.session_exists(session_id):
                return session_id

            db_path = self.get_session_db_path(session_id)

            try:
                # Create new database file
                engine = create_engine(
                    f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, poolclass=StaticPool
                )

                # Create all tables
                Base.metadata.create_all(bind=engine)

                # Store engine and session maker
                self.engines[session_id] = engine
                self.session_makers[session_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

                # Initialize with seed data
                self._initialize_session_data(session_id)

                # Track session metadata
                self.active_sessions[session_id] = {
                    "created_at": datetime.now(),
                    "last_accessed": datetime.now(),
                    "db_path": db_path,
                }

                return session_id

            except Exception as e:
                # Cleanup on failure
                if os.path.exists(db_path):
                    os.remove(db_path)
                if session_id in self.engines:
                    del self.engines[session_id]
                if session_id in self.session_makers:
                    del self.session_makers[session_id]
                raise Exception(f"Failed to create session {session_id}: {str(e)}")

    def get_session_db(self, session_id: str) -> Session:
        """Get database session for a specific session ID"""
        with self._lock:
            # Update last accessed time
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["last_accessed"] = datetime.now()

            # If session doesn't exist in memory, load it
            if session_id not in self.session_makers:
                if not self.session_exists(session_id):
                    # Create new session if it doesn't exist
                    self.create_session(session_id)
                else:
                    # Load existing session
                    self._load_existing_session(session_id)

            return self.session_makers[session_id]()

    def _load_existing_session(self, session_id: str):
        """Load an existing session into memory"""
        db_path = self.get_session_db_path(session_id)

        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, poolclass=StaticPool)

        self.engines[session_id] = engine
        self.session_makers[session_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Load metadata if not already tracked
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": datetime.fromtimestamp(os.path.getctime(db_path)),
                "last_accessed": datetime.now(),
                "db_path": db_path,
            }

    def _initialize_session_data(self, session_id: str):
        """Initialize session database with seed data"""
        try:
            # Run the seed data script for this session's database
            db_path = self.get_session_db_path(session_id)

            # Create a temporary script that seeds the specific session database
            temp_script = f"""
import sqlite3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Import and modify the seed script
from combined_seed_data import create_comprehensive_sample_data

# Temporarily override the database path
original_db_path = "listings.db"
session_db_path = "{db_path}"

# Monkey patch the database connection in the seed script
import combined_seed_data
original_connect = sqlite3.connect

def session_connect(db_path):
    if db_path == original_db_path:
        return original_connect(session_db_path)
    return original_connect(db_path)

sqlite3.connect = session_connect

# Run the seed data creation
create_comprehensive_sample_data()
"""

            # Write temporary script to system temp directory to avoid triggering file watcher
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", prefix=f"temp_seed_{session_id}_", delete=False
            ) as temp_file:
                temp_file.write(temp_script)
                temp_script_path = temp_file.name

            try:
                # Execute the temporary script
                result = subprocess.run(["python", temp_script_path], capture_output=True, text=True, cwd=".")
            finally:
                # Clean up temporary script
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)

            if result.returncode != 0:
                raise Exception(f"Seed script failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to initialize session data: {str(e)}")

    def reset_session(self, session_id: str) -> bool:
        """Reset session database to seed state without deleting the database file"""
        try:
            with self._lock:
                # Ensure session exists
                if not self.session_exists(session_id):
                    raise Exception(f"Session {session_id} does not exist")

                # Get database path
                db_path = self.get_session_db_path(session_id)

                # Close existing connections temporarily
                engine_backup = None
                session_maker_backup = None

                if session_id in self.engines:
                    self.engines[session_id].dispose()
                    engine_backup = self.engines[session_id]
                    del self.engines[session_id]
                if session_id in self.session_makers:
                    session_maker_backup = self.session_makers[session_id]
                    del self.session_makers[session_id]

                # Clear all data from existing tables
                engine = create_engine(
                    f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, poolclass=StaticPool
                )

                # Drop all tables and recreate them
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)

                # Store engine and session maker
                self.engines[session_id] = engine
                self.session_makers[session_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

                # Re-initialize with seed data
                self._initialize_session_data(session_id)

                # Update last accessed time
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]["last_accessed"] = datetime.now()

                return True

        except Exception as e:
            raise Exception(f"Failed to reset session {session_id}: {str(e)}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its database"""
        try:
            with self._lock:
                # Close connections
                if session_id in self.engines:
                    self.engines[session_id].dispose()
                    del self.engines[session_id]
                if session_id in self.session_makers:
                    del self.session_makers[session_id]

                # Remove database file
                db_path = self.get_session_db_path(session_id)
                if os.path.exists(db_path):
                    os.remove(db_path)

                # Remove from active sessions
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]

                return True

        except Exception as e:
            raise Exception(f"Failed to delete session {session_id}: {str(e)}")

    def list_sessions(self) -> List[Dict[str, any]]:
        """List all active sessions"""
        sessions = []

        # Check for database files in sessions directory
        if os.path.exists(self.sessions_dir):
            for filename in os.listdir(self.sessions_dir):
                if filename.startswith("listings_") and filename.endswith(".db"):
                    session_id = filename[9:-3]  # Remove "listings_" prefix and ".db" suffix

                    # Load session metadata if not in memory
                    if session_id not in self.active_sessions:
                        self._load_existing_session(session_id)

                    session_info = self.active_sessions.get(session_id, {})
                    sessions.append(
                        {
                            "session_id": session_id,
                            "created_at": session_info.get("created_at"),
                            "last_accessed": session_info.get("last_accessed"),
                            "db_path": session_info.get("db_path"),
                            "file_size": os.path.getsize(self.get_session_db_path(session_id)),
                        }
                    )

        return sorted(sessions, key=lambda x: x["last_accessed"] or datetime.min, reverse=True)

    def get_session_info(self, session_id: str) -> Optional[Dict[str, any]]:
        """Get information about a specific session"""
        if not self.session_exists(session_id):
            return None

        if session_id not in self.active_sessions:
            self._load_existing_session(session_id)

        session_info = self.active_sessions.get(session_id, {})
        db_path = self.get_session_db_path(session_id)

        return {
            "session_id": session_id,
            "created_at": session_info.get("created_at"),
            "last_accessed": session_info.get("last_accessed"),
            "db_path": session_info.get("db_path"),
            "file_size": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
            "exists": self.session_exists(session_id),
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> List[str]:
        """Clean up sessions older than specified hours"""
        cleaned_sessions = []
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        for session_info in self.list_sessions():
            last_accessed = session_info.get("last_accessed")
            if last_accessed and last_accessed.timestamp() < cutoff_time:
                try:
                    self.delete_session(session_info["session_id"])
                    cleaned_sessions.append(session_info["session_id"])
                except Exception as e:
                    print(f"Failed to cleanup session {session_info['session_id']}: {e}")

        return cleaned_sessions


# Global session manager instance
session_manager = SessionDatabaseManager()

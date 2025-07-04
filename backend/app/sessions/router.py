"""
Session Management API Endpoints
Provides session creation with auto-generated IDs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.session_manager import session_manager


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    message: str


session_router = APIRouter(prefix="/sessions", tags=["Session Management"])


@session_router.post("", response_model=SessionResponse)
def create_session():
    """
    Create a new session with auto-generated session ID

    Returns a unique session ID that must be used in X-Session-ID header for all subsequent requests
    """
    try:
        # Always auto-generate session ID (no user input)
        session_id = session_manager.generate_session_id()
        session_manager.create_session(session_id)

        return SessionResponse(
            session_id=session_id,
            created_at=datetime.now(),
            message=f"Session created successfully. Use 'X-Session-ID: {session_id}' header for all requests.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

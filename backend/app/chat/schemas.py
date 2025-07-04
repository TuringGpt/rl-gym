from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    message: str
    model: Literal["openai", "anthropic"] = "openai"
    session_id: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    message: str
    model: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, Any]] = None


class McpToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class McpToolResult(BaseModel):
    tool_name: str
    result: Any
    success: bool
    error: Optional[str] = None


class AvailableModel(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    supports_function_calling: bool

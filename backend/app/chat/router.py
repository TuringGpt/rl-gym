from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime

from .schemas import ChatRequest, ChatResponse, AvailableModel
from .services.langchain_service import langchain_service
from .services.mcp_client import mcp_client
from app.session_manager import session_manager

chat_router = APIRouter(prefix="/chat")


@chat_router.get("/models", response_model=List[AvailableModel])
async def get_available_models():
    """Get list of available AI models"""
    models_data = await langchain_service.get_available_models()
    return [AvailableModel(**model) for model in models_data]


@chat_router.post("/openai", response_model=ChatResponse)
async def chat_with_openai(request: ChatRequest):
    """Send message to OpenAI GPT-4 with MCP tool integration"""
    try:
        # Validate session exists
        if not session_manager.session_exists(request.session_id):
            raise HTTPException(
                status_code=400, detail=f"Invalid session ID: {request.session_id}. Please create a session first."
            )

        # Prepare messages including the new user message
        messages = request.conversation_history.copy()
        messages.append({"role": "user", "content": request.message, "timestamp": datetime.now()})

        # Get response from OpenAI via LangChain
        response_text, tool_calls, tool_results, usage = await langchain_service.chat_with_openai(
            messages, request.session_id
        )

        return ChatResponse(
            message=response_text,
            model="openai",
            timestamp=datetime.now(),
            tool_calls=tool_calls,
            tool_results=tool_results,
            usage=usage,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/anthropic", response_model=ChatResponse)
async def chat_with_anthropic(request: ChatRequest):
    """Send message to Anthropic Claude with MCP tool integration"""
    try:
        # Validate session exists
        if not session_manager.session_exists(request.session_id):
            raise HTTPException(
                status_code=400, detail=f"Invalid session ID: {request.session_id}. Please create a session first."
            )

        # Prepare messages including the new user message
        messages = request.conversation_history.copy()
        messages.append({"role": "user", "content": request.message, "timestamp": datetime.now()})

        # Get response from Anthropic via LangChain
        response_text, tool_calls, tool_results, usage = await langchain_service.chat_with_anthropic(
            messages, request.session_id
        )

        return ChatResponse(
            message=response_text,
            model="anthropic",
            timestamp=datetime.now(),
            tool_calls=tool_calls,
            tool_results=tool_results,
            usage=usage,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools"""
    try:
        tools = await mcp_client.get_available_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MCP tools: {str(e)}")


@chat_router.get("/config/status")
async def get_config_status():
    """Get configuration status for debugging"""
    try:
        status = langchain_service.get_config_status()
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config status: {str(e)}")

import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    """Configuration for chat services"""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Model Configuration
    openai_model: str = "gpt-4.1-2025-04-14"
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # LangChain Configuration
    temperature: float = 0.1
    max_tokens: int = 4000
    max_iterations: int = 5
    verbose: bool = False

    # MCP Configuration
    mcp_server_url: str = "http://localhost:8001"
    fastapi_base_url: str = "http://localhost:8000"

    # System Prompt
    system_prompt: str = """You are a helpful AI assistant that specializes in Amazon SP-API operations. 
You have access to various tools that can help users manage their Amazon seller listings.

When users ask about listings, products, or seller operations, use the appropriate tools to help them.
Always provide clear, helpful responses and explain what actions you're taking.

Available operations:
- Search for listings by various criteria
- Get detailed information about specific listings  
- Create new product listings
- Update existing listings (full or partial updates)
- Delete listings
- Create new sessions for data isolation

Be proactive in using tools when users ask questions that require data from the SP-API system.
Always explain what you're doing and provide context for the results.

If you encounter errors, explain them clearly and suggest alternative approaches.
"""

    class Config:
        env_file = ".env"
        env_prefix = "CHAT_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Override with environment variables if not set
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            "openai_configured": bool(self.openai_api_key),
            "anthropic_configured": bool(self.anthropic_api_key),
            "errors": [],
        }

        if not self.openai_api_key:
            status["errors"].append("OpenAI API key not configured")

        if not self.anthropic_api_key:
            status["errors"].append("Anthropic API key not configured")

        return status


# Global configuration instance
chat_config = ChatConfig()

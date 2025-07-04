import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from ..schemas import ChatMessage
from ..config import chat_config
from .mcp_tools import get_mcp_tools, inject_session_id

# Load environment variables
load_dotenv()


class ChatCallbackHandler(AsyncCallbackHandler):
    """Callback handler to track token usage and tool calls"""

    def __init__(self):
        self.tool_calls = []
        self.tool_results = []
        self.usage = {}

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts running"""
        tool_name = serialized.get("name", "unknown")
        self.tool_calls.append({"name": tool_name, "input": input_str})

    async def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes running"""
        self.tool_results.append({"result": output, "success": True})

    async def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when a tool encounters an error"""
        self.tool_results.append({"result": None, "success": False, "error": str(error)})

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM finishes running"""
        if hasattr(response, "llm_output") and response.llm_output:
            self.usage = response.llm_output.get("token_usage", {})


class LangChainChatService:
    def __init__(self):
        # Ensure environment variables are loaded
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        # Validate API keys and initialize models
        if not openai_key:
            print("Warning: OpenAI API key not found. OpenAI model will not be available.")
            self.openai_model = None
        else:
            self.openai_model = ChatOpenAI(
                model=chat_config.openai_model,
                temperature=chat_config.temperature,
                max_tokens=chat_config.max_tokens,
                api_key=openai_key,
            )

        if not anthropic_key:
            print("Warning: Anthropic API key not found. Anthropic model will not be available.")
            self.anthropic_model = None
        else:
            self.anthropic_model = ChatAnthropic(
                model=chat_config.anthropic_model,
                temperature=chat_config.temperature,
                max_tokens=chat_config.max_tokens,
                api_key=anthropic_key,
            )

        # Use system prompt from configuration
        self.system_prompt = chat_config.system_prompt

    def _convert_messages_to_langchain(self, messages: List[Any]) -> List[BaseMessage]:
        """Convert ChatMessage objects or dicts to LangChain message format"""
        lc_messages = []

        for msg in messages:
            # Handle both ChatMessage objects and dictionaries
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                role = msg.role
                content = msg.content

            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))

        return lc_messages

    async def chat_with_openai(
        self, messages: List[Any], session_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        """Chat with OpenAI using LangChain agent"""
        if not self.openai_model:
            raise Exception("OpenAI model not available. Please check your API key configuration.")
        return await self._chat_with_agent(self.openai_model, messages, session_id, "openai")

    async def chat_with_anthropic(
        self, messages: List[Any], session_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        """Chat with Anthropic using LangChain agent"""
        if not self.anthropic_model:
            raise Exception("Anthropic model not available. Please check your API key configuration.")
        return await self._chat_with_agent(self.anthropic_model, messages, session_id, "anthropic")

    async def _chat_with_agent(
        self, model, messages: List[Any], session_id: str, model_name: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        """Generic method to chat with any model using LangChain agent"""

        callback_handler = None
        agent_executor = None

        try:
            # Get MCP tools and inject session_id
            tools = get_mcp_tools()
            tools = inject_session_id(tools, session_id)

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder("agent_scratchpad"),
                ]
            )

            # Create agent
            agent = create_tool_calling_agent(model, tools, prompt)

            # Create agent executor with configuration
            callback_handler = ChatCallbackHandler()
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,  # Disable verbose to prevent shutdown issues
                callbacks=[callback_handler],
                handle_parsing_errors=True,
                max_iterations=chat_config.max_iterations,
                return_intermediate_steps=False,  # Reduce memory usage
            )

            # Convert messages to LangChain format
            lc_messages = self._convert_messages_to_langchain(
                messages[:-1]
            )  # Exclude the last message (current input)

            # Get current input - handle both dict and object
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    current_input = last_msg.get("content", "")
                else:
                    current_input = last_msg.content
            else:
                current_input = ""

            # Execute the agent with timeout protection
            try:
                result = await agent_executor.ainvoke({"input": current_input, "chat_history": lc_messages})
            except Exception as agent_error:
                print(f"Agent execution error: {agent_error}")
                # Return a fallback response instead of crashing
                return f"I encountered an error while processing your request: {str(agent_error)}", None, None, {}

            # Extract response and metadata
            raw_output = result.get("output", "") if result else ""

            # Handle different output formats from LangChain
            if isinstance(raw_output, list):
                # If output is a list of content blocks, extract text
                response_text = ""
                for item in raw_output:
                    if isinstance(item, dict) and item.get("type") == "text":
                        response_text += item.get("text", "")
                    elif isinstance(item, str):
                        response_text += item
            elif isinstance(raw_output, str):
                response_text = raw_output
            else:
                response_text = str(raw_output)

            # Ensure we have a valid response
            if not response_text:
                response_text = "I processed your request but didn't generate a response. Please try again."

            tool_calls = callback_handler.tool_calls if callback_handler and callback_handler.tool_calls else None
            tool_results = (
                callback_handler.tool_results if callback_handler and callback_handler.tool_results else None
            )
            usage = callback_handler.usage if callback_handler and callback_handler.usage else {}

            return response_text, tool_calls, tool_results, usage

        except Exception as e:
            print(f"LangChain {model_name} error: {str(e)}")
            # Return error message instead of raising exception
            return f"I encountered an error: {str(e)}", None, None, {}

        finally:
            # Clean up resources
            if callback_handler:
                callback_handler.tool_calls = []
                callback_handler.tool_results = []
                callback_handler.usage = {}
            agent_executor = None

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with configuration status"""
        models = []

        if self.openai_model:
            models.append(
                {
                    "id": "openai",
                    "name": f"GPT-4 Turbo ({chat_config.openai_model})",
                    "provider": "OpenAI",
                    "description": "GPT-4 Turbo with advanced reasoning and tool calling via LangChain",
                    "supports_function_calling": True,
                }
            )

        if self.anthropic_model:
            models.append(
                {
                    "id": "anthropic",
                    "name": f"Claude 3.5 Sonnet ({chat_config.anthropic_model})",
                    "provider": "Anthropic",
                    "description": "Claude 3.5 Sonnet with thoughtful analysis and tool use via LangChain",
                    "supports_function_calling": True,
                }
            )

        return models

    def get_config_status(self) -> Dict[str, Any]:
        """Get configuration status for debugging"""
        return chat_config.validate_config()


# Global LangChain service instance
langchain_service = LangChainChatService()

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from ..schemas import ChatMessage, McpToolCall, McpToolResult
from .mcp_client import mcp_client


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-1106-preview"  # Use GPT-4 Turbo with function calling

    async def get_mcp_functions(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function format"""
        mcp_tools = await mcp_client.get_available_tools()
        functions = []

        for tool in mcp_tools:
            functions.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                    },
                }
            )

        return functions

    async def chat_completion(
        self, messages: List[ChatMessage], session_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        """
        Send chat completion request to OpenAI with function calling
        Returns: (response_text, tool_calls, tool_results, usage)
        """
        try:
            # Convert ChatMessage objects to OpenAI format
            openai_messages = []
            for msg in messages:
                openai_messages.append({"role": msg.role, "content": msg.content})

            # Get available MCP functions
            functions = await self.get_mcp_functions()

            # Make the API call with function calling
            response = await self.client.chat.completions.create(
                model=self.model, messages=openai_messages, tools=functions, tool_choice="auto"
            )

            message = response.choices[0].message
            tool_calls = []
            tool_results = []

            # Handle function calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Add session_id to function arguments if not present
                    if "session_id" in [
                        param
                        for tool in await mcp_client.get_available_tools()
                        if tool["name"] == function_name
                        for param in tool["parameters"].get("required", [])
                    ]:
                        if "session_id" not in function_args:
                            function_args["session_id"] = session_id

                    # Execute the MCP tool
                    mcp_call = McpToolCall(tool_name=function_name, parameters=function_args)

                    tool_result = await mcp_client.execute_tool(mcp_call)

                    tool_calls.append(
                        {
                            "id": tool_call.id,
                            "function": {"name": function_name, "arguments": json.dumps(function_args)},
                        }
                    )

                    tool_results.append(
                        {
                            "tool_call_id": tool_call.id,
                            "result": tool_result.result,
                            "success": tool_result.success,
                            "error": tool_result.error,
                        }
                    )

                # If there were tool calls, make another API call to get the final response
                if tool_calls:
                    # Add the assistant's message with tool calls
                    openai_messages.append(
                        {
                            "role": "assistant",
                            "content": message.content,
                            "tool_calls": [
                                {"id": tc["id"], "type": "function", "function": tc["function"]} for tc in tool_calls
                            ],
                        }
                    )

                    # Add tool results
                    for result in tool_results:
                        openai_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": result["tool_call_id"],
                                "content": (
                                    json.dumps(result["result"]) if result["success"] else f"Error: {result['error']}"
                                ),
                            }
                        )

                    # Get final response
                    final_response = await self.client.chat.completions.create(
                        model=self.model, messages=openai_messages
                    )

                    final_message = final_response.choices[0].message.content
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens + final_response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens + final_response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens + final_response.usage.total_tokens,
                    }

                    return final_message, tool_calls, tool_results, usage

            # No function calls, return the direct response
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return message.content, None, None, usage

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


# Global OpenAI service instance
openai_service = OpenAIService()

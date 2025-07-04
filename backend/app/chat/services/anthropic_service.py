import os
import json
from typing import List, Dict, Any, Optional, Tuple
from anthropic import AsyncAnthropic
from ..schemas import ChatMessage, McpToolCall, McpToolResult
from .mcp_client import mcp_client


class AnthropicService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet with function calling

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Anthropic tool format"""
        mcp_tools = await mcp_client.get_available_tools()
        tools = []

        for tool in mcp_tools:
            tools.append(
                {"name": tool["name"], "description": tool["description"], "input_schema": tool["parameters"]}
            )

        return tools

    async def chat_completion(
        self, messages: List[ChatMessage], session_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        """
        Send chat completion request to Anthropic with tool use
        Returns: (response_text, tool_calls, tool_results, usage)
        """
        try:
            # Convert ChatMessage objects to Anthropic format
            anthropic_messages = []
            system_message = None

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({"role": msg.role, "content": msg.content})

            # Get available MCP tools
            tools = await self.get_mcp_tools()

            # Make the API call with tool use
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_message
                or "You are a helpful assistant that can use tools to help users with Amazon SP-API operations.",
                messages=anthropic_messages,
                tools=tools,
            )

            tool_calls = []
            tool_results = []
            response_text = ""

            # Process the response
            for content in response.content:
                if content.type == "text":
                    response_text += content.text
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_input = content.input

                    # Add session_id to tool input if not present
                    if "session_id" in [
                        param
                        for tool in await mcp_client.get_available_tools()
                        if tool["name"] == tool_name
                        for param in tool["parameters"].get("required", [])
                    ]:
                        if "session_id" not in tool_input:
                            tool_input["session_id"] = session_id

                    # Execute the MCP tool
                    mcp_call = McpToolCall(tool_name=tool_name, parameters=tool_input)

                    tool_result = await mcp_client.execute_tool(mcp_call)

                    tool_calls.append({"id": content.id, "name": tool_name, "input": tool_input})

                    tool_results.append(
                        {
                            "tool_use_id": content.id,
                            "result": tool_result.result,
                            "success": tool_result.success,
                            "error": tool_result.error,
                        }
                    )

            # If there were tool calls, make another API call to get the final response
            if tool_calls:
                # Add the assistant's message with tool use
                anthropic_messages.append({"role": "assistant", "content": response.content})

                # Add tool results
                tool_result_content = []
                for result in tool_results:
                    if result["success"]:
                        tool_result_content.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": result["tool_use_id"],
                                "content": json.dumps(result["result"]),
                            }
                        )
                    else:
                        tool_result_content.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": result["tool_use_id"],
                                "content": f"Error: {result['error']}",
                                "is_error": True,
                            }
                        )

                anthropic_messages.append({"role": "user", "content": tool_result_content})

                # Get final response
                final_response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=system_message
                    or "You are a helpful assistant that can use tools to help users with Amazon SP-API operations.",
                    messages=anthropic_messages,
                )

                final_text = ""
                for content in final_response.content:
                    if content.type == "text":
                        final_text += content.text

                usage = {
                    "input_tokens": response.usage.input_tokens + final_response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens + final_response.usage.output_tokens,
                    "total_tokens": (
                        response.usage.input_tokens
                        + response.usage.output_tokens
                        + final_response.usage.input_tokens
                        + final_response.usage.output_tokens
                    ),
                }

                return final_text, tool_calls, tool_results, usage

            # No tool calls, return the direct response
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return response_text, None, None, usage

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")


# Global Anthropic service instance
anthropic_service = AnthropicService()

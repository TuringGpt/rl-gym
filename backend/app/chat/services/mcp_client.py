import httpx
import json
from typing import Dict, Any, List, Optional
from ..schemas import McpToolCall, McpToolResult


class McpClient:
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools and their schemas"""
        try:
            # For now, return the known tools from your MCP server
            # In a real implementation, this would query the MCP server for available tools
            return [
                {
                    "name": "create_session",
                    "description": "Create a new session and get session ID for subsequent requests",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
                {
                    "name": "get_listing_item",
                    "description": "Get details about a specific listing item by seller ID and SKU",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from create_session (required)",
                            },
                            "seller_id": {"type": "string", "description": "The seller identifier (e.g., SELLER001)"},
                            "sku": {"type": "string", "description": "The SKU (Stock Keeping Unit) identifier"},
                            "marketplace_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional list of marketplace IDs to filter by",
                            },
                        },
                        "required": ["session_id", "seller_id", "sku"],
                    },
                },
                {
                    "name": "create_or_update_listing",
                    "description": "Create a new listing or fully update an existing one",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from create_session (required)",
                            },
                            "seller_id": {"type": "string", "description": "The seller identifier"},
                            "sku": {"type": "string", "description": "The SKU identifier"},
                            "title": {"type": "string", "description": "Product title"},
                            "description": {"type": "string", "description": "Product description"},
                            "price": {"type": "number", "description": "Product price"},
                            "quantity": {"type": "integer", "description": "Available quantity"},
                            "status": {
                                "type": "string",
                                "enum": ["ACTIVE", "INACTIVE"],
                                "description": "Listing status",
                            },
                            "marketplace_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of marketplace IDs",
                            },
                        },
                        "required": ["session_id", "seller_id", "sku"],
                    },
                },
                {
                    "name": "update_listing_partial",
                    "description": "Partially update an existing listing (only specified fields)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from create_session (required)",
                            },
                            "seller_id": {"type": "string", "description": "The seller identifier"},
                            "sku": {"type": "string", "description": "The SKU identifier"},
                            "title": {"type": "string", "description": "Product title"},
                            "description": {"type": "string", "description": "Product description"},
                            "price": {"type": "number", "description": "Product price"},
                            "quantity": {"type": "integer", "description": "Available quantity"},
                            "status": {
                                "type": "string",
                                "enum": ["ACTIVE", "INACTIVE"],
                                "description": "Listing status",
                            },
                            "marketplace_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of marketplace IDs",
                            },
                        },
                        "required": ["session_id", "seller_id", "sku"],
                    },
                },
                {
                    "name": "delete_listing_item",
                    "description": "Delete a listing item (sets status to INACTIVE)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from create_session (required)",
                            },
                            "seller_id": {"type": "string", "description": "The seller identifier"},
                            "sku": {"type": "string", "description": "The SKU identifier"},
                        },
                        "required": ["session_id", "seller_id", "sku"],
                    },
                },
                {
                    "name": "search_listings",
                    "description": "Search for listings with optional filters and text search",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from create_session (required)",
                            },
                            "seller_id": {"type": "string", "description": "Filter by seller ID"},
                            "seller_name": {"type": "string", "description": "Search by seller name (partial match)"},
                            "title_search": {
                                "type": "string",
                                "description": "Search in product title and description",
                            },
                            "marketplace_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by marketplace IDs",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["ACTIVE", "INACTIVE"],
                                "description": "Filter by listing status",
                            },
                            "skip": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Number of items to skip (pagination)",
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1000,
                                "description": "Maximum number of items to return",
                            },
                        },
                        "required": ["session_id"],
                    },
                },
            ]
        except Exception as e:
            print(f"Error getting MCP tools: {e}")
            return []

    async def execute_tool(self, tool_call: McpToolCall) -> McpToolResult:
        """Execute an MCP tool call"""
        try:
            # Make HTTP request to your existing FastAPI backend
            # Since the MCP tools are actually implemented as HTTP endpoints in your backend

            if tool_call.tool_name == "create_session":
                response = await self.client.post("http://localhost:8000/sessions")

            elif tool_call.tool_name == "get_listing_item":
                session_id = tool_call.parameters["session_id"]
                seller_id = tool_call.parameters["seller_id"]
                sku = tool_call.parameters["sku"]
                marketplace_ids = tool_call.parameters.get("marketplace_ids")

                url = f"http://localhost:8000/listings/2021-08-01/items/{seller_id}/{sku}"
                headers = {"X-Session-ID": session_id}
                params = {}
                if marketplace_ids:
                    params["marketplace_ids"] = marketplace_ids

                response = await self.client.get(url, headers=headers, params=params)

            elif tool_call.tool_name == "create_or_update_listing":
                session_id = tool_call.parameters.pop("session_id")
                seller_id = tool_call.parameters.pop("seller_id")
                sku = tool_call.parameters.pop("sku")

                url = f"http://localhost:8000/listings/2021-08-01/items/{seller_id}/{sku}"
                headers = {"X-Session-ID": session_id}

                response = await self.client.put(url, headers=headers, json=tool_call.parameters)

            elif tool_call.tool_name == "update_listing_partial":
                session_id = tool_call.parameters.pop("session_id")
                seller_id = tool_call.parameters.pop("seller_id")
                sku = tool_call.parameters.pop("sku")

                url = f"http://localhost:8000/listings/2021-08-01/items/{seller_id}/{sku}"
                headers = {"X-Session-ID": session_id}

                response = await self.client.patch(url, headers=headers, json=tool_call.parameters)

            elif tool_call.tool_name == "delete_listing_item":
                session_id = tool_call.parameters["session_id"]
                seller_id = tool_call.parameters["seller_id"]
                sku = tool_call.parameters["sku"]

                url = f"http://localhost:8000/listings/2021-08-01/items/{seller_id}/{sku}"
                headers = {"X-Session-ID": session_id}

                response = await self.client.delete(url, headers=headers)

            elif tool_call.tool_name == "search_listings":
                session_id = tool_call.parameters.pop("session_id")
                url = "http://localhost:8000/listings/2021-08-01/items"
                headers = {"X-Session-ID": session_id}

                response = await self.client.get(url, headers=headers, params=tool_call.parameters)

            else:
                return McpToolResult(
                    tool_name=tool_call.tool_name,
                    result=None,
                    success=False,
                    error=f"Unknown tool: {tool_call.tool_name}",
                )

            if response.status_code == 200:
                return McpToolResult(tool_name=tool_call.tool_name, result=response.json(), success=True)
            else:
                return McpToolResult(
                    tool_name=tool_call.tool_name,
                    result=None,
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                )

        except Exception as e:
            return McpToolResult(tool_name=tool_call.tool_name, result=None, success=False, error=str(e))

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global MCP client instance
mcp_client = McpClient()

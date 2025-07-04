#!/usr/bin/env python3
"""
Amazon SP-API Mock MCP Server

This MCP server provides tools to interact with the Amazon SP-API mock backend
by making HTTP requests to the FastAPI server.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource, LoggingLevel
from pydantic import BaseModel

# Add debug output to stderr
print("Amazon SP-API MCP Server starting...", file=sys.stderr)
print(f"Python executable: {sys.executable}", file=sys.stderr)
print(f"Working directory: {sys.path[0]}", file=sys.stderr)

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"

# Create MCP server
server = Server("amazon-sp-api-mock")

# HTTP client for making requests to FastAPI
http_client = httpx.AsyncClient(timeout=30.0)


class ListingCreateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = 0
    status: Optional[str] = "ACTIVE"
    marketplace_ids: Optional[List[str]] = []


class ListingUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    marketplace_ids: Optional[List[str]] = None


async def handle_http_error(response: httpx.Response) -> str:
    """Handle HTTP errors and return formatted error message"""
    try:
        error_data = response.json()
        if isinstance(error_data, dict) and "errors" in error_data:
            return f"API Error: {error_data['errors'][0].get('message', 'Unknown error')}"
        elif isinstance(error_data, dict) and "detail" in error_data:
            return f"API Error: {error_data['detail']}"
        else:
            return f"HTTP {response.status_code}: {response.text}"
    except:
        return f"HTTP {response.status_code}: {response.text}"


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_listing_item",
            description="Get details about a specific listing item by seller ID and SKU",
            inputSchema={
                "type": "object",
                "properties": {
                    "seller_id": {"type": "string", "description": "The seller identifier (e.g., SELLER001)"},
                    "sku": {"type": "string", "description": "The SKU (Stock Keeping Unit) identifier"},
                    "marketplace_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of marketplace IDs to filter by",
                    },
                },
                "required": ["seller_id", "sku"],
            },
        ),
        Tool(
            name="create_or_update_listing",
            description="Create a new listing or fully update an existing one",
            inputSchema={
                "type": "object",
                "properties": {
                    "seller_id": {"type": "string", "description": "The seller identifier"},
                    "sku": {"type": "string", "description": "The SKU identifier"},
                    "title": {"type": "string", "description": "Product title"},
                    "description": {"type": "string", "description": "Product description"},
                    "price": {"type": "number", "description": "Product price"},
                    "quantity": {"type": "integer", "description": "Available quantity"},
                    "status": {"type": "string", "enum": ["ACTIVE", "INACTIVE"], "description": "Listing status"},
                    "marketplace_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of marketplace IDs",
                    },
                },
                "required": ["seller_id", "sku"],
            },
        ),
        Tool(
            name="update_listing_partial",
            description="Partially update an existing listing (only specified fields)",
            inputSchema={
                "type": "object",
                "properties": {
                    "seller_id": {"type": "string", "description": "The seller identifier"},
                    "sku": {"type": "string", "description": "The SKU identifier"},
                    "title": {"type": "string", "description": "Product title"},
                    "description": {"type": "string", "description": "Product description"},
                    "price": {"type": "number", "description": "Product price"},
                    "quantity": {"type": "integer", "description": "Available quantity"},
                    "status": {"type": "string", "enum": ["ACTIVE", "INACTIVE"], "description": "Listing status"},
                    "marketplace_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of marketplace IDs",
                    },
                },
                "required": ["seller_id", "sku"],
            },
        ),
        Tool(
            name="delete_listing_item",
            description="Delete a listing item (sets status to INACTIVE)",
            inputSchema={
                "type": "object",
                "properties": {
                    "seller_id": {"type": "string", "description": "The seller identifier"},
                    "sku": {"type": "string", "description": "The SKU identifier"},
                },
                "required": ["seller_id", "sku"],
            },
        ),
        Tool(
            name="search_listings",
            description="Search for listings with optional filters and text search",
            inputSchema={
                "type": "object",
                "properties": {
                    "seller_id": {"type": "string", "description": "Filter by seller ID"},
                    "seller_name": {"type": "string", "description": "Search by seller name (partial match)"},
                    "title_search": {"type": "string", "description": "Search in product title and description"},
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
                    "skip": {"type": "integer", "minimum": 0, "description": "Number of items to skip (pagination)"},
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "description": "Maximum number of items to return",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "get_listing_item":
            seller_id = arguments["seller_id"]
            sku = arguments["sku"]
            marketplace_ids = arguments.get("marketplace_ids")

            url = f"{FASTAPI_BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}"
            params = {}
            if marketplace_ids:
                params["marketplace_ids"] = marketplace_ids

            response = await http_client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return [
                    TextContent(
                        type="text",
                        text=f"✅ **Listing Found**\n\n**SKU:** {data['sku']}\n**Status:** {data['status']}\n\n**Attributes:**\n- **Title:** {data['attributes'].get('title', 'N/A')}\n- **Description:** {data['attributes'].get('description', 'N/A')}\n- **Price:** ${data['attributes'].get('price', 'N/A')}\n- **Quantity:** {data['attributes'].get('quantity', 'N/A')}\n\n**Marketplaces:**\n"
                        + "\n".join(
                            [
                                f"- {summary['marketplace_id']} (ASIN: {summary['asin']})"
                                for summary in data["summaries"]
                            ]
                        )
                        + f"\n\n**Raw JSON:**\n```json\n{json.dumps(data, indent=2)}\n```",
                    )
                ]
            else:
                error_msg = await handle_http_error(response)
                return [TextContent(type="text", text=f"❌ **Error getting listing**\n\n{error_msg}")]

        elif name == "create_or_update_listing":
            seller_id = arguments["seller_id"]
            sku = arguments["sku"]

            # Build request body
            request_data = {}
            for field in ["title", "description", "price", "quantity", "status", "marketplace_ids"]:
                if field in arguments:
                    request_data[field] = arguments[field]

            url = f"{FASTAPI_BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}"
            response = await http_client.put(url, json=request_data)

            if response.status_code == 200:
                data = response.json()
                return [
                    TextContent(
                        type="text",
                        text=f"✅ **Listing Created/Updated Successfully**\n\n**SKU:** {data['sku']}\n**Status:** {data['status']}\n**Title:** {data['attributes'].get('title', 'N/A')}\n**Price:** ${data['attributes'].get('price', 'N/A')}\n**Quantity:** {data['attributes'].get('quantity', 'N/A')}\n\n**Raw JSON:**\n```json\n{json.dumps(data, indent=2)}\n```",
                    )
                ]
            else:
                error_msg = await handle_http_error(response)
                return [TextContent(type="text", text=f"❌ **Error creating/updating listing**\n\n{error_msg}")]

        elif name == "update_listing_partial":
            seller_id = arguments["seller_id"]
            sku = arguments["sku"]

            # Build request body (only include provided fields)
            request_data = {}
            for field in ["title", "description", "price", "quantity", "status", "marketplace_ids"]:
                if field in arguments:
                    request_data[field] = arguments[field]

            url = f"{FASTAPI_BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}"
            response = await http_client.patch(url, json=request_data)

            if response.status_code == 200:
                data = response.json()
                return [
                    TextContent(
                        type="text",
                        text=f"✅ **Listing Updated Successfully**\n\n**SKU:** {data['sku']}\n**Status:** {data['status']}\n**Title:** {data['attributes'].get('title', 'N/A')}\n**Price:** ${data['attributes'].get('price', 'N/A')}\n**Quantity:** {data['attributes'].get('quantity', 'N/A')}\n\n**Raw JSON:**\n```json\n{json.dumps(data, indent=2)}\n```",
                    )
                ]
            else:
                error_msg = await handle_http_error(response)
                return [TextContent(type="text", text=f"❌ **Error updating listing**\n\n{error_msg}")]

        elif name == "delete_listing_item":
            seller_id = arguments["seller_id"]
            sku = arguments["sku"]

            url = f"{FASTAPI_BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}"
            response = await http_client.delete(url)

            if response.status_code == 200:
                data = response.json()
                return [
                    TextContent(
                        type="text",
                        text=f"✅ **Listing Deleted Successfully**\n\n{data.get('message', 'Listing deleted')}",
                    )
                ]
            else:
                error_msg = await handle_http_error(response)
                return [TextContent(type="text", text=f"❌ **Error deleting listing**\n\n{error_msg}")]

        elif name == "search_listings":
            url = f"{FASTAPI_BASE_URL}/listings/2021-08-01/items"
            params = {}

            # Add query parameters
            for param in ["seller_id", "seller_name", "title_search", "marketplace_ids", "status", "skip", "limit"]:
                if param in arguments:
                    params[param] = arguments[param]

            response = await http_client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                pagination = data.get("pagination", {})

                if not items:
                    return [TextContent(type="text", text="📭 **No listings found** matching the search criteria.")]

                # Format results
                result_text = f"🔍 **Found {len(items)} listing(s)**\n\n"

                for i, item in enumerate(items, 1):
                    attrs = item.get("attributes", {})
                    result_text += f"**{i}. {item['sku']}**\n"
                    result_text += f"   - **Seller:** {attrs.get('seller_name', 'N/A')}\n"
                    result_text += f"   - **Title:** {attrs.get('title', 'N/A')}\n"
                    result_text += f"   - **Price:** ${attrs.get('price', 'N/A')}\n"
                    result_text += f"   - **Quantity:** {attrs.get('quantity', 'N/A')}\n"
                    result_text += f"   - **Status:** {item['status']}\n"
                    result_text += f"   - **Marketplaces:** {', '.join([s['marketplace_id'] for s in item.get('summaries', [])])}\n\n"

                result_text += f"**Pagination:** Showing {pagination.get('skip', 0) + 1}-{pagination.get('skip', 0) + len(items)} of {pagination.get('total', len(items))} total\n\n"
                result_text += f"**Raw JSON:**\n```json\n{json.dumps(data, indent=2)}\n```"

                return [TextContent(type="text", text=result_text)]
            else:
                error_msg = await handle_http_error(response)
                return [TextContent(type="text", text=f"❌ **Error searching listings**\n\n{error_msg}")]

        else:
            return [TextContent(type="text", text=f"❌ **Unknown tool:** {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ **Tool execution error:** {str(e)}")]


async def main():
    """Main entry point"""
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

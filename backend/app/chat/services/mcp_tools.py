from typing import Dict, Any, List, Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from ..schemas import McpToolCall, McpToolResult
from .mcp_client import mcp_client


# Tool input schemas
class CreateSessionInput(BaseModel):
    """Input for create_session tool"""

    pass


class GetListingItemInput(BaseModel):
    """Input for get_listing_item tool"""

    session_id: str = Field(description="Session ID from create_session (required)")
    seller_id: str = Field(description="The seller identifier (e.g., SELLER001)")
    sku: str = Field(description="The SKU (Stock Keeping Unit) identifier")
    marketplace_ids: Optional[List[str]] = Field(
        default=None, description="Optional list of marketplace IDs to filter by"
    )


class CreateOrUpdateListingInput(BaseModel):
    """Input for create_or_update_listing tool"""

    session_id: str = Field(description="Session ID from create_session (required)")
    seller_id: str = Field(description="The seller identifier")
    sku: str = Field(description="The SKU identifier")
    title: Optional[str] = Field(default=None, description="Product title")
    description: Optional[str] = Field(default=None, description="Product description")
    price: Optional[float] = Field(default=None, description="Product price")
    quantity: Optional[int] = Field(default=None, description="Available quantity")
    status: Optional[str] = Field(default=None, description="Listing status (ACTIVE or INACTIVE)")
    marketplace_ids: Optional[List[str]] = Field(default=None, description="List of marketplace IDs")


class UpdateListingPartialInput(BaseModel):
    """Input for update_listing_partial tool"""

    session_id: str = Field(description="Session ID from create_session (required)")
    seller_id: str = Field(description="The seller identifier")
    sku: str = Field(description="The SKU identifier")
    title: Optional[str] = Field(default=None, description="Product title")
    description: Optional[str] = Field(default=None, description="Product description")
    price: Optional[float] = Field(default=None, description="Product price")
    quantity: Optional[int] = Field(default=None, description="Available quantity")
    status: Optional[str] = Field(default=None, description="Listing status (ACTIVE or INACTIVE)")
    marketplace_ids: Optional[List[str]] = Field(default=None, description="List of marketplace IDs")


class DeleteListingItemInput(BaseModel):
    """Input for delete_listing_item tool"""

    session_id: str = Field(description="Session ID from create_session (required)")
    seller_id: str = Field(description="The seller identifier")
    sku: str = Field(description="The SKU identifier")


class SearchListingsInput(BaseModel):
    """Input for search_listings tool"""

    session_id: str = Field(description="Session ID from create_session (required)")
    seller_id: Optional[str] = Field(default=None, description="Filter by seller ID")
    seller_name: Optional[str] = Field(default=None, description="Search by seller name (partial match)")
    title_search: Optional[str] = Field(default=None, description="Search in product title and description")
    marketplace_ids: Optional[List[str]] = Field(default=None, description="Filter by marketplace IDs")
    status: Optional[str] = Field(default=None, description="Filter by listing status (ACTIVE or INACTIVE)")
    skip: Optional[int] = Field(default=0, description="Number of items to skip (pagination)")
    limit: Optional[int] = Field(default=100, description="Maximum number of items to return")


# LangChain Tool implementations
class CreateSessionTool(BaseTool):
    name: str = "create_session"
    description: str = "Create a new session and get session ID for subsequent requests"
    args_schema: Type[BaseModel] = CreateSessionInput

    async def _arun(self, **kwargs) -> str:
        tool_call = McpToolCall(tool_name=self.name, parameters=kwargs)
        result = await mcp_client.execute_tool(tool_call)
        if result.success:
            return f"Session created successfully: {result.result}"
        else:
            return f"Error creating session: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


class GetListingItemTool(BaseTool):
    name: str = "get_listing_item"
    description: str = "Get details about a specific listing item by seller ID and SKU"
    args_schema: Type[BaseModel] = GetListingItemInput

    async def _arun(
        self, session_id: str, seller_id: str, sku: str, marketplace_ids: Optional[List[str]] = None
    ) -> str:
        params = {"session_id": session_id, "seller_id": seller_id, "sku": sku}
        if marketplace_ids:
            params["marketplace_ids"] = marketplace_ids

        tool_call = McpToolCall(tool_name=self.name, parameters=params)
        result = await mcp_client.execute_tool(tool_call)

        if result.success:
            listing = result.result
            return (
                f"Listing found for SKU {sku}:\n"
                f"Title: {listing.get('attributes', {}).get('title', 'N/A')}\n"
                f"Price: ${listing.get('attributes', {}).get('price', 'N/A')}\n"
                f"Quantity: {listing.get('attributes', {}).get('quantity', 'N/A')}\n"
                f"Status: {listing.get('status', 'N/A')}"
            )
        else:
            return f"Error getting listing: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


class CreateOrUpdateListingTool(BaseTool):
    name: str = "create_or_update_listing"
    description: str = "Create a new listing or fully update an existing one"
    args_schema: Type[BaseModel] = CreateOrUpdateListingInput

    async def _arun(self, **kwargs) -> str:
        tool_call = McpToolCall(tool_name=self.name, parameters=kwargs)
        result = await mcp_client.execute_tool(tool_call)

        if result.success:
            listing = result.result
            return (
                f"Listing created/updated successfully for SKU {listing.get('sku')}:\n"
                f"Title: {listing.get('attributes', {}).get('title', 'N/A')}\n"
                f"Price: ${listing.get('attributes', {}).get('price', 'N/A')}\n"
                f"Status: {listing.get('status', 'N/A')}"
            )
        else:
            return f"Error creating/updating listing: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


class UpdateListingPartialTool(BaseTool):
    name: str = "update_listing_partial"
    description: str = "Partially update an existing listing (only specified fields)"
    args_schema: Type[BaseModel] = UpdateListingPartialInput

    async def _arun(self, **kwargs) -> str:
        tool_call = McpToolCall(tool_name=self.name, parameters=kwargs)
        result = await mcp_client.execute_tool(tool_call)

        if result.success:
            listing = result.result
            return (
                f"Listing updated successfully for SKU {listing.get('sku')}:\n"
                f"Title: {listing.get('attributes', {}).get('title', 'N/A')}\n"
                f"Price: ${listing.get('attributes', {}).get('price', 'N/A')}\n"
                f"Status: {listing.get('status', 'N/A')}"
            )
        else:
            return f"Error updating listing: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


class DeleteListingItemTool(BaseTool):
    name: str = "delete_listing_item"
    description: str = "Delete a listing item (sets status to INACTIVE)"
    args_schema: Type[BaseModel] = DeleteListingItemInput

    async def _arun(self, session_id: str, seller_id: str, sku: str) -> str:
        tool_call = McpToolCall(
            tool_name=self.name, parameters={"session_id": session_id, "seller_id": seller_id, "sku": sku}
        )
        result = await mcp_client.execute_tool(tool_call)

        if result.success:
            return f"Listing deleted successfully for SKU {sku}"
        else:
            return f"Error deleting listing: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


class SearchListingsTool(BaseTool):
    name: str = "search_listings"
    description: str = "Search for listings with optional filters and text search"
    args_schema: Type[BaseModel] = SearchListingsInput

    async def _arun(self, **kwargs) -> str:
        tool_call = McpToolCall(tool_name=self.name, parameters=kwargs)
        result = await mcp_client.execute_tool(tool_call)

        if result.success:
            data = result.result
            items = data.get("items", [])
            pagination = data.get("pagination", {})

            if not items:
                return "No listings found matching the search criteria."

            result_text = f"Found {len(items)} listing(s):\n\n"
            for i, item in enumerate(items[:5], 1):  # Show first 5 results
                attrs = item.get("attributes", {})
                result_text += f"{i}. SKU: {item['sku']}\n"
                result_text += f"   Title: {attrs.get('title', 'N/A')}\n"
                result_text += f"   Price: ${attrs.get('price', 'N/A')}\n"
                result_text += f"   Status: {item['status']}\n\n"

            if len(items) > 5:
                result_text += f"... and {len(items) - 5} more results\n"

            result_text += f"Total: {pagination.get('total', len(items))} listings"
            return result_text
        else:
            return f"Error searching listings: {result.error}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("This tool only supports async execution")


# Tool registry
def get_mcp_tools() -> List[BaseTool]:
    """Get all available MCP tools as LangChain tools"""
    return [
        CreateSessionTool(),
        GetListingItemTool(),
        CreateOrUpdateListingTool(),
        UpdateListingPartialTool(),
        DeleteListingItemTool(),
        SearchListingsTool(),
    ]


# Auto-inject session_id for tools that need it
def inject_session_id(tools: List[BaseTool], session_id: str) -> List[BaseTool]:
    """Inject session_id into tools that require it"""
    for tool in tools:
        if hasattr(tool.args_schema, "__fields__") and "session_id" in tool.args_schema.__fields__:
            # Create a wrapper that automatically injects session_id
            original_arun = tool._arun

            async def wrapped_arun(**kwargs):
                if "session_id" not in kwargs:
                    kwargs["session_id"] = session_id
                return await original_arun(**kwargs)

            tool._arun = wrapped_arun

    return tools

from mcp.server.fastmcp import FastMCP
import requests
from typing import List, Dict, Optional, Any
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("RL-Gym Amazon SP-API Assistant")

# Base URL for the Amazon SP-API mock service
BASE_URL = "http://localhost:8001"

# =============================================================================
# LISTINGS ITEMS APIs (2021-08-01)
# =============================================================================

@mcp.tool()
def get_listings_item(
    seller_id: str,
    sku: str,
    marketplace_ids: Optional[str] = "ATVPDKIKX0DER",
    included_data: Optional[str] = "summaries",
    issue_locale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get details for a specific listing item by seller ID and SKU.
    
    This API retrieves comprehensive information about a specific product listing,
    including summaries, offers, fulfillment availability, and any issues.
    
    Args:
        seller_id: The seller identifier (e.g., "SELLER001", "SELLER002")
        sku: The seller's Stock Keeping Unit identifier (e.g., "SKU-123456-001")
        marketplace_ids: Comma-separated list of Amazon marketplace IDs 
                        (default: "ATVPDKIKX0DER" for US marketplace)
                        Common values: "ATVPDKIKX0DER" (US), "A2EUQ1WTGCTBG2" (CA), "A1PA6795UKMFR9" (DE)
        included_data: Comma-separated list of data sets to include in response
                      Options: "summaries", "offers", "fulfillmentAvailability", "issues"
                      (default: "summaries")
        issue_locale: Locale for issue message localization (e.g., "en_US", "es_ES")
                     
    Returns:
        Dict containing:
            - sku: The SKU identifier
            - summaries: List of product summaries with ASIN, product type, status, etc.
            - offers: List of pricing offers if requested
            - fulfillmentAvailability: Inventory availability if requested  
            - issues: List of listing issues/errors if any exist
            
    Example Response:
        {
            "sku": "GM-ZDPI-9B4E",
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "asin": "B071VG5N9D", 
                    "productType": "LUGGAGE",
                    "conditionType": "new_new",
                    "status": ["BUYABLE"],
                    "itemName": "Hardside Carry-On Spinner Suitcase Luggage",
                    "createdDate": "2021-02-01T00:00:00Z",
                    "lastUpdatedDate": "2021-03-01T00:00:00Z",
                    "mainImage": {
                        "link": "https://www.example.com/luggage.png",
                        "height": 500,
                        "width": 500
                    }
                }
            ],
            "offers": [...],
            "fulfillmentAvailability": [...],
            "issues": [...]
        }
    """
    try:
        params = {
            "marketplaceIds": marketplace_ids,
            "includedData": included_data
        }
        if issue_locale:
            params["issueLocale"] = issue_locale
            
        response = requests.get(
            f"{BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {
                "success": False,
                "error": f"Listing not found for seller {seller_id} and SKU {sku}",
                "status_code": 404
            }
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for get_listings_item: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def put_listings_item(
    seller_id: str,
    sku: str,
    product_type: str,
    attributes: Dict[str, Any],
    marketplace_ids: Optional[str] = "ATVPDKIKX0DER",
    included_data: Optional[str] = None,
    issue_locale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or fully update a listing item.
    
    This API creates a new listing or completely replaces an existing listing
    with the provided data. Use this for initial listing creation or full updates.
    
    Args:
        seller_id: The seller identifier (e.g., "SELLER001", "SELLER002") 
        sku: The seller's Stock Keeping Unit identifier (e.g., "SKU-123456-001")
        product_type: Amazon product type (e.g., "LUGGAGE", "ELECTRONICS", "CLOTHING")
        attributes: Complete product attributes dictionary containing:
                   - item_name: Product title
                   - brand: Brand name
                   - bullet_point: List of product features
                   - product_description: Detailed description
                   - list_price: Price information
                   - condition_type: Product condition
                   - And other product-specific attributes
        marketplace_ids: Comma-separated list of marketplace IDs (default: "ATVPDKIKX0DER")
        included_data: Data sets to include in response (e.g., "issues")
        issue_locale: Locale for issue messages (e.g., "en_US")
        
    Returns:
        Dict containing:
            - sku: The SKU identifier
            - status: Submission status ("ACCEPTED", "REJECTED") 
            - submissionId: Unique submission identifier for tracking
            - issues: List of any validation issues
            
    Example Usage:
        attributes = {
            "item_name": [{"value": "Premium Bluetooth Headphones", "language_tag": "en_US"}],
            "brand": [{"value": "TechBrand", "language_tag": "en_US"}],
            "bullet_point": [
                {"value": "Wireless Bluetooth 5.0 connectivity", "language_tag": "en_US"},
                {"value": "30-hour battery life", "language_tag": "en_US"}
            ],
            "list_price": [{"value": 99.99, "currency": "USD"}],
            "condition_type": "new_new"
        }
    """
    try:
        params = {
            "marketplaceIds": marketplace_ids
        }
        if included_data:
            params["includedData"] = included_data
        if issue_locale:
            params["issueLocale"] = issue_locale
            
        request_data = {
            "productType": product_type,
            "attributes": attributes
        }
        
        response = requests.put(
            f"{BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}",
            params=params,
            json=request_data
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for put_listings_item: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def patch_listings_item(
    seller_id: str,
    sku: str,
    patches: List[Dict[str, Any]],
    marketplace_ids: Optional[str] = "ATVPDKIKX0DER",
    included_data: Optional[str] = None,
    issue_locale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Partially update a listing item using JSON Patch operations.
    
    This API allows selective updates to specific fields of an existing listing
    without replacing the entire listing data. Use this for targeted modifications.
    
    Args:
        seller_id: The seller identifier (e.g., "SELLER001", "SELLER002")
        sku: The seller's Stock Keeping Unit identifier (e.g., "SKU-123456-001")
        patches: List of JSON Patch operations, each containing:
                - op: Operation type ("add", "replace", "remove")
                - path: JSON path to the field (e.g., "/attributes/item_name")
                - value: New value for add/replace operations
        marketplace_ids: Comma-separated list of marketplace IDs (default: "ATVPDKIKX0DER")
        included_data: Data sets to include in response (e.g., "issues")
        issue_locale: Locale for issue messages (e.g., "en_US")
        
    Returns:
        Dict containing:
            - sku: The SKU identifier
            - status: Submission status ("ACCEPTED", "REJECTED")
            - submissionId: Unique submission identifier for tracking
            - issues: List of any validation issues
            
    Example Patch Operations:
        [
            {
                "op": "replace",
                "path": "/attributes/item_name",
                "value": [{"value": "Updated Product Name", "language_tag": "en_US"}]
            },
            {
                "op": "add", 
                "path": "/attributes/bullet_point/-",
                "value": {"value": "New feature added", "language_tag": "en_US"}
            },
            {
                "op": "remove",
                "path": "/attributes/old_attribute"
            }
        ]
    """
    try:
        params = {
            "marketplaceIds": marketplace_ids
        }
        if included_data:
            params["includedData"] = included_data
        if issue_locale:
            params["issueLocale"] = issue_locale
            
        request_data = {
            "patches": patches
        }
        
        response = requests.patch(
            f"{BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}",
            params=params,
            json=request_data
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {
                "success": False,
                "error": f"Listing not found for seller {seller_id} and SKU {sku}",
                "status_code": 404
            }
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for patch_listings_item: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def delete_listings_item(
    seller_id: str,
    sku: str,
    marketplace_ids: Optional[str] = "ATVPDKIKX0DER",
    issue_locale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a listing item from Amazon marketplace.
    
    This API removes a listing from the specified marketplace(s). The listing
    will no longer be available for purchase. Use with caution as this action
    may affect active orders and customer experience.
    
    Args:
        seller_id: The seller identifier (e.g., "SELLER001", "SELLER002")
        sku: The seller's Stock Keeping Unit identifier (e.g., "SKU-123456-001")
        marketplace_ids: Comma-separated list of marketplace IDs to delete from
                        (default: "ATVPDKIKX0DER" for US marketplace)
        issue_locale: Locale for issue messages (e.g., "en_US", "es_ES")
        
    Returns:
        Dict containing:
            - sku: The SKU identifier that was deleted
            - status: Deletion status ("ACCEPTED", "REJECTED")
            - submissionId: Unique submission identifier for tracking
            - issues: List of any issues encountered during deletion
            
    Note:
        - Deletion may not be immediate and could take time to process
        - Some marketplaces may restrict deletion of listings with recent orders
        - Consider using inventory updates to zero instead of deletion for temporary unavailability
    """
    try:
        params = {
            "marketplaceIds": marketplace_ids
        }
        if issue_locale:
            params["issueLocale"] = issue_locale
            
        response = requests.delete(
            f"{BASE_URL}/listings/2021-08-01/items/{seller_id}/{sku}",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {
                "success": False,
                "error": f"Listing not found for seller {seller_id} and SKU {sku}",
                "status_code": 404
            }
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for delete_listings_item: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def search_listings_items(
    seller_id: str,
    marketplace_ids: str,
    included_data: Optional[str] = "summaries",
    identifiers: Optional[str] = None,
    identifiers_type: Optional[str] = None,
    page_size: int = 10,
    page_token: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "ASC"
) -> Dict[str, Any]:
    """
    Search and retrieve multiple listing items for a seller.
    
    This API allows you to search through all listings for a seller with various
    filtering, sorting, and pagination options. Ideal for bulk operations and
    inventory management.
    
    Args:
        seller_id: The seller identifier (e.g., "SELLER001", "SELLER002")
        marketplace_ids: Comma-separated list of marketplace IDs to search in
                        (e.g., "ATVPDKIKX0DER,A2EUQ1WTGCTBG2")
        included_data: Comma-separated list of data sets to include
                      Options: "summaries", "offers", "fulfillmentAvailability", "issues"
                      (default: "summaries")
        identifiers: Comma-separated list of specific identifiers to search for
                    (e.g., "SKU-123456-001,SKU-789012-001" or "B071VG5N9D,B08N5WRWNW")
        identifiers_type: Type of identifiers provided
                         Options: "SKU", "ASIN"
        page_size: Number of results per page (1-50, default: 10)
        page_token: Token for pagination to get next set of results
        sort_by: Field to sort results by
                Options: "lastUpdatedDate", "createdDate", "sku"
        sort_order: Sort order - "ASC" for ascending, "DESC" for descending
        
    Returns:
        Dict containing:
            - numberOfResults: Total number of matching listings
            - pagination: Pagination information with nextToken if more results exist
            - items: List of listing items with requested data
            
    Example Response:
        {
            "numberOfResults": 3,
            "pagination": {
                "nextToken": "abc123...",
                "previousToken": "def456..."
            },
            "items": [
                {
                    "sku": "GM-ZDPI-9B4E",
                    "summaries": [...],
                    "attributes": {...},
                    "offers": [...],
                    "fulfillmentAvailability": [...],
                    "issues": [...]
                }
            ]
        }
        
    Use Cases:
        - Get all listings for inventory review
        - Search for listings with specific issues
        - Bulk price updates by filtering specific SKUs
        - Monitor listing status changes
    """
    try:
        params = {
            "marketplaceIds": marketplace_ids,
            "includedData": included_data,
            "pageSize": page_size,
            "sortOrder": sort_order
        }
        
        if identifiers:
            params["identifiers"] = identifiers
        if identifiers_type:
            params["identifiersType"] = identifiers_type
        if page_token:
            params["pageToken"] = page_token
        if sort_by:
            params["sortBy"] = sort_by
            
        response = requests.get(
            f"{BASE_URL}/listings/2021-08-01/items/{seller_id}",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for search_listings_items: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

# =============================================================================
# DATABASE RESET APIs
# =============================================================================

@mcp.tool()
def reset_database() -> Dict[str, Any]:
    """
    Reset the database to its initial seeded state.
    
    This powerful administrative tool clears all existing data and restores
    the database to its original state with all seed data. This is extremely
    useful for testing, development, and demo scenarios.
    
    WARNING: This operation will permanently delete all current data!
    
    What this does:
        1. Clears all existing data from all tables (orders, listings, inventory, etc.)
        2. Restores original seed data including:
           - 10 sellers across different marketplaces
           - 50 realistic orders with various statuses
           - 10 catalog items (ASINs) with full product details
           - Complete inventory, listing, and pricing data
           - Invoice, sales, and messaging sample data
        3. Provides detailed execution report
        
    Returns:
        Dict containing:
            - success: Boolean indicating if reset was successful
            - message: Summary message
            - details: Comprehensive execution details including:
                - start_time: When the reset began
                - end_time: When the reset completed
                - duration_seconds: Total execution time
                - tables_cleared: List of tables that were cleared
                - seed_migrations_executed: Details of data restoration
                - total_records_inserted: Total number of records restored
                - status: Overall operation status
                
    Example Response:
        {
            "success": true,
            "message": "Database reset to initial state successfully",
            "details": {
                "start_time": "2024-01-01T12:00:00.000000",
                "end_time": "2024-01-01T12:00:15.543210", 
                "duration_seconds": 15.54,
                "tables_cleared": ["order_items", "orders", "listings", "inventory", ...],
                "seed_migrations_executed": [
                    {"migration": "002_seed_data", "status": "success"},
                    {"migration": "004_seed_invoices_data", "status": "success"}
                ],
                "total_records_inserted": 1250,
                "status": "success"
            }
        }
        
    Use Cases:
        - Reset after testing that modified data
        - Restore predictable demo data
        - Clean development environment
        - Prepare for integration testing
        
    Security:
        - Only available in development environment
        - No authentication required for testing convenience
    """
    try:
        response = requests.post(f"{BASE_URL}/admin/reset-database")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Database reset failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for reset_database: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def get_database_status() -> Dict[str, Any]:
    """
    Get current database status and record counts.
    
    This diagnostic tool provides comprehensive information about the current
    state of the database, including health status and record counts for all
    tables. Very useful for verification and monitoring.
    
    Returns:
        Dict containing:
            - success: Boolean indicating if status check was successful
            - status: Database status information including:
                - database_health: Overall health and connection status
                - table_counts: Record count for each table
                - total_records: Sum of all records across all tables
            - timestamp: When the status was checked
            
    Example Response:
        {
            "success": true,
            "status": {
                "database_health": {
                    "status": "healthy",
                    "connection": "active", 
                    "tables_count": 23
                },
                "table_counts": {
                    "sellers": 10,
                    "catalog_items": 10,
                    "orders": 50,
                    "order_items": 75,
                    "inventory": 10,
                    "listings": 10,
                    "invoices": 50,
                    "sales_metrics": 189,
                    "product_fees": 28,
                    "messaging_actions": 64,
                    "buyer_attributes": 10,
                    "messages": 6
                },
                "total_records": 1250
            },
            "timestamp": "2024-01-01T12:00:00.000000"
        }
        
    Use Cases:
        - Verify database health before testing
        - Check if reset was successful
        - Monitor database growth during development
        - Troubleshoot data issues
        - Validate seed data integrity
    """
    try:
        response = requests.get(f"{BASE_URL}/admin/database-status")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Database status check failed with status {response.status_code}",
                "message": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for get_database_status: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

# =============================================================================
# HELPER RESOURCES
# =============================================================================

@mcp.resource("amazon://listings/examples")
def get_listings_examples() -> str:
    """Get examples of listing attributes for different product types."""
    return json.dumps({
        "LUGGAGE": {
            "item_name": [{"value": "Hardside Carry-On Spinner Suitcase", "language_tag": "en_US"}],
            "brand": [{"value": "TravelPro", "language_tag": "en_US"}],
            "bullet_point": [
                {"value": "Lightweight yet durable hardside construction", "language_tag": "en_US"},
                {"value": "360-degree spinner wheels for smooth rolling", "language_tag": "en_US"},
                {"value": "TSA-approved combination lock", "language_tag": "en_US"}
            ],
            "list_price": [{"value": 199.99, "currency": "USD"}],
            "condition_type": "new_new",
            "product_description": [{"value": "Premium hardside luggage perfect for business and leisure travel", "language_tag": "en_US"}]
        },
        "ELECTRONICS": {
            "item_name": [{"value": "Wireless Bluetooth Headphones", "language_tag": "en_US"}],
            "brand": [{"value": "AudioTech", "language_tag": "en_US"}],
            "bullet_point": [
                {"value": "Advanced noise cancellation technology", "language_tag": "en_US"},
                {"value": "30-hour battery life", "language_tag": "en_US"},
                {"value": "Bluetooth 5.0 connectivity", "language_tag": "en_US"}
            ],
            "list_price": [{"value": 149.99, "currency": "USD"}],
            "condition_type": "new_new"
        }
    }, indent=2)

@mcp.resource("amazon://marketplace/ids")
def get_marketplace_ids() -> str:
    """Get common Amazon marketplace IDs."""
    return json.dumps({
        "ATVPDKIKX0DER": "Amazon US",
        "A2EUQ1WTGCTBG2": "Amazon Canada", 
        "A1PA6795UKMFR9": "Amazon Germany",
        "A1RKKUPIHCS9HS": "Amazon Spain",
        "A13V1IB3VIYZZH": "Amazon France",
        "APJ6JRA9NG5V4": "Amazon Italy",
        "A1F83G8C2ARO7P": "Amazon UK",
        "A21TJRUUN4KGV": "Amazon India",
        "A1VC38T7YXB528": "Amazon Japan",
        "AAHKV2X7AFYLW": "Amazon China",
        "A39IBJ37TRP1C6": "Amazon Australia",
        "A2Q3Y263D00KWC": "Amazon Brazil",
        "A1AM78C64UM0Y8": "Amazon Mexico",
        "A1805IZSGTT6HS": "Amazon Netherlands",
        "A1C3SOZRARQ6R3": "Amazon Poland",
        "A17E79C6D8DWNP": "Amazon Saudi Arabia",
        "A2VIGQ35RCS4UG": "Amazon UAE",
        "A33AVAJ2PDY3EV": "Amazon Turkey",
        "A19VAU5U5O7RUS": "Amazon Singapore",
        "A1ZWQCGRT6QEQY": "Amazon Egypt"
    }, indent=2)

@mcp.resource("amazon://sellers/examples")
def get_seller_examples() -> str:
    """Get example seller IDs available in the system."""
    return json.dumps({
        "SELLER001": "TechGadgets Pro - Electronics seller in US marketplace",
        "SELLER002": "Home & Garden Essentials - Home products seller in US marketplace", 
        "SELLER003": "Fashion Forward - Clothing and accessories seller in US marketplace",
        "SELLER004": "Sports & Outdoors Co - Sports equipment seller in Canada marketplace",
        "SELLER005": "Books & Media Store - Books and media seller in Germany marketplace",
        "SELLER006": "Baby & Kids World - Baby products seller in US marketplace",
        "SELLER007": "Health & Beauty Plus - Beauty products seller in France marketplace",
        "SELLER008": "Automotive Solutions - Auto parts seller in US marketplace",
        "SELLER009": "Pet Supplies Central - Pet products seller in US marketplace",
        "SELLER010": "Kitchen & Dining Pro - Kitchen products seller in UK marketplace"
    }, indent=2)

if __name__ == "__main__":
    # Start the MCP server
    mcp.run()
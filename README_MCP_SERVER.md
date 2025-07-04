# RL-Gym Amazon SP-API MCP Server

This MCP (Model Context Protocol) server provides comprehensive access to Amazon Selling Partner API mock services, specifically focusing on Listings Items APIs and database management functionality. It's designed to help developers and AI assistants interact with Amazon marketplace data efficiently.

## Features

### 📦 Listings Items APIs (2021-08-01)
- **GET Listing Item** - Retrieve detailed information for a specific listing
- **PUT Listing Item** - Create or fully update a listing
- **PATCH Listing Item** - Partially update a listing using JSON Patch operations
- **DELETE Listing Item** - Remove a listing from marketplace
- **SEARCH Listing Items** - Search and filter multiple listings with pagination

### 🗄️ Database Management APIs
- **Reset Database** - Restore database to initial seeded state
- **Get Database Status** - Check database health and record counts

### 📚 Helper Resources
- **Listing Examples** - Sample attributes for different product types
- **Marketplace IDs** - Common Amazon marketplace identifiers
- **Seller Examples** - Available test seller accounts

## Installation

1. **Install dependencies:**
```bash
pip install fastmcp requests
```

2. **Start the Amazon SP-API mock service:**
```bash
cd services/amazon
docker-compose up -d
```

3. **Run the MCP server:**
```bash
python rl_gym_mcp_server.py
```

## Configuration

The server connects to the Amazon SP-API mock service at:
- **Base URL**: `http://localhost:8001`
- **Service**: Amazon SP-API Mock (should be running via Docker)

## API Tools Documentation

### Listings Items APIs

#### 🔍 get_listings_item
Retrieve comprehensive details for a specific listing.

**Parameters:**
- `seller_id` (required): Seller identifier (e.g., "SELLER001")
- `sku` (required): Stock Keeping Unit identifier (e.g., "SKU-123456-001")
- `marketplace_ids` (optional): Comma-separated marketplace IDs (default: "ATVPDKIKX0DER")
- `included_data` (optional): Data sets to include - "summaries", "offers", "fulfillmentAvailability", "issues"
- `issue_locale` (optional): Locale for issue messages (e.g., "en_US")

**Example:**
```python
result = get_listings_item(
    seller_id="SELLER001",
    sku="SKU-123456-001",
    marketplace_ids="ATVPDKIKX0DER",
    included_data="summaries,offers,issues"
)
```

#### ✏️ put_listings_item
Create or completely update a listing.

**Parameters:**
- `seller_id` (required): Seller identifier
- `sku` (required): Stock Keeping Unit identifier
- `product_type` (required): Amazon product type (e.g., "LUGGAGE", "ELECTRONICS")
- `attributes` (required): Complete product attributes dictionary
- `marketplace_ids` (optional): Target marketplaces
- `included_data` (optional): Response data sets
- `issue_locale` (optional): Issue message locale

**Example:**
```python
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

result = put_listings_item(
    seller_id="SELLER001",
    sku="SKU-NEW-001",
    product_type="ELECTRONICS",
    attributes=attributes
)
```

#### 🔧 patch_listings_item
Partially update specific fields of a listing.

**Parameters:**
- `seller_id` (required): Seller identifier
- `sku` (required): Stock Keeping Unit identifier
- `patches` (required): List of JSON Patch operations
- `marketplace_ids` (optional): Target marketplaces
- `included_data` (optional): Response data sets
- `issue_locale` (optional): Issue message locale

**Example:**
```python
patches = [
    {
        "op": "replace",
        "path": "/attributes/list_price",
        "value": [{"value": 89.99, "currency": "USD"}]
    },
    {
        "op": "add",
        "path": "/attributes/bullet_point/-",
        "value": {"value": "New feature added", "language_tag": "en_US"}
    }
]

result = patch_listings_item(
    seller_id="SELLER001",
    sku="SKU-123456-001",
    patches=patches
)
```

#### 🗑️ delete_listings_item
Remove a listing from marketplace.

**Parameters:**
- `seller_id` (required): Seller identifier
- `sku` (required): Stock Keeping Unit identifier
- `marketplace_ids` (optional): Target marketplaces
- `issue_locale` (optional): Issue message locale

**Example:**
```python
result = delete_listings_item(
    seller_id="SELLER001",
    sku="SKU-123456-001",
    marketplace_ids="ATVPDKIKX0DER"
)
```

#### 🔍 search_listings_items
Search and retrieve multiple listings with filtering and pagination.

**Parameters:**
- `seller_id` (required): Seller identifier
- `marketplace_ids` (required): Comma-separated marketplace IDs
- `included_data` (optional): Data sets to include
- `identifiers` (optional): Specific identifiers to search for
- `identifiers_type` (optional): Type of identifiers ("SKU", "ASIN")
- `page_size` (optional): Results per page (1-50, default: 10)
- `page_token` (optional): Pagination token
- `sort_by` (optional): Sort field ("lastUpdatedDate", "createdDate", "sku")
- `sort_order` (optional): Sort order ("ASC", "DESC")

**Example:**
```python
result = search_listings_items(
    seller_id="SELLER001",
    marketplace_ids="ATVPDKIKX0DER",
    included_data="summaries,offers",
    identifiers="SKU-123456-001,SKU-789012-001",
    identifiers_type="SKU",
    page_size=20,
    sort_by="lastUpdatedDate",
    sort_order="DESC"
)
```

### Database Management APIs

#### 🔄 reset_database
Reset the database to initial seeded state.

**⚠️ WARNING: This permanently deletes all current data!**

**Returns:**
- Comprehensive execution report
- List of cleared tables
- Details of restored data
- Total records inserted

**Example:**
```python
result = reset_database()
print(f"Reset completed in {result['details']['duration_seconds']} seconds")
print(f"Total records restored: {result['details']['total_records_inserted']}")
```

#### 📊 get_database_status
Check current database health and record counts.

**Returns:**
- Database health status
- Record counts per table
- Total records across all tables
- Timestamp of check

**Example:**
```python
status = get_database_status()
print(f"Total records: {status['status']['total_records']}")
print(f"Orders: {status['status']['table_counts']['orders']}")
print(f"Listings: {status['status']['table_counts']['listings']}")
```

## Available Test Data

### Sellers
- **SELLER001**: TechGadgets Pro (US)
- **SELLER002**: Home & Garden Essentials (US)
- **SELLER003**: Fashion Forward (US)
- **SELLER004**: Sports & Outdoors Co (Canada)
- **SELLER005**: Books & Media Store (Germany)
- **SELLER006**: Baby & Kids World (US)
- **SELLER007**: Health & Beauty Plus (France)
- **SELLER008**: Automotive Solutions (US)
- **SELLER009**: Pet Supplies Central (US)
- **SELLER010**: Kitchen & Dining Pro (UK)

### Marketplace IDs
- **ATVPDKIKX0DER**: Amazon US
- **A2EUQ1WTGCTBG2**: Amazon Canada
- **A1PA6795UKMFR9**: Amazon Germany
- **A13V1IB3VIYZZH**: Amazon France
- **A1F83G8C2ARO7P**: Amazon UK
- **A21TJRUUN4KGV**: Amazon India
- **A1VC38T7YXB528**: Amazon Japan

### Product Types
- **LUGGAGE**: Suitcases, bags, travel accessories
- **ELECTRONICS**: Headphones, speakers, tech gadgets
- **CLOTHING**: Apparel, shoes, accessories
- **HOME**: Furniture, kitchen, garden items
- **SPORTS**: Athletic equipment, outdoor gear

## Common Use Cases

### 1. Creating a New Listing
```python
# First, create the listing
result = put_listings_item(
    seller_id="SELLER001",
    sku="MY-NEW-PRODUCT-001",
    product_type="ELECTRONICS",
    attributes={
        "item_name": [{"value": "Amazing Wireless Speaker", "language_tag": "en_US"}],
        "brand": [{"value": "AudioBrand", "language_tag": "en_US"}],
        "list_price": [{"value": 79.99, "currency": "USD"}],
        "condition_type": "new_new"
    }
)

# Then verify it was created
listing = get_listings_item(
    seller_id="SELLER001",
    sku="MY-NEW-PRODUCT-001"
)
```

### 2. Bulk Price Updates
```python
# Search for listings to update
listings = search_listings_items(
    seller_id="SELLER001",
    marketplace_ids="ATVPDKIKX0DER",
    identifiers="SKU-001,SKU-002,SKU-003",
    identifiers_type="SKU"
)

# Update prices for each listing
for item in listings["items"]:
    patch_listings_item(
        seller_id="SELLER001",
        sku=item["sku"],
        patches=[{
            "op": "replace",
            "path": "/attributes/list_price",
            "value": [{"value": 99.99, "currency": "USD"}]
        }]
    )
```

### 3. Development Workflow
```python
# Check current database state
status = get_database_status()
print(f"Current listings: {status['status']['table_counts']['listings']}")

# Run tests that modify data
# ... your test code ...

# Reset to clean state
reset_result = reset_database()
print(f"Database reset: {reset_result['success']}")

# Verify reset
new_status = get_database_status()
print(f"Listings after reset: {new_status['status']['table_counts']['listings']}")
```

## Error Handling

The server provides comprehensive error information:

```python
result = get_listings_item(seller_id="INVALID", sku="NOT-FOUND")
if not result.get("success", True):
    print(f"Error: {result['error']}")
    print(f"Status Code: {result.get('status_code')}")
    print(f"Message: {result.get('message')}")
```

## Best Practices

1. **Use Specific Marketplace IDs**: Always specify the correct marketplace for your region
2. **Include Relevant Data**: Only request the data sets you need to improve performance
3. **Handle Pagination**: For large result sets, use pagination tokens
4. **Validate Attributes**: Ensure product attributes match Amazon's requirements
5. **Test with Reset**: Use database reset for consistent testing environments
6. **Monitor Status**: Check database status before and after operations

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the Amazon SP-API mock service is running
2. **404 Errors**: Check that seller_id and sku exist in the database
3. **Invalid Attributes**: Verify product attributes match the product type requirements
4. **Rate Limiting**: The mock service may have rate limits enabled

### Service Health Check
```python
# Check if the service is responding
status = get_database_status()
if status.get("success"):
    print("Service is healthy")
else:
    print("Service may be down")
```

## Contributing

To extend this MCP server:

1. Add new tool functions following the existing pattern
2. Include comprehensive docstrings with parameter descriptions
3. Add proper error handling and logging
4. Update this README with new functionality

## License

This MCP server is part of the RL-Gym project and follows the project's licensing terms.
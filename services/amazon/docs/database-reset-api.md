# Database Reset API

The Amazon SP-API Mock Service includes a database reset functionality that allows you to restore the database to its initial seeded state. This is useful for testing scenarios where you want to reset all data back to a clean, known state.

## Available Endpoints

### POST `/admin/reset-database`

Resets the database to initial seeded state by:
1. Clearing all existing data from all tables
2. Re-executing all seed migration files in the correct order
3. Restoring the database to the exact state after initial migrations

**Requirements:**
- Only available when `ENVIRONMENT=development`
- No authentication required (for easy testing)

**Request:**
```bash
curl -X POST http://localhost:8001/admin/reset-database
```

**Response:**
```json
{
  "success": true,
  "message": "Database reset to initial state successfully",
  "details": {
    "start_time": "2024-01-01T12:00:00.000000",
    "end_time": "2024-01-01T12:00:15.543210",
    "duration_seconds": 15.54,
    "tables_cleared": [
      "order_items",
      "notifications", 
      "finances",
      "product_pricing",
      "..."
    ],
    "seed_migrations_executed": [
      {
        "migration": "002_seed_data",
        "status": "success",
        "message": "Successfully executed 002_seed_data"
      },
      {
        "migration": "004_seed_invoices_data", 
        "status": "success",
        "message": "Successfully executed 004_seed_invoices_data"
      }
    ],
    "total_records_inserted": 1250,
    "status": "success"
  }
}
```

### GET `/admin/database-status`

Get current database status and record counts for verification.

**Request:**
```bash
curl http://localhost:8001/admin/database-status
```

**Response:**
```json
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
      "product_pricing": 10,
      "reports": 8,
      "feeds": 6,
      "invoices": 50,
      "invoice_documents": 30,
      "invoice_exports": 10,
      "sales_metrics": 189,
      "product_fees": 28,
      "messaging_actions": 64,
      "buyer_attributes": 10,
      "messages": 6,
      "..."
    },
    "total_records": 1250
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## Usage Scenarios

### 1. Reset After Testing
After running tests that modify data, reset to clean state:
```bash
# Run your tests that modify data
curl -X POST http://localhost:8001/orders/v0/orders

# Reset database back to initial state  
curl -X POST http://localhost:8001/admin/reset-database

# Verify reset was successful
curl http://localhost:8001/admin/database-status
```

### 2. Restore Known Test Data
When you need predictable test data for demos or development:
```bash
# Reset to get exactly the seeded test data
curl -X POST http://localhost:8001/admin/reset-database

# Now you have exactly:
# - 10 sellers
# - 50 orders with realistic data
# - 10 catalog items with full product information
# - Comprehensive invoice, sales, and messaging data
```

### 3. Development Workflow
```bash
# Check current state
curl http://localhost:8001/admin/database-status

# Make changes/test APIs
curl -X POST http://localhost:8001/listings/2021-08-01/listings
curl -X POST http://localhost:8001/orders/v0/orders

# Reset when needed
curl -X POST http://localhost:8001/admin/reset-database
```

## What Gets Reset

The reset API will restore these tables with their initial seed data:

### Core Data (from `002_seed_data.py`)
- **sellers**: 10 sellers across different marketplaces
- **catalog_items**: 10 ASINs with full product details
- **orders**: 50 realistic orders with various statuses
- **order_items**: Order line items linked to catalog products
- **inventory**: FBA inventory for all products
- **listings**: Product listings with attributes
- **product_pricing**: Competitive pricing data
- **reports**: Sample report generation data
- **feeds**: Feed processing examples

### Invoice Data (from `004_seed_invoices_data.py`)
- **invoice_attributes**: Tax invoice configuration data
- **invoices**: 50 sample invoices with different types and statuses
- **invoice_documents**: PDF document references
- **invoice_exports**: Export job examples

### Sales Data (from `006_seed_sales_data.py`)
- **sales_metrics**: 189 records of sales analytics across different time periods, buyer types, and ASINs

### Product Fees Data (from `008_seed_product_fees_data.py`)
- **product_fees**: 28 fee calculation records across different product categories and marketplaces

### Messaging Data (from `010_seed_messaging_data.py`)
- **messaging_actions**: 64 available messaging actions for orders
- **buyer_attributes**: Buyer locale and language preferences
- **messages**: 6 sample sent messages

### Catalog Data (from `012_seed_catalog_data.py`)
- **catalog_categories**: Product category hierarchy
- Enhanced catalog item data with full Amazon-style product information

## Technical Details

### Execution Order
1. **Clear Phase**: Tables are truncated in dependency order (child tables first)
2. **Seed Phase**: Migration files are executed in chronological order
3. **Verification Phase**: Record counts are calculated for confirmation

### Safety Features
- Only runs in development environment
- Uses database transactions for consistency
- Detailed logging of all operations
- Graceful error handling with rollback

### Performance
- Uses `TRUNCATE CASCADE` for fast deletion
- Bulk inserts for efficient data restoration
- Typical reset time: 10-20 seconds depending on database size

## Error Handling

If the reset fails, you'll get a detailed error response:
```json
{
  "success": false,
  "status": "failed",
  "errors": ["Specific error message here"],
  "details": {
    "tables_cleared": ["list of successfully cleared tables"],
    "seed_migrations_executed": ["partial migration results"]
  }
}
```

Common issues and solutions:
- **Permission errors**: Ensure database user has TRUNCATE privileges
- **Foreign key constraints**: The service handles this automatically with CASCADE
- **Missing migration files**: Check that all seed files exist in `alembic/versions/`

## Integration with Testing

Example test setup:
```python
import requests

def setup_test_data():
    """Reset database before each test suite."""
    response = requests.post("http://localhost:8001/admin/reset-database")
    assert response.json()["success"] == True
    
def test_order_api():
    setup_test_data()
    # Now test with known seed data
    response = requests.get("http://localhost:8001/orders/v0/orders") 
    assert len(response.json()["orders"]) == 50  # From seed data
```

This reset API provides a powerful tool for maintaining clean, predictable test environments while developing and testing against the Amazon SP-API mock service.
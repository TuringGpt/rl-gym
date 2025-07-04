# Testing Workflow Guide

## Overview

This testing system provides a minimal workflow to validate that Claude performs actions correctly against your Amazon SP-API mock database. It includes predefined test flows with deterministic expected results and APIs to validate and reset the system.

## Quick Start

### 1. Start the FastAPI Server
```bash
python app/main.py
# or
uvicorn app.main:app --reload
```

### 2. Reset Database to Seed State
```bash
curl -X POST http://localhost:8000/test/reset
```

### 3. Get Available Test Flows
```bash
curl http://localhost:8000/test/flows
```

### 4. Ask Claude to Perform a Test Action
Example: "Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001', title 'Test Gaming Laptop', description 'High-performance gaming laptop for testing', price $999.99, quantity 50, status ACTIVE, and marketplace_ids ['ATVPDKIKX0DER']"

### 5. Validate the Result
```bash
curl http://localhost:8000/test/validate/flow_1_create_laptop
```

### 6. Reset for Next Test
```bash
curl -X POST http://localhost:8000/test/reset
```

## Available Test Flows

### 1. **flow_1_create_laptop** - Create New Laptop Listing
- **Claude Instruction**: "Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001', title 'Test Gaming Laptop', description 'High-performance gaming laptop for testing', price $999.99, quantity 50, status ACTIVE, and marketplace_ids ['ATVPDKIKX0DER']"
- **Validates**: Item creation with correct fields

### 2. **flow_2_update_laptop_price** - Update Laptop Price and Quantity
- **Claude Instruction**: "Update SELLER001's LAPTOP-001 listing to change the price to $1199.99 and reduce quantity to 20"
- **Validates**: Price and quantity updates

### 3. **flow_3_delete_cable** - Delete Cable Listing
- **Claude Instruction**: "Delete SELLER003's CABLE-001 listing (set status to INACTIVE)"
- **Validates**: Status change to INACTIVE

### 4. **flow_4_search_bookwise** - Search BookWise Listings
- **Claude Instruction**: "Search for all active listings from SELLER002 (BookWise Publishing)"
- **Validates**: Search results and seller filtering

### 5. **flow_5_search_gaming** - Search Gaming Products
- **Claude Instruction**: "Search for all products that have 'gaming' in the title or description"
- **Validates**: Text search functionality

### 6. **flow_6_price_range_search** - Search Price Range $20-$50
- **Claude Instruction**: "Find all listings with prices between $20 and $50"
- **Validates**: Price range filtering

### 7. **flow_7_deactivate_fitness** - Deactivate Fitness Products
- **Claude Instruction**: "Set all listings from SELLER005 (FitLife Sports) to INACTIVE status"
- **Validates**: Bulk status updates

### 8. **flow_8_add_canada_kitchen** - Add Canada Marketplace to Kitchen Products
- **Claude Instruction**: "Update all listings from SELLER006 (KitchenPro Essentials) to include the Canada marketplace (A2EUQ1WTGCTBG2) in their marketplace_ids"
- **Validates**: Bulk marketplace updates

### 9. **flow_9_most_expensive_per_seller** - Find Most Expensive Product Per Seller
- **Claude Instruction**: "Find the most expensive (highest priced) product from each seller"
- **Validates**: Analysis and aggregation queries

### 10. **flow_10_bulk_inventory_reduction** - Reduce Electronics Inventory
- **Claude Instruction**: "Reduce the quantity of all SELLER001 (TechGear Electronics) products by 10 units each"
- **Validates**: Bulk quantity updates

## API Endpoints

### Testing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/test/flows` | List all available test flows |
| GET | `/test/flows/{flow_id}` | Get details about a specific test flow |
| GET | `/test/validate/{flow_id}` | Validate a specific test flow execution |
| GET | `/test/validate/all` | Validate all test flows at once |
| POST | `/test/reset` | Reset database to original seed state |
| GET | `/test/state` | Get current database state summary |
| POST | `/test/backup` | Create a backup of current database |
| GET | `/test/help` | Get help information |

### Example API Responses

#### Successful Validation
```json
{
  "success": true,
  "flow_id": "flow_1_create_laptop",
  "message": "Item created successfully",
  "validation_results": {
    "title": {
      "expected": "Test Gaming Laptop",
      "actual": "Test Gaming Laptop",
      "passed": true
    },
    "price": {
      "expected": 999.99,
      "actual": 999.99,
      "passed": true
    }
  },
  "summary": {
    "status": "PASS",
    "flow_name": "Create New Laptop Listing"
  }
}
```

#### Failed Validation
```json
{
  "success": false,
  "flow_id": "flow_1_create_laptop",
  "message": "Item created but some fields don't match",
  "validation_results": {
    "title": {
      "expected": "Test Gaming Laptop",
      "actual": "Different Title",
      "passed": false
    },
    "price": {
      "expected": 999.99,
      "actual": 999.99,
      "passed": true
    }
  },
  "summary": {
    "status": "FAIL",
    "flow_name": "Create New Laptop Listing"
  }
}
```

## Testing Workflow

### Basic Workflow
1. **Reset Database**: Ensure clean state with seed data
2. **Choose Test Flow**: Pick from predefined scenarios
3. **Ask Claude**: Give Claude the exact instruction from the test flow
4. **Validate Result**: Check if Claude performed the action correctly
5. **Reset Again**: Prepare for next test

### Advanced Workflow
1. **Backup Current State**: Save current database state
2. **Run Multiple Tests**: Execute several test flows
3. **Validate All**: Check all results at once
4. **Analyze Results**: Review success/failure patterns

## MCP Server Integration

The testing system works seamlessly with the MCP server. Claude can use these MCP tools:

- `get_listing_item`: Get details about a specific listing
- `create_or_update_listing`: Create or update a listing
- `update_listing_partial`: Partially update a listing
- `delete_listing_item`: Delete (deactivate) a listing
- `search_listings`: Search for listings with filters

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure the FastAPI server is running
   - Check that `listings.db` exists

2. **Validation Failures**
   - Verify Claude used the exact instruction from the test flow
   - Check if the database was reset before the test
   - Review the validation results for specific field mismatches

3. **Reset Failures**
   - Ensure `combined_seed_data.py` is in the root directory
   - Check file permissions
   - Verify Python can execute the seed script

### Debug Commands

```bash
# Check current database state
curl http://localhost:8000/test/state

# Get detailed test flow information
curl http://localhost:8000/test/flows/flow_1_create_laptop

# Validate all flows to see overall system health
curl http://localhost:8000/test/validate/all
```

## Best Practices

1. **Always Reset Between Tests**: Ensures deterministic results
2. **Use Exact Instructions**: Copy the `claude_instruction` exactly
3. **Check Validation Details**: Review specific field mismatches
4. **Test Incrementally**: Start with simple CRUD operations
5. **Backup Before Complex Tests**: Save state before bulk operations

## Example Complete Test Session

```bash
# 1. Reset database
curl -X POST http://localhost:8000/test/reset

# 2. Get test flows
curl http://localhost:8000/test/flows

# 3. Ask Claude: "Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001'..."

# 4. Validate result
curl http://localhost:8000/test/validate/flow_1_create_laptop

# 5. Reset for next test
curl -X POST http://localhost:8000/test/reset
```

This testing system provides a simple, deterministic way to validate that Claude performs database operations correctly against your Amazon SP-API mock system.
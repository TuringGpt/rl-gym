# Quick Testing Reference Card

## 🚀 Start Server
```bash
uvicorn app.main:app --reload
```

## 📋 Essential API Endpoints

| Action | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| **List Test Flows** | GET | `/test/flows` | See all available test scenarios |
| **Validate Test** | GET | `/test/validate/{flow_id}` | Check if Claude did it right |
| **Reset Database** | POST | `/test/reset` | Clean slate for next test |
| **Get Help** | GET | `/test/help` | Full documentation |

## 🎯 10 Test Flows Ready to Use

### Basic CRUD
1. **flow_1_create_laptop** - Create new laptop listing
2. **flow_2_update_laptop_price** - Update price and quantity  
3. **flow_3_delete_cable** - Delete (deactivate) listing

### Search & Filter
4. **flow_4_search_bookwise** - Find BookWise listings
5. **flow_5_search_gaming** - Search for gaming products
6. **flow_6_price_range_search** - Find $20-$50 items

### Bulk Operations
7. **flow_7_deactivate_fitness** - Deactivate all fitness products
8. **flow_8_add_canada_kitchen** - Add Canada marketplace to kitchen items
9. **flow_9_most_expensive_per_seller** - Find priciest item per seller
10. **flow_10_bulk_inventory_reduction** - Reduce all electronics inventory

## 🔄 Testing Workflow

```
1. POST /test/reset          # Clean database
2. GET /test/flows           # Pick a test flow
3. Ask Claude to do action   # Use exact instruction from flow
4. GET /test/validate/{id}   # Check if correct (PASS/FAIL)
5. Repeat with next flow
```

## 📝 Example Test Session

```bash
# 1. Reset
curl -X POST http://localhost:8000/test/reset

# 2. See available tests
curl http://localhost:8000/test/flows

# 3. Ask Claude: "Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001', title 'Test Gaming Laptop', description 'High-performance gaming laptop for testing', price $999.99, quantity 50, status ACTIVE, and marketplace_ids ['ATVPDKIKX0DER']"

# 4. Validate
curl http://localhost:8000/test/validate/flow_1_create_laptop

# 5. Reset for next test
curl -X POST http://localhost:8000/test/reset
```

## ✅ Success Response
```json
{
  "success": true,
  "flow_id": "flow_1_create_laptop",
  "message": "Item created successfully",
  "summary": { "status": "PASS" }
}
```

## ❌ Failure Response
```json
{
  "success": false,
  "flow_id": "flow_1_create_laptop", 
  "message": "Item created but some fields don't match",
  "summary": { "status": "FAIL" }
}
```

## 🛠️ Debug Commands
```bash
# Check current database state
curl http://localhost:8000/test/state

# Validate all flows at once
curl http://localhost:8000/test/validate/all

# Backup current state
curl -X POST http://localhost:8000/test/backup
```

## 🎯 Pro Tips
- Always reset between tests for deterministic results
- Copy Claude instructions exactly from test flows
- Check validation details for specific field mismatches
- Use `/test/help` for complete documentation
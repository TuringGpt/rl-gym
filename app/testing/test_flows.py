"""
Predefined test flows for Amazon SP-API Mock testing
Each test flow includes instructions for Claude and expected results
"""

from typing import Dict, List, Any
from decimal import Decimal

# Test flow definitions with expected results
TEST_FLOWS = {
    "flow_1_create_laptop": {
        "id": "flow_1_create_laptop",
        "name": "Create New Laptop Listing",
        "description": "Create a new laptop listing for SELLER001",
        "claude_instruction": "Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001', title 'Test Gaming Laptop', description 'High-performance gaming laptop for testing', price $999.99, quantity 50, status ACTIVE, and marketplace_ids ['ATVPDKIKX0DER']",
        "expected_changes": {
            "action": "create",
            "seller_id": "SELLER001",
            "sku": "TEST-LAPTOP-001",
            "expected_data": {
                "title": "Test Gaming Laptop",
                "description": "High-performance gaming laptop for testing",
                "price": Decimal("999.99"),
                "quantity": 50,
                "status": "ACTIVE",
                "marketplace_ids": ["ATVPDKIKX0DER"],
            },
        },
    },
    "flow_2_update_laptop_price": {
        "id": "flow_2_update_laptop_price",
        "name": "Update Laptop Price and Quantity",
        "description": "Update existing laptop listing price and quantity",
        "claude_instruction": "Update SELLER001's LAPTOP-001 listing to change the price to $1199.99 and reduce quantity to 20",
        "expected_changes": {
            "action": "update",
            "seller_id": "SELLER001",
            "sku": "LAPTOP-001",
            "expected_data": {"price": Decimal("1199.99"), "quantity": 20},
        },
    },
    "flow_3_delete_cable": {
        "id": "flow_3_delete_cable",
        "name": "Delete Cable Listing",
        "description": "Delete (set to INACTIVE) a cable listing",
        "claude_instruction": "Delete SELLER003's CABLE-001 listing (set status to INACTIVE)",
        "expected_changes": {
            "action": "delete",
            "seller_id": "SELLER003",
            "sku": "CABLE-001",
            "expected_data": {"status": "INACTIVE"},
        },
    },
    "flow_4_search_bookwise": {
        "id": "flow_4_search_bookwise",
        "name": "Search BookWise Listings",
        "description": "Find all active listings from SELLER002 (BookWise Publishing)",
        "claude_instruction": "Search for all active listings from SELLER002 (BookWise Publishing)",
        "expected_changes": {
            "action": "search",
            "search_criteria": {"seller_id": "SELLER002", "status": "ACTIVE"},
            "expected_count_min": 8,  # BookWise has 8 active listings in seed data
            "expected_seller_name": "BookWise Publishing",
        },
    },
    "flow_5_search_gaming": {
        "id": "flow_5_search_gaming",
        "name": "Search Gaming Products",
        "description": "Search for products with 'gaming' in title or description",
        "claude_instruction": "Search for all products that have 'gaming' in the title or description",
        "expected_changes": {
            "action": "search",
            "search_criteria": {"title_search": "gaming"},
            "expected_count_min": 3,  # At least gaming laptop, mouse, keyboard, headset
            "expected_keywords": ["gaming", "Gaming"],
        },
    },
    "flow_6_price_range_search": {
        "id": "flow_6_price_range_search",
        "name": "Search Price Range $20-$50",
        "description": "Find listings priced between $20-$50",
        "claude_instruction": "Find all listings with prices between $20 and $50",
        "expected_changes": {
            "action": "search",
            "search_criteria": {"price_min": 20.00, "price_max": 50.00},
            "expected_count_min": 5,  # Several items in this range
            "price_validation": True,
        },
    },
    "flow_7_deactivate_fitness": {
        "id": "flow_7_deactivate_fitness",
        "name": "Deactivate Fitness Products",
        "description": "Set all SELLER005's fitness products to INACTIVE",
        "claude_instruction": "Set all listings from SELLER005 (FitLife Sports) to INACTIVE status",
        "expected_changes": {
            "action": "bulk_update",
            "seller_id": "SELLER005",
            "expected_data": {"status": "INACTIVE"},
            "expected_count": 5,  # SELLER005 has 5 products
        },
    },
    "flow_8_add_canada_kitchen": {
        "id": "flow_8_add_canada_kitchen",
        "name": "Add Canada Marketplace to Kitchen Products",
        "description": "Add Canada marketplace to all SELLER006 kitchen products",
        "claude_instruction": "Update all listings from SELLER006 (KitchenPro Essentials) to include the Canada marketplace (A2EUQ1WTGCTBG2) in their marketplace_ids",
        "expected_changes": {
            "action": "bulk_update",
            "seller_id": "SELLER006",
            "expected_data": {"marketplace_ids_contains": "A2EUQ1WTGCTBG2"},
            "expected_count": 5,  # SELLER006 has 5 products
        },
    },
    "flow_9_most_expensive_per_seller": {
        "id": "flow_9_most_expensive_per_seller",
        "name": "Find Most Expensive Product Per Seller",
        "description": "Find the highest priced product from each seller",
        "claude_instruction": "Find the most expensive (highest priced) product from each seller",
        "expected_changes": {
            "action": "analysis",
            "expected_results": {
                "SELLER001": {"max_price_sku": "LAPTOP-001", "price": Decimal("1299.99")},
                "SELLER002": {"max_price_sku": "TABLET-002", "price": Decimal("299.99")},
                "SELLER003": {"max_price_sku": "EARBUDS-001", "price": Decimal("79.99")},
                "SELLER004": {"max_price_sku": "MIRROR-001", "price": Decimal("89.99")},
                "SELLER005": {"max_price_sku": "WEIGHTS-001", "price": Decimal("199.99")},
                "SELLER006": {"max_price_sku": "BLENDER-001", "price": Decimal("149.99")},
                "SELLER007": {"max_price_sku": "WATCH-001", "price": Decimal("199.99")},
                "SELLER008": {"max_price_sku": "COVER-001", "price": Decimal("79.99")},
            },
        },
    },
    "flow_10_bulk_inventory_reduction": {
        "id": "flow_10_bulk_inventory_reduction",
        "name": "Reduce Electronics Inventory",
        "description": "Reduce all SELLER001 electronics quantities by 10",
        "claude_instruction": "Reduce the quantity of all SELLER001 (TechGear Electronics) products by 10 units each",
        "expected_changes": {
            "action": "bulk_update",
            "seller_id": "SELLER001",
            "quantity_reduction": 10,
            "expected_count": 12,  # SELLER001 has 12 products
        },
    },
}


def get_test_flow(flow_id: str) -> Dict[str, Any]:
    """Get a specific test flow by ID"""
    return TEST_FLOWS.get(flow_id)


def get_all_test_flows() -> Dict[str, Dict[str, Any]]:
    """Get all test flows"""
    return TEST_FLOWS


def get_test_flow_list() -> List[Dict[str, str]]:
    """Get a simplified list of test flows for display"""
    return [
        {
            "id": flow_id,
            "name": flow_data["name"],
            "description": flow_data["description"],
            "claude_instruction": flow_data["claude_instruction"],
        }
        for flow_id, flow_data in TEST_FLOWS.items()
    ]

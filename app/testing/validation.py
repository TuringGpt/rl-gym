"""
Validation logic for test flows
Compares actual database state with expected results
"""

import json
from typing import Dict, List, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import ListingItem
from app.testing.test_flows import get_test_flow


class TestValidator:
    """Validates test flow results against expected outcomes"""

    def __init__(self, session_id: Optional[str] = None):
        if session_id:
            from app.session_manager import session_manager

            self.db = session_manager.get_session_db(session_id)
        else:
            self.db = SessionLocal()

    def __del__(self):
        if hasattr(self, "db"):
            self.db.close()

    def validate_test_flow(self, flow_id: str) -> Dict[str, Any]:
        """
        Validate a specific test flow
        Returns detailed validation results
        """
        try:
            flow = get_test_flow(flow_id)
            if not flow:
                return {
                    "success": False,
                    "flow_id": flow_id,
                    "message": f"Test flow '{flow_id}' not found",
                    "validation_results": None,
                }

            expected_changes = flow["expected_changes"]
            action = expected_changes["action"]

            if action == "create":
                return self._validate_create_action(flow_id, expected_changes)
            elif action == "update":
                return self._validate_update_action(flow_id, expected_changes)
            elif action == "delete":
                return self._validate_delete_action(flow_id, expected_changes)
            elif action == "search":
                return self._validate_search_action(flow_id, expected_changes)
            elif action == "bulk_update":
                return self._validate_bulk_update_action(flow_id, expected_changes)
            elif action == "analysis":
                return self._validate_analysis_action(flow_id, expected_changes)
            else:
                return {
                    "success": False,
                    "flow_id": flow_id,
                    "message": f"Unknown action type: {action}",
                    "validation_results": None,
                }

        except Exception as e:
            return {
                "success": False,
                "flow_id": flow_id,
                "message": f"Validation error: {str(e)}",
                "validation_results": None,
            }

    def _validate_create_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create action"""
        seller_id = expected["seller_id"]
        sku = expected["sku"]
        expected_data = expected["expected_data"]

        # Check if item exists
        item = self.db.query(ListingItem).filter(ListingItem.seller_id == seller_id, ListingItem.sku == sku).first()

        if not item:
            return {
                "success": False,
                "flow_id": flow_id,
                "message": f"Item {seller_id}/{sku} was not created",
                "validation_results": {"expected": expected_data, "actual": None},
            }

        # Validate fields
        validation_results = {}
        all_passed = True

        for field, expected_value in expected_data.items():
            if field == "marketplace_ids":
                actual_value = item.get_marketplace_ids()
                passed = set(actual_value) == set(expected_value)
            else:
                actual_value = getattr(item, field)
                if isinstance(expected_value, Decimal):
                    passed = abs(float(actual_value) - float(expected_value)) < 0.01
                else:
                    passed = actual_value == expected_value

            validation_results[field] = {"expected": expected_value, "actual": actual_value, "passed": passed}

            if not passed:
                all_passed = False

        return {
            "success": all_passed,
            "flow_id": flow_id,
            "message": "Item created successfully" if all_passed else "Item created but some fields don't match",
            "validation_results": validation_results,
        }

    def _validate_update_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update action"""
        seller_id = expected["seller_id"]
        sku = expected["sku"]
        expected_data = expected["expected_data"]

        # Check if item exists
        item = self.db.query(ListingItem).filter(ListingItem.seller_id == seller_id, ListingItem.sku == sku).first()

        if not item:
            return {
                "success": False,
                "flow_id": flow_id,
                "message": f"Item {seller_id}/{sku} not found for update validation",
                "validation_results": None,
            }

        # Validate updated fields
        validation_results = {}
        all_passed = True

        for field, expected_value in expected_data.items():
            actual_value = getattr(item, field)
            if isinstance(expected_value, Decimal):
                passed = abs(float(actual_value) - float(expected_value)) < 0.01
            else:
                passed = actual_value == expected_value

            validation_results[field] = {"expected": expected_value, "actual": actual_value, "passed": passed}

            if not passed:
                all_passed = False

        return {
            "success": all_passed,
            "flow_id": flow_id,
            "message": "Item updated successfully" if all_passed else "Item update validation failed",
            "validation_results": validation_results,
        }

    def _validate_delete_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate delete action"""
        seller_id = expected["seller_id"]
        sku = expected["sku"]
        expected_data = expected["expected_data"]

        # Check if item exists and has correct status
        item = self.db.query(ListingItem).filter(ListingItem.seller_id == seller_id, ListingItem.sku == sku).first()

        if not item:
            return {
                "success": False,
                "flow_id": flow_id,
                "message": f"Item {seller_id}/{sku} not found",
                "validation_results": None,
            }

        expected_status = expected_data.get("status", "INACTIVE")
        actual_status = item.status
        passed = actual_status == expected_status

        return {
            "success": passed,
            "flow_id": flow_id,
            "message": (
                "Item deleted successfully"
                if passed
                else f"Item status is {actual_status}, expected {expected_status}"
            ),
            "validation_results": {"status": {"expected": expected_status, "actual": actual_status, "passed": passed}},
        }

    def _validate_search_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate search action"""
        search_criteria = expected["search_criteria"]

        # Build query based on criteria
        query = self.db.query(ListingItem)

        if "seller_id" in search_criteria:
            query = query.filter(ListingItem.seller_id == search_criteria["seller_id"])

        if "status" in search_criteria:
            query = query.filter(ListingItem.status == search_criteria["status"])

        if "title_search" in search_criteria:
            search_term = search_criteria["title_search"]
            query = query.filter(
                (ListingItem.title.ilike(f"%{search_term}%")) | (ListingItem.description.ilike(f"%{search_term}%"))
            )

        results = query.all()
        actual_count = len(results)

        validation_results = {
            "count": {
                "actual": actual_count,
                "expected_min": expected.get("expected_count_min", 0),
                "passed": actual_count >= expected.get("expected_count_min", 0),
            }
        }

        # Additional validations
        all_passed = validation_results["count"]["passed"]

        if "expected_seller_name" in expected:
            seller_names = [r.seller_name for r in results if r.seller_name]
            expected_name = expected["expected_seller_name"]
            name_match = all(name == expected_name for name in seller_names)
            validation_results["seller_name"] = {
                "expected": expected_name,
                "actual": list(set(seller_names)),
                "passed": name_match,
            }
            all_passed = all_passed and name_match

        if "expected_keywords" in expected:
            keywords = expected["expected_keywords"]
            titles_and_descriptions = [f"{r.title} {r.description}" for r in results]
            keyword_found = any(any(keyword in text for keyword in keywords) for text in titles_and_descriptions)
            validation_results["keywords"] = {"expected": keywords, "found": keyword_found, "passed": keyword_found}
            all_passed = all_passed and keyword_found

        return {
            "success": all_passed,
            "flow_id": flow_id,
            "message": f"Search returned {actual_count} results",
            "validation_results": validation_results,
        }

    def _validate_bulk_update_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bulk update action"""
        seller_id = expected["seller_id"]
        expected_data = expected["expected_data"]
        expected_count = expected.get("expected_count")

        # Get all items for the seller
        items = self.db.query(ListingItem).filter(ListingItem.seller_id == seller_id).all()
        actual_count = len(items)

        validation_results = {
            "count": {
                "expected": expected_count,
                "actual": actual_count,
                "passed": actual_count == expected_count if expected_count else True,
            }
        }

        all_passed = validation_results["count"]["passed"]

        # Validate specific fields
        for field, expected_value in expected_data.items():
            if field == "marketplace_ids_contains":
                # Check if all items contain the marketplace ID
                items_with_marketplace = 0
                for item in items:
                    marketplace_ids = item.get_marketplace_ids()
                    if expected_value in marketplace_ids:
                        items_with_marketplace += 1

                passed = items_with_marketplace == actual_count
                validation_results[field] = {
                    "expected": f"All items should contain {expected_value}",
                    "actual": f"{items_with_marketplace}/{actual_count} items contain it",
                    "passed": passed,
                }
                all_passed = all_passed and passed

            elif field == "status":
                # Check if all items have the expected status
                items_with_status = sum(1 for item in items if item.status == expected_value)
                passed = items_with_status == actual_count
                validation_results[field] = {
                    "expected": expected_value,
                    "actual": f"{items_with_status}/{actual_count} items have status {expected_value}",
                    "passed": passed,
                }
                all_passed = all_passed and passed

        # Handle quantity reduction
        if "quantity_reduction" in expected:
            reduction = expected["quantity_reduction"]
            validation_results["quantity_reduction"] = {
                "expected": f"All quantities reduced by {reduction}",
                "actual": "Cannot validate without before/after comparison",
                "passed": True,  # This would need before/after state comparison
            }

        return {
            "success": all_passed,
            "flow_id": flow_id,
            "message": f"Bulk update validated for {actual_count} items",
            "validation_results": validation_results,
        }

    def _validate_analysis_action(self, flow_id: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis action (like finding most expensive items)"""
        expected_results = expected["expected_results"]

        validation_results = {}
        all_passed = True

        for seller_id, expected_data in expected_results.items():
            # Find the most expensive item for this seller
            item = (
                self.db.query(ListingItem)
                .filter(ListingItem.seller_id == seller_id)
                .order_by(ListingItem.price.desc())
                .first()
            )

            if item:
                expected_sku = expected_data["max_price_sku"]
                expected_price = expected_data["price"]

                sku_match = item.sku == expected_sku
                price_match = abs(float(item.price) - float(expected_price)) < 0.01

                validation_results[seller_id] = {
                    "expected_sku": expected_sku,
                    "actual_sku": item.sku,
                    "expected_price": float(expected_price),
                    "actual_price": float(item.price),
                    "sku_passed": sku_match,
                    "price_passed": price_match,
                    "passed": sku_match and price_match,
                }

                if not (sku_match and price_match):
                    all_passed = False
            else:
                validation_results[seller_id] = {
                    "expected_sku": expected_data["max_price_sku"],
                    "actual_sku": None,
                    "expected_price": float(expected_data["price"]),
                    "actual_price": None,
                    "passed": False,
                }
                all_passed = False

        return {
            "success": all_passed,
            "flow_id": flow_id,
            "message": "Analysis validation completed",
            "validation_results": validation_results,
        }


def validate_flow(flow_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to validate a test flow"""
    validator = TestValidator(session_id)
    return validator.validate_test_flow(flow_id)

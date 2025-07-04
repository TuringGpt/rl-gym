"""
Testing API endpoints for validation and reset functionality
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from app.testing.reset import backup_current_state, get_database_state, reset_database
from app.testing.test_flows import get_all_test_flows, get_test_flow, get_test_flow_list
from app.testing.validation import validate_flow

test_router = APIRouter(prefix="/test", tags=["Testing"])


def get_db_for_session(x_session_id: str = Header(..., alias="X-Session-ID")):
    """Get database session for required session ID from header"""
    from app.session_manager import session_manager

    # Validate session exists
    if not session_manager.session_exists(x_session_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session ID: {x_session_id}. Please create a session first using POST /sessions",
        )

    db = session_manager.get_session_db(x_session_id)
    try:
        yield db
    finally:
        db.close()


@test_router.get("/flows", response_model=List[Dict[str, str]])
def list_test_flows():
    """
    Get all available test flows with their instructions
    Use this to see what test scenarios you can ask Claude to perform
    """
    return get_test_flow_list()


@test_router.get("/flows/{flow_id}")
def get_test_flow_details(flow_id: str):
    """
    Get detailed information about a specific test flow
    """
    flow = get_test_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail=f"Test flow '{flow_id}' not found")

    return {
        "flow": flow,
        "usage": {
            "step_1": "Ask Claude to perform the action described in 'claude_instruction'",
            "step_2": f"Call GET /test/validate/{flow_id} to check if the action was performed correctly",
            "step_3": "Call POST /test/reset to restore the database for the next test",
        },
    }


@test_router.get("/validate/{flow_id}")
def validate_test_flow(
    flow_id: str, db: Session = Depends(get_db_for_session), x_session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Validate that a test flow was executed correctly
    Returns PASS/FAIL with detailed comparison results
    Requires X-Session-ID header
    """
    try:
        result = validate_flow(flow_id, x_session_id)

        # Add summary information
        result["summary"] = {
            "status": "PASS" if result["success"] else "FAIL",
            "flow_name": get_test_flow(flow_id)["name"] if get_test_flow(flow_id) else "Unknown",
            "session_id": x_session_id,
            "timestamp": None,  # Could add timestamp if needed
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error for flow '{flow_id}': {str(e)}")


@test_router.post("/reset")
def reset_test_database(
    db: Session = Depends(get_db_for_session), x_session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Reset the database to its original seed state
    Use this between tests to ensure clean state
    Requires X-Session-ID header
    """
    try:
        # Reset specific session
        from session_manager import session_manager

        success = session_manager.reset_session(x_session_id)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to reset session {x_session_id}")

        return {
            "status": "success",
            "message": f"Session '{x_session_id}' reset to original seed state",
            "session_id": x_session_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")


@test_router.get("/state")
def get_current_database_state(
    db: Session = Depends(get_db_for_session), x_session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Get current database state summary
    Useful for debugging and understanding current data
    Requires X-Session-ID header
    """
    try:
        from models import ListingItem
        from sqlalchemy import func

        # Basic counts
        total_count = db.query(ListingItem).count()
        active_count = db.query(ListingItem).filter(ListingItem.status == "ACTIVE").count()
        inactive_count = db.query(ListingItem).filter(ListingItem.status == "INACTIVE").count()

        # Count by seller
        seller_counts = {}
        sellers = db.query(ListingItem.seller_id, ListingItem.seller_name).distinct().all()
        for seller_id, seller_name in sellers:
            count = db.query(ListingItem).filter(ListingItem.seller_id == seller_id).count()
            seller_counts[seller_id] = {"name": seller_name, "count": count}

        # Price statistics
        price_stats = db.query(
            func.min(ListingItem.price), func.max(ListingItem.price), func.avg(ListingItem.price)
        ).first()

        # Total inventory
        total_quantity = db.query(func.sum(ListingItem.quantity)).scalar() or 0

        return {
            "session_id": x_session_id,
            "total_listings": total_count,
            "active_listings": active_count,
            "inactive_listings": inactive_count,
            "seller_counts": seller_counts,
            "price_stats": {
                "min_price": float(price_stats[0]) if price_stats[0] else 0,
                "max_price": float(price_stats[1]) if price_stats[1] else 0,
                "avg_price": float(price_stats[2]) if price_stats[2] else 0,
            },
            "total_inventory": total_quantity,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database state: {str(e)}")


@test_router.post("/backup")
def backup_database():
    """
    Create a backup of the current database state
    """
    try:
        result = backup_current_state()

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        return {
            "status": "success",
            "message": result["message"],
            "backup_path": result["backup_path"],
            "timestamp": result["timestamp"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to backup database: {str(e)}")


@test_router.get("/validate/all")
def validate_all_flows(
    db: Session = Depends(get_db_for_session), x_session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Validate all test flows at once
    Useful for comprehensive testing
    Requires X-Session-ID header
    """
    try:
        all_flows = get_all_test_flows()
        results = {}

        for flow_id in all_flows.keys():
            try:
                results[flow_id] = validate_flow(flow_id, x_session_id)
            except Exception as e:
                results[flow_id] = {
                    "success": False,
                    "flow_id": flow_id,
                    "message": f"Validation error: {str(e)}",
                    "validation_results": None,
                }

        # Summary statistics
        total_flows = len(results)
        passed_flows = sum(1 for r in results.values() if r["success"])
        failed_flows = total_flows - passed_flows

        return {
            "summary": {
                "total_flows": total_flows,
                "passed": passed_flows,
                "failed": failed_flows,
                "success_rate": f"{(passed_flows/total_flows)*100:.1f}%" if total_flows > 0 else "0%",
                "session_id": x_session_id,
            },
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate all flows: {str(e)}")


@test_router.get("/help")
def get_testing_help():
    """
    Get help information about using the testing system
    """
    return {
        "testing_workflow": {
            "step_0": "Create a session: POST /sessions",
            "step_1": "Call GET /test/flows to see available test scenarios (requires X-Session-ID header)",
            "step_2": "Pick a test flow and ask Claude to perform the action described in 'claude_instruction'",
            "step_3": "Call GET /test/validate/{flow_id} to check if Claude performed the action correctly (requires X-Session-ID header)",
            "step_4": "Call POST /test/reset to restore the database for the next test (requires X-Session-ID header)",
            "step_5": "Repeat with different test flows using the same session",
        },
        "session_requirements": {
            "all_endpoints": "All testing endpoints (except /test/flows and /test/help) require X-Session-ID header",
            "session_creation": "Create session with POST /sessions first",
            "header_format": "X-Session-ID: {your_session_id}",
            "isolation": "Each session has completely isolated test data",
        },
        "available_endpoints": {
            "GET /test/flows": "List all available test flows (no session required)",
            "GET /test/flows/{flow_id}": "Get details about a specific test flow (no session required)",
            "GET /test/validate/{flow_id}": "Validate a specific test flow execution (requires X-Session-ID header)",
            "GET /test/validate/all": "Validate all test flows at once (requires X-Session-ID header)",
            "POST /test/reset": "Reset database to original seed state (requires X-Session-ID header)",
            "GET /test/state": "Get current database state summary (requires X-Session-ID header)",
            "POST /test/backup": "Create a backup of current database (no session required)",
            "GET /test/help": "This help information (no session required)",
        },
        "example_usage": {
            "description": "Example workflow for testing with sessions",
            "steps": [
                "0. POST /sessions - Create a session and get session_id",
                "1. GET /test/flows - See that 'flow_1_create_laptop' is available",
                "2. Ask Claude: 'Create a new laptop listing for SELLER001 with SKU TEST-LAPTOP-001, title Test Gaming Laptop, description High-performance gaming laptop for testing, price $999.99, quantity 50, status ACTIVE, and marketplace_ids [ATVPDKIKX0DER]'",
                "3. GET /test/validate/flow_1_create_laptop with X-Session-ID header - Check if Claude created the listing correctly",
                "4. POST /test/reset with X-Session-ID header - Reset database for next test",
                "5. Repeat steps 2-4 with different test flows using the same session",
            ],
        },
    }

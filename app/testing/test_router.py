"""
Testing API endpoints for validation and reset functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from app.database import get_db
from app.testing.test_flows import get_test_flow, get_all_test_flows, get_test_flow_list
from app.testing.validation import validate_flow
from app.testing.reset import reset_database, get_database_state, backup_current_state

test_router = APIRouter(prefix="/test", tags=["Testing"])


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
def validate_test_flow(flow_id: str):
    """
    Validate that a test flow was executed correctly
    Returns PASS/FAIL with detailed comparison results
    """
    try:
        result = validate_flow(flow_id)

        # Add summary information
        result["summary"] = {
            "status": "PASS" if result["success"] else "FAIL",
            "flow_name": get_test_flow(flow_id)["name"] if get_test_flow(flow_id) else "Unknown",
            "timestamp": None,  # Could add timestamp if needed
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error for flow '{flow_id}': {str(e)}")


@test_router.post("/reset")
def reset_test_database():
    """
    Reset the database to its original seed state
    Use this between tests to ensure clean state
    """
    try:
        result = reset_database()

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        return {"status": "success", "message": "Database reset to original seed state", "details": result["details"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")


@test_router.get("/state")
def get_current_database_state():
    """
    Get current database state summary
    Useful for debugging and understanding current data
    """
    try:
        result = get_database_state()

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        return result["state"]

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
def validate_all_flows():
    """
    Validate all test flows at once
    Useful for comprehensive testing
    """
    try:
        all_flows = get_all_test_flows()
        results = {}

        for flow_id in all_flows.keys():
            try:
                results[flow_id] = validate_flow(flow_id)
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
            "step_1": "Call GET /test/flows to see available test scenarios",
            "step_2": "Pick a test flow and ask Claude to perform the action described in 'claude_instruction'",
            "step_3": "Call GET /test/validate/{flow_id} to check if Claude performed the action correctly",
            "step_4": "Call POST /test/reset to restore the database for the next test",
            "step_5": "Repeat with different test flows",
        },
        "available_endpoints": {
            "GET /test/flows": "List all available test flows",
            "GET /test/flows/{flow_id}": "Get details about a specific test flow",
            "GET /test/validate/{flow_id}": "Validate a specific test flow execution",
            "GET /test/validate/all": "Validate all test flows at once",
            "POST /test/reset": "Reset database to original seed state",
            "GET /test/state": "Get current database state summary",
            "POST /test/backup": "Create a backup of current database",
            "GET /test/help": "This help information",
        },
        "example_usage": {
            "description": "Example workflow for testing",
            "steps": [
                "1. GET /test/flows - See that 'flow_1_create_laptop' is available",
                "2. Ask Claude: 'Create a new laptop listing for SELLER001 with SKU TEST-LAPTOP-001, title Test Gaming Laptop, description High-performance gaming laptop for testing, price $999.99, quantity 50, status ACTIVE, and marketplace_ids [ATVPDKIKX0DER]'",
                "3. GET /test/validate/flow_1_create_laptop - Check if Claude created the listing correctly",
                "4. POST /test/reset - Reset database for next test",
            ],
        },
    }

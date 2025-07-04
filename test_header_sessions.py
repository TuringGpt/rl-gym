#!/usr/bin/env python3
"""
Test script for header-based session system
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_session_creation_and_usage():
    """Test session creation and header-based usage"""

    print("🧪 Testing Header-Based Session System")
    print("=" * 50)

    print("\n1. Creating sessions...")

    # Create multiple sessions
    sessions = []
    for i in range(3):
        response = requests.post(f"{BASE_URL}/sessions")
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            sessions.append(session_id)
            print(f"   Session {i+1}: {session_id}")
        else:
            print(f"❌ Failed to create session {i+1}: {response.status_code}")
            return False

    print(f"✅ Created {len(sessions)} sessions successfully")

    print("\n2. Testing session isolation with headers...")

    # Create different items in each session
    for i, session_id in enumerate(sessions):
        item_data = {
            "title": f"Session {i+1} Test Item",
            "description": f"Item created in session {i+1}",
            "price": 100.00 + i,
            "quantity": 10 + i,
            "status": "ACTIVE",
            "marketplace_ids": ["ATVPDKIKX0DER"],
        }

        headers = {"X-Session-ID": session_id}
        response = requests.put(
            f"{BASE_URL}/listings/2021-08-01/items/SELLER001/SESSION{i+1}-ITEM", json=item_data, headers=headers
        )

        if response.status_code == 200:
            print(f"   ✅ Created item in session {i+1}")
        else:
            print(f"   ❌ Failed to create item in session {i+1}: {response.status_code}")
            return False

    print("\n3. Verifying session isolation...")

    # Search in each session - should only find items from that session
    for i, session_id in enumerate(sessions):
        headers = {"X-Session-ID": session_id}
        response = requests.get(
            f"{BASE_URL}/listings/2021-08-01/items", params={"seller_id": "SELLER001"}, headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])

            # Find our test item
            test_items = [item for item in items if item["sku"].startswith(f"SESSION{i+1}")]

            # Should find exactly 1 test item (the one we created) plus seed data
            if len(test_items) == 1:
                print(f"   ✅ Session {i+1}: Found correct test item")
            else:
                print(f"   ❌ Session {i+1}: Found {len(test_items)} test items (expected 1)")
                return False

            # Verify we don't see items from other sessions
            other_session_items = [
                item
                for item in items
                if item["sku"].startswith("SESSION") and not item["sku"].startswith(f"SESSION{i+1}")
            ]
            if len(other_session_items) == 0:
                print(f"   ✅ Session {i+1}: No cross-session contamination")
            else:
                print(f"   ❌ Session {i+1}: Found {len(other_session_items)} items from other sessions")
                return False
        else:
            print(f"   ❌ Failed to search in session {i+1}: {response.status_code}")
            return False

    print("\n4. Testing missing header error...")

    # Try to make request without header
    response = requests.get(f"{BASE_URL}/listings/2021-08-01/items/SELLER001/LAPTOP-001")

    if response.status_code == 422:  # FastAPI validation error
        print("   ✅ Request without X-Session-ID header properly rejected")
    else:
        print(f"   ❌ Request without header should fail, got: {response.status_code}")
        return False

    print("\n5. Testing invalid session ID...")

    # Try to use invalid session ID
    headers = {"X-Session-ID": "invalid_session_123"}
    response = requests.get(f"{BASE_URL}/listings/2021-08-01/items/SELLER001/LAPTOP-001", headers=headers)

    if response.status_code == 400:  # Bad request for invalid session
        print("   ✅ Invalid session ID properly rejected")
    else:
        print(f"   ❌ Invalid session ID should fail with 400, got: {response.status_code}")
        return False

    print("\n6. Testing header-based testing endpoints...")

    # Test that testing endpoints also require headers
    session_id = sessions[0]
    headers = {"X-Session-ID": session_id}

    # Test /test/state endpoint
    response = requests.get(f"{BASE_URL}/test/state", headers=headers)
    if response.status_code == 200:
        print("   ✅ /test/state with session header works")
    else:
        print(f"   ❌ /test/state with session header failed: {response.status_code}")
        return False

    # Test /test/state without header (should fail)
    response = requests.get(f"{BASE_URL}/test/state")
    if response.status_code == 422:
        print("   ✅ /test/state without session header properly rejected")
    else:
        print(f"   ❌ /test/state without header should fail, got: {response.status_code}")
        return False

    print("\n🎉 All header-based session tests passed!")
    return True


def test_mcp_workflow():
    """Test the MCP workflow with sessions"""

    print("\n📋 Testing MCP Workflow")
    print("=" * 30)

    print("MCP Tool Usage Pattern:")
    print("1. create_session() → get session_id")
    print("2. Use session_id in all subsequent MCP tool calls")
    print("3. Each agent gets its own session for complete isolation")

    print("\nExample MCP Usage:")
    print("```python")
    print("# Step 1: Create session")
    print("session_result = use_mcp_tool('amazon-sp-api-mock', 'create_session', {})")
    print("session_id = extract_session_id_from_result(session_result)")
    print("")
    print("# Step 2: Use session in all operations")
    print("use_mcp_tool('amazon-sp-api-mock', 'create_or_update_listing', {")
    print("    'session_id': session_id,")
    print("    'seller_id': 'SELLER001',")
    print("    'sku': 'TEST-001',")
    print("    'title': 'Test Product',")
    print("    'price': 99.99")
    print("})")
    print("")
    print("use_mcp_tool('amazon-sp-api-mock', 'search_listings', {")
    print("    'session_id': session_id,")
    print("    'seller_id': 'SELLER001'")
    print("})")
    print("```")

    print("\nTesting Endpoints (also require X-Session-ID header):")
    print("• GET /test/validate/{flow_id} - Validate test flow execution")
    print("• GET /test/validate/all - Validate all test flows")
    print("• POST /test/reset - Reset session database")
    print("• GET /test/state - Get session database state")
    print("• GET /test/flows and /test/help - No session required")

    print("\n✅ MCP workflow and testing endpoints documented")
    return True


if __name__ == "__main__":
    print("🚀 Starting Header-Based Session Tests")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()

    try:
        # Test server availability
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding. Please start the FastAPI server first.")
            exit(1)

        # Run tests
        session_success = test_session_creation_and_usage()
        mcp_success = test_mcp_workflow()

        if session_success and mcp_success:
            print("\n🎉 All tests passed! Header-based session system is working correctly.")
            print("\n📝 Summary:")
            print("• Sessions are created with auto-generated IDs")
            print("• X-Session-ID header is required for all database operations")
            print("• X-Session-ID header is required for most testing endpoints")
            print("• Complete data isolation between sessions")
            print("• Same session can be reused across multiple requests")
            print("• Perfect for multi-agent testing scenarios")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            exit(1)

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server first:")
        print("   cd app && python main.py")
        exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        exit(1)

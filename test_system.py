#!/usr/bin/env python3
"""
Simple test script to verify the testing system works
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())


def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")

        # Test basic app imports
        from app.database import engine, SessionLocal
        from app.models import ListingItem

        print("✓ Basic app imports successful")

        # Test testing module imports
        from app.testing.test_flows import get_test_flow_list
        from app.testing.validation import validate_flow
        from app.testing.reset import reset_database, get_database_state

        print("✓ Testing module imports successful")

        # Test router import
        from app.testing.test_router import test_router

        print("✓ Test router import successful")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nTesting basic functionality...")

        # Test getting test flows
        from app.testing.test_flows import get_test_flow_list

        flows = get_test_flow_list()
        print(f"✓ Found {len(flows)} test flows")

        # Test database state
        from app.testing.reset import get_database_state

        state = get_database_state()
        if state["success"]:
            print(f"✓ Database state check successful - {state['state']['total_listings']} listings")
        else:
            print(f"✗ Database state check failed: {state['message']}")
            return False

        return True

    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing System Verification")
    print("=" * 50)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False

    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed")
        return False

    print("\n✅ All tests passed! Testing system is ready.")
    print("\nNext steps:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Visit http://localhost:8000/test/help for testing guide")
    print("3. Use the test flows to validate Claude actions")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

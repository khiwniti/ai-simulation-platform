#!/usr/bin/env python3
"""
Simple test for execution API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_api_imports():
    """Test that API imports work"""
    try:
        from app.api.v1.execution import router
        print("✓ Execution API router imported successfully")
        return True
    except Exception as e:
        print(f"✗ API import error: {e}")
        return False

def test_service_integration():
    """Test service integration with API"""
    try:
        from app.services.execution_service import execution_service
        from app.api.v1.execution import router
        print("✓ Service integration successful")
        return True
    except Exception as e:
        print(f"✗ Service integration error: {e}")
        return False

def main():
    """Run API tests"""
    print("Testing Execution API...")
    print("=" * 30)
    
    tests = [
        test_api_imports,
        test_service_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 30)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 API tests passed!")
        return 0
    else:
        print("❌ Some API tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
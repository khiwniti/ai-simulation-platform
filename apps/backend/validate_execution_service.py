#!/usr/bin/env python3
"""
Simple validation script for the execution service
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from app.services.execution_service import (
            ExecutionService,
            ExecutionRequest,
            ExecutionOutput,
            ExecutionStatus
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_model_creation():
    """Test that models can be created"""
    try:
        from app.services.execution_service import ExecutionRequest, ExecutionOutput, ExecutionStatus
        from datetime import datetime
        
        # Test ExecutionRequest
        request = ExecutionRequest(
            code="print('test')",
            cell_id="cell-123",
            notebook_id="notebook-456",
            execution_count=1
        )
        print(f"✓ ExecutionRequest created: {request.code}")
        
        # Test ExecutionOutput
        output = ExecutionOutput(
            output_type="stdout",
            content={"text": "Hello"},
            timestamp=datetime.utcnow()
        )
        print(f"✓ ExecutionOutput created: {output.output_type}")
        
        # Test ExecutionStatus
        status = ExecutionStatus(
            execution_id="test-123",
            status="queued"
        )
        print(f"✓ ExecutionStatus created: {status.status}")
        
        return True
    except Exception as e:
        print(f"✗ Model creation error: {e}")
        return False

def test_service_creation():
    """Test that service can be created"""
    try:
        from app.services.execution_service import ExecutionService
        
        service = ExecutionService()
        print("✓ ExecutionService created successfully")
        return True
    except Exception as e:
        print(f"✗ Service creation error: {e}")
        return False

def test_script_generation():
    """Test script generation functionality"""
    try:
        from app.services.execution_service import ExecutionService
        
        service = ExecutionService()
        script = service._create_execution_script("print('Hello, World!')")
        
        assert "print('Hello, World!')" in script
        assert "capture_output()" in script
        assert "json.dumps" in script
        
        print("✓ Script generation works correctly")
        return True
    except Exception as e:
        print(f"✗ Script generation error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Validating Execution Service Implementation...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_model_creation,
        test_service_creation,
        test_script_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Execution service is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
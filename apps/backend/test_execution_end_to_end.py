#!/usr/bin/env python3
"""
End-to-end test for execution service functionality
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.execution_service import ExecutionService, ExecutionRequest
from unittest.mock import AsyncMock

async def test_execution_workflow():
    """Test the complete execution workflow"""
    print("Testing execution workflow...")
    
    # Create service with mocked Redis
    service = ExecutionService()
    service.redis_client = AsyncMock()
    
    # Mock Redis operations
    service.redis_client.hset = AsyncMock()
    service.redis_client.lpush = AsyncMock()
    service.redis_client.hgetall = AsyncMock(return_value={
        "status": "completed",
        "started_at": "2024-01-01T00:00:00",
        "completed_at": "2024-01-01T00:01:00"
    })
    service.redis_client.lrange = AsyncMock(return_value=[])
    service.redis_client.llen = AsyncMock(return_value=0)
    
    # Test execution request
    request = ExecutionRequest(
        code="print('Hello, World!')",
        cell_id="test-cell",
        notebook_id="test-notebook",
        execution_count=1
    )
    
    try:
        # Test code execution
        execution_id = await service.execute_code(request)
        print(f"✓ Code execution queued with ID: {execution_id}")
        
        # Test status retrieval
        status = await service.get_execution_status(execution_id)
        print(f"✓ Status retrieved: {status.status}")
        
        # Test queue status
        queue_status = await service.get_queue_status()
        print(f"✓ Queue status: {queue_status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Execution workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_script_generation():
    """Test script generation with various code types"""
    print("Testing script generation...")
    
    service = ExecutionService()
    
    test_cases = [
        ("print('Hello')", "Simple print"),
        ("x = 1 + 1\nprint(x)", "Variable assignment"),
        ("import math\nprint(math.pi)", "Import statement"),
        ("for i in range(3):\n    print(i)", "Loop"),
        ("raise ValueError('test')", "Error case")
    ]
    
    try:
        for code, description in test_cases:
            script = service._create_execution_script(code)
            assert code in script
            assert "capture_output()" in script
            assert "json.dumps" in script
            print(f"✓ {description}: Script generated correctly")
            
        return True
        
    except Exception as e:
        print(f"✗ Script generation error: {e}")
        return False

async def main():
    """Run all end-to-end tests"""
    print("Running End-to-End Execution Tests...")
    print("=" * 40)
    
    tests = [
        test_execution_workflow,
        test_script_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All end-to-end tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
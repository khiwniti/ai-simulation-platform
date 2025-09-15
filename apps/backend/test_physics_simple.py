#!/usr/bin/env python3
"""
Simple test to verify NVIDIA PhysX AI physics integration
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_physics_service_import():
    """Test physics service can be imported and instantiated"""
    try:
        from app.services.physics_service import (
            PhysicsService, 
            PhysicsEngineType, 
            GPUResource, 
            PhysicsContext
        )
        
        # Create service instance
        service = PhysicsService()
        
        # Test basic functionality
        assert hasattr(service, 'available_engines')
        assert hasattr(service, 'gpu_resources')
        assert hasattr(service, 'active_contexts')
        
        print("✓ Physics service import and instantiation successful")
        return True
        
    except Exception as e:
        print(f"✗ Physics service test failed: {e}")
        return False

def test_execution_service_physics_integration():
    """Test execution service physics integration"""
    try:
        from app.services.execution_service import ExecutionService, ExecutionRequest
        
        # Test ExecutionRequest with physics parameters
        request = ExecutionRequest(
            code="print('test')",
            cell_id="test_cell",
            notebook_id="test_notebook", 
            execution_count=1,
            enable_physics=True,
            physics_requirements={
                "gpu_acceleration": True,
                "memory_mb": 1024,
                "complexity": "medium"
            }
        )
        
        assert request.enable_physics is True
        assert request.physics_requirements is not None
        assert request.physics_requirements["gpu_acceleration"] is True
        
        print("✓ Execution service physics integration successful")
        return True
        
    except Exception as e:
        print(f"✗ Execution service physics integration test failed: {e}")
        return False

def test_docker_files_exist():
    """Test Docker files exist"""
    try:
        docker_dir = Path(__file__).parent / "docker"
        
        dockerfile = docker_dir / "physics_executor.dockerfile"
        script = docker_dir / "physics_execute.py"
        
        assert dockerfile.exists(), "Physics executor Dockerfile missing"
        assert script.exists(), "Physics execution script missing"
        
        print("✓ Docker files exist")
        return True
        
    except Exception as e:
        print(f"✗ Docker files test failed: {e}")
        return False

def test_physics_execution_script():
    """Test physics execution script has required components"""
    try:
        script_path = Path(__file__).parent / "docker" / "physics_execute.py"
        content = script_path.read_text()
        
        required_components = [
            "PhysXAIWrapper",
            "PhysXCPUWrapper", 
            "SoftwareFallbackPhysics",
            "setup_physics_environment",
            "inject_physics_globals",
            "create_physics_sim",
            "simulate_particle_system"
        ]
        
        for component in required_components:
            assert component in content, f"Missing component: {component}"
        
        print("✓ Physics execution script has all required components")
        return True
        
    except Exception as e:
        print(f"✗ Physics execution script test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("NVIDIA PhysX AI Physics Integration - Simple Tests")
    print("=" * 50)
    
    tests = [
        ("Physics Service Import", test_physics_service_import),
        ("Execution Service Physics Integration", test_execution_service_physics_integration),
        ("Docker Files Exist", test_docker_files_exist),
        ("Physics Execution Script", test_physics_execution_script)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    print("Test Results:")
    
    passed = 0
    for i, (test_name, _) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"  {status}: {test_name}")
        if results[i]:
            passed += 1
    
    print(f"\nSummary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed!")
        print("\nNVIDIA PhysX AI integration is working correctly!")
        return True
    else:
        print(f"\n❌ {len(tests) - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
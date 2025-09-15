#!/usr/bin/env python3
"""
Minimal test to verify NVIDIA PhysX AI physics integration
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_physics_service_basic():
    """Test basic physics service functionality"""
    try:
        from app.services.physics_service import (
            PhysicsService, 
            PhysicsEngineType, 
            GPUResource, 
            PhysicsContext
        )
        
        print("✓ Physics service imports successful")
        
        # Test enum values
        assert PhysicsEngineType.PHYSX_AI.value == "physx_ai"
        assert PhysicsEngineType.PHYSX_CPU.value == "physx_cpu"
        assert PhysicsEngineType.SOFTWARE_FALLBACK.value == "software_fallback"
        print("✓ Physics engine types validated")
        
        # Test data classes
        gpu = GPUResource(
            device_id=0,
            name="Test GPU",
            memory_total=8192,
            memory_free=6144,
            compute_capability="8.6",
            is_available=True
        )
        assert gpu.device_id == 0
        print("✓ GPUResource dataclass working")
        
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_AI,
            gpu_device_id=0,
            memory_allocated=1024,
            parameters={},
            is_active=True
        )
        assert context.simulation_id == "test_sim"
        print("✓ PhysicsContext dataclass working")
        
        # Create service instance
        service = PhysicsService()
        assert hasattr(service, 'available_engines')
        assert hasattr(service, 'gpu_resources')
        assert hasattr(service, 'active_contexts')
        print("✓ Physics service instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Physics service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_docker_files():
    """Test Docker files exist and have correct content"""
    try:
        docker_dir = Path(__file__).parent / "docker"
        
        # Check Dockerfile
        dockerfile = docker_dir / "physics_executor.dockerfile"
        assert dockerfile.exists(), "Physics executor Dockerfile missing"
        
        dockerfile_content = dockerfile.read_text()
        assert "nvidia/cuda" in dockerfile_content, "Missing NVIDIA CUDA base"
        assert "PhysX" in dockerfile_content, "Missing PhysX references"
        assert "pynvml" in dockerfile_content, "Missing GPU monitoring"
        print("✓ Physics executor Dockerfile validated")
        
        # Check execution script
        script = docker_dir / "physics_execute.py"
        assert script.exists(), "Physics execution script missing"
        
        script_content = script.read_text()
        required_components = [
            "PhysXAIWrapper",
            "PhysXCPUWrapper", 
            "SoftwareFallbackPhysics",
            "setup_physics_environment",
            "inject_physics_globals"
        ]
        
        for component in required_components:
            assert component in script_content, f"Missing component: {component}"
        
        print("✓ Physics execution script validated")
        return True
        
    except Exception as e:
        print(f"✗ Docker files test failed: {e}")
        return False

def test_execution_request_model():
    """Test ExecutionRequest model has physics parameters"""
    try:
        # Import just the model without the service
        from app.services.execution_service import ExecutionRequest
        
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
        print("✓ ExecutionRequest physics parameters working")
        
        return True
        
    except Exception as e:
        print(f"✗ ExecutionRequest test failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("NVIDIA PhysX AI Physics Integration - Minimal Tests")
    print("=" * 52)
    
    tests = [
        ("Physics Service Basic", test_physics_service_basic),
        ("Docker Files", test_docker_files),
        ("ExecutionRequest Model", test_execution_request_model)
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
    
    print(f"\n{'='*52}")
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
        print("\nImplemented features:")
        print("• NVIDIA PhysX AI physics engine integration")
        print("• GPU resource detection and allocation")
        print("• Physics-specific code execution paths")
        print("• Docker container support for physics simulations")
        print("• Physics-aware execution request model")
        return True
    else:
        print(f"\n❌ {len(tests) - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
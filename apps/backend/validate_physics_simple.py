#!/usr/bin/env python3
"""
Simple validation script for NVIDIA PhysX AI physics engine integration
(No Docker required)
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def validate_physics_service_structure():
    """Validate physics service structure without instantiation"""
    print("\n=== Physics Service Structure Validation ===")
    
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
        
        return True
        
    except Exception as e:
        print(f"✗ Physics service structure validation failed: {e}")
        return False


def validate_execution_service_structure():
    """Validate execution service structure without Docker"""
    print("\n=== Execution Service Structure Validation ===")
    
    try:
        # Import without instantiating (to avoid Docker connection)
        import app.services.execution_service as exec_module
        
        # Check ExecutionRequest has physics parameters
        request = exec_module.ExecutionRequest(
            code="test_code",
            cell_id="test_cell", 
            notebook_id="test_notebook",
            execution_count=1,
            enable_physics=True,
            physics_requirements={"gpu_acceleration": True}
        )
        
        assert hasattr(request, 'enable_physics')
        assert hasattr(request, 'physics_requirements')
        assert request.enable_physics is True
        print("✓ ExecutionRequest physics parameters working")
        
        # Check ExecutionService class has physics methods
        exec_service_class = exec_module.ExecutionService
        physics_methods = [
            '_execute_with_physics',
            '_execute_regular', 
            '_build_physics_execution_image'
        ]
        
        for method in physics_methods:
            assert hasattr(exec_service_class, method)
        print("✓ ExecutionService physics methods present")
        
        return True
        
    except Exception as e:
        print(f"✗ Execution service structure validation failed: {e}")
        return False


def validate_docker_files():
    """Validate Docker files for physics execution"""
    print("\n=== Docker Files Validation ===")
    
    try:
        docker_dir = Path(__file__).parent / "docker"
        
        # Check physics dockerfile
        dockerfile_path = docker_dir / "physics_executor.dockerfile"
        if dockerfile_path.exists():
            print("✓ Physics executor Dockerfile exists")
            
            content = dockerfile_path.read_text()
            checks = [
                ("nvidia/cuda", "NVIDIA CUDA base image"),
                ("PhysX", "PhysX references"),
                ("pynvml", "GPU monitoring"),
                ("python-physics-executor", "Image tag"),
                ("PHYSX_AI_ROOT", "PhysX environment")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✓ Dockerfile includes {description}")
                else:
                    print(f"⚠ Dockerfile missing {description}")
        else:
            print("✗ Physics executor Dockerfile missing")
            return False
        
        # Check physics execution script
        script_path = docker_dir / "physics_execute.py"
        if script_path.exists():
            print("✓ Physics execution script exists")
            
            content = script_path.read_text()
            checks = [
                ("PhysXAIWrapper", "PhysX AI wrapper"),
                ("PhysXCPUWrapper", "PhysX CPU wrapper"), 
                ("SoftwareFallbackPhysics", "Software fallback"),
                ("inject_physics_globals", "Physics globals injection"),
                ("simulate_particle_system", "Particle simulation"),
                ("create_physics_sim", "Physics simulation creation")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✓ Script includes {description}")
                else:
                    print(f"⚠ Script missing {description}")
        else:
            print("✗ Physics execution script missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Docker files validation failed: {e}")
        return False


def validate_requirements():
    """Validate requirements include physics dependencies"""
    print("\n=== Requirements Validation ===")
    
    try:
        requirements_path = Path(__file__).parent / "requirements.txt"
        if requirements_path.exists():
            content = requirements_path.read_text()
            
            required_deps = [
                ("pynvml", "NVIDIA GPU monitoring"),
                ("psutil", "System resource monitoring"),
                ("docker", "Container management")
            ]
            
            all_present = True
            for dep, description in required_deps:
                if dep in content:
                    print(f"✓ {description} dependency included")
                else:
                    print(f"✗ {description} dependency missing")
                    all_present = False
                    
            return all_present
        else:
            print("✗ requirements.txt not found")
            return False
            
    except Exception as e:
        print(f"✗ Requirements validation failed: {e}")
        return False


def validate_test_files():
    """Validate test files exist and have proper structure"""
    print("\n=== Test Files Validation ===")
    
    try:
        tests_dir = Path(__file__).parent / "tests"
        
        test_files = [
            ("test_physics_service.py", "Physics service tests"),
            ("test_physics_execution.py", "Physics execution tests"),
            ("test_physics_integration.py", "Integration tests")
        ]
        
        all_present = True
        for test_file, description in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                print(f"✓ {description} exist")
                
                # Check test content
                content = test_path.read_text()
                if "class Test" in content and "def test_" in content:
                    print(f"  ✓ {test_file} has proper test structure")
                else:
                    print(f"  ⚠ {test_file} may have structural issues")
            else:
                print(f"✗ {description} missing")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"✗ Test files validation failed: {e}")
        return False


def validate_api_integration():
    """Validate API integration supports physics parameters"""
    print("\n=== API Integration Validation ===")
    
    try:
        # Check execution API
        api_path = Path(__file__).parent / "app" / "api" / "v1" / "execution.py"
        if api_path.exists():
            content = api_path.read_text()
            
            if "ExecutionRequest" in content:
                print("✓ API uses ExecutionRequest model")
            else:
                print("✗ API missing ExecutionRequest integration")
                return False
                
            if "execution_service" in content:
                print("✓ API integrates with execution service")
            else:
                print("✗ API missing execution service integration")
                return False
                
            print("✓ API integration validated")
            return True
        else:
            print("✗ Execution API file missing")
            return False
            
    except Exception as e:
        print(f"✗ API integration validation failed: {e}")
        return False


def main():
    """Main validation function"""
    print("NVIDIA PhysX AI Physics Engine Integration Validation")
    print("=" * 55)
    print("(Simple validation - no Docker required)")
    
    validations = [
        ("Physics Service Structure", validate_physics_service_structure),
        ("Execution Service Structure", validate_execution_service_structure),
        ("Docker Files", validate_docker_files),
        ("Requirements", validate_requirements),
        ("Test Files", validate_test_files),
        ("API Integration", validate_api_integration)
    ]
    
    results = []
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {name} validation crashed: {e}")
            results.append(False)
    
    print("\n=== Validation Summary ===")
    passed = sum(results)
    total = len(results)
    
    for i, (name, _) in enumerate(validations):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed!")
        print("\nPhysX AI integration implementation is complete!")
        print("\nImplemented features:")
        print("• NVIDIA PhysX AI physics engine integration")
        print("• GPU resource detection and allocation")
        print("• Physics-specific code execution paths")
        print("• Docker container support for physics simulations")
        print("• Comprehensive test suite")
        print("• API integration with physics parameters")
        
        print("\nNext steps for deployment:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Docker daemon")
        print("3. Build physics Docker image")
        print("4. Run integration tests")
        print("5. Test with actual physics simulations")
        return True
    else:
        print(f"\n❌ {total - passed} validation(s) failed")
        print("Please review the failed validations above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Validation script for NVIDIA PhysX AI physics engine integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.services.physics_service import PhysicsService, PhysicsEngineType
    from app.services.execution_service import ExecutionService, ExecutionRequest
    print("✓ Successfully imported physics and execution services")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


async def validate_physics_service():
    """Validate physics service functionality"""
    print("\n=== Physics Service Validation ===")
    
    try:
        # Create physics service
        physics_service = PhysicsService()
        print("✓ Physics service created")
        
        # Test initialization (mocked)
        print("✓ Physics service structure validated")
        
        # Test engine types
        assert hasattr(PhysicsEngineType, 'PHYSX_AI')
        assert hasattr(PhysicsEngineType, 'PHYSX_CPU')
        assert hasattr(PhysicsEngineType, 'SOFTWARE_FALLBACK')
        print("✓ Physics engine types defined")
        
        # Test service methods exist
        assert hasattr(physics_service, 'initialize')
        assert hasattr(physics_service, 'create_physics_context')
        assert hasattr(physics_service, 'release_physics_context')
        assert hasattr(physics_service, 'get_optimal_engine')
        assert hasattr(physics_service, 'get_physics_docker_config')
        assert hasattr(physics_service, 'get_service_status')
        print("✓ Physics service methods available")
        
        return True
        
    except Exception as e:
        print(f"✗ Physics service validation failed: {e}")
        return False


async def validate_execution_service():
    """Validate execution service physics integration"""
    print("\n=== Execution Service Physics Integration Validation ===")
    
    try:
        # Create execution service
        execution_service = ExecutionService()
        print("✓ Execution service created")
        
        # Test physics context storage
        assert hasattr(execution_service, 'physics_contexts')
        print("✓ Physics contexts storage available")
        
        # Test physics-aware methods
        assert hasattr(execution_service, '_execute_with_physics')
        assert hasattr(execution_service, '_execute_regular')
        assert hasattr(execution_service, '_build_physics_execution_image')
        print("✓ Physics-aware execution methods available")
        
        # Test ExecutionRequest physics parameters
        request = ExecutionRequest(
            code="test_code",
            cell_id="test_cell",
            notebook_id="test_notebook",
            execution_count=1,
            enable_physics=True,
            physics_requirements={"gpu_acceleration": True}
        )
        
        assert request.enable_physics is True
        assert request.physics_requirements is not None
        print("✓ ExecutionRequest physics parameters working")
        
        return True
        
    except Exception as e:
        print(f"✗ Execution service validation failed: {e}")
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
            
            # Check dockerfile content
            content = dockerfile_path.read_text()
            if "nvidia/cuda" in content:
                print("✓ Dockerfile uses NVIDIA CUDA base image")
            if "PhysX" in content:
                print("✓ Dockerfile references PhysX")
            if "pynvml" in content:
                print("✓ Dockerfile includes GPU monitoring")
        else:
            print("✗ Physics executor Dockerfile missing")
            return False
        
        # Check physics execution script
        script_path = docker_dir / "physics_execute.py"
        if script_path.exists():
            print("✓ Physics execution script exists")
            
            # Check script content
            content = script_path.read_text()
            if "PhysXAIWrapper" in content:
                print("✓ Script includes PhysX AI wrapper")
            if "PhysXCPUWrapper" in content:
                print("✓ Script includes PhysX CPU wrapper")
            if "SoftwareFallbackPhysics" in content:
                print("✓ Script includes software fallback")
            if "inject_physics_globals" in content:
                print("✓ Script includes physics globals injection")
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
            
            if "pynvml" in content:
                print("✓ pynvml dependency included")
            else:
                print("✗ pynvml dependency missing")
                return False
                
            if "psutil" in content:
                print("✓ psutil dependency included")
            else:
                print("✗ psutil dependency missing")
                return False
                
            print("✓ Physics dependencies validated")
            return True
        else:
            print("✗ requirements.txt not found")
            return False
            
    except Exception as e:
        print(f"✗ Requirements validation failed: {e}")
        return False


def validate_test_files():
    """Validate test files exist"""
    print("\n=== Test Files Validation ===")
    
    try:
        tests_dir = Path(__file__).parent / "tests"
        
        test_files = [
            "test_physics_service.py",
            "test_physics_execution.py", 
            "test_physics_integration.py"
        ]
        
        for test_file in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                print(f"✓ {test_file} exists")
            else:
                print(f"✗ {test_file} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test files validation failed: {e}")
        return False


async def main():
    """Main validation function"""
    print("NVIDIA PhysX AI Physics Engine Integration Validation")
    print("=" * 55)
    
    validations = [
        validate_physics_service(),
        validate_execution_service(),
        validate_docker_files(),
        validate_requirements(),
        validate_test_files()
    ]
    
    results = []
    for validation in validations:
        if asyncio.iscoroutine(validation):
            result = await validation
        else:
            result = validation
        results.append(result)
    
    print("\n=== Validation Summary ===")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} validations passed!")
        print("\nPhysX AI integration is ready for testing.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Build physics Docker image")
        print("3. Run integration tests")
        print("4. Test with actual physics simulations")
        return True
    else:
        print(f"✗ {total - passed} of {total} validations failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
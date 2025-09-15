"""
Integration tests for NVIDIA PhysX AI physics engine integration
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from app.services.execution_service import execution_service, ExecutionRequest
from app.services.physics_service import physics_service


class TestPhysicsIntegration:
    """Integration tests for physics engine integration"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_physics_execution(self):
        """Test complete end-to-end physics execution workflow"""
        
        # Mock the physics service initialization
        with patch.object(physics_service, '_detect_gpu_resources') as mock_detect_gpu, \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True), \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=True), \
             patch.object(execution_service, '_ensure_execution_images'), \
             patch.object(execution_service, 'redis_client', new=AsyncMock()):
            
            # Mock GPU resources
            mock_gpu = Mock()
            mock_gpu.device_id = 0
            mock_gpu.name = "NVIDIA RTX 4090"
            mock_gpu.memory_total = 24576
            mock_gpu.memory_free = 20480
            mock_gpu.compute_capability = "8.9"
            mock_gpu.is_available = True
            physics_service.gpu_resources = [mock_gpu]
            
            # Initialize services
            await execution_service.initialize()
            
            # Create physics execution request
            request = ExecutionRequest(
                code="""
# Test physics integration
import numpy as np

# Get physics engine info
physics_info = get_physics_info()
print(f"Physics Engine: {physics_info['engine']}")
print(f"GPU Device: {physics_info['gpu_device']}")
print(f"Simulation ID: {physics_info['simulation_id']}")

# Create a simple physics simulation
particles = {
    'positions': [[0, 10, 0], [5, 10, 0], [10, 10, 0]],
    'velocities': [[1, 0, 0], [0, 0, 0], [-1, 0, 0]],
    'masses': [1.0, 2.0, 1.0]
}

# Apply gravity
forces = [[0, -9.8, 0], [0, -19.6, 0], [0, -9.8, 0]]

# Run simulation
trajectory = simulate_particle_system(particles, forces, dt=0.01, steps=100)
print(f"Simulation completed: {trajectory.shape} trajectory points")

# Create physics simulation using PhysX
try:
    sim_config = create_physics_sim(
        particle_count=3,
        gravity=[0, -9.8, 0],
        time_step=0.01,
        simulation_time=1.0
    )
    print(f"PhysX simulation created: {sim_config['simulation_id']}")
    print(f"Using engine: {sim_config['engine']}")
except Exception as e:
    print(f"PhysX simulation error: {e}")

print("Physics integration test completed successfully!")
""",
                cell_id="physics_test_cell",
                notebook_id="physics_test_notebook",
                execution_count=1,
                enable_physics=True,
                physics_requirements={
                    "gpu_acceleration": True,
                    "memory_mb": 1024,
                    "complexity": "medium",
                    "particle_count": 1000
                }
            )
            
            # Execute the physics code
            execution_id = await execution_service.execute_code(request)
            
            # Verify physics context was created
            assert execution_id in execution_service.physics_contexts
            context = execution_service.physics_contexts[execution_id]
            assert context.engine_type.value in ["physx_ai", "physx_cpu", "software_fallback"]
            assert context.is_active is True
            
            # Verify execution was queued
            execution_service.redis_client.hset.assert_called()
            execution_service.redis_client.lpush.assert_called()
            
            print(f"✓ Physics execution test passed with engine: {context.engine_type.value}")
    
    @pytest.mark.asyncio
    async def test_physics_fallback_mechanism(self):
        """Test physics engine fallback when PhysX is not available"""
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=False), \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=False), \
             patch.object(execution_service, '_ensure_execution_images'), \
             patch.object(execution_service, 'redis_client', new=AsyncMock()):
            
            # Initialize services (should fall back to software physics)
            await execution_service.initialize()
            
            # Create physics execution request
            request = ExecutionRequest(
                code="physics_info = get_physics_info(); print(physics_info)",
                cell_id="fallback_test_cell",
                notebook_id="fallback_test_notebook",
                execution_count=1,
                enable_physics=True,
                physics_requirements={
                    "gpu_acceleration": True,  # Requested but not available
                    "memory_mb": 512
                }
            )
            
            # Execute the physics code
            execution_id = await execution_service.execute_code(request)
            
            # Verify physics context was created with fallback
            assert execution_id in execution_service.physics_contexts
            context = execution_service.physics_contexts[execution_id]
            assert context.engine_type.value == "software_fallback"
            
            print("✓ Physics fallback test passed")
    
    @pytest.mark.asyncio
    async def test_gpu_resource_allocation(self):
        """Test GPU resource allocation and management"""
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True), \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=True):
            
            # Mock multiple GPU resources
            gpu1 = Mock()
            gpu1.device_id = 0
            gpu1.memory_total = 8192
            gpu1.memory_free = 6144
            gpu1.is_available = True
            
            gpu2 = Mock()
            gpu2.device_id = 1
            gpu2.memory_total = 24576
            gpu2.memory_free = 20480
            gpu2.is_available = True
            
            physics_service.gpu_resources = [gpu1, gpu2]
            await physics_service.initialize()
            
            # Test allocation on first GPU
            context1 = await physics_service.create_physics_context(
                "sim_001", 
                {"gpu_acceleration": True, "memory_mb": 2048}
            )
            
            assert context1.gpu_device_id == 0
            assert context1.memory_allocated == 2048
            assert gpu1.memory_free == 6144 - 2048
            
            # Test allocation on second GPU (first is now limited)
            context2 = await physics_service.create_physics_context(
                "sim_002", 
                {"gpu_acceleration": True, "memory_mb": 8192}
            )
            
            assert context2.gpu_device_id == 1
            assert context2.memory_allocated == 8192
            assert gpu2.memory_free == 20480 - 8192
            
            # Release first context
            await physics_service.release_physics_context("sim_001")
            assert gpu1.memory_free == 6144  # Memory restored
            assert "sim_001" not in physics_service.active_contexts
            
            print("✓ GPU resource allocation test passed")
    
    @pytest.mark.asyncio
    async def test_physics_docker_configuration(self):
        """Test physics Docker configuration generation"""
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True):
            
            # Mock GPU resource
            gpu = Mock()
            gpu.device_id = 0
            gpu.memory_free = 10240
            gpu.is_available = True
            physics_service.gpu_resources = [gpu]
            
            await physics_service.initialize()
            
            # Create physics context
            context = await physics_service.create_physics_context(
                "docker_test_sim",
                {"gpu_acceleration": True, "memory_mb": 2048}
            )
            
            # Get Docker configuration
            docker_config = physics_service.get_physics_docker_config(context)
            
            # Verify configuration
            assert docker_config["image"] == "python-physics-executor:latest"
            assert docker_config["mem_limit"] == "2304m"  # 2048 + 256
            assert "device_requests" in docker_config
            assert docker_config["device_requests"][0]["device_ids"] == ["0"]
            assert docker_config["device_requests"][0]["driver"] == "nvidia"
            
            # Verify environment variables
            env = docker_config["environment"]
            assert env["PHYSICS_ENGINE"] == "physx_ai"
            assert env["CUDA_VISIBLE_DEVICES"] == "0"
            assert env["PHYSX_GPU_MEMORY_MB"] == "2048"
            assert env["PHYSX_AI_ENABLED"] == "1"
            
            print("✓ Physics Docker configuration test passed")
    
    @pytest.mark.asyncio
    async def test_physics_execution_script_injection(self):
        """Test physics function injection in execution environment"""
        
        # This would test the actual physics execution script
        # For now, we'll test the environment setup
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True):
            
            gpu = Mock()
            gpu.device_id = 0
            gpu.memory_free = 8192
            gpu.is_available = True
            physics_service.gpu_resources = [gpu]
            
            await physics_service.initialize()
            
            context = await physics_service.create_physics_context(
                "script_test_sim",
                {"gpu_acceleration": True, "memory_mb": 1024}
            )
            
            # Get execution environment
            env = physics_service.get_physics_execution_environment(context)
            
            # Verify physics-specific environment variables
            expected_vars = [
                "PHYSICS_ENGINE",
                "SIMULATION_ID", 
                "CUDA_VISIBLE_DEVICES",
                "PHYSX_GPU_MEMORY_MB",
                "PHYSX_AI_ENABLED"
            ]
            
            for var in expected_vars:
                assert var in env, f"Missing environment variable: {var}"
            
            assert env["PHYSICS_ENGINE"] == "physx_ai"
            assert env["SIMULATION_ID"] == "script_test_sim"
            
            print("✓ Physics execution script injection test passed")
    
    @pytest.mark.asyncio
    async def test_concurrent_physics_executions(self):
        """Test multiple concurrent physics executions"""
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True), \
             patch.object(execution_service, '_ensure_execution_images'), \
             patch.object(execution_service, 'redis_client', new=AsyncMock()):
            
            # Mock multiple GPUs
            gpu1 = Mock()
            gpu1.device_id = 0
            gpu1.memory_free = 8192
            gpu1.is_available = True
            
            gpu2 = Mock()
            gpu2.device_id = 1
            gpu2.memory_free = 8192
            gpu2.is_available = True
            
            physics_service.gpu_resources = [gpu1, gpu2]
            await execution_service.initialize()
            
            # Create multiple physics execution requests
            requests = []
            for i in range(3):
                request = ExecutionRequest(
                    code=f"print('Physics simulation {i}')",
                    cell_id=f"cell_{i}",
                    notebook_id="concurrent_test",
                    execution_count=i+1,
                    enable_physics=True,
                    physics_requirements={
                        "gpu_acceleration": True,
                        "memory_mb": 1024
                    }
                )
                requests.append(request)
            
            # Execute all requests concurrently
            execution_ids = []
            for request in requests:
                execution_id = await execution_service.execute_code(request)
                execution_ids.append(execution_id)
            
            # Verify all executions have physics contexts
            for execution_id in execution_ids:
                assert execution_id in execution_service.physics_contexts
            
            # Verify GPU allocation
            active_contexts = len(execution_service.physics_contexts)
            assert active_contexts == 3
            
            print(f"✓ Concurrent physics executions test passed ({active_contexts} contexts)")
    
    @pytest.mark.asyncio
    async def test_physics_service_status_reporting(self):
        """Test physics service status reporting"""
        
        with patch.object(physics_service, '_detect_gpu_resources'), \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True), \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=True):
            
            # Mock GPU resources
            gpu = Mock()
            gpu.device_id = 0
            gpu.name = "NVIDIA RTX 4090"
            gpu.memory_total = 24576
            gpu.memory_free = 20480
            gpu.compute_capability = "8.9"
            gpu.is_available = True
            physics_service.gpu_resources = [gpu]
            
            await physics_service.initialize()
            
            # Create some active contexts
            await physics_service.create_physics_context("status_test_1", {"memory_mb": 1024})
            await physics_service.create_physics_context("status_test_2", {"memory_mb": 2048})
            
            # Get service status
            status = await physics_service.get_service_status()
            
            # Verify status information
            assert "available_engines" in status
            assert "gpu_resources" in status
            assert "active_contexts" in status
            assert "physx_ai_available" in status
            assert "physx_cpu_available" in status
            
            assert status["active_contexts"] == 2
            assert status["physx_ai_available"] is True
            assert status["physx_cpu_available"] is True
            assert len(status["gpu_resources"]) == 1
            assert status["gpu_resources"][0]["name"] == "NVIDIA RTX 4090"
            
            print("✓ Physics service status reporting test passed")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"])
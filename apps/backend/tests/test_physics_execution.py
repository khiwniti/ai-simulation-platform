"""
Tests for Physics-enabled Execution Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.services.execution_service import (
    ExecutionService,
    ExecutionRequest,
    ExecutionStatus,
    ExecutionOutput
)
from app.services.physics_service import (
    PhysicsContext,
    PhysicsEngineType,
    physics_service
)


class TestPhysicsExecution:
    """Test suite for physics-enabled execution"""
    
    @pytest.fixture
    async def execution_service(self):
        """Create an execution service instance for testing"""
        service = ExecutionService()
        # Mock Redis client
        service.redis_client = AsyncMock()
        return service
    
    @pytest.fixture
    def physics_context(self):
        """Create a mock physics context"""
        return PhysicsContext(
            simulation_id="test_execution_001",
            engine_type=PhysicsEngineType.PHYSX_AI,
            gpu_device_id=0,
            memory_allocated=1024,
            parameters={"gpu_acceleration": True, "memory_mb": 1024},
            is_active=True
        )
    
    @pytest.fixture
    def physics_execution_request(self):
        """Create a physics-enabled execution request"""
        return ExecutionRequest(
            code="""
import numpy as np
physics_info = get_physics_info()
print(f"Physics engine: {physics_info['engine']}")

# Simple particle simulation
particles = {
    'positions': [[0, 0, 0], [1, 1, 1]],
    'velocities': [[1, 0, 0], [-1, 0, 0]],
    'masses': [1.0, 1.0]
}
forces = [[0, -9.8, 0], [0, -9.8, 0]]

trajectory = simulate_particle_system(particles, forces, dt=0.01, steps=10)
print(f"Simulation completed with {len(trajectory)} steps")
""",
            cell_id="cell_001",
            notebook_id="notebook_001",
            execution_count=1,
            enable_physics=True,
            physics_requirements={
                "gpu_acceleration": True,
                "memory_mb": 1024,
                "complexity": "medium"
            }
        )
    
    @pytest.fixture
    def regular_execution_request(self):
        """Create a regular execution request"""
        return ExecutionRequest(
            code="print('Hello, World!')",
            cell_id="cell_002",
            notebook_id="notebook_001",
            execution_count=2,
            enable_physics=False
        )
    
    @pytest.mark.asyncio
    async def test_physics_execution_initialization(self, execution_service):
        """Test initialization with physics service"""
        with patch.object(execution_service, '_ensure_execution_images') as mock_images, \
             patch.object(physics_service, 'initialize', return_value=True) as mock_physics_init:
            
            await execution_service.initialize()
            
            mock_images.assert_called_once()
            mock_physics_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_code_with_physics(self, execution_service, physics_execution_request, physics_context):
        """Test code execution with physics enabled"""
        with patch.object(physics_service, 'create_physics_context', return_value=physics_context) as mock_create_context, \
             patch('uuid.uuid4', return_value=Mock(hex='test-execution-id')):
            
            execution_id = await execution_service.execute_code(physics_execution_request)
            
            assert execution_id == 'test-execution-id'
            assert execution_id in execution_service.physics_contexts
            mock_create_context.assert_called_once_with(
                execution_id,
                physics_execution_request.physics_requirements
            )
            
            # Verify Redis storage
            execution_service.redis_client.hset.assert_called_once()
            execution_service.redis_client.lpush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_code_without_physics(self, execution_service, regular_execution_request):
        """Test code execution without physics"""
        with patch('uuid.uuid4', return_value=Mock(hex='test-execution-id')):
            
            execution_id = await execution_service.execute_code(regular_execution_request)
            
            assert execution_id == 'test-execution-id'
            assert execution_id not in execution_service.physics_contexts
            
            # Verify Redis storage
            execution_service.redis_client.hset.assert_called_once()
            execution_service.redis_client.lpush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_code_physics_context_failure(self, execution_service, physics_execution_request):
        """Test code execution when physics context creation fails"""
        with patch.object(physics_service, 'create_physics_context', side_effect=Exception("GPU not available")) as mock_create_context, \
             patch('uuid.uuid4', return_value=Mock(hex='test-execution-id')):
            
            execution_id = await execution_service.execute_code(physics_execution_request)
            
            assert execution_id == 'test-execution-id'
            assert execution_id not in execution_service.physics_contexts
            mock_create_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_physics_success(self, execution_service, physics_execution_request, physics_context):
        """Test successful physics execution"""
        execution_id = "test_execution_001"
        execution_service.physics_contexts[execution_id] = physics_context
        
        # Mock Docker container
        mock_container = Mock()
        mock_container.attach_socket.return_value = Mock(_sock=Mock())
        
        with patch.object(physics_service, 'get_physics_docker_config') as mock_docker_config, \
             patch.object(execution_service.docker_client.containers, 'run', return_value=mock_container) as mock_run, \
             patch.object(execution_service, '_stream_container_output') as mock_stream, \
             patch.object(physics_service, 'release_physics_context') as mock_release:
            
            mock_docker_config.return_value = {
                "image": "python-physics-executor:latest",
                "environment": {"PHYSICS_ENGINE": "physx_ai"},
                "mem_limit": "1280m",
                "device_requests": [{"driver": "nvidia", "device_ids": ["0"], "capabilities": [["gpu", "compute"]]}]
            }
            
            await execution_service._execute_with_physics(execution_id, physics_execution_request)
            
            mock_docker_config.assert_called_once_with(physics_context)
            mock_run.assert_called_once()
            mock_stream.assert_called_once_with(execution_id, mock_container)
            mock_release.assert_called_once_with(execution_id)
    
    @pytest.mark.asyncio
    async def test_execute_with_physics_failure(self, execution_service, physics_execution_request, physics_context):
        """Test physics execution failure"""
        execution_id = "test_execution_001"
        execution_service.physics_contexts[execution_id] = physics_context
        
        with patch.object(physics_service, 'get_physics_docker_config', side_effect=Exception("Docker error")) as mock_docker_config, \
             patch.object(execution_service, '_mark_execution_failed') as mock_mark_failed, \
             patch.object(physics_service, 'release_physics_context') as mock_release:
            
            await execution_service._execute_with_physics(execution_id, physics_execution_request)
            
            mock_mark_failed.assert_called_once()
            mock_release.assert_called_once_with(execution_id)
    
    @pytest.mark.asyncio
    async def test_execute_regular_success(self, execution_service, regular_execution_request):
        """Test successful regular execution"""
        execution_id = "test_execution_002"
        
        # Mock Docker container
        mock_container = Mock()
        
        with patch.object(execution_service.docker_client.containers, 'run', return_value=mock_container) as mock_run, \
             patch.object(execution_service, '_stream_container_output') as mock_stream, \
             patch.object(execution_service, '_create_execution_script', return_value="mock_script") as mock_script:
            
            await execution_service._execute_regular(execution_id, regular_execution_request)
            
            mock_script.assert_called_once_with(regular_execution_request.code)
            mock_run.assert_called_once()
            mock_stream.assert_called_once_with(execution_id, mock_container)
    
    @pytest.mark.asyncio
    async def test_stream_container_output_success(self, execution_service):
        """Test successful container output streaming"""
        execution_id = "test_execution_001"
        
        # Mock container with JSON output
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b'{"output_type": "stdout", "content": {"text": "Hello"}, "timestamp": "2024-01-01T00:00:00"}\n'
        
        await execution_service._stream_container_output(execution_id, mock_container)
        
        # Verify output was stored
        execution_service.redis_client.lpush.assert_called()
        execution_service.redis_client.hset.assert_called_with(
            f"execution:{execution_id}",
            mapping={
                "status": "completed",
                "completed_at": pytest.approx(str, abs=1)  # Allow some time variance
            }
        )
        mock_container.remove.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_container_output_non_json(self, execution_service):
        """Test container output streaming with non-JSON output"""
        execution_id = "test_execution_001"
        
        # Mock container with plain text output
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b'Plain text output\n'
        
        await execution_service._stream_container_output(execution_id, mock_container)
        
        # Verify plain text was handled
        execution_service.redis_client.lpush.assert_called()
        mock_container.remove.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cancel_execution_with_physics(self, execution_service, physics_context):
        """Test cancelling execution with physics context"""
        execution_id = "test_execution_001"
        mock_container = Mock()
        
        execution_service.running_executions[execution_id] = mock_container
        execution_service.physics_contexts[execution_id] = physics_context
        
        with patch.object(physics_service, 'release_physics_context') as mock_release:
            result = await execution_service.cancel_execution(execution_id)
            
            assert result is True
            mock_container.stop.assert_called_once_with(timeout=5)
            mock_container.remove.assert_called_once()
            mock_release.assert_called_once_with(execution_id)
            assert execution_id not in execution_service.running_executions
            assert execution_id not in execution_service.physics_contexts
    
    @pytest.mark.asyncio
    async def test_cancel_execution_without_physics(self, execution_service):
        """Test cancelling execution without physics context"""
        execution_id = "test_execution_002"
        mock_container = Mock()
        
        execution_service.running_executions[execution_id] = mock_container
        
        result = await execution_service.cancel_execution(execution_id)
        
        assert result is True
        mock_container.stop.assert_called_once_with(timeout=5)
        mock_container.remove.assert_called_once()
        assert execution_id not in execution_service.running_executions
    
    @pytest.mark.asyncio
    async def test_get_queue_status_with_physics(self, execution_service, physics_context):
        """Test queue status with physics information"""
        execution_service.physics_contexts["test_execution_001"] = physics_context
        execution_service.running_executions["test_execution_001"] = Mock()
        
        # Mock Redis responses
        execution_service.redis_client.llen.return_value = 3
        
        with patch.object(physics_service, 'get_service_status', return_value={"test": "status"}) as mock_physics_status:
            status = await execution_service.get_queue_status()
            
            assert status["queue_length"] == 3
            assert status["running_executions"] == 1
            assert status["physics_contexts"] == 1
            assert status["physics_service"] == {"test": "status"}
            mock_physics_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_build_physics_execution_image_success(self, execution_service):
        """Test successful physics execution image building"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('shutil.copy2') as mock_copy, \
             patch.object(execution_service.docker_client.images, 'build') as mock_build:
            
            await execution_service._build_physics_execution_image()
            
            assert mock_copy.call_count == 2  # Dockerfile and script
            mock_build.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_build_physics_execution_image_missing_files(self, execution_service):
        """Test physics execution image building with missing files"""
        with patch('pathlib.Path.exists', return_value=False):
            # Should not raise exception, just log error
            await execution_service._build_physics_execution_image()
    
    @pytest.mark.asyncio
    async def test_build_physics_execution_image_build_failure(self, execution_service):
        """Test physics execution image building failure"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('shutil.copy2'), \
             patch.object(execution_service.docker_client.images, 'build', side_effect=Exception("Build failed")):
            
            # Should not raise exception, just log error
            await execution_service._build_physics_execution_image()
    
    @pytest.mark.asyncio
    async def test_process_execution_queue_physics_execution(self, execution_service, physics_execution_request, physics_context):
        """Test processing execution queue with physics execution"""
        execution_id = "test_execution_001"
        execution_service.physics_contexts[execution_id] = physics_context
        
        # Mock Redis responses
        execution_service.redis_client.rpop.return_value = execution_id.encode('utf-8')
        execution_service.redis_client.hgetall.return_value = {
            "request": physics_execution_request.model_dump_json()
        }
        
        with patch.object(execution_service, '_execute_with_physics') as mock_execute_physics:
            await execution_service._process_execution_queue()
            
            mock_execute_physics.assert_called_once_with(execution_id, physics_execution_request)
    
    @pytest.mark.asyncio
    async def test_process_execution_queue_regular_execution(self, execution_service, regular_execution_request):
        """Test processing execution queue with regular execution"""
        execution_id = "test_execution_002"
        
        # Mock Redis responses
        execution_service.redis_client.rpop.return_value = execution_id.encode('utf-8')
        execution_service.redis_client.hgetall.return_value = {
            "request": regular_execution_request.model_dump_json()
        }
        
        with patch.object(execution_service, '_execute_regular') as mock_execute_regular:
            await execution_service._process_execution_queue()
            
            mock_execute_regular.assert_called_once_with(execution_id, regular_execution_request)
    
    @pytest.mark.asyncio
    async def test_process_execution_queue_max_capacity(self, execution_service):
        """Test processing execution queue when at max capacity"""
        # Fill up running executions
        for i in range(execution_service.max_concurrent_executions):
            execution_service.running_executions[f"exec_{i}"] = Mock()
        
        # Should return early without processing
        await execution_service._process_execution_queue()
        
        execution_service.redis_client.rpop.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_execution_queue_empty_queue(self, execution_service):
        """Test processing execution queue when queue is empty"""
        execution_service.redis_client.rpop.return_value = None
        
        await execution_service._process_execution_queue()
        
        execution_service.redis_client.hgetall.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_mark_execution_failed(self, execution_service):
        """Test marking execution as failed"""
        execution_id = "test_execution_001"
        error_message = "Test error"
        
        await execution_service._mark_execution_failed(execution_id, error_message)
        
        execution_service.redis_client.hset.assert_called_once_with(
            f"execution:{execution_id}",
            mapping={
                "status": "failed",
                "completed_at": pytest.approx(str, abs=1),
                "error": error_message
            }
        )
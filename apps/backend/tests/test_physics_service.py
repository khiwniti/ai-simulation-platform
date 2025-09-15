"""
Tests for Physics Service with NVIDIA PhysX AI integration
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.physics_service import (
    PhysicsService,
    PhysicsEngineType,
    GPUResource,
    PhysicsContext
)


class TestPhysicsService:
    """Test suite for Physics Service"""
    
    @pytest.fixture
    async def physics_service(self):
        """Create a physics service instance for testing"""
        service = PhysicsService()
        return service
    
    @pytest.fixture
    def mock_gpu_resources(self):
        """Mock GPU resources for testing"""
        return [
            GPUResource(
                device_id=0,
                name="NVIDIA RTX 4090",
                memory_total=24576,
                memory_free=20480,
                compute_capability="8.9",
                is_available=True
            ),
            GPUResource(
                device_id=1,
                name="NVIDIA RTX 3080",
                memory_total=10240,
                memory_free=8192,
                compute_capability="8.6",
                is_available=True
            )
        ]
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, physics_service):
        """Test successful physics service initialization"""
        with patch.object(physics_service, '_detect_gpu_resources') as mock_detect_gpu, \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=True) as mock_physx_ai, \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=True) as mock_physx_cpu:
            
            result = await physics_service.initialize()
            
            assert result is True
            assert PhysicsEngineType.PHYSX_AI in physics_service.available_engines
            assert PhysicsEngineType.PHYSX_CPU in physics_service.available_engines
            assert PhysicsEngineType.SOFTWARE_FALLBACK in physics_service.available_engines
            mock_detect_gpu.assert_called_once()
            mock_physx_ai.assert_called_once()
            mock_physx_cpu.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialization_no_physx(self, physics_service):
        """Test initialization when PhysX is not available"""
        with patch.object(physics_service, '_detect_gpu_resources') as mock_detect_gpu, \
             patch.object(physics_service, '_check_physx_ai_availability', return_value=False) as mock_physx_ai, \
             patch.object(physics_service, '_check_physx_cpu_availability', return_value=False) as mock_physx_cpu:
            
            result = await physics_service.initialize()
            
            assert result is True
            assert PhysicsEngineType.PHYSX_AI not in physics_service.available_engines
            assert PhysicsEngineType.PHYSX_CPU not in physics_service.available_engines
            assert PhysicsEngineType.SOFTWARE_FALLBACK in physics_service.available_engines
    
    @pytest.mark.asyncio
    async def test_gpu_detection_success(self, physics_service, mock_gpu_resources):
        """Test successful GPU detection"""
        with patch('pynvml.nvmlInit'), \
             patch('pynvml.nvmlDeviceGetCount', return_value=2), \
             patch('pynvml.nvmlDeviceGetHandleByIndex') as mock_handle, \
             patch('pynvml.nvmlDeviceGetName', side_effect=[b'NVIDIA RTX 4090', b'NVIDIA RTX 3080']), \
             patch('pynvml.nvmlDeviceGetMemoryInfo') as mock_memory, \
             patch('pynvml.nvmlDeviceGetCudaComputeCapability', side_effect=[(8, 9), (8, 6)]):
            
            # Mock memory info
            mock_memory.side_effect = [
                Mock(total=24576*1024*1024, free=20480*1024*1024),
                Mock(total=10240*1024*1024, free=8192*1024*1024)
            ]
            
            await physics_service._detect_gpu_resources()
            
            assert len(physics_service.gpu_resources) == 2
            assert physics_service.gpu_resources[0].name == "NVIDIA RTX 4090"
            assert physics_service.gpu_resources[0].memory_total == 24576
            assert physics_service.gpu_resources[1].name == "NVIDIA RTX 3080"
            assert physics_service.gpu_resources[1].memory_total == 10240
    
    @pytest.mark.asyncio
    async def test_gpu_detection_no_pynvml(self, physics_service):
        """Test GPU detection when pynvml is not available"""
        with patch('pynvml.nvmlInit', side_effect=ImportError("pynvml not available")):
            await physics_service._detect_gpu_resources()
            assert len(physics_service.gpu_resources) == 0
    
    @pytest.mark.asyncio
    async def test_physx_ai_availability_check(self, physics_service, mock_gpu_resources):
        """Test PhysX AI availability check"""
        physics_service.gpu_resources = mock_gpu_resources
        
        with patch.object(physics_service, '_check_physx_ai_installation', return_value=True):
            result = await physics_service._check_physx_ai_availability()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_physx_ai_no_gpu(self, physics_service):
        """Test PhysX AI check when no GPU is available"""
        physics_service.gpu_resources = []
        
        result = await physics_service._check_physx_ai_availability()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_physx_cpu_availability_check(self, physics_service):
        """Test PhysX CPU availability check"""
        with patch('psutil.cpu_count', return_value=8), \
             patch('psutil.virtual_memory', return_value=Mock(total=16*1024**3)):
            
            result = await physics_service._check_physx_cpu_availability()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_physx_cpu_insufficient_resources(self, physics_service):
        """Test PhysX CPU check with insufficient resources"""
        with patch('psutil.cpu_count', return_value=2), \
             patch('psutil.virtual_memory', return_value=Mock(total=4*1024**3)):
            
            result = await physics_service._check_physx_cpu_availability()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_optimal_engine_selection_gpu_required(self, physics_service, mock_gpu_resources):
        """Test optimal engine selection when GPU is required"""
        physics_service.available_engines = [PhysicsEngineType.PHYSX_AI, PhysicsEngineType.SOFTWARE_FALLBACK]
        physics_service.gpu_resources = mock_gpu_resources
        
        requirements = {
            "gpu_acceleration": True,
            "complexity": "high",
            "memory_mb": 1024
        }
        
        engine = await physics_service.get_optimal_engine(requirements)
        assert engine == PhysicsEngineType.PHYSX_AI
    
    @pytest.mark.asyncio
    async def test_optimal_engine_selection_fallback(self, physics_service):
        """Test optimal engine selection fallback"""
        physics_service.available_engines = [PhysicsEngineType.SOFTWARE_FALLBACK]
        physics_service.gpu_resources = []
        
        requirements = {
            "gpu_acceleration": True,
            "complexity": "high"
        }
        
        engine = await physics_service.get_optimal_engine(requirements)
        assert engine == PhysicsEngineType.SOFTWARE_FALLBACK
    
    @pytest.mark.asyncio
    async def test_create_physics_context(self, physics_service, mock_gpu_resources):
        """Test physics context creation"""
        physics_service.available_engines = [PhysicsEngineType.PHYSX_AI]
        physics_service.gpu_resources = mock_gpu_resources
        
        requirements = {
            "gpu_acceleration": True,
            "memory_mb": 512
        }
        
        context = await physics_service.create_physics_context("test_sim_001", requirements)
        
        assert context.simulation_id == "test_sim_001"
        assert context.engine_type == PhysicsEngineType.PHYSX_AI
        assert context.gpu_device_id is not None
        assert context.memory_allocated > 0
        assert context.is_active is True
        assert "test_sim_001" in physics_service.active_contexts
    
    @pytest.mark.asyncio
    async def test_release_physics_context(self, physics_service, mock_gpu_resources):
        """Test physics context release"""
        physics_service.available_engines = [PhysicsEngineType.PHYSX_AI]
        physics_service.gpu_resources = mock_gpu_resources
        
        # Create context
        context = await physics_service.create_physics_context("test_sim_001", {"memory_mb": 512})
        initial_free_memory = mock_gpu_resources[0].memory_free
        
        # Release context
        await physics_service.release_physics_context("test_sim_001")
        
        assert "test_sim_001" not in physics_service.active_contexts
        assert mock_gpu_resources[0].memory_free > initial_free_memory
    
    @pytest.mark.asyncio
    async def test_gpu_memory_allocation(self, physics_service, mock_gpu_resources):
        """Test GPU memory allocation"""
        physics_service.gpu_resources = mock_gpu_resources
        
        device_id, allocated = await physics_service._allocate_gpu_resources(1024)
        
        assert device_id == 0  # Should use first available GPU
        assert allocated == 1024
        assert mock_gpu_resources[0].memory_free == 20480 - 1024
    
    @pytest.mark.asyncio
    async def test_gpu_memory_allocation_insufficient(self, physics_service, mock_gpu_resources):
        """Test GPU memory allocation when insufficient memory"""
        physics_service.gpu_resources = mock_gpu_resources
        
        # Try to allocate more than available
        device_id, allocated = await physics_service._allocate_gpu_resources(30000)
        
        assert device_id is None
        assert allocated == 0
    
    def test_physics_execution_environment_physx_ai(self, physics_service):
        """Test physics execution environment for PhysX AI"""
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_AI,
            gpu_device_id=0,
            memory_allocated=1024,
            parameters={},
            is_active=True
        )
        
        env = physics_service.get_physics_execution_environment(context)
        
        assert env["PHYSICS_ENGINE"] == "physx_ai"
        assert env["CUDA_VISIBLE_DEVICES"] == "0"
        assert env["PHYSX_GPU_MEMORY_MB"] == "1024"
        assert env["PHYSX_AI_ENABLED"] == "1"
    
    def test_physics_execution_environment_cpu(self, physics_service):
        """Test physics execution environment for PhysX CPU"""
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_CPU,
            gpu_device_id=None,
            memory_allocated=0,
            parameters={},
            is_active=True
        )
        
        with patch('psutil.cpu_count', return_value=8):
            env = physics_service.get_physics_execution_environment(context)
        
        assert env["PHYSICS_ENGINE"] == "physx_cpu"
        assert env["PHYSX_CPU_THREADS"] == "8"
        assert env["PHYSX_CPU_ENABLED"] == "1"
    
    def test_physics_execution_environment_fallback(self, physics_service):
        """Test physics execution environment for software fallback"""
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.SOFTWARE_FALLBACK,
            gpu_device_id=None,
            memory_allocated=0,
            parameters={},
            is_active=True
        )
        
        env = physics_service.get_physics_execution_environment(context)
        
        assert env["PHYSICS_ENGINE"] == "software_fallback"
        assert env["PHYSICS_SOFTWARE_FALLBACK"] == "1"
    
    def test_physics_docker_config_with_gpu(self, physics_service):
        """Test Docker configuration with GPU support"""
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_AI,
            gpu_device_id=0,
            memory_allocated=1024,
            parameters={},
            is_active=True
        )
        
        config = physics_service.get_physics_docker_config(context)
        
        assert config["image"] == "python-physics-executor:latest"
        assert config["mem_limit"] == "1280m"  # 1024 + 256
        assert "device_requests" in config
        assert config["device_requests"][0]["device_ids"] == ["0"]
    
    def test_physics_docker_config_cpu_only(self, physics_service):
        """Test Docker configuration for CPU-only execution"""
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_CPU,
            gpu_device_id=None,
            memory_allocated=0,
            parameters={},
            is_active=True
        )
        
        config = physics_service.get_physics_docker_config(context)
        
        assert config["image"] == "python-physics-executor:latest"
        assert config["mem_limit"] == "512m"  # minimum 512
        assert "device_requests" not in config
    
    @pytest.mark.asyncio
    async def test_service_status(self, physics_service, mock_gpu_resources):
        """Test service status reporting"""
        physics_service.available_engines = [PhysicsEngineType.PHYSX_AI, PhysicsEngineType.SOFTWARE_FALLBACK]
        physics_service.gpu_resources = mock_gpu_resources
        physics_service.physx_ai_available = True
        physics_service.physx_cpu_available = False
        
        # Create an active context
        context = PhysicsContext(
            simulation_id="test_sim",
            engine_type=PhysicsEngineType.PHYSX_AI,
            gpu_device_id=0,
            memory_allocated=1024,
            parameters={},
            is_active=True
        )
        physics_service.active_contexts["test_sim"] = context
        
        status = await physics_service.get_service_status()
        
        assert status["available_engines"] == ["physx_ai", "software_fallback"]
        assert len(status["gpu_resources"]) == 2
        assert status["active_contexts"] == 1
        assert status["physx_ai_available"] is True
        assert status["physx_cpu_available"] is False
        assert status["gpu_resources"][0]["name"] == "NVIDIA RTX 4090"
"""
NVIDIA PhysX AI Physics Service

Provides physics simulation capabilities using NVIDIA PhysX AI with GPU acceleration,
resource management, and physics-specific code execution paths.
"""

import asyncio
import logging
import json
import subprocess
import platform
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import psutil

logger = logging.getLogger(__name__)


class PhysicsEngineType(Enum):
    """Available physics engine types"""
    PHYSX_AI = "physx_ai"
    PHYSX_CPU = "physx_cpu"
    SOFTWARE_FALLBACK = "software_fallback"


@dataclass
class GPUResource:
    """GPU resource information"""
    device_id: int
    name: str
    memory_total: int  # MB
    memory_free: int   # MB
    compute_capability: str
    is_available: bool


@dataclass
class PhysicsContext:
    """Physics simulation context"""
    simulation_id: str
    engine_type: PhysicsEngineType
    gpu_device_id: Optional[int]
    memory_allocated: int  # MB
    parameters: Dict[str, Any]
    is_active: bool


class PhysicsService:
    """
    NVIDIA PhysX AI integration service with GPU resource management
    """
    
    def __init__(self):
        self.available_engines: List[PhysicsEngineType] = []
        self.gpu_resources: List[GPUResource] = []
        self.active_contexts: Dict[str, PhysicsContext] = {}
        self.physx_ai_available = False
        self.physx_cpu_available = False
        
    async def initialize(self) -> bool:
        """
        Initialize the physics service and detect available engines
        """
        logger.info("Initializing Physics Service...")
        
        # Detect GPU resources
        await self._detect_gpu_resources()
        
        # Check PhysX AI availability
        self.physx_ai_available = await self._check_physx_ai_availability()
        
        # Check PhysX CPU availability
        self.physx_cpu_available = await self._check_physx_cpu_availability()
        
        # Determine available engines
        self._determine_available_engines()
        
        logger.info(f"Physics Service initialized. Available engines: {[e.value for e in self.available_engines]}")
        logger.info(f"GPU resources detected: {len(self.gpu_resources)}")
        
        return len(self.available_engines) > 0
        
    async def _detect_gpu_resources(self):
        """Detect available GPU resources"""
        self.gpu_resources = []
        
        try:
            # Try to detect NVIDIA GPUs using nvidia-ml-py
            import pynvml
            pynvml.nvmlInit()
            
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get device info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Get compute capability
                major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                compute_capability = f"{major}.{minor}"
                
                gpu = GPUResource(
                    device_id=i,
                    name=name,
                    memory_total=memory_info.total // (1024 * 1024),  # Convert to MB
                    memory_free=memory_info.free // (1024 * 1024),
                    compute_capability=compute_capability,
                    is_available=True
                )
                
                self.gpu_resources.append(gpu)
                logger.info(f"Detected GPU {i}: {name} ({gpu.memory_total}MB)")
                
        except ImportError:
            logger.warning("pynvml not available, cannot detect NVIDIA GPUs")
        except Exception as e:
            logger.warning(f"Error detecting GPU resources: {e}")
            
    async def _check_physx_ai_availability(self) -> bool:
        """Check if NVIDIA PhysX AI is available"""
        try:
            # Try to import PhysX AI (this would be the actual PhysX AI Python bindings)
            # For now, we'll simulate this check
            
            # Check if we have compatible GPU
            if not self.gpu_resources:
                logger.info("No NVIDIA GPUs detected, PhysX AI not available")
                return False
                
            # Check if PhysX AI libraries are installed
            # This would check for actual PhysX AI installation
            physx_ai_available = await self._check_physx_ai_installation()
            
            if physx_ai_available:
                logger.info("NVIDIA PhysX AI detected and available")
                return True
            else:
                logger.info("NVIDIA PhysX AI libraries not found")
                return False
                
        except Exception as e:
            logger.warning(f"Error checking PhysX AI availability: {e}")
            return False
            
    async def _check_physx_ai_installation(self) -> bool:
        """Check if PhysX AI libraries are properly installed"""
        try:
            # This would check for actual PhysX AI installation
            # For demonstration, we'll check for CUDA availability as a proxy
            result = subprocess.run(
                ["nvidia-smi"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
            
    async def _check_physx_cpu_availability(self) -> bool:
        """Check if PhysX CPU version is available"""
        try:
            # This would check for PhysX CPU libraries
            # For now, we'll assume it's available if we have sufficient CPU resources
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Require at least 4 cores and 8GB RAM for PhysX CPU
            if cpu_count >= 4 and memory_gb >= 8:
                logger.info("PhysX CPU requirements met")
                return True
            else:
                logger.info(f"Insufficient resources for PhysX CPU (CPU: {cpu_count}, RAM: {memory_gb:.1f}GB)")
                return False
                
        except Exception as e:
            logger.warning(f"Error checking PhysX CPU availability: {e}")
            return False
            
    def _determine_available_engines(self):
        """Determine which physics engines are available"""
        self.available_engines = []
        
        if self.physx_ai_available:
            self.available_engines.append(PhysicsEngineType.PHYSX_AI)
            
        if self.physx_cpu_available:
            self.available_engines.append(PhysicsEngineType.PHYSX_CPU)
            
        # Software fallback is always available
        self.available_engines.append(PhysicsEngineType.SOFTWARE_FALLBACK)
        
    async def get_optimal_engine(self, requirements: Dict[str, Any]) -> PhysicsEngineType:
        """
        Determine the optimal physics engine based on simulation requirements
        """
        # Check if GPU acceleration is required
        requires_gpu = requirements.get("gpu_acceleration", False)
        complexity = requirements.get("complexity", "medium")
        particle_count = requirements.get("particle_count", 1000)
        
        # Prefer PhysX AI for GPU-accelerated simulations
        if requires_gpu and PhysicsEngineType.PHYSX_AI in self.available_engines:
            if await self._has_available_gpu_memory(requirements.get("memory_mb", 512)):
                return PhysicsEngineType.PHYSX_AI
                
        # Use PhysX CPU for complex simulations without GPU requirement
        if complexity in ["high", "very_high"] and PhysicsEngineType.PHYSX_CPU in self.available_engines:
            return PhysicsEngineType.PHYSX_CPU
            
        # Use PhysX AI if available for medium complexity
        if complexity == "medium" and PhysicsEngineType.PHYSX_AI in self.available_engines:
            if await self._has_available_gpu_memory(256):
                return PhysicsEngineType.PHYSX_AI
                
        # Fallback to software implementation
        return PhysicsEngineType.SOFTWARE_FALLBACK
        
    async def _has_available_gpu_memory(self, required_mb: int) -> bool:
        """Check if there's sufficient GPU memory available"""
        for gpu in self.gpu_resources:
            if gpu.is_available and gpu.memory_free >= required_mb:
                return True
        return False
        
    async def create_physics_context(
        self, 
        simulation_id: str, 
        requirements: Dict[str, Any]
    ) -> PhysicsContext:
        """
        Create a physics simulation context with resource allocation
        """
        engine_type = await self.get_optimal_engine(requirements)
        gpu_device_id = None
        memory_allocated = 0
        
        # Allocate GPU resources if using PhysX AI
        if engine_type == PhysicsEngineType.PHYSX_AI:
            gpu_device_id, memory_allocated = await self._allocate_gpu_resources(
                requirements.get("memory_mb", 512)
            )
            
        context = PhysicsContext(
            simulation_id=simulation_id,
            engine_type=engine_type,
            gpu_device_id=gpu_device_id,
            memory_allocated=memory_allocated,
            parameters=requirements,
            is_active=True
        )
        
        self.active_contexts[simulation_id] = context
        logger.info(f"Created physics context for {simulation_id} using {engine_type.value}")
        
        return context
        
    async def _allocate_gpu_resources(self, required_mb: int) -> Tuple[Optional[int], int]:
        """Allocate GPU resources for a simulation"""
        for gpu in self.gpu_resources:
            if gpu.is_available and gpu.memory_free >= required_mb:
                # Reserve memory (simplified allocation)
                gpu.memory_free -= required_mb
                logger.info(f"Allocated {required_mb}MB on GPU {gpu.device_id}")
                return gpu.device_id, required_mb
                
        logger.warning(f"Could not allocate {required_mb}MB GPU memory")
        return None, 0
        
    async def release_physics_context(self, simulation_id: str):
        """Release physics context and associated resources"""
        if simulation_id not in self.active_contexts:
            return
            
        context = self.active_contexts[simulation_id]
        
        # Release GPU resources
        if context.gpu_device_id is not None:
            await self._release_gpu_resources(context.gpu_device_id, context.memory_allocated)
            
        # Mark context as inactive
        context.is_active = False
        del self.active_contexts[simulation_id]
        
        logger.info(f"Released physics context for {simulation_id}")
        
    async def _release_gpu_resources(self, device_id: int, memory_mb: int):
        """Release allocated GPU resources"""
        for gpu in self.gpu_resources:
            if gpu.device_id == device_id:
                gpu.memory_free += memory_mb
                logger.info(f"Released {memory_mb}MB on GPU {device_id}")
                break
                
    def get_physics_execution_environment(self, context: PhysicsContext) -> Dict[str, Any]:
        """
        Get environment configuration for physics code execution
        """
        env_config = {
            "PHYSICS_ENGINE": context.engine_type.value,
            "SIMULATION_ID": context.simulation_id,
        }
        
        if context.engine_type == PhysicsEngineType.PHYSX_AI:
            env_config.update({
                "CUDA_VISIBLE_DEVICES": str(context.gpu_device_id) if context.gpu_device_id is not None else "",
                "PHYSX_GPU_MEMORY_MB": str(context.memory_allocated),
                "PHYSX_AI_ENABLED": "1"
            })
        elif context.engine_type == PhysicsEngineType.PHYSX_CPU:
            env_config.update({
                "PHYSX_CPU_THREADS": str(min(psutil.cpu_count(), 8)),
                "PHYSX_CPU_ENABLED": "1"
            })
        else:
            env_config.update({
                "PHYSICS_SOFTWARE_FALLBACK": "1"
            })
            
        return env_config
        
    def get_physics_docker_config(self, context: PhysicsContext) -> Dict[str, Any]:
        """
        Get Docker configuration for physics simulations
        """
        config = {
            "image": "python-physics-executor:latest",
            "environment": self.get_physics_execution_environment(context),
            "mem_limit": f"{max(512, context.memory_allocated + 256)}m",
        }
        
        # Add GPU support for PhysX AI
        if context.engine_type == PhysicsEngineType.PHYSX_AI and context.gpu_device_id is not None:
            config.update({
                "device_requests": [
                    {
                        "driver": "nvidia",
                        "device_ids": [str(context.gpu_device_id)],
                        "capabilities": [["gpu", "compute"]]
                    }
                ]
            })
            
        return config
        
    async def get_service_status(self) -> Dict[str, Any]:
        """Get current physics service status"""
        return {
            "available_engines": [e.value for e in self.available_engines],
            "gpu_resources": [
                {
                    "device_id": gpu.device_id,
                    "name": gpu.name,
                    "memory_total": gpu.memory_total,
                    "memory_free": gpu.memory_free,
                    "compute_capability": gpu.compute_capability,
                    "is_available": gpu.is_available
                }
                for gpu in self.gpu_resources
            ],
            "active_contexts": len(self.active_contexts),
            "physx_ai_available": self.physx_ai_available,
            "physx_cpu_available": self.physx_cpu_available
        }


# Global physics service instance
physics_service = PhysicsService()
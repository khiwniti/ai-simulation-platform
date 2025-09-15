"""
Optimization Agent specialized for performance tuning and GPU optimization.
"""

import re
import logging
from typing import Dict, Any, List, Set
from datetime import datetime

from .base import BaseAgent, AgentContext, AgentResponse, AgentCapability

logger = logging.getLogger(__name__)


class OptimizationAgent(BaseAgent):
    """
    Specialized AI agent for performance optimization and GPU utilization.
    
    Provides expertise in performance profiling, GPU optimization, memory management,
    and simulation speed improvements for physics and visualization systems.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id)
        self.capabilities = {
            AgentCapability.PERFORMANCE_OPTIMIZATION,
            AgentCapability.GPU_OPTIMIZATION
        }
        
        # Optimization-specific knowledge patterns
        self.optimization_keywords = {
            'performance', 'optimize', 'optimization', 'speed', 'fast', 'slow',
            'lag', 'fps', 'memory', 'gpu', 'cuda', 'parallel', 'threading',
            'bottleneck', 'profile', 'benchmark', 'efficient', 'cache',
            'algorithm', 'complexity', 'scalability', 'throughput'
        }
        
        self.gpu_patterns = [
            r'gpu', r'cuda', r'opencl', r'webgl', r'shader', r'compute',
            r'parallel', r'thread', r'block', r'grid', r'memory bandwidth',
            r'texture memory', r'shared memory', r'global memory'
        ]
        
    @property
    def name(self) -> str:
        return "Performance Optimization Expert"
        
    @property
    def description(self) -> str:
        return ("Specialized in performance optimization, GPU utilization, "
                "memory management, and simulation speed improvements.")
        
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """Determine if this agent can handle the optimization-related query."""
        query_lower = query.lower()
        
        # Check for optimization keywords (count matches, not percentage)
        opt_matches = sum(1 for keyword in self.optimization_keywords 
                         if keyword in query_lower)
        opt_score = min(1.0, opt_matches * 0.2)  # Each match adds 0.2
        
        # Check for GPU-related patterns
        gpu_matches = sum(1 for pattern in self.gpu_patterns 
                         if re.search(pattern, query_lower))
        gpu_score = min(1.0, gpu_matches * 0.3)  # Each GPU match adds 0.3
        
        # Check context for performance-related code
        context_score = 0.0
        if context.current_code:
            code_lower = context.current_code.lower()
            context_matches = sum(1 for keyword in self.optimization_keywords 
                                if keyword in code_lower)
            context_score = min(0.3, context_matches * 0.1)  # Max 0.3 from context
            
        # Combine scores
        total_score = opt_score + gpu_score + context_score
        
        # Boost score for explicit optimization requests
        if any(term in query_lower for term in ['optimize', 'performance', 'speed up', 'faster', 'gpu', 'memory']):
            total_score = min(1.0, total_score + 0.4)
            
        return min(1.0, total_score)
        
    async def process_query(self, query: str, context: AgentContext) -> AgentResponse:
        """Process an optimization-related query and provide specialized assistance."""
        start_time = datetime.utcnow()
        
        try:
            # Analyze query type
            query_type = self._analyze_query_type(query)
            
            # Generate response based on query type
            response_text, suggestions, code_snippets = await self._generate_optimization_response(
                query, query_type, context
            )
            
            # Calculate confidence based on query match and context
            confidence = self._calculate_confidence(query, context, query_type)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                response=response_text,
                confidence_score=confidence,
                capabilities_used=list(self.capabilities),
                context={'query_type': query_type},
                suggestions=suggestions,
                code_snippets=code_snippets,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Optimization agent query processing failed: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                response=f"I encountered an error processing your optimization query: {str(e)}",
                confidence_score=0.1,
                response_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
    def _analyze_query_type(self, query: str) -> str:
        """Analyze the type of optimization query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['gpu', 'cuda', 'opencl', 'shader']):
            return 'gpu_optimization'
        elif any(term in query_lower for term in ['memory', 'ram', 'allocation', 'leak']):
            return 'memory_optimization'
        elif any(term in query_lower for term in ['physics', 'simulation', 'physx']):
            return 'physics_optimization'
        elif any(term in query_lower for term in ['render', 'graphics', '3d', 'fps']):
            return 'rendering_optimization'
        elif any(term in query_lower for term in ['algorithm', 'complexity', 'big o']):
            return 'algorithmic_optimization'
        elif any(term in query_lower for term in ['profile', 'benchmark', 'measure']):
            return 'profiling'
        elif any(term in query_lower for term in ['parallel', 'thread', 'concurrent']):
            return 'parallelization'
        elif any(term in query_lower for term in ['cache', 'data structure', 'access pattern']):
            return 'data_optimization'
        else:
            return 'general'
            
    async def _generate_optimization_response(
        self, 
        query: str, 
        query_type: str, 
        context: AgentContext
    ) -> tuple[str, List[str], List[str]]:
        """Generate optimization-specific response, suggestions, and code snippets."""
        
        if query_type == 'gpu_optimization':
            return self._generate_gpu_response(query, context)
        elif query_type == 'memory_optimization':
            return self._generate_memory_response(query, context)
        elif query_type == 'physics_optimization':
            return self._generate_physics_opt_response(query, context)
        elif query_type == 'rendering_optimization':
            return self._generate_rendering_opt_response(query, context)
        elif query_type == 'algorithmic_optimization':
            return self._generate_algorithmic_response(query, context)
        elif query_type == 'profiling':
            return self._generate_profiling_response(query, context)
        elif query_type == 'parallelization':
            return self._generate_parallel_response(query, context)
        elif query_type == 'data_optimization':
            return self._generate_data_opt_response(query, context)
        else:
            return self._generate_general_response(query, context)
            
    def _generate_gpu_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for GPU optimization queries."""
        response = """GPU optimization is crucial for high-performance physics and graphics:

**Key GPU Optimization Strategies:**
1. **Memory Coalescing**: Ensure contiguous memory access patterns
2. **Occupancy**: Balance threads per block with register/memory usage
3. **Memory Hierarchy**: Utilize shared memory, texture memory, and constant memory
4. **Compute Utilization**: Keep GPU cores busy with sufficient parallelism
5. **Memory Bandwidth**: Minimize data transfers between CPU and GPU"""

        suggestions = [
            "Profile GPU utilization using NVIDIA Nsight or similar tools",
            "Optimize memory access patterns for coalesced reads/writes",
            "Use appropriate thread block sizes (typically 128-512 threads)",
            "Minimize CPU-GPU data transfers by keeping data on GPU",
            "Utilize GPU-specific libraries like cuBLAS, cuFFT for common operations"
        ]
        
        code_snippets = [
            """# CUDA kernel optimization example
__global__ void optimized_physics_kernel(
    float* positions, 
    float* velocities, 
    float* forces,
    int num_particles,
    float dt
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    // Ensure we don't go out of bounds
    if (idx >= num_particles) return;
    
    // Coalesced memory access
    float3 pos = make_float3(positions[idx*3], positions[idx*3+1], positions[idx*3+2]);
    float3 vel = make_float3(velocities[idx*3], velocities[idx*3+1], velocities[idx*3+2]);
    float3 force = make_float3(forces[idx*3], forces[idx*3+1], forces[idx*3+2]);
    
    // Update physics (Verlet integration)
    vel.x += force.x * dt;
    vel.y += force.y * dt;
    vel.z += force.z * dt;
    
    pos.x += vel.x * dt;
    pos.y += vel.y * dt;
    pos.z += vel.z * dt;
    
    // Write back with coalesced access
    positions[idx*3] = pos.x;
    positions[idx*3+1] = pos.y;
    positions[idx*3+2] = pos.z;
    velocities[idx*3] = vel.x;
    velocities[idx*3+1] = vel.y;
    velocities[idx*3+2] = vel.z;
}
""",
            """# GPU memory management optimization
class GPUMemoryManager:
    def __init__(self):
        self.memory_pools = {}
        self.allocated_buffers = {}
    
    def allocate_buffer(self, size, buffer_type='physics'):
        # Use memory pools to reduce allocation overhead
        if buffer_type not in self.memory_pools:
            self.memory_pools[buffer_type] = []
        
        # Try to reuse existing buffer
        for buffer in self.memory_pools[buffer_type]:
            if buffer.size >= size and not buffer.in_use:
                buffer.in_use = True
                return buffer
        
        # Allocate new buffer if none available
        new_buffer = self._allocate_gpu_buffer(size)
        self.memory_pools[buffer_type].append(new_buffer)
        return new_buffer
    
    def _allocate_gpu_buffer(self, size):
        # Platform-specific GPU allocation
        import cupy as cp  # or use PyCUDA
        return cp.zeros(size, dtype=cp.float32)
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_memory_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for memory optimization queries."""
        response = """Memory optimization is essential for large-scale simulations:

**Memory Optimization Techniques:**
1. **Object Pooling**: Reuse objects instead of frequent allocation/deallocation
2. **Data Layout**: Structure of Arrays (SoA) vs Array of Structures (AoS)
3. **Cache Efficiency**: Optimize data access patterns for CPU cache
4. **Memory Alignment**: Align data structures for SIMD operations
5. **Garbage Collection**: Minimize GC pressure in managed languages"""

        suggestions = [
            "Use object pools for frequently created/destroyed objects",
            "Implement Structure of Arrays for better cache performance",
            "Profile memory usage to identify allocation hotspots",
            "Use memory-mapped files for large datasets",
            "Consider custom allocators for specific use cases"
        ]
        
        code_snippets = [
            """# Object pooling for physics objects
class PhysicsObjectPool:
    def __init__(self, initial_size=1000):
        self.available_objects = []
        self.active_objects = set()
        
        # Pre-allocate objects
        for _ in range(initial_size):
            obj = self._create_physics_object()
            self.available_objects.append(obj)
    
    def acquire_object(self):
        if self.available_objects:
            obj = self.available_objects.pop()
        else:
            obj = self._create_physics_object()
        
        self.active_objects.add(obj)
        return obj
    
    def release_object(self, obj):
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            obj.reset()  # Reset to default state
            self.available_objects.append(obj)
    
    def _create_physics_object(self):
        return PhysicsObject()

# Usage
pool = PhysicsObjectPool()
obj = pool.acquire_object()
# Use object...
pool.release_object(obj)
""",
            """# Structure of Arrays for better cache performance
class ParticleSystemSoA:
    def __init__(self, max_particles):
        # Separate arrays for each property (SoA)
        self.positions_x = np.zeros(max_particles, dtype=np.float32)
        self.positions_y = np.zeros(max_particles, dtype=np.float32)
        self.positions_z = np.zeros(max_particles, dtype=np.float32)
        
        self.velocities_x = np.zeros(max_particles, dtype=np.float32)
        self.velocities_y = np.zeros(max_particles, dtype=np.float32)
        self.velocities_z = np.zeros(max_particles, dtype=np.float32)
        
        self.masses = np.zeros(max_particles, dtype=np.float32)
        self.active_count = 0
    
    def update_positions(self, dt):
        # Vectorized operations on contiguous arrays
        active_slice = slice(0, self.active_count)
        
        self.positions_x[active_slice] += self.velocities_x[active_slice] * dt
        self.positions_y[active_slice] += self.velocities_y[active_slice] * dt
        self.positions_z[active_slice] += self.velocities_z[active_slice] * dt
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_physics_opt_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics optimization queries."""
        response = """Physics simulation optimization focuses on computational efficiency:

**Physics Optimization Strategies:**
1. **Spatial Partitioning**: Use octrees, grids, or BVH for collision detection
2. **Solver Optimization**: Tune iteration counts and convergence criteria
3. **Level of Detail**: Simplify physics for distant or less important objects
4. **Temporal Coherence**: Exploit frame-to-frame similarity
5. **Parallel Processing**: Distribute physics calculations across cores/GPU"""

        suggestions = [
            "Implement broad-phase collision detection with spatial partitioning",
            "Use adaptive time stepping for stability vs performance trade-offs",
            "Apply physics LOD based on distance or importance",
            "Optimize constraint solver iteration counts",
            "Consider using simplified physics for non-critical objects"
        ]
        
        code_snippets = [
            """# Spatial partitioning for collision optimization
class SpatialGrid:
    def __init__(self, world_size, cell_size):
        self.cell_size = cell_size
        self.grid_size = int(world_size / cell_size)
        self.grid = {}
        
    def insert_object(self, obj, position):
        cell_x = int(position.x / self.cell_size)
        cell_y = int(position.y / self.cell_size)
        cell_z = int(position.z / self.cell_size)
        
        cell_key = (cell_x, cell_y, cell_z)
        
        if cell_key not in self.grid:
            self.grid[cell_key] = []
        
        self.grid[cell_key].append(obj)
    
    def get_nearby_objects(self, position, radius):
        nearby = []
        cell_radius = int(radius / self.cell_size) + 1
        
        center_x = int(position.x / self.cell_size)
        center_y = int(position.y / self.cell_size)
        center_z = int(position.z / self.cell_size)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                for dz in range(-cell_radius, cell_radius + 1):
                    cell_key = (center_x + dx, center_y + dy, center_z + dz)
                    if cell_key in self.grid:
                        nearby.extend(self.grid[cell_key])
        
        return nearby
""",
            """# Adaptive physics LOD system
class PhysicsLODManager:
    def __init__(self, camera_position):
        self.camera_position = camera_position
        self.lod_distances = [10.0, 50.0, 200.0]  # LOD thresholds
        
    def update_physics_lod(self, physics_objects):
        for obj in physics_objects:
            distance = self._calculate_distance(obj.position, self.camera_position)
            
            if distance < self.lod_distances[0]:
                # High detail physics
                obj.solver_iterations = 8
                obj.collision_precision = 'high'
                obj.update_frequency = 60
            elif distance < self.lod_distances[1]:
                # Medium detail physics
                obj.solver_iterations = 4
                obj.collision_precision = 'medium'
                obj.update_frequency = 30
            elif distance < self.lod_distances[2]:
                # Low detail physics
                obj.solver_iterations = 2
                obj.collision_precision = 'low'
                obj.update_frequency = 15
            else:
                # Minimal physics or kinematic
                obj.solver_iterations = 1
                obj.collision_precision = 'minimal'
                obj.update_frequency = 5
    
    def _calculate_distance(self, pos1, pos2):
        return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)**0.5
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_rendering_opt_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for rendering optimization queries."""
        response = """Rendering optimization ensures smooth visual performance:

**Rendering Optimization Techniques:**
1. **Culling**: Frustum culling, occlusion culling, backface culling
2. **Level of Detail**: Reduce geometry complexity based on distance
3. **Batching**: Minimize draw calls by combining similar objects
4. **Texture Optimization**: Compression, mipmapping, atlasing
5. **Shader Optimization**: Reduce complexity, use appropriate precision"""

        suggestions = [
            "Implement frustum culling to avoid rendering off-screen objects",
            "Use instanced rendering for many similar objects",
            "Optimize texture sizes and use compression formats",
            "Implement dynamic LOD based on screen size",
            "Profile GPU performance to identify bottlenecks"
        ]
        
        code_snippets = [
            """// Frustum culling implementation
class FrustumCuller {
    constructor(camera) {
        this.camera = camera;
        this.frustum = new THREE.Frustum();
        this.matrix = new THREE.Matrix4();
    }
    
    updateFrustum() {
        this.matrix.multiplyMatrices(
            this.camera.projectionMatrix, 
            this.camera.matrixWorldInverse
        );
        this.frustum.setFromProjectionMatrix(this.matrix);
    }
    
    cullObjects(objects) {
        this.updateFrustum();
        const visibleObjects = [];
        
        for (const obj of objects) {
            if (this.frustum.intersectsObject(obj)) {
                visibleObjects.push(obj);
            }
        }
        
        return visibleObjects;
    }
}

// Usage in render loop
const culler = new FrustumCuller(camera);
const visibleObjects = culler.cullObjects(allObjects);
// Only render visible objects
""",
            """// Dynamic LOD system for rendering
class RenderLODManager {
    constructor() {
        this.lodLevels = [
            { distance: 50, geometryDetail: 'high', textureSize: 1024 },
            { distance: 200, geometryDetail: 'medium', textureSize: 512 },
            { distance: 500, geometryDetail: 'low', textureSize: 256 },
            { distance: Infinity, geometryDetail: 'minimal', textureSize: 128 }
        ];
    }
    
    updateLOD(objects, cameraPosition) {
        objects.forEach(obj => {
            const distance = obj.position.distanceTo(cameraPosition);
            const lodLevel = this.getLODLevel(distance);
            
            // Switch geometry based on distance
            if (obj.currentLOD !== lodLevel.geometryDetail) {
                this.switchGeometry(obj, lodLevel.geometryDetail);
                obj.currentLOD = lodLevel.geometryDetail;
            }
            
            // Adjust texture resolution
            this.adjustTextureResolution(obj, lodLevel.textureSize);
        });
    }
    
    getLODLevel(distance) {
        return this.lodLevels.find(level => distance < level.distance);
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_profiling_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for profiling queries."""
        response = """Performance profiling helps identify optimization opportunities:

**Profiling Tools and Techniques:**
1. **Browser DevTools**: Performance tab, memory profiler
2. **Python Profilers**: cProfile, line_profiler, memory_profiler
3. **GPU Profilers**: NVIDIA Nsight, AMD Radeon GPU Profiler
4. **Custom Profilers**: Application-specific timing and metrics
5. **Continuous Monitoring**: Real-time performance tracking"""

        suggestions = [
            "Use browser DevTools to profile JavaScript performance",
            "Implement custom timing for critical code sections",
            "Profile memory allocation patterns to identify leaks",
            "Use statistical profiling for production monitoring",
            "Set up automated performance regression testing"
        ]
        
        code_snippets = [
            """# Custom performance profiler
class PerformanceProfiler:
    def __init__(self):
        self.timings = {}
        self.counters = {}
        self.memory_snapshots = []
    
    def start_timer(self, name):
        self.timings[name] = {'start': time.perf_counter()}
    
    def end_timer(self, name):
        if name in self.timings:
            elapsed = time.perf_counter() - self.timings[name]['start']
            if 'total' not in self.timings[name]:
                self.timings[name]['total'] = 0
                self.timings[name]['count'] = 0
            
            self.timings[name]['total'] += elapsed
            self.timings[name]['count'] += 1
            self.timings[name]['average'] = self.timings[name]['total'] / self.timings[name]['count']
    
    def increment_counter(self, name, value=1):
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += value
    
    def take_memory_snapshot(self):
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        self.memory_snapshots.append({
            'timestamp': time.time(),
            'rss': memory_info.rss,
            'vms': memory_info.vms
        })
    
    def get_report(self):
        return {
            'timings': self.timings,
            'counters': self.counters,
            'memory_usage': self.memory_snapshots[-10:]  # Last 10 snapshots
        }

# Usage
profiler = PerformanceProfiler()

profiler.start_timer('physics_update')
# ... physics code ...
profiler.end_timer('physics_update')

profiler.increment_counter('particles_processed', num_particles)
""",
            """// JavaScript performance monitoring
class JSPerformanceMonitor {
    constructor() {
        this.metrics = {
            frameTime: [],
            renderTime: [],
            physicsTime: [],
            memoryUsage: []
        };
        this.maxSamples = 1000;
    }
    
    startFrame() {
        this.frameStart = performance.now();
    }
    
    endFrame() {
        const frameTime = performance.now() - this.frameStart;
        this.addMetric('frameTime', frameTime);
        
        // Monitor memory usage
        if (performance.memory) {
            this.addMetric('memoryUsage', performance.memory.usedJSHeapSize);
        }
    }
    
    timeFunction(name, func) {
        const start = performance.now();
        const result = func();
        const elapsed = performance.now() - start;
        this.addMetric(name, elapsed);
        return result;
    }
    
    addMetric(name, value) {
        if (!this.metrics[name]) {
            this.metrics[name] = [];
        }
        
        this.metrics[name].push(value);
        
        // Keep only recent samples
        if (this.metrics[name].length > this.maxSamples) {
            this.metrics[name].shift();
        }
    }
    
    getAverages() {
        const averages = {};
        for (const [name, values] of Object.entries(this.metrics)) {
            if (values.length > 0) {
                averages[name] = values.reduce((a, b) => a + b) / values.length;
            }
        }
        return averages;
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_general_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate general optimization response."""
        response = """I'm here to help optimize performance across your simulation system. I can assist with:

- GPU optimization and CUDA programming
- Memory management and allocation strategies
- Physics simulation performance tuning
- Rendering and graphics optimization
- Algorithm optimization and complexity analysis
- Performance profiling and benchmarking
- Parallel processing and threading

What specific performance aspect would you like to optimize?"""

        suggestions = [
            "Ask about GPU optimization for physics simulations",
            "Get help with memory management strategies",
            "Learn about performance profiling techniques",
            "Understand rendering optimization methods"
        ]
        
        code_snippets = [
            """# General performance optimization template
class PerformanceOptimizer:
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.memory_manager = MemoryManager()
        self.gpu_manager = GPUManager()
    
    def optimize_simulation_loop(self, simulation):
        # Profile current performance
        self.profiler.start_timer('simulation_step')
        
        # Optimize memory usage
        self.memory_manager.cleanup_unused_objects()
        
        # Optimize GPU utilization
        if self.gpu_manager.is_available():
            simulation.use_gpu_acceleration()
        
        # Run simulation step
        simulation.step()
        
        self.profiler.end_timer('simulation_step')
        
        # Analyze and suggest optimizations
        return self.analyze_performance()
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _calculate_confidence(self, query: str, context: AgentContext, query_type: str) -> float:
        """Calculate confidence score for the response."""
        base_confidence = self.can_handle_query(query, context)
        
        # Boost confidence for specific query types we handle well
        type_boost = {
            'gpu_optimization': 0.3,
            'memory_optimization': 0.25,
            'physics_optimization': 0.2,
            'rendering_optimization': 0.2,
            'algorithmic_optimization': 0.15,
            'profiling': 0.25,
            'parallelization': 0.2,
            'data_optimization': 0.15,
            'general': 0.1
        }
        
        confidence = min(1.0, base_confidence + type_boost.get(query_type, 0.0))
        
        # Reduce confidence if context suggests non-performance domain
        if context.current_code:
            code_lower = context.current_code.lower()
            if any(term in code_lower for term in ['ui', 'frontend', 'styling', 'css']):
                confidence *= 0.6
                
        return confidence
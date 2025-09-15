"""
Debug Agent specialized for error analysis and troubleshooting.
"""

import re
import logging
from typing import Dict, Any, List, Set
from datetime import datetime

from .base import BaseAgent, AgentContext, AgentResponse, AgentCapability

logger = logging.getLogger(__name__)


class DebugAgent(BaseAgent):
    """
    Specialized AI agent for debugging and error analysis.
    
    Provides expertise in physics simulation debugging, error pattern recognition,
    code quality analysis, and troubleshooting assistance.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id)
        self.capabilities = {
            AgentCapability.CODE_DEBUGGING,
            AgentCapability.ERROR_ANALYSIS,
            AgentCapability.PHYSICS_DEBUGGING
        }
        
        # Debug-specific knowledge patterns
        self.debug_keywords = {
            'debug', 'error', 'bug', 'issue', 'problem', 'fail', 'crash',
            'exception', 'traceback', 'stack trace', 'not working', 'broken',
            'fix', 'troubleshoot', 'diagnose', 'analyze', 'investigate'
        }
        
        self.error_patterns = [
            r'error', r'exception', r'traceback', r'stack trace',
            r'null pointer', r'segmentation fault', r'memory leak',
            r'assertion failed', r'runtime error', r'syntax error'
        ]
        
        # Common physics simulation errors
        self.physics_error_patterns = {
            'instability': ['unstable', 'exploding', 'jittering', 'oscillating'],
            'collision': ['falling through', 'no collision', 'stuck', 'penetration'],
            'performance': ['slow', 'lag', 'fps drop', 'freezing'],
            'initialization': ['not initializing', 'setup failed', 'null reference'],
            'parameters': ['wrong behavior', 'unrealistic', 'too fast', 'too slow']
        }
        
    @property
    def name(self) -> str:
        return "Debug & Error Analysis Expert"
        
    @property
    def description(self) -> str:
        return ("Specialized in debugging, error analysis, physics simulation "
                "troubleshooting, and code quality assessment.")
        
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """Determine if this agent can handle the debug-related query."""
        query_lower = query.lower()
        
        # Check for debug keywords (count matches, not percentage)
        debug_matches = sum(1 for keyword in self.debug_keywords 
                           if keyword in query_lower)
        debug_score = min(1.0, debug_matches * 0.2)  # Each match adds 0.2
        
        # Check for error patterns
        error_matches = sum(1 for pattern in self.error_patterns 
                           if re.search(pattern, query_lower))
        error_score = min(1.0, error_matches * 0.3)  # Each error match adds 0.3
        
        # Check for physics-specific error patterns
        physics_error_score = 0.0
        for category, patterns in self.physics_error_patterns.items():
            category_matches = sum(1 for pattern in patterns 
                                 if pattern in query_lower)
            physics_error_score += min(0.3, category_matches * 0.15)  # Max 0.3 per category
        
        # Check context for error-related code or messages
        context_score = 0.0
        if context.current_code:
            code_lower = context.current_code.lower()
            context_matches = sum(1 for keyword in self.debug_keywords 
                                if keyword in code_lower)
            context_score = min(0.3, context_matches * 0.1)  # Max 0.3 from context
            
        # Combine scores
        total_score = debug_score + error_score + physics_error_score + context_score
        
        # Boost score for explicit debug requests
        if any(term in query_lower for term in ['debug', 'error', 'fix', 'problem', 'crash', 'bug', 'troubleshoot']):
            total_score = min(1.0, total_score + 0.4)
            
        return min(1.0, total_score)
        
    async def process_query(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a debug-related query and provide specialized assistance."""
        start_time = datetime.utcnow()
        
        try:
            # Analyze query type and error category
            query_type = self._analyze_query_type(query)
            error_category = self._categorize_error(query, context)
            
            # Generate response based on query type and error category
            response_text, suggestions, code_snippets = await self._generate_debug_response(
                query, query_type, error_category, context
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
                context={'query_type': query_type, 'error_category': error_category},
                suggestions=suggestions,
                code_snippets=code_snippets,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Debug agent query processing failed: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                response=f"I encountered an error processing your debug query: {str(e)}",
                confidence_score=0.1,
                response_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
    def _analyze_query_type(self, query: str) -> str:
        """Analyze the type of debug query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['physics', 'simulation', 'physx']):
            return 'physics_debug'
        elif any(term in query_lower for term in ['crash', 'segfault', 'exception']):
            return 'crash_debug'
        elif any(term in query_lower for term in ['performance', 'slow', 'lag']):
            return 'performance_debug'
        elif any(term in query_lower for term in ['memory', 'leak', 'allocation']):
            return 'memory_debug'
        elif any(term in query_lower for term in ['render', 'graphics', 'visual']):
            return 'rendering_debug'
        elif any(term in query_lower for term in ['logic', 'algorithm', 'behavior']):
            return 'logic_debug'
        elif any(term in query_lower for term in ['syntax', 'compile', 'build']):
            return 'compilation_debug'
        else:
            return 'general_debug'
            
    def _categorize_error(self, query: str, context: AgentContext) -> str:
        """Categorize the type of error based on query and context."""
        query_lower = query.lower()
        
        # Check physics-specific error patterns
        for category, patterns in self.physics_error_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return f'physics_{category}'
                
        # Check for common error types
        if any(term in query_lower for term in ['null', 'undefined', 'none']):
            return 'null_reference'
        elif any(term in query_lower for term in ['index', 'bounds', 'range']):
            return 'index_error'
        elif any(term in query_lower for term in ['type', 'cast', 'conversion']):
            return 'type_error'
        elif any(term in query_lower for term in ['timeout', 'hang', 'freeze']):
            return 'timeout_error'
        else:
            return 'unknown'
            
    async def _generate_debug_response(
        self, 
        query: str, 
        query_type: str, 
        error_category: str,
        context: AgentContext
    ) -> tuple[str, List[str], List[str]]:
        """Generate debug-specific response, suggestions, and code snippets."""
        
        if query_type == 'physics_debug':
            return self._generate_physics_debug_response(query, error_category, context)
        elif query_type == 'crash_debug':
            return self._generate_crash_debug_response(query, error_category, context)
        elif query_type == 'performance_debug':
            return self._generate_performance_debug_response(query, error_category, context)
        elif query_type == 'memory_debug':
            return self._generate_memory_debug_response(query, error_category, context)
        elif query_type == 'rendering_debug':
            return self._generate_rendering_debug_response(query, error_category, context)
        elif query_type == 'logic_debug':
            return self._generate_logic_debug_response(query, error_category, context)
        elif query_type == 'compilation_debug':
            return self._generate_compilation_debug_response(query, error_category, context)
        else:
            return self._generate_general_debug_response(query, error_category, context)
            
    def _generate_physics_debug_response(self, query: str, error_category: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics debugging queries."""
        
        if 'instability' in error_category:
            response = """Physics simulation instability is often caused by:

1. **Time Step Issues**: Too large time steps can cause instability
2. **Solver Settings**: Insufficient solver iterations
3. **Mass Ratios**: Extreme mass differences between objects
4. **Constraint Violations**: Over-constrained or conflicting constraints
5. **Numerical Precision**: Floating-point precision issues"""

            suggestions = [
                "Reduce the simulation time step (try 1/120 or 1/240 seconds)",
                "Increase solver iteration counts for position and velocity",
                "Check for extreme mass ratios between interacting objects",
                "Enable continuous collision detection (CCD) for fast objects",
                "Verify constraint setup and remove conflicting constraints"
            ]
            
            code_snippets = [
                """# Fix simulation instability
# Reduce time step
dt = 1.0 / 120.0  # Instead of 1/60

# Increase solver iterations
scene.set_solver_iteration_counts(8, 4)  # position, velocity

# Check mass ratios
def validate_mass_ratios(bodies):
    masses = [body.get_mass() for body in bodies]
    max_mass = max(masses)
    min_mass = min(masses)
    
    if max_mass / min_mass > 100:
        print(f"Warning: Large mass ratio detected: {max_mass/min_mass:.1f}")
        return False
    return True

# Enable CCD for fast objects
for body in fast_moving_bodies:
    body.set_rigid_body_flag(px.RigidBodyFlag.ENABLE_CCD, True)
""",
                """# Stabilization techniques
def stabilize_simulation(scene, bodies):
    # Add damping to reduce oscillations
    for body in bodies:
        body.set_linear_damping(0.1)
        body.set_angular_damping(0.05)
    
    # Limit maximum velocities
    max_linear_vel = 50.0
    max_angular_vel = 10.0
    
    for body in bodies:
        body.set_max_linear_velocity(max_linear_vel)
        body.set_max_angular_velocity(max_angular_vel)
    
    # Use adaptive force for stability
    scene_desc.flags |= px.SceneFlag.ADAPTIVE_FORCE
"""
            ]
            
        elif 'collision' in error_category:
            response = """Collision detection issues can be resolved by:

1. **Shape Mismatch**: Visual and collision shapes don't match
2. **Scale Issues**: Incorrect scaling of collision shapes
3. **CCD Settings**: Continuous collision detection not enabled
4. **Collision Filtering**: Objects filtered out from collision
5. **Thickness**: Objects too thin for reliable collision detection"""

            suggestions = [
                "Verify collision shapes match visual geometry",
                "Enable continuous collision detection for fast objects",
                "Check collision filtering and layer settings",
                "Increase minimum thickness for thin objects",
                "Use convex decomposition for complex shapes"
            ]
            
            code_snippets = [
                """# Debug collision detection
def debug_collision_shapes(scene):
    # Enable collision visualization
    scene.set_visualization_parameter(px.VisualizationParameter.SCALE, 1.0)
    scene.set_visualization_parameter(px.VisualizationParameter.COLLISION_SHAPES, 1.0)
    scene.set_visualization_parameter(px.VisualizationParameter.CONTACT_POINT, 1.0)
    
    # Check for shape-visual mismatch
    for actor in scene.get_actors():
        shapes = actor.get_shapes()
        for shape in shapes:
            bounds = shape.get_local_bounds()
            print(f"Actor {actor}: Shape bounds = {bounds}")

# Fix thin object collision
def fix_thin_objects(thin_objects, min_thickness=0.1):
    for obj in thin_objects:
        bounds = obj.get_bounds()
        if any(dim < min_thickness for dim in [bounds.x, bounds.y, bounds.z]):
            # Increase thickness or use different collision shape
            obj.use_box_collision(min_thickness, min_thickness, min_thickness)
"""
            ]
            
        else:
            response = """General physics debugging approach:

1. **Enable Debug Visualization**: Show collision shapes, contact points
2. **Check Initialization**: Verify all objects are properly set up
3. **Validate Parameters**: Ensure realistic physics parameters
4. **Monitor Performance**: Check for performance bottlenecks
5. **Step-by-Step Testing**: Isolate the problematic component"""

            suggestions = [
                "Enable PhysX Visual Debugger for detailed inspection",
                "Add logging to track object states over time",
                "Test with simplified scenes to isolate issues",
                "Verify physics world initialization parameters",
                "Check for NaN or infinite values in calculations"
            ]
            
            code_snippets = [
                """# Comprehensive physics debugging
class PhysicsDebugger:
    def __init__(self, scene):
        self.scene = scene
        self.frame_count = 0
        self.debug_log = []
    
    def enable_debug_visualization(self):
        # Enable all debug visualizations
        viz_params = [
            px.VisualizationParameter.SCALE,
            px.VisualizationParameter.WORLD_AXES,
            px.VisualizationParameter.BODY_AXES,
            px.VisualizationParameter.COLLISION_SHAPES,
            px.VisualizationParameter.CONTACT_POINT,
            px.VisualizationParameter.CONTACT_NORMAL,
            px.VisualizationParameter.JOINT_LOCAL_FRAMES,
            px.VisualizationParameter.JOINT_LIMITS
        ]
        
        for param in viz_params:
            self.scene.set_visualization_parameter(param, 1.0)
    
    def validate_scene_state(self):
        issues = []
        
        for actor in self.scene.get_actors():
            # Check for NaN values
            pos = actor.get_global_pose().p
            if any(math.isnan(x) for x in [pos.x, pos.y, pos.z]):
                issues.append(f"NaN position detected in actor {actor}")
            
            # Check for extreme velocities
            if hasattr(actor, 'get_linear_velocity'):
                vel = actor.get_linear_velocity()
                if vel.magnitude() > 1000:
                    issues.append(f"Extreme velocity in actor {actor}: {vel.magnitude()}")
        
        return issues
"""
            ]
            
        return response, suggestions, code_snippets
        
    def _generate_crash_debug_response(self, query: str, error_category: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for crash debugging queries."""
        response = """Crash debugging requires systematic analysis:

1. **Stack Trace Analysis**: Identify the exact location of the crash
2. **Memory Issues**: Check for buffer overflows, null pointers
3. **Resource Management**: Verify proper cleanup and initialization
4. **Threading Issues**: Look for race conditions and synchronization
5. **External Dependencies**: Check library versions and compatibility"""

        suggestions = [
            "Use a debugger (GDB, Visual Studio Debugger) to get detailed stack traces",
            "Enable core dumps for post-mortem analysis",
            "Add null pointer checks before dereferencing",
            "Verify all resources are properly initialized before use",
            "Check for memory corruption using tools like Valgrind or AddressSanitizer"
        ]
        
        code_snippets = [
            """# Crash prevention and debugging
import traceback
import sys

class CrashHandler:
    def __init__(self):
        self.crash_log = []
        sys.excepthook = self.handle_exception
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        crash_info = {
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': traceback.format_tb(exc_traceback),
            'timestamp': datetime.now().isoformat()
        }
        
        self.crash_log.append(crash_info)
        self.log_crash(crash_info)
        
        # Try to save state before crashing
        self.emergency_save()
    
    def log_crash(self, crash_info):
        with open('crash_log.txt', 'a') as f:
            f.write(f"CRASH: {crash_info['timestamp']}\\n")
            f.write(f"Type: {crash_info['type']}\\n")
            f.write(f"Message: {crash_info['message']}\\n")
            f.write("Traceback:\\n")
            for line in crash_info['traceback']:
                f.write(f"  {line}")
            f.write("\\n" + "="*50 + "\\n")

# Safe pointer dereferencing
def safe_access(obj, attr, default=None):
    try:
        return getattr(obj, attr, default) if obj is not None else default
    except AttributeError:
        return default

# Example usage
velocity = safe_access(physics_body, 'get_linear_velocity', lambda: Vector3(0,0,0))()
""",
            """// C++ crash debugging helpers
#include <csignal>
#include <execinfo.h>

class CrashHandler {
public:
    static void install() {
        signal(SIGSEGV, handleCrash);
        signal(SIGABRT, handleCrash);
        signal(SIGFPE, handleCrash);
    }
    
private:
    static void handleCrash(int sig) {
        void *array[10];
        size_t size = backtrace(array, 10);
        
        fprintf(stderr, "Error: signal %d:\\n", sig);
        backtrace_symbols_fd(array, size, STDERR_FILENO);
        
        // Try to save critical data
        emergencySave();
        
        exit(1);
    }
    
    static void emergencySave() {
        // Save simulation state, user data, etc.
        try {
            saveSimulationState("emergency_save.dat");
        } catch (...) {
            // Even emergency save failed
        }
    }
};

// Safe pointer usage
template<typename T>
bool safeCall(T* ptr, std::function<void(T*)> func) {
    if (ptr != nullptr) {
        try {
            func(ptr);
            return true;
        } catch (...) {
            return false;
        }
    }
    return false;
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_general_debug_response(self, query: str, error_category: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate general debug response."""
        response = """I'm here to help debug your simulation issues. I can assist with:

- Physics simulation debugging and troubleshooting
- Crash analysis and error investigation
- Performance bottleneck identification
- Memory leak detection and analysis
- Code quality assessment and improvement
- Error pattern recognition and solutions

What specific issue are you experiencing? Please provide:
- Error messages or symptoms
- Code snippets if available
- Steps to reproduce the problem
- Expected vs actual behavior"""

        suggestions = [
            "Provide detailed error messages and stack traces",
            "Share the specific code that's causing issues",
            "Describe the expected behavior vs what's happening",
            "Include information about when the problem started",
            "Mention any recent changes to the code or environment"
        ]
        
        code_snippets = [
            """# General debugging utilities
class DebugUtils:
    @staticmethod
    def log_function_calls(func):
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                print(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                print(f"{func.__name__} raised exception: {e}")
                raise
        return wrapper
    
    @staticmethod
    def validate_inputs(**validators):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Validate inputs before function execution
                for param, validator in validators.items():
                    if param in kwargs:
                        if not validator(kwargs[param]):
                            raise ValueError(f"Invalid {param}: {kwargs[param]}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def safe_execute(func, *args, **kwargs):
        try:
            return func(*args, **kwargs), None
        except Exception as e:
            return None, e

# Usage examples
@DebugUtils.log_function_calls
@DebugUtils.validate_inputs(
    mass=lambda x: x > 0,
    position=lambda x: len(x) == 3
)
def create_physics_object(mass, position):
    # Function implementation
    pass
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _calculate_confidence(self, query: str, context: AgentContext, query_type: str) -> float:
        """Calculate confidence score for the response."""
        base_confidence = self.can_handle_query(query, context)
        
        # Boost confidence for specific query types we handle well
        type_boost = {
            'physics_debug': 0.3,
            'crash_debug': 0.25,
            'performance_debug': 0.2,
            'memory_debug': 0.2,
            'rendering_debug': 0.15,
            'logic_debug': 0.2,
            'compilation_debug': 0.15,
            'general_debug': 0.1
        }
        
        confidence = min(1.0, base_confidence + type_boost.get(query_type, 0.0))
        
        # Boost confidence if error details are provided in context
        if context.current_code and any(term in context.current_code.lower() 
                                       for term in ['error', 'exception', 'traceback']):
            confidence = min(1.0, confidence + 0.2)
            
        return confidence
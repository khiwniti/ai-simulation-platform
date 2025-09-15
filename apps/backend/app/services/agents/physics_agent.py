"""
Physics Agent specialized for NVIDIA PhysX AI assistance.
"""

import re
import logging
from typing import Dict, Any, List, Set
from datetime import datetime

from .base import BaseAgent, AgentContext, AgentResponse, AgentCapability

logger = logging.getLogger(__name__)


class PhysicsAgent(BaseAgent):
    """
    Specialized AI agent for physics simulation assistance using NVIDIA PhysX AI.
    
    Provides expertise in physics modeling, PhysX API guidance, simulation setup,
    and physics parameter optimization.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id)
        self.capabilities = {
            AgentCapability.PHYSICS_SIMULATION,
            AgentCapability.PHYSICS_DEBUGGING,
            AgentCapability.PARAMETER_TUNING,
            AgentCapability.EQUATION_ASSISTANCE
        }
        
        # Physics-specific knowledge patterns
        self.physics_keywords = {
            'physx', 'physics', 'simulation', 'rigid body', 'collision',
            'dynamics', 'kinematics', 'force', 'velocity', 'acceleration',
            'mass', 'gravity', 'friction', 'restitution', 'constraint',
            'joint', 'material', 'scene', 'actor', 'shape', 'geometry'
        }
        
        self.physx_api_patterns = [
            r'PxRigidDynamic',
            r'PxRigidStatic', 
            r'PxScene',
            r'PxPhysics',
            r'PxMaterial',
            r'PxShape',
            r'PxTransform',
            r'PxVec3',
            r'PxQuat'
        ]
        
    @property
    def name(self) -> str:
        return "Physics Simulation Expert"
        
    @property
    def description(self) -> str:
        return ("Specialized in NVIDIA PhysX AI physics simulations, "
                "physics modeling, parameter optimization, and debugging.")
        
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """Determine if this agent can handle the physics-related query."""
        query_lower = query.lower()
        
        # Check for physics keywords (count matches, not percentage)
        physics_matches = sum(1 for keyword in self.physics_keywords 
                            if keyword in query_lower)
        physics_score = min(1.0, physics_matches * 0.2)  # Each match adds 0.2
        
        # Check for PhysX API patterns
        api_matches = sum(1 for pattern in self.physx_api_patterns 
                         if re.search(pattern, query, re.IGNORECASE))
        api_score = min(1.0, api_matches * 0.3)  # Each API match adds 0.3
        
        # Check context for physics-related code
        context_score = 0.0
        if context.current_code:
            code_lower = context.current_code.lower()
            context_matches = sum(1 for keyword in self.physics_keywords 
                                if keyword in code_lower)
            context_score = min(0.3, context_matches * 0.1)  # Max 0.3 from context
            
        # Combine scores
        total_score = physics_score + api_score + context_score
        
        # Boost score for explicit physics requests
        if any(term in query_lower for term in ['physics', 'physx', 'simulation', 'rigid body']):
            total_score = min(1.0, total_score + 0.4)
            
        return min(1.0, total_score)
        
    async def process_query(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a physics-related query and provide specialized assistance."""
        start_time = datetime.utcnow()
        
        try:
            # Analyze query type
            query_type = self._analyze_query_type(query)
            
            # Generate response based on query type
            response_text, suggestions, code_snippets = await self._generate_physics_response(
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
            logger.error(f"Physics agent query processing failed: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                response=f"I encountered an error processing your physics query: {str(e)}",
                confidence_score=0.1,
                response_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
    def _analyze_query_type(self, query: str) -> str:
        """Analyze the type of physics query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['setup', 'initialize', 'create scene']):
            return 'setup'
        elif any(term in query_lower for term in ['debug', 'error', 'not working', 'problem']):
            return 'debug'
        elif any(term in query_lower for term in ['optimize', 'performance', 'faster', 'improve']):
            return 'optimization'
        elif any(term in query_lower for term in ['parameter', 'tune', 'adjust', 'configure']):
            return 'parameter_tuning'
        elif any(term in query_lower for term in ['equation', 'formula', 'math', 'calculate']):
            return 'equation'
        elif any(term in query_lower for term in ['collision', 'contact', 'hit']):
            return 'collision'
        elif any(term in query_lower for term in ['rigid body', 'dynamics', 'movement']):
            return 'dynamics'
        else:
            return 'general'
            
    async def _generate_physics_response(
        self, 
        query: str, 
        query_type: str, 
        context: AgentContext
    ) -> tuple[str, List[str], List[str]]:
        """Generate physics-specific response, suggestions, and code snippets."""
        
        if query_type == 'setup':
            return self._generate_setup_response(query, context)
        elif query_type == 'debug':
            return self._generate_debug_response(query, context)
        elif query_type == 'optimization':
            return self._generate_optimization_response(query, context)
        elif query_type == 'parameter_tuning':
            return self._generate_parameter_response(query, context)
        elif query_type == 'equation':
            return self._generate_equation_response(query, context)
        elif query_type == 'collision':
            return self._generate_collision_response(query, context)
        elif query_type == 'dynamics':
            return self._generate_dynamics_response(query, context)
        else:
            return self._generate_general_response(query, context)
            
    def _generate_setup_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics setup queries."""
        response = """I can help you set up a PhysX physics simulation. Here's a basic setup structure:

1. Initialize the PhysX foundation and physics system
2. Create a physics scene with appropriate settings
3. Set up materials with friction and restitution properties
4. Create rigid bodies (static and dynamic actors)
5. Configure collision shapes and geometries"""

        suggestions = [
            "Start with a simple scene containing a ground plane and a falling box",
            "Use appropriate time stepping for stable simulation",
            "Configure gravity and scene bounds",
            "Set up collision filtering if needed"
        ]
        
        code_snippets = [
            """# Basic PhysX scene setup
import physx as px

# Initialize foundation and physics
foundation = px.create_foundation()
physics = px.create_physics(foundation)

# Create scene
scene_desc = px.SceneDesc()
scene_desc.gravity = px.Vec3(0.0, -9.81, 0.0)
scene = physics.create_scene(scene_desc)

# Create default material
material = physics.create_material(0.5, 0.5, 0.6)  # friction, friction, restitution
""",
            """# Create ground plane
ground_geometry = px.create_plane()
ground = physics.create_rigid_static(px.Transform(px.Vec3(0, 0, 0)))
ground.create_exclusive_shape(ground_geometry, material)
scene.add_actor(ground)

# Create dynamic box
box_geometry = px.create_box(1.0, 1.0, 1.0)
box = physics.create_rigid_dynamic(px.Transform(px.Vec3(0, 10, 0)))
box.create_exclusive_shape(box_geometry, material)
px.set_mass_and_update_inertia(box, 1.0)
scene.add_actor(box)"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_debug_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics debugging queries."""
        response = """I can help debug your physics simulation. Common issues include:

1. **Simulation instability**: Often caused by inappropriate time stepping or extreme forces
2. **Objects falling through geometry**: Usually collision detection or CCD issues
3. **Unrealistic behavior**: Check material properties and mass distribution
4. **Performance problems**: Review collision complexity and solver settings"""

        suggestions = [
            "Enable continuous collision detection (CCD) for fast-moving objects",
            "Check that mass and inertia values are reasonable",
            "Verify collision shapes match visual geometry",
            "Use appropriate solver iteration counts",
            "Enable physics visualization for debugging"
        ]
        
        code_snippets = [
            """# Enable physics debugging visualization
scene.set_visualization_parameter(px.VisualizationParameter.SCALE, 1.0)
scene.set_visualization_parameter(px.VisualizationParameter.COLLISION_SHAPES, 1.0)
scene.set_visualization_parameter(px.VisualizationParameter.CONTACT_POINT, 1.0)
""",
            """# Enable CCD for fast objects
rigid_body.set_rigid_body_flag(px.RigidBodyFlag.ENABLE_CCD, True)

# Adjust solver settings for stability
scene.set_solver_iteration_counts(8, 4)  # position, velocity iterations
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_optimization_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics optimization queries."""
        response = """Here are key optimization strategies for PhysX simulations:

1. **Collision Optimization**: Use simpler collision shapes where possible
2. **Solver Tuning**: Balance iteration counts with performance needs
3. **Broad Phase**: Configure appropriate broad phase algorithm
4. **GPU Acceleration**: Utilize GPU features for large-scale simulations"""

        suggestions = [
            "Use convex hulls instead of triangle meshes for dynamic objects",
            "Implement spatial partitioning for large scenes",
            "Tune solver iteration counts based on accuracy needs",
            "Consider using GPU rigid bodies for massive simulations",
            "Profile simulation bottlenecks with PhysX Visual Debugger"
        ]
        
        code_snippets = [
            """# Optimize solver settings
scene.set_solver_iteration_counts(4, 2)  # Reduce for better performance

# Use GPU acceleration
scene_desc.flags |= px.SceneFlag.ENABLE_GPU_DYNAMICS
scene_desc.gpu_max_num_partitions = 8
""",
            """# Optimize collision detection
# Use convex shapes instead of triangle meshes
convex_mesh = cooking.create_convex_mesh(vertices)
convex_geometry = px.ConvexMeshGeometry(convex_mesh)

# Enable adaptive force for better performance
scene_desc.flags |= px.SceneFlag.ADAPTIVE_FORCE
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_parameter_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for parameter tuning queries."""
        response = """Physics parameter tuning is crucial for realistic simulations. Key parameters include:

1. **Material Properties**: Friction coefficients (0.0-1.0+), restitution (0.0-1.0)
2. **Solver Settings**: Position/velocity iterations, damping values
3. **Time Stepping**: Fixed vs variable time steps, substep counts
4. **Mass Properties**: Realistic mass distribution and inertia tensors"""

        suggestions = [
            "Start with realistic material values (rubber: restitution=0.8, steel: friction=0.7)",
            "Use fixed time stepping for deterministic results",
            "Adjust damping to prevent unrealistic oscillations",
            "Scale mass values appropriately for your simulation units"
        ]
        
        code_snippets = [
            """# Material parameter examples
rubber = physics.create_material(0.7, 0.7, 0.8)  # High restitution
steel = physics.create_material(0.7, 0.7, 0.1)   # Low restitution
ice = physics.create_material(0.1, 0.1, 0.05)    # Low friction

# Apply to shapes
shape.set_materials([rubber])
""",
            """# Solver and damping parameters
scene.set_solver_iteration_counts(8, 4)

# Set damping for stability
rigid_body.set_linear_damping(0.1)
rigid_body.set_angular_damping(0.05)

# Configure time stepping
dt = 1.0 / 60.0  # 60 FPS
scene.simulate(dt)
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_equation_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics equation queries."""
        response = """I can help with physics equations and mathematical formulations:

**Basic Dynamics:**
- F = ma (Newton's second law)
- v = u + at (velocity with constant acceleration)
- s = ut + ½at² (displacement with constant acceleration)

**Rotational Dynamics:**
- τ = Iα (torque = moment of inertia × angular acceleration)
- L = Iω (angular momentum)

**Energy:**
- KE = ½mv² (kinetic energy)
- PE = mgh (gravitational potential energy)"""

        suggestions = [
            "Use conservation of energy to validate simulation results",
            "Apply impulse-momentum theorem for collision responses",
            "Consider rotational inertia for realistic spinning objects",
            "Use spring equations for elastic constraints"
        ]
        
        code_snippets = [
            """# Calculate kinetic energy for validation
def calculate_kinetic_energy(rigid_body):
    velocity = rigid_body.get_linear_velocity()
    angular_vel = rigid_body.get_angular_velocity()
    mass = rigid_body.get_mass()
    inertia = rigid_body.get_mass_space_inertia_tensor()
    
    linear_ke = 0.5 * mass * velocity.magnitude_squared()
    angular_ke = 0.5 * angular_vel.dot(inertia * angular_vel)
    
    return linear_ke + angular_ke
""",
            """# Apply impulse for collision response
def apply_collision_impulse(body1, body2, contact_point, impulse_magnitude):
    impulse_vector = contact_point.normal * impulse_magnitude
    
    body1.add_force_at_pos(impulse_vector, contact_point.position)
    body2.add_force_at_pos(-impulse_vector, contact_point.position)
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_collision_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for collision-related queries."""
        response = """Collision detection and response in PhysX involves several components:

1. **Collision Shapes**: Define the geometry for collision detection
2. **Materials**: Control friction and restitution during collisions
3. **Filtering**: Determine which objects can collide with each other
4. **Contact Modification**: Customize collision responses"""

        suggestions = [
            "Use appropriate collision shapes for performance vs accuracy trade-offs",
            "Implement collision filtering to avoid unnecessary collision checks",
            "Handle collision events with contact callbacks",
            "Consider using triggers for non-physical collision detection"
        ]
        
        code_snippets = [
            """# Set up collision filtering
def setup_collision_groups():
    # Define collision groups
    GROUP_GROUND = 1 << 0
    GROUP_DYNAMIC = 1 << 1
    GROUP_TRIGGER = 1 << 2
    
    # Ground collides with dynamic objects only
    ground_filter = px.FilterData()
    ground_filter.word0 = GROUP_GROUND
    ground_filter.word1 = GROUP_DYNAMIC
    
    return ground_filter
""",
            """# Collision event handling
class CollisionCallback(px.SimulationEventCallback):
    def on_contact(self, pair_header, pairs):
        for pair in pairs:
            if pair.events & px.PairFlag.NOTIFY_TOUCH_FOUND:
                print(f"Collision detected between {pair_header.actors[0]} and {pair_header.actors[1]}")
                
# Register callback
scene.set_simulation_event_callback(CollisionCallback())
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_dynamics_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for dynamics-related queries."""
        response = """Rigid body dynamics in PhysX covers the motion of solid objects:

1. **Linear Motion**: Position, velocity, acceleration, and forces
2. **Angular Motion**: Orientation, angular velocity, and torques
3. **Mass Properties**: Mass, center of mass, and inertia tensor
4. **Constraints**: Joints and limits that restrict motion"""

        suggestions = [
            "Set realistic mass properties for stable simulation",
            "Use appropriate integration methods for different object types",
            "Apply forces at correct points to achieve desired motion",
            "Consider using kinematic objects for controlled motion"
        ]
        
        code_snippets = [
            """# Configure rigid body dynamics
def setup_dynamic_body(physics, position, mass=1.0):
    # Create dynamic rigid body
    body = physics.create_rigid_dynamic(px.Transform(position))
    
    # Set mass properties
    px.set_mass_and_update_inertia(body, mass)
    
    # Configure dynamics properties
    body.set_linear_damping(0.1)
    body.set_angular_damping(0.05)
    body.set_max_linear_velocity(100.0)
    body.set_max_angular_velocity(50.0)
    
    return body
""",
            """# Apply forces and torques
def apply_thrust(rigid_body, thrust_force, thrust_point):
    # Apply force at specific point (creates both linear and angular motion)
    rigid_body.add_force_at_pos(thrust_force, thrust_point)
    
    # Or apply pure force/torque
    rigid_body.add_force(thrust_force)
    rigid_body.add_torque(px.Vec3(0, 10, 0))  # Spin around Y-axis
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_general_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate general physics response."""
        response = """I'm here to help with NVIDIA PhysX physics simulations. I can assist with:

- Setting up physics scenes and rigid bodies
- Debugging simulation issues and instabilities  
- Optimizing performance for large-scale simulations
- Tuning material properties and solver parameters
- Implementing collision detection and response
- Physics equations and mathematical formulations

What specific aspect of physics simulation would you like help with?"""

        suggestions = [
            "Ask about setting up a basic physics scene",
            "Get help debugging simulation problems",
            "Learn about performance optimization techniques",
            "Understand material properties and their effects"
        ]
        
        code_snippets = [
            """# Basic PhysX simulation loop
def simulate_physics(scene, dt=1.0/60.0):
    # Step the simulation
    scene.simulate(dt)
    
    # Wait for simulation to complete
    scene.fetch_results(True)
    
    # Process results (update visual representations, etc.)
    for actor in scene.get_actors():
        if actor.get_type() == px.ActorType.RIGID_DYNAMIC:
            transform = actor.get_global_pose()
            # Update visual object position/rotation
            update_visual_object(actor, transform)
"""
        ]
        
        return response, suggestions, code_snippets
        
    def _calculate_confidence(self, query: str, context: AgentContext, query_type: str) -> float:
        """Calculate confidence score for the response."""
        base_confidence = self.can_handle_query(query, context)
        
        # Boost confidence for specific query types we handle well
        type_boost = {
            'setup': 0.2,
            'debug': 0.15,
            'optimization': 0.15,
            'parameter_tuning': 0.2,
            'equation': 0.25,
            'collision': 0.2,
            'dynamics': 0.2,
            'general': 0.1
        }
        
        confidence = min(1.0, base_confidence + type_boost.get(query_type, 0.0))
        
        # Reduce confidence if context suggests non-physics domain
        if context.current_code:
            code_lower = context.current_code.lower()
            if any(term in code_lower for term in ['web', 'html', 'css', 'javascript', 'react']):
                confidence *= 0.7
                
        return confidence
"""
Visualization Agent specialized for 3D graphics and data visualization assistance.
"""

import re
import logging
from typing import Dict, Any, List, Set
from datetime import datetime

from .base import BaseAgent, AgentContext, AgentResponse, AgentCapability

logger = logging.getLogger(__name__)


class VisualizationAgent(BaseAgent):
    """
    Specialized AI agent for 3D graphics and visualization assistance.
    
    Provides expertise in Three.js, data visualization, rendering optimization,
    and interactive visualization setup for physics simulations.
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(agent_id)
        self.capabilities = {
            AgentCapability.VISUALIZATION_3D,
            AgentCapability.VISUALIZATION_PLOTS,
            AgentCapability.PERFORMANCE_OPTIMIZATION
        }
        
        # Visualization-specific knowledge patterns
        self.viz_keywords = {
            'visualization', 'render', 'plot', 'chart', 'graph', '3d', 'threejs',
            'three.js', 'webgl', 'canvas', 'scene', 'camera', 'light', 'mesh',
            'geometry', 'material', 'texture', 'animation', 'interactive',
            'matplotlib', 'plotly', 'bokeh', 'seaborn', 'visualization'
        }
        
        self.threejs_patterns = [
            r'THREE\.',
            r'Scene\(\)',
            r'PerspectiveCamera',
            r'WebGLRenderer',
            r'Mesh\(',
            r'BufferGeometry',
            r'Material',
            r'OrbitControls'
        ]
        
    @property
    def name(self) -> str:
        return "3D Visualization Expert"
        
    @property
    def description(self) -> str:
        return ("Specialized in 3D graphics, data visualization, Three.js, "
                "rendering optimization, and interactive visualization setup.")
        
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """Determine if this agent can handle the visualization-related query."""
        query_lower = query.lower()
        
        # Check for visualization keywords (count matches, not percentage)
        viz_matches = sum(1 for keyword in self.viz_keywords 
                         if keyword in query_lower)
        viz_score = min(1.0, viz_matches * 0.15)  # Each match adds 0.15
        
        # Check for Three.js API patterns
        api_matches = sum(1 for pattern in self.threejs_patterns 
                         if re.search(pattern, query, re.IGNORECASE))
        api_score = min(1.0, api_matches * 0.3)  # Each API match adds 0.3
        
        # Check context for visualization-related code
        context_score = 0.0
        if context.current_code:
            code_lower = context.current_code.lower()
            context_matches = sum(1 for keyword in self.viz_keywords 
                                if keyword in code_lower)
            context_score = min(0.3, context_matches * 0.1)  # Max 0.3 from context
            
        # Combine scores
        total_score = viz_score + api_score + context_score
        
        # Boost score for explicit visualization requests
        if any(term in query_lower for term in ['visualize', 'render', 'plot', '3d', 'chart', 'three.js', 'webgl']):
            total_score = min(1.0, total_score + 0.4)
            
        return min(1.0, total_score)
        
    async def process_query(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a visualization-related query and provide specialized assistance."""
        start_time = datetime.utcnow()
        
        try:
            # Analyze query type
            query_type = self._analyze_query_type(query)
            
            # Generate response based on query type
            response_text, suggestions, code_snippets = await self._generate_visualization_response(
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
            logger.error(f"Visualization agent query processing failed: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                response=f"I encountered an error processing your visualization query: {str(e)}",
                confidence_score=0.1,
                response_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
    def _analyze_query_type(self, query: str) -> str:
        """Analyze the type of visualization query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['setup', 'initialize', 'create scene', 'basic']):
            return 'setup'
        elif any(term in query_lower for term in ['3d', 'three.js', 'webgl', 'mesh', 'geometry']):
            return '3d_graphics'
        elif any(term in query_lower for term in ['plot', 'chart', 'graph', 'data viz', 'matplotlib']):
            return 'data_visualization'
        elif any(term in query_lower for term in ['animation', 'animate', 'timeline', 'keyframe']):
            return 'animation'
        elif any(term in query_lower for term in ['interactive', 'controls', 'mouse', 'orbit']):
            return 'interaction'
        elif any(term in query_lower for term in ['performance', 'optimize', 'fps', 'lag', 'slow']):
            return 'performance'
        elif any(term in query_lower for term in ['physics', 'simulation', 'particle', 'rigid body']):
            return 'physics_visualization'
        elif any(term in query_lower for term in ['material', 'texture', 'shader', 'lighting']):
            return 'rendering'
        else:
            return 'general'
            
    async def _generate_visualization_response(
        self, 
        query: str, 
        query_type: str, 
        context: AgentContext
    ) -> tuple[str, List[str], List[str]]:
        """Generate visualization-specific response, suggestions, and code snippets."""
        
        if query_type == 'setup':
            return self._generate_setup_response(query, context)
        elif query_type == '3d_graphics':
            return self._generate_3d_response(query, context)
        elif query_type == 'data_visualization':
            return self._generate_data_viz_response(query, context)
        elif query_type == 'animation':
            return self._generate_animation_response(query, context)
        elif query_type == 'interaction':
            return self._generate_interaction_response(query, context)
        elif query_type == 'performance':
            return self._generate_performance_response(query, context)
        elif query_type == 'physics_visualization':
            return self._generate_physics_viz_response(query, context)
        elif query_type == 'rendering':
            return self._generate_rendering_response(query, context)
        else:
            return self._generate_general_response(query, context)
            
    def _generate_setup_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for visualization setup queries."""
        response = """I can help you set up a 3D visualization system using Three.js. Here's the basic structure:

1. Create a scene to hold all 3D objects
2. Set up a camera to view the scene
3. Initialize a WebGL renderer
4. Add lighting for proper visibility
5. Create geometry and materials for objects
6. Implement an animation loop for updates"""

        suggestions = [
            "Start with a basic scene containing a cube or sphere",
            "Use PerspectiveCamera for realistic 3D viewing",
            "Add OrbitControls for interactive camera movement",
            "Include ambient and directional lighting",
            "Set up responsive canvas sizing"
        ]
        
        code_snippets = [
            """// Basic Three.js scene setup
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

// Create scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

// Create camera
const camera = new THREE.PerspectiveCamera(
    75, // field of view
    window.innerWidth / window.innerHeight, // aspect ratio
    0.1, // near clipping plane
    1000 // far clipping plane
);
camera.position.set(5, 5, 5);

// Create renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
""",
            """// Add lighting
const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(10, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Add controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_3d_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for 3D graphics queries."""
        response = """For 3D graphics in Three.js, you'll work with these key concepts:

1. **Geometry**: Defines the shape (BoxGeometry, SphereGeometry, etc.)
2. **Materials**: Controls appearance (MeshBasicMaterial, MeshStandardMaterial)
3. **Meshes**: Combines geometry and material into renderable objects
4. **Transformations**: Position, rotation, and scale of objects
5. **Groups**: Organize related objects together"""

        suggestions = [
            "Use BufferGeometry for better performance with large datasets",
            "Choose appropriate materials based on lighting needs",
            "Implement level-of-detail (LOD) for complex scenes",
            "Use instanced rendering for many similar objects",
            "Consider using GLTF models for complex geometry"
        ]
        
        code_snippets = [
            """// Create 3D objects
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ 
    color: 0x00ff00,
    metalness: 0.3,
    roughness: 0.7
});
const cube = new THREE.Mesh(geometry, material);
cube.position.set(0, 0, 0);
cube.castShadow = true;
cube.receiveShadow = true;
scene.add(cube);

// Create custom geometry
const vertices = new Float32Array([
    -1, -1, 0,
     1, -1, 0,
     1,  1, 0,
    -1,  1, 0
]);
const customGeometry = new THREE.BufferGeometry();
customGeometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
""",
            """// Transform objects
cube.position.set(x, y, z);
cube.rotation.set(rx, ry, rz);
cube.scale.set(sx, sy, sz);

// Group objects
const group = new THREE.Group();
group.add(cube);
group.add(sphere);
scene.add(group);

// Animate transformations
function animateObjects() {
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    group.position.y = Math.sin(Date.now() * 0.001) * 2;
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_data_viz_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for data visualization queries."""
        response = """For data visualization, you can use various approaches:

**2D Plotting Libraries:**
- Matplotlib: Comprehensive plotting library for Python
- Plotly: Interactive plots with web support
- D3.js: Powerful web-based visualization library

**3D Data Visualization:**
- Three.js with data-driven geometry
- Plotly 3D plots
- Custom WebGL implementations

**Integration with Physics:**
- Real-time plotting of simulation data
- 3D particle system visualization
- Interactive parameter exploration"""

        suggestions = [
            "Use Plotly for interactive physics parameter exploration",
            "Implement real-time plotting for simulation monitoring",
            "Create 3D scatter plots for multi-dimensional data",
            "Use color mapping to represent additional data dimensions",
            "Add animation to show data evolution over time"
        ]
        
        code_snippets = [
            """# Python data visualization with Plotly
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Create 3D scatter plot
fig = go.Figure(data=go.Scatter3d(
    x=x_data,
    y=y_data,
    z=z_data,
    mode='markers',
    marker=dict(
        size=5,
        color=color_data,
        colorscale='Viridis',
        showscale=True
    )
))

fig.update_layout(
    title='Physics Simulation Results',
    scene=dict(
        xaxis_title='Position X',
        yaxis_title='Position Y',
        zaxis_title='Position Z'
    )
)
fig.show()
""",
            """// Real-time data visualization with Three.js
class DataVisualizer {
    constructor(scene) {
        this.scene = scene;
        this.dataPoints = [];
        this.geometry = new THREE.BufferGeometry();
        this.material = new THREE.PointsMaterial({
            color: 0xff0000,
            size: 0.1
        });
        this.points = new THREE.Points(this.geometry, this.material);
        scene.add(this.points);
    }
    
    updateData(newData) {
        const positions = new Float32Array(newData.length * 3);
        newData.forEach((point, i) => {
            positions[i * 3] = point.x;
            positions[i * 3 + 1] = point.y;
            positions[i * 3 + 2] = point.z;
        });
        
        this.geometry.setAttribute('position', 
            new THREE.BufferAttribute(positions, 3));
        this.geometry.attributes.position.needsUpdate = true;
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_animation_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for animation queries."""
        response = """Animation in 3D visualization can be achieved through several methods:

1. **Frame-based Animation**: Update object properties each frame
2. **Tween Libraries**: Use libraries like GSAP or Tween.js for smooth transitions
3. **Keyframe Animation**: Define specific states at time intervals
4. **Physics-driven Animation**: Let physics simulation drive the motion
5. **Shader Animation**: Use GPU shaders for complex effects"""

        suggestions = [
            "Use requestAnimationFrame for smooth 60fps animation",
            "Implement easing functions for natural motion",
            "Create timeline controls for simulation playback",
            "Use morph targets for complex geometry animation",
            "Consider performance impact of animated objects"
        ]
        
        code_snippets = [
            """// Basic animation loop with timing
let lastTime = 0;
const targetFPS = 60;
const frameTime = 1000 / targetFPS;

function animate(currentTime) {
    requestAnimationFrame(animate);
    
    const deltaTime = currentTime - lastTime;
    if (deltaTime >= frameTime) {
        // Update animations
        updatePhysicsVisualization(deltaTime);
        updateCameraAnimation(deltaTime);
        
        renderer.render(scene, camera);
        lastTime = currentTime;
    }
}

function updatePhysicsVisualization(deltaTime) {
    physicsObjects.forEach(obj => {
        // Update position from physics simulation
        obj.mesh.position.copy(obj.rigidBody.position);
        obj.mesh.quaternion.copy(obj.rigidBody.quaternion);
    });
}
""",
            """// Timeline animation system
class AnimationTimeline {
    constructor() {
        this.keyframes = [];
        this.currentTime = 0;
        this.duration = 0;
        this.isPlaying = false;
    }
    
    addKeyframe(time, object, properties) {
        this.keyframes.push({ time, object, properties });
        this.duration = Math.max(this.duration, time);
    }
    
    update(deltaTime) {
        if (!this.isPlaying) return;
        
        this.currentTime += deltaTime;
        
        // Interpolate between keyframes
        this.keyframes.forEach(keyframe => {
            if (this.currentTime >= keyframe.time) {
                Object.assign(keyframe.object, keyframe.properties);
            }
        });
        
        if (this.currentTime >= this.duration) {
            this.isPlaying = false;
        }
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_interaction_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for interaction queries."""
        response = """Interactive 3D visualization enhances user engagement:

1. **Camera Controls**: OrbitControls, FlyControls, FirstPersonControls
2. **Object Selection**: Raycasting for mouse picking
3. **Drag and Drop**: Move objects in 3D space
4. **GUI Controls**: dat.GUI or custom UI for parameter adjustment
5. **Touch Support**: Mobile-friendly interaction"""

        suggestions = [
            "Implement raycasting for object selection and interaction",
            "Add visual feedback for interactive elements",
            "Use dat.GUI for real-time parameter adjustment",
            "Implement multi-touch gestures for mobile devices",
            "Add keyboard shortcuts for common actions"
        ]
        
        code_snippets = [
            """// Object selection with raycasting
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
    // Calculate mouse position in normalized device coordinates
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
    // Update raycaster
    raycaster.setFromCamera(mouse, camera);
    
    // Find intersections
    const intersects = raycaster.intersectObjects(selectableObjects);
    
    if (intersects.length > 0) {
        const selectedObject = intersects[0].object;
        onObjectSelected(selectedObject);
    }
}

window.addEventListener('click', onMouseClick);
""",
            """// Interactive parameter controls
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';

const gui = new GUI();
const params = {
    gravity: -9.81,
    friction: 0.5,
    restitution: 0.8,
    timeScale: 1.0,
    showWireframe: false
};

// Add controls
gui.add(params, 'gravity', -20, 0).onChange(updateGravity);
gui.add(params, 'friction', 0, 1).onChange(updateFriction);
gui.add(params, 'restitution', 0, 1).onChange(updateRestitution);
gui.add(params, 'timeScale', 0.1, 2.0).onChange(updateTimeScale);
gui.add(params, 'showWireframe').onChange(toggleWireframe);

function updateGravity(value) {
    physicsWorld.setGravity(new THREE.Vector3(0, value, 0));
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_performance_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for performance optimization queries."""
        response = """Performance optimization for 3D visualization is crucial for smooth experience:

1. **Geometry Optimization**: Use BufferGeometry, reduce polygon count
2. **Material Efficiency**: Minimize material switches, use texture atlases
3. **Culling**: Frustum culling, occlusion culling, distance-based LOD
4. **Instancing**: Render many similar objects efficiently
5. **GPU Utilization**: Use shaders for complex calculations"""

        suggestions = [
            "Profile performance using browser dev tools",
            "Implement object pooling for dynamic objects",
            "Use instanced rendering for particle systems",
            "Optimize texture sizes and formats",
            "Consider using Web Workers for heavy computations"
        ]
        
        code_snippets = [
            """// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.frameCount = 0;
        this.lastTime = performance.now();
        this.fps = 0;
        this.frameTime = 0;
    }
    
    update() {
        const currentTime = performance.now();
        this.frameTime = currentTime - this.lastTime;
        this.frameCount++;
        
        if (this.frameCount % 60 === 0) {
            this.fps = 1000 / this.frameTime;
            console.log(`FPS: ${this.fps.toFixed(1)}, Frame Time: ${this.frameTime.toFixed(2)}ms`);
        }
        
        this.lastTime = currentTime;
    }
}

const monitor = new PerformanceMonitor();
""",
            """// Instanced rendering for performance
const instancedGeometry = new THREE.BoxGeometry(1, 1, 1);
const instancedMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const instancedMesh = new THREE.InstancedMesh(
    instancedGeometry, 
    instancedMaterial, 
    1000 // number of instances
);

// Set transforms for each instance
const matrix = new THREE.Matrix4();
for (let i = 0; i < 1000; i++) {
    matrix.setPosition(
        Math.random() * 100 - 50,
        Math.random() * 100 - 50,
        Math.random() * 100 - 50
    );
    instancedMesh.setMatrixAt(i, matrix);
}
instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_physics_viz_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for physics visualization queries."""
        response = """Visualizing physics simulations requires synchronizing visual objects with physics bodies:

1. **Rigid Body Visualization**: Match visual meshes to physics shapes
2. **Particle Systems**: Visualize fluid or granular simulations
3. **Force Visualization**: Show forces, velocities, and accelerations
4. **Constraint Visualization**: Display joints and connections
5. **Debug Rendering**: Wireframe physics shapes for debugging"""

        suggestions = [
            "Synchronize visual transforms with physics body transforms",
            "Use particle systems for fluid and soft body visualization",
            "Implement force vector visualization for debugging",
            "Add trails to show object motion history",
            "Use color coding to represent physical properties"
        ]
        
        code_snippets = [
            """// Physics-visual synchronization
class PhysicsVisualizer {
    constructor(scene, physicsWorld) {
        this.scene = scene;
        this.physicsWorld = physicsWorld;
        this.visualBodies = new Map();
    }
    
    addRigidBody(physicsBody, geometry, material) {
        const mesh = new THREE.Mesh(geometry, material);
        this.scene.add(mesh);
        this.visualBodies.set(physicsBody, mesh);
    }
    
    update() {
        this.visualBodies.forEach((mesh, physicsBody) => {
            // Sync position and rotation
            mesh.position.copy(physicsBody.position);
            mesh.quaternion.copy(physicsBody.quaternion);
        });
    }
}
""",
            """// Force and velocity visualization
class ForceVisualizer {
    constructor(scene) {
        this.scene = scene;
        this.forceArrows = [];
    }
    
    showForce(position, force, color = 0xff0000) {
        const direction = force.clone().normalize();
        const magnitude = force.length();
        
        const arrowHelper = new THREE.ArrowHelper(
            direction,
            position,
            magnitude * 0.1, // scale factor
            color
        );
        
        this.scene.add(arrowHelper);
        this.forceArrows.push(arrowHelper);
    }
    
    clearForces() {
        this.forceArrows.forEach(arrow => {
            this.scene.remove(arrow);
        });
        this.forceArrows = [];
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_rendering_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate response for rendering queries."""
        response = """Advanced rendering techniques enhance visual quality:

1. **Materials**: PBR materials for realistic appearance
2. **Lighting**: HDR environment maps, shadow mapping
3. **Post-processing**: Bloom, SSAO, tone mapping
4. **Shaders**: Custom vertex and fragment shaders
5. **Textures**: Normal maps, roughness maps, environment maps"""

        suggestions = [
            "Use PBR materials for physically accurate rendering",
            "Implement shadow mapping for realistic lighting",
            "Add post-processing effects for enhanced visuals",
            "Use environment maps for realistic reflections",
            "Consider deferred rendering for complex scenes"
        ]
        
        code_snippets = [
            """// PBR material setup
const pbrMaterial = new THREE.MeshStandardMaterial({
    color: 0x888888,
    metalness: 0.8,
    roughness: 0.2,
    normalMap: normalTexture,
    roughnessMap: roughnessTexture,
    metalnessMap: metalnessTexture,
    envMap: environmentTexture
});

// HDR environment lighting
const pmremGenerator = new THREE.PMREMGenerator(renderer);
const envTexture = pmremGenerator.fromScene(environmentScene).texture;
scene.environment = envTexture;
""",
            """// Post-processing pipeline
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { BloomPass } from 'three/examples/jsm/postprocessing/BloomPass';
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new SSAOPass(scene, camera, width, height));
composer.addPass(new BloomPass(1.5, 25, 4, 256));

// Render with post-processing
function render() {
    composer.render();
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _generate_general_response(self, query: str, context: AgentContext) -> tuple[str, List[str], List[str]]:
        """Generate general visualization response."""
        response = """I'm here to help with 3D graphics and data visualization. I can assist with:

- Setting up Three.js scenes and 3D rendering
- Creating interactive visualizations and controls
- Optimizing performance for complex 3D scenes
- Implementing animation and timeline systems
- Visualizing physics simulation data
- Advanced rendering techniques and materials

What specific aspect of visualization would you like help with?"""

        suggestions = [
            "Ask about setting up a basic Three.js scene",
            "Get help with 3D object creation and manipulation",
            "Learn about animation and interaction techniques",
            "Understand performance optimization strategies"
        ]
        
        code_snippets = [
            """// Basic visualization template
import * as THREE from 'three';

class Visualizer {
    constructor(container) {
        this.container = container;
        this.init();
        this.animate();
    }
    
    init() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, 
            window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.container.appendChild(this.renderer.domElement);
        
        // Add basic lighting
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(5, 5, 5);
        this.scene.add(light);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }
}"""
        ]
        
        return response, suggestions, code_snippets
        
    def _calculate_confidence(self, query: str, context: AgentContext, query_type: str) -> float:
        """Calculate confidence score for the response."""
        base_confidence = self.can_handle_query(query, context)
        
        # Boost confidence for specific query types we handle well
        type_boost = {
            'setup': 0.25,
            '3d_graphics': 0.3,
            'data_visualization': 0.2,
            'animation': 0.25,
            'interaction': 0.2,
            'performance': 0.15,
            'physics_visualization': 0.3,
            'rendering': 0.2,
            'general': 0.1
        }
        
        confidence = min(1.0, base_confidence + type_boost.get(query_type, 0.0))
        
        # Reduce confidence if context suggests non-visualization domain
        if context.current_code:
            code_lower = context.current_code.lower()
            if any(term in code_lower for term in ['backend', 'database', 'sql', 'api']):
                confidence *= 0.6
                
        return confidence
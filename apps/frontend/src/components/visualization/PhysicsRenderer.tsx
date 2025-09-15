'use client';

import React, { useRef, useEffect, useCallback, useState } from 'react';
import * as THREE from 'three';
import * as CANNON from 'cannon-es';

export interface PhysicsBody {
  id: string;
  shape: 'box' | 'sphere' | 'cylinder' | 'plane';
  position: [number, number, number];
  rotation?: [number, number, number];
  velocity?: [number, number, number];
  angularVelocity?: [number, number, number];
  mass: number;
  material?: {
    friction: number;
    restitution: number;
  };
  size: [number, number, number]; // [width, height, depth] or [radius, height, _] for cylinder
  color?: number;
}

export interface PhysicsConstraint {
  id: string;
  type: 'point' | 'distance' | 'lock' | 'hinge';
  bodyA: string;
  bodyB: string;
  pivotA?: [number, number, number];
  pivotB?: [number, number, number];
  distance?: number;
}

export interface PhysicsWorldConfig {
  gravity: [number, number, number];
  timestep: number;
  iterations: number;
  broadphase: 'naive' | 'sap' | 'grid';
  solver: 'gs' | 'split';
}

interface PhysicsRendererProps {
  bodies: PhysicsBody[];
  constraints?: PhysicsConstraint[];
  worldConfig?: Partial<PhysicsWorldConfig>;
  onBodyUpdate?: (bodyId: string, position: [number, number, number], quaternion: [number, number, number, number]) => void;
  onCollision?: (bodyAId: string, bodyBId: string, contactPoint: [number, number, number]) => void;
  width?: number;
  height?: number;
  showDebug?: boolean;
  enableShadows?: boolean;
}

export const PhysicsRenderer: React.FC<PhysicsRendererProps> = ({
  bodies,
  constraints = [],
  worldConfig = {},
  onBodyUpdate,
  onCollision,
  width = 800,
  height = 600,
  showDebug = false,
  enableShadows = true
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const worldRef = useRef<CANNON.World>();
  const animationIdRef = useRef<number>();
  
  // Store physics bodies and visual meshes
  const physicsBodyRef = useRef<Map<string, CANNON.Body>>(new Map());
  const visualMeshRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const constraintRef = useRef<Map<string, CANNON.Constraint>>(new Map());

  const [isRunning, setIsRunning] = useState(false);
  const [stats, setStats] = useState({
    fps: 0,
    bodies: 0,
    contacts: 0
  });

  // Default world configuration
  const defaultWorldConfig: PhysicsWorldConfig = {
    gravity: [0, -9.81, 0],
    timestep: 1/60,
    iterations: 10,
    broadphase: 'naive',
    solver: 'gs'
  };

  const initializePhysicsWorld = useCallback(() => {
    const config = { ...defaultWorldConfig, ...worldConfig };
    
    const world = new CANNON.World({
      gravity: new CANNON.Vec3(...config.gravity),
      broadphase: new CANNON.NaiveBroadphase(),
      solver: new CANNON.GSSolver()
    });

    // Configure solver
    world.solver.iterations = config.iterations;
    world.allowSleep = true;

    // Add contact material
    const defaultMaterial = new CANNON.Material('default');
    const defaultContactMaterial = new CANNON.ContactMaterial(defaultMaterial, defaultMaterial, {
      friction: 0.4,
      restitution: 0.3
    });
    world.addContactMaterial(defaultContactMaterial);

    // Collision detection
    world.addEventListener('collide', (event: any) => {
      if (onCollision) {
        const bodyA = event.target as CANNON.Body;
        const bodyB = event.body as CANNON.Body;
        const contact = event.contact as CANNON.ContactEquation;
        
        const bodyAId = (bodyA as any).userData?.id;
        const bodyBId = (bodyB as any).userData?.id;
        
        if (bodyAId && bodyBId) {
          onCollision(bodyAId, bodyBId, [
            contact.bi.position.x,
            contact.bi.position.y, 
            contact.bi.position.z
          ]);
        }
      }
    });

    worldRef.current = world;
    return world;
  }, [worldConfig, onCollision]);

  const initializeScene = useCallback(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB); // Sky blue
    scene.fog = new THREE.Fog(0x87CEEB, 10, 50);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(10, 10, 10);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    if (enableShadows) {
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 5);
    if (enableShadows) {
      directionalLight.castShadow = true;
      directionalLight.shadow.mapSize.width = 2048;
      directionalLight.shadow.mapSize.height = 2048;
      directionalLight.shadow.camera.near = 1;
      directionalLight.shadow.camera.far = 50;
      directionalLight.shadow.camera.left = -20;
      directionalLight.shadow.camera.right = 20;
      directionalLight.shadow.camera.top = 20;
      directionalLight.shadow.camera.bottom = -20;
    }
    scene.add(directionalLight);

    // Add ground plane if not present in bodies
    const hasGroundPlane = bodies.some(body => body.shape === 'plane');
    if (!hasGroundPlane) {
      const groundGeometry = new THREE.PlaneGeometry(50, 50);
      const groundMaterial = new THREE.MeshLambertMaterial({ 
        color: 0x90EE90,
        transparent: true,
        opacity: 0.8
      });
      const ground = new THREE.Mesh(groundGeometry, groundMaterial);
      ground.rotation.x = -Math.PI / 2;
      ground.position.y = -1;
      if (enableShadows) {
        ground.receiveShadow = true;
      }
      scene.add(ground);
    }

    // Store references
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;

    // Mount renderer
    mountRef.current.appendChild(renderer.domElement);

    // Add orbit controls
    addOrbitControls(camera, renderer);

    return { scene, camera, renderer };
  }, [bodies, width, height, enableShadows]);

  const addOrbitControls = (camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer) => {
    let isMouseDown = false;
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    let radius = camera.position.length();

    const handleMouseDown = (event: MouseEvent) => {
      isMouseDown = true;
      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleMouseMove = (event: MouseEvent) => {
      if (!isMouseDown) return;

      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;

      targetX += deltaX * 0.01;
      targetY += deltaY * 0.01;

      // Limit vertical rotation
      targetY = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, targetY));

      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleMouseUp = () => {
      isMouseDown = false;
    };

    const handleWheel = (event: WheelEvent) => {
      const scale = event.deltaY > 0 ? 1.1 : 0.9;
      radius *= scale;
      radius = Math.max(2, Math.min(50, radius));
    };

    renderer.domElement.addEventListener('mousedown', handleMouseDown);
    renderer.domElement.addEventListener('mousemove', handleMouseMove);
    renderer.domElement.addEventListener('mouseup', handleMouseUp);
    renderer.domElement.addEventListener('wheel', handleWheel);

    // Update camera position
    const updateCamera = () => {
      camera.position.x = radius * Math.cos(targetY) * Math.cos(targetX);
      camera.position.y = radius * Math.sin(targetY);
      camera.position.z = radius * Math.cos(targetY) * Math.sin(targetX);
      camera.lookAt(0, 0, 0);
    };

    (camera as any).updateControls = updateCamera;
  };

  const createPhysicsBody = useCallback((bodyDef: PhysicsBody): CANNON.Body => {
    let shape: CANNON.Shape;

    switch (bodyDef.shape) {
      case 'box':
        shape = new CANNON.Box(new CANNON.Vec3(...bodyDef.size.map(s => s / 2)));
        break;
      case 'sphere':
        shape = new CANNON.Sphere(bodyDef.size[0]);
        break;
      case 'cylinder':
        shape = new CANNON.Cylinder(bodyDef.size[0], bodyDef.size[0], bodyDef.size[1], 8);
        break;
      case 'plane':
        shape = new CANNON.Plane();
        break;
      default:
        shape = new CANNON.Box(new CANNON.Vec3(0.5, 0.5, 0.5));
    }

    const body = new CANNON.Body({
      mass: bodyDef.mass,
      shape: shape,
      position: new CANNON.Vec3(...bodyDef.position),
      material: new CANNON.Material({
        friction: bodyDef.material?.friction || 0.4,
        restitution: bodyDef.material?.restitution || 0.3
      })
    });

    if (bodyDef.rotation) {
      body.quaternion.setFromEuler(...bodyDef.rotation);
    }

    if (bodyDef.velocity) {
      body.velocity.set(...bodyDef.velocity);
    }

    if (bodyDef.angularVelocity) {
      body.angularVelocity.set(...bodyDef.angularVelocity);
    }

    // Store reference to body definition
    (body as any).userData = { id: bodyDef.id };

    return body;
  }, []);

  const createVisualMesh = useCallback((bodyDef: PhysicsBody): THREE.Mesh => {
    let geometry: THREE.BufferGeometry;

    switch (bodyDef.shape) {
      case 'box':
        geometry = new THREE.BoxGeometry(...bodyDef.size);
        break;
      case 'sphere':
        geometry = new THREE.SphereGeometry(bodyDef.size[0], 16, 16);
        break;
      case 'cylinder':
        geometry = new THREE.CylinderGeometry(bodyDef.size[0], bodyDef.size[0], bodyDef.size[1], 16);
        break;
      case 'plane':
        geometry = new THREE.PlaneGeometry(bodyDef.size[0] || 50, bodyDef.size[1] || 50);
        break;
      default:
        geometry = new THREE.BoxGeometry(1, 1, 1);
    }

    const material = new THREE.MeshLambertMaterial({ 
      color: bodyDef.color || 0x00aa00,
      transparent: bodyDef.shape === 'plane',
      opacity: bodyDef.shape === 'plane' ? 0.8 : 1.0
    });

    const mesh = new THREE.Mesh(geometry, material);
    
    if (enableShadows) {
      mesh.castShadow = true;
      mesh.receiveShadow = true;
    }

    return mesh;
  }, [enableShadows]);

  const createConstraint = useCallback((constraintDef: PhysicsConstraint): CANNON.Constraint | null => {
    const bodyA = physicsBodyRef.current.get(constraintDef.bodyA);
    const bodyB = physicsBodyRef.current.get(constraintDef.bodyB);

    if (!bodyA || !bodyB) {
      console.warn(`Cannot create constraint ${constraintDef.id}: missing bodies`);
      return null;
    }

    switch (constraintDef.type) {
      case 'point':
        return new CANNON.PointToPointConstraint(
          bodyA,
          new CANNON.Vec3(...(constraintDef.pivotA || [0, 0, 0])),
          bodyB,
          new CANNON.Vec3(...(constraintDef.pivotB || [0, 0, 0]))
        );
      case 'distance':
        return new CANNON.DistanceConstraint(
          bodyA,
          bodyB,
          constraintDef.distance || 1
        );
      case 'lock':
        return new CANNON.LockConstraint(bodyA, bodyB);
      case 'hinge':
        return new CANNON.HingeConstraint(
          bodyA,
          bodyB,
          {
            pivotA: new CANNON.Vec3(...(constraintDef.pivotA || [0, 0, 0])),
            pivotB: new CANNON.Vec3(...(constraintDef.pivotB || [0, 0, 0])),
            axisA: new CANNON.Vec3(0, 1, 0),
            axisB: new CANNON.Vec3(0, 1, 0)
          }
        );
      default:
        return null;
    }
  }, []);

  const initializeBodies = useCallback(() => {
    if (!worldRef.current || !sceneRef.current) return;

    const world = worldRef.current;
    const scene = sceneRef.current;

    // Clear existing bodies and meshes
    physicsBodyRef.current.forEach(body => world.removeBody(body));
    visualMeshRef.current.forEach(mesh => scene.remove(mesh));
    constraintRef.current.forEach(constraint => world.removeConstraint(constraint));

    physicsBodyRef.current.clear();
    visualMeshRef.current.clear();
    constraintRef.current.clear();

    // Create physics bodies and visual meshes
    bodies.forEach(bodyDef => {
      const physicsBody = createPhysicsBody(bodyDef);
      const visualMesh = createVisualMesh(bodyDef);

      world.addBody(physicsBody);
      scene.add(visualMesh);

      physicsBodyRef.current.set(bodyDef.id, physicsBody);
      visualMeshRef.current.set(bodyDef.id, visualMesh);
    });

    // Create constraints
    constraints.forEach(constraintDef => {
      const constraint = createConstraint(constraintDef);
      if (constraint) {
        world.addConstraint(constraint);
        constraintRef.current.set(constraintDef.id, constraint);
      }
    });

    setStats(prev => ({ ...prev, bodies: bodies.length }));
  }, [bodies, constraints, createPhysicsBody, createVisualMesh, createConstraint]);

  const updateSimulation = useCallback(() => {
    if (!worldRef.current || !isRunning) return;

    const world = worldRef.current;
    const timestep = (worldConfig.timestep || defaultWorldConfig.timestep);

    // Step physics simulation
    world.step(timestep);

    // Update visual meshes to match physics bodies
    physicsBodyRef.current.forEach((physicsBody, bodyId) => {
      const visualMesh = visualMeshRef.current.get(bodyId);
      if (visualMesh) {
        visualMesh.position.copy(physicsBody.position as any);
        visualMesh.quaternion.copy(physicsBody.quaternion as any);

        // Callback for external updates
        if (onBodyUpdate) {
          onBodyUpdate(
            bodyId,
            [physicsBody.position.x, physicsBody.position.y, physicsBody.position.z],
            [physicsBody.quaternion.x, physicsBody.quaternion.y, physicsBody.quaternion.z, physicsBody.quaternion.w]
          );
        }
      }
    });

    // Update stats
    setStats(prev => ({
      ...prev,
      contacts: world.contacts.length
    }));
  }, [isRunning, worldConfig.timestep, onBodyUpdate]);

  const animate = useCallback(() => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) return;

    // Update camera controls
    if ((cameraRef.current as any).updateControls) {
      (cameraRef.current as any).updateControls();
    }

    // Update physics simulation
    updateSimulation();

    // Render scene
    rendererRef.current.render(sceneRef.current, cameraRef.current);

    animationIdRef.current = requestAnimationFrame(animate);
  }, [updateSimulation]);

  // Calculate FPS
  useEffect(() => {
    let frameCount = 0;
    let lastTime = Date.now();

    const updateFPS = () => {
      frameCount++;
      const currentTime = Date.now();
      
      if (currentTime - lastTime >= 1000) {
        setStats(prev => ({ ...prev, fps: frameCount }));
        frameCount = 0;
        lastTime = currentTime;
      }
      
      if (isRunning) {
        requestAnimationFrame(updateFPS);
      }
    };

    if (isRunning) {
      updateFPS();
    }
  }, [isRunning]);

  // Initialize physics and graphics
  useEffect(() => {
    initializePhysicsWorld();
    initializeScene();
    initializeBodies();
    animate();

    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      if (rendererRef.current && mountRef.current && mountRef.current.contains(rendererRef.current.domElement)) {
        mountRef.current.removeChild(rendererRef.current.domElement);
        rendererRef.current.dispose();
      }
    };
  }, []);

  // Update bodies when props change
  useEffect(() => {
    initializeBodies();
  }, [initializeBodies]);

  // Restart animation loop when running state changes
  useEffect(() => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
    }
    animate();
  }, [animate]);

  const handleStartStop = () => {
    setIsRunning(!isRunning);
  };

  const handleReset = () => {
    setIsRunning(false);
    initializeBodies();
  };

  const handleStepForward = () => {
    if (!isRunning) {
      updateSimulation();
    }
  };

  return (
    <div className="physics-renderer">
      <div 
        ref={mountRef} 
        className="physics-canvas-container border rounded"
        style={{ width, height }}
      />
      
      {/* Controls */}
      <div className="physics-controls mt-3 p-3 bg-gray-50 rounded border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={handleStartStop}
              className={`px-4 py-2 rounded text-white font-medium ${
                isRunning ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {isRunning ? 'Stop' : 'Start'}
            </button>
            
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 font-medium"
            >
              Reset
            </button>
            
            <button
              onClick={handleStepForward}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Step
            </button>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>FPS: {stats.fps}</span>
            <span>Bodies: {stats.bodies}</span>
            <span>Contacts: {stats.contacts}</span>
          </div>
        </div>

        {/* Physics Configuration */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <label className="block text-gray-700 font-medium mb-1">Gravity Y</label>
              <input
                type="range"
                min="-20"
                max="0"
                step="0.1"
                value={worldConfig.gravity?.[1] || -9.81}
                onChange={(e) => {
                  if (worldRef.current) {
                    const newGravity = parseFloat(e.target.value);
                    worldRef.current.gravity.set(0, newGravity, 0);
                  }
                }}
                className="w-full"
              />
              <span className="text-gray-500">{(worldConfig.gravity?.[1] || -9.81).toFixed(1)}</span>
            </div>
            
            <div>
              <label className="block text-gray-700 font-medium mb-1">Timestep</label>
              <input
                type="range"
                min="0.008"
                max="0.033"
                step="0.001"
                value={worldConfig.timestep || 1/60}
                className="w-full"
              />
              <span className="text-gray-500">{((worldConfig.timestep || 1/60) * 1000).toFixed(0)}ms</span>
            </div>
            
            <div>
              <label className="block text-gray-700 font-medium mb-1">Iterations</label>
              <input
                type="range"
                min="5"
                max="20"
                step="1"
                value={worldConfig.iterations || 10}
                className="w-full"
              />
              <span className="text-gray-500">{worldConfig.iterations || 10}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showDebug}
                readOnly
                className="rounded"
              />
              <label className="text-gray-700 font-medium">Debug Mode</label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

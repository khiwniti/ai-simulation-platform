'use client';

import React, { useRef, useEffect, useCallback, useState } from 'react';
import * as THREE from 'three';

export interface VisualizationData {
  type: 'physics' | 'plot' | 'mesh' | 'particles';
  data: any;
  config?: {
    camera?: {
      position: [number, number, number];
      target: [number, number, number];
    };
    scene?: {
      background?: string;
      fog?: { color: string; near: number; far: number };
    };
    animation?: {
      enabled: boolean;
      duration?: number;
      loop?: boolean;
    };
  };
}

interface ThreeJSRendererProps {
  data: VisualizationData;
  width?: number;
  height?: number;
  onSceneReady?: (scene: THREE.Scene, camera: THREE.Camera, renderer: THREE.WebGLRenderer) => void;
}

export const ThreeJSRenderer: React.FC<ThreeJSRendererProps> = ({
  data,
  width = 800,
  height = 600,
  onSceneReady
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const animationIdRef = useRef<number>();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);

  const initializeScene = useCallback(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(data.config?.scene?.background || '#f8f9fa');
    
    if (data.config?.scene?.fog) {
      const fog = data.config.scene.fog;
      scene.fog = new THREE.Fog(fog.color, fog.near, fog.far);
    }

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    if (data.config?.camera?.position) {
      camera.position.set(...data.config.camera.position);
    } else {
      camera.position.set(5, 5, 5);
    }
    
    if (data.config?.camera?.target) {
      camera.lookAt(new THREE.Vector3(...data.config.camera.target));
    } else {
      camera.lookAt(0, 0, 0);
    }

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Store references
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;

    // Mount renderer
    mountRef.current.appendChild(renderer.domElement);

    // Add controls
    addOrbitControls(camera, renderer);

    // Callback for external access
    if (onSceneReady) {
      onSceneReady(scene, camera, renderer);
    }

    return { scene, camera, renderer };
  }, [data, width, height, onSceneReady]);

  const addOrbitControls = (camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer) => {
    // Simple orbit controls implementation
    let isMouseDown = false;
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

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
      camera.position.multiplyScalar(scale);
    };

    renderer.domElement.addEventListener('mousedown', handleMouseDown);
    renderer.domElement.addEventListener('mousemove', handleMouseMove);
    renderer.domElement.addEventListener('mouseup', handleMouseUp);
    renderer.domElement.addEventListener('wheel', handleWheel);

    // Update camera position based on mouse input
    const updateCamera = () => {
      const radius = camera.position.length();
      camera.position.x = radius * Math.cos(targetY) * Math.cos(targetX);
      camera.position.y = radius * Math.sin(targetY);
      camera.position.z = radius * Math.cos(targetY) * Math.sin(targetX);
      camera.lookAt(0, 0, 0);
    };

    // Store update function for animation loop
    (camera as any).updateControls = updateCamera;
  };

  const renderVisualization = useCallback(() => {
    if (!sceneRef.current) return;

    const scene = sceneRef.current;

    // Clear existing objects (except lights)
    const objectsToRemove = scene.children.filter(child => 
      !(child instanceof THREE.Light)
    );
    objectsToRemove.forEach(obj => scene.remove(obj));

    switch (data.type) {
      case 'physics':
        renderPhysicsSimulation(scene, data.data, currentFrame);
        break;
      case 'plot':
        renderPlotVisualization(scene, data.data);
        break;
      case 'mesh':
        renderMeshVisualization(scene, data.data);
        break;
      case 'particles':
        renderParticleSystem(scene, data.data, currentFrame);
        break;
    }
  }, [data, currentFrame]);

  const renderPhysicsSimulation = (scene: THREE.Scene, physicsData: any, frame: number) => {
    if (!physicsData.positions || !Array.isArray(physicsData.positions)) return;

    const positions = physicsData.positions;
    const frameData = positions[frame] || positions[0];

    if (!frameData) return;

    // Create objects for each physics body
    frameData.forEach((position: [number, number, number], index: number) => {
      const geometry = new THREE.SphereGeometry(0.1, 16, 16);
      const material = new THREE.MeshLambertMaterial({ 
        color: physicsData.colors?.[index] || 0x00ff00 
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(position[0], position[1], position[2]);
      sphere.castShadow = true;
      sphere.receiveShadow = true;
      scene.add(sphere);
    });

    // Add trajectory lines if available
    if (physicsData.trajectories) {
      physicsData.trajectories.forEach((trajectory: [number, number, number][], index: number) => {
        const points = trajectory.map(pos => new THREE.Vector3(pos[0], pos[1], pos[2]));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
          color: physicsData.colors?.[index] || 0x00ff00,
          opacity: 0.6,
          transparent: true
        });
        const line = new THREE.Line(geometry, material);
        scene.add(line);
      });
    }

    setTotalFrames(positions.length);
  };

  const renderPlotVisualization = (scene: THREE.Scene, plotData: any) => {
    if (!plotData.points || !Array.isArray(plotData.points)) return;

    // Create scatter plot
    plotData.points.forEach((point: [number, number, number], index: number) => {
      const geometry = new THREE.SphereGeometry(0.05, 8, 8);
      const material = new THREE.MeshLambertMaterial({ 
        color: plotData.colors?.[index] || 0x0066cc 
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(point[0], point[1], point[2]);
      scene.add(sphere);
    });

    // Add axes
    addAxes(scene, plotData.bounds || { x: [-5, 5], y: [-5, 5], z: [-5, 5] });
  };

  const renderMeshVisualization = (scene: THREE.Scene, meshData: any) => {
    if (!meshData.vertices || !meshData.faces) return;

    const geometry = new THREE.BufferGeometry();
    
    // Set vertices
    const vertices = new Float32Array(meshData.vertices.flat());
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

    // Set faces
    if (meshData.faces) {
      const indices = new Uint16Array(meshData.faces.flat());
      geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    }

    geometry.computeVertexNormals();

    const material = new THREE.MeshLambertMaterial({ 
      color: meshData.color || 0x00aa00,
      wireframe: meshData.wireframe || false
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
  };

  const renderParticleSystem = (scene: THREE.Scene, particleData: any, frame: number) => {
    if (!particleData.positions || !Array.isArray(particleData.positions)) return;

    const frameData = particleData.positions[frame] || particleData.positions[0];
    if (!frameData) return;

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(frameData.flat());
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      color: particleData.color || 0xffffff,
      size: particleData.size || 0.1,
      transparent: true,
      opacity: particleData.opacity || 0.8
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    setTotalFrames(particleData.positions.length);
  };

  const addAxes = (scene: THREE.Scene, bounds: any) => {
    const axesHelper = new THREE.AxesHelper(Math.max(
      Math.abs(bounds.x[1] - bounds.x[0]),
      Math.abs(bounds.y[1] - bounds.y[0]),
      Math.abs(bounds.z[1] - bounds.z[0])
    ) / 2);
    scene.add(axesHelper);
  };

  const animate = useCallback(() => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) return;

    // Update camera controls
    if ((cameraRef.current as any).updateControls) {
      (cameraRef.current as any).updateControls();
    }

    // Render scene
    rendererRef.current.render(sceneRef.current, cameraRef.current);

    // Continue animation if playing
    if (isPlaying && data.config?.animation?.enabled) {
      setCurrentFrame(prev => {
        const next = prev + 1;
        return next >= totalFrames ? (data.config?.animation?.loop ? 0 : totalFrames - 1) : next;
      });
    }

    animationIdRef.current = requestAnimationFrame(animate);
  }, [isPlaying, totalFrames, data.config?.animation]);

  // Initialize scene
  useEffect(() => {
    const sceneData = initializeScene();
    if (sceneData) {
      renderVisualization();
      animate();
    }

    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      if (rendererRef.current && mountRef.current) {
        mountRef.current.removeChild(rendererRef.current.domElement);
        rendererRef.current.dispose();
      }
    };
  }, []);

  // Update visualization when data changes
  useEffect(() => {
    renderVisualization();
  }, [renderVisualization]);

  // Animation loop
  useEffect(() => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
    }
    animate();
  }, [animate]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleFrameChange = (frame: number) => {
    setCurrentFrame(Math.max(0, Math.min(totalFrames - 1, frame)));
  };

  const handleReset = () => {
    setCurrentFrame(0);
    setIsPlaying(false);
  };

  return (
    <div className="threejs-renderer">
      <div 
        ref={mountRef} 
        className="threejs-canvas-container border rounded"
        style={{ width, height }}
      />
      
      {/* Animation Controls */}
      {totalFrames > 1 && (
        <div className="animation-controls mt-3 p-3 bg-gray-50 rounded border">
          <div className="flex items-center gap-3">
            <button
              onClick={handlePlayPause}
              className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
            >
              {isPlaying ? 'Pause' : 'Play'}
            </button>
            
            <button
              onClick={handleReset}
              className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
            >
              Reset
            </button>
            
            <div className="flex-1 flex items-center gap-2">
              <span className="text-sm text-gray-600">Frame:</span>
              <input
                type="range"
                min="0"
                max={totalFrames - 1}
                value={currentFrame}
                onChange={(e) => handleFrameChange(parseInt(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm text-gray-600 min-w-0">
                {currentFrame + 1} / {totalFrames}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
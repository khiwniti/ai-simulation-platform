'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';

export interface CameraConfig {
  type: 'perspective' | 'orthographic';
  fov?: number;
  position: [number, number, number];
  target: [number, number, number];
  near?: number;
  far?: number;
  zoom?: number;
}

export interface ControlsConfig {
  enableZoom: boolean;
  enablePan: boolean;
  enableRotate: boolean;
  autoRotate: boolean;
  autoRotateSpeed: number;
  enableDamping: boolean;
  dampingFactor: number;
  minDistance: number;
  maxDistance: number;
  minPolarAngle: number;
  maxPolarAngle: number;
  minAzimuthAngle: number;
  maxAzimuthAngle: number;
}

export interface InteractionEvent {
  type: 'hover' | 'click' | 'dragstart' | 'drag' | 'dragend' | 'select';
  object?: THREE.Object3D;
  point?: THREE.Vector3;
  worldPosition?: THREE.Vector3;
  screenPosition?: { x: number; y: number };
  button?: number;
}

interface InteractiveControlsProps {
  camera: THREE.Camera;
  renderer: THREE.WebGLRenderer;
  scene: THREE.Scene;
  selectableObjects?: THREE.Object3D[];
  cameraConfig?: Partial<CameraConfig>;
  controlsConfig?: Partial<ControlsConfig>;
  onInteraction?: (event: InteractionEvent) => void;
  onCameraChange?: (position: THREE.Vector3, target: THREE.Vector3) => void;
  enableObjectManipulation?: boolean;
  showGizmos?: boolean;
}

export const InteractiveControls: React.FC<InteractiveControlsProps> = ({
  camera,
  renderer,
  scene,
  selectableObjects = [],
  cameraConfig = {},
  controlsConfig = {},
  onInteraction,
  onCameraChange,
  enableObjectManipulation = true,
  showGizmos = true
}) => {
  const [selectedObject, setSelectedObject] = useState<THREE.Object3D | null>(null);
  const [hoveredObject, setHoveredObject] = useState<THREE.Object3D | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragMode, setDragMode] = useState<'translate' | 'rotate' | 'scale'>('translate');
  
  const raycasterRef = useRef(new THREE.Raycaster());
  const mouseRef = useRef(new THREE.Vector2());
  const previousMouseRef = useRef(new THREE.Vector2());
  const targetRef = useRef(new THREE.Vector3());
  const sphericalRef = useRef(new THREE.Spherical());
  const gizmosRef = useRef<THREE.Group>();

  // Default configurations
  const defaultCameraConfig: CameraConfig = {
    type: 'perspective',
    fov: 75,
    position: [10, 10, 10],
    target: [0, 0, 0],
    near: 0.1,
    far: 1000,
    zoom: 1
  };

  const defaultControlsConfig: ControlsConfig = {
    enableZoom: true,
    enablePan: true,
    enableRotate: true,
    autoRotate: false,
    autoRotateSpeed: 2.0,
    enableDamping: true,
    dampingFactor: 0.05,
    minDistance: 1,
    maxDistance: 100,
    minPolarAngle: 0,
    maxPolarAngle: Math.PI,
    minAzimuthAngle: -Infinity,
    maxAzimuthAngle: Infinity
  };

  const finalCameraConfig = { ...defaultCameraConfig, ...cameraConfig };
  const finalControlsConfig = { ...defaultControlsConfig, ...controlsConfig };

  // Initialize camera controls
  useEffect(() => {
    const target = new THREE.Vector3(...finalCameraConfig.target);
    targetRef.current.copy(target);
    
    if (camera instanceof THREE.PerspectiveCamera) {
      camera.position.set(...finalCameraConfig.position);
      camera.lookAt(target);
      camera.fov = finalCameraConfig.fov || 75;
      camera.near = finalCameraConfig.near || 0.1;
      camera.far = finalCameraConfig.far || 1000;
      camera.updateProjectionMatrix();
    }
  }, [camera, finalCameraConfig]);

  // Create manipulation gizmos
  const createGizmos = useCallback(() => {
    if (!showGizmos) return;

    const gizmos = new THREE.Group();
    
    // Translation arrows
    const arrowLength = 2;
    const arrowGeometry = new THREE.CylinderGeometry(0, 0.1, arrowLength, 8);
    
    // X axis (red)
    const xArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff0000 }));
    xArrow.rotation.z = -Math.PI / 2;
    xArrow.position.x = arrowLength / 2;
    xArrow.userData = { axis: 'x', type: 'translate' };
    gizmos.add(xArrow);

    // Y axis (green)
    const yArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x00ff00 }));
    yArrow.position.y = arrowLength / 2;
    yArrow.userData = { axis: 'y', type: 'translate' };
    gizmos.add(yArrow);

    // Z axis (blue)
    const zArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x0000ff }));
    zArrow.rotation.x = Math.PI / 2;
    zArrow.position.z = arrowLength / 2;
    zArrow.userData = { axis: 'z', type: 'translate' };
    gizmos.add(zArrow);

    // Rotation rings
    if (dragMode === 'rotate') {
      const ringGeometry = new THREE.RingGeometry(1.5, 1.6, 32);
      
      const xRing = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({ 
        color: 0xff0000, 
        transparent: true, 
        opacity: 0.7,
        side: THREE.DoubleSide
      }));
      xRing.rotation.y = Math.PI / 2;
      xRing.userData = { axis: 'x', type: 'rotate' };
      gizmos.add(xRing);

      const yRing = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({ 
        color: 0x00ff00, 
        transparent: true, 
        opacity: 0.7,
        side: THREE.DoubleSide
      }));
      yRing.userData = { axis: 'y', type: 'rotate' };
      gizmos.add(yRing);

      const zRing = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({ 
        color: 0x0000ff, 
        transparent: true, 
        opacity: 0.7,
        side: THREE.DoubleSide
      }));
      zRing.rotation.x = Math.PI / 2;
      zRing.userData = { axis: 'z', type: 'rotate' };
      gizmos.add(zRing);
    }

    // Scale handles
    if (dragMode === 'scale') {
      const handleGeometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
      
      const xHandle = new THREE.Mesh(handleGeometry, new THREE.MeshBasicMaterial({ color: 0xff0000 }));
      xHandle.position.x = 1.5;
      xHandle.userData = { axis: 'x', type: 'scale' };
      gizmos.add(xHandle);

      const yHandle = new THREE.Mesh(handleGeometry, new THREE.MeshBasicMaterial({ color: 0x00ff00 }));
      yHandle.position.y = 1.5;
      yHandle.userData = { axis: 'y', type: 'scale' };
      gizmos.add(yHandle);

      const zHandle = new THREE.Mesh(handleGeometry, new THREE.MeshBasicMaterial({ color: 0x0000ff }));
      zHandle.position.z = 1.5;
      zHandle.userData = { axis: 'z', type: 'scale' };
      gizmos.add(zHandle);
    }

    gizmos.visible = false;
    scene.add(gizmos);
    gizmosRef.current = gizmos;

    return gizmos;
  }, [scene, showGizmos, dragMode]);

  // Update gizmos position and visibility
  const updateGizmos = useCallback(() => {
    if (!gizmosRef.current || !selectedObject) return;

    gizmosRef.current.position.copy(selectedObject.position);
    gizmosRef.current.visible = selectedObject !== null && showGizmos;
  }, [selectedObject, showGizmos]);

  // Raycasting for object interaction
  const getIntersectedObject = useCallback((clientX: number, clientY: number): THREE.Object3D | null => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouseRef.current.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, camera);
    
    const intersects = raycasterRef.current.intersectObjects(selectableObjects, true);
    
    if (intersects.length > 0) {
      return intersects[0].object;
    }
    
    return null;
  }, [camera, renderer, selectableObjects]);

  // Camera orbit controls
  const updateCameraOrbit = useCallback((deltaX: number, deltaY: number) => {
    if (!finalControlsConfig.enableRotate) return;

    const spherical = sphericalRef.current;
    const target = targetRef.current;
    
    // Get current spherical coordinates
    const offset = new THREE.Vector3().subVectors(camera.position, target);
    spherical.setFromVector3(offset);

    // Update angles
    spherical.theta -= deltaX * 0.01;
    spherical.phi += deltaY * 0.01;

    // Constrain angles
    spherical.phi = Math.max(finalControlsConfig.minPolarAngle, 
                            Math.min(finalControlsConfig.maxPolarAngle, spherical.phi));
    
    if (finalControlsConfig.minAzimuthAngle !== -Infinity || finalControlsConfig.maxAzimuthAngle !== Infinity) {
      spherical.theta = Math.max(finalControlsConfig.minAzimuthAngle,
                                Math.min(finalControlsConfig.maxAzimuthAngle, spherical.theta));
    }

    // Constrain distance
    spherical.radius = Math.max(finalControlsConfig.minDistance,
                               Math.min(finalControlsConfig.maxDistance, spherical.radius));

    // Update camera position
    offset.setFromSpherical(spherical);
    camera.position.copy(target).add(offset);
    camera.lookAt(target);

    if (onCameraChange) {
      onCameraChange(camera.position, target);
    }
  }, [camera, finalControlsConfig, onCameraChange]);

  // Camera pan
  const panCamera = useCallback((deltaX: number, deltaY: number) => {
    if (!finalControlsConfig.enablePan) return;

    const offset = new THREE.Vector3();
    const target = targetRef.current;
    
    if (camera instanceof THREE.PerspectiveCamera) {
      // Calculate pan distance based on camera distance and FOV
      const distance = camera.position.distanceTo(target);
      const fov = camera.fov * Math.PI / 180;
      const panScale = 2 * Math.tan(fov / 2) * distance / renderer.domElement.clientHeight;
      
      offset.setFromMatrixColumn(camera.matrix, 0); // right vector
      offset.multiplyScalar(-deltaX * panScale);
      
      const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1); // up vector
      up.multiplyScalar(deltaY * panScale);
      offset.add(up);
      
      camera.position.add(offset);
      target.add(offset);
    }

    if (onCameraChange) {
      onCameraChange(camera.position, target);
    }
  }, [camera, renderer, finalControlsConfig.enablePan, onCameraChange]);

  // Zoom camera
  const zoomCamera = useCallback((delta: number) => {
    if (!finalControlsConfig.enableZoom) return;

    const spherical = sphericalRef.current;
    const target = targetRef.current;
    const offset = new THREE.Vector3().subVectors(camera.position, target);
    
    spherical.setFromVector3(offset);
    spherical.radius *= (delta > 0 ? 1.1 : 0.9);
    spherical.radius = Math.max(finalControlsConfig.minDistance,
                               Math.min(finalControlsConfig.maxDistance, spherical.radius));
    
    offset.setFromSpherical(spherical);
    camera.position.copy(target).add(offset);

    if (onCameraChange) {
      onCameraChange(camera.position, target);
    }
  }, [camera, finalControlsConfig, onCameraChange]);

  // Event handlers
  const handleMouseDown = useCallback((event: MouseEvent) => {
    const intersectedObject = getIntersectedObject(event.clientX, event.clientY);
    
    if (intersectedObject && enableObjectManipulation) {
      setSelectedObject(intersectedObject);
      setIsDragging(true);
      
      if (onInteraction) {
        onInteraction({
          type: 'select',
          object: intersectedObject,
          screenPosition: { x: event.clientX, y: event.clientY }
        });
      }
    }
    
    previousMouseRef.current.set(event.clientX, event.clientY);
  }, [getIntersectedObject, enableObjectManipulation, onInteraction]);

  const handleMouseMove = useCallback((event: MouseEvent) => {
    const currentMouse = new THREE.Vector2(event.clientX, event.clientY);
    const deltaX = currentMouse.x - previousMouseRef.current.x;
    const deltaY = currentMouse.y - previousMouseRef.current.y;

    // Check for hover
    if (!isDragging) {
      const intersectedObject = getIntersectedObject(event.clientX, event.clientY);
      
      if (intersectedObject !== hoveredObject) {
        setHoveredObject(intersectedObject);
        
        if (onInteraction) {
          onInteraction({
            type: 'hover',
            object: intersectedObject || undefined,
            screenPosition: { x: event.clientX, y: event.clientY }
          });
        }
      }
    }

    // Handle dragging
    if (isDragging) {
      if (selectedObject && enableObjectManipulation) {
        // Object manipulation
        if (onInteraction) {
          onInteraction({
            type: 'drag',
            object: selectedObject,
            screenPosition: { x: event.clientX, y: event.clientY }
          });
        }
      } else {
        // Camera controls
        if (event.buttons === 1) { // Left mouse button
          updateCameraOrbit(deltaX, deltaY);
        } else if (event.buttons === 2) { // Right mouse button
          panCamera(deltaX, deltaY);
        }
      }
    }

    previousMouseRef.current.copy(currentMouse);
  }, [isDragging, selectedObject, hoveredObject, enableObjectManipulation, getIntersectedObject, onInteraction, updateCameraOrbit, panCamera]);

  const handleMouseUp = useCallback((event: MouseEvent) => {
    if (isDragging && selectedObject && onInteraction) {
      onInteraction({
        type: 'dragend',
        object: selectedObject,
        screenPosition: { x: event.clientX, y: event.clientY }
      });
    }
    
    setIsDragging(false);
  }, [isDragging, selectedObject, onInteraction]);

  const handleClick = useCallback((event: MouseEvent) => {
    const intersectedObject = getIntersectedObject(event.clientX, event.clientY);
    
    if (onInteraction) {
      onInteraction({
        type: 'click',
        object: intersectedObject || undefined,
        screenPosition: { x: event.clientX, y: event.clientY },
        button: event.button
      });
    }
  }, [getIntersectedObject, onInteraction]);

  const handleWheel = useCallback((event: WheelEvent) => {
    event.preventDefault();
    zoomCamera(event.deltaY);
  }, [zoomCamera]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'g':
      case 'G':
        setDragMode('translate');
        break;
      case 'r':
      case 'R':
        setDragMode('rotate');
        break;
      case 's':
      case 'S':
        setDragMode('scale');
        break;
      case 'Escape':
        setSelectedObject(null);
        break;
    }
  }, []);

  // Set up event listeners
  useEffect(() => {
    const canvas = renderer.domElement;
    
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('click', handleClick);
    canvas.addEventListener('wheel', handleWheel);
    
    // Prevent context menu on right click
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    
    // Global keyboard events
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('click', handleClick);
      canvas.removeEventListener('wheel', handleWheel);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleMouseDown, handleMouseMove, handleMouseUp, handleClick, handleWheel, handleKeyDown, renderer.domElement]);

  // Initialize gizmos
  useEffect(() => {
    createGizmos();
    
    return () => {
      if (gizmosRef.current) {
        scene.remove(gizmosRef.current);
      }
    };
  }, [createGizmos, scene]);

  // Update gizmos when selection changes
  useEffect(() => {
    updateGizmos();
  }, [updateGizmos]);

  // Auto rotation
  useEffect(() => {
    if (!finalControlsConfig.autoRotate) return;

    const interval = setInterval(() => {
      updateCameraOrbit(finalControlsConfig.autoRotateSpeed * 0.01, 0);
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [finalControlsConfig.autoRotate, finalControlsConfig.autoRotateSpeed, updateCameraOrbit]);

  return null; // This component only handles events, no visual rendering
};

// Helper hook for using interactive controls
export const useInteractiveControls = (
  camera: THREE.Camera | null,
  renderer: THREE.WebGLRenderer | null,
  scene: THREE.Scene | null,
  options: Partial<InteractiveControlsProps> = {}
) => {
  const [selectedObject, setSelectedObject] = useState<THREE.Object3D | null>(null);
  const [hoveredObject, setHoveredObject] = useState<THREE.Object3D | null>(null);
  const [cameraPosition, setCameraPosition] = useState<THREE.Vector3>(new THREE.Vector3());
  const [cameraTarget, setCameraTarget] = useState<THREE.Vector3>(new THREE.Vector3());

  const handleInteraction = useCallback((event: InteractionEvent) => {
    switch (event.type) {
      case 'select':
        setSelectedObject(event.object || null);
        break;
      case 'hover':
        setHoveredObject(event.object || null);
        break;
    }
    
    options.onInteraction?.(event);
  }, [options]);

  const handleCameraChange = useCallback((position: THREE.Vector3, target: THREE.Vector3) => {
    setCameraPosition(position.clone());
    setCameraTarget(target.clone());
    options.onCameraChange?.(position, target);
  }, [options]);

  const controlsElement = camera && renderer && scene ? (
    <InteractiveControls
      camera={camera}
      renderer={renderer}
      scene={scene}
      onInteraction={handleInteraction}
      onCameraChange={handleCameraChange}
      {...options}
    />
  ) : null;

  return {
    controlsElement,
    selectedObject,
    hoveredObject,
    cameraPosition,
    cameraTarget,
    setSelectedObject
  };
};
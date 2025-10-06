'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { PhysicsRenderer, PhysicsBody, PhysicsConstraint, PhysicsWorldConfig } from './PhysicsRenderer';
import { InteractiveControls, InteractionEvent, useInteractiveControls } from './InteractiveControls';
import { PhysicsObjectLibrary, PhysicsObjectTemplate, PhysicsSystemTemplate } from './PhysicsObjectLibrary';

export interface SimulationState {
  isRunning: boolean;
  isPaused: boolean;
  currentTime: number;
  timeStep: number;
  totalSteps: number;
}

export interface VisualizationConfig {
  showDebug: boolean;
  enableShadows: boolean;
  enableObjectManipulation: boolean;
  showGizmos: boolean;
  autoRotate: boolean;
  quality: 'low' | 'medium' | 'high';
}

interface PhysicsVisualizationStudioProps {
  width?: number;
  height?: number;
  onSimulationStateChange?: (state: SimulationState) => void;
  onObjectsChange?: (bodies: PhysicsBody[], constraints: PhysicsConstraint[]) => void;
  onExportScene?: (sceneData: any) => void;
  onImportScene?: (sceneData: any) => void;
  className?: string;
}

export const PhysicsVisualizationStudio: React.FC<PhysicsVisualizationStudioProps> = ({
  width = 1200,
  height = 700,
  onSimulationStateChange,
  onObjectsChange,
  onExportScene,
  onImportScene,
  className = ''
}) => {
  // Core state
  const [bodies, setBodies] = useState<PhysicsBody[]>([]);
  const [constraints, setConstraints] = useState<PhysicsConstraint[]>([]);
  const [worldConfig, setWorldConfig] = useState<Partial<PhysicsWorldConfig>>({
    gravity: [0, -9.81, 0],
    timestep: 1/60,
    iterations: 10
  });

  // UI state
  const [showLibrary, setShowLibrary] = useState(true);
  const [showProperties, setShowProperties] = useState(true);
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null);
  const [visualConfig, setVisualConfig] = useState<VisualizationConfig>({
    showDebug: false,
    enableShadows: true,
    enableObjectManipulation: true,
    showGizmos: true,
    autoRotate: false,
    quality: 'medium'
  });

  // Simulation state
  const [simulationState, setSimulationState] = useState<SimulationState>({
    isRunning: false,
    isPaused: false,
    currentTime: 0,
    timeStep: 1/60,
    totalSteps: 0
  });

  // Scene references
  const sceneRef = useRef<THREE.Scene>();
  const cameraRef = useRef<THREE.Camera>();
  const rendererRef = useRef<THREE.WebGLRenderer>();

  // Get selected object
  const selectedObject = selectedObjectId ? bodies.find(body => body.id === selectedObjectId) : null;

  // Handle scene ready callback
  const handleSceneReady = useCallback((scene: THREE.Scene, camera: THREE.Camera, renderer: THREE.WebGLRenderer) => {
    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;
  }, []);

  // Interactive controls
  const {
    controlsElement,
    selectedObject: interactiveSelectedObject,
    hoveredObject,
    cameraPosition,
    cameraTarget
  } = useInteractiveControls(
    cameraRef.current || null,
    rendererRef.current || null,
    sceneRef.current || null,
    {
      selectableObjects: [], // Will be populated with physics meshes
      enableObjectManipulation: visualConfig.enableObjectManipulation,
      showGizmos: visualConfig.showGizmos,
      onInteraction: handleInteraction
    }
  );

  // Handle physics object library interactions
  const handleAddObject = useCallback((template: PhysicsObjectTemplate, position?: [number, number, number]) => {
    const newBody: PhysicsBody = {
      id: `${template.id}-${Date.now()}`,
      position: position || [Math.random() * 4 - 2, 5, Math.random() * 4 - 2],
      ...template.defaultProperties
    } as PhysicsBody;

    setBodies(prev => [...prev, newBody]);
    setSelectedObjectId(newBody.id);
  }, []);

  const handleAddSystem = useCallback((template: PhysicsSystemTemplate) => {
    // Clear existing objects and add system
    setBodies(template.bodies);
    setConstraints(template.constraints);
    
    if (template.worldConfig) {
      setWorldConfig(prev => ({ ...prev, ...template.worldConfig }));
    }
  }, []);

  // Handle interactive events
  function handleInteraction(event: InteractionEvent) {
    switch (event.type) {
      case 'select':
        if (event.object && (event.object as any).userData?.physicsBodyId) {
          setSelectedObjectId((event.object as any).userData.physicsBodyId);
        } else {
          setSelectedObjectId(null);
        }
        break;
      case 'hover':
        // Handle hover effects
        break;
      case 'drag':
        // Handle object dragging
        if (selectedObjectId && event.worldPosition) {
          updateObjectProperty(selectedObjectId, 'position', [
            event.worldPosition.x,
            event.worldPosition.y,
            event.worldPosition.z
          ]);
        }
        break;
    }
  }

  // Handle physics body updates from simulation
  const handleBodyUpdate = useCallback((bodyId: string, position: [number, number, number], quaternion: [number, number, number, number]) => {
    // This would be used to sync external simulation state
    // For now, we let the physics engine handle updates
  }, []);

  // Handle collisions
  const handleCollision = useCallback((bodyAId: string, bodyBId: string, contactPoint: [number, number, number]) => {
    console.log(`Collision between ${bodyAId} and ${bodyBId} at`, contactPoint);
    
    // You could add visual effects, sound, or other responses here
    // For example, changing object colors on collision
  }, []);

  // Update object properties
  const updateObjectProperty = useCallback((objectId: string, property: string, value: any) => {
    setBodies(prev => prev.map(body => 
      body.id === objectId 
        ? { ...body, [property]: value }
        : body
    ));
  }, []);

  // Delete object
  const deleteObject = useCallback((objectId: string) => {
    setBodies(prev => prev.filter(body => body.id !== objectId));
    setConstraints(prev => prev.filter(constraint => 
      constraint.bodyA !== objectId && constraint.bodyB !== objectId
    ));
    
    if (selectedObjectId === objectId) {
      setSelectedObjectId(null);
    }
  }, [selectedObjectId]);

  // Clone object
  const cloneObject = useCallback((objectId: string) => {
    const originalBody = bodies.find(body => body.id === objectId);
    if (originalBody) {
      const clonedBody: PhysicsBody = {
        ...originalBody,
        id: `${originalBody.id}-clone-${Date.now()}`,
        position: [
          originalBody.position[0] + 2,
          originalBody.position[1],
          originalBody.position[2]
        ]
      };
      setBodies(prev => [...prev, clonedBody]);
      setSelectedObjectId(clonedBody.id);
    }
  }, [bodies]);

  // Export scene data
  const handleExportScene = useCallback(() => {
    const sceneData = {
      bodies,
      constraints,
      worldConfig,
      visualConfig,
      cameraPosition: cameraPosition.toArray(),
      cameraTarget: cameraTarget.toArray(),
      timestamp: new Date().toISOString()
    };
    
    if (onExportScene) {
      onExportScene(sceneData);
    } else {
      // Default export as JSON file
      const dataStr = JSON.stringify(sceneData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `physics-scene-${Date.now()}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  }, [bodies, constraints, worldConfig, visualConfig, cameraPosition, cameraTarget, onExportScene]);

  // Clear scene
  const handleClearScene = useCallback(() => {
    setBodies([]);
    setConstraints([]);
    setSelectedObjectId(null);
  }, []);

  // Notify parent of changes
  useEffect(() => {
    if (onObjectsChange) {
      onObjectsChange(bodies, constraints);
    }
  }, [bodies, constraints, onObjectsChange]);

  useEffect(() => {
    if (onSimulationStateChange) {
      onSimulationStateChange(simulationState);
    }
  }, [simulationState, onSimulationStateChange]);

  return (
    <div className={`physics-visualization-studio flex h-full bg-gray-100 ${className}`}>
      {/* Left Sidebar - Object Library */}
      {showLibrary && (
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <PhysicsObjectLibrary
            onAddObject={handleAddObject}
            onAddSystem={handleAddSystem}
            className="flex-1"
          />
        </div>
      )}

      {/* Main Visualization Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Toolbar */}
        <div className="bg-white border-b border-gray-200 p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-800">Physics Studio</h2>
            
            {/* Scene controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleClearScene}
                className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                disabled={bodies.length === 0}
              >
                Clear Scene
              </button>
              
              <button
                onClick={handleExportScene}
                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                disabled={bodies.length === 0}
              >
                Export Scene
              </button>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="file"
                  accept=".json"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onload = (event) => {
                        try {
                          const sceneData = JSON.parse(event.target?.result as string);
                          if (onImportScene) {
                            onImportScene(sceneData);
                          } else {
                            setBodies(sceneData.bodies || []);
                            setConstraints(sceneData.constraints || []);
                            setWorldConfig(sceneData.worldConfig || worldConfig);
                            setVisualConfig(sceneData.visualConfig || visualConfig);
                          }
                        } catch (error) {
                          console.error('Failed to import scene:', error);
                        }
                      };
                      reader.readAsText(file);
                    }
                  }}
                  className="hidden"
                />
                <span className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600">
                  Import Scene
                </span>
              </label>
            </div>
          </div>

          {/* View controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowLibrary(!showLibrary)}
              className={`px-3 py-1 text-sm rounded ${
                showLibrary ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              Library
            </button>
            
            <button
              onClick={() => setShowProperties(!showProperties)}
              className={`px-3 py-1 text-sm rounded ${
                showProperties ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              Properties
            </button>

            <div className="flex items-center gap-2 ml-3">
              <span className="text-sm text-gray-600">Bodies: {bodies.length}</span>
              <span className="text-sm text-gray-600">Constraints: {constraints.length}</span>
            </div>
          </div>
        </div>

        {/* Physics Renderer */}
        <div className="flex-1 bg-gray-100 p-4">
          <PhysicsRenderer
            bodies={bodies}
            constraints={constraints}
            worldConfig={worldConfig}
            onBodyUpdate={handleBodyUpdate}
            onCollision={handleCollision}
            width={width - (showLibrary ? 320 : 0) - (showProperties ? 320 : 0) - 32}
            height={height - 120}
            showDebug={visualConfig.showDebug}
            enableShadows={visualConfig.enableShadows}
          />
          
          {/* Interactive Controls */}
          {controlsElement}
        </div>
      </div>

      {/* Right Sidebar - Properties Panel */}
      {showProperties && (
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">Properties</h3>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto">
            {selectedObject ? (
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Object: {selectedObject.id}</h4>
                  <div className="space-y-3">
                    {/* Position */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Position</label>
                      <div className="grid grid-cols-3 gap-2">
                        {['x', 'y', 'z'].map((axis, index) => (
                          <input
                            key={axis}
                            type="number"
                            step="0.1"
                            value={selectedObject.position[index].toFixed(2)}
                            onChange={(e) => {
                              const newPosition = [...selectedObject.position] as [number, number, number];
                              newPosition[index] = parseFloat(e.target.value) || 0;
                              updateObjectProperty(selectedObject.id, 'position', newPosition);
                            }}
                            className="px-2 py-1 text-sm border border-gray-300 rounded"
                            placeholder={axis.toUpperCase()}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Size */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Size</label>
                      <div className="grid grid-cols-3 gap-2">
                        {['w', 'h', 'd'].map((dim, index) => (
                          <input
                            key={dim}
                            type="number"
                            step="0.1"
                            min="0.1"
                            value={selectedObject.size[index].toFixed(2)}
                            onChange={(e) => {
                              const newSize = [...selectedObject.size] as [number, number, number];
                              newSize[index] = Math.max(0.1, parseFloat(e.target.value) || 0.1);
                              updateObjectProperty(selectedObject.id, 'size', newSize);
                            }}
                            className="px-2 py-1 text-sm border border-gray-300 rounded"
                            placeholder={dim.toUpperCase()}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Mass */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Mass</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        value={selectedObject.mass}
                        onChange={(e) => updateObjectProperty(selectedObject.id, 'mass', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>

                    {/* Material Properties */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Material</label>
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs text-gray-500">Friction</label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={selectedObject.material?.friction || 0.4}
                            onChange={(e) => updateObjectProperty(selectedObject.id, 'material', {
                              ...selectedObject.material,
                              friction: parseFloat(e.target.value)
                            })}
                            className="w-full"
                          />
                          <span className="text-xs text-gray-500">{(selectedObject.material?.friction || 0.4).toFixed(1)}</span>
                        </div>
                        
                        <div>
                          <label className="block text-xs text-gray-500">Restitution</label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={selectedObject.material?.restitution || 0.3}
                            onChange={(e) => updateObjectProperty(selectedObject.id, 'material', {
                              ...selectedObject.material,
                              restitution: parseFloat(e.target.value)
                            })}
                            className="w-full"
                          />
                          <span className="text-xs text-gray-500">{(selectedObject.material?.restitution || 0.3).toFixed(1)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Color */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Color</label>
                      <input
                        type="color"
                        value={`#${(selectedObject.color || 0x00aa00).toString(16).padStart(6, '0')}`}
                        onChange={(e) => updateObjectProperty(selectedObject.id, 'color', parseInt(e.target.value.substring(1), 16))}
                        className="w-full h-8 border border-gray-300 rounded"
                      />
                    </div>

                    {/* Actions */}
                    <div className="pt-4 border-t border-gray-200 space-y-2">
                      <button
                        onClick={() => cloneObject(selectedObject.id)}
                        className="w-full px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                      >
                        Clone Object
                      </button>
                      
                      <button
                        onClick={() => deleteObject(selectedObject.id)}
                        className="w-full px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                      >
                        Delete Object
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">🎯</div>
                <p>Select an object to edit its properties</p>
              </div>
            )}

            {/* World Settings */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-700 mb-3">World Settings</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Gravity</label>
                  <input
                    type="range"
                    min="-20"
                    max="0"
                    step="0.1"
                    value={worldConfig.gravity?.[1] || -9.81}
                    onChange={(e) => setWorldConfig(prev => ({
                      ...prev,
                      gravity: [0, parseFloat(e.target.value), 0]
                    }))}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-500">{(worldConfig.gravity?.[1] || -9.81).toFixed(1)} m/s²</span>
                </div>

                {/* Visual Settings */}
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={visualConfig.enableShadows}
                      onChange={(e) => setVisualConfig(prev => ({ ...prev, enableShadows: e.target.checked }))}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">Enable Shadows</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={visualConfig.showDebug}
                      onChange={(e) => setVisualConfig(prev => ({ ...prev, showDebug: e.target.checked }))}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">Show Debug Info</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={visualConfig.showGizmos}
                      onChange={(e) => setVisualConfig(prev => ({ ...prev, showGizmos: e.target.checked }))}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">Show Gizmos</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

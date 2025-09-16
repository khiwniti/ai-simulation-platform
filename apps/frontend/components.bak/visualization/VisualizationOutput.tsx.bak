'use client';

import React, { useState, useCallback } from 'react';
import { ThreeJSRenderer, VisualizationData } from './ThreeJSRenderer';
import * as THREE from 'three';

interface VisualizationOutputProps {
  data: any;
  metadata?: Record<string, any>;
}

export const VisualizationOutput: React.FC<VisualizationOutputProps> = ({
  data,
  metadata
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [sceneInfo, setSceneInfo] = useState<{
    objects: number;
    vertices: number;
    triangles: number;
  }>({ objects: 0, vertices: 0, triangles: 0 });

  const handleSceneReady = useCallback((
    scene: THREE.Scene, 
    camera: THREE.Camera, 
    renderer: THREE.WebGLRenderer
  ) => {
    // Calculate scene statistics
    let objects = 0;
    let vertices = 0;
    let triangles = 0;

    scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        objects++;
        if (child.geometry) {
          const geometry = child.geometry;
          if (geometry.attributes.position) {
            vertices += geometry.attributes.position.count;
          }
          if (geometry.index) {
            triangles += geometry.index.count / 3;
          } else if (geometry.attributes.position) {
            triangles += geometry.attributes.position.count / 3;
          }
        }
      } else if (child instanceof THREE.Points) {
        objects++;
        if (child.geometry && child.geometry.attributes.position) {
          vertices += child.geometry.attributes.position.count;
        }
      }
    });

    setSceneInfo({ objects, vertices, triangles });
  }, []);

  const parseVisualizationData = (rawData: any): VisualizationData => {
    // Handle different data formats
    if (typeof rawData === 'string') {
      try {
        rawData = JSON.parse(rawData);
      } catch (e) {
        console.error('Failed to parse visualization data:', e);
        return {
          type: 'plot',
          data: { points: [] }
        };
      }
    }

    // Default configuration
    const defaultConfig = {
      camera: {
        position: [5, 5, 5] as [number, number, number],
        target: [0, 0, 0] as [number, number, number]
      },
      scene: {
        background: '#f8f9fa'
      },
      animation: {
        enabled: false,
        loop: true
      }
    };

    // Merge with provided config
    const config = { ...defaultConfig, ...rawData.config };

    // Determine visualization type and format data
    let visualizationData: VisualizationData;

    if (rawData.type === 'physics' && rawData.positions) {
      // Physics simulation data
      visualizationData = {
        type: 'physics',
        data: {
          positions: rawData.positions,
          trajectories: rawData.trajectories,
          colors: rawData.colors || generateColors(rawData.positions[0]?.length || 1)
        },
        config: {
          ...config,
          animation: {
            enabled: true,
            loop: true,
            ...config.animation
          }
        }
      };
    } else if (rawData.type === 'mesh' && rawData.vertices) {
      // Mesh visualization
      visualizationData = {
        type: 'mesh',
        data: {
          vertices: rawData.vertices,
          faces: rawData.faces,
          color: rawData.color || 0x00aa00,
          wireframe: rawData.wireframe || false
        },
        config
      };
    } else if (rawData.type === 'particles' && rawData.positions) {
      // Particle system
      visualizationData = {
        type: 'particles',
        data: {
          positions: rawData.positions,
          color: rawData.color || 0xffffff,
          size: rawData.size || 0.1,
          opacity: rawData.opacity || 0.8
        },
        config: {
          ...config,
          animation: {
            enabled: true,
            loop: true,
            ...config.animation
          }
        }
      };
    } else if (rawData.points || rawData.x || rawData.y || rawData.z) {
      // Plot data - convert to 3D points
      let points: [number, number, number][] = [];
      
      if (rawData.points) {
        points = rawData.points;
      } else if (rawData.x && rawData.y && rawData.z) {
        points = rawData.x.map((x: number, i: number) => [
          x,
          rawData.y[i] || 0,
          rawData.z[i] || 0
        ]);
      } else if (rawData.x && rawData.y) {
        points = rawData.x.map((x: number, i: number) => [
          x,
          rawData.y[i] || 0,
          0
        ]);
      }

      visualizationData = {
        type: 'plot',
        data: {
          points,
          colors: rawData.colors || generateColors(points.length),
          bounds: calculateBounds(points)
        },
        config
      };
    } else {
      // Fallback to empty plot
      visualizationData = {
        type: 'plot',
        data: { points: [] },
        config
      };
    }

    return visualizationData;
  };

  const generateColors = (count: number): number[] => {
    const colors = [];
    for (let i = 0; i < count; i++) {
      const hue = (i * 137.508) % 360; // Golden angle approximation
      colors.push(parseInt(`0x${hslToHex(hue, 70, 50)}`));
    }
    return colors;
  };

  const hslToHex = (h: number, s: number, l: number): string => {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = (n: number) => {
      const k = (n + h / 30) % 12;
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
      return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return `${f(0)}${f(8)}${f(4)}`;
  };

  const calculateBounds = (points: [number, number, number][]) => {
    if (points.length === 0) {
      return { x: [-1, 1], y: [-1, 1], z: [-1, 1] };
    }

    const bounds = {
      x: [Infinity, -Infinity],
      y: [Infinity, -Infinity],
      z: [Infinity, -Infinity]
    };

    points.forEach(([x, y, z]) => {
      bounds.x[0] = Math.min(bounds.x[0], x);
      bounds.x[1] = Math.max(bounds.x[1], x);
      bounds.y[0] = Math.min(bounds.y[0], y);
      bounds.y[1] = Math.max(bounds.y[1], y);
      bounds.z[0] = Math.min(bounds.z[0], z);
      bounds.z[1] = Math.max(bounds.z[1], z);
    });

    return bounds;
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const downloadImage = () => {
    // This would capture the canvas and download as image
    const canvas = document.querySelector('.threejs-canvas-container canvas') as HTMLCanvasElement;
    if (canvas) {
      const link = document.createElement('a');
      link.download = 'visualization.png';
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const visualizationData = parseVisualizationData(data);
  const containerClass = isFullscreen 
    ? 'fixed inset-0 z-50 bg-white p-4' 
    : 'relative';

  return (
    <div className={containerClass}>
      {/* Header with controls */}
      <div className="flex items-center justify-between mb-3 p-2 bg-gray-50 rounded border">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-700">
              3D Visualization
            </span>
            <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
              {visualizationData.type}
            </span>
          </div>
          
          {/* Scene info */}
          <div className="text-xs text-gray-500">
            Objects: {sceneInfo.objects} | 
            Vertices: {sceneInfo.vertices.toLocaleString()} |
            Triangles: {Math.round(sceneInfo.triangles).toLocaleString()}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={downloadImage}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
            title="Download as image"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </button>
          
          <button
            onClick={toggleFullscreen}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Visualization renderer */}
      <ThreeJSRenderer
        data={visualizationData}
        width={isFullscreen ? window.innerWidth - 32 : 800}
        height={isFullscreen ? window.innerHeight - 120 : 600}
        onSceneReady={handleSceneReady}
      />

      {/* Metadata display */}
      {metadata && Object.keys(metadata).length > 0 && (
        <div className="mt-3 p-2 bg-gray-50 rounded border text-xs">
          <div className="font-medium text-gray-700 mb-1">Metadata:</div>
          <div className="text-gray-600">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <span className="font-medium">{key}:</span>
                <span>{JSON.stringify(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
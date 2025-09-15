import { VisualizationData } from '../components/visualization/ThreeJSRenderer';

export interface PhysicsSimulationData {
  positions: number[][][]; // [frame][object][x,y,z]
  velocities?: number[][][];
  forces?: number[][][];
  trajectories?: number[][][]; // [object][point][x,y,z]
  colors?: number[];
  metadata?: {
    timeStep: number;
    totalTime: number;
    objectNames?: string[];
  };
}

export interface PlotData {
  x?: number[];
  y?: number[];
  z?: number[];
  points?: [number, number, number][];
  colors?: number[];
  labels?: string[];
  title?: string;
}

export interface MeshData {
  vertices: number[][];
  faces?: number[][];
  normals?: number[][];
  colors?: number[];
  wireframe?: boolean;
  material?: {
    color?: number;
    opacity?: number;
    metalness?: number;
    roughness?: number;
  };
}

export interface ParticleData {
  positions: number[][][]; // [frame][particle][x,y,z]
  colors?: number[];
  sizes?: number[];
  opacity?: number;
  metadata?: {
    particleCount: number;
    frameCount: number;
  };
}

export class VisualizationService {
  /**
   * Convert physics simulation data to visualization format
   */
  static processPhysicsData(data: PhysicsSimulationData): VisualizationData {
    return {
      type: 'physics',
      data: {
        positions: data.positions,
        trajectories: data.trajectories,
        colors: data.colors || this.generateDefaultColors(data.positions[0]?.length || 1)
      },
      config: {
        camera: {
          position: this.calculateOptimalCameraPosition(data.positions),
          target: [0, 0, 0]
        },
        animation: {
          enabled: true,
          loop: true,
          duration: data.metadata?.totalTime || 5000
        }
      }
    };
  }

  /**
   * Convert plot data to visualization format
   */
  static processPlotData(data: PlotData): VisualizationData {
    let points: [number, number, number][] = [];

    if (data.points) {
      points = data.points;
    } else if (data.x && data.y && data.z) {
      points = data.x.map((x, i) => [x, data.y![i] || 0, data.z![i] || 0]);
    } else if (data.x && data.y) {
      points = data.x.map((x, i) => [x, data.y![i] || 0, 0]);
    } else if (data.x) {
      points = data.x.map((x, i) => [x, i, 0]);
    }

    const bounds = this.calculateBounds(points);

    return {
      type: 'plot',
      data: {
        points,
        colors: data.colors || this.generateDefaultColors(points.length),
        bounds
      },
      config: {
        camera: {
          position: this.calculateOptimalCameraPosition([points]),
          target: [
            (bounds.x[0] + bounds.x[1]) / 2,
            (bounds.y[0] + bounds.y[1]) / 2,
            (bounds.z[0] + bounds.z[1]) / 2
          ]
        }
      }
    };
  }

  /**
   * Convert mesh data to visualization format
   */
  static processMeshData(data: MeshData): VisualizationData {
    return {
      type: 'mesh',
      data: {
        vertices: data.vertices,
        faces: data.faces,
        normals: data.normals,
        color: data.material?.color || 0x00aa00,
        wireframe: data.wireframe || false,
        material: data.material
      },
      config: {
        camera: {
          position: this.calculateOptimalCameraPosition([data.vertices]),
          target: [0, 0, 0]
        }
      }
    };
  }

  /**
   * Convert particle data to visualization format
   */
  static processParticleData(data: ParticleData): VisualizationData {
    return {
      type: 'particles',
      data: {
        positions: data.positions,
        colors: data.colors || this.generateDefaultColors(1),
        sizes: data.sizes || [0.1],
        opacity: data.opacity || 0.8
      },
      config: {
        camera: {
          position: this.calculateOptimalCameraPosition(data.positions),
          target: [0, 0, 0]
        },
        animation: {
          enabled: true,
          loop: true
        }
      }
    };
  }

  /**
   * Generate default colors using golden ratio
   */
  private static generateDefaultColors(count: number): number[] {
    const colors = [];
    for (let i = 0; i < count; i++) {
      const hue = (i * 137.508) % 360; // Golden angle approximation
      colors.push(parseInt(`0x${this.hslToHex(hue, 70, 50)}`));
    }
    return colors;
  }

  /**
   * Convert HSL to hex color
   */
  private static hslToHex(h: number, s: number, l: number): string {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = (n: number) => {
      const k = (n + h / 30) % 12;
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
      return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return `${f(0)}${f(8)}${f(4)}`;
  }

  /**
   * Calculate bounds for a set of points
   */
  private static calculateBounds(points: [number, number, number][]) {
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
  }

  /**
   * Calculate optimal camera position based on data bounds
   */
  private static calculateOptimalCameraPosition(data: number[][][]): [number, number, number] {
    if (!data || data.length === 0) {
      return [5, 5, 5];
    }

    // Flatten all points to calculate overall bounds
    const allPoints: [number, number, number][] = [];
    data.forEach(frame => {
      if (Array.isArray(frame)) {
        frame.forEach(point => {
          if (Array.isArray(point) && point.length >= 3) {
            allPoints.push([point[0], point[1], point[2]]);
          }
        });
      }
    });

    if (allPoints.length === 0) {
      return [5, 5, 5];
    }

    const bounds = this.calculateBounds(allPoints);
    
    // Calculate the maximum extent
    const maxExtent = Math.max(
      bounds.x[1] - bounds.x[0],
      bounds.y[1] - bounds.y[0],
      bounds.z[1] - bounds.z[0]
    );

    // Position camera at a distance that shows the entire scene
    const distance = Math.max(maxExtent * 1.5, 5);
    
    return [distance, distance, distance];
  }

  /**
   * Validate visualization data format
   */
  static validateVisualizationData(data: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data) {
      errors.push('Visualization data is required');
      return { valid: false, errors };
    }

    if (typeof data !== 'object') {
      errors.push('Visualization data must be an object');
      return { valid: false, errors };
    }

    // Check for required fields based on type
    if (data.type === 'physics') {
      if (!data.positions || !Array.isArray(data.positions)) {
        errors.push('Physics visualization requires positions array');
      }
    } else if (data.type === 'mesh') {
      if (!data.vertices || !Array.isArray(data.vertices)) {
        errors.push('Mesh visualization requires vertices array');
      }
    } else if (data.type === 'particles') {
      if (!data.positions || !Array.isArray(data.positions)) {
        errors.push('Particle visualization requires positions array');
      }
    } else if (data.type === 'plot') {
      if (!data.points && !data.x && !data.y) {
        errors.push('Plot visualization requires points, x, or y data');
      }
    }

    return { valid: errors.length === 0, errors };
  }

  /**
   * Create sample visualization data for testing
   */
  static createSampleData(type: 'physics' | 'plot' | 'mesh' | 'particles'): VisualizationData {
    switch (type) {
      case 'physics':
        return this.createSamplePhysicsData();
      case 'plot':
        return this.createSamplePlotData();
      case 'mesh':
        return this.createSampleMeshData();
      case 'particles':
        return this.createSampleParticleData();
      default:
        return this.createSamplePlotData();
    }
  }

  private static createSamplePhysicsData(): VisualizationData {
    const frames = 100;
    const objects = 3;
    const positions = [];

    for (let frame = 0; frame < frames; frame++) {
      const frameData = [];
      for (let obj = 0; obj < objects; obj++) {
        const t = frame / frames * 2 * Math.PI;
        const radius = 2 + obj;
        const x = radius * Math.cos(t + obj * Math.PI / 3);
        const y = radius * Math.sin(t + obj * Math.PI / 3);
        const z = Math.sin(t * 2) * 0.5;
        frameData.push([x, y, z]);
      }
      positions.push(frameData);
    }

    return {
      type: 'physics',
      data: {
        positions,
        colors: [0xff0000, 0x00ff00, 0x0000ff]
      },
      config: {
        animation: { enabled: true, loop: true }
      }
    };
  }

  private static createSamplePlotData(): VisualizationData {
    const points: [number, number, number][] = [];
    for (let i = 0; i < 100; i++) {
      const t = i / 100 * 4 * Math.PI;
      points.push([
        Math.cos(t) * (1 + 0.3 * Math.cos(3 * t)),
        Math.sin(t) * (1 + 0.3 * Math.cos(3 * t)),
        0.3 * Math.sin(3 * t)
      ]);
    }

    return {
      type: 'plot',
      data: { points },
      config: {}
    };
  }

  private static createSampleMeshData(): VisualizationData {
    // Simple cube vertices
    const vertices = [
      [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ];

    const faces = [
      [0, 1, 2], [0, 2, 3], // front
      [4, 7, 6], [4, 6, 5], // back
      [0, 4, 5], [0, 5, 1], // bottom
      [2, 6, 7], [2, 7, 3], // top
      [0, 3, 7], [0, 7, 4], // left
      [1, 5, 6], [1, 6, 2]  // right
    ];

    return {
      type: 'mesh',
      data: { vertices, faces },
      config: {}
    };
  }

  private static createSampleParticleData(): VisualizationData {
    const frames = 50;
    const particleCount = 200;
    const positions = [];

    for (let frame = 0; frame < frames; frame++) {
      const frameData = [];
      for (let i = 0; i < particleCount; i++) {
        const t = frame / frames;
        const angle = i / particleCount * 2 * Math.PI;
        const radius = 1 + t * 2;
        const x = radius * Math.cos(angle + t * Math.PI);
        const y = radius * Math.sin(angle + t * Math.PI);
        const z = Math.sin(t * Math.PI * 2) * 0.5;
        frameData.push([x, y, z]);
      }
      positions.push(frameData);
    }

    return {
      type: 'particles',
      data: { positions },
      config: {
        animation: { enabled: true, loop: true }
      }
    };
  }
}
import { VisualizationService, PhysicsSimulationData, PlotData, MeshData, ParticleData } from '../../services/visualizationService';

describe('VisualizationService', () => {
  describe('processPhysicsData', () => {
    it('processes physics simulation data correctly', () => {
      const physicsData: PhysicsSimulationData = {
        positions: [
          [[0, 0, 0], [1, 1, 1]],
          [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1]]
        ],
        trajectories: [
          [[0, 0, 0], [0.5, 0.5, 0.5], [1, 1, 1]],
          [[1, 1, 1], [1.5, 1.5, 1.5], [2, 2, 2]]
        ],
        colors: [0xff0000, 0x00ff00],
        metadata: {
          timeStep: 0.01,
          totalTime: 1000,
          objectNames: ['Object1', 'Object2']
        }
      };

      const result = VisualizationService.processPhysicsData(physicsData);

      expect(result.type).toBe('physics');
      expect(result.data.positions).toEqual(physicsData.positions);
      expect(result.data.trajectories).toEqual(physicsData.trajectories);
      expect(result.data.colors).toEqual(physicsData.colors);
      expect(result.config?.animation?.enabled).toBe(true);
      expect(result.config?.animation?.duration).toBe(1000);
    });

    it('generates default colors when not provided', () => {
      const physicsData: PhysicsSimulationData = {
        positions: [[[0, 0, 0], [1, 1, 1], [2, 2, 2]]]
      };

      const result = VisualizationService.processPhysicsData(physicsData);

      expect(result.data.colors).toHaveLength(3);
      expect(result.data.colors).toEqual(expect.arrayContaining([expect.any(Number)]));
    });

    it('calculates optimal camera position', () => {
      const physicsData: PhysicsSimulationData = {
        positions: [[[10, 10, 10], [-10, -10, -10]]]
      };

      const result = VisualizationService.processPhysicsData(physicsData);

      expect(result.config?.camera?.position).toEqual(expect.arrayContaining([expect.any(Number)]));
      expect(result.config?.camera?.target).toEqual([0, 0, 0]);
    });
  });

  describe('processPlotData', () => {
    it('processes plot data with points array', () => {
      const plotData: PlotData = {
        points: [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
        colors: [0xff0000, 0x00ff00, 0x0000ff],
        title: 'Test Plot'
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.type).toBe('plot');
      expect(result.data.points).toEqual(plotData.points);
      expect(result.data.colors).toEqual(plotData.colors);
      expect(result.data.bounds).toBeDefined();
    });

    it('processes plot data with x, y, z arrays', () => {
      const plotData: PlotData = {
        x: [1, 2, 3],
        y: [4, 5, 6],
        z: [7, 8, 9]
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.type).toBe('plot');
      expect(result.data.points).toEqual([[1, 4, 7], [2, 5, 8], [3, 6, 9]]);
    });

    it('processes plot data with x, y arrays only', () => {
      const plotData: PlotData = {
        x: [1, 2, 3],
        y: [4, 5, 6]
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.type).toBe('plot');
      expect(result.data.points).toEqual([[1, 4, 0], [2, 5, 0], [3, 6, 0]]);
    });

    it('processes plot data with x array only', () => {
      const plotData: PlotData = {
        x: [1, 2, 3]
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.type).toBe('plot');
      expect(result.data.points).toEqual([[1, 0, 0], [2, 1, 0], [3, 2, 0]]);
    });

    it('generates default colors when not provided', () => {
      const plotData: PlotData = {
        points: [[0, 0, 0], [1, 1, 1]]
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.data.colors).toHaveLength(2);
      expect(result.data.colors).toEqual(expect.arrayContaining([expect.any(Number)]));
    });

    it('calculates bounds correctly', () => {
      const plotData: PlotData = {
        points: [[-5, -3, -1], [5, 3, 1]]
      };

      const result = VisualizationService.processPlotData(plotData);

      expect(result.data.bounds).toEqual({
        x: [-5, 5],
        y: [-3, 3],
        z: [-1, 1]
      });
    });
  });

  describe('processMeshData', () => {
    it('processes mesh data correctly', () => {
      const meshData: MeshData = {
        vertices: [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        faces: [[0, 1, 2]],
        wireframe: true,
        material: {
          color: 0xff0000,
          opacity: 0.8
        }
      };

      const result = VisualizationService.processMeshData(meshData);

      expect(result.type).toBe('mesh');
      expect(result.data.vertices).toEqual(meshData.vertices);
      expect(result.data.faces).toEqual(meshData.faces);
      expect(result.data.wireframe).toBe(true);
      expect(result.data.material).toEqual(meshData.material);
    });

    it('uses default color when not provided', () => {
      const meshData: MeshData = {
        vertices: [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
      };

      const result = VisualizationService.processMeshData(meshData);

      expect(result.data.color).toBe(0x00aa00);
      expect(result.data.wireframe).toBe(false);
    });
  });

  describe('processParticleData', () => {
    it('processes particle data correctly', () => {
      const particleData: ParticleData = {
        positions: [
          [[0, 0, 0], [1, 1, 1]],
          [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1]]
        ],
        colors: [0xff0000],
        sizes: [0.2],
        opacity: 0.9,
        metadata: {
          particleCount: 2,
          frameCount: 2
        }
      };

      const result = VisualizationService.processParticleData(particleData);

      expect(result.type).toBe('particles');
      expect(result.data.positions).toEqual(particleData.positions);
      expect(result.data.colors).toEqual(particleData.colors);
      expect(result.data.sizes).toEqual(particleData.sizes);
      expect(result.data.opacity).toBe(0.9);
      expect(result.config?.animation?.enabled).toBe(true);
    });

    it('uses default values when not provided', () => {
      const particleData: ParticleData = {
        positions: [[[0, 0, 0]]]
      };

      const result = VisualizationService.processParticleData(particleData);

      expect(result.data.colors).toEqual(expect.arrayContaining([expect.any(Number)]));
      expect(result.data.sizes).toEqual([0.1]);
      expect(result.data.opacity).toBe(0.8);
    });
  });

  describe('validateVisualizationData', () => {
    it('validates physics data correctly', () => {
      const validData = {
        type: 'physics',
        positions: [[[0, 0, 0]]]
      };

      const result = VisualizationService.validateVisualizationData(validData);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('validates mesh data correctly', () => {
      const validData = {
        type: 'mesh',
        vertices: [[0, 0, 0]]
      };

      const result = VisualizationService.validateVisualizationData(validData);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('validates plot data correctly', () => {
      const validData = {
        type: 'plot',
        points: [[0, 0, 0]]
      };

      const result = VisualizationService.validateVisualizationData(validData);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('returns errors for invalid data', () => {
      const invalidData = {
        type: 'physics'
        // missing positions
      };

      const result = VisualizationService.validateVisualizationData(invalidData);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Physics visualization requires positions array');
    });

    it('returns errors for null data', () => {
      const result = VisualizationService.validateVisualizationData(null);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Visualization data is required');
    });

    it('returns errors for non-object data', () => {
      const result = VisualizationService.validateVisualizationData('invalid');

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Visualization data must be an object');
    });
  });

  describe('createSampleData', () => {
    it('creates sample physics data', () => {
      const result = VisualizationService.createSampleData('physics');

      expect(result.type).toBe('physics');
      expect(result.data.positions).toBeDefined();
      expect(result.data.colors).toBeDefined();
      expect(result.config?.animation?.enabled).toBe(true);
    });

    it('creates sample plot data', () => {
      const result = VisualizationService.createSampleData('plot');

      expect(result.type).toBe('plot');
      expect(result.data.points).toBeDefined();
      expect(Array.isArray(result.data.points)).toBe(true);
    });

    it('creates sample mesh data', () => {
      const result = VisualizationService.createSampleData('mesh');

      expect(result.type).toBe('mesh');
      expect(result.data.vertices).toBeDefined();
      expect(result.data.faces).toBeDefined();
    });

    it('creates sample particle data', () => {
      const result = VisualizationService.createSampleData('particles');

      expect(result.type).toBe('particles');
      expect(result.data.positions).toBeDefined();
      expect(result.config?.animation?.enabled).toBe(true);
    });

    it('defaults to plot data for unknown type', () => {
      const result = VisualizationService.createSampleData('unknown' as any);

      expect(result.type).toBe('plot');
    });
  });
});
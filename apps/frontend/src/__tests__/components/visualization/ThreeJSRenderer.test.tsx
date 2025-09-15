import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThreeJSRenderer, VisualizationData } from '../../../components/visualization/ThreeJSRenderer';

// Mock Three.js
jest.mock('three', () => ({
  Scene: jest.fn(() => ({
    add: jest.fn(),
    remove: jest.fn(),
    children: [],
    background: null,
    fog: null,
    traverse: jest.fn()
  })),
  PerspectiveCamera: jest.fn(() => ({
    position: { set: jest.fn(), multiplyScalar: jest.fn(), length: jest.fn(() => 5) },
    lookAt: jest.fn(),
    updateControls: jest.fn()
  })),
  WebGLRenderer: jest.fn(() => ({
    setSize: jest.fn(),
    setPixelRatio: jest.fn(),
    render: jest.fn(),
    dispose: jest.fn(),
    domElement: document.createElement('canvas'),
    shadowMap: { enabled: false, type: null }
  })),
  Color: jest.fn(),
  Fog: jest.fn(),
  AmbientLight: jest.fn(() => ({ position: { set: jest.fn() } })),
  DirectionalLight: jest.fn(() => ({ 
    position: { set: jest.fn() },
    castShadow: false,
    shadow: { mapSize: { width: 0, height: 0 } }
  })),
  SphereGeometry: jest.fn(),
  MeshLambertMaterial: jest.fn(),
  Mesh: jest.fn(() => ({
    position: { set: jest.fn() },
    castShadow: false,
    receiveShadow: false
  })),
  BufferGeometry: jest.fn(() => ({
    setAttribute: jest.fn(),
    setIndex: jest.fn(),
    computeVertexNormals: jest.fn(),
    setFromPoints: jest.fn()
  })),
  BufferAttribute: jest.fn(),
  LineBasicMaterial: jest.fn(),
  Line: jest.fn(),
  PointsMaterial: jest.fn(),
  Points: jest.fn(),
  AxesHelper: jest.fn(),
  Vector3: jest.fn(),
  PCFSoftShadowMap: 'PCFSoftShadowMap'
}));

// Mock requestAnimationFrame
global.requestAnimationFrame = jest.fn((cb) => {
  setTimeout(cb, 16);
  return 1;
});

global.cancelAnimationFrame = jest.fn();

describe('ThreeJSRenderer', () => {
  const mockPhysicsData: VisualizationData = {
    type: 'physics',
    data: {
      positions: [
        [[0, 0, 0], [1, 1, 1]],
        [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1]]
      ],
      colors: [0xff0000, 0x00ff00]
    },
    config: {
      animation: { enabled: true, loop: true }
    }
  };

  const mockPlotData: VisualizationData = {
    type: 'plot',
    data: {
      points: [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
      colors: [0xff0000, 0x00ff00, 0x0000ff]
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ThreeJSRenderer data={mockPlotData} />);
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('initializes Three.js scene correctly', async () => {
    const onSceneReady = jest.fn();
    render(
      <ThreeJSRenderer 
        data={mockPlotData} 
        onSceneReady={onSceneReady}
      />
    );

    await waitFor(() => {
      expect(onSceneReady).toHaveBeenCalled();
    });
  });

  it('renders animation controls for physics data', () => {
    render(<ThreeJSRenderer data={mockPhysicsData} />);
    
    expect(screen.getByText('Play')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('does not render animation controls for static plot data', () => {
    render(<ThreeJSRenderer data={mockPlotData} />);
    
    expect(screen.queryByText('Play')).not.toBeInTheDocument();
    expect(screen.queryByText('Reset')).not.toBeInTheDocument();
  });

  it('handles play/pause button clicks', () => {
    render(<ThreeJSRenderer data={mockPhysicsData} />);
    
    const playButton = screen.getByText('Play');
    fireEvent.click(playButton);
    
    expect(screen.getByText('Pause')).toBeInTheDocument();
    
    fireEvent.click(screen.getByText('Pause'));
    expect(screen.getByText('Play')).toBeInTheDocument();
  });

  it('handles frame slider changes', () => {
    render(<ThreeJSRenderer data={mockPhysicsData} />);
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '1' } });
    
    expect(slider).toHaveValue('1');
  });

  it('handles reset button click', () => {
    render(<ThreeJSRenderer data={mockPhysicsData} />);
    
    // Change frame first
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '1' } });
    
    // Reset
    const resetButton = screen.getByText('Reset');
    fireEvent.click(resetButton);
    
    expect(slider).toHaveValue('0');
    expect(screen.getByText('Play')).toBeInTheDocument();
  });

  it('applies custom width and height', () => {
    const { container } = render(
      <ThreeJSRenderer 
        data={mockPlotData} 
        width={1000} 
        height={800} 
      />
    );
    
    const canvasContainer = container.querySelector('.threejs-canvas-container');
    expect(canvasContainer).toHaveStyle({ width: '1000px', height: '800px' });
  });

  it('handles different visualization types', () => {
    const meshData: VisualizationData = {
      type: 'mesh',
      data: {
        vertices: [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        faces: [[0, 1, 2]]
      }
    };

    render(<ThreeJSRenderer data={meshData} />);
    // Should render without errors
  });

  it('handles particle visualization', () => {
    const particleData: VisualizationData = {
      type: 'particles',
      data: {
        positions: [
          [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
          [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1], [2.1, 2.1, 2.1]]
        ]
      },
      config: {
        animation: { enabled: true, loop: true }
      }
    };

    render(<ThreeJSRenderer data={particleData} />);
    
    expect(screen.getByText('Play')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('handles empty or invalid data gracefully', () => {
    const emptyData: VisualizationData = {
      type: 'plot',
      data: { points: [] }
    };

    render(<ThreeJSRenderer data={emptyData} />);
    // Should render without errors
  });

  it('applies camera configuration', () => {
    const dataWithCameraConfig: VisualizationData = {
      type: 'plot',
      data: { points: [[0, 0, 0]] },
      config: {
        camera: {
          position: [10, 10, 10],
          target: [1, 1, 1]
        }
      }
    };

    render(<ThreeJSRenderer data={dataWithCameraConfig} />);
    // Should apply camera settings without errors
  });

  it('applies scene configuration', () => {
    const dataWithSceneConfig: VisualizationData = {
      type: 'plot',
      data: { points: [[0, 0, 0]] },
      config: {
        scene: {
          background: '#ff0000',
          fog: { color: '#ffffff', near: 1, far: 100 }
        }
      }
    };

    render(<ThreeJSRenderer data={dataWithSceneConfig} />);
    // Should apply scene settings without errors
  });

  it('cleans up resources on unmount', () => {
    const { unmount } = render(<ThreeJSRenderer data={mockPlotData} />);
    
    unmount();
    
    expect(global.cancelAnimationFrame).toHaveBeenCalled();
  });
});
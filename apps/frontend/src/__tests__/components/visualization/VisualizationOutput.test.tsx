import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { VisualizationOutput } from '../../../components/visualization/VisualizationOutput';

// Mock ThreeJSRenderer
jest.mock('../../../components/visualization/ThreeJSRenderer', () => ({
  ThreeJSRenderer: ({ data, onSceneReady }: any) => {
    // Simulate scene ready callback
    React.useEffect(() => {
      if (onSceneReady) {
        const mockScene = {
          traverse: jest.fn((callback) => {
            // Mock some mesh objects
            callback({ 
              isMesh: true,
              geometry: { 
                attributes: { position: { count: 100 } },
                index: { count: 300 }
              }
            });
          })
        };
        const mockCamera = {};
        const mockRenderer = {};
        onSceneReady(mockScene, mockCamera, mockRenderer);
      }
    }, [onSceneReady]);

    return (
      <div data-testid="threejs-renderer">
        <canvas data-testid="threejs-canvas" />
        <div>ThreeJS Renderer - Type: {data.type}</div>
      </div>
    );
  }
}));

// Mock Three.js for constructor calls
jest.mock('three', () => ({
  Mesh: function() { return { isMesh: true }; }
}));

describe('VisualizationOutput', () => {
  const mockPhysicsData = {
    type: 'physics',
    positions: [
      [[0, 0, 0], [1, 1, 1]],
      [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1]]
    ],
    colors: [0xff0000, 0x00ff00]
  };

  const mockPlotData = {
    type: 'plot',
    points: [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
  };

  const mockMeshData = {
    type: 'mesh',
    vertices: [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    faces: [[0, 1, 2]]
  };

  const mockMetadata = {
    timestamp: '2023-01-01T00:00:00Z',
    source: 'physics_simulation'
  };

  it('renders without crashing', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    expect(screen.getByText('3D Visualization')).toBeInTheDocument();
  });

  it('displays visualization type correctly', () => {
    render(<VisualizationOutput data={mockPhysicsData} />);
    expect(screen.getByText('physics')).toBeInTheDocument();
  });

  it('renders ThreeJS renderer', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    expect(screen.getByTestId('threejs-renderer')).toBeInTheDocument();
  });

  it('displays scene statistics', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    
    // Scene info should be displayed after scene is ready
    expect(screen.getByText(/Objects:/)).toBeInTheDocument();
    expect(screen.getByText(/Vertices:/)).toBeInTheDocument();
    expect(screen.getByText(/Triangles:/)).toBeInTheDocument();
  });

  it('handles fullscreen toggle', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    
    const fullscreenButton = screen.getByTitle('Enter fullscreen');
    fireEvent.click(fullscreenButton);
    
    expect(screen.getByTitle('Exit fullscreen')).toBeInTheDocument();
  });

  it('handles download image button', () => {
    // Mock canvas toDataURL
    HTMLCanvasElement.prototype.toDataURL = jest.fn(() => 'data:image/png;base64,mock');
    
    // Mock createElement and click
    const mockLink = {
      click: jest.fn(),
      download: '',
      href: ''
    };
    jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);

    render(<VisualizationOutput data={mockPlotData} />);
    
    const downloadButton = screen.getByTitle('Download as image');
    fireEvent.click(downloadButton);
    
    expect(mockLink.click).toHaveBeenCalled();
  });

  it('displays metadata when provided', () => {
    render(<VisualizationOutput data={mockPlotData} metadata={mockMetadata} />);
    
    expect(screen.getByText('Metadata:')).toBeInTheDocument();
    expect(screen.getByText('timestamp:')).toBeInTheDocument();
    expect(screen.getByText('source:')).toBeInTheDocument();
  });

  it('does not display metadata section when not provided', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    
    expect(screen.queryByText('Metadata:')).not.toBeInTheDocument();
  });

  it('parses string data correctly', () => {
    const stringData = JSON.stringify(mockPlotData);
    render(<VisualizationOutput data={stringData} />);
    
    expect(screen.getByText('plot')).toBeInTheDocument();
  });

  it('handles invalid JSON string data', () => {
    const invalidData = 'invalid json string';
    render(<VisualizationOutput data={invalidData} />);
    
    // Should render without crashing and show plot type (fallback)
    expect(screen.getByText('plot')).toBeInTheDocument();
  });

  it('processes physics data correctly', () => {
    render(<VisualizationOutput data={mockPhysicsData} />);
    
    expect(screen.getByText('physics')).toBeInTheDocument();
    expect(screen.getByTestId('threejs-renderer')).toBeInTheDocument();
  });

  it('processes mesh data correctly', () => {
    render(<VisualizationOutput data={mockMeshData} />);
    
    expect(screen.getByText('mesh')).toBeInTheDocument();
    expect(screen.getByTestId('threejs-renderer')).toBeInTheDocument();
  });

  it('processes plot data with x, y, z arrays', () => {
    const xyData = {
      x: [1, 2, 3],
      y: [4, 5, 6],
      z: [7, 8, 9]
    };
    
    render(<VisualizationOutput data={xyData} />);
    
    expect(screen.getByText('plot')).toBeInTheDocument();
  });

  it('processes plot data with x, y arrays only', () => {
    const xyData = {
      x: [1, 2, 3],
      y: [4, 5, 6]
    };
    
    render(<VisualizationOutput data={xyData} />);
    
    expect(screen.getByText('plot')).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
    render(<VisualizationOutput data={{}} />);
    
    expect(screen.getByText('plot')).toBeInTheDocument(); // fallback type
  });

  it('applies fullscreen styles correctly', () => {
    const { container } = render(<VisualizationOutput data={mockPlotData} />);
    
    const fullscreenButton = screen.getByTitle('Enter fullscreen');
    fireEvent.click(fullscreenButton);
    
    const visualizationContainer = container.firstChild as HTMLElement;
    expect(visualizationContainer).toHaveClass('fixed', 'inset-0', 'z-50');
  });

  it('calculates scene statistics correctly', () => {
    render(<VisualizationOutput data={mockPlotData} />);
    
    // After scene ready, should show calculated stats
    expect(screen.getByText(/Objects: \d+/)).toBeInTheDocument();
    expect(screen.getByText(/Vertices: \d+/)).toBeInTheDocument();
    expect(screen.getByText(/Triangles: \d+/)).toBeInTheDocument();
  });

  it('handles particle data correctly', () => {
    const particleData = {
      type: 'particles',
      positions: [
        [[0, 0, 0], [1, 1, 1]],
        [[0.1, 0.1, 0.1], [1.1, 1.1, 1.1]]
      ]
    };
    
    render(<VisualizationOutput data={particleData} />);
    
    expect(screen.getByText('particles')).toBeInTheDocument();
  });
});
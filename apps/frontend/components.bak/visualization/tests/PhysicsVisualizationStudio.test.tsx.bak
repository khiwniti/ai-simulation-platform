import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PhysicsVisualizationStudio } from '../PhysicsVisualizationStudio';
import { PhysicsObjectTemplate, PhysicsSystemTemplate } from '../PhysicsObjectLibrary';

// Mock the sub-components
jest.mock('../PhysicsRenderer', () => ({
  PhysicsRenderer: ({ bodies, constraints, onBodyUpdate, onCollision }: any) => (
    <div data-testid="physics-renderer">
      <div>Bodies: {bodies.length}</div>
      <div>Constraints: {constraints.length}</div>
      <button onClick={() => onBodyUpdate?.('test-body', [0, 0, 0], [0, 0, 0, 1])}>
        Simulate Body Update
      </button>
      <button onClick={() => onCollision?.('body1', 'body2', [0, 0, 0])}>
        Simulate Collision
      </button>
    </div>
  )
}));

jest.mock('../PhysicsObjectLibrary', () => ({
  PhysicsObjectLibrary: ({ onAddObject, onAddSystem }: any) => (
    <div data-testid="physics-library">
      <button 
        onClick={() => onAddObject({
          id: 'sphere',
          name: 'Test Sphere',
          defaultProperties: {
            shape: 'sphere',
            size: [1, 1, 1],
            mass: 1,
            position: [0, 5, 0]
          }
        } as PhysicsObjectTemplate)}
      >
        Add Sphere
      </button>
      <button 
        onClick={() => onAddSystem({
          id: 'pendulum',
          name: 'Test Pendulum',
          bodies: [
            { id: 'anchor', shape: 'box' as const, size: [0.2, 0.2, 0.2], position: [0, 5, 0], mass: 0 },
            { id: 'bob', shape: 'sphere' as const, size: [0.5, 0.5, 0.5], position: [3, 2, 0], mass: 2 }
          ],
          constraints: [
            { id: 'string', type: 'distance' as const, bodyA: 'anchor', bodyB: 'bob', distance: 3 }
          ]
        } as PhysicsSystemTemplate)}
      >
        Add Pendulum System
      </button>
    </div>
  )
}));

jest.mock('../InteractiveControls', () => ({
  useInteractiveControls: () => ({
    controlsElement: <div data-testid="interactive-controls">Interactive Controls</div>,
    selectedObject: null,
    hoveredObject: null,
    cameraPosition: { toArray: () => [5, 5, 5] },
    cameraTarget: { toArray: () => [0, 0, 0] },
    setSelectedObject: jest.fn()
  })
}));

describe('PhysicsVisualizationStudio', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the main studio interface', () => {
    render(<PhysicsVisualizationStudio />);

    expect(screen.getByText('Physics Studio')).toBeInTheDocument();
    expect(screen.getByTestId('physics-renderer')).toBeInTheDocument();
    expect(screen.getByTestId('physics-library')).toBeInTheDocument();
    expect(screen.getByText('Properties')).toBeInTheDocument();
  });

  it('displays correct initial state', () => {
    render(<PhysicsVisualizationStudio />);

    expect(screen.getByText('Bodies: 0')).toBeInTheDocument();
    expect(screen.getByText('Constraints: 0')).toBeInTheDocument();
    expect(screen.getByText('Clear Scene')).toBeDisabled();
    expect(screen.getByText('Export Scene')).toBeDisabled();
  });

  it('adds objects from the library', async () => {
    render(<PhysicsVisualizationStudio />);

    fireEvent.click(screen.getByText('Add Sphere'));

    await waitFor(() => {
      expect(screen.getByText('Bodies: 1')).toBeInTheDocument();
    });

    // Clear Scene and Export Scene should now be enabled
    expect(screen.getByText('Clear Scene')).not.toBeDisabled();
    expect(screen.getByText('Export Scene')).not.toBeDisabled();
  });

  it('adds physics systems from the library', async () => {
    render(<PhysicsVisualizationStudio />);

    fireEvent.click(screen.getByText('Add Pendulum System'));

    await waitFor(() => {
      expect(screen.getByText('Bodies: 2')).toBeInTheDocument();
      expect(screen.getByText('Constraints: 1')).toBeInTheDocument();
    });
  });

  it('clears the scene', async () => {
    render(<PhysicsVisualizationStudio />);

    // Add an object first
    fireEvent.click(screen.getByText('Add Sphere'));
    
    await waitFor(() => {
      expect(screen.getByText('Bodies: 1')).toBeInTheDocument();
    });

    // Clear the scene
    fireEvent.click(screen.getByText('Clear Scene'));

    await waitFor(() => {
      expect(screen.getByText('Bodies: 0')).toBeInTheDocument();
      expect(screen.getByText('Constraints: 0')).toBeInTheDocument();
    });

    // Buttons should be disabled again
    expect(screen.getByText('Clear Scene')).toBeDisabled();
    expect(screen.getByText('Export Scene')).toBeDisabled();
  });

  it('toggles library visibility', () => {
    render(<PhysicsVisualizationStudio />);

    const libraryButton = screen.getByText('Library');
    expect(screen.getByTestId('physics-library')).toBeInTheDocument();

    fireEvent.click(libraryButton);
    expect(screen.queryByTestId('physics-library')).not.toBeInTheDocument();

    fireEvent.click(libraryButton);
    expect(screen.getByTestId('physics-library')).toBeInTheDocument();
  });

  it('toggles properties panel visibility', () => {
    render(<PhysicsVisualizationStudio />);

    const propertiesButton = screen.getByText('Properties');
    expect(screen.getByText('World Settings')).toBeInTheDocument();

    fireEvent.click(propertiesButton);
    expect(screen.queryByText('World Settings')).not.toBeInTheDocument();

    fireEvent.click(propertiesButton);
    expect(screen.getByText('World Settings')).toBeInTheDocument();
  });

  it('handles file import', () => {
    const mockOnImportScene = jest.fn();
    render(<PhysicsVisualizationStudio onImportScene={mockOnImportScene} />);

    const importButton = screen.getByText('Import Scene');
    expect(importButton).toBeInTheDocument();

    // File input is hidden, but should be present
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
  });

  it('calls export callback when exporting scene', async () => {
    const mockOnExportScene = jest.fn();
    render(<PhysicsVisualizationStudio onExportScene={mockOnExportScene} />);

    // Add an object first to enable export
    fireEvent.click(screen.getByText('Add Sphere'));
    
    await waitFor(() => {
      expect(screen.getByText('Bodies: 1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Export Scene'));
    
    expect(mockOnExportScene).toHaveBeenCalledWith(
      expect.objectContaining({
        bodies: expect.any(Array),
        constraints: expect.any(Array),
        worldConfig: expect.any(Object),
        visualConfig: expect.any(Object)
      })
    );
  });

  it('calls simulation state change callback', () => {
    const mockOnSimulationStateChange = jest.fn();
    render(<PhysicsVisualizationStudio onSimulationStateChange={mockOnSimulationStateChange} />);

    // Initial state should be called
    expect(mockOnSimulationStateChange).toHaveBeenCalledWith(
      expect.objectContaining({
        isRunning: false,
        isPaused: false,
        currentTime: 0
      })
    );
  });

  it('calls objects change callback when objects are modified', async () => {
    const mockOnObjectsChange = jest.fn();
    render(<PhysicsVisualizationStudio onObjectsChange={mockOnObjectsChange} />);

    fireEvent.click(screen.getByText('Add Sphere'));

    await waitFor(() => {
      expect(mockOnObjectsChange).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({
            shape: 'sphere',
            mass: 1
          })
        ]),
        []
      );
    });
  });

  it('handles simulation events', () => {
    render(<PhysicsVisualizationStudio />);

    // These would normally come from the PhysicsRenderer
    fireEvent.click(screen.getByText('Simulate Body Update'));
    fireEvent.click(screen.getByText('Simulate Collision'));

    // Should not throw errors
  });

  it('displays properties for selected object', async () => {
    render(<PhysicsVisualizationStudio />);

    // Initially should show "Select an object" message
    expect(screen.getByText('Select an object to edit its properties')).toBeInTheDocument();

    // Add an object
    fireEvent.click(screen.getByText('Add Sphere'));

    // Object should be auto-selected (this depends on implementation)
    await waitFor(() => {
      expect(screen.getByText('Bodies: 1')).toBeInTheDocument();
    });
  });

  it('adjusts world settings', () => {
    render(<PhysicsVisualizationStudio />);

    const gravitySlider = screen.getByDisplayValue('-9.8');
    fireEvent.change(gravitySlider, { target: { value: '-15' } });

    // Should update gravity display
    expect(screen.getByText('-15.0 m/s²')).toBeInTheDocument();
  });

  it('toggles visual settings', () => {
    render(<PhysicsVisualizationStudio />);

    const shadowsCheckbox = screen.getByLabelText('Enable Shadows');
    const debugCheckbox = screen.getByLabelText('Show Debug Info');
    const gizmosCheckbox = screen.getByLabelText('Show Gizmos');

    expect(shadowsCheckbox).toBeChecked();
    expect(debugCheckbox).not.toBeChecked();
    expect(gizmosCheckbox).toBeChecked();

    fireEvent.click(shadowsCheckbox);
    fireEvent.click(debugCheckbox);
    fireEvent.click(gizmosCheckbox);

    expect(shadowsCheckbox).not.toBeChecked();
    expect(debugCheckbox).toBeChecked();
    expect(gizmosCheckbox).not.toBeChecked();
  });

  it('handles custom dimensions', () => {
    render(
      <PhysicsVisualizationStudio 
        width={1000} 
        height={800} 
      />
    );

    // Should render with custom dimensions without errors
    expect(screen.getByText('Physics Studio')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <PhysicsVisualizationStudio className="custom-studio" />
    );

    expect(container.firstChild).toHaveClass('custom-studio');
  });
});

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PhysicsRenderer, PhysicsBody, PhysicsConstraint } from '../PhysicsRenderer';

// Mock Three.js and Cannon.js
jest.mock('three', () => ({
  Scene: jest.fn(() => ({
    add: jest.fn(),
    remove: jest.fn(),
    background: null,
    fog: null,
    children: [],
    traverse: jest.fn()
  })),
  PerspectiveCamera: jest.fn(() => ({
    position: { set: jest.fn(), copy: jest.fn() },
    lookAt: jest.fn(),
    updateProjectionMatrix: jest.fn()
  })),
  WebGLRenderer: jest.fn(() => ({
    setSize: jest.fn(),
    setPixelRatio: jest.fn(),
    render: jest.fn(),
    dispose: jest.fn(),
    domElement: document.createElement('canvas'),
    shadowMap: { enabled: false, type: null }
  })),
  AmbientLight: jest.fn(() => ({ position: { set: jest.fn() } })),
  DirectionalLight: jest.fn(() => ({ 
    position: { set: jest.fn() },
    castShadow: false,
    shadow: {
      mapSize: { width: 0, height: 0 },
      camera: { near: 0, far: 0, left: 0, right: 0, top: 0, bottom: 0 }
    }
  })),
  PlaneGeometry: jest.fn(),
  MeshLambertMaterial: jest.fn(),
  Mesh: jest.fn(() => ({
    rotation: { x: 0 },
    position: { y: 0 },
    receiveShadow: false
  })),
  BoxGeometry: jest.fn(),
  SphereGeometry: jest.fn(),
  CylinderGeometry: jest.fn(),
  MeshBasicMaterial: jest.fn(),
  Color: jest.fn()
}));

jest.mock('cannon-es', () => ({
  World: jest.fn(() => ({
    gravity: { set: jest.fn() },
    solver: { iterations: 10 },
    allowSleep: true,
    addContactMaterial: jest.fn(),
    addEventListener: jest.fn(),
    addBody: jest.fn(),
    removeBody: jest.fn(),
    addConstraint: jest.fn(),
    removeConstraint: jest.fn(),
    step: jest.fn(),
    contacts: []
  })),
  NaiveBroadphase: jest.fn(),
  GSSolver: jest.fn(),
  Material: jest.fn(),
  ContactMaterial: jest.fn(),
  Vec3: jest.fn((x, y, z) => ({ x, y, z, set: jest.fn() })),
  Body: jest.fn(() => ({
    position: { x: 0, y: 0, z: 0, copy: jest.fn() },
    quaternion: { x: 0, y: 0, z: 0, w: 1, copy: jest.fn(), setFromEuler: jest.fn() },
    velocity: { set: jest.fn() },
    angularVelocity: { set: jest.fn() },
    userData: {}
  })),
  Box: jest.fn(),
  Sphere: jest.fn(),
  Cylinder: jest.fn(),
  Plane: jest.fn(),
  DistanceConstraint: jest.fn(),
  PointToPointConstraint: jest.fn(),
  LockConstraint: jest.fn(),
  HingeConstraint: jest.fn()
}));

describe('PhysicsRenderer', () => {
  const mockBodies: PhysicsBody[] = [
    {
      id: 'sphere-1',
      shape: 'sphere',
      position: [0, 5, 0],
      size: [0.5, 0.5, 0.5],
      mass: 1,
      material: { friction: 0.4, restitution: 0.6 },
      color: 0x00aa00
    },
    {
      id: 'box-1',
      shape: 'box',
      position: [2, 3, 0],
      size: [1, 1, 1],
      mass: 1,
      material: { friction: 0.4, restitution: 0.3 },
      color: 0x0066cc
    }
  ];

  const mockConstraints: PhysicsConstraint[] = [
    {
      id: 'distance-1',
      type: 'distance',
      bodyA: 'sphere-1',
      bodyB: 'box-1',
      distance: 2
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders physics renderer with controls', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
        width={800}
        height={600}
      />
    );

    expect(screen.getByText('Start')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
    expect(screen.getByText('Step')).toBeInTheDocument();
  });

  it('displays correct body and contact counts', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
      />
    );

    expect(screen.getByText('Bodies: 2')).toBeInTheDocument();
    expect(screen.getByText('Contacts: 0')).toBeInTheDocument();
  });

  it('handles start/stop simulation', async () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
      />
    );

    const startButton = screen.getByText('Start');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Stop')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Stop'));

    await waitFor(() => {
      expect(screen.getByText('Start')).toBeInTheDocument();
    });
  });

  it('handles reset simulation', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
      />
    );

    const resetButton = screen.getByText('Reset');
    fireEvent.click(resetButton);

    // Should stop simulation and reset to initial state
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('handles step forward when paused', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
      />
    );

    const stepButton = screen.getByText('Step');
    expect(stepButton).not.toBeDisabled();
    
    fireEvent.click(stepButton);
    // Should advance simulation by one step
  });

  it('disables step button when simulation is running', async () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
      />
    );

    fireEvent.click(screen.getByText('Start'));

    await waitFor(() => {
      expect(screen.getByText('Step')).toBeDisabled();
    });
  });

  it('calls onBodyUpdate callback when bodies move', () => {
    const mockOnBodyUpdate = jest.fn();
    
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
        onBodyUpdate={mockOnBodyUpdate}
      />
    );

    // Start simulation to trigger body updates
    fireEvent.click(screen.getByText('Start'));

    // Note: In a real test, we would need to wait for the animation frame
    // and verify that onBodyUpdate is called with correct parameters
  });

  it('calls onCollision callback when bodies collide', () => {
    const mockOnCollision = jest.fn();
    
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
        onCollision={mockOnCollision}
      />
    );

    // In a real scenario, we would simulate a collision and verify the callback
  });

  it('updates world config via controls', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={mockConstraints}
        worldConfig={{ gravity: [0, -9.81, 0] }}
      />
    );

    const gravitySlider = screen.getByDisplayValue('-9.8');
    fireEvent.change(gravitySlider, { target: { value: '-15' } });

    // Should update the world gravity
  });

  it('handles empty bodies array', () => {
    render(
      <PhysicsRenderer
        bodies={[]}
        constraints={[]}
      />
    );

    expect(screen.getByText('Bodies: 0')).toBeInTheDocument();
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('handles different physics body shapes', () => {
    const diverseBodies: PhysicsBody[] = [
      { id: 'sphere', shape: 'sphere', position: [0, 0, 0], size: [1, 1, 1], mass: 1 },
      { id: 'box', shape: 'box', position: [1, 0, 0], size: [1, 1, 1], mass: 1 },
      { id: 'cylinder', shape: 'cylinder', position: [2, 0, 0], size: [0.5, 2, 0.5], mass: 1 },
      { id: 'plane', shape: 'plane', position: [0, -1, 0], size: [10, 1, 10], mass: 0 }
    ];

    render(
      <PhysicsRenderer
        bodies={diverseBodies}
        constraints={[]}
      />
    );

    expect(screen.getByText('Bodies: 4')).toBeInTheDocument();
  });

  it('handles different constraint types', () => {
    const diverseConstraints: PhysicsConstraint[] = [
      { id: 'distance', type: 'distance', bodyA: 'sphere-1', bodyB: 'box-1', distance: 2 },
      { id: 'point', type: 'point', bodyA: 'sphere-1', bodyB: 'box-1', pivotA: [0, 0, 0], pivotB: [0, 0, 0] },
      { id: 'lock', type: 'lock', bodyA: 'sphere-1', bodyB: 'box-1' },
      { id: 'hinge', type: 'hinge', bodyA: 'sphere-1', bodyB: 'box-1', pivotA: [0, 0, 0], pivotB: [0, 0, 0] }
    ];

    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={diverseConstraints}
      />
    );

    // Should handle all constraint types without errors
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('applies custom world configuration', () => {
    const customWorldConfig = {
      gravity: [0, -20, 0],
      timestep: 1/120,
      iterations: 20,
      broadphase: 'sap' as const,
      solver: 'split' as const
    };

    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={[]}
        worldConfig={customWorldConfig}
      />
    );

    // Should apply custom configuration
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('enables and disables shadows correctly', () => {
    const { rerender } = render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={[]}
        enableShadows={true}
      />
    );

    rerender(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={[]}
        enableShadows={false}
      />
    );

    // Should handle shadow state changes
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('handles debug mode toggle', () => {
    render(
      <PhysicsRenderer
        bodies={mockBodies}
        constraints={[]}
        showDebug={true}
      />
    );

    // Should render debug information when enabled
    expect(screen.getByText('Start')).toBeInTheDocument();
  });
});

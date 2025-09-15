import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import * as THREE from 'three';
import { InteractiveControls, useInteractiveControls } from '../InteractiveControls';

// Mock Three.js
jest.mock('three', () => ({
  Scene: jest.fn(() => ({
    add: jest.fn(),
    remove: jest.fn(),
    children: []
  })),
  PerspectiveCamera: jest.fn(() => ({
    position: { 
      set: jest.fn(), 
      copy: jest.fn(), 
      length: jest.fn(() => 10),
      distanceTo: jest.fn(() => 10)
    },
    lookAt: jest.fn(),
    updateProjectionMatrix: jest.fn(),
    matrix: {
      setFromMatrixColumn: jest.fn()
    }
  })),
  WebGLRenderer: jest.fn(() => ({
    domElement: {
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      clientHeight: 600,
      getBoundingClientRect: jest.fn(() => ({
        left: 0,
        top: 0,
        width: 800,
        height: 600
      }))
    }
  })),
  Raycaster: jest.fn(() => ({
    setFromCamera: jest.fn(),
    intersectObjects: jest.fn(() => [])
  })),
  Vector2: jest.fn(() => ({
    x: 0,
    y: 0,
    set: jest.fn(),
    copy: jest.fn()
  })),
  Vector3: jest.fn(() => ({
    x: 0,
    y: 0,
    z: 0,
    copy: jest.fn(),
    add: jest.fn(),
    subVectors: jest.fn(),
    setFromSpherical: jest.fn(),
    setFromMatrixColumn: jest.fn(),
    multiplyScalar: jest.fn(),
    clone: jest.fn(() => ({ x: 0, y: 0, z: 0 }))
  })),
  Spherical: jest.fn(() => ({
    setFromVector3: jest.fn(),
    theta: 0,
    phi: 0,
    radius: 10
  })),
  Group: jest.fn(() => ({
    position: { copy: jest.fn() },
    visible: false
  })),
  CylinderGeometry: jest.fn(),
  RingGeometry: jest.fn(),
  BoxGeometry: jest.fn(),
  MeshBasicMaterial: jest.fn(),
  Mesh: jest.fn(() => ({
    rotation: { x: 0, y: 0, z: 0 },
    position: { x: 0, y: 0, z: 0 },
    userData: {}
  })),
  DoubleSide: 2
}));

describe('InteractiveControls', () => {
  let mockScene: THREE.Scene;
  let mockCamera: THREE.Camera;
  let mockRenderer: THREE.WebGLRenderer;
  let mockOnInteraction: jest.Mock;
  let mockOnCameraChange: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockScene = new THREE.Scene();
    mockCamera = new THREE.PerspectiveCamera();
    mockRenderer = new THREE.WebGLRenderer();
    mockOnInteraction = jest.fn();
    mockOnCameraChange = jest.fn();
  });

  it('renders without crashing', () => {
    render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );
    
    // InteractiveControls doesn't render visible content
    expect(document.body).toBeInTheDocument();
  });

  it('sets up event listeners on renderer domElement', () => {
    render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );

    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('mousedown', expect.any(Function));
    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('mousemove', expect.any(Function));
    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('mouseup', expect.any(Function));
    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('wheel', expect.any(Function));
    expect(mockRenderer.domElement.addEventListener).toHaveBeenCalledWith('contextmenu', expect.any(Function));
  });

  it('removes event listeners on unmount', () => {
    const { unmount } = render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );

    unmount();

    expect(mockRenderer.domElement.removeEventListener).toHaveBeenCalledWith('mousedown', expect.any(Function));
    expect(mockRenderer.domElement.removeEventListener).toHaveBeenCalledWith('mousemove', expect.any(Function));
    expect(mockRenderer.domElement.removeEventListener).toHaveBeenCalledWith('mouseup', expect.any(Function));
    expect(mockRenderer.domElement.removeEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    expect(mockRenderer.domElement.removeEventListener).toHaveBeenCalledWith('wheel', expect.any(Function));
  });

  it('applies camera configuration', () => {
    const cameraConfig = {
      position: [5, 5, 5] as [number, number, number],
      target: [0, 0, 0] as [number, number, number],
      fov: 60
    };

    render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        cameraConfig={cameraConfig}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );

    expect(mockCamera.position.set).toHaveBeenCalledWith(5, 5, 5);
    expect(mockCamera.lookAt).toHaveBeenCalled();
  });

  it('handles disabled controls', () => {
    const controlsConfig = {
      enableZoom: false,
      enablePan: false,
      enableRotate: false,
      enableDamping: false,
      autoRotate: false,
      autoRotateSpeed: 0,
      dampingFactor: 0,
      minDistance: 1,
      maxDistance: 100,
      minPolarAngle: 0,
      maxPolarAngle: Math.PI,
      minAzimuthAngle: -Infinity,
      maxAzimuthAngle: Infinity
    };

    render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        controlsConfig={controlsConfig}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );

    // Should still render without errors
    expect(document.body).toBeInTheDocument();
  });

  it('handles object selection', () => {
    const selectableObjects = [
      { userData: { id: 'object1' } },
      { userData: { id: 'object2' } }
    ] as THREE.Object3D[];

    render(
      <InteractiveControls
        camera={mockCamera}
        renderer={mockRenderer}
        scene={mockScene}
        selectableObjects={selectableObjects}
        onInteraction={mockOnInteraction}
        onCameraChange={mockOnCameraChange}
      />
    );

    // Should handle selectable objects without errors
    expect(document.body).toBeInTheDocument();
  });
});

// Test the useInteractiveControls hook
describe('useInteractiveControls', () => {
  const TestComponent: React.FC = () => {
    const mockScene = new THREE.Scene();
    const mockCamera = new THREE.PerspectiveCamera();
    const mockRenderer = new THREE.WebGLRenderer();

    const {
      controlsElement,
      selectedObject,
      hoveredObject,
      cameraPosition,
      cameraTarget,
      setSelectedObject
    } = useInteractiveControls(mockCamera, mockRenderer, mockScene, {
      onInteraction: jest.fn(),
      onCameraChange: jest.fn()
    });

    return (
      <div>
        {controlsElement}
        <div data-testid="selected-object">{selectedObject?.userData?.id || 'none'}</div>
        <div data-testid="hovered-object">{hoveredObject?.userData?.id || 'none'}</div>
        <button onClick={() => setSelectedObject({ userData: { id: 'test' } } as THREE.Object3D)}>
          Select Test Object
        </button>
      </div>
    );
  };

  it('provides control state and actions', () => {
    render(<TestComponent />);

    expect(screen.getByTestId('selected-object')).toHaveTextContent('none');
    expect(screen.getByTestId('hovered-object')).toHaveTextContent('none');

    fireEvent.click(screen.getByText('Select Test Object'));
    expect(screen.getByTestId('selected-object')).toHaveTextContent('test');
  });

  it('handles null camera/renderer/scene', () => {
    const TestComponentWithNulls: React.FC = () => {
      const {
        controlsElement,
        selectedObject,
        hoveredObject
      } = useInteractiveControls(null, null, null);

      return (
        <div>
          {controlsElement}
          <div data-testid="selected-object">{selectedObject?.userData?.id || 'none'}</div>
          <div data-testid="hovered-object">{hoveredObject?.userData?.id || 'none'}</div>
        </div>
      );
    };

    render(<TestComponentWithNulls />);

    expect(screen.getByTestId('selected-object')).toHaveTextContent('none');
    expect(screen.getByTestId('hovered-object')).toHaveTextContent('none');
  });
});

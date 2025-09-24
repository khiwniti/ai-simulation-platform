'use client';

import React, { useState, useCallback } from 'react';
import { PhysicsBody, PhysicsConstraint } from './PhysicsRenderer';

export interface PhysicsObjectTemplate {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'compound' | 'vehicles' | 'mechanisms' | 'custom';
  icon: string;
  defaultProperties: Partial<PhysicsBody>;
  preview?: string; // Base64 image or icon
}

export interface PhysicsSystemTemplate {
  id: string;
  name: string;
  description: string;
  bodies: PhysicsBody[];
  constraints: PhysicsConstraint[];
  worldConfig?: any;
}

interface PhysicsObjectLibraryProps {
  onAddObject: (template: PhysicsObjectTemplate, position?: [number, number, number]) => void;
  onAddSystem: (template: PhysicsSystemTemplate) => void;
  selectedCategory?: string;
  className?: string;
}

export const PhysicsObjectLibrary: React.FC<PhysicsObjectLibraryProps> = ({
  onAddObject,
  onAddSystem,
  selectedCategory = 'basic',
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'objects' | 'systems'>('objects');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentCategory, setCurrentCategory] = useState(selectedCategory);

  // Predefined physics object templates
  const objectTemplates: PhysicsObjectTemplate[] = [
    // Basic Objects
    {
      id: 'sphere',
      name: 'Sphere',
      description: 'A basic spherical rigid body',
      category: 'basic',
      icon: '🔮',
      defaultProperties: {
        shape: 'sphere',
        size: [0.5, 0.5, 0.5],
        mass: 1,
        material: { friction: 0.4, restitution: 0.6 },
        color: 0x00aa00
      }
    },
    {
      id: 'box',
      name: 'Box',
      description: 'A rectangular rigid body',
      category: 'basic',
      icon: '📦',
      defaultProperties: {
        shape: 'box',
        size: [1, 1, 1],
        mass: 1,
        material: { friction: 0.4, restitution: 0.3 },
        color: 0x0066cc
      }
    },
    {
      id: 'cylinder',
      name: 'Cylinder',
      description: 'A cylindrical rigid body',
      category: 'basic',
      icon: '🥫',
      defaultProperties: {
        shape: 'cylinder',
        size: [0.5, 2, 0.5],
        mass: 1,
        material: { friction: 0.4, restitution: 0.3 },
        color: 0xcc6600
      }
    },
    {
      id: 'ground-plane',
      name: 'Ground Plane',
      description: 'An infinite static ground plane',
      category: 'basic',
      icon: '🌍',
      defaultProperties: {
        shape: 'plane',
        size: [50, 1, 50],
        mass: 0,
        position: [0, -1, 0],
        rotation: [-Math.PI / 2, 0, 0],
        material: { friction: 0.8, restitution: 0.1 },
        color: 0x90EE90
      }
    },
    
    // Compound Objects
    {
      id: 'domino',
      name: 'Domino',
      description: 'A thin rectangular block perfect for domino chains',
      category: 'compound',
      icon: '🀫',
      defaultProperties: {
        shape: 'box',
        size: [0.1, 2, 1],
        mass: 0.5,
        material: { friction: 0.6, restitution: 0.2 },
        color: 0xffffff
      }
    },
    {
      id: 'bowling-ball',
      name: 'Bowling Ball',
      description: 'A heavy sphere for knocking things down',
      category: 'compound',
      icon: '🎳',
      defaultProperties: {
        shape: 'sphere',
        size: [0.8, 0.8, 0.8],
        mass: 5,
        material: { friction: 0.7, restitution: 0.2 },
        color: 0x111111
      }
    },
    {
      id: 'bouncy-ball',
      name: 'Bouncy Ball',
      description: 'A highly elastic sphere that bounces a lot',
      category: 'compound',
      icon: '⚾',
      defaultProperties: {
        shape: 'sphere',
        size: [0.3, 0.3, 0.3],
        mass: 0.2,
        material: { friction: 0.3, restitution: 0.9 },
        color: 0xff0000
      }
    },
    
    // Vehicle Parts
    {
      id: 'wheel',
      name: 'Wheel',
      description: 'A wheel for vehicles and mechanisms',
      category: 'vehicles',
      icon: '🛞',
      defaultProperties: {
        shape: 'cylinder',
        size: [0.8, 0.3, 0.8],
        mass: 2,
        material: { friction: 0.9, restitution: 0.3 },
        color: 0x333333
      }
    },
    {
      id: 'chassis',
      name: 'Chassis',
      description: 'A vehicle chassis or platform',
      category: 'vehicles',
      icon: '🚗',
      defaultProperties: {
        shape: 'box',
        size: [4, 0.5, 2],
        mass: 10,
        material: { friction: 0.5, restitution: 0.1 },
        color: 0x666666
      }
    },
    
    // Mechanisms
    {
      id: 'pendulum-bob',
      name: 'Pendulum Bob',
      description: 'A heavy sphere for pendulum systems',
      category: 'mechanisms',
      icon: '🔸',
      defaultProperties: {
        shape: 'sphere',
        size: [0.4, 0.4, 0.4],
        mass: 2,
        material: { friction: 0.2, restitution: 0.1 },
        color: 0xffd700
      }
    },
    {
      id: 'lever-arm',
      name: 'Lever Arm',
      description: 'A long rigid bar for lever mechanisms',
      category: 'mechanisms',
      icon: '📏',
      defaultProperties: {
        shape: 'box',
        size: [6, 0.2, 0.2],
        mass: 1,
        material: { friction: 0.4, restitution: 0.2 },
        color: 0x8B4513
      }
    },
    {
      id: 'gear',
      name: 'Gear',
      description: 'A circular disc for gear mechanisms',
      category: 'mechanisms',
      icon: '⚙️',
      defaultProperties: {
        shape: 'cylinder',
        size: [1, 0.2, 1],
        mass: 1.5,
        material: { friction: 0.6, restitution: 0.1 },
        color: 0x888888
      }
    }
  ];

  // Predefined physics system templates
  const systemTemplates: PhysicsSystemTemplate[] = [
    {
      id: 'domino-chain',
      name: 'Domino Chain',
      description: 'A chain of dominoes ready to fall',
      bodies: Array.from({ length: 10 }, (_, i) => ({
        id: `domino-${i}`,
        shape: 'box' as const,
        size: [0.1, 2, 1] as [number, number, number],
        position: [i * 1.2, 1, 0] as [number, number, number],
        mass: 0.5,
        material: { friction: 0.6, restitution: 0.2 },
        color: 0xffffff
      })),
      constraints: []
    },
    {
      id: 'pendulum',
      name: 'Simple Pendulum',
      description: 'A classic pendulum system',
      bodies: [
        {
          id: 'anchor',
          shape: 'box',
          size: [0.2, 0.2, 0.2],
          position: [0, 5, 0],
          mass: 0, // Static
          material: { friction: 0.5, restitution: 0.1 },
          color: 0x666666
        },
        {
          id: 'pendulum-bob',
          shape: 'sphere',
          size: [0.5, 0.5, 0.5],
          position: [3, 2, 0],
          mass: 2,
          material: { friction: 0.2, restitution: 0.1 },
          color: 0xffd700
        }
      ],
      constraints: [
        {
          id: 'pendulum-string',
          type: 'distance',
          bodyA: 'anchor',
          bodyB: 'pendulum-bob',
          distance: 3
        }
      ]
    },
    {
      id: 'seesaw',
      name: 'Seesaw',
      description: 'A balanced seesaw mechanism',
      bodies: [
        {
          id: 'fulcrum',
          shape: 'box',
          size: [0.5, 1, 0.5],
          position: [0, 0.5, 0],
          mass: 0, // Static
          material: { friction: 0.8, restitution: 0.1 },
          color: 0x8B4513
        },
        {
          id: 'lever',
          shape: 'box',
          size: [8, 0.2, 0.5],
          position: [0, 1.5, 0],
          mass: 2,
          material: { friction: 0.5, restitution: 0.2 },
          color: 0xDEB887
        }
      ],
      constraints: [
        {
          id: 'seesaw-hinge',
          type: 'hinge',
          bodyA: 'fulcrum',
          bodyB: 'lever',
          pivotA: [0, 0.5, 0],
          pivotB: [0, 0, 0]
        }
      ]
    },
    {
      id: 'newton-cradle',
      name: 'Newton\'s Cradle',
      description: 'A physics demonstration of momentum conservation',
      bodies: [
        ...Array.from({ length: 5 }, (_, i) => ({
          id: `anchor-${i}`,
          shape: 'box' as const,
          size: [0.1, 0.1, 0.1] as [number, number, number],
          position: [i * 1 - 2, 5, 0] as [number, number, number],
          mass: 0, // Static
          material: { friction: 0.5, restitution: 0.1 },
          color: 0x444444
        })),
        ...Array.from({ length: 5 }, (_, i) => ({
          id: `ball-${i}`,
          shape: 'sphere' as const,
          size: [0.4, 0.4, 0.4] as [number, number, number],
          position: [i * 1 - 2, 2, 0] as [number, number, number],
          mass: 1,
          material: { friction: 0.1, restitution: 0.8 },
          color: 0xc0c0c0
        }))
      ],
      constraints: Array.from({ length: 5 }, (_, i) => ({
        id: `string-${i}`,
        type: 'distance' as const,
        bodyA: `anchor-${i}`,
        bodyB: `ball-${i}`,
        distance: 3
      }))
    },
    {
      id: 'tower-collapse',
      name: 'Tower Collapse',
      description: 'A tower of blocks ready to be knocked down',
      bodies: [
        // Base layer
        ...Array.from({ length: 4 }, (_, i) => ({
          id: `base-${i}`,
          shape: 'box' as const,
          size: [1, 1, 1] as [number, number, number],
          position: [i * 1.1 - 1.65, 0.5, 0] as [number, number, number],
          mass: 1,
          material: { friction: 0.6, restitution: 0.3 },
          color: 0x8B4513
        })),
        // Second layer
        ...Array.from({ length: 3 }, (_, i) => ({
          id: `mid-${i}`,
          shape: 'box' as const,
          size: [1, 1, 1] as [number, number, number],
          position: [i * 1.1 - 1.1, 1.5, 0] as [number, number, number],
          mass: 1,
          material: { friction: 0.6, restitution: 0.3 },
          color: 0xDEB887
        })),
        // Top layer
        ...Array.from({ length: 2 }, (_, i) => ({
          id: `top-${i}`,
          shape: 'box' as const,
          size: [1, 1, 1] as [number, number, number],
          position: [i * 1.1 - 0.55, 2.5, 0] as [number, number, number],
          mass: 1,
          material: { friction: 0.6, restitution: 0.3 },
          color: 0xF4A460
        })),
        // Wrecking ball
        {
          id: 'wrecking-ball',
          shape: 'sphere',
          size: [1, 1, 1],
          position: [-8, 8, 0],
          mass: 10,
          material: { friction: 0.3, restitution: 0.7 },
          color: 0x696969
        },
        // Crane anchor
        {
          id: 'crane',
          shape: 'box',
          size: [0.2, 0.2, 0.2],
          position: [-8, 12, 0],
          mass: 0, // Static
          material: { friction: 0.5, restitution: 0.1 },
          color: 0x333333
        }
      ],
      constraints: [
        {
          id: 'crane-cable',
          type: 'distance',
          bodyA: 'crane',
          bodyB: 'wrecking-ball',
          distance: 4
        }
      ]
    }
  ];

  const categories = [
    { id: 'basic', name: 'Basic Shapes', icon: '🔷' },
    { id: 'compound', name: 'Compound Objects', icon: '🏗️' },
    { id: 'vehicles', name: 'Vehicle Parts', icon: '🚗' },
    { id: 'mechanisms', name: 'Mechanisms', icon: '⚙️' },
    { id: 'custom', name: 'Custom', icon: '🎨' }
  ];

  const filteredObjects = objectTemplates.filter(template => {
    const matchesCategory = currentCategory === 'all' || template.category === currentCategory;
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const filteredSystems = systemTemplates.filter(template => {
    return template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           template.description.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const handleObjectClick = useCallback((template: PhysicsObjectTemplate) => {
    onAddObject(template);
  }, [onAddObject]);

  const handleSystemClick = useCallback((template: PhysicsSystemTemplate) => {
    onAddSystem(template);
  }, [onAddSystem]);

  return (
    <div className={`physics-object-library bg-white border rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Physics Library</h3>
        
        {/* Tabs */}
        <div className="flex gap-1 mb-3">
          <button
            onClick={() => setActiveTab('objects')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              activeTab === 'objects' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Objects
          </button>
          <button
            onClick={() => setActiveTab('systems')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              activeTab === 'systems' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Systems
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'objects' && (
          <>
            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-4">
              <button
                onClick={() => setCurrentCategory('all')}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  currentCategory === 'all'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setCurrentCategory(category.id)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    currentCategory === category.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {category.icon} {category.name}
                </button>
              ))}
            </div>

            {/* Objects Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {filteredObjects.map(template => (
                <div
                  key={template.id}
                  onClick={() => handleObjectClick(template)}
                  className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">{template.icon}</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-800 text-sm">{template.name}</h4>
                      <p className="text-xs text-gray-600 mt-1">{template.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          {template.defaultProperties.shape}
                        </span>
                        <span className="text-xs text-gray-500">
                          Mass: {template.defaultProperties.mass}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {activeTab === 'systems' && (
          <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
            {filteredSystems.map(template => (
              <div
                key={template.id}
                onClick={() => handleSystemClick(template)}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
              >
                <h4 className="font-medium text-gray-800 mb-2">{template.name}</h4>
                <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{template.bodies.length} Bodies</span>
                  <span>{template.constraints.length} Constraints</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="p-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
        💡 Click on any object or system to add it to your scene
      </div>
    </div>
  );
};

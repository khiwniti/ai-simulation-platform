'use client';

import React, { useRef, useCallback, useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Cell } from '@ai-jupyter/shared';
import { PhysicsVisualizationStudio, SimulationState } from '../../visualization/PhysicsVisualizationStudio';
import { PhysicsBody, PhysicsConstraint } from '../../visualization/PhysicsRenderer';

interface PhysicsVisualizationCellProps {
  cell: Cell;
  isSelected: boolean;
  isFocused: boolean;
  onContentChange: (content: string) => void;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onExecute?: (code: string) => Promise<any>;
}

interface PhysicsSimulationResult {
  type: 'physics_simulation';
  bodies: PhysicsBody[];
  constraints: PhysicsConstraint[];
  worldConfig?: any;
  frames?: any[];
  metadata?: {
    duration: number;
    steps: number;
    fps: number;
  };
}

export const PhysicsVisualizationCell: React.FC<PhysicsVisualizationCellProps> = ({
  cell,
  isSelected,
  isFocused,
  onContentChange,
  onFocus,
  onBlur,
  onKeyDown,
  onExecute
}) => {
  const editorRef = useRef<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<PhysicsSimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [simulationState, setSimulationState] = useState<SimulationState>({
    isRunning: false,
    isPaused: false,
    currentTime: 0,
    timeStep: 1/60,
    totalSteps: 0
  });

  const handleEditorDidMount = useCallback((editor: any, monaco: any) => {
    editorRef.current = editor;

    // Physics-specific completions
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          // Physics World Setup
          {
            label: 'physics_world_setup',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: [
              'import physics_sim as ps',
              '',
              '# Create physics world',
              'world = ps.World(gravity=[0, -9.81, 0])',
              'world.set_timestep(1/60)',
              'world.set_solver_iterations(10)',
              '',
              '# Add ground plane',
              'ground = ps.create_plane(position=[0, -1, 0], size=[20, 1, 20])',
              'world.add_body(ground)'
            ].join('\n'),
            documentation: 'Set up a basic physics world with gravity and ground plane'
          },

          // Rigid Body Creation
          {
            label: 'create_rigid_bodies',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Create rigid bodies',
              'sphere = ps.create_sphere(',
              '    position=[0, 5, 0],',
              '    radius=0.5,',
              '    mass=1.0,',
              '    material=ps.Material(friction=0.4, restitution=0.6)',
              ')',
              '',
              'box = ps.create_box(',
              '    position=[2, 5, 0],',
              '    size=[1, 1, 1],',
              '    mass=1.0,',
              '    material=ps.Material(friction=0.4, restitution=0.3)',
              ')',
              '',
              'world.add_body(sphere)',
              'world.add_body(box)'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create sphere and box rigid bodies'
          },

          // Constraints and Joints
          {
            label: 'create_constraints',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Create constraints',
              'anchor = ps.create_box(position=[0, 8, 0], size=[0.2, 0.2, 0.2], mass=0)',
              'ball = ps.create_sphere(position=[3, 5, 0], radius=0.3, mass=1)',
              '',
              '# Distance constraint (rope/string)',
              'rope = ps.DistanceConstraint(',
              '    body_a=anchor,',
              '    body_b=ball,',
              '    distance=3.0',
              ')',
              '',
              '# Hinge constraint (door/pendulum)',
              'hinge = ps.HingeConstraint(',
              '    body_a=anchor,',
              '    body_b=ball,',
              '    pivot_a=[0, 0, 0],',
              '    pivot_b=[0, 1, 0],',
              '    axis=[0, 0, 1]',
              ')',
              '',
              'world.add_constraint(rope)'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create distance and hinge constraints'
          },

          // Complex Systems
          {
            label: 'domino_chain',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Create domino chain',
              'dominoes = []',
              'for i in range(10):',
              '    domino = ps.create_box(',
              '        position=[i * 1.2, 1, 0],',
              '        size=[0.1, 2, 1],',
              '        mass=0.5,',
              '        material=ps.Material(friction=0.6, restitution=0.2)',
              '    )',
              '    dominoes.append(domino)',
              '    world.add_body(domino)',
              '',
              '# Push the first domino',
              'dominoes[0].apply_impulse([5, 0, 0], [0, 1, 0])'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a chain of falling dominoes'
          },

          // Simulation Execution
          {
            label: 'run_simulation',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Run physics simulation',
              'simulation = ps.Simulation(world)',
              'simulation.set_duration(5.0)  # 5 seconds',
              'simulation.set_frame_rate(60)  # 60 FPS',
              '',
              '# Run and collect data',
              'results = simulation.run()',
              '',
              '# Extract visualization data',
              'viz_data = {',
              '    "type": "physics_simulation",',
              '    "bodies": results.get_body_definitions(),',
              '    "constraints": results.get_constraint_definitions(),',
              '    "frames": results.get_frame_data(),',
              '    "worldConfig": {',
              '        "gravity": world.gravity,',
              '        "timestep": world.timestep',
              '    },',
              '    "metadata": {',
              '        "duration": results.duration,',
              '        "steps": results.total_steps,',
              '        "fps": simulation.frame_rate',
              '    }',
              '}',
              '',
              '# Return for visualization',
              'viz_data'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Run physics simulation and prepare visualization data'
          },

          // Forces and Impulses
          {
            label: 'apply_forces',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Apply forces and impulses',
              '',
              '# Continuous force (like wind)',
              'body.add_force([10, 0, 0])  # Force in newtons',
              '',
              '# Impulse (instant velocity change)',
              'body.apply_impulse(',
              '    impulse=[5, 0, 0],      # Impulse vector',
              '    point=[0, 0.5, 0]       # Application point (relative to body)',
              ')',
              '',
              '# Torque (rotational force)',
              'body.add_torque([0, 10, 0])  # Torque around Y axis',
              '',
              '# Set velocity directly',
              'body.set_velocity([2, 0, 0])           # Linear velocity',
              'body.set_angular_velocity([0, 1, 0])   # Angular velocity'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Apply forces, impulses, and set velocities'
          },

          // Material Properties
          {
            label: 'material_properties',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Material property examples',
              '',
              '# Bouncy ball',
              'bouncy_material = ps.Material(',
              '    friction=0.3,',
              '    restitution=0.9,  # High bounce',
              '    density=0.5',
              ')',
              '',
              '# Sticky surface',
              'sticky_material = ps.Material(',
              '    friction=1.0,     # High friction',
              '    restitution=0.1,  # Low bounce',
              '    density=2.0',
              ')',
              '',
              '# Ice (slippery)',
              'ice_material = ps.Material(',
              '    friction=0.05,    # Very low friction',
              '    restitution=0.1,',
              '    density=0.9',
              ')',
              '',
              '# Apply to body',
              'body.set_material(bouncy_material)'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Define and apply different material properties'
          },

          // Collision Detection
          {
            label: 'collision_detection',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Collision detection and response',
              '',
              'def on_collision(contact):',
              '    body_a = contact.body_a',
              '    body_b = contact.body_b',
              '    contact_point = contact.point',
              '    contact_normal = contact.normal',
              '    ',
              '    print(f"Collision between {body_a.name} and {body_b.name}")',
              '    print(f"Contact point: {contact_point}")',
              '    print(f"Impact force: {contact.impulse}")',
              '    ',
              '    # Custom response (e.g., change color, play sound)',
              '    body_a.set_color([1, 0, 0])  # Turn red on collision',
              '',
              '# Register collision callback',
              'world.set_collision_callback(on_collision)',
              '',
              '# Collision filtering',
              'body_a.set_collision_group(1)    # Group 1',
              'body_b.set_collision_group(2)    # Group 2',
              'body_a.set_collision_mask(2)     # Only collide with group 2',
              'body_b.set_collision_mask(1)     # Only collide with group 1'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Handle collision detection and response'
          }
        ];

        return { suggestions };
      }
    });

    // Execute on Ctrl+Enter
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      handleExecuteCell();
    });

    editor.onDidFocusEditorText(() => {
      onFocus();
    });

    editor.onDidBlurEditorText(() => {
      onBlur();
    });
  }, [onFocus, onBlur]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    onContentChange(value || '');
  }, [onContentChange]);

  const handleExecuteCell = useCallback(async () => {
    if (!onExecute || isExecuting) return;

    setIsExecuting(true);
    setError(null);

    try {
      const result = await onExecute(cell.content);
      
      // Check if the result is physics simulation data
      if (result && typeof result === 'object' && result.type === 'physics_simulation') {
        setExecutionResult(result as PhysicsSimulationResult);
      } else {
        // Handle other types of results or convert to physics format
        console.log('Execution result:', result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
      setExecutionResult(null);
    } finally {
      setIsExecuting(false);
    }
  }, [cell.content, onExecute, isExecuting]);

  const handleSimulationStateChange = useCallback((state: SimulationState) => {
    setSimulationState(state);
  }, []);

  const handleObjectsChange = useCallback((bodies: PhysicsBody[], constraints: PhysicsConstraint[]) => {
    // Update the execution result when objects change in the studio
    if (executionResult) {
      setExecutionResult(prev => prev ? {
        ...prev,
        bodies,
        constraints
      } : null);
    }
  }, [executionResult]);

  const getEditorHeight = () => {
    const lines = cell.content.split('\n').length;
    const minHeight = 150;
    const maxHeight = 400;
    const lineHeight = 20;
    const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, lines * lineHeight + 40));
    return calculatedHeight;
  };

  return (
    <div className="physics-visualization-cell">
      {/* Cell Header */}
      <div className="physics-cell-header bg-purple-50 px-4 py-2 border-b border-purple-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span className="text-sm font-medium text-purple-700">
              Physics Visualization Cell
            </span>
            <span className="text-xs text-purple-600">
              3D Physics Simulation
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {simulationState.isRunning && (
              <div className="flex items-center gap-1 text-xs text-purple-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Running</span>
              </div>
            )}
            
            <button
              onClick={handleExecuteCell}
              disabled={isExecuting}
              className="px-3 py-1 bg-purple-500 text-white rounded text-sm hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExecuting ? 'Executing...' : 'Execute'}
            </button>
          </div>
        </div>
      </div>

      {/* Code Editor */}
      <div 
        className="physics-code-editor"
        data-focusable="true"
        tabIndex={0}
        onKeyDown={onKeyDown}
      >
        <Editor
          height={getEditorHeight()}
          defaultLanguage="python"
          value={cell.content}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={isSelected ? 'vs' : 'vs'}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            lineNumbers: 'on',
            glyphMargin: false,
            folding: true,
            lineDecorationsWidth: 0,
            lineNumbersMinChars: 3,
            renderLineHighlight: isFocused ? 'line' : 'none',
            selectOnLineNumbers: true,
            automaticLayout: true,
            wordWrap: 'on',
            contextmenu: true,
            quickSuggestions: {
              other: true,
              comments: false,
              strings: false
            },
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnEnter: 'on',
            tabCompletion: 'on',
            parameterHints: {
              enabled: true
            },
            hover: {
              enabled: true
            },
            bracketPairColorization: {
              enabled: true
            },
            guides: {
              indentation: true,
              bracketPairs: true
            }
          }}
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-display bg-red-50 border border-red-200 rounded p-3 m-3">
          <div className="flex items-start gap-2">
            <div className="text-red-500 text-sm">⚠️</div>
            <div>
              <div className="text-red-700 font-medium text-sm">Execution Error</div>
              <div className="text-red-600 text-sm mt-1 font-mono">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Physics Visualization Output */}
      {executionResult && (
        <div className="physics-output mt-3">
          <div className="bg-gray-50 border-t border-gray-200 p-2">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Physics Simulation Result</span>
              </div>
              
              {executionResult.metadata && (
                <div className="text-xs text-gray-500">
                  {executionResult.metadata.duration.toFixed(2)}s • {executionResult.metadata.steps} steps • {executionResult.metadata.fps} FPS
                </div>
              )}
            </div>

            <PhysicsVisualizationStudio
              width={800}
              height={500}
              onSimulationStateChange={handleSimulationStateChange}
              onObjectsChange={handleObjectsChange}
              className="border border-gray-300 rounded"
            />
          </div>
        </div>
      )}

      {/* Loading State */}
      {isExecuting && (
        <div className="execution-loading bg-blue-50 border border-blue-200 rounded p-3 m-3">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-blue-700 text-sm">Executing physics simulation...</span>
          </div>
        </div>
      )}
    </div>
  );
};

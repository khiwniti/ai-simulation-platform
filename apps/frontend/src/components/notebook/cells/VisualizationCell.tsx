'use client';

import React, { useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { Cell } from '@ai-jupyter/shared';

interface VisualizationCellProps {
  cell: Cell;
  isSelected: boolean;
  isFocused: boolean;
  onContentChange: (content: string) => void;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

export const VisualizationCell: React.FC<VisualizationCellProps> = ({
  cell,
  isSelected,
  isFocused,
  onContentChange,
  onFocus,
  onBlur,
  onKeyDown
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = useCallback((editor: any, monaco: any) => {
    editorRef.current = editor;

    // Visualization-specific completions
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          // Plotting libraries
          {
            label: 'matplotlib_setup',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: [
              'import matplotlib.pyplot as plt',
              'import numpy as np',
              'from mpl_toolkits.mplot3d import Axes3D'
            ].join('\n'),
            documentation: 'Import matplotlib for plotting'
          },
          
          {
            label: 'three_js_setup',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: [
              'import three_js_bridge as three',
              '# Create 3D scene for interactive visualization',
              'scene = three.Scene()',
              'camera = three.PerspectiveCamera(75, 16/9, 0.1, 1000)',
              'renderer = three.WebGLRenderer()'
            ].join('\n'),
            documentation: 'Set up Three.js for 3D visualization'
          },
          
          // 3D plotting
          {
            label: 'plot_3d_scatter',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'fig = plt.figure(figsize=(${1:10}, ${2:8}))',
              'ax = fig.add_subplot(111, projection=\'3d\')',
              '',
              '# Your data',
              'x = ${3:x_data}',
              'y = ${4:y_data}',
              'z = ${5:z_data}',
              '',
              'ax.scatter(x, y, z, c=${6:\'blue\'}, marker=${7:\'o\'})',
              'ax.set_xlabel(\'X Label\')',
              'ax.set_ylabel(\'Y Label\')',
              'ax.set_zlabel(\'Z Label\')',
              'plt.title(\'${8:3D Scatter Plot}\')',
              'plt.show()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a 3D scatter plot'
          },
          
          {
            label: 'plot_physics_trajectory',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'fig = plt.figure(figsize=(12, 8))',
              'ax = fig.add_subplot(111, projection=\'3d\')',
              '',
              '# Physics trajectory data',
              'positions = ${1:physics_positions}  # Shape: (time_steps, num_objects, 3)',
              '',
              'for obj_idx in range(positions.shape[1]):',
              '    trajectory = positions[:, obj_idx, :]',
              '    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], ',
              '           label=f\'Object {obj_idx}\', linewidth=2)',
              '',
              'ax.set_xlabel(\'X Position (m)\')',
              'ax.set_ylabel(\'Y Position (m)\')',
              'ax.set_zlabel(\'Z Position (m)\')',
              'ax.legend()',
              'plt.title(\'Physics Simulation Trajectories\')',
              'plt.show()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Plot physics simulation trajectories'
          },
          
          // Interactive visualizations
          {
            label: 'interactive_3d_scene',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              '# Create interactive 3D scene',
              'scene = three.Scene()',
              'camera = three.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000)',
              'renderer = three.WebGLRenderer()',
              '',
              '# Add objects to scene',
              'geometry = three.${1:BoxGeometry}(${2:1}, ${3:1}, ${4:1})',
              'material = three.MeshBasicMaterial({\'color\': ${5:0x00ff00}})',
              'cube = three.Mesh(geometry, material)',
              'scene.add(cube)',
              '',
              '# Position camera',
              'camera.position.z = 5',
              '',
              '# Animation loop',
              'def animate():',
              '    cube.rotation.x += 0.01',
              '    cube.rotation.y += 0.01',
              '    renderer.render(scene, camera)',
              '',
              'animate()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create an interactive 3D scene with Three.js'
          },
          
          // Data visualization
          {
            label: 'plot_simulation_data',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'fig, axes = plt.subplots(2, 2, figsize=(15, 10))',
              '',
              '# Position over time',
              'axes[0, 0].plot(${1:time}, ${2:positions})',
              'axes[0, 0].set_title(\'Position vs Time\')',
              'axes[0, 0].set_xlabel(\'Time (s)\')',
              'axes[0, 0].set_ylabel(\'Position (m)\')',
              '',
              '# Velocity over time',
              'axes[0, 1].plot(${3:time}, ${4:velocities})',
              'axes[0, 1].set_title(\'Velocity vs Time\')',
              'axes[0, 1].set_xlabel(\'Time (s)\')',
              'axes[0, 1].set_ylabel(\'Velocity (m/s)\')',
              '',
              '# Energy over time',
              'axes[1, 0].plot(${5:time}, ${6:kinetic_energy}, label=\'Kinetic\')',
              'axes[1, 0].plot(${7:time}, ${8:potential_energy}, label=\'Potential\')',
              'axes[1, 0].set_title(\'Energy vs Time\')',
              'axes[1, 0].set_xlabel(\'Time (s)\')',
              'axes[1, 0].set_ylabel(\'Energy (J)\')',
              'axes[1, 0].legend()',
              '',
              '# Phase space',
              'axes[1, 1].plot(${9:positions}, ${10:velocities})',
              'axes[1, 1].set_title(\'Phase Space\')',
              'axes[1, 1].set_xlabel(\'Position (m)\')',
              'axes[1, 1].set_ylabel(\'Velocity (m/s)\')',
              '',
              'plt.tight_layout()',
              'plt.show()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create comprehensive simulation data visualization'
          },
          
          // Animation
          {
            label: 'animate_simulation',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'from matplotlib.animation import FuncAnimation',
              '',
              'fig = plt.figure(figsize=(10, 8))',
              'ax = fig.add_subplot(111, projection=\'3d\')',
              '',
              'def animate_frame(frame):',
              '    ax.clear()',
              '    ',
              '    # Get data for current frame',
              '    current_positions = ${1:simulation_data}[frame]',
              '    ',
              '    # Plot current state',
              '    ax.scatter(current_positions[:, 0], ',
              '              current_positions[:, 1], ',
              '              current_positions[:, 2],',
              '              c=\'blue\', s=50)',
              '    ',
              '    ax.set_xlim(${2:-10}, ${3:10})',
              '    ax.set_ylim(${4:-10}, ${5:10})',
              '    ax.set_zlim(${6:-10}, ${7:10})',
              '    ax.set_title(f\'Simulation Step: {frame}\')',
              '',
              'anim = FuncAnimation(fig, animate_frame, frames=${8:100}, interval=${9:50})',
              'plt.show()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create animated visualization of simulation'
          }
        ];

        return { suggestions };
      }
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      const event = new KeyboardEvent('keydown', {
        key: 'Enter',
        ctrlKey: true,
        bubbles: true
      });
      onKeyDown(event as any);
    });

    editor.onDidFocusEditorText(() => {
      onFocus();
    });

    editor.onDidBlurEditorText(() => {
      onBlur();
    });
  }, [onFocus, onBlur, onKeyDown]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    onContentChange(value || '');
  }, [onContentChange]);

  const getEditorHeight = () => {
    const lines = cell.content.split('\n').length;
    const minHeight = 120;
    const maxHeight = 500;
    const lineHeight = 20;
    const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, lines * lineHeight + 40));
    return calculatedHeight;
  };

  return (
    <div className="visualization-cell">
      <div className="visualization-cell-header bg-orange-50 px-4 py-2 border-b border-orange-200">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
          <span className="text-sm font-medium text-orange-700">
            Visualization Cell
          </span>
          <span className="text-xs text-orange-600">
            3D Graphics & Plotting
          </span>
        </div>
      </div>
      
      <div 
        className="visualization-code-editor"
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
    </div>
  );
};
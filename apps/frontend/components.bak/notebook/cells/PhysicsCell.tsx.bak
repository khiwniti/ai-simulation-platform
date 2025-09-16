'use client';

import React, { useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { Cell } from '@ai-jupyter/shared';

interface PhysicsCellProps {
  cell: Cell;
  isSelected: boolean;
  isFocused: boolean;
  onContentChange: (content: string) => void;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

export const PhysicsCell: React.FC<PhysicsCellProps> = ({
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

    // Enhanced physics-specific completions
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          // PhysX AI imports
          {
            label: 'physx_ai',
            kind: monaco.languages.CompletionItemKind.Module,
            insertText: 'import physx_ai as px',
            documentation: 'Import NVIDIA PhysX AI library'
          },
          {
            label: 'physx_ai.scene',
            kind: monaco.languages.CompletionItemKind.Module,
            insertText: 'from physx_ai import scene',
            documentation: 'Import PhysX AI scene module'
          },
          
          // Scene creation
          {
            label: 'create_physics_scene',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'scene = px.create_scene(',
              '    gravity=(0, -9.81, 0),',
              '    timestep=1.0/60.0',
              ')'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a new physics scene with gravity'
          },
          
          // Rigid bodies
          {
            label: 'add_box_rigid_body',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'box = scene.add_rigid_body(',
              '    geometry=px.BoxGeometry(${1:1.0}, ${2:1.0}, ${3:1.0}),',
              '    material=px.Material(density=${4:1000}),',
              '    position=(${5:0}, ${6:0}, ${7:0})',
              ')'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Add a box rigid body to the scene'
          },
          
          {
            label: 'add_sphere_rigid_body',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'sphere = scene.add_rigid_body(',
              '    geometry=px.SphereGeometry(${1:1.0}),',
              '    material=px.Material(density=${2:1000}),',
              '    position=(${3:0}, ${4:0}, ${5:0})',
              ')'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Add a sphere rigid body to the scene'
          },
          
          // Simulation
          {
            label: 'simulate_physics',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'for step in range(${1:100}):',
              '    scene.simulate()',
              '    # Get results',
              '    positions = scene.get_positions()',
              '    velocities = scene.get_velocities()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Run physics simulation loop'
          },
          
          // Materials
          {
            label: 'create_material',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'material = px.Material(',
              '    density=${1:1000},',
              '    friction=${2:0.5},',
              '    restitution=${3:0.3}',
              ')'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a physics material'
          },
          
          // Constraints
          {
            label: 'add_joint',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'joint = scene.add_joint(',
              '    body1=${1:body1},',
              '    body2=${2:body2},',
              '    joint_type=px.JointType.${3:FIXED}',
              ')'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Add a joint constraint between two bodies'
          },
          
          // Visualization helpers
          {
            label: 'visualize_scene',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: [
              'import matplotlib.pyplot as plt',
              'from mpl_toolkits.mplot3d import Axes3D',
              '',
              'fig = plt.figure()',
              'ax = fig.add_subplot(111, projection=\'3d\')',
              '',
              'positions = scene.get_positions()',
              'ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2])',
              'plt.show()'
            ].join('\n'),
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a 3D visualization of the physics scene'
          }
        ];

        return { suggestions };
      }
    });

    // Physics-specific keyboard shortcuts
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
    const minHeight = 120; // Slightly taller for physics cells
    const maxHeight = 500;
    const lineHeight = 20;
    const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, lines * lineHeight + 40));
    return calculatedHeight;
  };

  return (
    <div className="physics-cell">
      <div className="physics-cell-header bg-purple-50 px-4 py-2 border-b border-purple-200">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
          <span className="text-sm font-medium text-purple-700">
            Physics Simulation Cell
          </span>
          <span className="text-xs text-purple-600">
            NVIDIA PhysX AI
          </span>
        </div>
      </div>
      
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
    </div>
  );
};
'use client';

import React, { useRef, useCallback, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Cell } from '@ai-jupyter/shared';
import { useInlineAssistance } from '../../../hooks/useInlineAssistance';
import { InlineSuggestionWidget } from '../../inline-assistance/InlineSuggestionWidget';
import { HoverTooltip } from '../../inline-assistance/HoverTooltip';
import { inlineAssistanceService } from '../../../services/inlineAssistanceService';

interface CodeCellProps {
  cell: Cell;
  isSelected: boolean;
  isFocused: boolean;
  onContentChange: (content: string) => void;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  sessionId?: string;
}

export const CodeCell: React.FC<CodeCellProps> = ({
  cell,
  isSelected,
  isFocused,
  onContentChange,
  onFocus,
  onBlur,
  onKeyDown,
  sessionId = 'default-session'
}) => {
  const editorRef = useRef<any>(null);
  
  // Initialize inline assistance
  const {
    assistanceState,
    suggestionWidget,
    hoverTooltip,
    setEditor,
    handleAutoCompletion,
    handleHover,
    requestManualAssistance,
    applySuggestion,
    rejectSuggestion,
    clearSuggestions,
    hideSuggestionWidget,
    hideHoverTooltip
  } = useInlineAssistance({
    sessionId,
    notebookId: cell.notebookId,
    cellId: cell.id,
    enableAutoCompletion: true,
    enableHover: true
  });

  const handleEditorDidMount = useCallback((editor: any, monaco: any) => {
    editorRef.current = editor;
    setEditor(editor);

    // Configure Python language features
    monaco.languages.setLanguageConfiguration('python', {
      comments: {
        lineComment: '#',
        blockComment: ['"""', '"""']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"', notIn: ['string'] },
        { open: "'", close: "'", notIn: ['string', 'comment'] }
      ],
      surroundingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ],
      indentationRules: {
        increaseIndentPattern: /^\s*(def|class|if|elif|else|for|while|with|try|except|finally|async def).*:\s*$/,
        decreaseIndentPattern: /^\s*(elif|else|except|finally)\b.*$/
      }
    });

    // Add physics-specific completions
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          {
            label: 'physx_ai',
            kind: monaco.languages.CompletionItemKind.Module,
            insertText: 'import physx_ai',
            documentation: 'Import NVIDIA PhysX AI library'
          },
          {
            label: 'create_physics_scene',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'create_physics_scene()',
            documentation: 'Create a new physics scene'
          },
          {
            label: 'add_rigid_body',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'add_rigid_body(${1:geometry}, ${2:material})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Add a rigid body to the physics scene'
          },
          {
            label: 'simulate_physics',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'simulate_physics(${1:timestep})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Run physics simulation step'
          }
        ];

        return { suggestions };
      }
    });

    // Handle keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      // Trigger execution via synthetic keyboard event
      const event = new KeyboardEvent('keydown', {
        key: 'Enter',
        ctrlKey: true,
        bubbles: true
      });
      onKeyDown(event as any);
    });

    // Manual assistance shortcut (Ctrl+Space)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => {
      const position = (inlineAssistanceService.constructor as any).getCursorPosition(editor);
      const model = editor.getModel();
      if (model) {
        requestManualAssistance(
          model.getValue(),
          position.position,
          position.line,
          position.column
        );
      }
    });

    // Content change handler for auto-completion
    editor.onDidChangeModelContent(() => {
      const position = (inlineAssistanceService.constructor as any).getCursorPosition(editor);
      const model = editor.getModel();
      if (model && isFocused) {
        // Debounced auto-completion
        handleAutoCompletion(
          model.getValue(),
          position.position,
          position.line,
          position.column
        );
      }
    });

    // Cursor position change handler
    editor.onDidChangeCursorPosition(() => {
      // Clear suggestions when cursor moves significantly
      clearSuggestions();
    });

    // Hover handler
    editor.onMouseMove((e: any) => {
      if (e.target?.position) {
        const model = editor.getModel();
        const word = (inlineAssistanceService.constructor as any).getWordAtPosition(editor);
        
        if (model && word && word.length > 2) {
          const position = (inlineAssistanceService.constructor as any).getCursorPosition(editor);
          
          // Debounced hover
          setTimeout(() => {
            handleHover(
              model.getValue(),
              position.position,
              position.line,
              position.column,
              word
            );
          }, 500);
        }
      }
    });

    // Focus handling
    editor.onDidFocusEditorText(() => {
      onFocus();
    });

    editor.onDidBlurEditorText(() => {
      onBlur();
      // Clear suggestions when editor loses focus
      clearSuggestions();
    });
  }, [onFocus, onBlur, onKeyDown, setEditor, requestManualAssistance, handleAutoCompletion, handleHover, clearSuggestions, isFocused]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    onContentChange(value || '');
  }, [onContentChange]);

  // Calculate editor height based on content
  const getEditorHeight = () => {
    const lines = cell.content.split('\n').length;
    const minHeight = 100;
    const maxHeight = 400;
    const lineHeight = 20;
    const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, lines * lineHeight + 40));
    return calculatedHeight;
  };

  return (
    <div 
      className="code-cell relative"
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
          folding: false,
          lineDecorationsWidth: 0,
          lineNumbersMinChars: 3,
          renderLineHighlight: isFocused ? 'line' : 'none',
          selectOnLineNumbers: true,
          automaticLayout: true,
          wordWrap: 'on',
          contextmenu: true,
          quickSuggestions: {
            other: false, // Disable Monaco's built-in suggestions
            comments: false,
            strings: false
          },
          suggestOnTriggerCharacters: false, // Disable built-in trigger characters
          acceptSuggestionOnEnter: 'off', // We handle this ourselves
          tabCompletion: 'off', // We handle this ourselves
          parameterHints: {
            enabled: true
          },
          hover: {
            enabled: false // We handle hover ourselves
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

      {/* Inline Suggestion Widget */}
      <InlineSuggestionWidget
        suggestions={suggestionWidget.suggestions}
        position={suggestionWidget.position}
        visible={suggestionWidget.visible}
        onAccept={applySuggestion}
        onReject={rejectSuggestion}
        onClose={hideSuggestionWidget}
      />

      {/* Hover Tooltip */}
      <HoverTooltip
        suggestion={hoverTooltip.suggestion}
        position={hoverTooltip.position}
        visible={hoverTooltip.visible}
        onClose={hideHoverTooltip}
      />

      {/* Loading indicator */}
      {assistanceState.isLoading && (
        <div className="absolute top-2 right-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
          AI analyzing...
        </div>
      )}

      {/* Error indicator */}
      {assistanceState.error && (
        <div className="absolute top-2 right-2 bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
          AI error: {assistanceState.error}
        </div>
      )}
    </div>
  );
};
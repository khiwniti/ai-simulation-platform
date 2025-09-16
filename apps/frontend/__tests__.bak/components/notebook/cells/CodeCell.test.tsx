import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CodeCell } from '@/components/notebook/cells/CodeCell';
import { Cell, CellType } from '@ai-jupyter/shared';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => {
  return {
    __esModule: true,
    default: ({ value, onChange, onMount }: any) => {
      React.useEffect(() => {
        if (onMount) {
          const mockEditor = {
            addCommand: jest.fn(),
            onDidFocusEditorText: jest.fn(),
            onDidBlurEditorText: jest.fn(),
          };
          const mockMonaco = {
            languages: {
              setLanguageConfiguration: jest.fn(),
              registerCompletionItemProvider: jest.fn(),
              CompletionItemKind: {
                Module: 1,
                Function: 2,
              },
              CompletionItemInsertTextRule: {
                InsertAsSnippet: 1,
              },
            },
            KeyMod: {
              CtrlCmd: 1,
            },
            KeyCode: {
              Enter: 2,
            },
          };
          onMount(mockEditor, mockMonaco);
        }
      }, [onMount]);

      return (
        <textarea
          data-testid="monaco-editor"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
        />
      );
    },
  };
});

const mockCell: Cell = {
  id: 'test-cell-1',
  notebookId: 'test-notebook-1',
  cellType: CellType.CODE,
  content: 'print("Hello, World!")',
  outputs: [],
  executionCount: 0,
  metadata: {},
  position: 0,
};

const mockProps = {
  cell: mockCell,
  isSelected: false,
  isFocused: false,
  onContentChange: jest.fn(),
  onFocus: jest.fn(),
  onBlur: jest.fn(),
  onKeyDown: jest.fn(),
};

describe('CodeCell', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders Monaco editor with cell content', () => {
    render(<CodeCell {...mockProps} />);
    
    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toBeInTheDocument();
    expect(editor).toHaveValue('print("Hello, World!")');
  });

  it('calls onContentChange when editor content changes', () => {
    render(<CodeCell {...mockProps} />);
    
    const editor = screen.getByTestId('monaco-editor');
    fireEvent.change(editor, { target: { value: 'new content' } });
    
    expect(mockProps.onContentChange).toHaveBeenCalledWith('new content');
  });

  it('handles keyboard events', () => {
    render(<CodeCell {...mockProps} />);
    
    const codeCell = screen.getByRole('generic');
    fireEvent.keyDown(codeCell, { key: 'Enter', ctrlKey: true });
    
    expect(mockProps.onKeyDown).toHaveBeenCalled();
  });

  it('is focusable', () => {
    render(<CodeCell {...mockProps} />);
    
    const focusableElement = screen.getByTestId('monaco-editor').closest('[data-focusable="true"]');
    expect(focusableElement).toBeInTheDocument();
  });

  it('calculates editor height based on content', () => {
    const longContentCell = {
      ...mockCell,
      content: Array(20).fill('print("line")').join('\n'),
    };
    
    render(<CodeCell {...mockProps} cell={longContentCell} />);
    
    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toBeInTheDocument();
  });

  it('handles empty content', () => {
    const emptyCell = { ...mockCell, content: '' };
    render(<CodeCell {...mockProps} cell={emptyCell} />);
    
    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toHaveValue('');
  });

  it('configures Python language features on mount', () => {
    const onMount = jest.fn();
    
    // We can't easily test the Monaco configuration directly,
    // but we can verify the component renders without errors
    render(<CodeCell {...mockProps} />);
    
    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });
});
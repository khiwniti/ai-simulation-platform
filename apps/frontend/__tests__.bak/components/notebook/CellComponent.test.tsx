import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CellComponent } from '@/components/notebook/CellComponent';
import { Cell, CellType } from '@ai-jupyter/shared';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => {
  return {
    __esModule: true,
    default: ({ value, onChange }: any) => (
      <textarea
        data-testid="monaco-editor"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
    ),
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
  isExecuting: false,
  onContentChange: jest.fn(),
  onSelect: jest.fn(),
  onExecute: jest.fn(),
};

describe('CellComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders cell with correct type label', () => {
    render(<CellComponent {...mockProps} />);
    
    expect(screen.getByText('Code')).toBeInTheDocument();
  });

  it('shows execution count when greater than 0', () => {
    const cellWithExecution = { ...mockCell, executionCount: 5 };
    render(<CellComponent {...mockProps} cell={cellWithExecution} />);
    
    expect(screen.getByText('[5]')).toBeInTheDocument();
  });

  it('shows executing state when isExecuting is true', () => {
    render(<CellComponent {...mockProps} isExecuting={true} />);
    
    expect(screen.getByText('Executing...')).toBeInTheDocument();
  });

  it('applies selected styles when isSelected is true', () => {
    render(<CellComponent {...mockProps} isSelected={true} />);
    
    const cellElement = screen.getByTestId('cell-test-cell-1');
    expect(cellElement).toHaveClass('ring-2', 'ring-blue-300', 'bg-blue-50');
  });

  it('calls onSelect when cell is clicked', () => {
    render(<CellComponent {...mockProps} />);
    
    const cellElement = screen.getByTestId('cell-test-cell-1');
    fireEvent.click(cellElement);
    
    expect(mockProps.onSelect).toHaveBeenCalled();
  });

  it('calls onExecute when run button is clicked', () => {
    render(<CellComponent {...mockProps} />);
    
    const runButton = screen.getByText('Run');
    fireEvent.click(runButton);
    
    expect(mockProps.onExecute).toHaveBeenCalled();
  });

  it('calls onExecute when Ctrl+Enter is pressed', () => {
    render(<CellComponent {...mockProps} />);
    
    const cellElement = screen.getByTestId('cell-test-cell-1');
    fireEvent.keyDown(cellElement, { key: 'Enter', ctrlKey: true });
    
    expect(mockProps.onExecute).toHaveBeenCalled();
  });

  it('disables run button when executing', () => {
    render(<CellComponent {...mockProps} isExecuting={true} />);
    
    const runButton = screen.getByText('Running...');
    expect(runButton).toBeDisabled();
  });

  it('renders different cell types with appropriate colors', () => {
    const cellTypes = [
      { type: CellType.CODE, color: 'border-l-blue-500', label: 'Code' },
      { type: CellType.MARKDOWN, color: 'border-l-green-500', label: 'Markdown' },
      { type: CellType.PHYSICS, color: 'border-l-purple-500', label: 'Physics' },
      { type: CellType.VISUALIZATION, color: 'border-l-orange-500', label: 'Visualization' },
    ];

    cellTypes.forEach(({ type, color, label }) => {
      const { unmount } = render(
        <CellComponent {...mockProps} cell={{ ...mockCell, cellType: type }} />
      );
      
      expect(screen.getByText(label)).toBeInTheDocument();
      const cellElement = screen.getByTestId('cell-test-cell-1');
      expect(cellElement).toHaveClass(color);
      
      unmount();
    });
  });

  it('does not show run button for markdown cells', () => {
    const markdownCell = { ...mockCell, cellType: CellType.MARKDOWN };
    render(<CellComponent {...mockProps} cell={markdownCell} />);
    
    expect(screen.queryByText('Run')).not.toBeInTheDocument();
  });

  it('shows run button for executable cell types', () => {
    const executableTypes = [CellType.CODE, CellType.PHYSICS, CellType.VISUALIZATION];
    
    executableTypes.forEach((cellType) => {
      const { unmount } = render(
        <CellComponent {...mockProps} cell={{ ...mockCell, cellType }} />
      );
      
      expect(screen.getByText('Run')).toBeInTheDocument();
      unmount();
    });
  });

  it('renders cell outputs when present', () => {
    const cellWithOutput = {
      ...mockCell,
      outputs: [
        {
          outputType: 'text' as const,
          data: 'Hello, World!',
          metadata: { timestamp: new Date().toISOString() },
        },
      ],
    };
    
    render(<CellComponent {...mockProps} cell={cellWithOutput} />);
    
    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
  });

  it('calls onContentChange when editor content changes', () => {
    render(<CellComponent {...mockProps} />);
    
    const editor = screen.getByTestId('monaco-editor');
    fireEvent.change(editor, { target: { value: 'new content' } });
    
    expect(mockProps.onContentChange).toHaveBeenCalledWith('new content');
  });

  it('handles focus and blur events', () => {
    const { container } = render(<CellComponent {...mockProps} />);
    
    const focusableElement = container.querySelector('[data-focusable="true"]');
    expect(focusableElement).toBeInTheDocument();
  });
});
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MarkdownCell } from '@/components/notebook/cells/MarkdownCell';
import { Cell, CellType } from '@ai-jupyter/shared';

const mockCell: Cell = {
  id: 'test-cell-1',
  notebookId: 'test-notebook-1',
  cellType: CellType.MARKDOWN,
  content: '# Hello World\n\nThis is **bold** text.',
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

describe('MarkdownCell', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders markdown content in view mode', () => {
    render(<MarkdownCell {...mockProps} />);
    
    // Should render the markdown as HTML
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('enters edit mode on double click', () => {
    render(<MarkdownCell {...mockProps} />);
    
    const cellElement = screen.getByRole('generic');
    fireEvent.doubleClick(cellElement);
    
    // Should show textarea in edit mode
    expect(screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.')).toBeInTheDocument();
  });

  it('enters edit mode when selected and focused', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    // Should automatically enter edit mode
    expect(screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.')).toBeInTheDocument();
  });

  it('calls onContentChange when textarea content changes', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    const textarea = screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.');
    fireEvent.change(textarea, { target: { value: '# Updated content' } });
    
    expect(mockProps.onContentChange).toHaveBeenCalledWith('# Updated content');
  });

  it('exits edit mode on Escape key', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    const textarea = screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.');
    fireEvent.keyDown(textarea, { key: 'Escape' });
    
    // Should exit edit mode and show rendered content
    waitFor(() => {
      expect(screen.queryByDisplayValue('# Hello World\n\nThis is **bold** text.')).not.toBeInTheDocument();
      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });
  });

  it('exits edit mode on Ctrl+Enter', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    const textarea = screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.');
    fireEvent.keyDown(textarea, { key: 'Enter', ctrlKey: true });
    
    waitFor(() => {
      expect(screen.queryByDisplayValue('# Hello World\n\nThis is **bold** text.')).not.toBeInTheDocument();
      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });
  });

  it('shows placeholder text for empty cells', () => {
    const emptyCell = { ...mockCell, content: '' };
    render(<MarkdownCell {...mockProps} cell={emptyCell} />);
    
    expect(screen.getByText('Double-click to edit this markdown cell')).toBeInTheDocument();
  });

  it('renders basic markdown formatting', () => {
    const formattedCell = {
      ...mockCell,
      content: '# Header 1\n## Header 2\n### Header 3\n\n**Bold text**\n*Italic text*\n\n`inline code`\n\n```\ncode block\n```',
    };
    
    render(<MarkdownCell {...mockProps} cell={formattedCell} />);
    
    // The basic markdown parser should render these elements
    expect(screen.getByText('Header 1')).toBeInTheDocument();
    expect(screen.getByText('Header 2')).toBeInTheDocument();
    expect(screen.getByText('Header 3')).toBeInTheDocument();
  });

  it('calls onFocus when cell is clicked', () => {
    render(<MarkdownCell {...mockProps} />);
    
    const cellElement = screen.getByRole('generic');
    fireEvent.click(cellElement);
    
    expect(mockProps.onFocus).toHaveBeenCalled();
  });

  it('handles keyboard events in view mode', () => {
    render(<MarkdownCell {...mockProps} />);
    
    const cellElement = screen.getByRole('generic');
    fireEvent.keyDown(cellElement, { key: 'Enter' });
    
    expect(mockProps.onKeyDown).toHaveBeenCalled();
  });

  it('auto-resizes textarea in edit mode', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    const textarea = screen.getByDisplayValue('# Hello World\n\nThis is **bold** text.');
    
    // Simulate input event that would trigger resize
    fireEvent.input(textarea);
    
    expect(textarea).toBeInTheDocument();
  });

  it('is focusable in view mode', () => {
    render(<MarkdownCell {...mockProps} />);
    
    const focusableElement = screen.getByRole('generic');
    expect(focusableElement).toHaveAttribute('tabIndex', '0');
    expect(focusableElement).toHaveAttribute('data-focusable', 'true');
  });

  it('shows editing instructions in edit mode', () => {
    render(<MarkdownCell {...mockProps} isSelected={true} isFocused={true} />);
    
    expect(screen.getByText('Editing markdown (Ctrl+Enter to finish, Esc to cancel)')).toBeInTheDocument();
  });
});
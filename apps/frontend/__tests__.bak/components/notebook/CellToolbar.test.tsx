import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CellToolbar } from '@/components/notebook/CellToolbar';
import { Cell, CellType } from '@ai-jupyter/shared';

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
  isSelected: true,
  isExecuting: false,
  canMoveUp: true,
  canMoveDown: true,
  onExecute: jest.fn(),
  onDelete: jest.fn(),
  onMoveUp: jest.fn(),
  onMoveDown: jest.fn(),
  onAddAbove: jest.fn(),
  onAddBelow: jest.fn(),
};

describe('CellToolbar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('does not render when cell is not selected', () => {
    const { container } = render(<CellToolbar {...mockProps} isSelected={false} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders all toolbar buttons when selected', () => {
    render(<CellToolbar {...mockProps} />);
    
    // Add cell buttons
    expect(screen.getAllByTitle('Add cell above')).toHaveLength(1);
    expect(screen.getAllByTitle('Add cell below')).toHaveLength(1);
    
    // Move buttons
    expect(screen.getByTitle('Move cell up')).toBeInTheDocument();
    expect(screen.getByTitle('Move cell down')).toBeInTheDocument();
    
    // Execute button (for executable cells)
    expect(screen.getByText('Run')).toBeInTheDocument();
    
    // Delete button
    expect(screen.getByTitle('Delete cell')).toBeInTheDocument();
  });

  it('calls onAddAbove when add above button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const addAboveButton = screen.getByTitle('Add cell above');
    fireEvent.click(addAboveButton);
    
    expect(mockProps.onAddAbove).toHaveBeenCalled();
  });

  it('calls onAddBelow when add below button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const addBelowButton = screen.getByTitle('Add cell below');
    fireEvent.click(addBelowButton);
    
    expect(mockProps.onAddBelow).toHaveBeenCalled();
  });

  it('calls onMoveUp when move up button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const moveUpButton = screen.getByTitle('Move cell up');
    fireEvent.click(moveUpButton);
    
    expect(mockProps.onMoveUp).toHaveBeenCalled();
  });

  it('calls onMoveDown when move down button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const moveDownButton = screen.getByTitle('Move cell down');
    fireEvent.click(moveDownButton);
    
    expect(mockProps.onMoveDown).toHaveBeenCalled();
  });

  it('disables move up button when canMoveUp is false', () => {
    render(<CellToolbar {...mockProps} canMoveUp={false} />);
    
    const moveUpButton = screen.getByTitle('Move cell up');
    expect(moveUpButton).toBeDisabled();
  });

  it('disables move down button when canMoveDown is false', () => {
    render(<CellToolbar {...mockProps} canMoveDown={false} />);
    
    const moveDownButton = screen.getByTitle('Move cell down');
    expect(moveDownButton).toBeDisabled();
  });

  it('calls onExecute when run button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const runButton = screen.getByText('Run');
    fireEvent.click(runButton);
    
    expect(mockProps.onExecute).toHaveBeenCalled();
  });

  it('shows executing state when isExecuting is true', () => {
    render(<CellToolbar {...mockProps} isExecuting={true} />);
    
    expect(screen.getByText('Running')).toBeInTheDocument();
    const runButton = screen.getByText('Running');
    expect(runButton).toBeDisabled();
  });

  it('calls onDelete when delete button is clicked', () => {
    render(<CellToolbar {...mockProps} />);
    
    const deleteButton = screen.getByTitle('Delete cell');
    fireEvent.click(deleteButton);
    
    expect(mockProps.onDelete).toHaveBeenCalled();
  });

  it('does not show run button for markdown cells', () => {
    const markdownCell = { ...mockCell, cellType: CellType.MARKDOWN };
    render(<CellToolbar {...mockProps} cell={markdownCell} />);
    
    expect(screen.queryByText('Run')).not.toBeInTheDocument();
  });

  it('shows run button for executable cell types', () => {
    const executableTypes = [CellType.CODE, CellType.PHYSICS, CellType.VISUALIZATION];
    
    executableTypes.forEach((cellType) => {
      const { unmount } = render(
        <CellToolbar {...mockProps} cell={{ ...mockCell, cellType }} />
      );
      
      expect(screen.getByText('Run')).toBeInTheDocument();
      unmount();
    });
  });

  it('has proper accessibility attributes', () => {
    render(<CellToolbar {...mockProps} />);
    
    // Check that buttons have proper titles for screen readers
    expect(screen.getByTitle('Add cell above')).toBeInTheDocument();
    expect(screen.getByTitle('Add cell below')).toBeInTheDocument();
    expect(screen.getByTitle('Move cell up')).toBeInTheDocument();
    expect(screen.getByTitle('Move cell down')).toBeInTheDocument();
    expect(screen.getByTitle('Delete cell')).toBeInTheDocument();
    expect(screen.getByTitle('Execute cell (Ctrl+Enter)')).toBeInTheDocument();
  });
});
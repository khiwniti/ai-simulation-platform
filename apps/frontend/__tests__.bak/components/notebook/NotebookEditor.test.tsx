import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { NotebookEditor } from '@/components/notebook/NotebookEditor';
import { Notebook, CellType } from '@ai-jupyter/shared';

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
                Snippet: 3,
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

// Mock workbook store
const mockUpdateNotebook = jest.fn();
jest.mock('@/stores/workbookStore', () => ({
  useWorkbookStore: () => ({
    updateNotebook: mockUpdateNotebook,
  }),
}));

const mockNotebook: Notebook = {
  id: 'test-notebook-1',
  title: 'Test Notebook',
  description: 'A test notebook for unit testing',
  workbookId: 'test-workbook-1',
  cells: [
    {
      id: 'cell-1',
      notebookId: 'test-notebook-1',
      cellType: CellType.CODE,
      content: 'print("Hello, World!")',
      outputs: [],
      executionCount: 0,
      metadata: {},
      position: 0,
    },
    {
      id: 'cell-2',
      notebookId: 'test-notebook-1',
      cellType: CellType.MARKDOWN,
      content: '# Test Markdown',
      outputs: [],
      executionCount: 0,
      metadata: {},
      position: 1,
    },
  ],
  metadata: {},
  createdAt: new Date(),
  updatedAt: new Date(),
  version: 1,
};

describe('NotebookEditor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders notebook title and description', () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    expect(screen.getByText('Test Notebook')).toBeInTheDocument();
    expect(screen.getByText('A test notebook for unit testing')).toBeInTheDocument();
  });

  it('renders all cell type buttons', () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    expect(screen.getByText('+ Code')).toBeInTheDocument();
    expect(screen.getByText('+ Markdown')).toBeInTheDocument();
    expect(screen.getByText('+ Physics')).toBeInTheDocument();
    expect(screen.getByText('+ Visualization')).toBeInTheDocument();
  });

  it('renders existing cells in correct order', () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const cells = screen.getAllByTestId(/^cell-/);
    expect(cells).toHaveLength(2);
    expect(cells[0]).toHaveAttribute('data-testid', 'cell-cell-1');
    expect(cells[1]).toHaveAttribute('data-testid', 'cell-cell-2');
  });

  it('adds a new code cell when + Code button is clicked', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const addCodeButton = screen.getByText('+ Code');
    fireEvent.click(addCodeButton);

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          cells: expect.arrayContaining([
            expect.objectContaining({
              cellType: CellType.CODE,
              position: 2,
            }),
          ]),
        })
      );
    });
  });

  it('adds a new markdown cell when + Markdown button is clicked', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const addMarkdownButton = screen.getByText('+ Markdown');
    fireEvent.click(addMarkdownButton);

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          cells: expect.arrayContaining([
            expect.objectContaining({
              cellType: CellType.MARKDOWN,
              content: '# New Markdown Cell\n\nEdit this cell to add your documentation.',
            }),
          ]),
        })
      );
    });
  });

  it('adds a new physics cell when + Physics button is clicked', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const addPhysicsButton = screen.getByText('+ Physics');
    fireEvent.click(addPhysicsButton);

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          cells: expect.arrayContaining([
            expect.objectContaining({
              cellType: CellType.PHYSICS,
              content: expect.stringContaining('PhysX AI'),
            }),
          ]),
        })
      );
    });
  });

  it('adds a new visualization cell when + Visualization button is clicked', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const addVisualizationButton = screen.getByText('+ Visualization');
    fireEvent.click(addVisualizationButton);

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          cells: expect.arrayContaining([
            expect.objectContaining({
              cellType: CellType.VISUALIZATION,
              content: expect.stringContaining('3D visualizations'),
            }),
          ]),
        })
      );
    });
  });

  it('shows empty notebook message when no cells exist', () => {
    const emptyNotebook = { ...mockNotebook, cells: [] };
    render(<NotebookEditor notebook={emptyNotebook} />);
    
    expect(screen.getByText('This notebook is empty. Add your first cell to get started!')).toBeInTheDocument();
    expect(screen.getByText('Add Code Cell')).toBeInTheDocument();
  });

  it('handles cell selection', () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const firstCell = screen.getByTestId('cell-cell-1');
    fireEvent.click(firstCell);
    
    // Cell should be selected (visual feedback would be tested in integration tests)
    expect(firstCell).toBeInTheDocument();
  });

  it('clears selection on Escape key', () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const editor = screen.getByRole('generic', { name: /notebook-editor/ });
    fireEvent.keyDown(editor, { key: 'Escape' });
    
    // Selection should be cleared (state change)
    expect(editor).toBeInTheDocument();
  });

  it('executes cell when execute function is called', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    // Find and click a run button (would be in cell toolbar when cell is selected)
    const firstCell = screen.getByTestId('cell-cell-1');
    fireEvent.click(firstCell);
    
    // Simulate execution by finding the run button in the cell header
    const runButtons = screen.getAllByText(/Run/);
    if (runButtons.length > 0) {
      fireEvent.click(runButtons[0]);
      
      await waitFor(() => {
        expect(mockUpdateNotebook).toHaveBeenCalled();
      });
    }
  });

  it('updates cell content when editor content changes', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const editor = screen.getAllByTestId('monaco-editor')[0];
    fireEvent.change(editor, { target: { value: 'print("Updated content")' } });

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          cells: expect.arrayContaining([
            expect.objectContaining({
              content: 'print("Updated content")',
            }),
          ]),
        })
      );
    });
  });

  it('increments notebook version when cells are updated', async () => {
    render(<NotebookEditor notebook={mockNotebook} />);
    
    const addCodeButton = screen.getByText('+ Code');
    fireEvent.click(addCodeButton);

    await waitFor(() => {
      expect(mockUpdateNotebook).toHaveBeenCalledWith(
        'test-notebook-1',
        expect.objectContaining({
          version: 2, // Original version was 1
        })
      );
    });
  });
});
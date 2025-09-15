'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Notebook, Cell, CellType, CodeSnippet } from '@ai-jupyter/shared';
import { CellComponent } from './CellComponent';
import { CellToolbar } from './CellToolbar';
import { useWorkbookStore } from '@/stores/workbookStore';
import { PhysicsVisualizationCell } from './cells/PhysicsVisualizationCell';

interface NotebookEditorProps {
  notebook: Notebook;
  className?: string;
  sessionId?: string;
}

export const NotebookEditor: React.FC<NotebookEditorProps> = ({ 
  notebook, 
  className = '',
  sessionId = `session_${notebook.id}`
}) => {
  const { updateNotebook } = useWorkbookStore();
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState<Set<string>>(new Set());

  // Sort cells by position
  const sortedCells = [...notebook.cells].sort((a, b) => a.position - b.position);

  const updateCell = useCallback(async (cellId: string, updates: Partial<Cell>) => {
    const updatedCells = notebook.cells.map(cell =>
      cell.id === cellId ? { ...cell, ...updates } : cell
    );

    updateNotebook(notebook.id, {
      cells: updatedCells,
      updatedAt: new Date(),
      version: notebook.version + 1
    });
  }, [notebook, updateNotebook]);

  const addCell = useCallback(async (
    cellType: CellType = CellType.CODE, 
    position?: number
  ) => {
    const newPosition = position !== undefined ? position : notebook.cells.length;
    const newCell: Cell = {
      id: `cell_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      notebookId: notebook.id,
      cellType,
      content: getDefaultContent(cellType),
      outputs: [],
      executionCount: 0,
      metadata: {},
      position: newPosition
    };

    // Update positions of cells that come after the new cell
    const updatedCells = notebook.cells.map(cell => 
      cell.position >= newPosition 
        ? { ...cell, position: cell.position + 1 }
        : cell
    );

    updatedCells.push(newCell);

    updateNotebook(notebook.id, {
      cells: updatedCells,
      updatedAt: new Date(),
      version: notebook.version + 1
    });

    setSelectedCellId(newCell.id);
  }, [notebook, updateNotebook]);

  const deleteCell = useCallback(async (cellId: string) => {
    const cellToDelete = notebook.cells.find(cell => cell.id === cellId);
    if (!cellToDelete) return;

    // Remove the cell and update positions
    const updatedCells = notebook.cells
      .filter(cell => cell.id !== cellId)
      .map(cell => 
        cell.position > cellToDelete.position 
          ? { ...cell, position: cell.position - 1 }
          : cell
      );

    updateNotebook(notebook.id, {
      cells: updatedCells,
      updatedAt: new Date(),
      version: notebook.version + 1
    });

    // Clear selection if deleted cell was selected
    if (selectedCellId === cellId) {
      setSelectedCellId(null);
    }
  }, [notebook, updateNotebook, selectedCellId]);

  const moveCell = useCallback(async (cellId: string, direction: 'up' | 'down') => {
    const cellIndex = sortedCells.findIndex(cell => cell.id === cellId);
    if (cellIndex === -1) return;

    const targetIndex = direction === 'up' ? cellIndex - 1 : cellIndex + 1;
    if (targetIndex < 0 || targetIndex >= sortedCells.length) return;

    const updatedCells = [...sortedCells];
    [updatedCells[cellIndex], updatedCells[targetIndex]] = 
    [updatedCells[targetIndex], updatedCells[cellIndex]];

    // Update positions
    updatedCells.forEach((cell, index) => {
      cell.position = index;
    });

    updateNotebook(notebook.id, {
      cells: updatedCells,
      updatedAt: new Date(),
      version: notebook.version + 1
    });
  }, [sortedCells, notebook, updateNotebook]);

  const executeCell = useCallback(async (cellId: string) => {
    const cell = notebook.cells.find(c => c.id === cellId);
    if (!cell || cell.cellType !== CellType.CODE) return;

    setIsExecuting(prev => new Set(prev).add(cellId));

    try {
      // Simulate code execution - in real implementation this would call the backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock execution result
      const mockOutput = {
        outputType: 'text' as const,
        data: `Executed: ${cell.content.slice(0, 50)}${cell.content.length > 50 ? '...' : ''}`,
        metadata: { timestamp: new Date().toISOString() }
      };

      await updateCell(cellId, {
        outputs: [mockOutput],
        executionCount: cell.executionCount + 1
      });
    } catch (error) {
      const errorOutput = {
        outputType: 'text' as const,
        data: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        metadata: { error: true }
      };

      await updateCell(cellId, {
        outputs: [errorOutput]
      });
    } finally {
      setIsExecuting(prev => {
        const newSet = new Set(prev);
        newSet.delete(cellId);
        return newSet;
      });
    }
  }, [notebook.cells, updateCell]);

  const handleCellSelect = useCallback((cellId: string) => {
    setSelectedCellId(cellId);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setSelectedCellId(null);
    }
  }, []);

  // Listen for code insertion events from chat
  useEffect(() => {
    const handleCodeInsertion = (event: CustomEvent<CodeSnippet>) => {
      const snippet = event.detail;
      
      if (selectedCellId) {
        // Insert into selected cell
        const selectedCell = notebook.cells.find(cell => cell.id === selectedCellId);
        if (selectedCell) {
          const newContent = selectedCell.content + '\n\n' + snippet.code;
          updateCell(selectedCellId, { content: newContent });
        }
      } else {
        // Create new cell with the code
        const newCell: Cell = {
          id: `cell_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
          notebookId: notebook.id,
          cellType: snippet.language === 'markdown' ? CellType.MARKDOWN : CellType.CODE,
          content: snippet.code,
          outputs: [],
          executionCount: 0,
          metadata: {
            insertedFromChat: true,
            originalDescription: snippet.description
          },
          position: notebook.cells.length
        };

        const updatedCells = [...notebook.cells, newCell];
        updateNotebook(notebook.id, {
          cells: updatedCells,
          updatedAt: new Date(),
          version: notebook.version + 1
        });

        setSelectedCellId(newCell.id);
      }
    };

    window.addEventListener('insertCodeSnippet', handleCodeInsertion as EventListener);
    
    return () => {
      window.removeEventListener('insertCodeSnippet', handleCodeInsertion as EventListener);
    };
  }, [selectedCellId, notebook, updateCell, updateNotebook]);

  return (
    <div 
      className={`notebook-editor ${className}`}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div className="notebook-header mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {notebook.title}
        </h1>
        {notebook.description && (
          <p className="text-gray-600 mb-4">{notebook.description}</p>
        )}
        
        <div className="flex gap-2">
          <button
            onClick={() => addCell(CellType.CODE)}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
          >
            + Code
          </button>
          <button
            onClick={() => addCell(CellType.MARKDOWN)}
            className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
          >
            + Markdown
          </button>
          <button
            onClick={() => addCell(CellType.PHYSICS)}
            className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm"
          >
            + Physics
          </button>
          <button
            onClick={() => addCell(CellType.VISUALIZATION)}
            className="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm"
          >
            + Visualization
          </button>
        </div>
      </div>

      <div className="cells-container space-y-4">
        {sortedCells.length === 0 ? (
          <div className="empty-notebook text-center py-12 text-gray-500">
            <p className="mb-4">This notebook is empty. Add your first cell to get started!</p>
            <button
              onClick={() => addCell(CellType.CODE)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Add Code Cell
            </button>
          </div>
        ) : (
          sortedCells.map((cell, index) => (
            <div key={cell.id} className="cell-container">
              <CellToolbar
                cell={cell}
                isSelected={selectedCellId === cell.id}
                isExecuting={isExecuting.has(cell.id)}
                canMoveUp={index > 0}
                canMoveDown={index < sortedCells.length - 1}
                onExecute={() => executeCell(cell.id)}
                onDelete={() => deleteCell(cell.id)}
                onMoveUp={() => moveCell(cell.id, 'up')}
                onMoveDown={() => moveCell(cell.id, 'down')}
                onAddAbove={() => addCell(CellType.CODE, cell.position)}
                onAddBelow={() => addCell(CellType.CODE, cell.position + 1)}
              />
              <CellComponent
                cell={cell}
                isSelected={selectedCellId === cell.id}
                isExecuting={isExecuting.has(cell.id)}
                onContentChange={(content) => updateCell(cell.id, { content })}
                onSelect={() => handleCellSelect(cell.id)}
                onExecute={() => executeCell(cell.id)}
                sessionId={sessionId}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
};

function getDefaultContent(cellType: CellType): string {
  switch (cellType) {
    case CellType.CODE:
      return '';
    case CellType.MARKDOWN:
      return '# New Markdown Cell\n\nEdit this cell to add your documentation.';
    case CellType.PHYSICS:
      return `# Physics Simulation Cell
import physics_sim as ps

# Create physics world
world = ps.World(gravity=[0, -9.81, 0])
world.set_timestep(1/60)

# Add ground plane
ground = ps.create_plane(position=[0, -1, 0], size=[20, 1, 20])
world.add_body(ground)

# Create a falling sphere
sphere = ps.create_sphere(
    position=[0, 5, 0],
    radius=0.5,
    mass=1.0,
    material=ps.Material(friction=0.4, restitution=0.6)
)
world.add_body(sphere)

# Run physics simulation
simulation = ps.Simulation(world)
simulation.set_duration(3.0)  # 3 seconds
simulation.set_frame_rate(60)  # 60 FPS

# Execute and return visualization data
results = simulation.run()

viz_data = {
    "type": "physics_simulation",
    "bodies": results.get_body_definitions(),
    "constraints": results.get_constraint_definitions(),
    "worldConfig": {
        "gravity": world.gravity,
        "timestep": world.timestep
    },
    "metadata": {
        "duration": results.duration,
        "steps": results.total_steps,
        "fps": simulation.frame_rate
    }
}

viz_data`;
    case CellType.VISUALIZATION:
      return '# Visualization Cell\n# Use this cell for 3D visualizations and plots\n\nimport matplotlib.pyplot as plt\nimport numpy as np\n\n# Your visualization code here';
    default:
      return '';
  }
}
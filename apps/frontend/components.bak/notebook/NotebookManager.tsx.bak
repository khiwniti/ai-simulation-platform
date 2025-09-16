'use client';

import React from 'react';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Notebook, Cell, CellType } from '@ai-jupyter/shared';
import { NotebookEditor } from './NotebookEditor';

interface NotebookManagerProps {
  className?: string;
}

export const NotebookManager: React.FC<NotebookManagerProps> = ({ className = '' }) => {
  const {
    selectedNotebook,
    updateNotebook,
    addNotebook,
    deleteNotebook,
    setLoading,
    setError
  } = useWorkbookStore();

  const createNotebook = async (workbookId: string, title: string, description: string = '') => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const newNotebook: Notebook = {
        id: `nb_${Date.now()}`,
        title,
        description,
        workbookId,
        cells: [
          // Create a default code cell
          {
            id: `cell_${Date.now()}`,
            notebookId: `nb_${Date.now()}`,
            cellType: CellType.CODE,
            content: '# Welcome to your new notebook\n# Start writing your physics simulation code here\n\nprint("Hello, PhysX AI!")',
            outputs: [],
            executionCount: 0,
            metadata: {},
            position: 0
          }
        ],
        metadata: {
          kernelspec: {
            display_name: 'Python 3 (PhysX AI)',
            language: 'python',
            name: 'python3-physx'
          },
          language_info: {
            name: 'python',
            version: '3.11.0'
          }
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        version: 1
      };
      
      addNotebook(workbookId, newNotebook);
      return newNotebook;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create notebook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateNotebookData = async (id: string, updates: Partial<Notebook>) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 200));
      
      updateNotebook(id, { 
        ...updates, 
        updatedAt: new Date(),
        version: selectedNotebook ? selectedNotebook.version + 1 : 1
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update notebook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteNotebookData = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      deleteNotebook(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete notebook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const addCell = async (notebookId: string, cellType: CellType = CellType.CODE, position?: number) => {
    if (!selectedNotebook || selectedNotebook.id !== notebookId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const newPosition = position !== undefined ? position : selectedNotebook.cells.length;
      const newCell: Cell = {
        id: `cell_${Date.now()}`,
        notebookId,
        cellType,
        content: cellType === CellType.CODE ? '' : cellType === CellType.MARKDOWN ? '# New markdown cell' : '',
        outputs: [],
        executionCount: 0,
        metadata: {},
        position: newPosition
      };

      // Update positions of cells that come after the new cell
      const updatedCells = selectedNotebook.cells.map(cell => 
        cell.position >= newPosition 
          ? { ...cell, position: cell.position + 1 }
          : cell
      );

      updatedCells.splice(newPosition, 0, newCell);

      updateNotebook(notebookId, { 
        cells: updatedCells,
        updatedAt: new Date(),
        version: selectedNotebook.version + 1
      });

      return newCell;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add cell');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateCell = async (notebookId: string, cellId: string, updates: Partial<Cell>) => {
    if (!selectedNotebook || selectedNotebook.id !== notebookId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const updatedCells = selectedNotebook.cells.map(cell =>
        cell.id === cellId ? { ...cell, ...updates } : cell
      );

      updateNotebook(notebookId, { 
        cells: updatedCells,
        updatedAt: new Date(),
        version: selectedNotebook.version + 1
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update cell');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteCell = async (notebookId: string, cellId: string) => {
    if (!selectedNotebook || selectedNotebook.id !== notebookId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const cellToDelete = selectedNotebook.cells.find(cell => cell.id === cellId);
      if (!cellToDelete) return;

      // Remove the cell and update positions
      const updatedCells = selectedNotebook.cells
        .filter(cell => cell.id !== cellId)
        .map(cell => 
          cell.position > cellToDelete.position 
            ? { ...cell, position: cell.position - 1 }
            : cell
        );

      updateNotebook(notebookId, { 
        cells: updatedCells,
        updatedAt: new Date(),
        version: selectedNotebook.version + 1
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete cell');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Render the notebook editor if a notebook is selected
  if (!selectedNotebook) {
    return (
      <div className={`notebook-manager ${className} flex items-center justify-center h-full`}>
        <div className="text-center text-gray-500">
          <div className="mb-4">
            <svg className="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Notebook Selected</h3>
          <p className="text-gray-600">Select a notebook from the sidebar to start editing.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`notebook-manager ${className}`}>
      <NotebookEditor notebook={selectedNotebook} />
    </div>
  );
};

// Export the manager functions for use in other components
export const useNotebookManager = () => {
  const store = useWorkbookStore();
  
  const createNotebook = async (workbookId: string, title: string, description: string = '') => {
    // Implementation would go here - for now, use the store directly
    const newNotebook: Notebook = {
      id: `nb_${Date.now()}`,
      title,
      description,
      workbookId,
      cells: [],
      metadata: {},
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };
    
    store.addNotebook(workbookId, newNotebook);
    return newNotebook;
  };

  return {
    ...store,
    createNotebook,
    // Add any additional notebook-specific methods here
  };
};
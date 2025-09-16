'use client';

import React from 'react';
import { Cell, CellType } from '@ai-jupyter/shared';

interface CellToolbarProps {
  cell: Cell;
  isSelected: boolean;
  isExecuting: boolean;
  canMoveUp: boolean;
  canMoveDown: boolean;
  onExecute: () => void;
  onDelete: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onAddAbove: () => void;
  onAddBelow: () => void;
}

export const CellToolbar: React.FC<CellToolbarProps> = ({
  cell,
  isSelected,
  isExecuting,
  canMoveUp,
  canMoveDown,
  onExecute,
  onDelete,
  onMoveUp,
  onMoveDown,
  onAddAbove,
  onAddBelow
}) => {
  if (!isSelected) return null;

  const canExecute = cell.cellType === CellType.CODE || 
                    cell.cellType === CellType.PHYSICS || 
                    cell.cellType === CellType.VISUALIZATION;

  return (
    <div className="cell-toolbar flex items-center justify-between bg-gray-100 px-4 py-2 border-b border-gray-200">
      <div className="flex items-center gap-2">
        {/* Add cells */}
        <button
          onClick={onAddAbove}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
          title="Add cell above"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        
        <button
          onClick={onAddBelow}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
          title="Add cell below"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>

        <div className="w-px h-4 bg-gray-300 mx-1"></div>

        {/* Move cells */}
        <button
          onClick={onMoveUp}
          disabled={!canMoveUp}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Move cell up"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>
        
        <button
          onClick={onMoveDown}
          disabled={!canMoveDown}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Move cell down"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <div className="flex items-center gap-2">
        {/* Execute button */}
        {canExecute && (
          <button
            onClick={onExecute}
            disabled={isExecuting}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            title="Execute cell (Ctrl+Enter)"
          >
            {isExecuting ? (
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Running</span>
              </div>
            ) : (
              'Run'
            )}
          </button>
        )}

        <div className="w-px h-4 bg-gray-300 mx-1"></div>

        {/* Delete button */}
        <button
          onClick={onDelete}
          className="p-1 text-red-600 hover:text-red-800 hover:bg-red-100 rounded"
          title="Delete cell"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  );
};
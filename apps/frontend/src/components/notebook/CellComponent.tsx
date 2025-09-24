'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Cell, CellType, CellOutput } from '@ai-jupyter/shared';
import { CodeCell } from './cells/CodeCell';
import { MarkdownCell } from './cells/MarkdownCell';
import { PhysicsCell } from './cells/PhysicsCell';
import { VisualizationCell } from './cells/VisualizationCell';
import { CellOutput as CellOutputComponent } from './CellOutput';

interface CellComponentProps {
  cell: Cell;
  isSelected: boolean;
  isExecuting: boolean;
  onContentChange: (content: string) => void;
  onSelect: () => void;
  onExecute: () => void;
  sessionId?: string;
}

export const CellComponent: React.FC<CellComponentProps> = ({
  cell,
  isSelected,
  isExecuting,
  onContentChange,
  onSelect,
  onExecute,
  sessionId
}) => {
  const cellRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  const handleClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect();
  }, [onSelect]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      onExecute();
    }
  }, [onExecute]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
    onSelect();
  }, [onSelect]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  // Auto-focus when cell is selected
  useEffect(() => {
    if (isSelected && cellRef.current) {
      const focusableElement = cellRef.current.querySelector('[data-focusable="true"]') as HTMLElement;
      if (focusableElement && document.activeElement !== focusableElement) {
        focusableElement.focus();
      }
    }
  }, [isSelected]);

  const getCellTypeColor = (cellType: CellType): string => {
    switch (cellType) {
      case CellType.CODE:
        return 'border-l-blue-500';
      case CellType.MARKDOWN:
        return 'border-l-green-500';
      case CellType.PHYSICS:
        return 'border-l-purple-500';
      case CellType.VISUALIZATION:
        return 'border-l-orange-500';
      default:
        return 'border-l-gray-500';
    }
  };

  const getCellTypeLabel = (cellType: CellType): string => {
    switch (cellType) {
      case CellType.CODE:
        return 'Code';
      case CellType.MARKDOWN:
        return 'Markdown';
      case CellType.PHYSICS:
        return 'Physics';
      case CellType.VISUALIZATION:
        return 'Visualization';
      default:
        return 'Unknown';
    }
  };

  const renderCellEditor = () => {
    const commonProps = {
      cell,
      isSelected,
      isFocused,
      onContentChange,
      onFocus: handleFocus,
      onBlur: handleBlur,
      onKeyDown: handleKeyDown,
      sessionId
    };

    switch (cell.cellType) {
      case CellType.CODE:
        return <CodeCell {...commonProps} />;
      case CellType.MARKDOWN:
        return <MarkdownCell {...commonProps} />;
      case CellType.PHYSICS:
        return <PhysicsCell {...commonProps} />;
      case CellType.VISUALIZATION:
        return <VisualizationCell {...commonProps} />;
      default:
        return <CodeCell {...commonProps} />;
    }
  };

  return (
    <div
      ref={cellRef}
      className={`
        cell-component border-l-4 ${getCellTypeColor(cell.cellType)}
        ${isSelected ? 'ring-2 ring-blue-300 bg-blue-50' : 'bg-white'}
        ${isFocused ? 'ring-2 ring-blue-400' : ''}
        rounded-r-lg shadow-sm hover:shadow-md transition-all duration-200
        ${isExecuting ? 'opacity-75' : ''}
      `}
      onClick={handleClick}
      data-testid={`cell-${cell.id}`}
    >
      {/* Cell Header */}
      <div className="cell-header flex items-center justify-between px-4 py-2 bg-gray-50 border-b">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
            {getCellTypeLabel(cell.cellType)}
          </span>
          {cell.executionCount > 0 && (
            <span className="text-xs text-gray-500">
              [{cell.executionCount}]
            </span>
          )}
          {isExecuting && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-blue-600">Executing...</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {(cell.cellType === CellType.CODE || cell.cellType === CellType.PHYSICS || cell.cellType === CellType.VISUALIZATION) && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onExecute();
              }}
              disabled={isExecuting}
              className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Execute cell (Ctrl+Enter)"
            >
              {isExecuting ? 'Running...' : 'Run'}
            </button>
          )}
        </div>
      </div>

      {/* Cell Content */}
      <div className="cell-content">
        {renderCellEditor()}
      </div>

      {/* Cell Output */}
      {cell.outputs.length > 0 && (
        <div className="cell-outputs border-t bg-gray-50">
          {cell.outputs.map((output, index) => (
            <CellOutputComponent
              key={index}
              output={output}
              cellType={cell.cellType}
            />
          ))}
        </div>
      )}
    </div>
  );
};
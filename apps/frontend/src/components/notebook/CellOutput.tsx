'use client';

import React from 'react';
import { CellOutput as CellOutputType, CellType } from '@ai-jupyter/shared';
import { VisualizationOutput } from '../visualization/VisualizationOutput';

interface CellOutputProps {
  output: CellOutputType;
  cellType: CellType;
}

export const CellOutput: React.FC<CellOutputProps> = ({ output, cellType }) => {
  const renderOutput = () => {
    switch (output.outputType) {
      case 'text':
        return (
          <pre className={`
            text-sm font-mono whitespace-pre-wrap p-3
            ${output.metadata?.error ? 'text-red-600 bg-red-50' : 'text-gray-800'}
          `}>
            {output.data}
          </pre>
        );

      case 'html':
        return (
          <div 
            className="p-3"
            dangerouslySetInnerHTML={{ __html: output.data }}
          />
        );

      case 'image':
        return (
          <div className="p-3">
            <img 
              src={output.data} 
              alt="Cell output" 
              className="max-w-full h-auto rounded"
            />
          </div>
        );

      case 'visualization':
        return (
          <div className="p-3">
            <VisualizationOutput 
              data={output.data} 
              metadata={output.metadata}
            />
          </div>
        );

      default:
        return (
          <div className="p-3 text-gray-500 text-sm">
            Unknown output type: {output.outputType}
          </div>
        );
    }
  };

  return (
    <div className="cell-output border-t border-gray-200">
      {output.metadata?.timestamp && (
        <div className="px-3 py-1 bg-gray-100 text-xs text-gray-500 border-b border-gray-200">
          Output from {new Date(output.metadata.timestamp).toLocaleTimeString()}
        </div>
      )}
      {renderOutput()}
    </div>
  );
};
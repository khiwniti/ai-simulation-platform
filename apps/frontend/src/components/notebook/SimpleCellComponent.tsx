'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Trash2, 
  Plus, 
  Code, 
  FileText, 
  Zap,
  MoreVertical,
  Copy,
  ArrowUp,
  ArrowDown,
  Sparkles
} from 'lucide-react';
import { InlineAIAssistance } from './InlineAIAssistance';

interface Cell {
  id: string;
  type: 'code' | 'markdown' | 'physics';
  content: string;
  output?: {
    text?: string;
    figures?: string[];
    error?: {
      type: string;
      message: string;
      traceback: string;
    };
  };
  isRunning?: boolean;
  executionId?: string;
}

interface SimpleCellComponentProps {
  cell: Cell;
  onUpdate: (content: string) => void;
  onDelete: () => void;
  onRun: () => void;
  onAddCell: (type: 'code' | 'markdown' | 'physics') => void;
  onFocus?: () => void;
}

export function CellComponent({ 
  cell, 
  onUpdate, 
  onDelete, 
  onRun, 
  onAddCell,
  onFocus
}: SimpleCellComponentProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [showAI, setShowAI] = useState(false);
  const [cursorPosition, setCursorPosition] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const getCellIcon = () => {
    switch (cell.type) {
      case 'code': return <Code className="w-4 h-4" />;
      case 'markdown': return <FileText className="w-4 h-4" />;
      case 'physics': return <Zap className="w-4 h-4" />;
      default: return <Code className="w-4 h-4" />;
    }
  };

  const getCellColor = () => {
    switch (cell.type) {
      case 'code': return 'border-l-blue-500 bg-blue-50/30';
      case 'markdown': return 'border-l-green-500 bg-green-50/30';
      case 'physics': return 'border-l-purple-500 bg-purple-50/30';
      default: return 'border-l-gray-500 bg-gray-50/30';
    }
  };

  const handleAISuggestion = (code: string) => {
    const currentContent = cell.content;
    const newContent = currentContent + '\n\n' + code;
    onUpdate(newContent);
    setShowAI(false);
  };

  const handleTextChange = (newContent: string) => {
    onUpdate(newContent);
    
    // Show AI assistance for code and physics cells when there's substantial content
    if ((cell.type === 'code' || cell.type === 'physics') && 
        newContent.length > 20 && 
        newContent.length % 50 === 0) { // Trigger every 50 characters
      setShowAI(true);
    }
  };

  const handleTextFocus = () => {
    setIsEditing(true);
    // Notify parent component that this cell is focused
    onFocus?.();
    // Show AI assistance after a delay when focusing on code/physics cells
    if (cell.type === 'code' || cell.type === 'physics') {
      setTimeout(() => setShowAI(true), 2000);
    }
  };

  const handleTextBlur = () => {
    setIsEditing(false);
    setTimeout(() => setShowAI(false), 3000); // Hide AI after delay
  };

  const renderContent = () => {
    if (cell.type === 'markdown' && !isEditing && cell.content) {
      // Simple markdown rendering for demo
      return (
        <div 
          className="prose prose-sm max-w-none p-4 cursor-pointer"
          onClick={() => setIsEditing(true)}
          dangerouslySetInnerHTML={{ 
            __html: cell.content
              .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mb-4">$1</h1>')
              .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mb-3">$1</h2>')
              .replace(/^### (.*$)/gim, '<h3 class="text-lg font-medium mb-2">$1</h3>')
              .replace(/^\- (.*$)/gim, '<li class="ml-4">• $1</li>')
              .replace(/\n/g, '<br>')
          }}
        />
      );
    }

    return (
      <textarea
        ref={textareaRef}
        value={cell.content}
        onChange={(e) => handleTextChange(e.target.value)}
        onFocus={handleTextFocus}
        onBlur={handleTextBlur}
        onSelect={(e) => {
          const target = e.target as HTMLTextAreaElement;
          setCursorPosition(target.selectionStart);
        }}
        placeholder={`Enter ${cell.type} content...`}
        className="w-full min-h-[120px] p-4 bg-transparent border-none outline-none resize-none font-mono text-sm"
        style={{ 
          fontFamily: cell.type === 'code' || cell.type === 'physics' 
            ? 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace' 
            : 'inherit'
        }}
      />
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative group border-l-4 ${getCellColor()} bg-white dark:bg-gray-800 rounded-r-lg shadow-sm hover:shadow-md transition-all`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Cell Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/50">
        <div className="flex items-center space-x-2">
          {getCellIcon()}
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
            {cell.type}
          </span>
          {cell.isRunning && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-blue-600">Running...</span>
            </div>
          )}
        </div>

        {/* Cell Actions */}
        <div className={`flex items-center space-x-1 transition-opacity ${showActions ? 'opacity-100' : 'opacity-0'}`}>
          {(cell.type === 'code' || cell.type === 'physics') && (
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowAI(!showAI);
                }}
                className={`p-1 rounded transition-colors ${
                  showAI 
                    ? 'text-purple-700 bg-purple-100 dark:bg-purple-900/20' 
                    : 'text-purple-600 hover:bg-purple-100 dark:hover:bg-purple-900/20'
                }`}
                title="AI Assistance"
              >
                <Sparkles className="w-3 h-3" />
              </button>
              <button
                onClick={onRun}
                disabled={cell.isRunning}
                className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/20 rounded transition-colors disabled:opacity-50"
                title="Run cell"
              >
                <Play className="w-3 h-3" />
              </button>
            </>
          )}
          
          {cell.type === 'markdown' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowAI(!showAI);
              }}
              className={`p-1 rounded transition-colors ${
                showAI 
                  ? 'text-purple-700 bg-purple-100 dark:bg-purple-900/20' 
                  : 'text-purple-600 hover:bg-purple-100 dark:hover:bg-purple-900/20'
              }`}
              title="AI Writing Assistant"
            >
              <Sparkles className="w-3 h-3" />
            </button>
          )}
          
          <div className="relative group/menu">
            <button className="p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors">
              <MoreVertical className="w-3 h-3" />
            </button>
            
            <div className="absolute right-0 top-full mt-1 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover/menu:opacity-100 group-hover/menu:visible transition-all z-10">
              <button
                onClick={() => onAddCell('code')}
                className="w-full flex items-center space-x-2 px-3 py-2 text-xs hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Plus className="w-3 h-3" />
                <span>Add Below</span>
              </button>
              <button
                onClick={onDelete}
                className="w-full flex items-center space-x-2 px-3 py-2 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <Trash2 className="w-3 h-3" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Cell Content */}
      <div className="relative">
        {renderContent()}
        
        {/* Inline AI Assistance */}
        <InlineAIAssistance
          cellContent={cell.content}
          cellType={cell.type}
          cursorPosition={cursorPosition}
          onAcceptSuggestion={handleAISuggestion}
          onRejectSuggestion={() => setShowAI(false)}
          isVisible={showAI && (cell.type === 'code' || cell.type === 'physics')}
        />
      </div>

      {/* Cell Output */}
      {cell.output && (
        <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/50 p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Output:</div>
          
          {/* Error Display */}
          {cell.output.error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3 mb-3">
              <div className="text-red-800 dark:text-red-200 font-medium text-sm mb-1">
                {cell.output.error.type}: {cell.output.error.message}
              </div>
              {cell.output.error.traceback && (
                <details className="mt-2">
                  <summary className="text-xs text-red-600 dark:text-red-400 cursor-pointer">
                    Show traceback
                  </summary>
                  <pre className="text-xs text-red-700 dark:text-red-300 mt-1 overflow-x-auto">
                    {cell.output.error.traceback}
                  </pre>
                </details>
              )}
            </div>
          )}
          
          {/* Text Output */}
          {cell.output.text && (
            <div className="bg-white dark:bg-gray-800 rounded border p-3 font-mono text-sm mb-3">
              <pre className="whitespace-pre-wrap">{cell.output.text}</pre>
            </div>
          )}
          
          {/* Figure Output */}
          {cell.output.figures && cell.output.figures.length > 0 && (
            <div className="space-y-3">
              {cell.output.figures.map((figureData, index) => (
                <div key={index} className="bg-white dark:bg-gray-800 rounded border p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    Figure {index + 1}:
                  </div>
                  <img 
                    src={`data:image/png;base64,${figureData}`}
                    alt={`Generated figure ${index + 1}`}
                    className="max-w-full h-auto rounded"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
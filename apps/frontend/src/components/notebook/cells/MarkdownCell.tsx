'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Cell } from '@ai-jupyter/shared';

interface MarkdownCellProps {
  cell: Cell;
  isSelected: boolean;
  isFocused: boolean;
  onContentChange: (content: string) => void;
  onFocus: () => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

export const MarkdownCell: React.FC<MarkdownCellProps> = ({
  cell,
  isSelected,
  isFocused,
  onContentChange,
  onFocus,
  onBlur,
  onKeyDown
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleDoubleClick = useCallback(() => {
    setIsEditing(true);
  }, []);

  const handleTextareaChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onContentChange(e.target.value);
  }, [onContentChange]);

  const handleTextareaKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      setIsEditing(false);
      e.preventDefault();
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      setIsEditing(false);
      e.preventDefault();
    }
    onKeyDown(e);
  }, [onKeyDown]);

  const handleTextareaFocus = useCallback(() => {
    onFocus();
  }, [onFocus]);

  const handleTextareaBlur = useCallback(() => {
    onBlur();
    // Don't exit editing mode immediately on blur to allow for toolbar interactions
    setTimeout(() => {
      if (document.activeElement?.tagName !== 'BUTTON') {
        setIsEditing(false);
      }
    }, 100);
  }, [onBlur]);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, []);

  useEffect(() => {
    if (isEditing) {
      adjustTextareaHeight();
    }
  }, [isEditing, cell.content, adjustTextareaHeight]);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isEditing]);

  // Start editing when cell is selected and focused
  useEffect(() => {
    if (isSelected && isFocused && !isEditing) {
      setIsEditing(true);
    }
  }, [isSelected, isFocused, isEditing]);

  // Simple markdown rendering (basic implementation)
  const renderMarkdown = (content: string) => {
    if (!content.trim()) {
      return (
        <div className="text-gray-400 italic p-4">
          Double-click to edit this markdown cell
        </div>
      );
    }

    // Basic markdown parsing (in a real app, you'd use a proper markdown parser)
    let html = content
      // Headers
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
      // Bold and italic
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-3 rounded font-mono text-sm overflow-x-auto"><code>$1</code></pre>')
      // Inline code
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded font-mono text-sm">$1</code>')
      // Line breaks
      .replace(/\n/g, '<br>');

    return <div dangerouslySetInnerHTML={{ __html: html }} />;
  };

  if (isEditing) {
    return (
      <div className="markdown-cell-editor p-4">
        <div className="mb-2 text-xs text-gray-500">
          Editing markdown (Ctrl+Enter to finish, Esc to cancel)
        </div>
        <textarea
          ref={textareaRef}
          value={cell.content}
          onChange={handleTextareaChange}
          onKeyDown={handleTextareaKeyDown}
          onFocus={handleTextareaFocus}
          onBlur={handleTextareaBlur}
          onInput={adjustTextareaHeight}
          className="w-full p-3 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          placeholder="Enter markdown content..."
          data-focusable="true"
        />
      </div>
    );
  }

  return (
    <div 
      className="markdown-cell-rendered p-4 cursor-pointer hover:bg-gray-50 min-h-[60px]"
      onDoubleClick={handleDoubleClick}
      onClick={onFocus}
      data-focusable="true"
      tabIndex={0}
      onKeyDown={onKeyDown}
    >
      {renderMarkdown(cell.content)}
    </div>
  );
};
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { InlineSuggestion } from '../../services/inlineAssistanceService';

interface InlineSuggestionWidgetProps {
  suggestions: InlineSuggestion[];
  position: { top: number; left: number };
  onAccept: (suggestion: InlineSuggestion) => void;
  onReject: (suggestion: InlineSuggestion, reason?: string) => void;
  onClose: () => void;
  visible: boolean;
}

export const InlineSuggestionWidget: React.FC<InlineSuggestionWidgetProps> = ({
  suggestions,
  position,
  onAccept,
  onReject,
  onClose,
  visible
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const widgetRef = useRef<HTMLDivElement>(null);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!visible || suggestions.length === 0) return;

      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => Math.max(0, prev - 1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => Math.min(suggestions.length - 1, prev + 1));
          break;
        case 'Enter':
          e.preventDefault();
          if (suggestions[selectedIndex]) {
            onAccept(suggestions[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
        case 'Tab':
          e.preventDefault();
          if (suggestions[selectedIndex]) {
            onAccept(suggestions[selectedIndex]);
          }
          break;
        case 'i':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            setShowDetails(!showDetails);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [visible, suggestions, selectedIndex, onAccept, onClose, showDetails]);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (widgetRef.current && !widgetRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (visible) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [visible, onClose]);

  // Reset selected index when suggestions change
  useEffect(() => {
    setSelectedIndex(0);
  }, [suggestions]);

  if (!visible || suggestions.length === 0) {
    return null;
  }

  const selectedSuggestion = suggestions[selectedIndex];

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1: return 'border-blue-500 bg-blue-50';
      case 2: return 'border-yellow-500 bg-yellow-50';
      case 3: return 'border-gray-500 bg-gray-50';
      default: return 'border-gray-300 bg-white';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'completion': return '💡';
      case 'fix': return '🔧';
      case 'optimization': return '⚡';
      case 'explanation': return '📖';
      default: return '💭';
    }
  };

  return (
    <div
      ref={widgetRef}
      className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg max-w-md"
      style={{
        top: position.top,
        left: position.left,
        maxHeight: '400px'
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-2 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">AI Suggestions</span>
          <span className="text-xs text-gray-500">({suggestions.length})</span>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title="Toggle details (Ctrl+I)"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title="Close (Esc)"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Suggestions List */}
      <div className="max-h-60 overflow-y-auto">
        {suggestions.map((suggestion, index) => (
          <div
            key={suggestion.id}
            className={`p-3 border-b border-gray-100 cursor-pointer transition-colors ${
              index === selectedIndex 
                ? `${getPriorityColor(suggestion.priority)} border-l-4` 
                : 'hover:bg-gray-50'
            }`}
            onClick={() => {
              setSelectedIndex(index);
              onAccept(suggestion);
            }}
            onMouseEnter={() => setSelectedIndex(index)}
          >
            <div className="flex items-start space-x-2">
              <span className="text-lg">{getTypeIcon(suggestion.suggestionType)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {suggestion.text}
                  </span>
                  <span className="text-xs text-gray-500 bg-gray-100 px-1 rounded">
                    {suggestion.agentType}
                  </span>
                </div>
                
                {showDetails && (
                  <div className="space-y-1">
                    {suggestion.insertText && (
                      <div className="text-xs bg-gray-100 p-2 rounded font-mono">
                        {suggestion.insertText}
                      </div>
                    )}
                    {suggestion.explanation && (
                      <p className="text-xs text-gray-600">{suggestion.explanation}</p>
                    )}
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>Confidence: {Math.round(suggestion.confidenceScore * 100)}%</span>
                      <span>•</span>
                      <span>Priority: {suggestion.priority}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer with actions */}
      <div className="p-2 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            ↑↓ Navigate • Enter/Tab Accept • Esc Close
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => onReject(selectedSuggestion, 'not_helpful')}
              className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
              title="Reject suggestion"
            >
              Reject
            </button>
            <button
              onClick={() => onAccept(selectedSuggestion)}
              className="px-2 py-1 text-xs bg-blue-500 text-white hover:bg-blue-600 rounded"
              title="Accept suggestion"
            >
              Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InlineSuggestionWidget;
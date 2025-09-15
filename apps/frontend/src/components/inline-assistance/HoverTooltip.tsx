'use client';

import React, { useState, useEffect } from 'react';
import { InlineSuggestion } from '../../services/inlineAssistanceService';

interface HoverTooltipProps {
  suggestion: InlineSuggestion | null;
  position: { top: number; left: number };
  visible: boolean;
  onClose: () => void;
}

export const HoverTooltip: React.FC<HoverTooltipProps> = ({
  suggestion,
  position,
  visible,
  onClose
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Auto-close after delay
  useEffect(() => {
    if (visible) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000); // Auto-close after 5 seconds

      return () => clearTimeout(timer);
    }
  }, [visible, onClose]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (visible) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [visible, onClose]);

  if (!visible || !suggestion) {
    return null;
  }

  const getAgentColor = (agentType: string) => {
    switch (agentType) {
      case 'physics': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'visualization': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'optimization': return 'bg-green-100 text-green-800 border-green-200';
      case 'debug': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'explanation': return '📖';
      case 'completion': return '💡';
      case 'fix': return '🔧';
      case 'optimization': return '⚡';
      default: return '💭';
    }
  };

  return (
    <div
      className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg max-w-sm"
      style={{
        top: position.top,
        left: position.left,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getTypeIcon(suggestion.suggestionType)}</span>
          <span className={`px-2 py-1 text-xs font-medium rounded border ${getAgentColor(suggestion.agentType)}`}>
            {suggestion.agentType}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 rounded"
          title="Close"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="space-y-2">
          {/* Main explanation */}
          <div className="text-sm text-gray-900">
            {suggestion.explanation || suggestion.text}
          </div>

          {/* Code snippet if available */}
          {suggestion.insertText && (
            <div className="bg-gray-100 p-2 rounded text-xs font-mono">
              <div className="text-gray-600 mb-1">Code:</div>
              <div className="text-gray-900">{suggestion.insertText}</div>
            </div>
          )}

          {/* Documentation link if available */}
          {suggestion.documentation && (
            <div className="text-xs">
              <span className="text-gray-600">Documentation: </span>
              <a 
                href={suggestion.documentation} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Learn more
              </a>
            </div>
          )}

          {/* Expandable details */}
          {(suggestion.explanation && suggestion.text !== suggestion.explanation) && (
            <div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <span>{isExpanded ? 'Show less' : 'Show more'}</span>
                <svg 
                  className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {isExpanded && (
                <div className="mt-2 text-xs text-gray-600 space-y-1">
                  <div>
                    <span className="font-medium">Confidence:</span> {Math.round(suggestion.confidenceScore * 100)}%
                  </div>
                  <div>
                    <span className="font-medium">Priority:</span> {suggestion.priority === 1 ? 'High' : suggestion.priority === 2 ? 'Medium' : 'Low'}
                  </div>
                  <div>
                    <span className="font-medium">Agent ID:</span> {suggestion.agentId}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <div className="text-xs text-gray-500 text-center">
          Press Esc to close • Auto-closes in 5s
        </div>
      </div>
    </div>
  );
};

export default HoverTooltip;
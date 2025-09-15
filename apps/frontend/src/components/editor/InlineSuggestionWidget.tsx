/**
 * Enhanced Inline Suggestion Widget for AI-powered code assistance.
 */

import React, { useState, useEffect, useRef } from 'react';
import { InlineSuggestion } from '../../services/inlineAssistanceService';

interface InlineSuggestionWidgetProps {
  suggestions: InlineSuggestion[];
  visible: boolean;
  position: { top: number; left: number };
  onApplySuggestion: (suggestion: InlineSuggestion) => void;
  onRejectSuggestion: (suggestion: InlineSuggestion, reason?: string) => void;
  onHide: () => void;
  maxSuggestions?: number;
}

interface SuggestionItemProps {
  suggestion: InlineSuggestion;
  index: number;
  isSelected: boolean;
  onApply: () => void;
  onReject: (reason?: string) => void;
  onSelect: () => void;
}

const SuggestionItem: React.FC<SuggestionItemProps> = ({
  suggestion,
  index,
  isSelected,
  onApply,
  onReject,
  onSelect
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectDialog, setShowRejectDialog] = useState(false);

  const getSuggestionIcon = (type: string, provider?: string) => {
    if (provider?.includes('ai_provider')) {
      return '🤖';
    }
    
    switch (type) {
      case 'completion': return '💡';
      case 'fix': return '🔧';
      case 'optimization': return '⚡';
      case 'explanation': return '📖';
      default: return '💭';
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1: return 'text-red-600 font-bold';
      case 2: return 'text-orange-600 font-semibold';
      case 3: return 'text-blue-600';
      case 4: return 'text-gray-600';
      default: return 'text-gray-500';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div
      className={`p-3 border-l-4 cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'bg-blue-50 border-blue-500 shadow-md' 
          : 'bg-white border-gray-200 hover:bg-gray-50'
      }`}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onApply();
        if (e.key === 'Delete') setShowRejectDialog(true);
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getSuggestionIcon(suggestion.suggestionType, suggestion.agentType)}</span>
            <span className="text-sm font-medium text-gray-900 truncate">
              {suggestion.text}
            </span>
            <span className={`text-xs px-2 py-1 rounded-full bg-gray-100 ${getPriorityColor(suggestion.priority)}`}>
              P{suggestion.priority}
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
            <span>Agent: {suggestion.agentType}</span>
            <span className={getConfidenceColor(suggestion.confidenceScore)}>
              {Math.round(suggestion.confidenceScore * 100)}% confidence
            </span>
            {suggestion.metadata?.model_used && (
              <span>Model: {suggestion.metadata.model_used}</span>
            )}
            {suggestion.metadata?.processing_time && (
              <span>{suggestion.metadata.processing_time}ms</span>
            )}
          </div>

          {suggestion.insertText && (
            <div className="bg-gray-100 p-2 rounded text-sm font-mono text-gray-800 mb-2 max-h-20 overflow-y-auto">
              {suggestion.insertText}
            </div>
          )}

          {showDetails && suggestion.explanation && (
            <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-gray-700">
              {suggestion.explanation}
            </div>
          )}

          {showDetails && suggestion.documentation && (
            <div className="mt-2 p-2 bg-green-50 rounded text-sm text-gray-600">
              <strong>Documentation:</strong> {suggestion.documentation}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-1 ml-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onApply();
            }}
            className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            title={`Apply suggestion (Ctrl+${index + 1})`}
          >
            Apply
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowDetails(!showDetails);
            }}
            className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          >
            {showDetails ? 'Less' : 'More'}
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowRejectDialog(true);
            }}
            className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
            title="Reject suggestion"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
          <div className="text-sm font-medium text-red-800 mb-2">Why reject this suggestion?</div>
          <textarea
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Optional feedback..."
            className="w-full p-1 text-xs border border-red-300 rounded resize-none"
            rows={2}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => {
                onReject(rejectReason);
                setShowRejectDialog(false);
                setRejectReason('');
              }}
              className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reject
            </button>
            <button
              onClick={() => {
                setShowRejectDialog(false);
                setRejectReason('');
              }}
              className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export const InlineSuggestionWidget: React.FC<InlineSuggestionWidgetProps> = ({
  suggestions,
  visible,
  position,
  onApplySuggestion,
  onRejectSuggestion,
  onHide,
  maxSuggestions = 5
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const widgetRef = useRef<HTMLDivElement>(null);

  // Limit and sort suggestions
  const limitedSuggestions = suggestions
    .slice(0, maxSuggestions)
    .sort((a, b) => {
      // Sort by priority (lower is better) then by confidence (higher is better)
      if (a.priority !== b.priority) {
        return a.priority - b.priority;
      }
      return b.confidenceScore - a.confidenceScore;
    });

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!visible || limitedSuggestions.length === 0) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => 
            prev < limitedSuggestions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => 
            prev > 0 ? prev - 1 : limitedSuggestions.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (limitedSuggestions[selectedIndex]) {
            onApplySuggestion(limitedSuggestions[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onHide();
          break;
        default:
          // Handle Ctrl+Number shortcuts for quick application
          if (e.ctrlKey && e.key >= '1' && e.key <= '9') {
            e.preventDefault();
            const index = parseInt(e.key) - 1;
            if (index < limitedSuggestions.length) {
              onApplySuggestion(limitedSuggestions[index]);
            }
          }
          break;
      }
    };

    if (visible) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [visible, limitedSuggestions, selectedIndex, onApplySuggestion, onHide]);

  // Handle clicks outside to hide widget
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (widgetRef.current && !widgetRef.current.contains(event.target as Node)) {
        onHide();
      }
    };

    if (visible) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [visible, onHide]);

  // Reset selection when suggestions change
  useEffect(() => {
    setSelectedIndex(0);
  }, [suggestions]);

  if (!visible || limitedSuggestions.length === 0) {
    return null;
  }

  return (
    <div
      ref={widgetRef}
      className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg max-w-md max-h-96 overflow-hidden"
      style={{
        top: position.top,
        left: position.left,
        minWidth: '300px'
      }}
    >
      {/* Header */}
      <div className="bg-gray-50 px-3 py-2 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">
              AI Suggestions ({limitedSuggestions.length})
            </span>
            {suggestions.length > maxSuggestions && (
              <span className="text-xs text-gray-500">
                Showing top {maxSuggestions}
              </span>
            )}
          </div>
          <button
            onClick={onHide}
            className="text-gray-400 hover:text-gray-600 text-lg"
            title="Close (Esc)"
          >
            ×
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Use ↑↓ to navigate, Enter to apply, Ctrl+1-9 for quick apply
        </div>
      </div>

      {/* Suggestions List */}
      <div className="max-h-80 overflow-y-auto">
        {limitedSuggestions.map((suggestion, index) => (
          <SuggestionItem
            key={suggestion.id}
            suggestion={suggestion}
            index={index}
            isSelected={index === selectedIndex}
            onApply={() => onApplySuggestion(suggestion)}
            onReject={(reason) => onRejectSuggestion(suggestion, reason)}
            onSelect={() => setSelectedIndex(index)}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-3 py-2 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Powered by AI • Press Escape to close
        </div>
      </div>
    </div>
  );
};

export default InlineSuggestionWidget;

/**
 * Hook for managing inline AI assistance functionality.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { 
  inlineAssistanceService, 
  InlineSuggestion, 
  InlineAssistanceRequest,
  InlineAssistanceResponse 
} from '../services/inlineAssistanceService';

interface UseInlineAssistanceOptions {
  sessionId: string;
  notebookId: string;
  cellId: string;
  debounceMs?: number;
  enableAutoCompletion?: boolean;
  enableHover?: boolean;
}

interface InlineAssistanceState {
  suggestions: InlineSuggestion[];
  isLoading: boolean;
  error: string | null;
  contextAnalysis: Record<string, any>;
  processingTime: number;
  agentsUsed: string[];
}

interface SuggestionWidgetState {
  visible: boolean;
  position: { top: number; left: number };
  suggestions: InlineSuggestion[];
}

interface HoverTooltipState {
  visible: boolean;
  position: { top: number; left: number };
  suggestion: InlineSuggestion | null;
}

export const useInlineAssistance = (options: UseInlineAssistanceOptions) => {
  const {
    sessionId,
    notebookId,
    cellId,
    debounceMs = 300,
    enableAutoCompletion = true,
    enableHover = true
  } = options;

  // State
  const [assistanceState, setAssistanceState] = useState<InlineAssistanceState>({
    suggestions: [],
    isLoading: false,
    error: null,
    contextAnalysis: {},
    processingTime: 0,
    agentsUsed: []
  });

  const [suggestionWidget, setSuggestionWidget] = useState<SuggestionWidgetState>({
    visible: false,
    position: { top: 0, left: 0 },
    suggestions: []
  });

  const [hoverTooltip, setHoverTooltip] = useState<HoverTooltipState>({
    visible: false,
    position: { top: 0, left: 0 },
    suggestion: null
  });

  // Refs
  const editorRef = useRef<any>(null);
  const lastRequestRef = useRef<string>('');
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Set the Monaco editor reference.
   */
  const setEditor = useCallback((editor: any) => {
    editorRef.current = editor;
  }, []);

  /**
   * Get suggestions for the current cursor position.
   */
  const getSuggestions = useCallback(async (
    codeContent: string,
    cursorPosition: number,
    lineNumber: number,
    columnNumber: number,
    triggerType: 'completion' | 'hover' | 'manual',
    useDebounce: boolean = false
  ): Promise<InlineAssistanceResponse | null> => {
    try {
      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      setAssistanceState(prev => ({ ...prev, isLoading: true, error: null }));

      const request: InlineAssistanceRequest = {
        sessionId,
        notebookId,
        cellId,
        codeContent,
        cursorPosition,
        lineNumber,
        columnNumber,
        triggerType
      };

      // Create request signature for deduplication
      const requestSignature = `${triggerType}_${cursorPosition}_${codeContent.length}`;
      
      // Skip if same request is already in progress
      if (lastRequestRef.current === requestSignature) {
        return null;
      }
      
      lastRequestRef.current = requestSignature;

      // Get suggestions
      const response = useDebounce 
        ? await inlineAssistanceService.getDebouncedSuggestions(request, debounceMs)
        : await inlineAssistanceService.getSuggestions(request);

      setAssistanceState(prev => ({
        ...prev,
        suggestions: response.suggestions,
        contextAnalysis: response.contextAnalysis,
        processingTime: response.processingTime,
        agentsUsed: response.agentsUsed,
        isLoading: false
      }));

      return response;

    } catch (error) {
      console.error('Error getting suggestions:', error);
      setAssistanceState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
      return null;
    }
  }, [sessionId, notebookId, cellId, debounceMs]);

  /**
   * Show suggestion widget at cursor position.
   */
  const showSuggestionWidget = useCallback((
    suggestions: InlineSuggestion[],
    editorPosition?: { top: number; left: number }
  ) => {
    if (!editorRef.current || suggestions.length === 0) return;

    let position = editorPosition;
    
    if (!position) {
      // Get cursor position from editor
      const cursorPos = editorRef.current.getPosition();
      if (cursorPos) {
        const coords = editorRef.current.getScrolledVisiblePosition(cursorPos);
        const editorElement = editorRef.current.getDomNode();
        const editorRect = editorElement?.getBoundingClientRect();
        
        if (coords && editorRect) {
          position = {
            top: editorRect.top + coords.top + 20,
            left: editorRect.left + coords.left
          };
        }
      }
    }

    if (position) {
      setSuggestionWidget({
        visible: true,
        position,
        suggestions
      });
    }
  }, []);

  /**
   * Hide suggestion widget.
   */
  const hideSuggestionWidget = useCallback(() => {
    setSuggestionWidget(prev => ({ ...prev, visible: false }));
  }, []);

  /**
   * Show hover tooltip.
   */
  const showHoverTooltip = useCallback((
    suggestion: InlineSuggestion,
    editorPosition?: { top: number; left: number }
  ) => {
    if (!editorRef.current) return;

    let position = editorPosition;
    
    if (!position) {
      // Get cursor position from editor
      const cursorPos = editorRef.current.getPosition();
      if (cursorPos) {
        const coords = editorRef.current.getScrolledVisiblePosition(cursorPos);
        const editorElement = editorRef.current.getDomNode();
        const editorRect = editorElement?.getBoundingClientRect();
        
        if (coords && editorRect) {
          position = {
            top: editorRect.top + coords.top - 10,
            left: editorRect.left + coords.left + 20
          };
        }
      }
    }

    if (position) {
      setHoverTooltip({
        visible: true,
        position,
        suggestion
      });
    }
  }, []);

  /**
   * Hide hover tooltip.
   */
  const hideHoverTooltip = useCallback(() => {
    setHoverTooltip(prev => ({ ...prev, visible: false }));
  }, []);

  /**
   * Handle auto-completion trigger.
   */
  const handleAutoCompletion = useCallback(async (
    codeContent: string,
    cursorPosition: number,
    lineNumber: number,
    columnNumber: number
  ) => {
    if (!enableAutoCompletion) return;

    const response = await getSuggestions(
      codeContent,
      cursorPosition,
      lineNumber,
      columnNumber,
      'completion',
      true // Use debounce for auto-completion
    );

    if (response && response.suggestions.length > 0) {
      // Filter for completion suggestions
      const completionSuggestions = response.suggestions.filter(
        s => s.suggestionType === 'completion'
      );
      
      if (completionSuggestions.length > 0) {
        showSuggestionWidget(completionSuggestions);
      }
    }
  }, [enableAutoCompletion, getSuggestions, showSuggestionWidget]);

  /**
   * Handle hover for explanations.
   */
  const handleHover = useCallback(async (
    codeContent: string,
    cursorPosition: number,
    lineNumber: number,
    columnNumber: number,
    word: string
  ) => {
    if (!enableHover || !word) return;

    const response = await getSuggestions(
      codeContent,
      cursorPosition,
      lineNumber,
      columnNumber,
      'hover'
    );

    if (response && response.suggestions.length > 0) {
      // Find explanation suggestion
      const explanationSuggestion = response.suggestions.find(
        s => s.suggestionType === 'explanation'
      );
      
      if (explanationSuggestion) {
        showHoverTooltip(explanationSuggestion);
      }
    }
  }, [enableHover, getSuggestions, showHoverTooltip]);

  /**
   * Handle manual assistance request.
   */
  const requestManualAssistance = useCallback(async (
    codeContent: string,
    cursorPosition: number,
    lineNumber: number,
    columnNumber: number
  ) => {
    const response = await getSuggestions(
      codeContent,
      cursorPosition,
      lineNumber,
      columnNumber,
      'manual'
    );

    if (response && response.suggestions.length > 0) {
      showSuggestionWidget(response.suggestions);
    }
  }, [getSuggestions, showSuggestionWidget]);

  /**
   * Apply a suggestion.
   */
  const applySuggestion = useCallback(async (suggestion: InlineSuggestion) => {
    try {
      // Apply to editor
      if (editorRef.current && suggestion.insertText) {
        if (suggestion.replaceRange) {
          (inlineAssistanceService.constructor as any).replaceTextRange(
            editorRef.current,
            suggestion.replaceRange.startPos,
            suggestion.replaceRange.endPos,
            suggestion.insertText
          );
        } else {
          (inlineAssistanceService.constructor as any).insertTextAtCursor(
            editorRef.current,
            suggestion.insertText
          );
        }
      }

      // Send feedback to backend
      await inlineAssistanceService.applySuggestion(suggestion.id, sessionId);
      
      // Hide widgets
      hideSuggestionWidget();
      hideHoverTooltip();

    } catch (error) {
      console.error('Error applying suggestion:', error);
    }
  }, [sessionId, hideSuggestionWidget, hideHoverTooltip]);

  /**
   * Reject a suggestion.
   */
  const rejectSuggestion = useCallback(async (
    suggestion: InlineSuggestion, 
    reason?: string
  ) => {
    try {
      // Send feedback to backend
      await inlineAssistanceService.rejectSuggestion(suggestion.id, sessionId, reason);
      
      // Hide widgets
      hideSuggestionWidget();
      hideHoverTooltip();

    } catch (error) {
      console.error('Error rejecting suggestion:', error);
    }
  }, [sessionId, hideSuggestionWidget, hideHoverTooltip]);

  /**
   * Clear all suggestions and hide widgets.
   */
  const clearSuggestions = useCallback(() => {
    inlineAssistanceService.clearSuggestions();
    hideSuggestionWidget();
    hideHoverTooltip();
    setAssistanceState(prev => ({
      ...prev,
      suggestions: [],
      error: null
    }));
  }, [hideSuggestionWidget, hideHoverTooltip]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      clearSuggestions();
    };
  }, [clearSuggestions]);

  return {
    // State
    assistanceState,
    suggestionWidget,
    hoverTooltip,
    
    // Actions
    setEditor,
    getSuggestions,
    handleAutoCompletion,
    handleHover,
    requestManualAssistance,
    applySuggestion,
    rejectSuggestion,
    clearSuggestions,
    
    // Widget controls
    showSuggestionWidget,
    hideSuggestionWidget,
    showHoverTooltip,
    hideHoverTooltip
  };
};

export default useInlineAssistance;
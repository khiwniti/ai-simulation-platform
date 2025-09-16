/**
 * Inline AI Assistance Service for frontend integration.
 */

export interface InlineAssistanceRequest {
  sessionId: string;
  notebookId: string;
  cellId: string;
  codeContent: string;
  cursorPosition: number;
  lineNumber: number;
  columnNumber: number;
  triggerType: 'completion' | 'hover' | 'manual';
  context?: Record<string, any>;
}

export interface InlineSuggestion {
  id: string;
  agentId: string;
  agentType: string;
  suggestionType: 'completion' | 'fix' | 'optimization' | 'explanation';
  text: string;
  insertText?: string;
  replaceRange?: {
    startPos: number;
    endPos: number;
  };
  confidenceScore: number;
  priority: number;
  explanation?: string;
  documentation?: string;
  metadata?: {
    model_used?: string;
    processing_time?: number;
    tokens_used?: number;
    provider?: string;
    domain?: string;
    intent?: string;
  };
}

export interface InlineAssistanceResponse {
  suggestions: InlineSuggestion[];
  contextAnalysis: Record<string, any>;
  processingTime: number;
  agentsUsed: string[];
  confidence?: number;
  providerStats?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface CodeContext {
  currentLine: string;
  currentWord: string;
  precedingCode: string;
  followingCode: string;
  functionContext?: string;
  classContext?: string;
  importStatements: string[];
  variablesInScope: string[];
  syntaxErrors: string[];
  codeType: 'physics' | 'visualization' | 'general' | 'math';
  indentationLevel: number;
  isInString: boolean;
  isInComment: boolean;
}

class InlineAssistanceService {
  private baseUrl: string;
  private activeSuggestions: Map<string, InlineSuggestion> = new Map();
  private suggestionCache: Map<string, InlineAssistanceResponse> = new Map();
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private performanceStats: {
    totalRequests: number;
    successfulRequests: number;
    averageResponseTime: number;
    cacheHitRate: number;
  } = {
    totalRequests: 0,
    successfulRequests: 0,
    averageResponseTime: 0,
    cacheHitRate: 0
  };

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Get enhanced inline suggestions for the current cursor position.
   */
  async getSuggestions(request: InlineAssistanceRequest): Promise<InlineAssistanceResponse> {
    const startTime = Date.now();
    this.performanceStats.totalRequests++;
    
    try {
      // Create cache key
      const cacheKey = this.createCacheKey(request);
      
      // Check cache first (more aggressive caching for completions)
      if (this.suggestionCache.has(cacheKey)) {
        const cached = this.suggestionCache.get(cacheKey)!;
        const cacheAge = Date.now() - (cached as any).timestamp;
        const maxAge = request.triggerType === 'completion' ? 3000 : 10000; // 3s for completions, 10s for others
        
        if (cacheAge < maxAge) {
          this.updateCacheHitRate(true);
          return cached;
        }
      }
      this.updateCacheHitRate(false);

      const response = await fetch(`${this.baseUrl}/api/v1/inline-assistance/suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': `${request.cellId}-${Date.now()}`,
        },
        body: JSON.stringify({
          session_id: request.sessionId,
          notebook_id: request.notebookId,
          cell_id: request.cellId,
          code_content: request.codeContent,
          cursor_position: request.cursorPosition,
          line_number: request.lineNumber,
          column_number: request.columnNumber,
          trigger_type: request.triggerType,
          context: request.context || {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: InlineAssistanceResponse = await response.json();
      
      // Update performance stats
      const responseTime = Date.now() - startTime;
      this.updatePerformanceStats(responseTime, true);
      
      // Enhanced result processing
      result.metadata = {
        ...result.metadata,
        requestTime: startTime,
        responseTime,
        cacheKey,
        requestId: `${request.cellId}-${Date.now()}`
      };
      
      // Cache the result with timestamp
      (result as any).timestamp = Date.now();
      this.suggestionCache.set(cacheKey, result);
      
      // Store active suggestions with enhanced metadata
      result.suggestions.forEach(suggestion => {
        suggestion.metadata = {
          ...suggestion.metadata,
          receivedAt: Date.now(),
          requestId: result.metadata?.requestId
        } as any;
        this.activeSuggestions.set(suggestion.id, suggestion);
      });

      return result;
    } catch (error) {
      console.error('Error getting inline suggestions:', error);
      this.updatePerformanceStats(Date.now() - startTime, false);
      
      return {
        suggestions: [],
        contextAnalysis: {},
        processingTime: Date.now() - startTime,
        agentsUsed: [],
        confidence: 0,
        metadata: {
          error: error instanceof Error ? error.message : 'Unknown error',
          requestTime: startTime,
          responseTime: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Get suggestions with debouncing for auto-completion.
   */
  async getDebouncedSuggestions(
    request: InlineAssistanceRequest,
    debounceMs: number = 300
  ): Promise<InlineAssistanceResponse> {
    return new Promise((resolve) => {
      const key = `${request.cellId}_${request.cursorPosition}`;
      
      // Clear existing timer
      if (this.debounceTimers.has(key)) {
        clearTimeout(this.debounceTimers.get(key)!);
      }
      
      // Set new timer
      const timer = setTimeout(async () => {
        const result = await this.getSuggestions(request);
        resolve(result);
        this.debounceTimers.delete(key);
      }, debounceMs);
      
      this.debounceTimers.set(key, timer);
    });
  }

  /**
   * Apply a suggestion and provide feedback to the backend.
   */
  async applySuggestion(suggestionId: string, sessionId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/inline-assistance/apply-suggestion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          suggestion_id: suggestionId,
          session_id: sessionId
        })
      });

      if (response.ok) {
        // Remove from active suggestions
        this.activeSuggestions.delete(suggestionId);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error applying suggestion:', error);
      return false;
    }
  }

  /**
   * Reject a suggestion and provide feedback to the backend.
   */
  async rejectSuggestion(
    suggestionId: string, 
    sessionId: string, 
    reason?: string
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/inline-assistance/reject-suggestion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          suggestion_id: suggestionId,
          session_id: sessionId,
          reason
        })
      });

      if (response.ok) {
        // Remove from active suggestions
        this.activeSuggestions.delete(suggestionId);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error rejecting suggestion:', error);
      return false;
    }
  }

  /**
   * Analyze code context for debugging purposes.
   */
  async analyzeCodeContext(
    codeContent: string,
    cursorPosition: number,
    lineNumber: number,
    columnNumber: number
  ): Promise<Record<string, any>> {
    try {
      const params = new URLSearchParams({
        code_content: codeContent,
        cursor_position: cursorPosition.toString(),
        line_number: lineNumber.toString(),
        column_number: columnNumber.toString()
      });

      const response = await fetch(
        `${this.baseUrl}/api/v1/inline-assistance/context-analysis?${params}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing code context:', error);
      return {};
    }
  }

  /**
   * Get an active suggestion by ID.
   */
  getSuggestion(suggestionId: string): InlineSuggestion | undefined {
    return this.activeSuggestions.get(suggestionId);
  }

  /**
   * Clear all active suggestions.
   */
  clearSuggestions(): void {
    this.activeSuggestions.clear();
  }

  /**
   * Clear suggestion cache.
   */
  clearCache(): void {
    this.suggestionCache.clear();
  }

  /**
   * Get performance statistics.
   */
  getPerformanceStats(): typeof this.performanceStats {
    return { ...this.performanceStats };
  }

  /**
   * Get service health status.
   */
  async getHealthStatus(): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/inline-assistance/health`);
      if (response.ok) {
        return await response.json();
      }
      return { status: 'unhealthy', error: `HTTP ${response.status}` };
    } catch (error) {
      return { 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  /**
   * Enable/disable real-time suggestions.
   */
  setRealTimeMode(enabled: boolean): void {
    // This could control whether to use streaming or batch suggestions
    (this as any).realTimeMode = enabled;
  }

  /**
   * Create a cache key for suggestions.
   */
  private createCacheKey(request: InlineAssistanceRequest): string {
    // Include more context for better cache granularity
    const contentHash = this.simpleHash(request.codeContent.substring(
      Math.max(0, request.cursorPosition - 100),
      request.cursorPosition + 100
    ));
    return `${request.cellId}_${request.cursorPosition}_${request.triggerType}_${contentHash}`;
  }

  /**
   * Simple hash function for cache keys.
   */
  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }

  /**
   * Update performance statistics.
   */
  private updatePerformanceStats(responseTime: number, success: boolean): void {
    if (success) {
      this.performanceStats.successfulRequests++;
    }
    
    // Update average response time
    const total = this.performanceStats.totalRequests;
    this.performanceStats.averageResponseTime = (
      (this.performanceStats.averageResponseTime * (total - 1) + responseTime) / total
    );
  }

  /**
   * Update cache hit rate statistics.
   */
  private updateCacheHitRate(hit: boolean): void {
    const hitCount = this.performanceStats.cacheHitRate * this.performanceStats.totalRequests;
    this.performanceStats.cacheHitRate = (
      (hitCount + (hit ? 1 : 0)) / this.performanceStats.totalRequests
    );
  }

  /**
   * Get cursor position from Monaco editor position.
   */
  static getCursorPosition(editor: any): { line: number; column: number; position: number } {
    const position = editor.getPosition();
    const model = editor.getModel();
    
    if (!position || !model) {
      return { line: 1, column: 0, position: 0 };
    }

    const offset = model.getOffsetAt(position);
    
    return {
      line: position.lineNumber,
      column: position.column - 1, // Monaco uses 1-based columns, we use 0-based
      position: offset
    };
  }

  /**
   * Get word at cursor position in Monaco editor.
   */
  static getWordAtPosition(editor: any): string {
    const position = editor.getPosition();
    const model = editor.getModel();
    
    if (!position || !model) {
      return '';
    }

    const wordInfo = model.getWordAtPosition(position);
    return wordInfo?.word || '';
  }

  /**
   * Insert text at cursor position in Monaco editor.
   */
  static insertTextAtCursor(editor: any, text: string): void {
    const position = editor.getPosition();
    if (!position) return;

    editor.executeEdits('inline-assistance', [{
      range: {
        startLineNumber: position.lineNumber,
        startColumn: position.column,
        endLineNumber: position.lineNumber,
        endColumn: position.column
      },
      text: text
    }]);
  }

  /**
   * Replace text range in Monaco editor.
   */
  static replaceTextRange(
    editor: any, 
    startPos: number, 
    endPos: number, 
    text: string
  ): void {
    const model = editor.getModel();
    if (!model) return;

    const startPosition = model.getPositionAt(startPos);
    const endPosition = model.getPositionAt(endPos);

    editor.executeEdits('inline-assistance', [{
      range: {
        startLineNumber: startPosition.lineNumber,
        startColumn: startPosition.column,
        endLineNumber: endPosition.lineNumber,
        endColumn: endPosition.column
      },
      text: text
    }]);
  }
}

export const inlineAssistanceService = new InlineAssistanceService();
export default inlineAssistanceService;
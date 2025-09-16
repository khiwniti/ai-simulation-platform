/**
 * Tests for Inline Assistance Service
 */

import { inlineAssistanceService, InlineAssistanceRequest } from '../../services/inlineAssistanceService';

// Mock fetch
global.fetch = jest.fn();

describe('InlineAssistanceService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    inlineAssistanceService.clearSuggestions();
    inlineAssistanceService.clearCache();
  });

  describe('getSuggestions', () => {
    it('should fetch suggestions from API', async () => {
      const mockResponse = {
        suggestions: [
          {
            id: 'test-suggestion-1',
            agentId: 'physics-agent',
            agentType: 'physics',
            suggestionType: 'completion',
            text: 'Create physics scene',
            insertText: 'scene = physx.create_scene()',
            confidenceScore: 0.9,
            priority: 1
          }
        ],
        contextAnalysis: { codeType: 'physics' },
        processingTime: 0.1,
        agentsUsed: ['physics']
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const request: InlineAssistanceRequest = {
        sessionId: 'test-session',
        notebookId: 'test-notebook',
        cellId: 'test-cell',
        codeContent: 'import physx\n',
        cursorPosition: 13,
        lineNumber: 2,
        columnNumber: 0,
        triggerType: 'completion'
      };

      const result = await inlineAssistanceService.getSuggestions(request);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/inline-assistance/suggestions'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('test-session')
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const request: InlineAssistanceRequest = {
        sessionId: 'test-session',
        notebookId: 'test-notebook',
        cellId: 'test-cell',
        codeContent: 'test code',
        cursorPosition: 0,
        lineNumber: 1,
        columnNumber: 0,
        triggerType: 'completion'
      };

      const result = await inlineAssistanceService.getSuggestions(request);

      expect(result).toEqual({
        suggestions: [],
        contextAnalysis: {},
        processingTime: 0,
        agentsUsed: []
      });
    });

    it('should cache suggestions', async () => {
      const mockResponse = {
        suggestions: [],
        contextAnalysis: {},
        processingTime: 0.1,
        agentsUsed: []
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const request: InlineAssistanceRequest = {
        sessionId: 'test-session',
        notebookId: 'test-notebook',
        cellId: 'test-cell',
        codeContent: 'test',
        cursorPosition: 4,
        lineNumber: 1,
        columnNumber: 4,
        triggerType: 'completion'
      };

      // First call
      await inlineAssistanceService.getSuggestions(request);
      
      // Second call should use cache
      const result = await inlineAssistanceService.getSuggestions(request);

      expect(fetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(expect.objectContaining(mockResponse));
    });
  });

  describe('applySuggestion', () => {
    it('should apply suggestion and send feedback', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      const result = await inlineAssistanceService.applySuggestion('test-suggestion', 'test-session');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/inline-assistance/apply-suggestion'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('test-suggestion')
        })
      );

      expect(result).toBe(true);
    });

    it('should handle apply errors', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const result = await inlineAssistanceService.applySuggestion('test-suggestion', 'test-session');

      expect(result).toBe(false);
    });
  });

  describe('rejectSuggestion', () => {
    it('should reject suggestion with reason', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      const result = await inlineAssistanceService.rejectSuggestion(
        'test-suggestion', 
        'test-session', 
        'not_helpful'
      );

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/inline-assistance/reject-suggestion'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('not_helpful')
        })
      );

      expect(result).toBe(true);
    });
  });

  describe('static utility methods', () => {
    describe('getCursorPosition', () => {
      it('should get cursor position from Monaco editor', () => {
        const mockEditor = {
          getPosition: () => ({ lineNumber: 5, column: 10 }),
          getModel: () => ({
            getOffsetAt: () => 50
          })
        };

        const result = (inlineAssistanceService.constructor as any).getCursorPosition(mockEditor);

        expect(result).toEqual({
          line: 5,
          column: 9, // 0-based
          position: 50
        });
      });

      it('should handle missing position', () => {
        const mockEditor = {
          getPosition: () => null,
          getModel: () => null
        };

        const result = (inlineAssistanceService.constructor as any).getCursorPosition(mockEditor);

        expect(result).toEqual({
          line: 1,
          column: 0,
          position: 0
        });
      });
    });

    describe('getWordAtPosition', () => {
      it('should get word at cursor position', () => {
        const mockEditor = {
          getPosition: () => ({ lineNumber: 1, column: 5 }),
          getModel: () => ({
            getWordAtPosition: () => ({ word: 'test' })
          })
        };

        const result = (inlineAssistanceService.constructor as any).getWordAtPosition(mockEditor);

        expect(result).toBe('test');
      });

      it('should handle no word at position', () => {
        const mockEditor = {
          getPosition: () => ({ lineNumber: 1, column: 5 }),
          getModel: () => ({
            getWordAtPosition: () => null
          })
        };

        const result = (inlineAssistanceService.constructor as any).getWordAtPosition(mockEditor);

        expect(result).toBe('');
      });
    });

    describe('insertTextAtCursor', () => {
      it('should insert text at cursor position', () => {
        const mockEditor = {
          getPosition: () => ({ lineNumber: 1, column: 5 }),
          executeEdits: jest.fn()
        };

        (inlineAssistanceService.constructor as any).insertTextAtCursor(mockEditor, 'inserted text');

        expect(mockEditor.executeEdits).toHaveBeenCalledWith(
          'inline-assistance',
          [{
            range: {
              startLineNumber: 1,
              startColumn: 5,
              endLineNumber: 1,
              endColumn: 5
            },
            text: 'inserted text'
          }]
        );
      });
    });

    describe('replaceTextRange', () => {
      it('should replace text in range', () => {
        const mockEditor = {
          getModel: () => ({
            getPositionAt: jest.fn()
              .mockReturnValueOnce({ lineNumber: 1, column: 1 })
              .mockReturnValueOnce({ lineNumber: 1, column: 10 })
          }),
          executeEdits: jest.fn()
        };

        (inlineAssistanceService.constructor as any).replaceTextRange(mockEditor, 0, 9, 'replacement');

        expect(mockEditor.executeEdits).toHaveBeenCalledWith(
          'inline-assistance',
          [{
            range: {
              startLineNumber: 1,
              startColumn: 1,
              endLineNumber: 1,
              endColumn: 10
            },
            text: 'replacement'
          }]
        );
      });
    });
  });
});
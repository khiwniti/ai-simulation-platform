/**
 * Tests for the InlineSuggestionWidget component.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { InlineSuggestionWidget } from '../InlineSuggestionWidget';
import { InlineSuggestion } from '../../../services/inlineAssistanceService';

// Mock suggestions for testing
const mockSuggestions: InlineSuggestion[] = [
  {
    id: 'suggestion-1',
    agentId: 'ai-provider-1',
    agentType: 'ai_provider',
    suggestionType: 'completion',
    text: 'Create numpy array',
    insertText: 'np.array([1, 2, 3])',
    confidenceScore: 0.95,
    priority: 1,
    explanation: 'Creates a NumPy array with the specified values',
    metadata: {
      model_used: 'gpt-4',
      processing_time: 120,
      provider: 'openai',
      domain: 'general'
    }
  },
  {
    id: 'suggestion-2',
    agentId: 'physics-agent',
    agentType: 'legacy_physics',
    suggestionType: 'fix',
    text: 'Fix syntax error',
    insertText: 'missing_parenthesis)',
    confidenceScore: 0.88,
    priority: 1,
    explanation: 'Adds missing closing parenthesis',
    documentation: 'Python syntax requires balanced parentheses'
  },
  {
    id: 'suggestion-3',
    agentId: 'optimization-agent',
    agentType: 'legacy_optimization',
    suggestionType: 'optimization',
    text: 'Use list comprehension',
    insertText: '[x**2 for x in range(10)]',
    confidenceScore: 0.72,
    priority: 3,
    explanation: 'More efficient than traditional loop'
  }
];

describe('InlineSuggestionWidget', () => {
  const defaultProps = {
    suggestions: mockSuggestions,
    visible: true,
    position: { top: 100, left: 200 },
    onApplySuggestion: jest.fn(),
    onRejectSuggestion: jest.fn(),
    onHide: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders widget when visible with suggestions', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      expect(screen.getByText('AI Suggestions (3)')).toBeInTheDocument();
      expect(screen.getByText('Create numpy array')).toBeInTheDocument();
      expect(screen.getByText('Fix syntax error')).toBeInTheDocument();
      expect(screen.getByText('Use list comprehension')).toBeInTheDocument();
    });

    test('does not render when not visible', () => {
      render(<InlineSuggestionWidget {...defaultProps} visible={false} />);
      
      expect(screen.queryByText('AI Suggestions')).not.toBeInTheDocument();
    });

    test('does not render when no suggestions', () => {
      render(<InlineSuggestionWidget {...defaultProps} suggestions={[]} />);
      
      expect(screen.queryByText('AI Suggestions')).not.toBeInTheDocument();
    });

    test('displays suggestion metadata correctly', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      expect(screen.getByText('Agent: ai_provider')).toBeInTheDocument();
      expect(screen.getByText('95% confidence')).toBeInTheDocument();
      expect(screen.getByText('Model: gpt-4')).toBeInTheDocument();
      expect(screen.getByText('120ms')).toBeInTheDocument();
    });

    test('displays priority indicators', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      expect(screen.getAllByText('P1')).toHaveLength(2); // Two priority 1 suggestions
      expect(screen.getByText('P3')).toBeInTheDocument();
    });

    test('shows insert text in code blocks', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      expect(screen.getByText('np.array([1, 2, 3])')).toBeInTheDocument();
      expect(screen.getByText('[x**2 for x in range(10)]')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('applies suggestion when Apply button is clicked', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      const applyButton = screen.getAllByText('Apply')[0];
      await user.click(applyButton);
      
      expect(defaultProps.onApplySuggestion).toHaveBeenCalledWith(mockSuggestions[0]);
    });

    test('shows/hides details when More/Less button is clicked', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      const moreButton = screen.getAllByText('More')[0];
      await user.click(moreButton);
      
      expect(screen.getByText('Creates a NumPy array with the specified values')).toBeInTheDocument();
      
      const lessButton = screen.getByText('Less');
      await user.click(lessButton);
      
      expect(screen.queryByText('Creates a NumPy array with the specified values')).not.toBeInTheDocument();
    });

    test('opens reject dialog when X button is clicked', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      const rejectButton = screen.getAllByText('✕')[0];
      await user.click(rejectButton);
      
      expect(screen.getByText('Why reject this suggestion?')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Optional feedback...')).toBeInTheDocument();
    });

    test('rejects suggestion with reason', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Open reject dialog
      const rejectButton = screen.getAllByText('✕')[0];
      await user.click(rejectButton);
      
      // Enter reason
      const textarea = screen.getByPlaceholderText('Optional feedback...');
      await user.type(textarea, 'Not what I needed');
      
      // Confirm rejection
      const confirmButton = screen.getByText('Reject');
      await user.click(confirmButton);
      
      expect(defaultProps.onRejectSuggestion).toHaveBeenCalledWith(
        mockSuggestions[0], 
        'Not what I needed'
      );
    });

    test('cancels rejection', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Open reject dialog
      const rejectButton = screen.getAllByText('✕')[0];
      await user.click(rejectButton);
      
      // Cancel
      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);
      
      expect(screen.queryByText('Why reject this suggestion?')).not.toBeInTheDocument();
      expect(defaultProps.onRejectSuggestion).not.toHaveBeenCalled();
    });

    test('hides widget when close button is clicked', async () => {
      const user = userEvent.setup();
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      const closeButton = screen.getByTitle('Close (Esc)');
      await user.click(closeButton);
      
      expect(defaultProps.onHide).toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    test('navigates suggestions with arrow keys', async () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // First suggestion should be selected by default
      const firstSuggestion = screen.getByText('Create numpy array').closest('div');
      expect(firstSuggestion).toHaveClass('bg-blue-50');
      
      // Navigate down
      fireEvent.keyDown(document, { key: 'ArrowDown' });
      
      await waitFor(() => {
        const secondSuggestion = screen.getByText('Fix syntax error').closest('div');
        expect(secondSuggestion).toHaveClass('bg-blue-50');
      });
      
      // Navigate up
      fireEvent.keyDown(document, { key: 'ArrowUp' });
      
      await waitFor(() => {
        const firstSuggestion = screen.getByText('Create numpy array').closest('div');
        expect(firstSuggestion).toHaveClass('bg-blue-50');
      });
    });

    test('applies suggestion with Enter key', async () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      fireEvent.keyDown(document, { key: 'Enter' });
      
      expect(defaultProps.onApplySuggestion).toHaveBeenCalledWith(mockSuggestions[0]);
    });

    test('hides widget with Escape key', async () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      fireEvent.keyDown(document, { key: 'Escape' });
      
      expect(defaultProps.onHide).toHaveBeenCalled();
    });

    test('applies suggestion with Ctrl+number shortcuts', async () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Ctrl+2 should apply second suggestion
      fireEvent.keyDown(document, { key: '2', ctrlKey: true });
      
      expect(defaultProps.onApplySuggestion).toHaveBeenCalledWith(mockSuggestions[1]);
    });

    test('wraps navigation at boundaries', async () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Navigate to last suggestion
      fireEvent.keyDown(document, { key: 'ArrowUp' });
      
      await waitFor(() => {
        const lastSuggestion = screen.getByText('Use list comprehension').closest('div');
        expect(lastSuggestion).toHaveClass('bg-blue-50');
      });
      
      // Navigate past last (should wrap to first)
      fireEvent.keyDown(document, { key: 'ArrowDown' });
      
      await waitFor(() => {
        const firstSuggestion = screen.getByText('Create numpy array').closest('div');
        expect(firstSuggestion).toHaveClass('bg-blue-50');
      });
    });
  });

  describe('Suggestion Sorting and Limiting', () => {
    test('sorts suggestions by priority and confidence', () => {
      const unsortedSuggestions = [
        { ...mockSuggestions[2], priority: 3, confidenceScore: 0.7 },
        { ...mockSuggestions[0], priority: 1, confidenceScore: 0.95 },
        { ...mockSuggestions[1], priority: 1, confidenceScore: 0.88 }
      ];
      
      render(
        <InlineSuggestionWidget 
          {...defaultProps} 
          suggestions={unsortedSuggestions} 
        />
      );
      
      const suggestionTexts = screen.getAllByText(/Create numpy array|Fix syntax error|Use list comprehension/);
      
      // Should be sorted: highest priority (1) with highest confidence first
      expect(suggestionTexts[0]).toHaveTextContent('Create numpy array');
      expect(suggestionTexts[1]).toHaveTextContent('Fix syntax error');
      expect(suggestionTexts[2]).toHaveTextContent('Use list comprehension');
    });

    test('limits suggestions to maxSuggestions prop', () => {
      const manySuggestions = Array.from({ length: 10 }, (_, i) => ({
        ...mockSuggestions[0],
        id: `suggestion-${i}`,
        text: `Suggestion ${i}`
      }));
      
      render(
        <InlineSuggestionWidget 
          {...defaultProps} 
          suggestions={manySuggestions}
          maxSuggestions={3}
        />
      );
      
      expect(screen.getByText('AI Suggestions (3)')).toBeInTheDocument();
      expect(screen.getByText('Showing top 3')).toBeInTheDocument();
      
      // Should only show 3 suggestions
      const suggestionElements = screen.getAllByText('Apply');
      expect(suggestionElements).toHaveLength(3);
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Widget should be focusable and have role
      const widget = screen.getByText('AI Suggestions (3)').closest('div');
      expect(widget).toBeInTheDocument();
      
      // Buttons should have proper titles
      expect(screen.getByTitle('Close (Esc)')).toBeInTheDocument();
      expect(screen.getByTitle('Apply suggestion (Ctrl+1)')).toBeInTheDocument();
    });

    test('supports keyboard navigation instructions', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      expect(screen.getByText('Use ↑↓ to navigate, Enter to apply, Ctrl+1-9 for quick apply')).toBeInTheDocument();
    });
  });

  describe('Position and Styling', () => {
    test('positions widget correctly', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      const widget = screen.getByText('AI Suggestions (3)').closest('div');
      expect(widget).toHaveStyle({
        position: 'fixed',
        top: '100px',
        left: '200px'
      });
    });

    test('applies confidence-based styling', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // High confidence should be green
      expect(screen.getByText('95% confidence')).toHaveClass('text-green-600');
      
      // Medium confidence should be different color
      expect(screen.getByText('72% confidence')).toHaveClass('text-yellow-600');
    });

    test('shows appropriate icons for suggestion types', () => {
      render(<InlineSuggestionWidget {...defaultProps} />);
      
      // Should have emoji icons for different types
      const suggestions = screen.getAllByText(/💡|🔧|⚡|🤖/);
      expect(suggestions.length).toBeGreaterThan(0);
    });
  });
});

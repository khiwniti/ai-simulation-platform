/**
 * Tests for InlineSuggestionWidget component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { InlineSuggestionWidget } from '../../../components/inline-assistance/InlineSuggestionWidget';
import { InlineSuggestion } from '../../../services/inlineAssistanceService';

const mockSuggestions: InlineSuggestion[] = [
  {
    id: 'suggestion-1',
    agentId: 'physics-agent',
    agentType: 'physics',
    suggestionType: 'completion',
    text: 'Create physics scene',
    insertText: 'scene = physx.create_scene()',
    confidenceScore: 0.9,
    priority: 1,
    explanation: 'Creates a new physics scene for simulation'
  },
  {
    id: 'suggestion-2',
    agentId: 'optimization-agent',
    agentType: 'optimization',
    suggestionType: 'optimization',
    text: 'Optimize performance',
    insertText: 'scene.set_gpu_acceleration(True)',
    confidenceScore: 0.8,
    priority: 2,
    explanation: 'Enables GPU acceleration for better performance'
  }
];

const defaultProps = {
  suggestions: mockSuggestions,
  position: { top: 100, left: 200 },
  onAccept: jest.fn(),
  onReject: jest.fn(),
  onClose: jest.fn(),
  visible: true
};

describe('InlineSuggestionWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render suggestions when visible', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    expect(screen.getByText('AI Suggestions')).toBeInTheDocument();
    expect(screen.getByText('Create physics scene')).toBeInTheDocument();
    expect(screen.getByText('Optimize performance')).toBeInTheDocument();
    expect(screen.getByText('physics')).toBeInTheDocument();
    expect(screen.getByText('optimization')).toBeInTheDocument();
  });

  it('should not render when not visible', () => {
    render(<InlineSuggestionWidget {...defaultProps} visible={false} />);

    expect(screen.queryByText('AI Suggestions')).not.toBeInTheDocument();
  });

  it('should not render when no suggestions', () => {
    render(<InlineSuggestionWidget {...defaultProps} suggestions={[]} />);

    expect(screen.queryByText('AI Suggestions')).not.toBeInTheDocument();
  });

  it('should handle keyboard navigation', async () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const widget = screen.getByText('AI Suggestions').closest('div');
    
    // Arrow down should select next suggestion
    fireEvent.keyDown(document, { key: 'ArrowDown' });
    
    // Arrow up should select previous suggestion
    fireEvent.keyDown(document, { key: 'ArrowUp' });
    
    // Enter should accept selected suggestion
    fireEvent.keyDown(document, { key: 'Enter' });
    
    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('should handle Tab key to accept suggestion', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    fireEvent.keyDown(document, { key: 'Tab' });

    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('should handle Escape key to close', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('should handle mouse click to accept suggestion', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const suggestion = screen.getByText('Create physics scene');
    fireEvent.click(suggestion);

    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('should handle mouse hover to select suggestion', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const suggestion = screen.getByText('Optimize performance');
    fireEvent.mouseEnter(suggestion.closest('div')!);

    // The second suggestion should now be selected
    // We can verify this by checking if Enter would accept the second suggestion
    fireEvent.keyDown(document, { key: 'Enter' });
    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockSuggestions[1]);
  });

  it('should toggle details view', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    // Details should not be visible initially
    expect(screen.queryByText('Creates a new physics scene for simulation')).not.toBeInTheDocument();

    // Click details toggle button
    const detailsButton = screen.getByTitle('Toggle details (Ctrl+I)');
    fireEvent.click(detailsButton);

    // Details should now be visible
    expect(screen.getByText('Creates a new physics scene for simulation')).toBeInTheDocument();
    expect(screen.getByText('scene = physx.create_scene()')).toBeInTheDocument();
  });

  it('should handle Ctrl+I to toggle details', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    fireEvent.keyDown(document, { key: 'i', ctrlKey: true });

    expect(screen.getByText('Creates a new physics scene for simulation')).toBeInTheDocument();
  });

  it('should handle reject button click', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const rejectButton = screen.getByText('Reject');
    fireEvent.click(rejectButton);

    expect(defaultProps.onReject).toHaveBeenCalledWith(mockSuggestions[0], 'not_helpful');
  });

  it('should handle accept button click', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const acceptButton = screen.getByText('Accept');
    fireEvent.click(acceptButton);

    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('should handle close button click', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const closeButton = screen.getByTitle('Close (Esc)');
    fireEvent.click(closeButton);

    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('should display correct priority colors', () => {
    const highPrioritySuggestion = { ...mockSuggestions[0], priority: 1 };
    const mediumPrioritySuggestion = { ...mockSuggestions[1], priority: 2 };
    
    render(
      <InlineSuggestionWidget 
        {...defaultProps} 
        suggestions={[highPrioritySuggestion, mediumPrioritySuggestion]} 
      />
    );

    // First suggestion should have high priority styling (blue)
    const firstSuggestion = screen.getByText('Create physics scene').closest('div');
    expect(firstSuggestion).toHaveClass('border-l-4');
  });

  it('should display correct type icons', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    // Should display appropriate icons for different suggestion types
    const completionIcon = screen.getByText('💡');
    const optimizationIcon = screen.getByText('⚡');
    
    expect(completionIcon).toBeInTheDocument();
    expect(optimizationIcon).toBeInTheDocument();
  });

  it('should show confidence scores in details view', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    // Toggle details
    const detailsButton = screen.getByTitle('Toggle details (Ctrl+I)');
    fireEvent.click(detailsButton);

    expect(screen.getByText('Confidence: 90%')).toBeInTheDocument();
    expect(screen.getByText('Priority: 1')).toBeInTheDocument();
  });

  it('should handle click outside to close', async () => {
    render(
      <div>
        <InlineSuggestionWidget {...defaultProps} />
        <div data-testid="outside">Outside element</div>
      </div>
    );

    const outsideElement = screen.getByTestId('outside');
    fireEvent.mouseDown(outsideElement);

    await waitFor(() => {
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  it('should position widget correctly', () => {
    render(<InlineSuggestionWidget {...defaultProps} />);

    const widget = screen.getByText('AI Suggestions').closest('div');
    expect(widget).toHaveStyle({
      top: '100px',
      left: '200px'
    });
  });
});
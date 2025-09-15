import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChatMessages } from '../../../components/chat/ChatMessages';
import { ChatMessage } from '@ai-jupyter/shared';

describe('ChatMessages', () => {
  const mockMessages: ChatMessage[] = [
    {
      id: 'msg-1',
      sessionId: 'session-1',
      type: 'user',
      content: 'Hello, can you help me with physics?',
      timestamp: new Date('2023-01-01T10:00:00Z')
    },
    {
      id: 'msg-2',
      sessionId: 'session-1',
      type: 'agent',
      content: 'Of course! I can help you with physics simulations.',
      agentId: 'physics-agent',
      agentType: 'physics',
      timestamp: new Date('2023-01-01T10:00:30Z'),
      confidenceScore: 0.95,
      suggestions: ['Try using PhysX for rigid body dynamics'],
      codeSnippets: [
        {
          id: 'snippet-1',
          language: 'python',
          code: 'import physx\nscene = physx.create_scene()',
          description: 'Basic PhysX setup',
          insertable: true
        }
      ]
    }
  ];

  it('renders messages correctly', () => {
    render(<ChatMessages messages={mockMessages} />);
    
    expect(screen.getByText('Hello, can you help me with physics?')).toBeInTheDocument();
    expect(screen.getByText('Of course! I can help you with physics simulations.')).toBeInTheDocument();
  });

  it('displays empty state when no messages', () => {
    render(<ChatMessages messages={[]} />);
    
    expect(screen.getByText('Start a conversation')).toBeInTheDocument();
    expect(screen.getByText('Ask the AI agents for help with your simulation code, physics problems, or visualization needs.')).toBeInTheDocument();
  });

  it('shows example queries in empty state', () => {
    render(<ChatMessages messages={[]} />);
    
    expect(screen.getByText('"Help me set up a physics simulation with PhysX"')).toBeInTheDocument();
    expect(screen.getByText('"How can I optimize my GPU memory usage?"')).toBeInTheDocument();
    expect(screen.getByText('"Create a 3D visualization for my data"')).toBeInTheDocument();
  });

  it('displays typing indicator when typing', () => {
    render(<ChatMessages messages={mockMessages} isTyping={true} />);
    
    expect(screen.getByText('AI agent is thinking...')).toBeInTheDocument();
  });

  it('scrolls to bottom when new messages arrive', () => {
    const scrollIntoViewMock = jest.fn();
    Element.prototype.scrollIntoView = scrollIntoViewMock;
    
    const { rerender } = render(<ChatMessages messages={[mockMessages[0]]} />);
    
    rerender(<ChatMessages messages={mockMessages} />);
    
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' });
  });
});
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentSelector } from '../../../components/chat/AgentSelector';
import { useChatStore } from '../../../stores/chatStore';
import { AgentInfo } from '@ai-jupyter/shared';

jest.mock('../../../stores/chatStore');

const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;

describe('AgentSelector', () => {
  const mockAgents: AgentInfo[] = [
    {
      id: 'physics',
      type: 'physics',
      name: 'Physics Agent',
      description: 'Specialized in NVIDIA PhysX AI and physics simulations',
      capabilities: ['physics_modeling', 'simulation_setup'],
      isActive: false,
      isAvailable: true
    },
    {
      id: 'visualization',
      type: 'visualization',
      name: 'Visualization Agent',
      description: 'Expert in 3D graphics and data visualization',
      capabilities: ['3d_rendering', 'data_visualization'],
      isActive: false,
      isAvailable: true
    }
  ];

  const mockStoreActions = {
    toggleAgentSelection: jest.fn(),
    setSelectedAgents: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseChatStore.mockReturnValue(mockStoreActions as any);
  });

  it('renders available agents', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={[]}
      />
    );
    
    expect(screen.getByText('Physics Agent')).toBeInTheDocument();
    expect(screen.getByText('Visualization Agent')).toBeInTheDocument();
    expect(screen.getByText('Specialized in NVIDIA PhysX AI and physics simulations')).toBeInTheDocument();
  });

  it('shows agent capabilities', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={[]}
      />
    );
    
    expect(screen.getByText('physics modeling')).toBeInTheDocument();
    expect(screen.getByText('simulation setup')).toBeInTheDocument();
    expect(screen.getByText('3d rendering')).toBeInTheDocument();
  });

  it('handles agent selection', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={[]}
      />
    );
    
    fireEvent.click(screen.getByText('Physics Agent'));
    
    expect(mockStoreActions.toggleAgentSelection).toHaveBeenCalledWith('physics');
  });

  it('shows selected agents with different styling', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={['physics']}
      />
    );
    
    const physicsAgent = screen.getByText('Physics Agent').closest('.agent-item');
    expect(physicsAgent).toHaveClass('selected');
  });

  it('handles select all button', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={[]}
      />
    );
    
    fireEvent.click(screen.getByText('All'));
    
    expect(mockStoreActions.setSelectedAgents).toHaveBeenCalledWith(['physics', 'visualization']);
  });

  it('handles select none button', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={['physics', 'visualization']}
      />
    );
    
    fireEvent.click(screen.getByText('None'));
    
    expect(mockStoreActions.setSelectedAgents).toHaveBeenCalledWith([]);
  });

  it('shows selection summary', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={['physics', 'visualization']}
      />
    );
    
    expect(screen.getByText('2 agents selected')).toBeInTheDocument();
    expect(screen.getByText('Multiple agents will coordinate to answer your questions')).toBeInTheDocument();
  });

  it('disables interactions when disabled prop is true', () => {
    render(
      <AgentSelector
        availableAgents={mockAgents}
        selectedAgents={[]}
        disabled={true}
      />
    );
    
    const physicsAgent = screen.getByText('Physics Agent').closest('.agent-item');
    expect(physicsAgent).toHaveClass('disabled');
    
    fireEvent.click(screen.getByText('Physics Agent'));
    expect(mockStoreActions.toggleAgentSelection).not.toHaveBeenCalled();
  });
});
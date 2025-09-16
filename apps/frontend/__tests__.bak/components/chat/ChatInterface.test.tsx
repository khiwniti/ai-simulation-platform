import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInterface } from '../../../components/chat/ChatInterface';
import { useChatStore } from '../../../stores/chatStore';
import { useWorkbookStore } from '../../../stores/workbookStore';
import { chatWebSocketService } from '../../../services/chatWebSocketService';
import { chatApiService } from '../../../services/chatApiService';

// Mock the stores
jest.mock('../../../stores/chatStore');
jest.mock('../../../stores/workbookStore');
jest.mock('../../../services/chatWebSocketService');
jest.mock('../../../services/chatApiService');

const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;
const mockUseWorkbookStore = useWorkbookStore as jest.MockedFunction<typeof useWorkbookStore>;
const mockChatWebSocketService = chatWebSocketService as jest.Mocked<typeof chatWebSocketService>;
const mockChatApiService = chatApiService as jest.Mocked<typeof chatApiService>;

describe('ChatInterface', () => {
  const mockChatState = {
    isOpen: true,
    currentSession: null,
    isConnected: false,
    error: null,
    selectedAgents: [],
    availableAgents: [],
    closeChat: jest.fn(),
    setCurrentSession: jest.fn(),
    setConnectionStatus: jest.fn(),
    setError: jest.fn(),
    addMessage: jest.fn(),
    setAvailableAgents: jest.fn()
  };

  const mockWorkbookState = {
    selectedNotebook: {
      id: 'notebook-1',
      title: 'Test Notebook',
      workbookId: 'workbook-1'
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockUseChatStore.mockReturnValue(mockChatState as any);
    mockUseWorkbookStore.mockReturnValue(mockWorkbookState as any);
    
    mockChatApiService.createChatSession.mockResolvedValue({
      id: 'session-1',
      context: {}
    } as any);
    
    mockChatApiService.getAvailableAgents.mockResolvedValue([
      {
        id: 'physics',
        type: 'physics',
        name: 'Physics Agent',
        description: 'Physics simulation expert',
        capabilities: ['physics_modeling'],
        isActive: false,
        isAvailable: true
      }
    ]);
    
    mockChatWebSocketService.connect.mockResolvedValue();
    mockChatWebSocketService.isConnected = false;
  });

  it('renders chat interface when open', () => {
    render(<ChatInterface />);
    
    expect(screen.getByText('AI Agents Chat')).toBeInTheDocument();
    expect(screen.getByText('Select AI Agents')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    mockUseChatStore.mockReturnValue({
      ...mockChatState,
      isOpen: false
    } as any);
    
    const { container } = render(<ChatInterface />);
    expect(container.firstChild).toBeNull();
  });

  it('initializes chat session when opened', async () => {
    render(<ChatInterface />);
    
    await waitFor(() => {
      expect(mockChatApiService.createChatSession).toHaveBeenCalledWith(
        expect.any(String),
        'notebook-1',
        expect.objectContaining({
          notebookTitle: 'Test Notebook',
          workbookId: 'workbook-1'
        })
      );
    });
    
    expect(mockChatWebSocketService.connect).toHaveBeenCalled();
  });

  it('displays error message when present', () => {
    mockUseChatStore.mockReturnValue({
      ...mockChatState,
      error: 'Connection failed'
    } as any);
    
    render(<ChatInterface />);
    
    expect(screen.getByText('Connection failed')).toBeInTheDocument();
  });

  it('loads available agents on mount', async () => {
    render(<ChatInterface />);
    
    await waitFor(() => {
      expect(mockChatApiService.getAvailableAgents).toHaveBeenCalled();
      expect(mockChatState.setAvailableAgents).toHaveBeenCalledWith([
        expect.objectContaining({
          id: 'physics',
          name: 'Physics Agent'
        })
      ]);
    });
  });

  it('handles WebSocket connection events', async () => {
    render(<ChatInterface />);
    
    await waitFor(() => {
      expect(mockChatWebSocketService.onConnect).toHaveBeenCalled();
      expect(mockChatWebSocketService.onDisconnect).toHaveBeenCalled();
      expect(mockChatWebSocketService.onError).toHaveBeenCalled();
    });
  });

  it('cleans up on unmount', () => {
    const { unmount } = render(<ChatInterface />);
    
    mockChatWebSocketService.isConnected = true;
    unmount();
    
    expect(mockChatWebSocketService.disconnect).toHaveBeenCalled();
  });
});
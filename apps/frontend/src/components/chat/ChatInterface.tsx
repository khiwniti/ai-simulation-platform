'use client';

import React, { useEffect, useState } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { useWorkbookStore } from '../../stores/workbookStore';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { AgentSelector } from './AgentSelector';
import { chatWebSocketService } from '../../services/chatWebSocketService';
import { chatApiService } from '../../services/chatApiService';
import { MessageType, ChatMessage } from '@ai-jupyter/shared';
import { v4 as uuidv4 } from 'uuid';

interface ChatInterfaceProps {
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const {
    isOpen,
    currentSession,
    isConnected,
    error,
    selectedAgents,
    availableAgents,
    closeChat,
    setCurrentSession,
    setConnectionStatus,
    setError,
    addMessage,
    setAvailableAgents
  } = useChatStore();

  const { selectedNotebook } = useWorkbookStore();
  const [isInitializing, setIsInitializing] = useState(false);

  useEffect(() => {
    if (isOpen && !currentSession) {
      initializeChatSession();
    }
  }, [isOpen, selectedNotebook]);

  useEffect(() => {
    if (isOpen) {
      setupWebSocketHandlers();
      loadAvailableAgents();
    }

    return () => {
      if (chatWebSocketService.isConnected) {
        chatWebSocketService.disconnect();
      }
    };
  }, [isOpen]);

  const initializeChatSession = async () => {
    if (isInitializing) return;
    
    setIsInitializing(true);
    setError(null);

    try {
      const sessionId = uuidv4();
      
      // Create session via API
      const session = await chatApiService.createChatSession(
        sessionId,
        selectedNotebook?.id,
        {
          notebookTitle: selectedNotebook?.title,
          workbookId: selectedNotebook?.workbookId
        }
      );

      setCurrentSession({
        id: sessionId,
        notebookId: selectedNotebook?.id,
        activeAgents: [],
        messages: [],
        context: session.context || {},
        createdAt: new Date(),
        updatedAt: new Date()
      });

      // Connect WebSocket
      await chatWebSocketService.connect(sessionId);
      setConnectionStatus(true);

    } catch (error) {
      console.error('Failed to initialize chat session:', error);
      setError(error instanceof Error ? error.message : 'Failed to initialize chat');
    } finally {
      setIsInitializing(false);
    }
  };

  const setupWebSocketHandlers = () => {
    chatWebSocketService.onConnect(() => {
      setConnectionStatus(true);
      setError(null);
    });

    chatWebSocketService.onDisconnect(() => {
      setConnectionStatus(false);
    });

    chatWebSocketService.onError((error) => {
      setError('Connection error occurred');
      setConnectionStatus(false);
    });

    // Handle incoming agent responses
    chatWebSocketService.onMessage(MessageType.AGENT_RESPONSE, (payload) => {
      const message: ChatMessage = {
        id: uuidv4(),
        sessionId: currentSession?.id || '',
        type: 'agent',
        content: payload.response,
        agentId: payload.agent_id,
        agentType: payload.agent_type,
        timestamp: new Date(),
        codeSnippets: payload.code_snippets || [],
        suggestions: payload.suggestions || [],
        confidenceScore: payload.confidence_score,
        metadata: {
          responseTime: payload.response_time,
          capabilitiesUsed: payload.capabilities_used
        }
      };
      
      addMessage(message);
    });

    // Handle coordination responses
    chatWebSocketService.onMessage(MessageType.AGENT_COORDINATION, (payload) => {
      const primaryMessage: ChatMessage = {
        id: uuidv4(),
        sessionId: currentSession?.id || '',
        type: 'agent',
        content: payload.primary_response.response,
        agentId: payload.primary_response.agent_id,
        agentType: payload.primary_response.agent_type,
        timestamp: new Date(),
        codeSnippets: payload.primary_response.code_snippets || [],
        suggestions: payload.primary_response.suggestions || [],
        confidenceScore: payload.primary_response.confidence_score,
        metadata: {
          coordinationType: 'primary',
          consensusScore: payload.consensus_score,
          coordinationTime: payload.coordination_time,
          supportingAgents: payload.supporting_responses?.map((r: any) => r.agent_id) || []
        }
      };
      
      addMessage(primaryMessage);

      // Add supporting responses if any
      payload.supporting_responses?.forEach((response: any) => {
        const supportingMessage: ChatMessage = {
          id: uuidv4(),
          sessionId: currentSession?.id || '',
          type: 'agent',
          content: response.response,
          agentId: response.agent_id,
          agentType: response.agent_type,
          timestamp: new Date(),
          codeSnippets: response.code_snippets || [],
          suggestions: response.suggestions || [],
          confidenceScore: response.confidence_score,
          metadata: {
            coordinationType: 'supporting'
          }
        };
        
        addMessage(supportingMessage);
      });
    });

    // Handle system messages
    chatWebSocketService.onMessage(MessageType.SYSTEM_MESSAGE, (payload) => {
      const message: ChatMessage = {
        id: uuidv4(),
        sessionId: currentSession?.id || '',
        type: 'system',
        content: payload.message,
        timestamp: new Date(),
        metadata: payload.metadata
      };
      
      addMessage(message);
    });

    // Handle errors
    chatWebSocketService.onMessage(MessageType.ERROR, (payload) => {
      setError(payload.message || 'An error occurred');
    });
  };

  const loadAvailableAgents = async () => {
    try {
      const agents = await chatApiService.getAvailableAgents();
      setAvailableAgents(agents);
    } catch (error) {
      console.error('Failed to load available agents:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!currentSession || !content.trim()) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: uuidv4(),
      sessionId: currentSession.id,
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
    
    addMessage(userMessage);

    // Send message via WebSocket
    if (selectedAgents.length > 1) {
      // Multi-agent coordination
      chatWebSocketService.requestAgentCoordination(content.trim());
    } else {
      // Single agent or general query
      chatWebSocketService.sendUserMessage(content.trim(), selectedAgents);
    }
  };

  const handleCloseChat = async () => {
    if (currentSession) {
      try {
        await chatApiService.endChatSession(currentSession.id);
      } catch (error) {
        console.error('Failed to end chat session:', error);
      }
    }
    
    chatWebSocketService.disconnect();
    setCurrentSession(null);
    setConnectionStatus(false);
    closeChat();
  };

  if (!isOpen) return null;

  return (
    <div className={`chat-interface ${className}`}>
      <div className="chat-container">
        <ChatHeader
          isConnected={isConnected}
          isInitializing={isInitializing}
          onClose={handleCloseChat}
          sessionId={currentSession?.id}
        />
        
        {error && (
          <div className="chat-error">
            <span className="error-icon">⚠️</span>
            <span className="error-message">{error}</span>
          </div>
        )}
        
        <AgentSelector
          availableAgents={availableAgents}
          selectedAgents={selectedAgents}
          disabled={!isConnected || isInitializing}
        />
        
        <ChatMessages
          messages={currentSession?.messages || []}
          isTyping={false} // Will be implemented with typing indicators
        />
        
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected || isInitializing}
          placeholder={
            isInitializing 
              ? "Initializing chat..." 
              : !isConnected 
                ? "Connecting..." 
                : "Ask the AI agents for help..."
          }
        />
      </div>
    </div>
  );
};
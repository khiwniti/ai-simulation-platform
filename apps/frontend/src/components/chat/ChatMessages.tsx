'use client';

import React, { useEffect, useRef } from 'react';
import { ChatMessage } from '@ai-jupyter/shared';
import { ChatMessageItem } from './ChatMessageItem';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isTyping?: boolean;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isTyping = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="chat-messages">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-messages">
            <div className="empty-icon">💬</div>
            <h4>Start a conversation</h4>
            <p>Ask the AI agents for help with your simulation code, physics problems, or visualization needs.</p>
            <div className="example-queries">
              <div className="example-query">
                "Help me set up a physics simulation with PhysX"
              </div>
              <div className="example-query">
                "How can I optimize my GPU memory usage?"
              </div>
              <div className="example-query">
                "Create a 3D visualization for my data"
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessageItem
              key={message.id}
              message={message}
            />
          ))
        )}
        
        {isTyping && (
          <div className="typing-indicator">
            <div className="typing-avatar">🤖</div>
            <div className="typing-content">
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="typing-text">AI agent is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
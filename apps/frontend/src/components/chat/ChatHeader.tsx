'use client';

import React from 'react';

interface ChatHeaderProps {
  isConnected: boolean;
  isInitializing: boolean;
  onClose: () => void;
  sessionId?: string;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  isConnected,
  isInitializing,
  onClose,
  sessionId
}) => {
  const getStatusIndicator = () => {
    if (isInitializing) {
      return (
        <div className="status-indicator initializing">
          <div className="spinner"></div>
          <span>Initializing...</span>
        </div>
      );
    }
    
    if (isConnected) {
      return (
        <div className="status-indicator connected">
          <div className="status-dot connected"></div>
          <span>Connected</span>
        </div>
      );
    }
    
    return (
      <div className="status-indicator disconnected">
        <div className="status-dot disconnected"></div>
        <span>Disconnected</span>
      </div>
    );
  };

  return (
    <div className="chat-header">
      <div className="chat-title">
        <h3>AI Agents Chat</h3>
        {sessionId && (
          <span className="session-id">Session: {sessionId.slice(0, 8)}...</span>
        )}
      </div>
      
      <div className="chat-controls">
        {getStatusIndicator()}
        
        <button
          className="close-button"
          onClick={onClose}
          title="Close chat"
        >
          ✕
        </button>
      </div>
    </div>
  );
};
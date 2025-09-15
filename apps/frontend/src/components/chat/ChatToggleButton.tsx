'use client';

import React from 'react';
import { useChatStore } from '../../stores/chatStore';

export const ChatToggleButton: React.FC = () => {
  const { isOpen, openChat, closeChat } = useChatStore();

  const handleToggle = () => {
    if (isOpen) {
      closeChat();
    } else {
      openChat();
    }
  };

  return (
    <button
      className={`chat-toggle-button ${isOpen ? 'active' : ''}`}
      onClick={handleToggle}
      title={isOpen ? 'Close AI Chat' : 'Open AI Chat'}
    >
      <div className="chat-icon">
        {isOpen ? (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
          </svg>
        )}
      </div>
      
      <span className="chat-label">
        {isOpen ? 'Close Chat' : 'AI Chat'}
      </span>
    </button>
  );
};
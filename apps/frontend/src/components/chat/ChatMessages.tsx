'use client';

import React, { useState, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatMessagesProps {
  className?: string;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({ className = '' }) => {
  const [messages] = useState<Message[]>([]);
  const [isLoading] = useState(false);

  return (
    <div className={`chat-messages flex-1 overflow-y-auto p-4 space-y-4 ${className}`}>
      {messages.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <div className="text-4xl mb-4">🤖</div>
          <p className="text-sm">Start a conversation with the AI assistant</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <span className="text-xs opacity-75">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))
      )}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
              <span className="text-sm">AI is thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
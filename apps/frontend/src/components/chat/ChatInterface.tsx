'use client';

import React, { useState } from 'react';

interface ChatInterfaceProps {
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  className = '' 
}) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className={`chat-interface ${className}`}>
      {!isVisible ? (
        <button
          onClick={() => setIsVisible(true)}
          className="fixed bottom-4 right-4 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        >
          <span className="text-xl">💬</span>
        </button>
      ) : (
        <div className="fixed bottom-4 right-4 w-80 h-96 bg-white border border-gray-200 rounded-lg shadow-lg flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">AI Assistant</h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <div className="flex-1 p-4 text-center">
            <div className="text-gray-400 mb-4">
              <span className="text-4xl">🤖</span>
            </div>
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              AI Chat Coming Soon
            </h3>
            <p className="text-sm text-gray-500">
              AI-powered assistance will be available in the next phase.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
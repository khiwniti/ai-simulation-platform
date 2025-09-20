'use client';

import React, { useState } from 'react';

interface CodeSnippet {
  id: string;
  language: string;
  code: string;
  description?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  codeSnippets?: CodeSnippet[];
}

interface ChatMessageItemProps {
  message: Message;
  className?: string;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ 
  message, 
  className = '' 
}) => {
  const [expandedSnippets, setExpandedSnippets] = useState<Set<string>>(new Set());

  const isUser = message.role === 'user';

  const handleInsertCode = (snippet: CodeSnippet) => {
    // This would typically insert code into the current notebook cell
    console.log('Inserting code snippet:', snippet.code);
  };

  const toggleSnippetExpansion = (snippetId: string) => {
    setExpandedSnippets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(snippetId)) {
        newSet.delete(snippetId);
      } else {
        newSet.add(snippetId);
      }
      return newSet;
    });
  };

  return (
    <div className={`chat-message-item flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 ${className}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 text-gray-800'
      }`}>
        <div className="message-content">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          
          {message.codeSnippets && message.codeSnippets.length > 0 && (
            <div className="code-snippets mt-3 space-y-2">
              {message.codeSnippets.map((snippet) => (
                <div key={snippet.id} className="code-snippet bg-gray-800 rounded p-2">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-300">{snippet.language}</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => toggleSnippetExpansion(snippet.id)}
                        className="text-xs text-blue-300 hover:text-blue-200"
                      >
                        {expandedSnippets.has(snippet.id) ? 'Collapse' : 'Expand'}
                      </button>
                      <button
                        onClick={() => handleInsertCode(snippet)}
                        className="text-xs text-green-300 hover:text-green-200"
                      >
                        Insert
                      </button>
                    </div>
                  </div>
                  
                  {snippet.description && (
                    <p className="text-xs text-gray-400 mb-2">{snippet.description}</p>
                  )}
                  
                  <pre className={`text-xs text-gray-100 overflow-x-auto ${
                    expandedSnippets.has(snippet.id) ? '' : 'max-h-20 overflow-hidden'
                  }`}>
                    <code>{snippet.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="message-timestamp mt-2">
          <span className="text-xs opacity-75">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};
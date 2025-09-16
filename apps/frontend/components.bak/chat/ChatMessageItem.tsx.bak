'use client';

import React, { useState } from 'react';
import { ChatMessage, CodeSnippet } from '@ai-jupyter/shared';
import { useChatStore } from '../../stores/chatStore';

interface ChatMessageItemProps {
  message: ChatMessage;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message }) => {
  const { insertCodeSnippet } = useChatStore();
  const [expandedSnippets, setExpandedSnippets] = useState<Set<string>>(new Set());

  const getMessageAvatar = () => {
    if (message.type === 'user') {
      return '👤';
    } else if (message.type === 'system') {
      return '⚙️';
    } else {
      // Agent message
      const agentIcons: Record<string, string> = {
        physics: '⚛️',
        visualization: '📊',
        optimization: '⚡',
        debug: '🔧'
      };
      return agentIcons[message.agentType || ''] || '🤖';
    }
  };

  const getMessageSender = () => {
    if (message.type === 'user') {
      return 'You';
    } else if (message.type === 'system') {
      return 'System';
    } else {
      return message.agentId || 'AI Agent';
    }
  };

  const handleInsertCode = (snippet: CodeSnippet) => {
    insertCodeSnippet(snippet);
  };

  const toggleSnippetExpansion = (snippetId: string) => {
    const newExpanded = new Set(expandedSnippets);
    if (newExpanded.has(snippetId)) {
      newExpanded.delete(snippetId);
    } else {
      newExpanded.add(snippetId);
    }
    setExpandedSnippets(newExpanded);
  };

  const formatTimestamp = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(timestamp));
  };

  const renderCodeSnippets = () => {
    if (!message.codeSnippets || message.codeSnippets.length === 0) {
      return null;
    }

    return (
      <div className="code-snippets">
        <h5>Code Suggestions:</h5>
        {message.codeSnippets.map((snippet) => {
          const isExpanded = expandedSnippets.has(snippet.id);
          const previewLines = snippet.code.split('\n').slice(0, 3);
          const hasMoreLines = snippet.code.split('\n').length > 3;

          return (
            <div key={snippet.id} className="code-snippet">
              <div className="snippet-header">
                <span className="snippet-language">{snippet.language}</span>
                {snippet.description && (
                  <span className="snippet-description">{snippet.description}</span>
                )}
                {snippet.insertable && (
                  <button
                    className="insert-button"
                    onClick={() => handleInsertCode(snippet)}
                    title="Insert into notebook"
                  >
                    Insert
                  </button>
                )}
              </div>
              
              <div className="snippet-code">
                <pre>
                  <code>
                    {isExpanded ? snippet.code : previewLines.join('\n')}
                    {!isExpanded && hasMoreLines && '\n...'}
                  </code>
                </pre>
                
                {hasMoreLines && (
                  <button
                    className="expand-button"
                    onClick={() => toggleSnippetExpansion(snippet.id)}
                  >
                    {isExpanded ? 'Show Less' : 'Show More'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderSuggestions = () => {
    if (!message.suggestions || message.suggestions.length === 0) {
      return null;
    }

    return (
      <div className="suggestions">
        <h5>Suggestions:</h5>
        <ul>
          {message.suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    );
  };

  const renderMetadata = () => {
    if (!message.metadata || message.type === 'user') {
      return null;
    }

    return (
      <div className="message-metadata">
        {message.confidenceScore && (
          <span className="confidence-score">
            Confidence: {Math.round(message.confidenceScore * 100)}%
          </span>
        )}
        
        {message.metadata.responseTime && (
          <span className="response-time">
            Response time: {message.metadata.responseTime.toFixed(2)}s
          </span>
        )}
        
        {message.metadata.coordinationType && (
          <span className={`coordination-type ${message.metadata.coordinationType}`}>
            {message.metadata.coordinationType === 'primary' ? 'Primary Response' : 'Supporting Response'}
          </span>
        )}
        
        {message.metadata.consensusScore && (
          <span className="consensus-score">
            Consensus: {Math.round(message.metadata.consensusScore * 100)}%
          </span>
        )}
      </div>
    );
  };

  return (
    <div className={`chat-message ${message.type}`}>
      <div className="message-avatar">
        {getMessageAvatar()}
      </div>
      
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">{getMessageSender()}</span>
          <span className="message-timestamp">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>
        
        <div className="message-text">
          {message.content}
        </div>
        
        {renderCodeSnippets()}
        {renderSuggestions()}
        {renderMetadata()}
      </div>
    </div>
  );
};
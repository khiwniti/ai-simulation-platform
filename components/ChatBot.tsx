import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Bot, User, Code, Play, Lightbulb } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'code' | 'suggestion';
  codeBlock?: string;
  cellId?: string;
}

interface ChatBotProps {
  isOpen: boolean;
  onClose: () => void;
  onCodeInsert: (code: string, cellType: 'code' | 'physics') => void;
  currentNotebook?: any;
  notebookState?: any;
}

const ChatBot: React.FC<ChatBotProps> = ({ 
  isOpen, 
  onClose, 
  onCodeInsert, 
  currentNotebook, 
  notebookState 
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "👋 Hi! I'm your AI simulation assistant. I can help you:\n\n• Write Python code for engineering analysis\n• Create 3D visualizations and plots\n• Debug simulation errors\n• Suggest optimization improvements\n• Explain physics concepts\n\nWhat would you like to work on?",
      role: 'assistant',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to AI agent with context
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          notebookContext: {
            cells: currentNotebook?.cells || [],
            currentState: notebookState,
            lastExecution: currentNotebook?.lastExecution
          },
          conversationHistory: messages.slice(-5) // Last 5 messages for context
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          role: 'assistant',
          timestamp: new Date(),
          type: data.type || 'text',
          codeBlock: data.codeBlock,
          cellId: data.cellId
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Failed to get AI response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please try again or check your connection.",
        role: 'assistant',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeInsert = (code: string, cellType: 'code' | 'physics' = 'code') => {
    onCodeInsert(code, cellType);
    // Add confirmation message
    const confirmMessage: Message = {
      id: Date.now().toString(),
      content: `✅ Code inserted into ${cellType} cell. You can now run it in your notebook!`,
      role: 'assistant',
      timestamp: new Date(),
      type: 'text'
    };
    setMessages(prev => [...prev, confirmMessage]);
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500 ml-2' : 'bg-green-500 mr-2'
          }`}>
            {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
          </div>
          
          <div className={`px-4 py-2 rounded-lg ${
            isUser 
              ? 'bg-blue-500 text-white rounded-br-none' 
              : 'bg-gray-100 text-gray-800 rounded-bl-none'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {message.codeBlock && (
              <div className="mt-3 p-3 bg-gray-900 rounded text-green-400 text-sm font-mono overflow-x-auto">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Suggested Code:</span>
                  <button
                    onClick={() => handleCodeInsert(message.codeBlock!)}
                    className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 flex items-center"
                  >
                    <Code size={12} className="mr-1" />
                    Insert
                  </button>
                </div>
                <pre className="whitespace-pre-wrap">{message.codeBlock}</pre>
              </div>
            )}
            
            <div className="text-xs opacity-70 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const quickActions = [
    {
      icon: <Code size={16} />,
      text: "Help me write a Python simulation",
      action: () => setInputMessage("Help me write a Python simulation for ")
    },
    {
      icon: <Play size={16} />,
      text: "Debug my current code",
      action: () => setInputMessage("I'm having trouble with my current code. Can you help debug it?")
    },
    {
      icon: <Lightbulb size={16} />,
      text: "Suggest improvements",
      action: () => setInputMessage("Can you suggest improvements for my simulation?")
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center">
            <Bot className="text-green-500 mr-2" size={24} />
            <h2 className="text-lg font-semibold text-gray-800">AI Simulation Assistant</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex max-w-[80%]">
                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-green-500 mr-2">
                  <Bot size={16} className="text-white" />
                </div>
                <div className="px-4 py-2 rounded-lg bg-gray-100 text-gray-800 rounded-bl-none">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="px-4 py-2 border-t border-gray-100">
            <p className="text-sm text-gray-600 mb-2">Quick actions:</p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.action}
                  className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  {action.icon}
                  <span className="ml-1">{action.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything about simulations, code, or physics..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
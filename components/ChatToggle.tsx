import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import ChatBot from './ChatBot';

interface ChatToggleProps {
  onCodeInsert?: (code: string, cellType: 'code' | 'physics') => void;
  currentNotebook?: any;
  notebookState?: any;
}

const ChatToggle: React.FC<ChatToggleProps> = ({ 
  onCodeInsert, 
  currentNotebook, 
  notebookState 
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const handleCodeInsert = (code: string, cellType: 'code' | 'physics' = 'code') => {
    if (onCodeInsert) {
      onCodeInsert(code, cellType);
    } else {
      // Fallback: try to add to notebook directly
      const event = new CustomEvent('addNotebookCell', {
        detail: { code, cellType }
      });
      window.dispatchEvent(event);
    }
  };

  return (
    <>
      {/* Floating Chat Toggle Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsChatOpen(true)}
          className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 
                     text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all duration-300 
                     transform hover:scale-110 group"
          title="AI Assistant"
        >
          <MessageCircle size={24} className="group-hover:rotate-12 transition-transform duration-300" />
          
          {/* Notification Badge */}
          <div className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-3 h-3 
                          flex items-center justify-center text-xs animate-pulse">
            !
          </div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-800 text-white text-sm 
                          rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 
                          whitespace-nowrap">
            AI Simulation Assistant
          </div>
        </button>
        
        {/* Pulsing Ring Animation */}
        <div className="absolute inset-0 bg-blue-400 rounded-full animate-ping opacity-20"></div>
      </div>

      {/* Chat Bot Modal */}
      {isChatOpen && (
        <ChatBot
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
          onCodeInsert={handleCodeInsert}
          currentNotebook={currentNotebook}
          notebookState={notebookState}
        />
      )}
    </>
  );
};

export default ChatToggle;
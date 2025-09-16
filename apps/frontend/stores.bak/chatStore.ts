import { create } from 'zustand';
import { 
  ChatState, 
  ChatSession, 
  ChatMessage, 
  AgentInfo, 
  CodeSnippet 
} from '@ai-jupyter/shared';

interface ChatStore extends ChatState {
  // Actions
  openChat: () => void;
  closeChat: () => void;
  setCurrentSession: (session: ChatSession | null) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  setAvailableAgents: (agents: AgentInfo[]) => void;
  toggleAgentSelection: (agentId: string) => void;
  setSelectedAgents: (agentIds: string[]) => void;
  setConnectionStatus: (isConnected: boolean) => void;
  setTypingStatus: (isTyping: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
  insertCodeSnippet: (snippet: CodeSnippet) => void;
  updateContext: (context: Record<string, any>) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // Initial state
  isOpen: false,
  currentSession: null,
  availableAgents: [],
  selectedAgents: [],
  isConnected: false,
  isTyping: false,
  error: null,

  // Actions
  openChat: () => set({ isOpen: true }),
  
  closeChat: () => set({ isOpen: false }),
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  addMessage: (message) => set((state) => {
    if (!state.currentSession) return state;
    
    return {
      currentSession: {
        ...state.currentSession,
        messages: [...state.currentSession.messages, message],
        updatedAt: new Date()
      }
    };
  }),
  
  updateMessage: (messageId, updates) => set((state) => {
    if (!state.currentSession) return state;
    
    return {
      currentSession: {
        ...state.currentSession,
        messages: state.currentSession.messages.map(msg =>
          msg.id === messageId ? { ...msg, ...updates } : msg
        ),
        updatedAt: new Date()
      }
    };
  }),
  
  setAvailableAgents: (agents) => set({ availableAgents: agents }),
  
  toggleAgentSelection: (agentId) => set((state) => {
    const isSelected = state.selectedAgents.includes(agentId);
    return {
      selectedAgents: isSelected
        ? state.selectedAgents.filter(id => id !== agentId)
        : [...state.selectedAgents, agentId]
    };
  }),
  
  setSelectedAgents: (agentIds) => set({ selectedAgents: agentIds }),
  
  setConnectionStatus: (isConnected) => set({ isConnected }),
  
  setTypingStatus: (isTyping) => set({ isTyping }),
  
  setError: (error) => set({ error }),
  
  clearMessages: () => set((state) => {
    if (!state.currentSession) return state;
    
    return {
      currentSession: {
        ...state.currentSession,
        messages: [],
        updatedAt: new Date()
      }
    };
  }),
  
  insertCodeSnippet: (snippet) => {
    // This will be handled by the notebook editor
    // For now, we'll emit a custom event that the notebook can listen to
    const event = new CustomEvent('insertCodeSnippet', { 
      detail: snippet 
    });
    window.dispatchEvent(event);
  },
  
  updateContext: (context) => set((state) => {
    if (!state.currentSession) return state;
    
    return {
      currentSession: {
        ...state.currentSession,
        context: { ...state.currentSession.context, ...context },
        updatedAt: new Date()
      }
    };
  })
}));
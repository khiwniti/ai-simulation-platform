'use client';

import { create } from 'zustand';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentAgent: string;
  selectedAgents: string[];
  isOpen: boolean;
}

interface ChatActions {
  addMessage: (message: Omit<Message, 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setCurrentAgent: (agent: string) => void;
  setSelectedAgents: (agents: string[]) => void;
  toggleAgentSelection: (agentId: string) => void;
  insertCodeSnippet: (code: string) => void;
  openChat: () => void;
  closeChat: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState & ChatActions>((set) => ({
  messages: [],
  isLoading: false,
  currentAgent: 'general',
  selectedAgents: [],
  isOpen: false,
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, { ...message, timestamp: new Date() }],
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  setSelectedAgents: (agents) => set({ selectedAgents: agents }),
  toggleAgentSelection: (agentId) =>
    set((state) => ({
      selectedAgents: state.selectedAgents.includes(agentId)
        ? state.selectedAgents.filter((id) => id !== agentId)
        : [...state.selectedAgents, agentId],
    })),
  insertCodeSnippet: (code) => {
    // This would typically insert code into the current notebook cell
    console.log('Inserting code snippet:', code);
  },
  openChat: () => set({ isOpen: true }),
  closeChat: () => set({ isOpen: false }),
  clearMessages: () => set({ messages: [] }),
}));
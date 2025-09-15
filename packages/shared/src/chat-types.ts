export interface ChatMessage {
  id: string;
  sessionId: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  agentId?: string;
  agentType?: string;
  timestamp: Date;
  metadata?: Record<string, any>;
  codeSnippets?: CodeSnippet[];
  suggestions?: string[];
  confidenceScore?: number;
}

export interface CodeSnippet {
  id: string;
  language: string;
  code: string;
  description?: string;
  insertable: boolean;
}

export interface ChatSession {
  id: string;
  notebookId?: string;
  activeAgents: string[];
  messages: ChatMessage[];
  context: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface AgentInfo {
  id: string;
  type: string;
  name: string;
  description: string;
  capabilities: string[];
  isActive: boolean;
  isAvailable: boolean;
}

export interface ChatState {
  isOpen: boolean;
  currentSession: ChatSession | null;
  availableAgents: AgentInfo[];
  selectedAgents: string[];
  isConnected: boolean;
  isTyping: boolean;
  error: string | null;
}

export enum MessageType {
  USER_MESSAGE = 'user_message',
  AGENT_RESPONSE = 'agent_response',
  AGENT_COORDINATION = 'agent_coordination',
  CODE_INSERTION = 'code_insertion',
  CONTEXT_UPDATE = 'context_update',
  SYSTEM_MESSAGE = 'system_message',
  ERROR = 'error'
}

export interface WebSocketMessage {
  type: MessageType;
  payload: any;
  sessionId: string;
  timestamp: Date;
}
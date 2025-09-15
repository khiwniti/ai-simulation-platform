import { 
  WebSocketMessage, 
  MessageType, 
  ChatMessage, 
  AgentInfo 
} from '@ai-jupyter/shared';

export class ChatWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private sessionId: string | null = null;
  private messageHandlers: Map<MessageType, (payload: any) => void> = new Map();
  private connectionHandlers: {
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Event) => void;
  } = {};

  constructor() {
    this.setupMessageHandlers();
  }

  connect(sessionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.sessionId = sessionId;
        const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/chat/${sessionId}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
          console.log('Chat WebSocket connected');
          this.reconnectAttempts = 0;
          this.connectionHandlers.onConnect?.();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        this.ws.onclose = (event) => {
          console.log('Chat WebSocket disconnected:', event.code, event.reason);
          this.connectionHandlers.onDisconnect?.();
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('Chat WebSocket error:', error);
          this.connectionHandlers.onError?.(error);
          reject(error);
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.sessionId = null;
  }

  sendMessage(type: MessageType, payload: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    const message: WebSocketMessage = {
      type,
      payload,
      sessionId: this.sessionId!,
      timestamp: new Date()
    };

    this.ws.send(JSON.stringify(message));
  }

  sendUserMessage(content: string, selectedAgents: string[] = []): void {
    this.sendMessage(MessageType.USER_MESSAGE, {
      content,
      selectedAgents,
      timestamp: new Date().toISOString()
    });
  }

  requestAgentCoordination(query: string, capabilities: string[] = []): void {
    this.sendMessage(MessageType.AGENT_COORDINATION, {
      query,
      capabilities,
      timestamp: new Date().toISOString()
    });
  }

  insertCode(snippet: any): void {
    this.sendMessage(MessageType.CODE_INSERTION, {
      snippet,
      timestamp: new Date().toISOString()
    });
  }

  updateContext(context: Record<string, any>): void {
    this.sendMessage(MessageType.CONTEXT_UPDATE, {
      context,
      timestamp: new Date().toISOString()
    });
  }

  onMessage(type: MessageType, handler: (payload: any) => void): void {
    this.messageHandlers.set(type, handler);
  }

  onConnect(handler: () => void): void {
    this.connectionHandlers.onConnect = handler;
  }

  onDisconnect(handler: () => void): void {
    this.connectionHandlers.onDisconnect = handler;
  }

  onError(handler: (error: Event) => void): void {
    this.connectionHandlers.onError = handler;
  }

  private handleMessage(message: WebSocketMessage): void {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message.payload);
    } else {
      console.warn('No handler for message type:', message.type);
    }
  }

  private setupMessageHandlers(): void {
    // Default handlers will be set up by the chat components
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.sessionId) {
        this.connect(this.sessionId).catch(console.error);
      }
    }, delay);
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const chatWebSocketService = new ChatWebSocketService();
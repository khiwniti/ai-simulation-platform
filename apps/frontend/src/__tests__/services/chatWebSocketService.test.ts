import { ChatWebSocketService } from '../../services/chatWebSocketService';
import { MessageType } from '@ai-jupyter/shared';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(public url: string) {
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  send = jest.fn();
  close = jest.fn((code?: number, reason?: string) => {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close', { code, reason, wasClean: true }));
  });
}

// Mock global WebSocket
(global as any).WebSocket = MockWebSocket;

describe('ChatWebSocketService', () => {
  let service: ChatWebSocketService;
  let mockWebSocket: MockWebSocket;

  beforeEach(() => {
    service = new ChatWebSocketService();
    jest.clearAllMocks();
  });

  afterEach(() => {
    service.disconnect();
  });

  describe('Connection Management', () => {
    it('should connect to WebSocket successfully', async () => {
      const sessionId = 'test-session';
      const connectPromise = service.connect(sessionId);

      // Wait for connection to establish
      await connectPromise;

      expect(service.isConnected).toBe(true);
    });

    it('should handle connection errors', async () => {
      const sessionId = 'test-session';
      
      // Mock WebSocket constructor to throw error
      (global as any).WebSocket = jest.fn(() => {
        throw new Error('Connection failed');
      });

      await expect(service.connect(sessionId)).rejects.toThrow('Connection failed');
    });

    it('should disconnect properly', async () => {
      const sessionId = 'test-session';
      await service.connect(sessionId);

      service.disconnect();

      expect(service.isConnected).toBe(false);
    });

    it('should handle reconnection attempts', async () => {
      const sessionId = 'test-session';
      await service.connect(sessionId);

      // Simulate unexpected disconnection
      const ws = (service as any).ws as MockWebSocket;
      ws.onclose?.(new CloseEvent('close', { code: 1006, wasClean: false }));

      // Should attempt reconnection
      expect(setTimeout).toHaveBeenCalled();
    });
  });

  describe('Message Handling', () => {
    beforeEach(async () => {
      await service.connect('test-session');
      mockWebSocket = (service as any).ws as MockWebSocket;
    });

    it('should send user messages', () => {
      const content = 'Help me with physics';
      const selectedAgents = ['physics'];

      service.sendUserMessage(content, selectedAgents);

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: MessageType.USER_MESSAGE,
          payload: {
            content,
            selectedAgents,
            timestamp: expect.any(String)
          },
          sessionId: 'test-session',
          timestamp: expect.any(Date)
        })
      );
    });

    it('should request agent coordination', () => {
      const query = 'Optimize my simulation';
      const capabilities = ['performance_optimization'];

      service.requestAgentCoordination(query, capabilities);

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: MessageType.AGENT_COORDINATION,
          payload: {
            query,
            capabilities,
            timestamp: expect.any(String)
          },
          sessionId: 'test-session',
          timestamp: expect.any(Date)
        })
      );
    });

    it('should handle incoming agent responses', () => {
      const mockHandler = jest.fn();
      service.onMessage(MessageType.AGENT_RESPONSE, mockHandler);

      const mockMessage = {
        type: MessageType.AGENT_RESPONSE,
        payload: {
          agent_id: 'physics-1',
          response: 'Here is physics help',
          confidence_score: 0.9
        },
        sessionId: 'test-session',
        timestamp: new Date()
      };

      // Simulate incoming message
      mockWebSocket.onmessage?.(new MessageEvent('message', {
        data: JSON.stringify(mockMessage)
      }));

      expect(mockHandler).toHaveBeenCalledWith(mockMessage.payload);
    });

    it('should handle malformed messages gracefully', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      // Simulate malformed message
      mockWebSocket.onmessage?.(new MessageEvent('message', {
        data: 'invalid json'
      }));

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to parse WebSocket message:',
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });

    it('should not send messages when disconnected', () => {
      service.disconnect();

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      service.sendUserMessage('test message');

      expect(consoleSpy).toHaveBeenCalledWith('WebSocket not connected');
      expect(mockWebSocket.send).not.toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('Event Handlers', () => {
    it('should register connection event handlers', () => {
      const onConnect = jest.fn();
      const onDisconnect = jest.fn();
      const onError = jest.fn();

      service.onConnect(onConnect);
      service.onDisconnect(onDisconnect);
      service.onError(onError);

      // Verify handlers are stored
      expect((service as any).connectionHandlers.onConnect).toBe(onConnect);
      expect((service as any).connectionHandlers.onDisconnect).toBe(onDisconnect);
      expect((service as any).connectionHandlers.onError).toBe(onError);
    });

    it('should call connection handlers on events', async () => {
      const onConnect = jest.fn();
      const onDisconnect = jest.fn();

      service.onConnect(onConnect);
      service.onDisconnect(onDisconnect);

      await service.connect('test-session');
      expect(onConnect).toHaveBeenCalled();

      service.disconnect();
      expect(onDisconnect).toHaveBeenCalled();
    });
  });

  describe('Message Types', () => {
    beforeEach(async () => {
      await service.connect('test-session');
      mockWebSocket = (service as any).ws as MockWebSocket;
    });

    it('should send code insertion messages', () => {
      const snippet = {
        id: 'snippet-1',
        language: 'python',
        code: 'print("hello")',
        insertable: true
      };

      service.insertCode(snippet);

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: MessageType.CODE_INSERTION,
          payload: {
            snippet,
            timestamp: expect.any(String)
          },
          sessionId: 'test-session',
          timestamp: expect.any(Date)
        })
      );
    });

    it('should send context updates', () => {
      const context = {
        notebook_id: 'nb-123',
        current_cell: 'cell-456'
      };

      service.updateContext(context);

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: MessageType.CONTEXT_UPDATE,
          payload: {
            context,
            timestamp: expect.any(String)
          },
          sessionId: 'test-session',
          timestamp: expect.any(Date)
        })
      );
    });
  });

  describe('Reconnection Logic', () => {
    it('should implement exponential backoff for reconnection', async () => {
      const sessionId = 'test-session';
      await service.connect(sessionId);

      // Mock setTimeout to track reconnection attempts
      const setTimeoutSpy = jest.spyOn(global, 'setTimeout');

      // Simulate multiple failed reconnections
      for (let i = 0; i < 3; i++) {
        const ws = (service as any).ws as MockWebSocket;
        ws.onclose?.(new CloseEvent('close', { code: 1006, wasClean: false }));
      }

      // Should use exponential backoff
      const delays = setTimeoutSpy.mock.calls.map(call => call[1]);
      expect(delays[0]).toBe(1000); // First retry: 1s
      expect(delays[1]).toBe(2000); // Second retry: 2s
      expect(delays[2]).toBe(4000); // Third retry: 4s

      setTimeoutSpy.mockRestore();
    });

    it('should stop reconnecting after max attempts', async () => {
      const sessionId = 'test-session';
      await service.connect(sessionId);

      const setTimeoutSpy = jest.spyOn(global, 'setTimeout');

      // Simulate max reconnection attempts
      for (let i = 0; i < 6; i++) {
        const ws = (service as any).ws as MockWebSocket;
        ws.onclose?.(new CloseEvent('close', { code: 1006, wasClean: false }));
      }

      // Should not attempt more than 5 reconnections
      expect(setTimeoutSpy).toHaveBeenCalledTimes(5);

      setTimeoutSpy.mockRestore();
    });
  });
});
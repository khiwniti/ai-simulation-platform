import { ChatSession, AgentInfo } from '@ai-jupyter/shared';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ChatApiService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API request failed: ${response.status} ${error}`);
    }

    return response.json();
  }

  async createChatSession(
    sessionId: string, 
    notebookId?: string, 
    context?: Record<string, any>
  ): Promise<ChatSession> {
    return this.request<ChatSession>('/api/v1/agents/sessions', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        notebook_id: notebookId,
        context: context || {}
      }),
    });
  }

  async endChatSession(sessionId: string): Promise<void> {
    await this.request(`/api/v1/agents/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getAvailableAgents(): Promise<AgentInfo[]> {
    const agentTypes = await this.request<string[]>('/api/v1/agents/types');
    
    // Transform agent types into AgentInfo objects
    const agentInfoMap: Record<string, Partial<AgentInfo>> = {
      physics: {
        name: 'Physics Agent',
        description: 'Specialized in NVIDIA PhysX AI and physics simulations',
        capabilities: ['physics_modeling', 'simulation_setup', 'parameter_optimization']
      },
      visualization: {
        name: 'Visualization Agent',
        description: 'Expert in 3D graphics and data visualization',
        capabilities: ['3d_rendering', 'data_visualization', 'animation']
      },
      optimization: {
        name: 'Optimization Agent',
        description: 'Performance tuning and GPU optimization specialist',
        capabilities: ['performance_tuning', 'gpu_optimization', 'memory_management']
      },
      debug: {
        name: 'Debug Agent',
        description: 'Error analysis and troubleshooting expert',
        capabilities: ['error_analysis', 'debugging', 'code_quality']
      }
    };

    return agentTypes.map(type => ({
      id: type,
      type,
      name: agentInfoMap[type]?.name || `${type} Agent`,
      description: agentInfoMap[type]?.description || `Specialized ${type} agent`,
      capabilities: agentInfoMap[type]?.capabilities || [],
      isActive: false,
      isAvailable: true
    }));
  }

  async queryAgent(
    agentType: string,
    query: string,
    sessionId: string,
    context?: Record<string, any>
  ): Promise<any> {
    return this.request('/api/v1/agents/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId,
        context: context || {}
      }),
      headers: {
        'X-Agent-Type': agentType
      }
    });
  }

  async coordinateAgents(
    query: string,
    sessionId: string,
    selectedAgents: string[] = [],
    capabilities: string[] = [],
    context?: Record<string, any>
  ): Promise<any> {
    return this.request('/api/v1/agents/coordinate', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId,
        required_capabilities: capabilities,
        preferred_agents: selectedAgents,
        max_agents: Math.max(selectedAgents.length, 3),
        context: context || {}
      }),
    });
  }

  async getSessionStatus(sessionId: string): Promise<Record<string, any>> {
    return this.request(`/api/v1/agents/sessions/${sessionId}/status`);
  }

  async updateSessionContext(
    sessionId: string, 
    context: Record<string, any>
  ): Promise<void> {
    await this.request(`/api/v1/agents/sessions/${sessionId}/context`, {
      method: 'POST',
      body: JSON.stringify(context),
    });
  }

  async getCoordinationHistory(limit: number = 10): Promise<any[]> {
    return this.request(`/api/v1/agents/coordination-history?limit=${limit}`);
  }

  async getMetrics(): Promise<Record<string, any>> {
    return this.request('/api/v1/agents/metrics');
  }
}

export const chatApiService = new ChatApiService();
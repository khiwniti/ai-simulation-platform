interface NotebookExecutionResult {
  success: boolean;
  data: {
    executionId: string;
    cellId: string;
    output: string;
    figures: string[];
    error?: {
      type: string;
      message: string;
      traceback: string;
    };
    status: 'success' | 'error';
  };
}

interface NotebookData {
  id: string;
  name: string;
  description: string;
  template: string;
  type: string;
  cells: any[];
  createdAt: string;
  lastModified: string;
  metadata: {
    kernel: string;
    language: string;
  };
}

class NotebookService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';
  }

  async createNotebook(data: {
    name: string;
    description?: string;
    template?: string;
    type?: string;
  }): Promise<NotebookData> {
    const response = await fetch(`${this.baseURL}/notebooks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create notebook');
    }

    const result = await response.json();
    return result.data;
  }

  async getNotebook(id: string): Promise<NotebookData> {
    const response = await fetch(`${this.baseURL}/notebooks/${id}`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch notebook');
    }

    const result = await response.json();
    return result.data;
  }

  async updateNotebook(id: string, updates: Partial<NotebookData>): Promise<NotebookData> {
    const response = await fetch(`${this.baseURL}/notebooks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error('Failed to update notebook');
    }

    const result = await response.json();
    return result.data;
  }

  async executeCode(
    notebookId: string,
    cellId: string,
    code: string,
    cellType: string = 'code'
  ): Promise<NotebookExecutionResult> {
    const response = await fetch(`${this.baseURL}/notebooks/${notebookId}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        cellId,
        code,
        cellType,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to execute code');
    }

    return await response.json();
  }

  async getExecutionStatus(notebookId: string, executionId: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/notebooks/${notebookId}/executions/${executionId}`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch execution status');
    }

    const result = await response.json();
    return result.data;
  }

  async listNotebooks(): Promise<NotebookData[]> {
    const response = await fetch(`${this.baseURL}/notebooks`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to list notebooks');
    }

    const result = await response.json();
    return result.data;
  }

  async deleteNotebook(id: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/notebooks/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to delete notebook');
    }
  }
}

export const notebookService = new NotebookService();
export type { NotebookData, NotebookExecutionResult };
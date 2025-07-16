// API service for backend integration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('authToken');
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    return this.request<{ user: any; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, username: string, password: string) {
    return this.request<{ user: any; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
  }

  async logout() {
    return this.request('/auth/logout', { method: 'POST' });
  }

  // User management (Admin only)
  async getUsers() {
    return this.request<any[]>('/admin/users');
  }

  async updateUserRole(userId: string, role: string) {
    return this.request(`/admin/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  }

  async deleteUser(userId: string) {
    return this.request(`/admin/users/${userId}`, { method: 'DELETE' });
  }

  // Tools endpoints
  async getTools() {
    return this.request<any[]>('/tools');
  }

  async createTool(toolData: any) {
    return this.request('/tools', {
      method: 'POST',
      body: JSON.stringify(toolData),
    });
  }

  async updateTool(toolId: string, toolData: any) {
    return this.request(`/tools/${toolId}`, {
      method: 'PUT',
      body: JSON.stringify(toolData),
    });
  }

  async deleteTool(toolId: string) {
    return this.request(`/tools/${toolId}`, { method: 'DELETE' });
  }

  // Scraping jobs endpoints
  async createScrapingJob(jobData: any) {
    return this.request('/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  }

  async getScrapingJobs(userId?: string) {
    const endpoint = userId ? `/jobs?userId=${userId}` : '/jobs';
    return this.request<any[]>(endpoint);
  }

  async getJobStatus(jobId: string) {
    return this.request(`/jobs/${jobId}/status`);
  }

  async stopJob(jobId: string) {
    return this.request(`/jobs/${jobId}/stop`, { method: 'POST' });
  }

  async downloadJobOutput(jobId: string, filename: string) {
    const token = localStorage.getItem('authToken');
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/download/${filename}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
    
    if (!response.ok) {
      throw new Error('Download failed');
    }
    
    return response.blob();
  }

  // Performance analytics
  async getPerformanceData(userId?: string) {
    const endpoint = userId ? `/analytics/performance?userId=${userId}` : '/analytics/performance';
    return this.request(endpoint);
  }

  async getSystemMetrics() {
    return this.request('/admin/system-metrics');
  }

  // WebSocket connection for real-time updates
  connectWebSocket(jobId: string, onMessage: (data: any) => void) {
    const token = localStorage.getItem('authToken');
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/jobs/${jobId}/stream?token=${token}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    return ws;
  }
}

export const apiService = new ApiService();
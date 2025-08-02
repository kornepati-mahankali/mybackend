export interface User {
  id: string;
  email: string;
  username: string;
  role: 'user' | 'admin' | 'super_admin';
  createdAt: string;
  lastLogin?: string;
  isActive: boolean;
  bio?: string;
}

export interface Tool {
  id?: string;
  name: string;
  category?: 'gem' | 'global' | 'all' | 'eprocurement' | 'ireps';
  description: string;
  icon?: string;
  isActive?: boolean;
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
  script_path?: string;
  inputs?: {
    name: string;
    type: string;
    required: boolean;
    default?: any;
    description?: string;
  }[];
  valid_states?: string[]; // rename from states
  valid_cities?: { [state: string]: string[] }; // rename from cities
}


export interface ScrapingJob {
  id: string;
  userId: string;
  toolId: string;
  state: string;
  username: string;
  startingName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  progress: number;
  startTime: string;
  endTime?: string;
  outputFiles: string[];
  logs: string[];
  createdAt: string;
}

export interface Performance {
  userId: string;
  totalJobs: number;
  successfulJobs: number;
  failedJobs: number;
  averageTime: number;
  lastActivity: string;
}

export interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalJobs: number;
  runningJobs: number;
  systemLoad: number;
  memoryUsage: number;
  diskUsage: number;
  uptime: number;
}
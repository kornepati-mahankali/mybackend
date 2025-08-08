// Centralized API configuration
export const API_CONFIG = {
  // Main API base URL - Updated to use AWS EC2 instance
  MAIN_API: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : 'http://54.149.111.114:8002',
  
  // System metrics API
  SYSTEM_API: window.location.hostname === 'localhost' 
    ? 'http://localhost:8001'
    : 'http://54.149.111.114:8002',
  
  // Dashboard API
  DASHBOARD_API: window.location.hostname === 'localhost' 
    ? 'http://localhost:8004'
    : 'http://54.149.111.114:8002',
  
  // WebSocket URLs
  WS_MAIN: window.location.hostname === 'localhost'
    ? 'ws://localhost:8002'
    : 'ws://54.149.111.114:8002',
  
  WS_DASHBOARD: window.location.hostname === 'localhost'
    ? 'ws://localhost:8002'
    : 'ws://54.149.111.114:8002'
};

// Helper function to get API URL for different services
export const getApiUrl = (service: 'main' | 'system' | 'dashboard' = 'main') => {
  switch (service) {
    case 'system':
      return API_CONFIG.SYSTEM_API;
    case 'dashboard':
      return API_CONFIG.DASHBOARD_API;
    default:
      return API_CONFIG.MAIN_API;
  }
};

// Helper function to get WebSocket URL
export const getWsUrl = (service: 'main' | 'dashboard' = 'main') => {
  switch (service) {
    case 'dashboard':
      return API_CONFIG.WS_DASHBOARD;
    default:
      return API_CONFIG.WS_MAIN;
  }
}; 
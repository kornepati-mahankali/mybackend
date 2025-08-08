import { API_CONFIG } from '../config/api';

export const testBackendConnection = async () => {
  const testUrls = [
    { name: 'Main API', url: `${API_CONFIG.MAIN_API}/health` },
    { name: 'System API', url: `${API_CONFIG.SYSTEM_API}/health` },
    { name: 'Dashboard API', url: `${API_CONFIG.DASHBOARD_API}/health` }
  ];

  const results = [];

  for (const { name, url } of testUrls) {
    try {
      console.log(`🔍 Testing ${name} at: ${url}`);
      const response = await fetch(url, { 
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        console.log(`✅ ${name} is accessible`);
        results.push({ name, status: 'success', url });
      } else {
        console.log(`⚠️ ${name} returned status: ${response.status}`);
        results.push({ name, status: 'error', url, error: `HTTP ${response.status}` });
      }
    } catch (error) {
      console.error(`❌ ${name} connection failed:`, error);
      results.push({ name, status: 'error', url, error: error.message });
    }
  }

  return results;
};

export const getConnectionStatus = () => {
  const isLocalhost = window.location.hostname === 'localhost';
  const backendUrl = isLocalhost ? 'localhost' : 'AWS Elastic Beanstalk';
  
  return {
    isLocalhost,
    backendUrl,
    apiConfig: API_CONFIG
  };
}; 
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const APITest: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const testAPI = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Use admin metrics API on port 8001
      const API_BASE_URL = window.location.hostname === 'localhost' 
        ? 'http://localhost:8001'
        : 'https://lavangam-minimal-backend-env.eba-22qprjmg.us-east-1.elasticbeanstalk.com';
      
      const response = await axios.get(`${API_BASE_URL}/admin-metrics`);
      setData(response.data);
    } catch (err: any) {
      console.error('API Error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to connect to admin metrics API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <div className="p-4 bg-gray-800 border border-gray-600 rounded-lg mb-4">
      <h3 className="text-white font-bold mb-2">🧪 API Connection Test</h3>
      
      <button 
        onClick={testAPI}
        className="mb-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
      >
        Test API
      </button>
      
      {loading && <p className="text-yellow-400">🔄 Loading...</p>}
      
      {error && (
        <div className="text-red-400 mb-2">
          <p>❌ Error: {error}</p>
        </div>
      )}
      
      {data && (
        <div className="text-green-400 text-sm">
          <p>✅ API Connected!</p>
          <p>Database Size: {data.database_size?.total_size || 'N/A'}</p>
          <p>Active Jobs: {data.jobs_info?.active_jobs || 'N/A'}</p>
          <p>Queued Jobs: {data.jobs_info?.queued_jobs || 'N/A'}</p>
          <p>CPU: {data.system_load?.cpu_percent?.toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
};

export default APITest; 
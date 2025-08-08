import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface AdminMetrics {
  system_load: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    timestamp: string;
  };
  database_size: {
    total_size: string;
    today_growth: string;
  };
  jobs_info: {
    active_jobs: number;
    queued_jobs: number;
  };
}

const AdminMetricsTest: React.FC = () => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Use admin metrics API on port 8001
        const API_BASE_URL = window.location.hostname === 'localhost' 
          ? 'http://localhost:8001'
          : 'https://lavangam-minimal-backend-env.eba-22qprjmg.us-east-1.elasticbeanstalk.com';
        
        const response = await axios.get<AdminMetrics>(`${API_BASE_URL}/admin-metrics`);
        setMetrics(response.data);
      } catch (err: any) {
        console.error('Failed to fetch admin metrics:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-4 bg-blue-100 border border-blue-400 rounded">
        <p className="text-blue-700">🔄 Loading admin metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 rounded">
        <p className="text-red-700">❌ {error}</p>
        <p className="text-red-600 text-sm mt-2">
          Make sure the admin metrics API is running on the backend server
        </p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
        <p className="text-yellow-700">⚠️ No metrics data received</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-green-100 border border-green-400 rounded">
      <h3 className="text-green-800 font-bold mb-2">✅ Admin Metrics API Connected!</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <strong>System Load:</strong>
          <p>CPU: {metrics.system_load.cpu_percent.toFixed(1)}%</p>
          <p>Memory: {metrics.system_load.memory_percent.toFixed(1)}%</p>
          <p>Disk: {metrics.system_load.disk_percent.toFixed(1)}%</p>
        </div>
        <div>
          <strong>Database:</strong>
          <p>Size: {metrics.database_size.total_size}</p>
          <p>Growth: {metrics.database_size.today_growth}</p>
        </div>
        <div>
          <strong>Jobs:</strong>
          <p>Active: {metrics.jobs_info.active_jobs}</p>
          <p>Queued: {metrics.jobs_info.queued_jobs}</p>
        </div>
      </div>
      <p className="text-green-600 text-xs mt-2">
        Last updated: {new Date(metrics.system_load.timestamp).toLocaleTimeString()}
      </p>
    </div>
  );
};

export default AdminMetricsTest; 
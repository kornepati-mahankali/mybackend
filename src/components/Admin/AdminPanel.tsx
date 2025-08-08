import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Server, 
  Database, 
  Shield, 
  Activity,
  AlertTriangle,
  Settings,
  Plus
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useAnimation } from '../../contexts/AnimationContext';
import dayjs from 'dayjs';
import SystemUsageChart from '../SystemUsageChart';
import AdminMetricsTest from './AdminMetricsTest';
import { apiService } from '../../services/api';

// Types for admin metrics
interface SystemLoad {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  memory_used: string;
  memory_total: string;
  disk_used: string;
  disk_total: string;
  uptime_seconds: number;
  uptime_formatted: string;
  timestamp: string;
}

interface DatabaseSize {
  total_size: string;
  total_size_bytes: number;
  today_growth: string;
  today_growth_bytes: number;
  growth_percentage: number;
}

interface JobsInfo {
  active_jobs: number;
  queued_jobs: number;
  completed_jobs: number;
  total_jobs: number;
  note?: string;
  error?: string;
}

interface AdminMetrics {
  system_load: SystemLoad;
  database_size: DatabaseSize;
  jobs_info: JobsInfo;
  timestamp: string;
}

export const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<Array<{ id: string; email: string; created_at: string; last_sign_in_at: string; role: string }>>([]);
  const [adminMetrics, setAdminMetrics] = useState<AdminMetrics | null>(null);
  const [metricsError, setMetricsError] = useState('');
  const [fetchError, setFetchError] = useState('');
  const { enabled: animationsEnabled } = useAnimation();

  // Fetch admin metrics
  const fetchAdminMetrics = async () => {
    try {
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      // Use admin metrics API on port 8001
      const API_BASE_URL = window.location.hostname === 'localhost' 
        ? 'http://localhost:8001'
        : 'https://lavangam-minimal-backend-env.eba-22qprjmg.us-east-1.elasticbeanstalk.com';
      const response = await axios.get<AdminMetrics>(`${API_BASE_URL}/admin-metrics?t=${timestamp}`);
      setAdminMetrics(response.data);
      setMetricsError('');
    } catch (err: any) {
      console.error('Failed to fetch admin metrics:', err);
      const errorMessage = err.response?.status 
        ? `API Error: ${err.response.status} - ${err.response.statusText}`
        : err.message || 'Failed to fetch system metrics.';
      setMetricsError(errorMessage);
    }
  };

  // Fetch users
  const fetchUsers = async () => {
    try {
      console.log('🔍 Fetching users from API service...');
      const response = await apiService.getSupabaseUsers();
      console.log('✅ Users fetched successfully:', response);
      setUsers(response.users || []);
      setFetchError('');
    } catch (err) {
      console.error('❌ Failed to fetch users:', err);
      setFetchError('Failed to fetch users from backend.');
      setUsers([]);
    }
  };

  useEffect(() => {
    fetchUsers();
    
    // Initial connection test
    const testConnection = async () => {
      try {
        // Use dynamic URL based on environment
        const API_BASE_URL = window.location.hostname === 'localhost' 
          ? 'http://localhost:8001'
          : 'https://lavangam-minimal-backend-env.eba-22qprjmg.us-east-1.elasticbeanstalk.com';
        const response = await axios.get(`${API_BASE_URL}/test`);
        console.log('✅ API connection test successful:', response.data);
        fetchAdminMetrics(); // If test passes, fetch metrics
      } catch (err) {
        console.error('❌ API connection test failed:', err);
        setMetricsError('API server not reachable');
      }
    };
    
    testConnection();
    
    // Set up real-time updates every 3 seconds for faster updates
    const metricsInterval = setInterval(fetchAdminMetrics, 3000);
    
    return () => {
      clearInterval(metricsInterval);
    };
  }, []);

  const activeUserCount = users.length; // You can refine this if you have an 'active' field
  const totalUserCount = users.length;

  // Get real-time metrics or use fallback values
  const systemLoad = adminMetrics?.system_load;
  const databaseSize = adminMetrics?.database_size;
  const jobsInfo = adminMetrics?.jobs_info;



      return (
      <div className="space-y-6">
        <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 sm:gap-0"
      >
        <div>
          <h1 className="text-3xl sm:text-2xl font-bold dark:text-white text-black mb-2">Admin Panel</h1>
          <p className="dark:text-gray-400 text-gray-600 text-base sm:text-sm">System administration and user management</p>
        </div>
        <div className="flex items-center space-x-2 text-green-400 mt-2 sm:mt-0">
          <Shield className="w-5 h-5" />
          <span className="text-sm">Admin Access</span>
        </div>
      </motion.div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Active Users',
            value: totalUserCount.toString(),
            change: `+${activeUserCount} online`,
            icon: Users,
            color: 'blue'
          },
          {
            title: 'System Load',
            value: systemLoad ? `${systemLoad.cpu_percent.toFixed(1)}%` : '43.7%',
            change: systemLoad ? (systemLoad.cpu_percent > 80 ? 'High' : systemLoad.cpu_percent > 50 ? 'Normal' : 'Low') : 'Normal',
            icon: Server,
            color: 'green'
          },
          {
            title: 'Database Size',
            value: databaseSize ? databaseSize.total_size : '128.0KB',
            change: databaseSize ? `${databaseSize.today_growth} today` : '0B today',
            icon: Database,
            color: 'purple'
          },
          {
            title: 'Active Jobs',
            value: jobsInfo ? jobsInfo.active_jobs.toString() : '0',
            change: jobsInfo ? `${jobsInfo.queued_jobs} queued` : '0 queued',
            icon: Activity,
            color: 'orange'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg bg-${stat.color}-600/20`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
              </div>
            </div>
            
            <div>
              <h3 className="text-2xl font-bold dark:text-white text-black mb-1">{stat.value}</h3>
              <p className="text-sm dark:text-gray-400 text-gray-600 mb-2">{stat.title}</p>
              <p className="text-xs text-green-400">{stat.change}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Resources */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <SystemUsageChart />
        </motion.div>

        {/* User Management */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold dark:text-white text-black">User Management</h3>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200"
            >
              <Plus className="w-4 h-4 text-white" />
            </motion.button>
          </div>
          {fetchError && (
            <div className="mb-4 text-red-500 text-sm">{fetchError}</div>
          )}
          <div className="space-y-3">
            {users.slice(0, 10).map((user, index) => {
              // Determine if user is active based on last_sign_in_at within 30 days
              const isActive = user.last_sign_in_at && dayjs().diff(dayjs(user.last_sign_in_at), 'day') <= 30;
              return (
                <div key={user.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 rounded-lg dark:bg-gray-700/50 bg-gray-100 gap-2 sm:gap-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-white">
                        {user.email ? user.email[0].toUpperCase() : '?'}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium dark:text-white text-black">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${isActive ? 'bg-green-900/50 text-green-400' : 'bg-blue-900/50 text-blue-400'}`}>
                      {isActive ? 'active' : 'inactive'}
                    </span>
                    <span className="text-xs dark:text-gray-400 text-gray-600">Created: {user.created_at ? user.created_at.split('T')[0] : ''}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div> 
      {/* System Alerts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
      >
        <h3 className="text-lg font-semibold dark:text-white text-black mb-4">System Alerts</h3>
        <div className="space-y-3">
          {[
            {
              type: 'warning',
              message: 'Database storage is approaching 80% capacity',
              time: '2 minutes ago',
              action: 'Review storage usage'
            },
            {
              type: 'info',
              message: 'Scheduled maintenance completed successfully',
              time: '1 hour ago',
              action: 'View maintenance log'
            },
            {
              type: 'error',
              message: 'Failed to connect to external API endpoint',
              time: '3 hours ago',
              action: 'Check API status'
            }
          ].map((alert, index) => (
            <div key={index} className=  "flex items-start space-x-3 p-3 bg-gray-700/50 rounded-lg">
              <div className={`p-1 rounded-full ${
                alert.type === 'error' ? 'bg-red-600/20' :
                alert.type === 'warning' ? 'bg-yellow-600/20' : 'bg-blue-600/20'
              }`}>
                <AlertTriangle className={`w-4 h-4 ${
                  alert.type === 'error' ? 'text-red-400' :
                  alert.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                }`} />
              </div>
              <div className="flex-1">
                <p className="text-sm text-white">{alert.message}</p>
                <div className="flex items-center justify-between mt-1">
                  <p className="text-xs text-gray-400">{alert.time}</p>
                  <button className="text-xs text-blue-400 hover:text-blue-300">
                    {alert.action}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

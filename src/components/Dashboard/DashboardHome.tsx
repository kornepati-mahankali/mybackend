import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Download, 
  Clock, 
  TrendingUp,
  Users,
  Server,
  AlertCircle,
  CheckCircle,
  Wifi,
  WifiOff
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAnimation } from '../../contexts/AnimationContext';
import axios from 'axios';

interface DashboardMetrics {
  active_jobs: number;
  completed_today: number;
  total_downloads: number;
  success_rate: number;
  recent_activity: Array<{
    title: string;
    status: string;
    updated_at: string;
    downloads: number;
    records_extracted: number;
    error: string | null;
  }>;
  weekly_chart_data: Array<{
    name: string;
    jobs: number;
    success: number;
  }>;
  system_status: {
    api_server: { status: string; uptime: string; cpu_usage?: string; memory_usage?: string };
    database: { status: string; uptime: string; disk_usage?: string };
    queue_system: { status: string; uptime: string };
  };
}

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data: DashboardMetrics;
}

export const DashboardHome: React.FC = () => {
  const { enabled: animationsEnabled } = useAnimation();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

          // API base URL
        const API_BASE_URL = 'http://localhost:8004';
        const WS_URL = 'ws://localhost:8002';

  // Fetch initial data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/metrics`);
      setMetrics(response.data as DashboardMetrics);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
      // Fallback to mock data if API is not available
      setMetrics(getMockData());
    } finally {
      setLoading(false);
    }
  };

  // WebSocket connection
  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket(WS_URL);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'dashboard_update' || message.type === 'initial_data') {
            setMetrics(message.data);
            setLastUpdate(new Date());
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };
    } catch (err) {
      console.error('Error connecting to WebSocket:', err);
      setWsConnected(false);
    }
  };

  // Mock data fallback
  const getMockData = (): DashboardMetrics => ({
    active_jobs: 7,
    completed_today: 24,
    total_downloads: 1247,
    success_rate: 94.2,
    recent_activity: [
      {
        title: 'Gem Portal Scraper completed',
        status: 'completed',
        updated_at: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        downloads: 1247,
        records_extracted: 1247,
        error: null
      },
      {
        title: 'Global Trade Monitor started',
        status: 'running',
        updated_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        downloads: 856,
        records_extracted: 856,
        error: null
      },
      {
        title: 'E-Procurement scan failed',
        status: 'failed',
        updated_at: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
        downloads: 0,
        records_extracted: 0,
        error: 'Connection timeout - retrying'
      },
      {
        title: 'Market Intelligence completed',
        status: 'completed',
        updated_at: new Date(Date.now() - 18 * 60 * 1000).toISOString(),
        downloads: 856,
        records_extracted: 856,
        error: null
      }
    ],
    weekly_chart_data: [
      { name: 'Mon', jobs: 12, success: 10 },
      { name: 'Tue', jobs: 19, success: 16 },
      { name: 'Wed', jobs: 8, success: 7 },
      { name: 'Thu', jobs: 15, success: 13 },
      { name: 'Fri', jobs: 22, success: 20 },
      { name: 'Sat', jobs: 18, success: 17 },
      { name: 'Sun', jobs: 14, success: 12 },
    ],
    system_status: {
      api_server: { status: 'online', uptime: '99.9%', cpu_usage: '15.2%', memory_usage: '45.8%' },
      database: { status: 'online', uptime: '99.8%', disk_usage: '67.3%' },
      queue_system: { status: 'online', uptime: '99.7%' }
    }
  });

  // Format time ago
  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-400';
      case 'running': return 'bg-blue-400';
      case 'failed': return 'bg-red-400';
      case 'queued': return 'bg-yellow-400';
      default: return 'bg-gray-400';
    }
  };

  // Get activity details
  const getActivityDetails = (activity: any) => {
    if (activity.error) return activity.error || 'Error occurred';
    if (activity.records_extracted) return `${activity.records_extracted} records extracted`;
    if (activity.downloads > 0) return `${activity.downloads} downloads`;
    
    // Check for different status types and provide appropriate messages
    switch (activity.status) {
      case 'completed':
        return 'Job completed successfully';
      case 'running':
        return 'Job in progress...';
      case 'failed':
        return 'Job failed - check logs';
      case 'queued':
        return 'Waiting in queue...';
      default:
        return 'Processing...';
    }
  };

  useEffect(() => {
    fetchDashboardData();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const currentMetrics = metrics || getMockData();

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:justify-between md:items-center gap-2 md:gap-0"
      >
        <div>
          <h1 className="text-3xl md:text-4xl font-bold dark:text-white text-black mb-2">Dashboard Overview</h1>
          <p className="dark:text-gray-400 text-gray-600 text-base md:text-lg">Monitor your scraping operations and performance</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {wsConnected ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-400" />
            )}
            <span className="text-sm dark:text-gray-400">
              {wsConnected ? 'Live Updates' : 'Polling Mode'}
            </span>
          </div>
          <div className="flex items-center space-x-2 text-green-400 mt-2 md:mt-0">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm">System Online</span>
          </div>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
        >
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </motion.div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-4">
        {[
          {
            title: 'Active Jobs',
            value: currentMetrics.active_jobs.toString(),
            change: '+2 from yesterday',
            icon: Activity,
            color: 'blue'
          },
          {
            title: 'Completed Today',
            value: currentMetrics.completed_today.toString(),
            change: '+18% from yesterday',
            icon: CheckCircle,
            color: 'green'
          },
          {
            title: 'Total Downloads',
            value: currentMetrics.total_downloads.toLocaleString(),
            change: '+5.2% this week',
            icon: Download,
            color: 'purple'
          },
          {
            title: 'Success Rate',
            value: `${currentMetrics.success_rate}%`,
            change: '+2.1% improvement',
            icon: TrendingUp,
            color: 'orange'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              delay: animationsEnabled ? index * 0.1 : 0,
              duration: animationsEnabled ? 0.5 : 0
            }}
            className="rounded-xl p-6 sm:p-4 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
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

      {/* Chart Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mt-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ 
            delay: animationsEnabled ? 0.4 : 0,
            duration: animationsEnabled ? 0.5 : 0
          }}
          className="rounded-xl p-6 sm:p-4 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Weekly Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={currentMetrics.weekly_chart_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="jobs" 
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                isAnimationActive={animationsEnabled}
                name="Total Jobs"
              />
              <Line 
                type="monotone" 
                dataKey="success" 
                stroke="#10B981"
                strokeWidth={2}
                dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                isAnimationActive={animationsEnabled}
                name="Successful"
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ 
            delay: animationsEnabled ? 0.5 : 0,
            duration: animationsEnabled ? 0.5 : 0
          }}
          className="rounded-xl p-6 sm:p-4 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {currentMetrics.recent_activity.map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ 
                  delay: 0.6 + (index * 0.1),
                  duration: animationsEnabled ? 0.5 : 0
                }}
                className="flex items-start space-x-3 p-3 rounded-lg dark:bg-gray-700/50 bg-gray-100"
              >
                <div className={`w-2 h-2 rounded-full mt-2 ${getStatusColor(activity.status)}`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium dark:text-white text-black">{activity.title}</p>
                  <p className="text-xs dark:text-gray-400 text-gray-600">{getActivityDetails(activity)}</p>
                  <p className="text-xs dark:text-gray-500 text-gray-500 mt-1">{formatTimeAgo(activity.updated_at)}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
                  transition={{ 
            delay: animationsEnabled ? 0.6 : 0,
            duration: animationsEnabled ? 0.5 : 0
          }}
        className="rounded-xl p-6 sm:p-4 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
      >
        <h3 className="text-lg font-semibold dark:text-white text-black mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-2">
          {[
            { 
              name: 'API Server', 
              status: currentMetrics.system_status.api_server.status, 
              uptime: currentMetrics.system_status.api_server.uptime,
              details: currentMetrics.system_status.api_server.cpu_usage 
                ? `CPU: ${currentMetrics.system_status.api_server.cpu_usage} | RAM: ${currentMetrics.system_status.api_server.memory_usage}`
                : null
            },
            { 
              name: 'Database', 
              status: currentMetrics.system_status.database.status, 
              uptime: currentMetrics.system_status.database.uptime,
              details: currentMetrics.system_status.database.disk_usage 
                ? `Disk: ${currentMetrics.system_status.database.disk_usage}`
                : null
            },
            { 
              name: 'Queue System', 
              status: currentMetrics.system_status.queue_system.status, 
              uptime: currentMetrics.system_status.queue_system.uptime,
              details: null
            }
          ].map((service, index) => (
            <div key={service.name} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 sm:p-2 rounded-lg dark:bg-gray-700/50 bg-gray-100">
              <div className="flex items-center space-x-3">
                <Server className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm sm:text-xs font-medium dark:text-white text-black">{service.name}</p>
                  <p className="text-xs sm:text-[11px] dark:text-gray-400 text-gray-600">Uptime: {service.uptime}</p>
                  {service.details && (
                    <p className="text-xs sm:text-[10px] dark:text-gray-500 text-gray-500">{service.details}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 ${service.status === 'online' ? 'bg-green-400' : 'bg-red-400'} rounded-full`}></div>
                <span className="text-xs sm:text-[11px] text-green-400 capitalize">{service.status}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Last Update Indicator */}
      {lastUpdate && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-xs dark:text-gray-500 text-gray-500"
        >
          Last updated: {lastUpdate.toLocaleTimeString()}
        </motion.div>
      )}
    </div>
  );
};
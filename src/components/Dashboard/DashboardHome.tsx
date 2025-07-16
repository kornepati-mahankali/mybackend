import React from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Download, 
  Clock, 
  TrendingUp,
  Users,
  Server,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAnimation } from '../../contexts/AnimationContext';

const mockData = [
  { name: 'Mon', jobs: 12, success: 10 },
  { name: 'Tue', jobs: 19, success: 16 },
  { name: 'Wed', jobs: 8, success: 7 },
  { name: 'Thu', jobs: 15, success: 13 },
  { name: 'Fri', jobs: 22, success: 20 },
  { name: 'Sat', jobs: 18, success: 17 },
  { name: 'Sun', jobs: 14, success: 12 },
];

export const DashboardHome: React.FC = () => {
  const { enabled: animationsEnabled } = useAnimation();
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold dark:text-white text-black mb-2">Dashboard Overview</h1>
          <p className="dark:text-gray-400 text-gray-600">Monitor your scraping operations and performance</p>
        </div>
        <div className="flex items-center space-x-2 text-green-400">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm">System Online</span>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Active Jobs',
            value: '7',
            change: '+2 from yesterday',
            icon: Activity,
            color: 'blue'
          },
          {
            title: 'Completed Today',
            value: '24',
            change: '+18% from yesterday',
            icon: CheckCircle,
            color: 'green'
          },
          {
            title: 'Total Downloads',
            value: '1,247',
            change: '+5.2% this week',
            icon: Download,
            color: 'purple'
          },
          {
            title: 'Success Rate',
            value: '94.2%',
            change: '+2.1% improvement',
            icon: TrendingUp,
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

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Weekly Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockData}>
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
          transition={{ delay: 0.5 }}
          className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              {
                action: 'Gem Portal Scraper completed',
                time: '2 minutes ago',
                status: 'success',
                details: '1,247 records extracted'
              },
              {
                action: 'Global Trade Monitor started',
                time: '5 minutes ago',
                status: 'running',
                details: 'Processing USA market data'
              },
              {
                action: 'E-Procurement scan failed',
                time: '12 minutes ago',
                status: 'error',
                details: 'Connection timeout - retrying'
              },
              {
                action: 'Market Intelligence completed',
                time: '18 minutes ago',
                status: 'success',
                details: '856 opportunities found'
              }
            ].map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  activity.status === 'success' ? 'bg-green-400' :
                  activity.status === 'running' ? 'bg-blue-400' : 'bg-red-400'
                }`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium dark:text-white text-black">{activity.action}</p>
                  <p className="text-xs dark:text-gray-400 text-gray-600">{activity.details}</p>
                  <p className="text-xs dark:text-gray-500 text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
      >
        <h3 className="text-lg font-semibold dark:text-white text-black mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { name: 'API Server', status: 'online', uptime: '99.9%' },
            { name: 'Database', status: 'online', uptime: '99.8%' },
            { name: 'Queue System', status: 'online', uptime: '99.7%' }
          ].map((service, index) => (
            <div key={service.name} className="flex items-center justify-between p-3 rounded-lg dark:bg-gray-700/50 bg-gray-100">
              <div className="flex items-center space-x-3">
                <Server className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium dark:text-white text-black">{service.name}</p>
                  <p className="text-xs dark:text-gray-400 text-gray-600">Uptime: {service.uptime}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-xs text-green-400 capitalize">{service.status}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Activity,
  Download
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useAuth } from '../../contexts/AuthContext';
import { useAnimation } from '../../contexts/AnimationContext';

const performanceData = [
  { name: 'Jan', jobs: 45, success: 42, failed: 3 },
  { name: 'Feb', jobs: 52, success: 48, failed: 4 },
  { name: 'Mar', jobs: 38, success: 36, failed: 2 },
  { name: 'Apr', jobs: 61, success: 58, failed: 3 },
  { name: 'May', jobs: 55, success: 51, failed: 4 },
  { name: 'Jun', jobs: 67, success: 63, failed: 4 },
];

const toolUsage = [
  { name: 'Gem Portal', usage: 85 },
  { name: 'Global Trade', usage: 72 },
  { name: 'E-Procurement', usage: 68 },
  { name: 'Universal Extractor', usage: 45 },
  { name: 'Market Intelligence', usage: 38 },
];

export const PerformanceView: React.FC = () => {
  const { user } = useAuth();
  const { enabled: animationsEnabled } = useAnimation();

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold dark:text-white text-black mb-2">Performance Analytics</h1>
          <p className="dark:text-gray-400 text-gray-600">
            {user?.role === 'admin' ? 'System-wide performance metrics' : 'Your scraping performance overview'}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2">
            <option>Last 30 days</option>
            <option>Last 90 days</option>
            <option>Last 6 months</option>
          </select>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Total Jobs',
            value: '1,247',
            change: '+12.5%',
            trend: 'up',
            icon: Activity,
            color: 'blue'
          },
          {
            title: 'Success Rate',
            value: '94.2%',
            change: '+2.1%',
            trend: 'up',
            icon: CheckCircle,
            color: 'green'
          },
          {
            title: 'Avg. Duration',
            value: '4.2m',
            change: '-8.3%',
            trend: 'down',
            icon: Clock,
            color: 'yellow'
          },
          {
            title: 'Data Volume',
            value: '847GB',
            change: '+15.7%',
            trend: 'up',
            icon: Download,
            color: 'purple'
          }
        ].map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg bg-${metric.color}-600/20`}>
                <metric.icon className={`w-6 h-6 text-${metric.color}-400`} />
              </div>
              <div className={`flex items-center space-x-1 text-sm ${
                metric.trend === 'up' ? 'text-green-400' : 'text-red-400'
              }`}>
                <TrendingUp className={`w-4 h-4 ${metric.trend === 'down' ? 'rotate-180' : ''}`} />
                <span>{metric.change}</span>
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-bold dark:text-white text-black mb-1">{metric.value}</h3>
              <p className="text-sm dark:text-gray-400 text-gray-600">{metric.title}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Job Success Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
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
                stroke={animationsEnabled ? "#3B82F6" : "#F59E42"} // blue if enabled, orange if disabled
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="Total Jobs"
              />
              <Line 
                type="monotone" 
                dataKey="success" 
                stroke="#10B981" 
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="Successful"
              />
              <Line 
                type="monotone" 
                dataKey="failed" 
                stroke="#EF4444" 
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="Failed"
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
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Tool Usage Statistics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={toolUsage} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" />
              <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={100} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="usage" fill="#3B82F6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Recent Jobs Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
      >
        <h3 className="text-lg font-semibold dark:text-white text-black mb-4">Recent Jobs</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Tool</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">State</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Duration</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Records</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Started</th>
              </tr>
            </thead>
            <tbody>
              {[
                {
                  tool: 'Gem Portal Scraper',
                  state: 'Delhi',
                  duration: '4m 32s',
                  records: '1,247',
                  status: 'success',
                  started: '2 hours ago'
                },
                {
                  tool: 'Global Trade Monitor',
                  state: 'USA',
                  duration: '12m 15s',
                  records: '3,856',
                  status: 'success',
                  started: '4 hours ago'
                },
                {
                  tool: 'E-Procurement Monitor',
                  state: 'Central Govt',
                  duration: '2m 08s',
                  records: '0',
                  status: 'failed',
                  started: '6 hours ago'
                },
                {
                  tool: 'Market Intelligence',
                  state: 'Europe',
                  duration: '8m 45s',
                  records: '2,134',
                  status: 'success',
                  started: '8 hours ago'
                }
              ].map((job, index) => (
                <tr key={index} className="border-b border-gray-700/50 dark:hover:bg-gray-700/20 hover:bg-gray-100">
                  <td className="py-3 px-4 font-medium dark:text-white text-black">{job.tool}</td>
                  <td className="py-3 px-4 dark:text-gray-300 text-gray-700">{job.state}</td>
                  <td className="py-3 px-4 dark:text-gray-300 text-gray-700">{job.duration}</td>
                  <td className="py-3 px-4 dark:text-gray-300 text-gray-700">{job.records}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      job.status === 'success' 
                        ? 'bg-green-900/50 text-green-400' 
                        : 'bg-red-900/50 text-red-400'
                    }`}>
                      {job.status === 'success' ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : (
                        <AlertTriangle className="w-3 h-3 mr-1" />
                      )}
                      {job.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 dark:text-gray-400 text-gray-600">{job.started}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
};
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
import { supabase } from '../supabaseClient'; // adjust path if needed
import { useAnimation } from '../../contexts/AnimationContext';

const systemData = [
  { name: '00:00', cpu: 45, memory: 62, storage: 78 },
  { name: '04:00', cpu: 52, memory: 58, storage: 79 },
  { name: '08:00', cpu: 68, memory: 71, storage: 80 },
  { name: '12:00', cpu: 82, memory: 85, storage: 82 },
  { name: '16:00', cpu: 76, memory: 79, storage: 83 },
  { name: '20:00', cpu: 61, memory: 65, storage: 84 },
];

export const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<Array<{ id: string; username: string; email: string; isActive: boolean; jobs: number }>>([]);
  const [fetchError, setFetchError] = useState('');
  const { enabled: animationsEnabled } = useAnimation();

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data, error } = await supabase.from('users').select('id, username, email, isActive, jobs');
        if (error) throw error;
        setUsers(data || []);
        setFetchError('');
      } catch (err) {
        setFetchError('Failed to fetch users from database.');
        setUsers([]);
      }
    };
    fetchUsers();
  }, []);

  const fakeUsers = [
    { id: '1', username: 'John Doe', email: 'john@example.com', isActive: true, jobs: 12 },
    { id: '2', username: 'Jane Smith', email: 'jane@example.com', isActive: true, jobs: 8 },
    { id: '3', username: 'Mike Johnson', email: 'mike@example.com', isActive: false, jobs: 5 },
    { id: '4', username: 'Sarah Wilson', email: 'sarah@example.com', isActive: true, jobs: 15 },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold dark:text-white text-black mb-2">Admin Panel</h1>
          <p className="dark:text-gray-400 text-gray-600">System administration and user management</p>
        </div>
        <div className="flex items-center space-x-2 text-green-400">
          <Shield className="w-5 h-5" />
          <span className="text-sm">Admin Access</span>
        </div>
      </motion.div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Active Users',
            value: '24',
            change: '+3 online',
            icon: Users,
            color: 'blue'
          },
          {
            title: 'System Load',
            value: '76%',
            change: 'Normal',
            icon: Server,
            color: 'green'
          },
          {
            title: 'Database Size',
            value: '2.4TB',
            change: '+120GB today',
            icon: Database,
            color: 'purple'
          },
          {
            title: 'Active Jobs',
            value: '12',
            change: '8 queued',
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
          <h3 className="text-lg font-semibold dark:text-white text-black mb-4">System Resources</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={systemData}>
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
                dataKey="cpu" 
                stroke={animationsEnabled ? "#3B82F6" : "#F59E42"} // blue if enabled, orange if disabled
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="CPU %"
              />
              <Line 
                type="monotone" 
                dataKey="memory" 
                stroke={animationsEnabled ? "#10B981" : "#A78BFA"} // green if enabled, purple if disabled
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="Memory %"
              />
              <Line 
                type="monotone" 
                dataKey="storage" 
                stroke={animationsEnabled ? "#F59E0B" : "#6B7280"} // yellow if enabled, gray if disabled
                strokeWidth={2}
                isAnimationActive={animationsEnabled}
                name="Storage %"
              />
            </LineChart>
          </ResponsiveContainer>
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
            {(fetchError ? fakeUsers : users).map((user, index) => (
              <div key={user.id} className="flex items-center justify-between p-3 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user.username.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium dark:text-white text-black">{user.username}</p>
                    <p className="text-xs dark:text-gray-400 text-gray-600">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    user.isActive ? 'bg-green-900/50 text-green-400' : 'bg-gray-900/50 text-gray-400'
                  }`}>
                    {user.isActive ? 'active' : 'inactive'}
                  </span>
                  <span className="text-xs dark:text-gray-400 text-gray-600">{user.jobs || 0} jobs</span>
                </div>
              </div>
            ))}
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

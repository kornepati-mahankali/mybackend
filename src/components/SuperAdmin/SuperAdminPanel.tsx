import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Crown, 
  Users, 
  Database, 
  Server, 
  Shield,
  Settings,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Plus,
  Power,
  RefreshCw
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const systemData = [
  { name: '00:00', cpu: 45, memory: 62, storage: 78, users: 12 },
  { name: '04:00', cpu: 52, memory: 58, storage: 79, users: 8 },
  { name: '08:00', cpu: 68, memory: 71, storage: 80, users: 24 },
  { name: '12:00', cpu: 82, memory: 85, storage: 82, users: 31 },
  { name: '16:00', cpu: 76, memory: 79, storage: 83, users: 28 },
  { name: '20:00', cpu: 61, memory: 65, storage: 84, users: 15 },
];

export const SuperAdminPanel: React.FC = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', label: 'System Overview', icon: Activity },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'tools', label: 'Tool Management', icon: Database },
    { id: 'system', label: 'System Control', icon: Server },
    { id: 'security', label: 'Security Center', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 sm:gap-0"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-yellow-600 to-orange-600 rounded-lg">
            <Crown className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-2xl font-bold text-white mb-2">Super Admin Control Center</h1>
            <p className="text-gray-400 text-base sm:text-sm">Complete system administration and control</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-yellow-400 mt-2 sm:mt-0">
          <Crown className="w-5 h-5" />
          <span className="text-sm font-medium">Super Admin Access</span>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-gray-800 p-1 rounded-xl border border-gray-700">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                activeSection === section.id
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{section.label}</span>
            </button>
          );
        })}
      </div>

      {/* System Overview */}
      {activeSection === 'overview' && (
        <div className="space-y-6">
          {/* Critical System Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Total Users',
                value: '1,247',
                change: '+12 today',
                icon: Users,
                color: 'blue',
                status: 'normal'
              },
              {
                title: 'System Load',
                value: '76%',
                change: 'High load',
                icon: Server,
                color: 'orange',
                status: 'warning'
              },
              {
                title: 'Active Jobs',
                value: '24',
                change: '8 queued',
                icon: Activity,
                color: 'green',
                status: 'normal'
              },
              {
                title: 'Security Status',
                value: 'Secure',
                change: 'All systems OK',
                icon: Shield,
                color: 'green',
                status: 'normal'
              }
            ].map((metric, index) => (
              <motion.div
                key={metric.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-800 rounded-xl p-6 border border-gray-700"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-2 rounded-lg bg-${metric.color}-600/20`}>
                    <metric.icon className={`w-6 h-6 text-${metric.color}-400`} />
                  </div>
                  <div className={`w-2 h-2 rounded-full ${
                    metric.status === 'warning' ? 'bg-yellow-400' : 'bg-green-400'
                  } animate-pulse`}></div>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-1">{metric.value}</h3>
                  <p className="text-sm text-gray-400 mb-2">{metric.title}</p>
                  <p className={`text-xs ${
                    metric.status === 'warning' ? 'text-yellow-400' : 'text-green-400'
                  }`}>{metric.change}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* System Performance Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gray-800 rounded-xl p-6 border border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">System Performance (24h)</h3>
              <button className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200">
                <RefreshCw className="w-4 h-4 text-white" />
              </button>
            </div>
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
                <Line type="monotone" dataKey="cpu" stroke="#EF4444" strokeWidth={2} name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#F59E0B" strokeWidth={2} name="Memory %" />
                <Line type="monotone" dataKey="storage" stroke="#8B5CF6" strokeWidth={2} name="Storage %" />
                <Line type="monotone" dataKey="users" stroke="#10B981" strokeWidth={2} name="Active Users" />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        </div>
      )}

      {/* User Management */}
      {activeSection === 'users' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">User Management</h3>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 px-4 py-2 sm:px-3 sm:py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-200 text-base sm:text-sm"
            >
              <Plus className="w-4 h-4 text-white" />
              <span className="text-white">Add User</span>
            </motion.button>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="overflow-x-auto">
              <table className="w-full text-sm sm:text-xs">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">User</th>
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">Role</th>
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">Status</th>
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">Last Login</th>
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">Jobs</th>
                    <th className="text-left py-3 px-2 sm:px-4 text-gray-400 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { name: 'John Doe', email: 'john@example.com', role: 'user', status: 'active', lastLogin: '2 hours ago', jobs: 12 },
                    { name: 'Jane Smith', email: 'jane@example.com', role: 'admin', status: 'active', lastLogin: '1 hour ago', jobs: 8 },
                    { name: 'Mike Johnson', email: 'mike@example.com', role: 'user', status: 'inactive', lastLogin: '2 days ago', jobs: 5 },
                    { name: 'Sarah Wilson', email: 'sarah@example.com', role: 'user', status: 'active', lastLogin: '30 min ago', jobs: 15 }
                  ].map((user, index) => (
                    <tr key={user.email} className="border-b border-gray-700/50 hover:bg-gray-700/20">
                      <td className="py-3 px-2 sm:px-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-white">
                              {user.name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white">{user.name}</p>
                            <p className="text-xs text-gray-400">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-2 sm:px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.role === 'admin' 
                            ? 'bg-blue-900/50 text-blue-400' 
                            : 'bg-gray-900/50 text-gray-400'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="py-3 px-2 sm:px-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          user.status === 'active' 
                            ? 'bg-green-900/50 text-green-400' 
                            : 'bg-red-900/50 text-red-400'
                        }`}>
                          {user.status === 'active' ? (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          ) : (
                            <XCircle className="w-3 h-3 mr-1" />
                          )}
                          {user.status}
                        </span>
                      </td>
                      <td className="py-3 px-2 sm:px-4 text-gray-300">{user.lastLogin}</td>
                      <td className="py-3 px-2 sm:px-4 text-gray-300">{user.jobs}</td>
                      <td className="py-3 px-2 sm:px-4">
                        <div className="flex items-center space-x-2">
                          <button className="p-1 bg-blue-600 hover:bg-blue-700 rounded text-white">
                            <Edit className="w-3 h-3" />
                          </button>
                          <button className="p-1 bg-red-600 hover:bg-red-700 rounded text-white">
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* System Control */}
      {activeSection === 'system' && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-white">System Control</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">System Services</h4>
              <div className="space-y-3">
                {[
                  { name: 'API Server', status: 'running', port: '3001' },
                  { name: 'Database', status: 'running', port: '5432' },
                  { name: 'Redis Queue', status: 'running', port: '6379' },
                  { name: 'WebSocket Server', status: 'running', port: '3002' }
                ].map((service) => (
                  <div key={service.name} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <div>
                        <p className="text-sm font-medium text-white">{service.name}</p>
                        <p className="text-xs text-gray-400">Port: {service.port}</p>
                      </div>
                    </div>
                    <button className="p-1 bg-red-600 hover:bg-red-700 rounded text-white">
                      <Power className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">System Actions</h4>
              <div className="space-y-3">
                <button className="w-full flex items-center justify-center space-x-2 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200">
                  <RefreshCw className="w-4 h-4 text-white" />
                  <span className="text-white">Restart All Services</span>
                </button>
                <button className="w-full flex items-center justify-center space-x-2 p-3 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition-colors duration-200">
                  <Database className="w-4 h-4 text-white" />
                  <span className="text-white">Backup Database</span>
                </button>
                <button className="w-full flex items-center justify-center space-x-2 p-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors duration-200">
                  <Settings className="w-4 h-4 text-white" />
                  <span className="text-white">System Maintenance</span>
                </button>
                <button className="w-full flex items-center justify-center space-x-2 p-3 bg-red-600 hover:bg-red-700 rounded-lg transition-colors duration-200">
                  <Power className="w-4 h-4 text-white" />
                  <span className="text-white">Emergency Shutdown</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
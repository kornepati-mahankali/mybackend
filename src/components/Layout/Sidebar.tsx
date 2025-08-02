import React from 'react';
import { motion } from 'framer-motion';
import { 
  Home, 
  Gem, 
  Globe, 
  Layers, 
  ShoppingCart, 
  BarChart3, 
  Settings, 
  LogOut,
  Shield,
  Crown,
  Users,
  Database,
  ChevronDown,
  Play,
  X
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useState } from 'react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, sidebarOpen = false, setSidebarOpen }) => {
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'gem-tools', label: 'Gem Tools', icon: Gem },
    { id: 'global-tools', label: 'Global Tools', icon: Globe },
    { id: 'all-tools', label: 'All Tools', icon: Layers },
    { id: 'eprocurement-tools', label: 'E-Procurement', icon: ShoppingCart },
    { id: 'performance', label: 'Performance', icon: BarChart3 },
    { id: 'ireps', label: 'IREPS', icon: Layers },
    ...(user?.role === 'admin' ? [{ id: 'admin', label: 'Admin Panel', icon: Shield }] : []),
    ...(user?.role === 'super_admin' ? [
      { id: 'admin', label: 'Admin Panel', icon: Shield },
      { id: 'super-admin', label: 'Super Admin', icon: Crown },
      { id: 'user-management', label: 'User Management', icon: Users },
      { id: 'system-control', label: 'System Control', icon: Database }
    ] : []),
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'text-yellow-400';
      case 'admin':
        return 'text-blue-400';
      default:
        return 'text-green-400';
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin':
        return Crown;
      case 'admin':
        return Shield;
      default:
        return Users;
    }
  };

  const RoleIcon = getRoleIcon(user?.role || 'user');

  // Sidebar classes for responsive behavior
  const sidebarBase = "fixed left-0 top-0 h-full w-64 dark:bg-gray-800 dark:border-gray-700 bg-white border-r border-gray-200 z-50 transition-transform duration-300";
  const sidebarMobile = sidebarOpen ? "translate-x-0" : "-translate-x-full";
  // On mobile/tablet: show/hide with translate-x, on md+ always visible
  const sidebarClass = `${sidebarBase} ${sidebarMobile} md:translate-x-0 md:block`;

  return (
    <div className={sidebarClass}>
      {/* Close button for mobile */}
      <div className="md:hidden flex justify-end p-2">
        <button
          onClick={() => setSidebarOpen && setSidebarOpen(false)}
          className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
          aria-label="Close sidebar"
        >
          <X className="w-6 h-6" />
        </button>
      </div>
      <div className="p-6 md:p-6 sm:p-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center space-x-3 mb-8 sm:mb-4"
        >
          <div className="w-10 h-10 sm:w-8 sm:h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Globe className="w-6 h-6 sm:w-5 sm:h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl sm:text-lg font-bold dark:text-white text-black">Super Scraper</h1>
            <p className="text-sm sm:text-xs dark:text-gray-400 text-gray-600">Pro Dashboard v3.0</p>
          </div>
        </motion.div>

        <div className="mb-6 sm:mb-4">
          <div className="flex items-center space-x-3 p-3 sm:p-2 rounded-lg dark:bg-gray-700 bg-gray-100 border dark:border-gray-600 border-gray-200">
            <div className="w-8 h-8 sm:w-7 sm:h-7 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-white">
                {user?.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm sm:text-xs font-medium dark:text-white text-black">{user?.username}</p>
              <div className="flex items-center space-x-1">
                <RoleIcon className={`w-3 h-3 sm:w-2.5 sm:h-2.5 ${getRoleColor(user?.role || 'user')}`} />
                <p className={`text-xs sm:text-[10px] capitalize ${getRoleColor(user?.role || 'user')}`}>{user?.role?.replace('_', ' ')}</p>
              </div>
            </div>
          </div>
        </div>

        <nav className="space-y-3 sm:space-y-2 md:space-y-1">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <motion.button
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onTabChange(item.id);
                  // Removed immediate sidebar close - let setActiveTab handle it with proper timing
                }}
                className={`w-full flex items-center space-x-3 px-3 py-2 sm:px-2 sm:py-1 rounded-lg transition-all duration-200 text-left ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'dark:text-gray-300 text-gray-700 dark:hover:bg-gray-700 hover:bg-gray-100 dark:hover:text-white hover:text-black'
                }`}
              >
                <Icon className="w-5 h-5 sm:w-4 sm:h-4" />
                <span className="text-sm sm:text-xs font-medium">{item.label}</span>
                {item.id === 'super-admin' && (
                  <Crown className="w-4 h-4 sm:w-3 sm:h-3 text-yellow-400 ml-auto" />
                )}
              </motion.button>
            );
          })}
        </nav>
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-3 mt-8 border-t border-gray-700/40 dark:border-gray-600/40">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={logout}
          className="w-full flex items-center space-x-3 px-3 py-2 sm:px-2 sm:py-1 rounded-lg transition-all duration-200 dark:text-gray-300 text-gray-700 dark:hover:bg-red-600 hover:bg-red-100 dark:hover:text-white hover:text-black"
        >
          <LogOut className="w-5 h-5 sm:w-4 sm:h-4" />
          <span className="text-sm sm:text-xs font-medium">Sign Out</span>
        </motion.button>
      </div>
    </div>
  );
};
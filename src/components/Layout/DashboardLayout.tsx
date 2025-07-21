import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { DashboardHome } from '../Dashboard/DashboardHome';
import { ToolsGrid } from '../Tools/ToolsGrid';
import { PerformanceView } from '../Performance/PerformanceView';
import { AdminPanel } from '../Admin/AdminPanel';
import { SuperAdminPanel } from '../SuperAdmin/SuperAdminPanel';
import { SettingsView } from '../Settings/SettingsView';
import { ToolInterface } from '../Tools/ToolInterface';
import { Tool } from '../../types';
import { useSelectedTool } from '../../contexts/SelectedToolContext';

export const DashboardLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { selectedTool, setSelectedTool } = useSelectedTool();

  const renderContent = () => {
    if (selectedTool) {
      return <ToolInterface tool={selectedTool} onBack={() => setSelectedTool(null)} />;
    }
    switch (activeTab) {
      case 'dashboard':
        return <DashboardHome />;
      case 'gem-tools':
        return <ToolsGrid category="gem-tools" title="Gem Tools" setSelectedTool={setSelectedTool} />;
      case 'global-tools':
        return <ToolsGrid category="global-tools" title="Global Tools" setSelectedTool={setSelectedTool} />;
      case 'all-tools':
        return <ToolsGrid category="all-tools" title="All Tools" setSelectedTool={setSelectedTool} />;
      case 'eprocurement-tools':
        return <ToolsGrid category="eprocurement-tools" title="E-Procurement Tools" setSelectedTool={setSelectedTool} />;
      case 'performance':
        return <PerformanceView />;
      case 'admin':
        return <AdminPanel />;
      case 'super-admin':
      case 'user-management':
      case 'system-control':
        return <SuperAdminPanel />;
      case 'settings':
        return <SettingsView />;
      default:
        return <DashboardHome />;
    }
  };

  return (
    <div className="min-h-screen bg-white text-black dark:bg-gray-900 dark:text-white">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="ml-64 min-h-screen">
        <motion.main
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="p-8"
        >
          {renderContent()}
        </motion.main>
      </div>
      {/* Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 35,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"
        />
      </div>
    </div>
  );
};
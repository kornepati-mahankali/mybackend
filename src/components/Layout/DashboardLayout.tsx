// @ts-nocheck
import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { DashboardHome } from '../Dashboard/DashboardHome';
import { ToolsGrid } from '../Tools/ToolsGrid';
import { PerformanceView } from '../Performance/PerformanceView';
import { AdminPanel } from '../Admin/AdminPanel';
import { SuperAdminPanel } from '../SuperAdmin/SuperAdminPanel';
import { SettingsView } from '../Settings/SettingsView';
import { ToolInterface } from '../Tools/ToolInterface';
import { useSelectedTool } from '../../contexts/SelectedToolContext';
import { Menu } from 'lucide-react';

export const DashboardLayout: React.FC = () => {
  const [activeTab, _setActiveTab] = useState('dashboard');
  const { selectedTool, setSelectedTool } = useSelectedTool();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Debug effect to monitor activeTab changes - removed to clean up console
      







  // Helper to set tab and clear selected tool
  const setActiveTab = (tab: string) => {
    // Only update if the tab is actually different
    if (activeTab === tab) {
      return;
    }
    
    setSelectedTool(null); // Clear selected tool when switching tabs
    
    // Set the new tab
    _setActiveTab(tab);
    
    if (window.innerWidth < 768) {
      setTimeout(() => {
        setSidebarOpen(false); // Close sidebar after a short delay
      }, 150); // Increased delay to ensure state update completes
    }
  };

  // Memoized renderContent to prevent unnecessary re-renders
  const renderContent = useMemo(() => {
    // Removed debug log to reduce console spam
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
      case 'ireps':
        return <ToolsGrid category="ireps-tools" title="IREPS Tools" setSelectedTool={setSelectedTool} />;
      default:
        return <DashboardHome />;
    }
  }, [activeTab, selectedTool, setSelectedTool]);

  return (
    <div className="min-h-screen bg-white text-black dark:bg-gray-900 dark:text-white relative overflow-x-hidden flex flex-col md:flex-row">
      {/* Mobile/Tablet Header Bar */}
      <div className="md:hidden flex items-center bg-black dark:bg-gray-900 text-white px-6 py-3 w-full z-40">
        <button
          className="mr-4 focus:outline-none"
          onClick={() => setSidebarOpen(true)}
          aria-label="Open sidebar"
        >
          <Menu className="w-7 h-7" />
        </button>
        <span className="font-bold text-lg">Super Scraper</span>
      </div>
      {/* Sidebar: pass open state and toggle */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <div className="flex-1 min-h-screen md:ml-64 transition-all duration-300 px-4 md:px-8 pt-8">
        <main className="main-content w-full max-w-7xl mx-auto" key={activeTab}>
          {renderContent}
        </main>
      </div>
      {/* Background Elements - Memoized to prevent re-renders */}
      {useMemo(() => (
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
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
      ), [])}
    </div>
  );
};
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  Zap,
  Shield,
  BarChart3,
  Users,
  FileText,
  ArrowRight,
  Play,
  CheckCircle,
  TrendingUp,
  Globe,
  Lock,
  Crown,
  Settings,
  Bot
} from 'lucide-react';
import { AIAssistant } from './AIAssistant';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const features = [
    {
      icon: <Database className="w-8 h-8" />,
      title: "Advanced Data Scraping",
      description: "Powerful web scraping tools for extracting data from multiple sources with high accuracy and speed."
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Real-time Processing",
      description: "Process large datasets in real-time with our optimized scraping engines and parallel processing."
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Secure & Reliable",
      description: "Enterprise-grade security with encrypted data transmission and secure storage protocols."
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Analytics Dashboard",
      description: "Comprehensive analytics and reporting tools to track performance and monitor scraping activities."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Multi-user Support",
      description: "Role-based access control with admin and super admin capabilities for team management."
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Export & Integration",
      description: "Export data in multiple formats and integrate with your existing systems seamlessly."
    }
  ];



  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex flex-col overflow-x-hidden w-full max-w-full">
        {/* Navigation */}
        <nav className="flex flex-col sm:flex-row justify-between items-center px-4 sm:px-8 py-4 sm:py-6 gap-2 sm:gap-0 w-full max-w-full">
          <div className="flex items-center space-x-3">
            <Database className="w-8 h-8 text-white" />
            <span className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold text-white">ScraperPro</span>
          </div>
          <button
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 sm:px-4 sm:py-2 rounded-lg font-semibold transition-all duration-200 text-base sm:text-sm"
            onClick={() => window.location.href = '/auth'}
          >
            Login
          </button>
        </nav>

        {/* Hero Section */}
        <section className="flex-1 flex flex-col items-center justify-center text-center px-2 sm:px-4 relative w-full max-w-full">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-xl sm:text-2xl md:text-4xl lg:text-5xl xl:text-7xl font-bold text-white mb-6 break-words">
              Super Scraper
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Dashboard</span>
            </h1>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto break-words">
              The ultimate web scraping platform with advanced analytics, real-time processing, and enterprise-grade security for your data extraction needs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8 w-full max-w-full">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.href = '/auth'}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white w-auto max-w-xs mx-auto block px-4 py-2 sm:px-6 sm:py-3 rounded-lg font-semibold text-sm sm:text-base md:text-lg transition-all duration-200 flex items-center justify-center space-x-2 mb-3 sm:mb-0 cursor-pointer z-10 relative"
              >
                <Play className="w-5 h-5 sm:w-4 sm:h-4" />
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5 sm:w-4 sm:h-4" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowAIAssistant(true)}
                className="border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 w-auto max-w-xs mx-auto block px-4 py-2 sm:px-6 sm:py-3 rounded-lg font-semibold text-sm sm:text-base md:text-lg transition-all duration-200 flex items-center justify-center space-x-2 cursor-pointer"
              >
                <CheckCircle className="w-5 h-5 sm:w-4 sm:h-4" />
                <span>AI Assistant</span>
              </motion.button>
            </div>
          </motion.div>
          {/* Animated background elements */}
          <motion.div
            animate={{ x: [0, 100, 0], y: [0, -100, 0] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute top-1/4 left-1/4 w-72 h-72 sm:w-96 sm:h-96 bg-blue-500/10 rounded-full blur-3xl"
          />
          <motion.div
            animate={{ x: [0, -100, 0], y: [0, 100, 0] }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-1/4 right-1/4 w-60 h-60 sm:w-80 sm:h-80 bg-purple-500/10 rounded-full blur-3xl"
          />
        </section>

        {/* Features Grid */}
        <section className="max-w-6xl mx-auto py-12 sm:py-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-6 px-2 sm:px-4 w-full max-w-full">
          {features.map((feature, idx) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              whileHover={{ y: -5, scale: 1.03 }}
              className="bg-gray-800/60 rounded-xl p-8 sm:p-6 flex flex-col items-center text-center hover:shadow-2xl transition w-full max-w-full"
            >
              <div className="w-16 h-16 sm:w-12 sm:h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-sm sm:text-base md:text-lg lg:text-xl font-semibold text-white mb-2 break-words">{feature.title}</h3>
              <p className="text-gray-400 text-xs sm:text-sm md:text-base break-words">{feature.description}</p>
            </motion.div>
          ))}
        </section>
      </div>
      
                   {/* AI Assistant Floating Button/Modal - Positioned outside main content */}
      <AIAssistant isOpen={showAIAssistant} onToggle={() => setShowAIAssistant((v) => !v)} variant="homepage" />
      
      {/* Floating AI Assistant Logo Button - Bottom Right Corner */}
      <motion.button
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setShowAIAssistant(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center z-40 group"
      >
        <div className="relative">
          <Bot className="w-8 h-8 text-white" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        </div>
        {/* Tooltip */}
        <div className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
          AI Assistant
          <div className="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-gray-900 border-t-4 border-t-transparent border-b-4 border-b-transparent"></div>
        </div>
      </motion.button>
     </>
   );
 }; 
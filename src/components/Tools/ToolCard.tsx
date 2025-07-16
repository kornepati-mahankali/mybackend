import React from 'react';
import { motion } from 'framer-motion';
import { 
  Gem, 
  Globe, 
  Download, 
  Layers, 
  ShoppingCart, 
  Target,
  BarChart3,
  Play
} from 'lucide-react';
import { Tool } from '../../types';

interface ToolCardProps {
  tool: Tool;
  onSelect: (tool: Tool) => void;
}

const iconMap = {
  gem: Gem,
  globe: Globe,
  download: Download,
  layers: Layers,
  'shopping-cart': ShoppingCart,
  target: Target,
  chart: BarChart3,
  analyze: BarChart3
};

export const ToolCard: React.FC<ToolCardProps> = ({ tool, onSelect }) => {
  const IconComponent = iconMap[tool.icon as keyof typeof iconMap] || Play;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, y: -5 }}
      transition={{ duration: 0.3 }}
      className="bg-transparent dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:border-blue-500 cursor-pointer group shadow-none dark:shadow-md"
      onClick={() => onSelect(tool)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-blue-600/20 rounded-lg group-hover:bg-blue-600/30 transition-colors duration-200">
          <IconComponent className="w-6 h-6 text-blue-400" />
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          <span className="text-xs text-green-400">Active</span>
        </div>
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-400 transition-colors duration-200">
        {tool.name}
      </h3>
      
      <p className="text-sm text-gray-700 dark:text-gray-400 mb-4 line-clamp-2">
        {tool.description}
      </p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">States:</span>
          <span className="text-xs text-blue-400 font-medium">{tool.valid_states?.length ?? 0}</span>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200"
        >
          <Play className="w-4 h-4 text-white" />
        </motion.button>
      </div>
    </motion.div>
  );
};
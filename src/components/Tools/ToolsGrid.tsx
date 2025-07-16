// import React, { useState } from 'react';
// import { motion } from 'framer-motion';
// import { ToolCard } from './ToolCard';
// import { ToolInterface } from './ToolInterface';
// import { Tool } from '../../types';
// import { tools } from '../../data/tools';

// interface ToolsGridProps {
//   category: string;
//   title: string;
// }

// export const ToolsGrid: React.FC<ToolsGridProps> = ({ category, title }) => {
//   const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  
//   const categoryMap: Record<string, string> = {
//     'gem-tools': 'gem',
//     'global-tools': 'global',
//     'all-tools': 'all',
//     'eprocurement-tools': 'eprocurement'
//   };

//   const filteredTools = tools.filter(tool => tool.category === categoryMap[category]);

//   if (selectedTool) {
//     return <ToolInterface tool={selectedTool} onBack={() => setSelectedTool(null)} />;
//   }

//   return (
//     <div className="space-y-6">
//       <motion.div
//         initial={{ opacity: 0, y: 20 }}
//         animate={{ opacity: 1, y: 0 }}
//       >
//         <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
//         <p className="text-gray-400">
//           Select a tool to configure and start your scraping operation
//         </p>
//       </motion.div>

//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//         {filteredTools.map((tool, index) => (
//           <motion.div
//             key={tool.id}
//             initial={{ opacity: 0, y: 20 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ delay: index * 0.1 }}
//           >
//             <ToolCard tool={tool} onSelect={setSelectedTool} />
//           </motion.div>
//         ))}
//       </div>

//       {filteredTools.length === 0 && (
//         <motion.div
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           className="text-center py-12"
//         >
//           <p className="text-gray-400 text-lg">No tools available in this category yet.</p>
//           <p className="text-gray-500 text-sm mt-2">Check back later for new tools!</p>
//         </motion.div>
//       )}
//     </div>
//   );
// };



// 🚧 We'll modernize and connect the frontend dynamically to the backend
// Changes:
// - Replace static import of `tools` with API call
// - Move tool fetching logic to `useEffect`
// - Add loading/error handling
// - Still preserves styling + transitions

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ToolCard } from './ToolCard';
import { ToolInterface } from './ToolInterface';
import { Tool } from '../../types';

interface ToolsGridProps {
  category: string;
  title: string;
}

export const ToolsGrid: React.FC<ToolsGridProps> = ({ category, title }) => {
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const res = await fetch('http://localhost:8000/scrapers');
        const data = await res.json();
        setTools(data.tools);
      } catch (err) {
        setError('Failed to load tools.');
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, []);

  const categoryMap: Record<string, string> = {
    'gem-tools': 'gem',
    'global-tools': 'global',
    'all-tools': 'all',
    'eprocurement-tools': 'eprocurement'
  };

  const filteredTools = tools.filter(tool => tool.category === categoryMap[category] || category === 'all-tools');

  if (selectedTool) {
    return <ToolInterface tool={selectedTool} onBack={() => setSelectedTool(null)} />;
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{title}</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Select a tool to configure and start your scraping operation
        </p>
      </motion.div>

      {loading ? (
        <div className="text-gray-400 text-center py-12">Loading tools...</div>
      ) : error ? (
        <div className="text-red-500 text-center py-12">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTools.map((tool, index) => (
            <motion.div
              key={tool.id || tool.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <ToolCard tool={tool} onSelect={setSelectedTool} />
            </motion.div>
          ))}
          {/* Static E-Procurement Tool card if no tools available */}
          {filteredTools.length === 0 && category === 'eprocurement-tools' && (
            <div
              className="bg-zinc-900 rounded-xl p-6 border border-gray-700 shadow-md w-full max-w-md mx-auto flex flex-col justify-between cursor-pointer hover:border-blue-500"
              onClick={() => setSelectedTool({
                name: 'eprocurement',
                category: 'eprocurement',
                icon: 'shopping-cart',
                script_path: 'scrapers/search.py',
                description: 'Scrapes data from the E-Procurement website and generates Excel files for each page.',
                inputs: [
                  { name: 'base_url', type: 'string', required: true, description: 'Base URL for scraping' },
                  { name: 'tender_type', type: 'string', required: true, description: 'Tender type (O/L)' },
                  { name: 'days_interval', type: 'int', required: true, description: 'How many days back to scrape' },
                  { name: 'start_page', type: 'int', required: true, description: 'Starting page number' }
                ]
              })}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-600/20 rounded-lg">
                  <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 6h15l-1.5 9h-13z"/><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/></svg>
                </div>
                <span className="text-xs text-green-400">Inactive</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">E-Procurement Tool</h3>
              <p className="text-sm text-gray-400 mb-4">
                Scrapes data from the E-Procurement website and generates Excel files for each page.
              </p>
              <button className="px-4 py-2 rounded-md text-white bg-violet-600 hover:bg-violet-700 w-full mt-2 pointer-events-none">
                Add Tool / Upload
              </button>
            </div>
          )}
        </div>
      )}
      {!loading && filteredTools.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <p className="text-gray-400 text-lg">No tools available in this category yet.</p>
          <p className="text-gray-500 text-sm mt-2">Check back later for new tools!</p>
        </motion.div>
      )}
    </div>
  );
};

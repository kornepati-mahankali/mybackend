import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Tool } from '../types';

interface SelectedToolContextType {
  selectedTool: Tool | null;
  setSelectedTool: React.Dispatch<React.SetStateAction<Tool | null>>;
}

const SelectedToolContext = createContext<SelectedToolContextType | undefined>(undefined);

export const SelectedToolProvider = ({ children }: { children: ReactNode }) => {
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  return (
    <SelectedToolContext.Provider value={{ selectedTool, setSelectedTool }}>
      {children}
    </SelectedToolContext.Provider>
  );
};

export const useSelectedTool = () => {
  const context = useContext(SelectedToolContext);
  if (!context) {
    throw new Error('useSelectedTool must be used within a SelectedToolProvider');
  }
  return context;
}; 
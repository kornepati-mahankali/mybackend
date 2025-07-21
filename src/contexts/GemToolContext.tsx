import React, { createContext, useContext, useState, ReactNode } from "react";
import { type Socket } from 'socket.io-client';

// Define the shape of the Gem Tool state
export type GemToolState = {
  inputValues: { [key: string]: string };
  selectedState: string;
  selectedCity: string;
  log: string;
  isRunning: boolean;
  runId: string | null;
  outputFiles: string[];
  isScrapingComplete: boolean;
  isStopping: boolean;
  stopMessage: string;
  scrapingJobs: { state: string, status: 'in-progress' | 'complete' }[];
  activeJobState: string | null;
  jobData: Record<string, {
    inputValues: { [key: string]: string },
    selectedCity: string,
    log: string,
    isRunning: boolean,
    isScrapingComplete: boolean,
    runId: string | null,
    outputFiles: string[],
    stopMessage: string
  }>;
  socket: any | null;
};

export type GemToolContextType = {
  state: GemToolState;
  setState: React.Dispatch<React.SetStateAction<GemToolState>>;
};

const defaultState: GemToolState = {
  inputValues: {},
  selectedState: '',
  selectedCity: '',
  log: '',
  isRunning: false,
  runId: null,
  outputFiles: [],
  isScrapingComplete: false,
  isStopping: false,
  stopMessage: '',
  scrapingJobs: [],
  activeJobState: null,
  jobData: {},
  socket: null,
};

const GemToolContext = createContext<GemToolContextType | undefined>(undefined);

export const GemToolProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<GemToolState>(defaultState);
  return (
    <GemToolContext.Provider value={{ state, setState }}>
      {children}
    </GemToolContext.Provider>
  );
};

export const useGemTool = () => {
  const context = useContext(GemToolContext);
  if (!context) {
    throw new Error("useGemTool must be used within a GemToolProvider");
  }
  return context;
}; 
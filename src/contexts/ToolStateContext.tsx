import React, { createContext, useContext, useState, ReactNode } from "react";

// E-Procurement Tool State
export type EProcJob = {
  session_id: string;
  params: any;
  logs: string[];
  status: 'running' | 'completed' | 'failed';
  form: any;
  files?: any[];
  filesLoading?: boolean;
};
export type EProcForm = {
  base_url: string;
  tender_type: string;
  days_interval: number;
  start_page: number;
  captcha: string;
};

export type EProcurementState = {
  forms: EProcForm[];
  jobs: EProcJob[];
  selectedSession: string | null;
};

// Gem Tool State (reuse from GemToolContext)
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

export type ToolState = {
  eprocurement: EProcurementState;
  gem: GemToolState;
};

const defaultEProcurementState: EProcurementState = {
  forms: [
    {
      base_url: "",
      tender_type: "",
      days_interval: 1,
      start_page: 1,
      captcha: ""
    }
  ],
  jobs: [],
  selectedSession: null,
};

const defaultGemState: GemToolState = {
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

const defaultState: ToolState = {
  eprocurement: defaultEProcurementState,
  gem: defaultGemState,
};

const ToolStateContext = createContext<{
  state: ToolState;
  setState: React.Dispatch<React.SetStateAction<ToolState>>;
}>({
  state: defaultState,
  setState: () => {},
});

export const useToolState = () => useContext(ToolStateContext);

export const ToolStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<ToolState>(defaultState);
  return (
    <ToolStateContext.Provider value={{ state, setState }}>
      {children}
    </ToolStateContext.Provider>
  );
}; 
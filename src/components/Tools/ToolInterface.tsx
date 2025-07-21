import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Play, Square, Download, Trash2, FileText, Merge } from 'lucide-react';
import { Tool } from '../../types';
import io, { Socket } from 'socket.io-client';
import { useGemTool } from '../../contexts/GemToolContext';
import LiveLogViewer from './LiveLogViewer';

async function fetchFileSize(url: string): Promise<string> {
  try {
    const res = await fetch(url, { method: 'HEAD' });
    if (res.ok) {
      const size = res.headers.get('content-length');
      if (size) {
        const kb = Math.round(Number(size) / 1024);
        return `${kb} KB`;
      }
    }
  } catch {}
  return '';
}

interface ToolInterfaceProps {
  tool: Tool;
  onBack: () => void;
}



export const ToolInterface: React.FC<ToolInterfaceProps> = ({ tool, onBack }) => {
  // Use context for Gem Tool state
  const { state, setState } = useGemTool();

  // For Gem Tool, use context state; for others, use local state
  const [showCaptchaReminder, setShowCaptchaReminder] = useState(false);
  const [eStep, setEStep] = useState<'start' | 'captcha'>('start');

  // Add scrapingJobs state
  const [scrapingJobs, setScrapingJobs] = useState<{ state: string, status: 'in-progress' | 'complete' }[]>([]);
  // Add activeJobState and per-job data
  const [activeJobState, setActiveJobState] = useState<string | null>(null);
  const [jobData, setJobData] = useState<Record<string, {
    inputValues: { [key: string]: string },
    selectedCity: string,
    log: string,
    isRunning: boolean,
    isScrapingComplete: boolean,
    runId: string | null,
    outputFiles: string[],
    stopMessage: string
  }>>({});

  // Add validStates array at the top (should match backend order)
  const validStates = [
    "ANDAMAN & NICOBAR",
    "ANDHRA PRADESH",
    "ARUNACHAL PRADESH",
    "ASSAM",
    "BIHAR",
    "CHANDIGARH",
    "CHHATTISGARH",
    "DADRA & NAGAR HAVELI",
    "DAMAN & DIU",
    "DELHI",
    "GOA",
    "GUJARAT",
    "HARYANA",
    "HIMACHAL PRADESH",
    "JAMMU & KASHMIR",
    "JHARKHAND",
    "KARNATAKA",
    "KERALA",
    "LAKSHADWEEP",
    "MADHYA PRADESH",
    "MAHARASHTRA",
    "MANIPUR",
    "MEGHALAYA",
    "MIZORAM",
    "NAGALAND",
    "ODISHA",
    "PUDUCHERRY",
    "PUNJAB",
    "RAJASTHAN",
    "SIKKIM",
    "TAMIL NADU",
    "TELANGANA",
    "TRIPURA",
    "UTTAR PRADESH",
    "UTTARAKHAND",
    "WEST BENGAL"
  ];

  // E-Procurement specific state (updated)
  const [eBaseUrl, setEBaseUrl] = useState('');
  const [eTenderType, setETenderType] = useState('');
  const [eDaysInterval, setEDaysInterval] = useState('');
  const [eStartPage, setEStartPage] = useState('');
  const [eCaptcha, setECaptcha] = useState('');
  const [eIsRunning, setEIsRunning] = useState(false);
  const [eScrapingStarted, setEScrapingStarted] = useState(false);
  const [eError, setEError] = useState('');
  const [eSuccess, setESuccess] = useState('');
  const [edgeOpened, setEdgeOpened] = useState(false);
  const [eOutputFiles, setEOutputFiles] = useState<string[]>([]);
  const [eCurrentSessionId, setECurrentSessionId] = useState<string | null>(null);

  // WebSocket connection for E-Procurement
  const [eSocket, setESocket] = useState<any>(null);

  // Backend configuration
  const BACKEND_URL = 'http://localhost:5021';
  const WS_URL = 'ws://localhost:5021';

  useEffect(() => {
    if (tool.inputs) {
      const initialInputs: { [key: string]: string } = {};
      tool.inputs.forEach(input => {
        initialInputs[input.name] = input.default ? String(input.default) : '';
      });
      setState(prev => ({ ...prev, inputValues: initialInputs }));
    }
  }, [tool, setState]);

  // Add WebSocket event listener for instant output file updates
  useEffect(() => {
    if (state.socket) {
      const handleFileWritten = (data: { filename: string, run_id: string }) => {
        setState(prev => ({
          ...prev,
          outputFiles: prev.outputFiles && !prev.outputFiles.includes(data.filename)
            ? [...prev.outputFiles, data.filename]
            : prev.outputFiles || []
        }));
      };
      state.socket.on('file_written', handleFileWritten);
      return () => {
        state.socket.off('file_written', handleFileWritten);
      };
    }
  }, [state.socket, setState]);

  // Replace all useState for Gem Tool with context state
  // Example: state.inputValues, state.selectedState, etc.
  // Replace setInputValues, setSelectedState, etc. with setState updater

  // Example for input change:
  const handleInputChange = (name: string, value: string) => {
    setState(prev => ({ ...prev, inputValues: { ...prev.inputValues, [name]: value } }));
  };

  // Example for state selection:
  // setState(prev => ({ ...prev, selectedState: value }));

  // Example for log update:
  // setState(prev => ({ ...prev, log: prev.log + newLog }));

  // Example for output files:
  // setState(prev => ({ ...prev, outputFiles: [...prev.outputFiles, file] }));

  // All other Gem Tool state (isRunning, runId, etc.) should use context

  const handleStart = () => {
    const isGem = tool.name === 'gem';
    console.log('inputValues:', state.inputValues);
    console.log('selectedState:', state.selectedState);
    // Only check required fields, city/city_input and state_index are optional/handled separately
    const missingFields: string[] = [];
    const requiredInputsFilled = Object.entries(state.inputValues).every(([key, val]) => {
      // Ignore state_index and city_input for required check
      if (key === 'state_index' || key === 'city_input') return true;
      const inputDef = tool.inputs?.find(i => i.name === key);
      if (inputDef?.required && val.trim() === '') {
        missingFields.push(key);
        return false;
      }
      return true;
    });
    if ((isGem && !state.selectedState) || !requiredInputsFilled) {
      if (isGem && !state.selectedState) missingFields.push('state');
      const errorMsg = 'Please fill in all required fields.' + (missingFields.length ? '\nMissing: ' + missingFields.join(', ') : '');
      setState(prev => ({ ...prev, log: `\n[ERROR] ${errorMsg}\n` }));
      return;
    }
    setState(prev => ({ ...prev, isRunning: true }));
    setState(prev => ({ ...prev, log: '' }));
    setState(prev => ({ ...prev, outputFiles: [] }));
    setState(prev => ({ ...prev, isScrapingComplete: false }));
    const newRunId = Date.now().toString();
    setState(prev => ({ ...prev, runId: newRunId }));
    const payload = {
      startingpage: state.inputValues['startingpage'],
      totalpages: state.inputValues['totalpages'],
      username: state.inputValues['username'],
      state_index: isGem && tool.valid_states ? tool.valid_states.indexOf(state.selectedState) + 1 : undefined,
      city_input: state.selectedCity || "",
      days_interval: state.inputValues['days_interval'],
      run_id: newRunId
    };
    // Change the socket connection to use port 5003
    const sock = io('http://127.0.0.1:5003');
    setState(prev => ({ ...prev, socket: sock }));
    sock.emit('start_scraping', payload);
    setActiveJobState(state.selectedState);
    setJobData(prev => ({
      ...prev,
      [state.selectedState]: {
        inputValues: { ...state.inputValues },
        selectedCity: state.selectedCity,
        log: '',
        isRunning: true,
        isScrapingComplete: false,
        runId: newRunId,
        outputFiles: [],
        stopMessage: ''
      }
    }));
    sock.on('scraping_output', (data: { output: string }) => {
      setJobData(prev => {
        const job = prev[state.selectedState] || {};
        return {
          ...prev,
          [state.selectedState]: {
            ...job,
            log: (job.log || '') + data.output,
            isRunning: data.output.includes('SCRAPING COMPLETED') ? false : true,
            isScrapingComplete: data.output.includes('SCRAPING COMPLETED') ? true : job.isScrapingComplete
          }
        };
      });
      if (data.output.includes('SCRAPING COMPLETED')) {
        setScrapingJobs(jobs => jobs.map(job => job.state === state.selectedState ? { ...job, status: 'complete' } : job));
      }
    });
    sock.on('file_written', (data: { filename: string, run_id: string }) => {
      setJobData(prev => {
        const job = prev[state.selectedState] || {};
        return {
          ...prev,
          [state.selectedState]: {
            ...job,
            outputFiles: job.outputFiles && !job.outputFiles.includes(data.filename)
              ? [...job.outputFiles, data.filename]
              : job.outputFiles || []
          }
        };
      });
    });
    sock.on('disconnect', () => {
      setState(prev => ({ ...prev, isRunning: false }));
    });
    // Add or update job in scrapingJobs
    setScrapingJobs(jobs => {
      // If state already exists, set to in-progress
      if (jobs.some(job => job.state === state.selectedState)) {
        return jobs.map(job => job.state === state.selectedState ? { ...job, status: 'in-progress' } : job);
      }
      // Otherwise, add new job
      return [...jobs, { state: state.selectedState, status: 'in-progress' }];
    });
  };

  const handleStop = async () => {
    setState(prev => ({ ...prev, isStopping: true }));
    setState(prev => ({ ...prev, stopMessage: 'Stop scraping...' }));
    if (state.socket) {
      state.socket.disconnect();
      setState(prev => ({ ...prev, socket: null }));
    }
    // Send stop request to backend
    try {
      await fetch('http://127.0.0.1:5003/api/stop-scraping', { method: 'POST' });
      setState(prev => ({ ...prev, stopMessage: 'Scraping stopped.' }));
    } catch (error) {
      setState(prev => ({ ...prev, stopMessage: 'Failed to stop scraping.' }));
    }
    setState(prev => ({ ...prev, isRunning: false }));
    setState(prev => ({ ...prev, isScrapingComplete: true })); // Treat stop as completion to show files
    setState(prev => ({ ...prev, isStopping: false }));
  };

  const handleDeleteFile = async (filename: string) => {
    if (!state.runId) return;
    if (window.confirm(`Are you sure you want to delete ${filename}?`)) {
      try {
        const res = await fetch(`http://127.0.0.1:5002/api/delete/${state.runId}/${filename}`, {
          method: 'DELETE',
        });
        if (res.ok) {
          setState(prev => ({ ...prev, outputFiles: state.outputFiles.filter(f => f !== filename) }));
          setState(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} File deleted: ${filename}\n` }));
        } else {
          alert('Failed to delete file.');
        }
      } catch (error) {
        alert('Error deleting file.');
      }
    }
  };

  const handleMergeFiles = async () => {
    if (!state.runId) return;
    setState(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} Merging files...\n` }));
    // Call the merge endpoint and wait for it to finish
    try {
      const res = await fetch(`http://127.0.0.1:5002/api/merge-download/${state.runId}`);
      if (res.ok) {
        setState(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} Files merged into: merged_data_${state.runId}.xlsx\n` }));
        // Refresh the file list immediately after merge completes
        const filesRes = await fetch(`http://127.0.0.1:5002/api/files/${state.runId}`);
        if (filesRes.ok) {
          const files = await filesRes.json();
          setState(prev => ({ ...prev, outputFiles: files }));
        }
        // Optionally, trigger the download in a new tab
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `merged_data_${state.runId}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        setState(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} Failed to merge files.\n` }));
      }
    } catch (error) {
      setState(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} Error merging files.\n` }));
    }
  };

  function getTimestamp() {
    return `[${new Date().toLocaleTimeString()}]`;
  }

  // Use activeJobState for log, output, etc.
  const currentJob = activeJobState && typeof jobData[activeJobState] === 'object' ? jobData[activeJobState] : undefined;

  // Custom handler for E-Procurement
  // Remove two-step logic and always enable captcha input
  const [sessionId, setSessionId] = useState<string | null>(null);

  // E-Procurement WebSocket setup
  useEffect(() => {
    if (tool.name === 'eprocurement') {
      const socket = io(BACKEND_URL);

      const handleConnect = () => console.log('Connected to E-Procurement backend');
      const handleScrapingComplete = (data: { success: boolean; message: string; session_id: string }) => {
        setEIsRunning(false);
        setESuccess(data.message);
        if (data.session_id) {
          fetchSessionFiles(data.session_id);
        }
      };
      const handleScrapingError = (data: { error: string }) => {
        setEIsRunning(false);
        setEError(data.error);
      };
      const handleStatusUpdate = (data: { active: boolean; session_id: string | null }) => {
        setEIsRunning(data.active);
        if (data.session_id) {
          setECurrentSessionId(data.session_id);
        }
      };

      socket.on('connect', handleConnect);
      socket.on('scraping_complete', handleScrapingComplete);
      socket.on('scraping_error', handleScrapingError);
      socket.on('status_update', handleStatusUpdate);

      setESocket(socket);

      return () => {
        socket.off('connect', handleConnect);
        socket.off('scraping_complete', handleScrapingComplete);
        socket.off('scraping_error', handleScrapingError);
        socket.off('status_update', handleStatusUpdate);
        socket.disconnect();
      };
    }
  }, [tool.name]);

  // Fetch session files
  const fetchSessionFiles = async (sessionId: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/files/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setEOutputFiles(data.files.map((file: any) => file.name));
      }
    } catch (error) {
      console.error('Failed to fetch session files:', error);
    }
  };

  // E-Procurement handlers
  const handleOpenEdge = async () => {
    setEError('');
    setESuccess('');
    setEdgeOpened(false);
    
    if (!eBaseUrl) {
      setEError('Please enter the E-Procurement URL.');
      return;
    }

    setEIsRunning(true);
    try {
      console.log('[DEBUG] Sending URL to backend:', eBaseUrl);
      console.log('[DEBUG] Backend URL:', `${BACKEND_URL}/api/open-edge`);
      
      const res = await fetch(`${BACKEND_URL}/api/open-edge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: eBaseUrl })
    });
      
    const data = await res.json();
      console.log('[DEBUG] Backend response:', data);
      
      if (res.ok) {
      setEdgeOpened(true);
        setECurrentSessionId(data.session_id); // <-- Save session_id here
        setESuccess(`[INFO] Edge opened successfully with URL: ${data.url}\n[INFO] Please enter the captcha in the Edge window, then fill the rest of the fields and click Start Scraping.`);
    } else {
        setEError(data.error || 'Failed to open Edge');
    }
    } catch (error) {
      console.error('[DEBUG] Error:', error);
      setEError('Failed to connect to backend server');
    } finally {
    setEIsRunning(false);
    }
  };

  const handleStartEproc = async () => {
    if (!eBaseUrl || !eTenderType || !eDaysInterval || !eStartPage || !eCaptcha) {
      setEError('Please fill in all required fields.');
      return;
    }

    setEIsRunning(true);
    setEScrapingStarted(true);
    setEError('');
    setESuccess('');

    try {
      const res = await fetch(`${BACKEND_URL}/api/start-eproc-scraping`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
          session_id: eCurrentSessionId, // <-- Include session_id here
          base_url: eBaseUrl,
        tender_type: eTenderType,
          days_interval: parseInt(eDaysInterval),
          start_page: parseInt(eStartPage),
          captcha: eCaptcha
      })
    });

    const data = await res.json();

      if (res.ok) {
        setESuccess('Scraping started successfully!');
    } else {
        setEError(data.error || 'Failed to start scraping');
        setEIsRunning(false);
    }
    } catch (error) {
      setEError('Failed to connect to backend server');
    setEIsRunning(false);
    }
  };

  const handleStopEproc = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/stop-scraping`, {
      method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (res.ok) {
        setESuccess('Scraping stopped by user');
      }
    } catch (error) {
      console.error('Failed to stop scraping:', error);
    }
  };

  const handleResetEproc = () => {
    setEBaseUrl('');
    setETenderType('');
    setEDaysInterval('');
    setEStartPage('');
    setECaptcha('');
    setEIsRunning(false);
    setEScrapingStarted(false);
    setEError('');
    setESuccess('');
    setEdgeOpened(false);
    setEOutputFiles([]);
    setECurrentSessionId(null);
  };

  // File management handlers
  const handleEprocDownload = async (filename: string) => {
    if (!eCurrentSessionId) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/download/${eCurrentSessionId}/${filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      setEError('Failed to download file');
    }
  };

  const handleEprocMerge = async () => {
    if (!eCurrentSessionId) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/merge/${eCurrentSessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        setESuccess(`Files merged successfully: ${data.merged_file}`);
    // Refresh file list
        fetchSessionFiles(eCurrentSessionId);
      } else {
        const errorData = await response.json();
        setEError(errorData.error || 'Failed to merge files');
      }
    } catch (error) {
      setEError('Failed to merge files');
    }
  };

  // Handler to open Edge for captcha
  // Remove handleOpenEdge and edgeOpened logic for E-Procurement

  // Update handleSubmitCaptcha to include session_id
  const handleSubmitCaptcha = async () => {
    setEIsRunning(true);
    if (!eCurrentSessionId) {
      setEError('Session ID missing. Please restart.');
      setEIsRunning(false);
      return;
    }
    const res = await fetch(`${BACKEND_URL}/api/submit-eproc-captcha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ captcha: eCaptcha, session_id: eCurrentSessionId })
    });
    const data = await res.json();
    if (data.status === 'success') {
      setESuccess('Scraping completed!');
      setEIsRunning(false);
      setEStep('start');
      setECurrentSessionId(null);
    } else {
      setEError(data.message || 'Scraping failed');
      setEIsRunning(false);
    }
  };



  if (tool.name === 'eprocurement') {
    const isAllFieldsFilled = eBaseUrl && eTenderType && eDaysInterval && eCaptcha && eStartPage && !eIsRunning;
    
    return (
      <div className="space-y-6 bg-transparent dark:bg-gray-900 p-4 rounded-xl">
        <button
          className="text-sm text-blue-400 hover:underline flex items-center gap-2"
          onClick={onBack}
        >
          <ArrowLeft size={16} /> Back
        </button>
        
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">E-Procurement Scraper</h2>
        <p className="text-gray-700 dark:text-gray-400 mb-4">
          Scrapes data from the E-Procurement website and generates Excel files for each page.
        </p>

        <div className="space-y-4">
          {/* URL Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Enter E-Procurement URL <span className="text-red-400">*</span>
            </label>
            <div className="flex gap-4">
              <input 
                type="text" 
                className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white" 
                value={eBaseUrl} 
                onChange={e => setEBaseUrl(e.target.value)} 
                disabled={eIsRunning} 
                placeholder="https://etenders.hry.nic.in/nicgep/app"
              />
              <button
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
                onClick={handleOpenEdge}
                disabled={!eBaseUrl || eIsRunning}
                type="button"
              >
                Open Edge
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Examples: https://etenders.hry.nic.in/nicgep/app or https://mahatenders.gov.in/nicgep/app
            </p>
          </div>

          {/* Tender Type */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Tender Type <span className="text-red-400">*</span>
            </label>
            <select
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white"
              value={eTenderType}
              onChange={e => setETenderType(e.target.value)}
              disabled={eIsRunning}
            >
              <option value="">Select tender type...</option>
              <option value="O">Open Tender (O)</option>
              <option value="L">Limited Tender (L)</option>
            </select>
          </div>

          {/* Days Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              How many days back to scrape <span className="text-red-400">*</span>
            </label>
            <input 
              type="number" 
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white" 
              value={eDaysInterval} 
              onChange={e => setEDaysInterval(e.target.value)} 
              disabled={eIsRunning}
              min="1"
              max="365"
              placeholder="7"
            />
          </div>

          {/* Start Page */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Starting Page Number <span className="text-red-400">*</span>
            </label>
            <input 
              type="number" 
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white" 
              value={eStartPage} 
              onChange={e => setEStartPage(e.target.value)} 
              disabled={eIsRunning}
              min="1"
              placeholder="1"
            />
          </div>

          {/* Captcha */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Captcha <span className="text-red-400">*</span>
            </label>
            <input 
              type="text" 
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white" 
              value={eCaptcha} 
              onChange={e => setECaptcha(e.target.value)} 
              disabled={eIsRunning}
              placeholder="Enter captcha from the website"
            />
          </div>

          {/* Instructions */}
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
            <h4 className="text-blue-400 font-semibold mb-2">Instructions:</h4>
            <ol className="text-blue-300 text-sm space-y-1">
              <li>1. Enter the E-Procurement website URL</li>
              <li>2. Click "Open Edge" to open the website in Edge browser</li>
              <li>3. Fill in all the required fields above</li>
              <li>4. Enter the captcha from the website</li>
              <li>5. Click "Start Scraping" to begin the process</li>
            </ol>
            <div className="mt-3 p-2 bg-yellow-900/20 border border-yellow-500/30 rounded">
              <p className="text-yellow-300 text-xs">
                <strong>Note:</strong> If Edge opens the wrong URL, try refreshing the page (Ctrl+F5) to clear cache, 
                or check the browser console (F12) for debug information.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
                <button
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded flex items-center gap-2 disabled:opacity-50"
              onClick={handleStartEproc}
              disabled={!isAllFieldsFilled}
                >
              <Play size={16} /> Start Scraping
                </button>
            
            {eIsRunning && (
            <button
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded flex items-center gap-2"
                onClick={handleStopEproc}
              >
                <Square size={16} /> Stop Scraping
              </button>
            )}
            
            <button
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded flex items-center gap-2 disabled:opacity-50"
              onClick={handleResetEproc}
              disabled={eIsRunning}
            >
              Reset
            </button>
          </div>

          {/* Status Messages */}
          {eError && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
              <div className="text-red-400 font-semibold">Error: {eError}</div>
            </div>
          )}
          
          {eSuccess && (
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3">
              <div className="text-green-400 font-semibold">{eSuccess}</div>
            </div>
          )}

          {/* Log Output */}
          {eScrapingStarted && (
            <div className="bg-black border border-gray-600 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-2">Real-time Log:</div>
              <LiveLogViewer />
            </div>
          )}

          {/* File Management */}
          {eOutputFiles.length > 0 && (
            <div className="bg-gray-800/50 border border-gray-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-white font-semibold">Generated Files:</h4>
                <button
                  onClick={handleEprocMerge}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded flex items-center gap-1 text-sm"
                >
                  <Merge size={14} /> Merge Files
                </button>
              </div>
              
              <div className="grid gap-2">
                {eOutputFiles.map((filename, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-700/50 rounded p-2">
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-blue-400" />
                      <span className="text-white text-sm">{filename}</span>
                    </div>
                    <button
                      onClick={() => handleEprocDownload(filename)}
                      className="bg-green-600 hover:bg-green-700 text-white p-1 rounded"
                    >
                      <Download size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-transparent dark:bg-gray-900 p-4 rounded-xl">
      <button
        className="text-sm text-blue-400 hover:underline flex items-center gap-2"
        onClick={onBack}
      >
        <ArrowLeft size={16} /> Back
      </button>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{tool.name}</h2>
      <p className="text-gray-700 dark:text-gray-400 mb-4">{tool.description}</p>
      {/* Scraping Jobs Navigation Bar */}
      {scrapingJobs.length > 0 && (
        <div className="flex gap-2 mb-4">
          {scrapingJobs.map(job => (
            <span
              key={job.state}
              onClick={() => {
                setActiveJobState(job.state);
                // Restore form fields for this job
                const jobInfo = jobData[job.state];
                if (jobInfo) {
                  setState(prev => ({ ...prev, inputValues: { ...jobInfo.inputValues } }));
                  setState(prev => ({ ...prev, selectedCity: jobInfo.selectedCity }));
                }
              }}
              className={`px-3 py-1 rounded text-white font-semibold cursor-pointer ${job.status === 'in-progress' ? 'bg-blue-500' : 'bg-green-500'} ${activeJobState === job.state ? 'ring-2 ring-violet-400' : ''}`}
            >
              {job.state}
            </span>
          ))}
        </div>
      )}
      <div className="space-y-4">
        {tool.name === 'gem' && tool.valid_states && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Select State/Region</label>
            <select
              value={state.selectedState}
              onChange={e => {
                setState(prev => ({ ...prev, selectedState: e.target.value }));
                setState(prev => ({ ...prev, selectedCity: '' }));
                setState(prev => ({
                  ...prev,
                  inputValues: {
                    ...prev.inputValues,
                  state_index: String(validStates.indexOf(e.target.value) + 1) // 1-based index
                  }
                }));
                setState(prev => ({ ...prev, isRunning: false }));
                setState(prev => ({ ...prev, isScrapingComplete: false }));
                setState(prev => ({ ...prev, log: '' }));
                setState(prev => ({ ...prev, runId: null }));
                setState(prev => ({ ...prev, outputFiles: [] }));
                setState(prev => ({ ...prev, stopMessage: '' }));
                // Optionally: reset any other stateful values
              }}
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white"
            >
              <option value="">Choose a state...</option>
              {tool.valid_states.map((state: string) => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
        )}
        {tool.name === 'gem' && state.selectedState && tool.valid_cities?.[state.selectedState] && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Select City (optional)</label>
            <select
              value={state.selectedCity}
              onChange={e => {
                setState(prev => ({ ...prev, selectedCity: e.target.value }));
                setState(prev => ({
                  ...prev,
                  inputValues: {
                    ...prev.inputValues,
                  city_input: e.target.value || ""
                  }
                }));
              }}
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white"
            >
              <option value="">Skip city filtering</option>
              {tool.valid_cities[state.selectedState].map((city: string) => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>
        )}
        {tool.inputs?.map(input => (
          input.name !== 'city_input' && input.name !== 'state_index' && (
            <div key={input.name}>
              <label className="block text-sm font-medium text-gray-300 mb-2">{input.description}</label>
              <input
                type={input.type === 'int' ? 'number' : 'text'}
                value={state.inputValues[input.name] || ''}
                onChange={e => handleInputChange(input.name, e.target.value)}
                className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white"
              />
            </div>
          )
        ))}
        <div className="flex gap-4">
          <button
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded w-full flex items-center justify-center gap-2"
            onClick={handleStart}
            disabled={state.isRunning}
          >
            <Play size={16} /> Start Scraping
          </button>
          <button
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded w-full flex items-center justify-center gap-2"
            onClick={handleStop}
            disabled={!state.isRunning || state.isStopping}
          >
            <Square size={16} /> Stop
          </button>
        </div>
        {(currentJob?.isRunning || currentJob?.log) && (
          <div className="bg-black text-green-400 p-4 rounded mt-4 h-64 overflow-y-auto whitespace-pre-wrap font-mono" style={{ fontSize: "1rem", lineHeight: "1.4" }}>
            {currentJob?.log || <span className="text-gray-500">Waiting for output...</span>}
            <span className="animate-pulse">█</span>
          </div>
        )}
        {state.stopMessage && (
          <div className="text-red-400 font-semibold mt-2">{state.stopMessage}</div>
        )}

      </div>

      {/* NEW OUTPUT FILES SECTION */}
      {state.runId && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Output Files</h3>
            <a
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded flex items-center gap-2"
              onClick={handleMergeFiles}
              style={{ cursor: 'pointer' }}
            >
              <Merge size={16} /> Merge Files
            </a>
          </div>
          <div className="bg-transparent dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            {state.outputFiles.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {state.outputFiles.map((file: string) => (
                  <FileCard
                    key={file}
                    file={file}
                    runId={state.runId || ''}
                    setLog={setState}
                    handleDeleteFile={handleDeleteFile}
                    getTimestamp={getTimestamp}
                    isMerged={file.startsWith('merged_data_')}
                  />
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No output files found for this run.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const FileCard: React.FC<{ file: string; runId: string; setLog: (fn: (prev: any) => any) => void; handleDeleteFile: (file: string) => void; getTimestamp: () => string; isMerged?: boolean }> = ({ file, runId, setLog, handleDeleteFile, getTimestamp, isMerged }) => {
  const [size, setSize] = React.useState('');
  React.useEffect(() => {
    fetchFileSize(`http://127.0.0.1:5002/api/download/${runId}/${file}`).then(setSize);
  }, [file, runId]);
  return (
    <div className="flex items-center bg-gray-900 rounded-lg p-3 gap-3 shadow border border-gray-700">
      <FileText className="text-blue-400 flex-shrink-0" size={28} />
      <div className="flex-1 min-w-0">
        <div className="truncate text-gray-200 font-mono text-sm">
          {file}
          {isMerged && (
            <span className="ml-2 px-2 py-0.5 bg-purple-600 text-white text-xs rounded">merge file ani</span>
          )}
        </div>
        <div className="text-xs text-gray-500 mt-1">{size}</div>
      </div>
      <a
        href={`http://127.0.0.1:5002/api/download/${runId}/${file}`}
        className="p-2 text-green-400 hover:text-green-300"
        title="Download"
        onClick={() => setLog(prev => ({ ...prev, log: prev.log + `\n${getTimestamp()} File downloaded: ${file}\n` }))}
      >
        <Download size={18} />
      </a>
      <button
        onClick={() => handleDeleteFile(file)}
        className="p-2 text-red-400 hover:text-red-300"
        title="Delete"
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
};

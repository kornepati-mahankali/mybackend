import React, { useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';

function LiveLogViewer() {
  const [logs, setLogs] = useState<string[]>([]);
  const [usePolling, setUsePolling] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<any>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  // Fallback HTTP polling mechanism
  const startPolling = () => {
    console.log('LiveLogViewer: Starting HTTP polling fallback...');
    setUsePolling(true);
    
    const fetchLogs = async () => {
      try {
        const res = await fetch('http://localhost:5023/api/logs');
        if (res.ok) {
          const data = await res.json();
          if (data.logs && data.logs.length > 0) {
            setLogs(data.logs);
          }
        }
      } catch (e) {
        console.error('LiveLogViewer: HTTP polling error:', e);
      }
    };
    
    fetchLogs(); // Initial fetch
    pollingIntervalRef.current = setInterval(fetchLogs, 2000);
  };

  useEffect(() => {
    console.log('LiveLogViewer: Attempting to connect to Socket.IO...');
    
    // Connect to Socket.IO with polling transport only
    socketRef.current = io('http://localhost:5023', {
      transports: ['polling'],
      timeout: 10000
    });
    
    socketRef.current.on('connect', () => {
      console.log('LiveLogViewer: ✅ Connected to backend Socket.IO');
      setUsePolling(false);
    });
    
    socketRef.current.on('scraping_log', (data: any) => {
      console.log('LiveLogViewer: 📝 Received log:', data);
      setLogs(prev => [...prev, data.message]);
    });
    
    socketRef.current.on('disconnect', (reason: string) => {
      console.log('LiveLogViewer: ❌ Disconnected from backend Socket.IO, reason:', reason);
      if (!usePolling) {
        startPolling(); // Fallback to HTTP polling
      }
    });
    
    socketRef.current.on('connect_error', (error: any) => {
      console.error('LiveLogViewer: ❌ Socket.IO connection error:', error);
      console.error('LiveLogViewer: Error details:', {
        message: error.message,
        description: error.description,
        context: error.context
      });
      
      // Fallback to HTTP polling after 5 seconds
      setTimeout(() => {
        if (!usePolling) {
          startPolling();
        }
      }, 5000);
    });

    return () => {
      console.log('LiveLogViewer: Cleaning up Socket.IO connection...');
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [usePolling]);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  return (
    <div style={{
      background: '#111',
      color: '#0f0',
      padding: 10,
      height: 400,
      overflowY: 'auto',
      fontFamily: 'monospace',
      fontSize: 14,
      borderRadius: 6,
      border: '1px solid #333'
    }}>
      {logs.length > 0 ? (
        logs.map((line, idx) => <div key={idx}>{line}</div>)
      ) : (
        <div style={{ color: '#666' }}>Waiting for logs... Start a scraping job to see live logs here.</div>
      )}
      <div ref={logEndRef} />
    </div>
  );
}

export default LiveLogViewer; 
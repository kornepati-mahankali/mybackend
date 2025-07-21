import React, { useEffect, useState, useRef } from 'react';
// import io from 'socket.io-client';

// const socket = io('http://localhost:5021');

function LiveLogViewer() {
  const [logs, setLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Poll logs from backend every 2 seconds
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch('http://localhost:5021/api/logs');
        if (res.ok) {
          const data = await res.json();
          setLogs(data.logs);
          // Print logs to the browser console for debugging
          console.log("--- Fetched Logs from Backend ---");
          data.logs.forEach((line: string) => console.log(line));
        }
      } catch (e) {
        // Optionally handle error
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

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
      {logs.map((line, idx) => <div key={idx}>{line}</div>)}
      <div ref={logEndRef} />
    </div>
  );
}

export default LiveLogViewer; 
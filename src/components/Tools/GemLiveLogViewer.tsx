import React, { useEffect, useState } from "react";
import io from "socket.io-client";

export const GemLiveLogViewer: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  useEffect(() => {
    const socket = io("http://127.0.0.1:5003");

    socket.on("scraping_output", (data: any) => {
      setLogs((prev) => [...prev, data.output]);
    });

    socket.on("file_written", (data: any) => {
      setFileUrl(`/outputs/gem/${data.run_id}/${data.filename}`);
      setLogs((prev) => [...prev, `File ready: ${data.filename}`]);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="bg-zinc-900 text-green-400 p-4 rounded h-48 overflow-y-auto mt-4">
      <div className="font-bold mb-2">Live Logs</div>
      {logs.length === 0 ? (
        <div className="text-gray-400">No logs yet...</div>
      ) : (
        logs.map((log, idx) => <div key={idx}>{log}</div>)
      )}
      {fileUrl && (
        <a
          href={fileUrl}
          download
          className="block mt-4 bg-blue-600 text-white px-4 py-2 rounded text-center"
        >
          Download Output File
        </a>
      )}
    </div>
  );
}; 
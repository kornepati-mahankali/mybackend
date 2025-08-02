import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid
} from "recharts";
import { useAnimation } from '../contexts/AnimationContext';

interface SystemLoadData {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  timestamp: string;
}

const API_URL = "http://localhost:8001/system-load"; // Admin metrics API endpoint

const SystemUsageChart = () => {
  const [data, setData] = useState<any[]>([]);
  // Fix: Use number type for browser setInterval
  const intervalRef = useRef<number | null>(null);
  const { enabled: animationsEnabled } = useAnimation();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get<SystemLoadData>(API_URL);
        // Transform the data to match the chart format
        const transformedData = {
          time: new Date(res.data.timestamp).toLocaleTimeString(),
          cpu: res.data.cpu_percent,
          memory: res.data.memory_percent,
          storage: res.data.disk_percent
        };
        setData(prev => {
          const newData = [...prev, transformedData];
          return newData.length > 6 ? newData.slice(newData.length - 6) : newData;
        });
      } catch (err) {
        console.error('Failed to fetch system usage data:', err);
      }
    };
    fetchData();
    intervalRef.current = window.setInterval(fetchData, 5000);
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, []);

  return (
    <div style={{
      background: "#232b3e",
      padding: 24,
      borderRadius: 12,
      color: "#fff",
      boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
    }}>
      <h3 style={{ color: "#6cf" }}>System Resources</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid stroke="#2c3550" />
          <XAxis dataKey="time" stroke="#fff" />
          <YAxis stroke="#fff" domain={[0, 100]} />
          <Tooltip
            contentStyle={{ background: "#232b3e", color: "#fff", border: "none" }}
            labelStyle={{ color: "#fff" }}
          />
          <Legend />
          <Line type="monotone" dataKey="cpu" stroke="#ffb347" name="CPU %" dot isAnimationActive={animationsEnabled} />
          <Line type="monotone" dataKey="memory" stroke="#8884d8" name="Memory %" dot isAnimationActive={animationsEnabled} />
          <Line type="monotone" dataKey="storage" stroke="#82ca9d" name="Storage %" dot isAnimationActive={animationsEnabled} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SystemUsageChart; 
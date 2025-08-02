#!/usr/bin/env python3
"""
Dashboard Services Startup Script
Starts both the Dashboard API and WebSocket servers
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_dashboard_api():
    """Start the Dashboard API server"""
    print("Starting Dashboard API server on port 8001...")
    try:
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "dashboard_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ])
        return api_process
    except Exception as e:
        print(f"Error starting Dashboard API: {e}")
        return None

def start_dashboard_websocket():
    """Start the Dashboard WebSocket server"""
    print("Starting Dashboard WebSocket server on port 8002...")
    try:
        ws_process = subprocess.Popen([
            sys.executable, "dashboard_websocket.py"
        ])
        return ws_process
    except Exception as e:
        print(f"Error starting Dashboard WebSocket: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nShutting down dashboard services...")
    sys.exit(0)

def main():
    """Main function to start all dashboard services"""
    print("🚀 Starting Dashboard Services...")
    print("=" * 50)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start API server
    api_process = start_dashboard_api()
    if not api_process:
        print("❌ Failed to start Dashboard API server")
        sys.exit(1)
    
    # Wait a moment for API to start
    time.sleep(2)
    
    # Start WebSocket server
    ws_process = start_dashboard_websocket()
    if not ws_process:
        print("❌ Failed to start Dashboard WebSocket server")
        api_process.terminate()
        sys.exit(1)
    
    print("✅ Dashboard services started successfully!")
    print("📊 Dashboard API: http://localhost:8001")
    print("🔌 WebSocket: ws://localhost:8002")
    print("📖 API Docs: http://localhost:8001/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ Dashboard API server stopped unexpectedly")
                break
                
            if ws_process.poll() is not None:
                print("❌ Dashboard WebSocket server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard services...")
    finally:
        # Cleanup
        if api_process:
            api_process.terminate()
            api_process.wait()
        if ws_process:
            ws_process.terminate()
            ws_process.wait()
        print("✅ Dashboard services stopped")

if __name__ == "__main__":
    main() 
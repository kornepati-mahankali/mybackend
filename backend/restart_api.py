#!/usr/bin/env python3
"""
Restart the admin metrics API server
"""

import os
import subprocess
import time
import signal
import psutil

def restart_api_server():
    """Restart the admin metrics API server"""
    try:
        print("🔄 Restarting admin metrics API server...")
        
        # Find and kill existing Python processes running admin_metrics_api.py
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'admin_metrics_api.py' in ' '.join(cmdline):
                    print(f"🛑 Stopping existing server (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        # Wait a moment for the process to fully stop
        time.sleep(2)
        
        # Start the server again
        print("🚀 Starting admin metrics API server...")
        subprocess.Popen(['python', 'admin_metrics_api.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        print("✅ Server restarted! Testing connection...")
        
        # Test the connection
        import requests
        try:
            response = requests.get('http://localhost:8001/database-size', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is working! Database size: {data.get('total_size', 'N/A')}")
            else:
                print(f"⚠️ API returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ API test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error restarting server: {e}")

if __name__ == "__main__":
    restart_api_server() 
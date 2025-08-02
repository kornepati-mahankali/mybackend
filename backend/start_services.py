#!/usr/bin/env python3
"""
Startup script for Super Scraper Pro backend services
"""

import subprocess
import sys
import time
import signal
import os
from threading import Thread
import uvicorn
from job_processor import start_job_processor, stop_job_processor

# Global variables to track processes
admin_metrics_process = None
job_processor_running = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down services...")
    
    # Stop job processor
    if job_processor_running:
        stop_job_processor()
    
    # Stop admin metrics server
    if admin_metrics_process:
        admin_metrics_process.terminate()
        try:
            admin_metrics_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            admin_metrics_process.kill()
    
    print("✅ All services stopped")
    sys.exit(0)

def start_admin_metrics_api():
    """Start the admin metrics API server"""
    global admin_metrics_process
    
    print("🚀 Starting Admin Metrics API...")
    
    # Start the admin metrics API using uvicorn
    config = uvicorn.Config(
        "admin_metrics_api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    server.run()

def start_job_processor_service():
    """Start the job processor service"""
    global job_processor_running
    
    print("🔧 Starting Job Processor...")
    start_job_processor()
    job_processor_running = True
    
    # Keep the job processor running
    try:
        while job_processor_running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

def main():
    """Main startup function"""
    print("🎯 Super Scraper Pro Backend Services")
    print("=" * 50)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start job processor in a separate thread
        job_processor_thread = Thread(target=start_job_processor_service, daemon=True)
        job_processor_thread.start()
        
        # Give job processor time to start
        time.sleep(2)
        
        # Start admin metrics API in main thread
        start_admin_metrics_api()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error starting services: {e}")
    finally:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 
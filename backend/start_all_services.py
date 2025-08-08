#!/usr/bin/env python3
"""
Multi-service startup script for Lavangam backend
This script starts all the required services on different ports
"""

import subprocess
import time
import sys
import os
import signal
import threading
from datetime import datetime

# Service configurations
SERVICES = [
    {
        "name": "Main API",
        "command": ["python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        "port": 8000,
        "description": "Main FastAPI application with all routers"
    },
    {
        "name": "Scrapers API",
        "command": ["python", "-m", "uvicorn", "scrapers.api:app", "--reload", "--port", "5022"],
        "port": 5022,
        "description": "Scraping tools and WebSocket endpoints"
    },
    {
        "name": "System Usage API",
        "command": ["python", "-m", "uvicorn", "system_usage_api:app", "--reload", "--port", "5024"],
        "port": 5024,
        "description": "System monitoring and metrics"
    },
    {
        "name": "Dashboard API",
        "command": ["python", "-m", "uvicorn", "dashboard_api:app", "--host", "127.0.0.1", "--port", "8004"],
        "port": 8004,
        "description": "Dashboard metrics and analytics"
    },
    {
        "name": "File Manager",
        "command": ["python", "file_manager.py"],
        "port": 5000,  # Flask default
        "description": "File management and downloads"
    },
    {
        "name": "Scraper WebSocket",
        "command": ["python", "scraper_ws.py"],
        "port": 5001,  # Flask-SocketIO default
        "description": "Real-time scraping WebSocket server"
    },
    {
        "name": "Admin Metrics API",
        "command": ["python", "-m", "uvicorn", "admin_metrics_api:app", "--reload", "--port", "5025"],
        "port": 5025,
        "description": "Admin dashboard metrics"
    },
    {
        "name": "E-Procurement Server",
        "command": ["python", "eproc_server_fixed.py"],
        "port": 5002,  # Flask default
        "description": "E-procurement scraping server"
    },
    {
        "name": "Dashboard WebSocket",
        "command": ["python", "dashboard_websocket.py"],
        "port": 8765,  # WebSocket default
        "description": "Dashboard real-time updates"
    }
]

# Store running processes
running_processes = {}
stop_event = threading.Event()

def log(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def start_service(service_config):
    """Start a single service"""
    name = service_config["name"]
    command = service_config["command"]
    port = service_config["port"]
    
    try:
        log(f"Starting {name} on port {port}...")
        log(f"Command: {' '.join(command)}")
        
        # Start the process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        running_processes[name] = {
            "process": process,
            "config": service_config,
            "start_time": datetime.now()
        }
        
        log(f"✅ {name} started successfully (PID: {process.pid})")
        
        # Start a thread to monitor the process output
        def monitor_output():
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        log(f"[{name}] {line.strip()}")
                    if stop_event.is_set():
                        break
            except Exception as e:
                log(f"Error monitoring {name}: {e}", "ERROR")
        
        monitor_thread = threading.Thread(target=monitor_output, daemon=True)
        monitor_thread.start()
        
        return True
        
    except Exception as e:
        log(f"❌ Failed to start {name}: {e}", "ERROR")
        return False

def stop_service(name):
    """Stop a single service"""
    if name in running_processes:
        process_info = running_processes[name]
        process = process_info["process"]
        
        try:
            log(f"Stopping {name}...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                log(f"✅ {name} stopped gracefully")
            except subprocess.TimeoutExpired:
                log(f"⚠️  {name} didn't stop gracefully, forcing...")
                process.kill()
                process.wait()
                log(f"✅ {name} stopped forcefully")
                
        except Exception as e:
            log(f"❌ Error stopping {name}: {e}", "ERROR")
        finally:
            del running_processes[name]

def stop_all_services():
    """Stop all running services"""
    log("Stopping all services...")
    stop_event.set()
    
    for name in list(running_processes.keys()):
        stop_service(name)
    
    log("All services stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    log(f"Received signal {signum}, shutting down...")
    stop_all_services()
    sys.exit(0)

def check_port_availability(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log("🚀 Starting Lavangam Backend Services")
    log("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        log("❌ Error: main.py not found. Please run this script from the backend directory.", "ERROR")
        sys.exit(1)
    
    # Check port availability
    log("Checking port availability...")
    for service in SERVICES:
        if not check_port_availability(service["port"]):
            log(f"⚠️  Warning: Port {service['port']} ({service['name']}) may already be in use", "WARNING")
    
    # Start services
    successful_starts = 0
    for service in SERVICES:
        if start_service(service):
            successful_starts += 1
        time.sleep(1)  # Small delay between starts
    
    log(f"✅ Started {successful_starts}/{len(SERVICES)} services successfully")
    log("=" * 50)
    log("Services Summary:")
    for service in SERVICES:
        status = "✅ Running" if service["name"] in running_processes else "❌ Failed"
        log(f"  {service['name']} (Port {service['port']}): {status}")
    
    log("=" * 50)
    log("Press Ctrl+C to stop all services")
    
    try:
        # Keep the main thread alive
        while running_processes and not stop_event.is_set():
            time.sleep(1)
            
            # Check if any processes have died
            dead_services = []
            for name, info in running_processes.items():
                if info["process"].poll() is not None:
                    dead_services.append(name)
            
            for name in dead_services:
                log(f"⚠️  {name} has stopped unexpectedly", "WARNING")
                del running_processes[name]
                
    except KeyboardInterrupt:
        log("Received interrupt signal")
    finally:
        stop_all_services()

if __name__ == "__main__":
    main() 
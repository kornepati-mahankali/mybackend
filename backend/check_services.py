#!/usr/bin/env python3
"""
Service Health Checker for Lavangam Backend
This script checks if all services are running and accessible
"""

import requests
import socket
import time
from datetime import datetime
import json

# Service configurations
SERVICES = [
    {
        "name": "Main API",
        "port": 8000,
        "health_endpoint": "/docs",
        "type": "FastAPI"
    },
    {
        "name": "Scrapers API", 
        "port": 5022,
        "health_endpoint": "/docs",
        "type": "FastAPI"
    },
    {
        "name": "System Usage API",
        "port": 5024,
        "health_endpoint": "/api/system-usage",
        "type": "FastAPI"
    },
    {
        "name": "Dashboard API",
        "port": 8004,
        "health_endpoint": "/health",
        "type": "FastAPI"
    },
    {
        "name": "File Manager",
        "port": 5000,
        "health_endpoint": "/",
        "type": "Flask"
    },
    {
        "name": "Scraper WebSocket",
        "port": 5001,
        "health_endpoint": "/",
        "type": "Flask-SocketIO"
    },
    {
        "name": "Admin Metrics API",
        "port": 5025,
        "health_endpoint": "/health",
        "type": "FastAPI"
    },
    {
        "name": "E-Procurement Server",
        "port": 5002,
        "health_endpoint": "/api/health",
        "type": "Flask"
    }
]

def check_port_open(host, port, timeout=3):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_http_endpoint(host, port, endpoint, timeout=5):
    """Check if an HTTP endpoint is accessible"""
    try:
        url = f"http://{host}:{port}{endpoint}"
        response = requests.get(url, timeout=timeout)
        return response.status_code < 500  # Accept 2xx, 3xx, 4xx but not 5xx
    except requests.exceptions.RequestException:
        return False

def log(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def main():
    """Main function to check all services"""
    log("🔍 Checking Lavangam Backend Services")
    log("=" * 50)
    
    results = []
    all_healthy = True
    
    for service in SERVICES:
        name = service["name"]
        port = service["port"]
        endpoint = service["health_endpoint"]
        service_type = service["type"]
        
        log(f"Checking {name} (Port {port})...")
        
        # Check if port is open
        port_open = check_port_open("localhost", port)
        
        if port_open:
            # Check HTTP endpoint
            http_ok = check_http_endpoint("localhost", port, endpoint)
            
            if http_ok:
                status = "✅ HEALTHY"
                log(f"  {name}: {status}")
            else:
                status = "⚠️  PORT_OPEN_BUT_HTTP_FAILED"
                log(f"  {name}: {status}", "WARNING")
                all_healthy = False
        else:
            status = "❌ NOT_RUNNING"
            log(f"  {name}: {status}", "ERROR")
            all_healthy = False
        
        results.append({
            "name": name,
            "port": port,
            "type": service_type,
            "status": status,
            "port_open": port_open,
            "http_ok": http_ok if port_open else False
        })
    
    log("=" * 50)
    log("Service Health Summary:")
    
    healthy_count = sum(1 for r in results if "HEALTHY" in r["status"])
    total_count = len(results)
    
    for result in results:
        status_icon = "✅" if "HEALTHY" in result["status"] else "❌"
        log(f"  {status_icon} {result['name']} (Port {result['port']}): {result['status']}")
    
    log("=" * 50)
    log(f"Overall Status: {healthy_count}/{total_count} services healthy")
    
    if all_healthy:
        log("🎉 All services are running correctly!", "SUCCESS")
        return 0
    else:
        log("⚠️  Some services are not running properly", "WARNING")
        return 1

if __name__ == "__main__":
    exit(main()) 
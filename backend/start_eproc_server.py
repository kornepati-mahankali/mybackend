#!/usr/bin/env python3
"""
E-Procurement Backend Server Startup Script
This script starts the E-Procurement scraping backend server with proper setup.
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_socketio',
        'flask_cors',
        'selenium',
        'pandas',
        'xlsxwriter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_edge_driver():
    """Check if Edge driver is available"""
    driver_path = os.path.join(os.path.dirname(__file__), 'scrapers', 'edgedriver_win64', 'msedgedriver.exe')
    
    if os.path.exists(driver_path):
        print(f"✅ Edge driver found at: {driver_path}")
        return True
    else:
        print(f"❌ Edge driver not found at: {driver_path}")
        print("Please ensure the Edge driver is installed in the correct location.")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        os.path.join(os.path.dirname(__file__), 'outputs'),
        os.path.join(os.path.dirname(__file__), 'outputs', 'eproc'),
        os.path.join(os.path.dirname(__file__), 'scrapers', 'OUTPUT'),
        os.path.join(os.path.dirname(__file__), 'scrapers', 'OUTPUT', 'Downloaded_Documents')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def main():
    """Main startup function"""
    print("🚀 E-Procurement Backend Server Startup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    # Check Edge driver
    print("\n🔧 Checking Edge driver...")
    if not check_edge_driver():
        print("\n❌ Edge driver check failed. Please install the Edge driver.")
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Start the server
    print("\n🚀 Starting E-Procurement backend server...")
    print("📡 Server will be available at: http://localhost:5020")
    print("🔌 WebSocket will be available at: ws://localhost:5020")
    print("\n📋 Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/open-edge - Open Edge browser")
    print("  POST /api/start-eproc-scraping - Start scraping")
    print("  POST /api/stop-scraping - Stop scraping")
    print("  GET  /api/status - Get status")
    print("  GET  /api/files/<session_id> - Get session files")
    print("  GET  /api/download/<session_id>/<filename> - Download file")
    print("  POST /api/merge/<session_id> - Merge session files")
    print("  GET  /api/sessions - List all sessions")
    print("\n" + "=" * 50)
    
    try:
        # Import and run the server
        from eproc_server import app, socketio
        
        print("✅ Server imported successfully")
        print("🔄 Starting server...")
        
        socketio.run(app, host='0.0.0.0', port=5020, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
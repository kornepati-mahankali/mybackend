# Multi-Service Backend Setup

This guide explains how to run all the Lavangam backend services on multiple ports simultaneously.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Windows Batch File:**
```bash
# Navigate to backend directory
cd backend

# Run the batch file
start_all_services.bat
```

**PowerShell Script:**
```powershell
# Navigate to backend directory
cd backend

# Run the PowerShell script
.\start_all_services.ps1

# For verbose output
.\start_all_services.ps1 -Verbose

# For help
.\start_all_services.ps1 -Help
```

**Python Script:**
```bash
# Navigate to backend directory
cd backend

# Run the Python script
python start_all_services.py
```

### Option 2: Manual Startup

If you prefer to start services individually, here are the commands:

```bash
# Terminal 1: Main API
py -m uvicorn main:app --reload --port 8000

# Terminal 2: Scrapers API
py -m uvicorn scrapers.api:app --reload --port 5022

# Terminal 3: System Usage API
py -m uvicorn system_usage_api:app --reload --port 5024

# Terminal 4: Dashboard API
python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8004

# Terminal 5: File Manager
py file_manager.py

# Terminal 6: Scraper WebSocket
py scraper_ws.py

# Terminal 7: Admin Metrics API
py -m uvicorn admin_metrics_api:app --reload --port 5025

# Terminal 8: E-Procurement Server
py eproc_server_fixed.py

# Terminal 9: Dashboard WebSocket
py dashboard_websocket.py
```

## 📋 Service Ports

| Service | Port | Description | Framework |
|---------|------|-------------|-----------|
| Main API | 8000 | Main FastAPI application with all routers | FastAPI |
| Scrapers API | 5022 | Scraping tools and WebSocket endpoints | FastAPI |
| System Usage API | 5024 | System monitoring and metrics | FastAPI |
| Dashboard API | 8004 | Dashboard metrics and analytics | FastAPI |
| File Manager | 5000 | File management and downloads | Flask |
| Scraper WebSocket | 5001 | Real-time scraping WebSocket server | Flask-SocketIO |
| Admin Metrics API | 5025 | Admin dashboard metrics | FastAPI |
| E-Procurement Server | 5002 | E-procurement scraping server | Flask |
| Dashboard WebSocket | 8765 | Dashboard real-time updates | WebSocket |

## 🔧 Prerequisites

1. **Python 3.8+** installed and in PATH
2. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database** running (MySQL on port 3307)
4. **Edge WebDriver** available in `scrapers/edgedriver_win64/`

## 🛠️ Features

### Automated Script Features

- **Port Availability Check**: Warns if ports are already in use
- **Process Monitoring**: Monitors all running services
- **Graceful Shutdown**: Properly stops all services on Ctrl+C
- **Error Handling**: Handles service failures gracefully
- **Real-time Logging**: Shows output from all services
- **Status Summary**: Shows which services started successfully

### Service Management

- **Start All**: Launches all services simultaneously
- **Stop All**: Gracefully stops all services
- **Individual Monitoring**: Each service output is labeled
- **Auto-restart**: Can detect if services crash (manual restart required)

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Warning: Port 8000 (Main API) may already be in use
   ```
   **Solution**: Stop the service using that port or change the port in the script

2. **Python Not Found**
   ```
   ERROR: Python is not installed or not in PATH
   ```
   **Solution**: Install Python and add it to your system PATH

3. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Solution**: Install dependencies with `pip install -r requirements.txt`

4. **Database Connection Failed**
   ```
   Database connection failed
   ```
   **Solution**: Ensure MySQL is running on port 3307 with correct credentials

### Manual Port Changes

To change ports, edit the `SERVICES` list in `start_all_services.py`:

```python
SERVICES = [
    {
        "name": "Main API",
        "command": ["python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        "port": 8000,  # Change this port
        "description": "Main FastAPI application with all routers"
    },
    # ... other services
]
```

### Checking Service Status

You can check if services are running by visiting:

- Main API: http://localhost:8000/docs
- Scrapers API: http://localhost:5022/docs
- System Usage: http://localhost:5024/api/system-usage
- Dashboard API: http://localhost:8004/health
- File Manager: http://localhost:5000/
- Admin Metrics: http://localhost:5025/health

## 📝 Logging

The automated script provides detailed logging:

- **Service Start/Stop**: Shows when services start and stop
- **Process Output**: Captures and displays output from each service
- **Error Messages**: Highlights errors in red
- **Warnings**: Shows warnings in yellow
- **Success Messages**: Shows successful operations in green

## 🔄 Stopping Services

### Automated Script
- Press `Ctrl+C` to stop all services gracefully
- The script will wait up to 10 seconds for graceful shutdown
- If services don't stop gracefully, they will be forcefully terminated

### Manual Stop
If you started services manually, stop each terminal with `Ctrl+C`

## 🎯 Best Practices

1. **Use the Automated Script**: It handles all the complexity for you
2. **Check Ports First**: Ensure no other applications are using the required ports
3. **Monitor Logs**: Watch the output for any errors or warnings
4. **Keep Dependencies Updated**: Regularly update your Python packages
5. **Backup Configuration**: Keep backups of your service configurations

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check the service logs for specific error messages
4. Ensure your database and dependencies are properly configured

## 🔗 Related Files

- `start_all_services.py` - Main Python script
- `start_all_services.bat` - Windows batch file
- `start_all_services.ps1` - PowerShell script
- `requirements.txt` - Python dependencies
- `config.py` - Configuration settings 
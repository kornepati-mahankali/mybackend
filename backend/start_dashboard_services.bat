@echo off
echo 🚀 Starting Dashboard Services...
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import fastapi, uvicorn, websockets, pymysql, psutil" >nul 2>&1
if errorlevel 1 (
    echo ❌ Missing required packages. Installing...
    pip install fastapi uvicorn websockets pymysql psutil
    if errorlevel 1 (
        echo ❌ Failed to install required packages
        pause
        exit /b 1
    )
)

REM Start the dashboard services
echo Starting Dashboard API server on port 8001...
start "Dashboard API" cmd /k "python -m uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

echo Starting Dashboard WebSocket server on port 8002...
start "Dashboard WebSocket" cmd /k "python dashboard_websocket.py"

echo ✅ Dashboard services started successfully!
echo 📊 Dashboard API: http://localhost:8001
echo 🔌 WebSocket: ws://localhost:8002
echo 📖 API Docs: http://localhost:8001/docs
echo ==================================================
echo Press any key to stop all services...
pause >nul

REM Stop all services
taskkill /f /im python.exe >nul 2>&1
echo ✅ Dashboard services stopped
pause 
@echo off
echo ========================================
echo    Lavangam Backend Services Starter
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the backend directory
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

echo Starting all backend services...
echo.
echo Services that will be started:
echo - Main API (Port 8000)
echo - Scrapers API (Port 5022) 
echo - System Usage API (Port 5024)
echo - Dashboard API (Port 8004)
echo - File Manager (Port 5000)
echo - Scraper WebSocket (Port 5001)
echo - Admin Metrics API (Port 5025)
echo - E-Procurement Server (Port 5002)
echo - Dashboard WebSocket (Port 8765)
echo.

REM Start the Python script
python start_all_services.py

echo.
echo All services have been stopped.
pause 
@echo off
echo ========================================
echo    Lavangam Service Health Checker
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
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

echo Checking all backend services...
echo.

REM Run the health check
python check_services.py

echo.
pause 
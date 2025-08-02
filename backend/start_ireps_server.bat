@echo off
echo ========================================
echo    IREPS Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found. Starting IREPS server...
echo.

REM Change to the backend directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
    echo Consider creating a virtual environment for better dependency management.
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting IREPS backend server...
echo Server will be available at: http://localhost:5022
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python start_ireps_server.py

echo.
echo Server stopped.
pause 
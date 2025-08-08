# Lavangam Backend Services Starter (PowerShell)
# This script starts all the required backend services

param(
    [switch]$Verbose,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Lavangam Backend Services Starter

Usage:
    .\start_all_services.ps1 [-Verbose] [-Help]

Options:
    -Verbose    Show detailed output
    -Help       Show this help message

This script will start the following services:
- Main API (Port 8000)
- Scrapers API (Port 5022) 
- System Usage API (Port 5024)
- Dashboard API (Port 8004)
- File Manager (Port 5000)
- Scraper WebSocket (Port 5001)
- Admin Metrics API (Port 5025)
- E-Procurement Server (Port 5002)
- Dashboard WebSocket (Port 8765)

Press Ctrl+C to stop all services.
"@
    exit 0
}

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Lavangam Backend Services Starter" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($Verbose) {
        Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the backend directory
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the backend directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting all backend services..." -ForegroundColor Yellow
Write-Host ""

# Show services that will be started
$services = @(
    "Main API (Port 8000)",
    "Scrapers API (Port 5022)",
    "System Usage API (Port 5024)", 
    "Dashboard API (Port 8004)",
    "File Manager (Port 5000)",
    "Scraper WebSocket (Port 5001)",
    "Admin Metrics API (Port 5025)",
    "E-Procurement Server (Port 5002)",
    "Dashboard WebSocket (Port 8765)"
)

Write-Host "Services that will be started:" -ForegroundColor Cyan
foreach ($service in $services) {
    Write-Host "  - $service" -ForegroundColor White
}
Write-Host ""

# Start the Python script
try {
    if ($Verbose) {
        Write-Host "Running: python start_all_services.py" -ForegroundColor Yellow
    }
    python start_all_services.py
} catch {
    Write-Host "ERROR: Failed to start services" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "All services have been stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
} 
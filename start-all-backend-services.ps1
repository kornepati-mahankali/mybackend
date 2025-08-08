# Start All Backend Services
# This script starts all the backend services you mentioned

Write-Host "🚀 Starting All Backend Services..." -ForegroundColor Green

# Function to start a service in a new window
function Start-ServiceInWindow {
    param(
        [string]$ServiceName,
        [string]$Command,
        [string]$WorkingDirectory = "backend"
    )
    
    Write-Host "📡 Starting $ServiceName..." -ForegroundColor Yellow
    
    # Start the service in a new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkingDirectory'; $Command" -WindowStyle Normal
    
    # Wait a moment for the service to start
    Start-Sleep -Seconds 2
}

# Navigate to backend directory
Set-Location backend

# Start main FastAPI server
Start-ServiceInWindow "Main FastAPI Server" "uvicorn main:app --reload --port 8000"

# Start scrapers API
Start-ServiceInWindow "Scrapers API" "uvicorn scrapers.api:app --reload --port 5022"

# Start system usage API
Start-ServiceInWindow "System Usage API" "uvicorn system_usage_api:app --reload --port 5024"

# Start dashboard API
Start-ServiceInWindow "Dashboard API" "python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8004"

# Start other services
Start-ServiceInWindow "File Manager" "python file_manager.py"
Start-ServiceInWindow "Scraper WebSocket" "python scraper_ws.py"
Start-ServiceInWindow "Admin Metrics API" "python admin_metrics_api.py"
Start-ServiceInWindow "E-Procurement Server" "python eproc_server_fixed.py"
Start-ServiceInWindow "Dashboard WebSocket" "python dashboard_websocket.py"

Write-Host "`n✅ All services started!" -ForegroundColor Green
Write-Host "`n📊 Service URLs:" -ForegroundColor Cyan
Write-Host "   Main API: http://localhost:8000" -ForegroundColor White
Write-Host "   Scrapers API: http://localhost:5022" -ForegroundColor White
Write-Host "   System Usage API: http://localhost:5024" -ForegroundColor White
Write-Host "   Dashboard API: http://localhost:8004" -ForegroundColor White

Write-Host "`n🔍 Test the main backend:" -ForegroundColor Yellow
Write-Host "   .\test-backend-connection.ps1" -ForegroundColor White

# Go back to root directory
Set-Location ..

Write-Host "`n💡 To stop all services, close the PowerShell windows or use Ctrl+C in each window" -ForegroundColor Yellow 
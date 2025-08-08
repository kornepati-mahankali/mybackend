# Simple Backend Start Script
Write-Host "Starting Unified Backend..." -ForegroundColor Green

# Go to backend directory
Set-Location backend

# Test API
Write-Host "Testing unified API..." -ForegroundColor Yellow
try {
    python -c "from unified_api import app; print('API ready')"
    Write-Host "API test passed" -ForegroundColor Green
} catch {
    Write-Host "API test failed" -ForegroundColor Red
    exit 1
}

# Start server
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

uvicorn unified_api:app --host 0.0.0.0 --port 8000 --reload

# Go back
Set-Location .. 
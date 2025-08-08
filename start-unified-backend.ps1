# Start Unified Backend (All Services Combined)
# This script starts the unified backend that includes all your services

Write-Host "🚀 Starting Unified Backend (All Services Combined)..." -ForegroundColor Green
Write-Host "📦 This includes all your services in one deployment:" -ForegroundColor Cyan
Write-Host "   • Main API (port 8000)" -ForegroundColor White
Write-Host "   • Scrapers API (port 5022)" -ForegroundColor White
Write-Host "   • System Usage API (port 5024)" -ForegroundColor White
Write-Host "   • Dashboard API (port 8004)" -ForegroundColor White

# Navigate to backend directory
Set-Location backend

# Test if unified API can be imported
Write-Host "`n🧪 Testing unified API..." -ForegroundColor Yellow
try {
    python -c "from unified_api import app; print('✅ Unified API ready')"
} catch {
    Write-Host "❌ Unified API test failed. Please check the code." -ForegroundColor Red
    exit 1
}

# Start the unified backend
Write-Host "`n📡 Starting unified backend server..." -ForegroundColor Yellow
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "💚 Health Check: http://localhost:8000/health" -ForegroundColor Cyan

Write-Host "`n📊 Service Endpoints:" -ForegroundColor Cyan
Write-Host "   Main API: http://localhost:8000/main" -ForegroundColor White
Write-Host "   Scrapers API: http://localhost:8000/scrapers" -ForegroundColor White
Write-Host "   System API: http://localhost:8000/system" -ForegroundColor White
Write-Host "   Dashboard API: http://localhost:8000/dashboard" -ForegroundColor White

Write-Host "`n⏹️ Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Start the server
uvicorn unified_api:app --host 0.0.0.0 --port 8000 --reload

# Go back to root directory
Set-Location .. 
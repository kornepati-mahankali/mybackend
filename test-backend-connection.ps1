# Test Backend Connection
# This script tests if your backend is accessible

param(
    [string]$BackendUrl = "http://localhost:8000"
)

Write-Host "🔍 Testing Backend Connection..." -ForegroundColor Green
Write-Host "🌐 Backend URL: $BackendUrl" -ForegroundColor Cyan

# Test basic connectivity
try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend is accessible!" -ForegroundColor Green
    Write-Host "📊 Health check passed: $($response.message)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Backend connection failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Test if the server is running at all
    try {
        $pingResponse = Invoke-WebRequest -Uri "$BackendUrl" -Method GET -TimeoutSec 5
        Write-Host "⚠️ Server is running but health endpoint not found" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Server is not running or not accessible" -ForegroundColor Red
        Write-Host "💡 Make sure your backend is running with: uvicorn unified_api:app --reload --port 8000" -ForegroundColor Yellow
    }
}

# Test CORS headers
Write-Host "`n🔍 Testing CORS headers..." -ForegroundColor Green
try {
    $corsResponse = Invoke-WebRequest -Uri "$BackendUrl/health" -Method OPTIONS -TimeoutSec 5
    Write-Host "✅ CORS headers are configured" -ForegroundColor Green
} catch {
    Write-Host "⚠️ CORS test failed (this might be normal)" -ForegroundColor Yellow
}

# Test individual services
Write-Host "`n🔍 Testing individual services..." -ForegroundColor Green
$services = @("main", "scrapers", "system", "dashboard")
foreach ($service in $services) {
    try {
        $serviceResponse = Invoke-WebRequest -Uri "$BackendUrl/$service" -Method GET -TimeoutSec 5
        Write-Host "✅ $service service is accessible" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ $service service test failed" -ForegroundColor Yellow
    }
}

Write-Host "`n🎯 Next steps:" -ForegroundColor Green
Write-Host "1. If localhost test failed, start your backend: uvicorn unified_api:app --reload --port 8000" -ForegroundColor Yellow
Write-Host "2. If you're testing AWS deployment, update the BackendUrl parameter" -ForegroundColor Yellow
Write-Host "3. Update your frontend API_BASE_URL to match the working backend URL" -ForegroundColor Yellow 
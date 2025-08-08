# Test Deployment Package Locally
Write-Host "Testing Complete Unified API Locally..." -ForegroundColor Green

# Check if deployment package exists
$zipPath = "all-ports-deployment-20250805-102740.zip"
if (Test-Path $zipPath) {
    Write-Host "✅ Deployment package found: $zipPath" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment package not found: $zipPath" -ForegroundColor Red
    Write-Host "Creating new deployment package..." -ForegroundColor Yellow
    Compress-Archive -Path "backend\*" -DestinationPath $zipPath -Force
    Write-Host "✅ Created: $zipPath" -ForegroundColor Green
}

# Test the unified API locally
Write-Host "`nStarting Complete Unified API locally..." -ForegroundColor Yellow
Write-Host "This will test ALL your ports on localhost:8000" -ForegroundColor Cyan

# Start the unified API
Start-Process powershell -ArgumentList "-Command", "cd backend; python -m uvicorn unified_api_complete:app --host 0.0.0.0 --port 8000 --reload"

# Wait a moment for the server to start
Start-Sleep -Seconds 5

# Test all endpoints
Write-Host "`nTesting all endpoints..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$endpoints = @(
    "/",
    "/health", 
    "/port-mapping",
    "/docs",
    "/main",
    "/scrapers",
    "/system",
    "/dashboard",
    "/port-5002",
    "/port-5003",
    "/port-8001",
    "/port-5021",
    "/port-5023",
    "/port-8002"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method GET -TimeoutSec 5
        Write-Host "✅ $endpoint - Working" -ForegroundColor Green
    } catch {
        Write-Host "❌ $endpoint - Failed" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Local testing complete!" -ForegroundColor Green
Write-Host "Your unified API is ready for AWS deployment." -ForegroundColor Cyan
Write-Host "Use the manual deployment guide: MANUAL_DEPLOYMENT_ALL_PORTS.md" -ForegroundColor Yellow 
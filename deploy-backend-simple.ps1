# Simple Backend Deployment to AWS
Write-Host "Deploying Backend to AWS..." -ForegroundColor Green

# Check EB CLI
try {
    eb --version
    Write-Host "EB CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "EB CLI not found. Install with: pip install awsebcli" -ForegroundColor Red
    exit 1
}

# Go to backend directory
Set-Location backend

# Test unified API
Write-Host "Testing unified API..." -ForegroundColor Yellow
try {
    python -c "from unified_api import app; print('Unified API ready')"
    Write-Host "Unified API test passed" -ForegroundColor Green
} catch {
    Write-Host "Unified API test failed" -ForegroundColor Red
    exit 1
}

# Initialize EB if needed
if (-not (Test-Path ".elasticbeanstalk")) {
    Write-Host "Initializing EB application..." -ForegroundColor Yellow
    eb init lavangam-backend --platform python-3.11 --region us-west-2
}

# Create environment
Write-Host "Creating EB environment..." -ForegroundColor Yellow
eb create lavangam-env --instance-type t3.medium --single-instance

# Deploy
Write-Host "Deploying..." -ForegroundColor Yellow
eb deploy

# Get URL
$appUrl = eb status | Select-String "CNAME" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Backend URL: https://$appUrl" -ForegroundColor Cyan
Write-Host "Health Check: https://$appUrl/health" -ForegroundColor Cyan

# Go back
Set-Location .. 
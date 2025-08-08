# Deploy All Backend Services to AWS Elastic Beanstalk
# This script deploys the unified backend that includes all your services

Write-Host "🚀 Deploying All Backend Services to AWS..." -ForegroundColor Green
Write-Host "📦 Services included:" -ForegroundColor Cyan
Write-Host "   • Main API (port 8000)" -ForegroundColor White
Write-Host "   • Scrapers API (port 5022)" -ForegroundColor White
Write-Host "   • System Usage API (port 5024)" -ForegroundColor White
Write-Host "   • Dashboard API (port 8004)" -ForegroundColor White
Write-Host "   • File Manager" -ForegroundColor White
Write-Host "   • Scraper WebSocket" -ForegroundColor White
Write-Host "   • Admin Metrics API" -ForegroundColor White
Write-Host "   • E-Procurement Server" -ForegroundColor White
Write-Host "   • Dashboard WebSocket" -ForegroundColor White

# Check if EB CLI is installed
try {
    eb --version
    Write-Host "✅ EB CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ EB CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "pip install awsebcli" -ForegroundColor Yellow
    exit 1
}

# Navigate to backend directory
Set-Location backend

# Test the unified API locally first
Write-Host "`n🧪 Testing unified API locally..." -ForegroundColor Yellow
try {
    python -c "from unified_api import app; print('✅ Unified API imports successfully')"
    Write-Host "✅ Unified API is ready for deployment" -ForegroundColor Green
} catch {
    Write-Host "❌ Unified API test failed. Please check the code." -ForegroundColor Red
    exit 1
}

# Initialize EB application if not already done
if (-not (Test-Path ".elasticbeanstalk")) {
    Write-Host "`n📝 Initializing Elastic Beanstalk application..." -ForegroundColor Yellow
    eb init lavangam-unified-backend --platform python-3.11 --region us-west-2
}

# Create environment if it doesn't exist
Write-Host "`n🌍 Creating/updating Elastic Beanstalk environment..." -ForegroundColor Yellow
eb create lavangam-unified-env --instance-type t3.medium --single-instance

# Deploy the application
Write-Host "`n📦 Deploying unified application..." -ForegroundColor Yellow
eb deploy

# Get the application URL
Write-Host "`n🔗 Getting application URL..." -ForegroundColor Yellow
$appUrl = eb status | Select-String "CNAME" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }

Write-Host "`n✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your unified backend is now available at: https://$appUrl" -ForegroundColor Cyan

Write-Host "`n📊 Service Endpoints:" -ForegroundColor Cyan
Write-Host "   Main API: https://$appUrl/main" -ForegroundColor White
Write-Host "   Scrapers API: https://$appUrl/scrapers" -ForegroundColor White
Write-Host "   System API: https://$appUrl/system" -ForegroundColor White
Write-Host "   Dashboard API: https://$appUrl/dashboard" -ForegroundColor White
Write-Host "   Health Check: https://$appUrl/health" -ForegroundColor White
Write-Host "   Documentation: https://$appUrl/docs" -ForegroundColor White

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update your frontend API_BASE_URL to: https://$appUrl" -ForegroundColor White
Write-Host "2. Test the endpoints using the test script" -ForegroundColor White
Write-Host "3. Update mobile app configuration if needed" -ForegroundColor White

# Go back to root directory
Set-Location ..

Write-Host "`n🎯 To test the deployment:" -ForegroundColor Green
Write-Host "   .\test-backend-connection.ps1 -BackendUrl 'https://$appUrl'" -ForegroundColor White 
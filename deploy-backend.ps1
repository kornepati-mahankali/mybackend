# Deploy Backend to AWS Elastic Beanstalk
# Make sure you have AWS CLI and EB CLI installed

Write-Host "🚀 Deploying Backend to AWS Elastic Beanstalk..." -ForegroundColor Green

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

# Initialize EB application if not already done
if (-not (Test-Path ".elasticbeanstalk")) {
    Write-Host "📝 Initializing Elastic Beanstalk application..." -ForegroundColor Yellow
    eb init lavangam-backend --platform python-3.11 --region us-west-2
}

# Create environment if it doesn't exist
Write-Host "🌍 Creating/updating Elastic Beanstalk environment..." -ForegroundColor Yellow
eb create lavangam-backend-env --instance-type t3.small --single-instance

# Deploy the application
Write-Host "📦 Deploying application..." -ForegroundColor Yellow
eb deploy

# Get the application URL
Write-Host "🔗 Getting application URL..." -ForegroundColor Yellow
$appUrl = eb status | Select-String "CNAME" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your backend is now available at: https://$appUrl" -ForegroundColor Cyan
Write-Host "📝 Update your frontend API_BASE_URL to: https://$appUrl" -ForegroundColor Yellow

# Go back to root directory
Set-Location .. 
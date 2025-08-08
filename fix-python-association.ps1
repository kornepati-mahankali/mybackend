# Fix Python File Association and AWS Setup Script
Write-Host "🔧 Fixing Python File Association and AWS Setup..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script needs to be run as Administrator to fix file associations." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host "Alternatively, you can manually fix this through Windows Settings:" -ForegroundColor Cyan
    Write-Host "1. Open Settings > Apps > Default apps" -ForegroundColor White
    Write-Host "2. Click 'Choose default apps by file type'" -ForegroundColor White
    Write-Host "3. Find '.py' and set it to Python" -ForegroundColor White
} else {
    Write-Host "✅ Running as Administrator - attempting to fix file association..." -ForegroundColor Green
    
    # Try to fix file association
    try {
        & cmd /c "assoc .py=Python.File"
        Write-Host "✅ File association fixed!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not fix file association automatically" -ForegroundColor Red
    }
}

# Alternative: Create a batch file to run Python scripts
Write-Host "📝 Creating alternative Python runner..." -ForegroundColor Yellow

$pythonRunner = @"
@echo off
python "%~f0" %*
pause
"@

$pythonRunner | Out-File -FilePath "run-python.bat" -Encoding ASCII

Write-Host "✅ Created run-python.bat - you can use this to run Python scripts" -ForegroundColor Green

# Check AWS CLI installation
Write-Host "🔍 Checking AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI is installed: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Installing..." -ForegroundColor Red
    
    # Install AWS CLI using winget
    try {
        winget install Amazon.AWSCLI
        Write-Host "✅ AWS CLI installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not install AWS CLI automatically" -ForegroundColor Red
        Write-Host "Please install manually from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    }
}

# Check AWS configuration
Write-Host "🔍 Checking AWS configuration..." -ForegroundColor Yellow
try {
    $awsConfig = aws configure list
    Write-Host "✅ AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not configured. Please run: aws configure" -ForegroundColor Red
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. If file association is still broken, fix it manually in Windows Settings" -ForegroundColor White
Write-Host "2. Configure AWS CLI: aws configure" -ForegroundColor White
Write-Host "3. Test Python: python --version" -ForegroundColor White
Write-Host "4. Test AWS: aws s3 ls" -ForegroundColor White 
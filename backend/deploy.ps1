Write-Host "Starting deployment to AWS Elastic Beanstalk..." -ForegroundColor Green

# Check if we're in the backend directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Error: Please run this script from the backend directory" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow

# Remove old deployment package if it exists
if (Test-Path "deployment.zip") {
    Remove-Item "deployment.zip" -Force
    Write-Host "Removed old deployment.zip" -ForegroundColor Yellow
}

# Create new deployment package
try {
    Compress-Archive -Path ".\*" -DestinationPath "deployment.zip" -Force
    Write-Host "Deployment package created: deployment.zip" -ForegroundColor Green
    
    # Check package size
    $packageSize = (Get-Item "deployment.zip").Length
    Write-Host "Package size: $packageSize bytes" -ForegroundColor Cyan
    
    # List contents
    Write-Host "Package contents:" -ForegroundColor Cyan
    $contents = Get-ChildItem -Path "deployment.zip" | Select-Object -First 10
    foreach ($item in $contents) {
        Write-Host "   - $($item.Name)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Error creating deployment package: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Upload deployment.zip to AWS Elastic Beanstalk" -ForegroundColor White
Write-Host "2. Or use: eb deploy (if you have EB CLI configured)" -ForegroundColor White
Write-Host "3. Monitor the deployment in the AWS Console" -ForegroundColor White
Write-Host ""
Write-Host "To monitor deployment:" -ForegroundColor Yellow
Write-Host "   - Check /var/log/eb-engine.log on the EC2 instance" -ForegroundColor White
Write-Host "   - Check /var/log/cfn-init.log for configuration errors" -ForegroundColor White
Write-Host "   - Use: eb logs (if you have EB CLI)" -ForegroundColor White
Write-Host ""
Write-Host "Deployment package ready!" -ForegroundColor Green
Read-Host "Press Enter to continue" 
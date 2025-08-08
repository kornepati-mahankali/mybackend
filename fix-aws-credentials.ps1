# Fix AWS Credentials Script
Write-Host "Fixing AWS Credentials..." -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

Write-Host "`nCurrent AWS Configuration:" -ForegroundColor Yellow
aws configure list

Write-Host "`nIMPORTANT: Your Access Key ID and Secret Access Key appear to be swapped!" -ForegroundColor Red
Write-Host "The Access Key ID should start with 'AKIA' and be shorter" -ForegroundColor Yellow
Write-Host "The Secret Access Key should be longer (40+ characters)" -ForegroundColor Yellow

Write-Host "`nTo fix this:" -ForegroundColor Cyan
Write-Host "1. Go to AWS Console → IAM → Users → Your User" -ForegroundColor White
Write-Host "2. Click 'Security credentials' tab" -ForegroundColor White
Write-Host "3. Create new access key" -ForegroundColor White
Write-Host "4. Copy the correct Access Key ID and Secret Access Key" -ForegroundColor White

$fixNow = Read-Host "`nDo you want to configure AWS now? (y/n)"

if ($fixNow -eq "y" -or $fixNow -eq "Y") {
    Write-Host "`nConfiguring AWS CLI..." -ForegroundColor Yellow
    aws configure
} else {
    Write-Host "`nPlease run 'aws configure' manually when ready" -ForegroundColor Yellow
}

Write-Host "`nAfter fixing credentials, test with: aws sts get-caller-identity" -ForegroundColor Cyan 
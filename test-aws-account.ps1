# Test AWS Account and Credentials
Write-Host "Testing AWS Account and Credentials" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`nCurrent AWS Configuration:" -ForegroundColor Yellow
aws configure list

Write-Host "`nTesting AWS Connection..." -ForegroundColor Yellow
try {
    $result = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AWS connection successful!" -ForegroundColor Green
        Write-Host "Account details:" -ForegroundColor Cyan
        Write-Host $result -ForegroundColor White
    } else {
        Write-Host "❌ AWS connection failed!" -ForegroundColor Red
        Write-Host "Error: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ AWS connection failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n🔍 Analysis:" -ForegroundColor Cyan
Write-Host "Your current Access Key ID: mx6Q4hc" -ForegroundColor Yellow
Write-Host "This is NOT a valid AWS Access Key ID!" -ForegroundColor Red
Write-Host "Valid AWS Access Key IDs start with 'AKIA' and are 20 characters long" -ForegroundColor Yellow

Write-Host "`n📋 To Fix This:" -ForegroundColor Cyan
Write-Host "1. Go to https://aws.amazon.com/console/" -ForegroundColor White
Write-Host "2. Sign in to your AWS account" -ForegroundColor White
Write-Host "3. Search for 'IAM' and click on it" -ForegroundColor White
Write-Host "4. Click 'Users' → Your username → 'Security credentials'" -ForegroundColor White
Write-Host "5. Click 'Create access key'" -ForegroundColor White
Write-Host "6. Choose 'CLI' and create the key" -ForegroundColor White
Write-Host "7. Copy the new Access Key ID and Secret Access Key" -ForegroundColor White

Write-Host "`n💡 What Valid Credentials Look Like:" -ForegroundColor Cyan
Write-Host "Access Key ID: AKIAIOSFODNN7EXAMPLE" -ForegroundColor Green
Write-Host "Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" -ForegroundColor Green

$getNewCredentials = Read-Host "`nDo you want to configure new credentials now? (y/n)"

if ($getNewCredentials -eq "y" -or $getNewCredentials -eq "Y") {
    Write-Host "`nConfiguring new AWS credentials..." -ForegroundColor Yellow
    Write-Host "Please enter your NEW credentials from AWS Console:" -ForegroundColor Cyan
    aws configure
} else {
    Write-Host "`nPlease get new credentials from AWS Console first, then run:" -ForegroundColor Yellow
    Write-Host "aws configure" -ForegroundColor Cyan
}

Write-Host "`nAfter getting new credentials, test with:" -ForegroundColor Cyan
Write-Host "aws sts get-caller-identity" -ForegroundColor White 
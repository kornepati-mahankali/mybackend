# Simple AWS Test
Write-Host "Testing AWS Access..." -ForegroundColor Green

# Test basic access
Write-Host "Testing basic AWS access..." -ForegroundColor Yellow
aws sts get-caller-identity

# Test S3
Write-Host "Testing S3..." -ForegroundColor Yellow
aws s3 ls

# Test EB
Write-Host "Testing Elastic Beanstalk..." -ForegroundColor Yellow
aws elasticbeanstalk describe-applications --region us-west-2

Write-Host "Test completed!" -ForegroundColor Green 
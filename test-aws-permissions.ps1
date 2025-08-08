# Test AWS Permissions
Write-Host "Testing AWS Permissions..." -ForegroundColor Green

# Test 1: Basic AWS access
Write-Host "`n1. Testing basic AWS access..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity
    Write-Host "✅ AWS credentials working" -ForegroundColor Green
    Write-Host "User: $identity" -ForegroundColor Cyan
} catch {
    Write-Host "❌ AWS credentials not working" -ForegroundColor Red
    Write-Host "Run: aws configure" -ForegroundColor Yellow
    exit 1
}

# Test 2: S3 access
Write-Host "`n2. Testing S3 access..." -ForegroundColor Yellow
try {
    aws s3 ls
    Write-Host "✅ S3 access working" -ForegroundColor Green
} catch {
    Write-Host "❌ S3 access denied" -ForegroundColor Red
    Write-Host "Need S3 permissions" -ForegroundColor Yellow
}

# Test 3: Elastic Beanstalk access
Write-Host "`n3. Testing Elastic Beanstalk access..." -ForegroundColor Yellow
try {
    aws elasticbeanstalk describe-applications --region us-west-2
    Write-Host "✅ Elastic Beanstalk access working" -ForegroundColor Green
} catch {
    Write-Host "❌ Elastic Beanstalk access denied" -ForegroundColor Red
    Write-Host "Need Elastic Beanstalk permissions" -ForegroundColor Yellow
}

# Test 4: IAM access
Write-Host "`n4. Testing IAM access..." -ForegroundColor Yellow
try {
    aws iam list-policies --scope AWS --max-items 5
    Write-Host "✅ IAM access working" -ForegroundColor Green
} catch {
    Write-Host "❌ IAM access denied" -ForegroundColor Red
    Write-Host "Need IAM permissions" -ForegroundColor Yellow
}

Write-Host "`n📋 Summary:" -ForegroundColor Green
Write-Host "If you see ❌ errors above, you need to add permissions." -ForegroundColor Yellow
Write-Host "Follow the guide in: AWS_PERMISSIONS_FIX.md" -ForegroundColor Cyan
Write-Host "Or use manual console deployment." -ForegroundColor Cyan 
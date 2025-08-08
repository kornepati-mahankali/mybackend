# Deploy Backend using AWS CLI
Write-Host "Deploying Backend to AWS using AWS CLI..." -ForegroundColor Green

# Check AWS CLI
try {
    aws --version
    Write-Host "AWS CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI not found. Please install it first." -ForegroundColor Red
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

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipName = "backend-deployment-$timestamp.zip"

# Create zip file
Compress-Archive -Path * -DestinationPath "../$zipName" -Force
Write-Host "Created deployment package: $zipName" -ForegroundColor Green

# Upload to S3 (you'll need to create a bucket first)
$bucketName = "lavangam-backend-deployments"
Write-Host "Uploading to S3 bucket: $bucketName" -ForegroundColor Yellow

try {
    aws s3 cp "../$zipName" "s3://$bucketName/"
    Write-Host "Uploaded to S3 successfully" -ForegroundColor Green
} catch {
    Write-Host "S3 upload failed. Creating bucket first..." -ForegroundColor Yellow
    aws s3 mb "s3://$bucketName" --region us-west-2
    aws s3 cp "../$zipName" "s3://$bucketName/"
}

# Create Elastic Beanstalk application version
Write-Host "Creating EB application version..." -ForegroundColor Yellow
$appName = "lavangam-backend"
$versionLabel = "v-$timestamp"

aws elasticbeanstalk create-application-version `
    --application-name $appName `
    --version-label $versionLabel `
    --source-bundle S3Bucket=$bucketName,S3Key=$zipName `
    --region us-west-2

# Create environment if it doesn't exist
Write-Host "Creating EB environment..." -ForegroundColor Yellow
$envName = "lavangam-backend-env"

aws elasticbeanstalk create-environment `
    --application-name $appName `
    --environment-name $envName `
    --version-label $versionLabel `
    --solution-stack-name "64bit Amazon Linux 2 v3.5.0 running Python 3.11" `
    --option-settings "Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=aws-elasticbeanstalk-ec2-role" `
    --region us-west-2

Write-Host "Deployment initiated!" -ForegroundColor Green
Write-Host "Check AWS Console for deployment status" -ForegroundColor Yellow
Write-Host "Application: $appName" -ForegroundColor Cyan
Write-Host "Environment: $envName" -ForegroundColor Cyan
Write-Host "Version: $versionLabel" -ForegroundColor Cyan

# Go back
Set-Location .. 
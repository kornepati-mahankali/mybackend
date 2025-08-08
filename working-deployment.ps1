# Working AWS Deployment Script
Write-Host "Starting AWS Deployment..." -ForegroundColor Green

# Check AWS access
Write-Host "Checking AWS access..." -ForegroundColor Yellow
aws sts get-caller-identity

# Create S3 bucket
$bucketName = "lavangam-backend-deployments-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "Creating S3 bucket: $bucketName" -ForegroundColor Yellow
aws s3 mb "s3://$bucketName" --region us-west-2

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Set-Location backend
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipName = "backend-deployment-$timestamp.zip"
Compress-Archive -Path * -DestinationPath "../$zipName" -Force
Write-Host "Created: $zipName" -ForegroundColor Green

# Upload to S3
Write-Host "Uploading to S3..." -ForegroundColor Yellow
aws s3 cp "../$zipName" "s3://$bucketName/"
Write-Host "Uploaded successfully" -ForegroundColor Green

# Create EB application
Write-Host "Creating EB application..." -ForegroundColor Yellow
$appName = "lavangam-backend"
aws elasticbeanstalk create-application --application-name $appName --region us-west-2

# Create application version
Write-Host "Creating application version..." -ForegroundColor Yellow
$versionLabel = "v-$timestamp"
aws elasticbeanstalk create-application-version `
    --application-name $appName `
    --version-label $versionLabel `
    --source-bundle S3Bucket=$bucketName,S3Key=$zipName `
    --region us-west-2

# Create environment
Write-Host "Creating EB environment..." -ForegroundColor Yellow
$envName = "lavangam-backend-env"

# Use Python 3.9 stack
aws elasticbeanstalk create-environment `
    --application-name $appName `
    --environment-name $envName `
    --version-label $versionLabel `
    --solution-stack-name "64bit Amazon Linux 2 v3.4.0 running Python 3.9" `
    --region us-west-2

Write-Host "Deployment initiated!" -ForegroundColor Green
Write-Host "Check AWS Console: https://console.aws.amazon.com/elasticbeanstalk/" -ForegroundColor Cyan
Write-Host "Application: $appName" -ForegroundColor White
Write-Host "Environment: $envName" -ForegroundColor White
Write-Host "S3 Bucket: $bucketName" -ForegroundColor White

Set-Location .. 
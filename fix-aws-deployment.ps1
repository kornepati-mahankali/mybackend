# Fix AWS Deployment Issues
Write-Host "Fixing AWS Deployment Issues..." -ForegroundColor Green

# Check AWS CLI
try {
    aws --version
    Write-Host "AWS CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Check AWS credentials
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity
    Write-Host "AWS credentials are configured" -ForegroundColor Green
} catch {
    Write-Host "AWS credentials not configured. Please run: aws configure" -ForegroundColor Red
    exit 1
}

# List available solution stacks
Write-Host "`nChecking available Python solution stacks..." -ForegroundColor Yellow
aws elasticbeanstalk list-available-solution-stacks --region us-west-2 | Select-String "Python"

# Create S3 bucket with proper naming
$bucketName = "lavangam-backend-deployments-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "`nCreating S3 bucket: $bucketName" -ForegroundColor Yellow
aws s3 mb "s3://$bucketName" --region us-west-2

# Create deployment package
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
Set-Location backend
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipName = "backend-deployment-$timestamp.zip"
Compress-Archive -Path * -DestinationPath "../$zipName" -Force
Write-Host "Created: $zipName" -ForegroundColor Green

# Upload to S3
Write-Host "`nUploading to S3..." -ForegroundColor Yellow
aws s3 cp "../$zipName" "s3://$bucketName/"
Write-Host "Uploaded successfully" -ForegroundColor Green

# Create EB application
Write-Host "`nCreating EB application..." -ForegroundColor Yellow
$appName = "lavangam-backend"
aws elasticbeanstalk create-application --application-name $appName --region us-west-2

# Create application version
Write-Host "`nCreating application version..." -ForegroundColor Yellow
$versionLabel = "v-$timestamp"
aws elasticbeanstalk create-application-version `
    --application-name $appName `
    --version-label $versionLabel `
    --source-bundle S3Bucket=$bucketName,S3Key=$zipName `
    --region us-west-2

# Create environment with correct solution stack
Write-Host "`nCreating EB environment..." -ForegroundColor Yellow
$envName = "lavangam-backend-env"

# Use a simpler solution stack name
aws elasticbeanstalk create-environment `
    --application-name $appName `
    --environment-name $envName `
    --version-label $versionLabel `
    --solution-stack-name "64bit Amazon Linux 2 v3.4.0 running Python 3.9" `
    --region us-west-2

Write-Host "`nDeployment initiated!" -ForegroundColor Green
Write-Host "Check AWS Console: https://console.aws.amazon.com/elasticbeanstalk/" -ForegroundColor Cyan
Write-Host "Application: $appName" -ForegroundColor White
Write-Host "Environment: $envName" -ForegroundColor White
Write-Host "S3 Bucket: $bucketName" -ForegroundColor White

Set-Location .. 
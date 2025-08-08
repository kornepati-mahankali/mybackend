# Deploy Fixed Version to AWS
Write-Host "Deploying Fixed Version to AWS..." -ForegroundColor Green

# Check AWS access
Write-Host "Checking AWS access..." -ForegroundColor Yellow
aws sts get-caller-identity

# Create S3 bucket
$bucketName = "lavangam-fixed-deployments-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "Creating S3 bucket: $bucketName" -ForegroundColor Yellow
aws s3 mb "s3://$bucketName" --region us-west-2

# Upload fixed deployment package
Write-Host "Uploading fixed deployment package..." -ForegroundColor Yellow
aws s3 cp "fixed-deployment.zip" "s3://$bucketName/"

# Create EB application
Write-Host "Creating EB application..." -ForegroundColor Yellow
$appName = "lavangam-fixed-backend"
aws elasticbeanstalk create-application --application-name $appName --region us-west-2

# Create application version
Write-Host "Creating application version..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$versionLabel = "v-$timestamp"
aws elasticbeanstalk create-application-version `
    --application-name $appName `
    --version-label $versionLabel `
    --source-bundle S3Bucket=$bucketName,S3Key="fixed-deployment.zip" `
    --region us-west-2

# Create environment
Write-Host "Creating EB environment..." -ForegroundColor Yellow
$envName = "lavangam-fixed-env"

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

Write-Host "After deployment, your services will be available at:" -ForegroundColor Cyan
Write-Host "Main API: https://your-eb-url.elasticbeanstalk.com/main" -ForegroundColor White
Write-Host "Scrapers API: https://your-eb-url.elasticbeanstalk.com/scrapers" -ForegroundColor White
Write-Host "System API: https://your-eb-url.elasticbeanstalk.com/system" -ForegroundColor White
Write-Host "Dashboard API: https://your-eb-url.elasticbeanstalk.com/dashboard" -ForegroundColor White
Write-Host "Health Check: https://your-eb-url.elasticbeanstalk.com/health" -ForegroundColor Green 
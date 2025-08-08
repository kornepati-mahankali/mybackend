# Deploy All Ports to AWS - Complete Solution
Write-Host "Deploying ALL Ports to AWS..." -ForegroundColor Green
Write-Host "This will deploy ALL your services:" -ForegroundColor Cyan
Write-Host "   • Port 8000 (Main API) → /main" -ForegroundColor White
Write-Host "   • Port 5022 (Scrapers API) → /scrapers" -ForegroundColor White
Write-Host "   • Port 5024 (System API) → /system" -ForegroundColor White
Write-Host "   • Port 8004 (Dashboard API) → /dashboard" -ForegroundColor White
Write-Host "   • Port 5002 → /port-5002" -ForegroundColor White
Write-Host "   • Port 5003 → /port-5003" -ForegroundColor White
Write-Host "   • Port 8001 → /port-8001" -ForegroundColor White
Write-Host "   • Port 5021 → /port-5021" -ForegroundColor White
Write-Host "   • Port 5023 → /port-5023" -ForegroundColor White
Write-Host "   • Port 8002 → /port-8002" -ForegroundColor White

# Check AWS access
Write-Host "`nChecking AWS access..." -ForegroundColor Yellow
aws sts get-caller-identity

# Create S3 bucket
$bucketName = "lavangam-all-ports-deployments-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "`nCreating S3 bucket: $bucketName" -ForegroundColor Yellow
aws s3 mb "s3://$bucketName" --region us-west-2

# Create deployment package
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
Set-Location backend
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipName = "all-ports-deployment-$timestamp.zip"
Compress-Archive -Path * -DestinationPath "../$zipName" -Force
Write-Host "Created: $zipName" -ForegroundColor Green

# Upload to S3
Write-Host "`nUploading to S3..." -ForegroundColor Yellow
aws s3 cp "../$zipName" "s3://$bucketName/"
Write-Host "Uploaded successfully" -ForegroundColor Green

# Create EB application
Write-Host "`nCreating EB application..." -ForegroundColor Yellow
$appName = "lavangam-all-ports-backend"
aws elasticbeanstalk create-application --application-name $appName --region us-west-2

# Create application version
Write-Host "`nCreating application version..." -ForegroundColor Yellow
$versionLabel = "v-$timestamp"
aws elasticbeanstalk create-application-version `
    --application-name $appName `
    --version-label $versionLabel `
    --source-bundle S3Bucket=$bucketName,S3Key=$zipName `
    --region us-west-2

# Create environment
Write-Host "`nCreating EB environment..." -ForegroundColor Yellow
$envName = "lavangam-all-ports-env"

# Use Python 3.9 stack
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

Write-Host "`nAfter deployment, your services will be available at:" -ForegroundColor Cyan
Write-Host "   Main API: https://your-eb-url.elasticbeanstalk.com/main" -ForegroundColor White
Write-Host "   Scrapers API: https://your-eb-url.elasticbeanstalk.com/scrapers" -ForegroundColor White
Write-Host "   System API: https://your-eb-url.elasticbeanstalk.com/system" -ForegroundColor White
Write-Host "   Dashboard API: https://your-eb-url.elasticbeanstalk.com/dashboard" -ForegroundColor White
Write-Host "   Port 5002: https://your-eb-url.elasticbeanstalk.com/port-5002" -ForegroundColor White
Write-Host "   Port 5003: https://your-eb-url.elasticbeanstalk.com/port-5003" -ForegroundColor White
Write-Host "   Port 8001: https://your-eb-url.elasticbeanstalk.com/port-8001" -ForegroundColor White
Write-Host "   Port 5021: https://your-eb-url.elasticbeanstalk.com/port-5021" -ForegroundColor White
Write-Host "   Port 5023: https://your-eb-url.elasticbeanstalk.com/port-5023" -ForegroundColor White
Write-Host "   Port 8002: https://your-eb-url.elasticbeanstalk.com/port-8002" -ForegroundColor White

Write-Host "`nHealth Check: https://your-eb-url.elasticbeanstalk.com/health" -ForegroundColor Green
Write-Host "Documentation: https://your-eb-url.elasticbeanstalk.com/docs" -ForegroundColor Green
Write-Host "Port Mapping: https://your-eb-url.elasticbeanstalk.com/port-mapping" -ForegroundColor Green

Set-Location .. 
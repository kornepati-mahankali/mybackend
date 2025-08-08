# Lavangam Project Deployment Script
Write-Host "Deploying Lavangam Project to AWS" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "`nChecking Prerequisites..." -ForegroundColor Yellow

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Check Node.js
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found in PATH" -ForegroundColor Red
    exit 1
}

# Check AWS CLI
if (Test-Command "aws") {
    $awsVersion = aws --version
    Write-Host "AWS CLI: $awsVersion" -ForegroundColor Green
} else {
    Write-Host "AWS CLI not found" -ForegroundColor Red
    exit 1
}

# Test AWS connection
Write-Host "`nTesting AWS Connection..." -ForegroundColor Yellow
try {
    $awsIdentity = aws sts get-caller-identity
    Write-Host "AWS connection successful!" -ForegroundColor Green
    Write-Host "Account: $($awsIdentity | ConvertFrom-Json | Select-Object -ExpandProperty Account)" -ForegroundColor Cyan
} catch {
    Write-Host "AWS connection failed!" -ForegroundColor Red
    Write-Host "Please fix your AWS credentials first." -ForegroundColor Yellow
    Write-Host "Run: .\fix-aws-credentials.ps1" -ForegroundColor Cyan
    exit 1
}

# Generate unique bucket name
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$bucketName = "lavangam-frontend-$timestamp"
$region = "us-east-1"

Write-Host "`nDeployment Configuration:" -ForegroundColor Cyan
Write-Host "Frontend Bucket: $bucketName" -ForegroundColor White
Write-Host "Region: $region" -ForegroundColor White

# Step 1: Create S3 Bucket
Write-Host "`nStep 1: Creating S3 Bucket..." -ForegroundColor Yellow
try {
    aws s3 mb s3://$bucketName --region $region
    Write-Host "S3 bucket created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to create S3 bucket!" -ForegroundColor Red
    exit 1
}

# Step 2: Enable Static Website Hosting
Write-Host "`nStep 2: Enabling Static Website Hosting..." -ForegroundColor Yellow
try {
    aws s3 website s3://$bucketName --index-document index.html --error-document index.html
    Write-Host "Static website hosting enabled!" -ForegroundColor Green
} catch {
    Write-Host "Failed to enable static website hosting!" -ForegroundColor Red
    exit 1
}

# Step 3: Create Bucket Policy
Write-Host "`nStep 3: Creating Bucket Policy..." -ForegroundColor Yellow
$bucketPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$bucketName/*"
        }
    ]
}
"@

$bucketPolicy | Out-File -FilePath "s3-bucket-policy.json" -Encoding UTF8
try {
    aws s3api put-bucket-policy --bucket $bucketName --policy file://s3-bucket-policy.json
    Write-Host "Bucket policy applied successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to apply bucket policy!" -ForegroundColor Red
    exit 1
}

# Step 4: Build Frontend
Write-Host "`nStep 4: Building Frontend..." -ForegroundColor Yellow
try {
    npm run build
    if (Test-Path "dist") {
        Write-Host "Frontend built successfully!" -ForegroundColor Green
    } else {
        Write-Host "Build failed - dist folder not found!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}

# Step 5: Deploy Frontend to S3
Write-Host "`nStep 5: Deploying Frontend to S3..." -ForegroundColor Yellow
try {
    aws s3 sync dist/ s3://$bucketName --delete --region $region
    Write-Host "Frontend deployed to S3 successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to deploy frontend to S3!" -ForegroundColor Red
    exit 1
}

# Step 6: Deploy Backend (Optional)
$deployBackend = Read-Host "`nDo you want to deploy the backend to Elastic Beanstalk? (y/n)"

if ($deployBackend -eq "y" -or $deployBackend -eq "Y") {
    Write-Host "`nStep 6: Deploying Backend..." -ForegroundColor Yellow
    
    # Check if EB CLI is installed
    if (-not (Test-Command "eb")) {
        Write-Host "Installing EB CLI..." -ForegroundColor Yellow
        python -m pip install awsebcli
    }
    
    Set-Location backend
    
    # Check if EB is initialized
    if (-not (Test-Path ".elasticbeanstalk")) {
        Write-Host "Initializing Elastic Beanstalk..." -ForegroundColor Yellow
        eb init
    }
    
    $envName = Read-Host "Enter your EB environment name (or press Enter for 'lavangam-backend')"
    if (-not $envName) {
        $envName = "lavangam-backend"
    }
    
    Write-Host "Deploying to Elastic Beanstalk environment: $envName" -ForegroundColor Yellow
    try {
        eb deploy $envName
        Write-Host "Backend deployed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Backend deployment failed!" -ForegroundColor Red
    }
    
    Set-Location ..
}

# Success Message
Write-Host "`n🎉 Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Frontend URL: https://$bucketName.s3-website-$region.amazonaws.com" -ForegroundColor Cyan

if ($deployBackend -eq "y" -or $deployBackend -eq "Y") {
    Write-Host "Backend URL: http://$envName.elasticbeanstalk.com" -ForegroundColor Cyan
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Test your frontend at the URL above" -ForegroundColor White
Write-Host "2. Update your frontend API endpoints to point to your backend" -ForegroundColor White
Write-Host "3. Consider setting up CloudFront for better performance" -ForegroundColor White
Write-Host "4. Set up monitoring and logging" -ForegroundColor White

# Clean up temporary files
if (Test-Path "s3-bucket-policy.json") {
    Remove-Item "s3-bucket-policy.json"
} 
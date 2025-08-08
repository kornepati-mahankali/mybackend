# Simplified AWS Deployment Script (PowerShell)
# This script works around Python file association issues

Write-Host "Simplified AWS Deployment Script" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function definitions
function Deploy-Frontend {
    Write-Host "Building frontend..." -ForegroundColor Yellow
    npm run build
    
    if (-not (Test-Path "dist")) {
        Write-Host "Build failed!" -ForegroundColor Red
        return
    }
    
    $bucketName = Read-Host "Enter your S3 bucket name"
    $region = Read-Host "Enter your AWS region (default: us-east-1)" -DefaultValue "us-east-1"
    
    Write-Host "Deploying to S3..." -ForegroundColor Yellow
    aws s3 sync dist/ s3://$bucketName --delete --region $region
    
    Write-Host "Frontend deployed!" -ForegroundColor Green
    Write-Host "URL: https://$bucketName.s3-website-$region.amazonaws.com" -ForegroundColor Cyan
}

function Deploy-Backend {
    Write-Host "Preparing backend..." -ForegroundColor Yellow
    
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
    
    $envName = Read-Host "Enter your EB environment name"
    
    Write-Host "Deploying to Elastic Beanstalk..." -ForegroundColor Yellow
    eb deploy $envName
    
    Set-Location ..
    Write-Host "Backend deployed!" -ForegroundColor Green
}

function Setup-AWS-Resources {
    Write-Host "Setting up AWS Resources..." -ForegroundColor Yellow
    
    $bucketName = Read-Host "Enter desired S3 bucket name for frontend"
    $region = Read-Host "Enter your AWS region (default: us-east-1)" -DefaultValue "us-east-1"
    
    # Create S3 bucket
    Write-Host "Creating S3 bucket..." -ForegroundColor Yellow
    aws s3 mb s3://$bucketName --region $region
    
    # Enable static website hosting
    Write-Host "Enabling static website hosting..." -ForegroundColor Yellow
    aws s3 website s3://$bucketName --index-document index.html --error-document index.html
    
    # Create bucket policy
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
    aws s3api put-bucket-policy --bucket $bucketName --policy file://s3-bucket-policy.json
    
    Write-Host "AWS resources created!" -ForegroundColor Green
    Write-Host "Update your deployment scripts with:" -ForegroundColor Cyan
    Write-Host "   S3_BUCKET = `"$bucketName`"" -ForegroundColor White
    Write-Host "   REGION = `"$region`"" -ForegroundColor White
}

# Check prerequisites
Write-Host "`nChecking Prerequisites..." -ForegroundColor Yellow

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check AWS CLI
if (Test-Command "aws") {
    $awsVersion = aws --version
    Write-Host "AWS CLI: $awsVersion" -ForegroundColor Green
} else {
    Write-Host "AWS CLI not found" -ForegroundColor Red
    Write-Host "Installing AWS CLI..." -ForegroundColor Yellow
    try {
        winget install Amazon.AWSCLI
        Write-Host "AWS CLI installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Could not install AWS CLI automatically" -ForegroundColor Red
        Write-Host "Please install manually from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
        exit 1
    }
}

# Check AWS configuration
Write-Host "`nChecking AWS Configuration..." -ForegroundColor Yellow
try {
    $awsConfig = aws configure list
    Write-Host "AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI not configured" -ForegroundColor Red
    Write-Host "Please run: aws configure" -ForegroundColor Yellow
    Write-Host "You'll need your AWS Access Key ID and Secret Access Key" -ForegroundColor Cyan
    exit 1
}

# Test AWS connection
Write-Host "`nTesting AWS Connection..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity
    Write-Host "AWS connection successful!" -ForegroundColor Green
} catch {
    Write-Host "AWS connection failed" -ForegroundColor Red
    Write-Host "Please check your AWS credentials" -ForegroundColor Yellow
    exit 1
}

# Deployment Options
Write-Host "`nChoose Deployment Option:" -ForegroundColor Cyan
Write-Host "1. Frontend only (S3 + CloudFront)" -ForegroundColor White
Write-Host "2. Backend only (Elastic Beanstalk)" -ForegroundColor White
Write-Host "3. Both frontend and backend" -ForegroundColor White
Write-Host "4. Setup AWS resources only" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" { 
        Write-Host "`nDeploying Frontend..." -ForegroundColor Green
        Deploy-Frontend
    }
    "2" { 
        Write-Host "`nDeploying Backend..." -ForegroundColor Green
        Deploy-Backend
    }
    "3" { 
        Write-Host "`nDeploying Both..." -ForegroundColor Green
        Deploy-Frontend
        Deploy-Backend
    }
    "4" { 
        Write-Host "`nSetting up AWS Resources..." -ForegroundColor Green
        Setup-AWS-Resources
    }
    default { 
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nDeployment process completed!" -ForegroundColor Green 
# Lavangam Backend AWS Deployment Script (PowerShell)
# This script helps deploy Lavangam backend to AWS EC2 from Windows

param(
    [string]$KeyPairName,
    [string]$InstanceType = "t3.medium",
    [string]$Region = "us-west-2",
    [string]$StackName = "lavangam-backend",
    [switch]$UseCloudFormation,
    [switch]$ManualDeployment,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Lavangam Backend AWS Deployment Script

Usage:
    .\deploy_to_aws.ps1 [-KeyPairName <name>] [-InstanceType <type>] [-Region <region>] [-StackName <name>] [-UseCloudFormation] [-ManualDeployment] [-Help]

Options:
    -KeyPairName        Name of your AWS EC2 Key Pair (required)
    -InstanceType       EC2 instance type (default: t3.medium)
    -Region            AWS region (default: us-west-2)
    -StackName         CloudFormation stack name (default: lavangam-backend)
    -UseCloudFormation Use CloudFormation for deployment
    -ManualDeployment  Use manual EC2 deployment
    -Help              Show this help message

Examples:
    # CloudFormation deployment
    .\deploy_to_aws.ps1 -KeyPairName my-key-pair -UseCloudFormation

    # Manual deployment
    .\deploy_to_aws.ps1 -KeyPairName my-key-pair -ManualDeployment
"@
    exit 0
}

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

function Write-Log {
    param([string]$Message, [string]$Color = $Green)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Warning {
    param([string]$Message)
    Write-Log "WARNING: $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Log "ERROR: $Message" $Red
    exit 1
}

# Check prerequisites
Write-Log "🔍 Checking prerequisites..."

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version 2>&1
    Write-Log "✅ AWS CLI found: $awsVersion"
} catch {
    Write-Error "AWS CLI is not installed. Please install AWS CLI v2 from https://aws.amazon.com/cli/"
}

# Check if AWS CLI is configured
try {
    $awsIdentity = aws sts get-caller-identity 2>&1
    if ($awsIdentity -match "Account") {
        Write-Log "✅ AWS CLI is configured"
    } else {
        Write-Error "AWS CLI is not configured. Run 'aws configure' first."
    }
} catch {
    Write-Error "AWS CLI is not configured. Run 'aws configure' first."
}

# Check if required files exist
$requiredFiles = @("aws_cloudformation_template.yaml", "deploy_to_aws.sh")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Log "✅ Found $file"
    } else {
        Write-Error "Required file $file not found in current directory"
    }
}

# Validate parameters
if (-not $KeyPairName) {
    Write-Error "KeyPairName is required. Use -KeyPairName parameter."
}

Write-Log "🚀 Starting Lavangam Backend AWS Deployment..."

if ($UseCloudFormation) {
    Write-Log "📦 Using CloudFormation deployment method..."
    
    # Deploy CloudFormation stack
    Write-Log "Creating CloudFormation stack: $StackName"
    
    $cfCommand = "aws cloudformation create-stack --stack-name $StackName --template-body file://aws_cloudformation_template.yaml --parameters ParameterKey=KeyPairName,ParameterValue=$KeyPairName --capabilities CAPABILITY_IAM --region $Region"
    
    Write-Log "Executing: $cfCommand"
    Invoke-Expression $cfCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ CloudFormation stack creation initiated successfully"
        
        # Wait for stack creation
        Write-Log "⏳ Waiting for stack creation to complete..."
        $waitCommand = "aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region"
        Invoke-Expression $waitCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Stack creation completed successfully"
            
            # Get stack outputs
            Write-Log "📋 Getting stack outputs..."
            $outputsCommand = "aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].Outputs' --output table"
            Invoke-Expression $outputsCommand
            
            Write-Log "🎉 Deployment completed successfully!"
            Write-Log ""
            Write-Log "📋 Next steps:"
            Write-Log "1. SSH to your instance using the provided command"
            Write-Log "2. Update environment variables in /opt/lavangam/.env"
            Write-Log "3. Test your endpoints"
            
        } else {
            Write-Error "Stack creation failed. Check CloudFormation console for details."
        }
    } else {
        Write-Error "Failed to create CloudFormation stack"
    }
    
} elseif ($ManualDeployment) {
    Write-Log "🔧 Using manual EC2 deployment method..."
    
    Write-Log "📋 Manual deployment steps:"
    Write-Log ""
    Write-Log "1. Create EC2 Instance:"
    Write-Log "   - Go to AWS Console → EC2 → Launch Instance"
    Write-Log "   - AMI: Ubuntu 22.04 LTS"
    Write-Log "   - Instance Type: $InstanceType"
    Write-Log "   - Key Pair: $KeyPairName"
    Write-Log "   - Security Group: Allow ports 22, 80, 443, 8000, 5022, 5024, 8004, 5000, 5001, 5025, 5002, 8765"
    Write-Log ""
    Write-Log "2. After instance is running, get the public IP and run:"
    Write-Log "   scp -i your-key.pem -r backend/ ubuntu@YOUR-EC2-IP:/opt/lavangam/"
    Write-Log ""
    Write-Log "3. SSH to your instance:"
    Write-Log "   ssh -i your-key.pem ubuntu@YOUR-EC2-IP"
    Write-Log ""
    Write-Log "4. Run deployment script:"
    Write-Log "   cd /opt/lavangam"
    Write-Log "   chmod +x deploy_to_aws.sh"
    Write-Log "   ./deploy_to_aws.sh"
    Write-Log ""
    Write-Log "5. Update environment variables:"
    Write-Log "   sudo nano /opt/lavangam/.env"
    Write-Log ""
    Write-Log "6. Test your deployment:"
    Write-Log "   curl http://YOUR-EC2-IP/api/"
    Write-Log "   curl http://YOUR-EC2-IP/scrapers/"
    
} else {
    Write-Log "❓ No deployment method specified. Use -UseCloudFormation or -ManualDeployment"
    Write-Log ""
    Write-Log "Recommended: Use -ManualDeployment for easier troubleshooting"
    Write-Log "Example: .\deploy_to_aws.ps1 -KeyPairName my-key-pair -ManualDeployment"
}

Write-Log "📚 For detailed instructions, see QUICK_DEPLOYMENT_GUIDE.md" 
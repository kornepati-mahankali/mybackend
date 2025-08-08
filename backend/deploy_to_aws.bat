@echo off
echo ========================================
echo    Lavangam AWS Deployment Helper
echo ========================================
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS CLI is not installed
    echo Please install AWS CLI v2 from https://aws.amazon.com/cli/
    pause
    exit /b 1
)

echo ✅ AWS CLI found
echo.

REM Check if required files exist
if not exist "aws_cloudformation_template.yaml" (
    echo ERROR: aws_cloudformation_template.yaml not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

if not exist "deploy_to_aws.sh" (
    echo ERROR: deploy_to_aws.sh not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

echo ✅ Required files found
echo.

echo Choose deployment method:
echo 1. CloudFormation (Automated - 5 minutes)
echo 2. Manual EC2 (Step-by-step - 15 minutes)
echo 3. Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto cloudformation
if "%choice%"=="2" goto manual
if "%choice%"=="3" goto exit
echo Invalid choice. Please try again.
pause
exit /b 1

:cloudformation
echo.
echo ========================================
echo    CloudFormation Deployment
echo ========================================
echo.

set /p keypair="Enter your EC2 Key Pair name: "
if "%keypair%"=="" (
    echo ERROR: Key Pair name is required
    pause
    exit /b 1
)

echo.
echo Creating CloudFormation stack...
echo This will take about 5-10 minutes...
echo.

aws cloudformation create-stack --stack-name lavangam-backend --template-body file://aws_cloudformation_template.yaml --parameters ParameterKey=KeyPairName,ParameterValue=%keypair% --capabilities CAPABILITY_IAM

if errorlevel 1 (
    echo ERROR: Failed to create CloudFormation stack
    pause
    exit /b 1
)

echo.
echo ✅ CloudFormation stack creation initiated
echo ⏳ Waiting for stack creation to complete...
echo.

aws cloudformation wait stack-create-complete --stack-name lavangam-backend

if errorlevel 1 (
    echo ERROR: Stack creation failed
    echo Check AWS CloudFormation console for details
    pause
    exit /b 1
)

echo.
echo ✅ Stack creation completed successfully!
echo.
echo 📋 Getting stack outputs...
echo.

aws cloudformation describe-stacks --stack-name lavangam-backend --query "Stacks[0].Outputs" --output table

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Next steps:
echo 1. SSH to your instance using the provided command above
echo 2. Update environment variables in /opt/lavangam/.env
echo 3. Test your endpoints
echo.
pause
goto exit

:manual
echo.
echo ========================================
echo    Manual EC2 Deployment
echo ========================================
echo.

echo 📋 Follow these steps:
echo.
echo 1. Create EC2 Instance:
echo    - Go to AWS Console → EC2 → Launch Instance
echo    - AMI: Ubuntu 22.04 LTS
echo    - Instance Type: t3.medium
echo    - Key Pair: Your existing key pair
echo    - Security Group: Allow these ports:
echo      * SSH (22)
echo      * HTTP (80)
echo      * HTTPS (443)
echo      * Custom TCP: 8000, 5022, 5024, 8004, 5000, 5001, 5025, 5002, 8765
echo.
echo 2. After instance is running, get the public IP
echo.
echo 3. Upload files (replace YOUR-EC2-IP with actual IP):
echo    scp -i your-key.pem -r backend/ ubuntu@YOUR-EC2-IP:/opt/lavangam/
echo.
echo 4. SSH to your instance:
echo    ssh -i your-key.pem ubuntu@YOUR-EC2-IP
echo.
echo 5. Run deployment script:
echo    cd /opt/lavangam
echo    chmod +x deploy_to_aws.sh
echo    ./deploy_to_aws.sh
echo.
echo 6. Update environment variables:
echo    sudo nano /opt/lavangam/.env
echo.
echo 7. Test your deployment:
echo    curl http://YOUR-EC2-IP/api/
echo    curl http://YOUR-EC2-IP/scrapers/
echo.
echo 📚 For detailed instructions, see QUICK_DEPLOYMENT_GUIDE.md
echo.
pause
goto exit

:exit
echo.
echo Thank you for using Lavangam AWS Deployment Helper!
pause 
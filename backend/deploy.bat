@echo off
echo 🚀 Starting deployment to AWS Elastic Beanstalk...

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo ❌ Error: Please run this script from the backend directory
    pause
    exit /b 1
)

REM Create deployment package
echo 📦 Creating deployment package...

REM Remove old deployment package if it exists
if exist "deployment.zip" (
    del deployment.zip
)

REM Create new deployment package using PowerShell
powershell.exe -Command "Compress-Archive -Path '.\*' -DestinationPath 'deployment.zip' -Force"

echo ✅ Deployment package created: deployment.zip

REM Check package size
for %%A in (deployment.zip) do echo 📊 Package size: %%~zA bytes

echo.
echo 🎯 Next steps:
echo 1. Upload deployment.zip to AWS Elastic Beanstalk
echo 2. Or use: eb deploy (if you have EB CLI configured)
echo 3. Monitor the deployment in the AWS Console
echo.
echo 🔍 To monitor deployment:
echo    - Check /var/log/eb-engine.log on the EC2 instance
echo    - Check /var/log/cfn-init.log for configuration errors
echo    - Use: eb logs (if you have EB CLI)
echo.
echo ✅ Deployment package ready!
pause 
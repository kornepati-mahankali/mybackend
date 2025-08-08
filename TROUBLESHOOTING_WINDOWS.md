# Windows Deployment Troubleshooting Guide

## Issue 1: "File association not found for extension .py"

### Quick Fix (Manual):
1. **Open Windows Settings**
2. Go to **Apps** → **Default apps**
3. Click **"Choose default apps by file type"**
4. Find **.py** in the list
5. Click on it and select **Python** from the dropdown
6. If Python isn't listed, click **"Look for an app in Microsoft Store"** or **"More apps"**

### Alternative Fix (Registry):
1. **Run PowerShell as Administrator**
2. Execute these commands:
```powershell
# Set file association
cmd /c "assoc .py=Python.File"

# Set file type handler
cmd /c 'ftype Python.File="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" "%1" %*'
```

### Workaround:
Use the simplified deployment script: `.\deploy-simple.ps1`

## Issue 2: "The AWS Access Key Id you provided does not exist in our records"

### Solution:
1. **Get your AWS credentials**:
   - Go to AWS Console → IAM → Users → Your User
   - Click "Security credentials" tab
   - Create new access key

2. **Configure AWS CLI**:
```powershell
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key  
# Enter your region (e.g., us-east-1)
# Enter output format (json)
```

3. **Test configuration**:
```powershell
aws sts get-caller-identity
```

## Issue 3: "aws command not found"

### Solution:
1. **Install AWS CLI**:
```powershell
winget install Amazon.AWSCLI
```

2. **Or download manually**:
   - Go to https://aws.amazon.com/cli/
   - Download Windows installer
   - Run the installer

3. **Restart PowerShell** after installation

## Issue 4: "python command not found"

### Solution:
1. **Check if Python is installed**:
```powershell
python --version
```

2. **If not installed**:
   - Go to https://python.org
   - Download Python 3.11+
   - Install with "Add to PATH" checked

3. **If installed but not in PATH**:
   - Add Python to PATH manually
   - Or use full path: `C:\Users\YourUser\AppData\Local\Programs\Python\Python311\python.exe`

## Issue 5: "node command not found"

### Solution:
1. **Install Node.js**:
```powershell
winget install OpenJS.NodeJS
```

2. **Or download manually**:
   - Go to https://nodejs.org
   - Download LTS version
   - Install

3. **Restart PowerShell** after installation

## Issue 6: Permission Denied Errors

### Solution:
1. **Run PowerShell as Administrator**:
   - Right-click PowerShell
   - Select "Run as administrator"

2. **Check execution policy**:
```powershell
Get-ExecutionPolicy
```

3. **If restricted, allow scripts**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Issue 7: S3 Bucket Creation Fails

### Common Causes:
1. **Bucket name already exists** (S3 bucket names are globally unique)
2. **Invalid bucket name** (must be 3-63 characters, lowercase, no underscores)
3. **Region mismatch**

### Solution:
1. **Use a unique bucket name**:
```powershell
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$bucketName = "my-app-frontend-$timestamp"
aws s3 mb s3://$bucketName --region us-east-1
```

2. **Check bucket name rules**:
   - Only lowercase letters, numbers, hyphens, and dots
   - Must start and end with letter or number
   - No consecutive dots or hyphens

## Issue 8: Elastic Beanstalk Deployment Fails

### Common Causes:
1. **Missing dependencies**
2. **Invalid configuration**
3. **Instance type not available**

### Solution:
1. **Check EB CLI installation**:
```powershell
pip install awsebcli
```

2. **Initialize EB properly**:
```powershell
cd backend
eb init
# Follow the prompts carefully
```

3. **Use supported instance type**:
```powershell
eb create my-env --instance-type t2.micro --single-instance
```

## Issue 9: Build Failures

### Frontend Build Issues:
1. **Check Node.js version**:
```powershell
node --version
npm --version
```

2. **Clear npm cache**:
```powershell
npm cache clean --force
```

3. **Delete node_modules and reinstall**:
```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Backend Build Issues:
1. **Check Python version**:
```powershell
python --version
```

2. **Install dependencies**:
```powershell
cd backend
pip install -r requirements.txt
```

3. **Check for missing packages**:
```powershell
pip list
```

## Issue 10: CORS Errors

### Solution:
1. **Update backend CORS configuration**:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://your-frontend-domain.com"])
```

2. **Or allow all origins (development only)**:
```python
CORS(app, origins="*")
```

## Quick Diagnostic Commands

Run these to check your setup:

```powershell
# Check all tools
python --version
node --version
npm --version
aws --version
pip list | findstr awsebcli

# Check AWS configuration
aws configure list
aws sts get-caller-identity

# Check file associations
Get-ItemProperty -Path "HKLM:\SOFTWARE\Classes\.py" -Name "(Default)" -ErrorAction SilentlyContinue
```

## Getting Help

1. **Check AWS documentation**: https://docs.aws.amazon.com/
2. **AWS CLI troubleshooting**: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-troubleshooting.html
3. **Elastic Beanstalk troubleshooting**: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/troubleshooting.html

## Emergency Workaround

If all else fails, use the **simplified deployment script**:
```powershell
.\deploy-simple.ps1
```

This script includes built-in error handling and will guide you through the process step by step. 
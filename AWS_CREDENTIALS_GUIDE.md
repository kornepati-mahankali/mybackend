# AWS Credentials Setup Guide

## Step 1: Get Your AWS Credentials

### 1.1 Go to AWS Console
1. Open your web browser
2. Go to https://aws.amazon.com/console/
3. Sign in to your AWS account

### 1.2 Navigate to IAM
1. In the AWS Console, search for "IAM" in the search bar
2. Click on "IAM" (Identity and Access Management)

### 1.3 Find Your User
1. In the left sidebar, click "Users"
2. Find your username in the list
3. Click on your username

### 1.4 Create Access Key
1. Click the "Security credentials" tab
2. Scroll down to "Access keys"
3. Click "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Check the confirmation box
6. Click "Next"
7. Click "Create access key"

### 1.5 Copy Your Credentials
**IMPORTANT**: Copy both values immediately - you won't be able to see the Secret Access Key again!

- **Access Key ID**: Starts with `AKIA` (example: `AKIAIOSFODNN7EXAMPLE`)
- **Secret Access Key**: Long string (example: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)

## Step 2: Configure AWS CLI

### 2.1 Run AWS Configure
```powershell
aws configure
```

### 2.2 Enter Your Credentials
When prompted:
- **AWS Access Key ID**: Paste your Access Key ID (starts with AKIA)
- **AWS Secret Access Key**: Paste your Secret Access Key (long string)
- **Default region name**: `us-east-1`
- **Default output format**: `json`

### 2.3 Test Your Configuration
```powershell
aws sts get-caller-identity
```

This should return something like:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/YourUsername"
}
```

## Step 3: Troubleshooting

### If you get "InvalidClientTokenId" error:
1. Double-check that your Access Key ID starts with `AKIA`
2. Make sure you copied the Secret Access Key correctly
3. Try creating a new access key if the current one doesn't work

### If you get "Access Denied" error:
1. Make sure your IAM user has the necessary permissions
2. Attach these policies to your user:
   - `AmazonS3FullAccess`
   - `CloudFrontFullAccess`
   - `ElasticBeanstalkFullAccess`

## Step 4: Required IAM Permissions

Your IAM user needs these permissions for deployment:

### S3 Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### CloudFront Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Elastic Beanstalk Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticbeanstalk:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Quick Commands

After setting up credentials, test with these commands:

```powershell
# Test AWS connection
aws sts get-caller-identity

# List S3 buckets (test S3 access)
aws s3 ls

# List Elastic Beanstalk applications (test EB access)
aws elasticbeanstalk describe-applications
```

## Security Best Practices

1. **Never commit credentials to Git**
2. **Use IAM roles when possible**
3. **Rotate access keys regularly**
4. **Use least privilege principle**
5. **Enable MFA for your AWS account**

## Next Steps

Once your credentials are working:
1. Run the deployment script: `.\deploy-simple.ps1`
2. Choose option 4 to set up AWS resources first
3. Then deploy your frontend and backend 
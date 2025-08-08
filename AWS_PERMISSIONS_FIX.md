# AWS Permissions Fix Guide

## 🚨 Problem: Policies Not Showing

The policies `AmazonS3FullAccess` and `AWSElasticBeanstalkFullAccess` are not showing because:
1. Your user `mahi` doesn't have IAM permissions
2. You might be in a different AWS account/region
3. The policies might have different names

## 🔧 Solution: Create Custom Policy

### Step 1: Create Custom Policy

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Click**: "Policies" (left sidebar)
3. **Click**: "Create Policy"
4. **Choose**: "JSON" tab
5. **Copy and paste** this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticbeanstalk:*",
                "s3:*",
                "ec2:*",
                "iam:PassRole",
                "iam:GetRole",
                "cloudwatch:*",
                "autoscaling:*",
                "rds:*",
                "sqs:*",
                "sns:*",
                "logs:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
```

6. **Click**: "Next: Tags" (skip tags)
7. **Click**: "Next: Review"
8. **Name**: `LavangamBackendDeployment`
9. **Description**: `Custom policy for backend deployment`
10. **Click**: "Create Policy"

### Step 2: Attach Policy to User

1. **Go to**: "Users" (left sidebar)
2. **Find**: `mahi`
3. **Click**: `mahi`
4. **Click**: "Add permissions"
5. **Choose**: "Attach policies directly"
6. **Search**: `LavangamBackendDeployment`
7. **Check**: Your custom policy
8. **Click**: "Next: Review"
9. **Click**: "Add permissions"

### Step 3: Alternative - Use Existing Policies

If you can't create custom policies, try these common names:

**S3 Policies:**
- `AmazonS3FullAccess`
- `S3FullAccess`
- `AmazonS3ReadOnlyAccess`

**Elastic Beanstalk Policies:**
- `AWSElasticBeanstalkFullAccess`
- `ElasticBeanstalkFullAccess`
- `AWSElasticBeanstalkReadOnlyAccess`

**EC2 Policies:**
- `AmazonEC2FullAccess`
- `EC2FullAccess`

## 🔍 Check Your Current Permissions

```powershell
# Check what you can do
aws sts get-caller-identity

# Test S3 access
aws s3 ls

# Test EB access
aws elasticbeanstalk describe-applications --region us-west-2
```

## 🎯 Quick Test

After adding permissions, test with:

```powershell
# Test the fixed deployment script
.\fix-aws-deployment.ps1
```

## 🚨 If Still No Access

If you still can't see policies or add permissions:

1. **Contact AWS Admin**: Ask your AWS administrator to add these permissions
2. **Use Different Account**: Use an account with admin access
3. **Manual Deployment**: Use AWS Console instead of CLI

## 📱 Manual Console Deployment (No Permissions Needed)

If you can't get CLI permissions, use the AWS Console:

1. **Go to**: https://console.aws.amazon.com/elasticbeanstalk/
2. **Create Application**: `lavangam-backend`
3. **Platform**: `Python 3.9`
4. **Upload**: `backend-deployment.zip`
5. **Deploy**

## 📞 Support

If you need help:
1. Check your AWS account permissions
2. Try the manual console deployment
3. Contact your AWS administrator 
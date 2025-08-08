# AWS Deployment Guide for Full-Stack Application

This guide will help you deploy your React frontend and Flask/Node.js backend to AWS.

## Prerequisites

1. **AWS Account** - Sign up at https://aws.amazon.com/
2. **AWS CLI** - Install and configure with your credentials
3. **Node.js & npm** - For frontend build
4. **Python & pip** - For backend dependencies
5. **Git** - For version control

## Step 1: AWS Setup

### 1.1 Install and Configure AWS CLI
```bash
# Install AWS CLI
pip install awscli

# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your output format (json)
```

### 1.2 Create IAM User (if needed)
- Go to AWS IAM Console
- Create a new user with programmatic access
- Attach policies: `AmazonS3FullAccess`, `CloudFrontFullAccess`, `ElasticBeanstalkFullAccess`

## Step 2: Frontend Deployment (S3 + CloudFront)

### 2.1 Create S3 Bucket
```bash
# Create S3 bucket for frontend
aws s3 mb s3://your-frontend-bucket-name --region us-east-1

# Enable static website hosting
aws s3 website s3://your-frontend-bucket-name --index-document index.html --error-document index.html
```

### 2.2 Configure S3 Bucket Policy
Create a file `s3-bucket-policy.json`:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-frontend-bucket-name/*"
        }
    ]
}
```

Apply the policy:
```bash
aws s3api put-bucket-policy --bucket your-frontend-bucket-name --policy file://s3-bucket-policy.json
```

### 2.3 Create CloudFront Distribution (Optional but Recommended)
1. Go to CloudFront Console
2. Create Distribution
3. Origin Domain: `your-frontend-bucket-name.s3.amazonaws.com`
4. Viewer Protocol Policy: `Redirect HTTP to HTTPS`
5. Default Root Object: `index.html`
6. Error Pages: Create custom error response for 403/404 → 200 with `/index.html`

### 2.4 Deploy Frontend
```bash
# Update the deployment script with your bucket name
# Edit deploy-frontend.sh and replace:
# S3_BUCKET="your-frontend-bucket-name"
# CLOUDFRONT_DISTRIBUTION_ID="your-cloudfront-distribution-id"

# Make script executable
chmod +x deploy-frontend.sh

# Run deployment
./deploy-frontend.sh
```

## Step 3: Backend Deployment (Elastic Beanstalk)

### 3.1 Install EB CLI
```bash
pip install awsebcli
```

### 3.2 Initialize Elastic Beanstalk Application
```bash
cd backend
eb init

# Follow the prompts:
# - Select your region
# - Create new application: your-backend-app-name
# - Select Python platform
# - Use CodeCommit: No
# - Set up SSH: No
```

### 3.3 Create Environment
```bash
eb create your-backend-env-name --instance-type t2.micro --single-instance
```

### 3.4 Configure Environment Variables
```bash
eb setenv FLASK_ENV=production FLASK_DEBUG=False
```

### 3.5 Deploy Backend
```bash
# Update the deployment script with your app and environment names
# Edit deploy-backend.sh and replace:
# EB_APPLICATION_NAME="your-backend-app-name"
# EB_ENVIRONMENT_NAME="your-backend-env-name"

# Make script executable
chmod +x deploy-backend.sh

# Run deployment
./deploy-backend.sh
```

## Step 4: Database Setup (RDS)

### 4.1 Create RDS Instance
1. Go to RDS Console
2. Create Database
3. Choose MySQL or PostgreSQL
4. Select Free tier (if available)
5. Configure security group to allow access from Elastic Beanstalk

### 4.2 Update Backend Configuration
Update your backend configuration to use RDS:
```python
# In your config.py or main.py
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://user:password@your-rds-endpoint:3306/dbname')
```

### 4.3 Set Environment Variables
```bash
eb setenv DATABASE_URL=mysql://user:password@your-rds-endpoint:3306/dbname
```

## Step 5: Update Frontend Configuration

### 5.1 Update API Endpoints
Update your frontend to use the deployed backend URL:
```javascript
// In your API configuration
const API_BASE_URL = 'https://your-backend-env-name.your-backend-app-name.us-east-1.elasticbeanstalk.com';
```

### 5.2 Rebuild and Deploy Frontend
```bash
npm run build
./deploy-frontend.sh
```

## Step 6: Domain and SSL Setup (Optional)

### 6.1 Register Domain (Route 53)
1. Go to Route 53 Console
2. Register a new domain or transfer existing one
3. Create hosted zone

### 6.2 Configure SSL Certificate
1. Go to Certificate Manager
2. Request certificate for your domain
3. Validate via DNS or email

### 6.3 Update CloudFront Distribution
1. Update CloudFront distribution
2. Add custom domain
3. Attach SSL certificate
4. Update Route 53 with CloudFront distribution

## Step 7: Monitoring and Logging

### 7.1 Set up CloudWatch
```bash
# Enable CloudWatch logging
eb config
# Add CloudWatch configuration
```

### 7.2 Set up Alarms
1. Go to CloudWatch Console
2. Create alarms for:
   - CPU utilization
   - Memory usage
   - Error rates
   - Response times

## Step 8: CI/CD Pipeline (Optional)

### 8.1 Set up GitHub Actions
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: aws s3 sync dist/ s3://your-frontend-bucket-name --delete

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install awsebcli
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: |
          cd backend
          eb deploy your-backend-env-name
```

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Update backend CORS configuration
2. **Database Connection**: Check security groups and credentials
3. **Build Failures**: Check dependencies and Node.js/Python versions
4. **Deployment Timeouts**: Increase timeout settings in EB configuration

### Useful Commands:
```bash
# Check EB status
eb status

# View logs
eb logs

# SSH into instance
eb ssh

# Check S3 bucket contents
aws s3 ls s3://your-frontend-bucket-name

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Cost Optimization

1. **Use Free Tier**: Leverage AWS free tier for development
2. **Auto Scaling**: Configure auto scaling for production
3. **Reserved Instances**: Use reserved instances for predictable workloads
4. **S3 Lifecycle**: Set up lifecycle policies for old files
5. **CloudFront**: Use CloudFront for global content delivery

## Security Best Practices

1. **IAM Roles**: Use IAM roles instead of access keys
2. **Security Groups**: Restrict access to necessary ports only
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Store secrets in environment variables
5. **Regular Updates**: Keep dependencies updated

## Next Steps

1. Set up monitoring and alerting
2. Implement backup strategies
3. Configure auto-scaling
4. Set up staging environment
5. Implement blue-green deployments

Your application should now be successfully deployed to AWS! 🚀 
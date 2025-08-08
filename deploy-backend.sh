#!/bin/bash

# Backend Deployment Script for AWS Elastic Beanstalk
echo "🚀 Starting Backend Deployment to AWS Elastic Beanstalk..."

# Navigate to backend directory
cd backend

# Create deployment package
echo "📦 Creating deployment package..."

# Create .ebextensions directory if it doesn't exist
mkdir -p .ebextensions

# Create environment configuration
cat > .ebextensions/environment.config << EOF
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
EOF

# Create deployment package
zip -r ../backend-deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*" "node_modules/*" "venv/*"

# Deploy to Elastic Beanstalk (replace with your application and environment names)
EB_APPLICATION_NAME="your-backend-app-name"
EB_ENVIRONMENT_NAME="your-backend-env-name"
REGION="us-east-1"

echo "🌐 Deploying to Elastic Beanstalk..."
echo "Application: $EB_APPLICATION_NAME"
echo "Environment: $EB_ENVIRONMENT_NAME"

# Deploy using EB CLI
eb deploy $EB_ENVIRONMENT_NAME --region $REGION

# Alternative: Deploy using AWS CLI (if EB CLI is not available)
# aws elasticbeanstalk create-application-version \
#     --application-name $EB_APPLICATION_NAME \
#     --version-label "v$(date +%Y%m%d-%H%M%S)" \
#     --source-bundle S3Bucket="your-deployment-bucket",S3Key="backend-deployment.zip" \
#     --region $REGION

echo "✅ Backend deployment completed!"
echo "🌍 Your API should be available at: http://$EB_ENVIRONMENT_NAME.$EB_APPLICATION_NAME.$REGION.elasticbeanstalk.com" 
#!/bin/bash

# Frontend Deployment Script for AWS
echo "🚀 Starting Frontend Deployment to AWS..."

# Build the frontend
echo "📦 Building frontend application..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed! dist folder not found."
    exit 1
fi

echo "✅ Build completed successfully!"

# Deploy to S3 (replace with your bucket name)
S3_BUCKET="your-frontend-bucket-name"
REGION="us-east-1"

echo "🌐 Deploying to S3 bucket: $S3_BUCKET"

# Sync files to S3
aws s3 sync dist/ s3://$S3_BUCKET --delete --region $REGION

# Invalidate CloudFront cache (replace with your distribution ID)
CLOUDFRONT_DISTRIBUTION_ID="your-cloudfront-distribution-id"

if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*" \
        --region $REGION
fi

echo "✅ Frontend deployment completed!"
echo "🌍 Your app should be available at: https://$S3_BUCKET.s3-website-$REGION.amazonaws.com" 
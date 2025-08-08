# Frontend Deployment Script for AWS (PowerShell)
Write-Host "🚀 Starting Frontend Deployment to AWS..." -ForegroundColor Green

# Build the frontend
Write-Host "📦 Building frontend application..." -ForegroundColor Yellow
npm run build

# Check if build was successful
if (-not (Test-Path "dist")) {
    Write-Host "❌ Build failed! dist folder not found." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build completed successfully!" -ForegroundColor Green

# Deploy to S3 (replace with your bucket name)
$S3_BUCKET = "your-frontend-bucket-name"
$REGION = "us-east-1"

Write-Host "🌐 Deploying to S3 bucket: $S3_BUCKET" -ForegroundColor Yellow

# Sync files to S3
aws s3 sync dist/ s3://$S3_BUCKET --delete --region $REGION

# Invalidate CloudFront cache (replace with your distribution ID)
$CLOUDFRONT_DISTRIBUTION_ID = "your-cloudfront-distribution-id"

if ($CLOUDFRONT_DISTRIBUTION_ID -ne "your-cloudfront-distribution-id") {
    Write-Host "🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
    aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*" --region $REGION
}

Write-Host "✅ Frontend deployment completed!" -ForegroundColor Green
Write-Host "🌍 Your app should be available at: https://$S3_BUCKET.s3-website-$REGION.amazonaws.com" -ForegroundColor Cyan 
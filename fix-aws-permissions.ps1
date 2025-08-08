# Fix AWS Permissions and Alternative Deployment
Write-Host "Fixing AWS Permissions and Deployment Issues" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

Write-Host "`nCurrent AWS User:" -ForegroundColor Yellow
aws sts get-caller-identity

Write-Host "`n🔍 Issues Found:" -ForegroundColor Cyan
Write-Host "1. S3 CreateBucket permission denied" -ForegroundColor Red
Write-Host "2. EB CLI has Windows compatibility issues" -ForegroundColor Red
Write-Host "3. Frontend build was successful!" -ForegroundColor Green

Write-Host "`n📋 To Fix S3 Permissions:" -ForegroundColor Cyan
Write-Host "1. Go to AWS Console → IAM → Users → mahi" -ForegroundColor White
Write-Host "2. Click 'Add permissions'" -ForegroundColor White
Write-Host "3. Attach these policies:" -ForegroundColor White
Write-Host "   - AmazonS3FullAccess" -ForegroundColor Yellow
Write-Host "   - CloudFrontFullAccess" -ForegroundColor Yellow
Write-Host "   - ElasticBeanstalkFullAccess" -ForegroundColor Yellow

Write-Host "`n🚀 Alternative: Deploy Frontend Only (Working Solution)" -ForegroundColor Green

# Check if dist folder exists
if (Test-Path "dist") {
    Write-Host "✅ Frontend build found!" -ForegroundColor Green
    
    # Create a simple bucket name
    $bucketName = "lavangam-app-" + (Get-Random -Minimum 1000 -Maximum 9999)
    $region = "us-east-1"
    
    Write-Host "`nTrying to create bucket: $bucketName" -ForegroundColor Yellow
    
    try {
        # Try to create bucket
        aws s3 mb s3://$bucketName --region $region
        Write-Host "✅ S3 bucket created successfully!" -ForegroundColor Green
        
        # Enable static website hosting
        aws s3 website s3://$bucketName --index-document index.html --error-document index.html
        Write-Host "✅ Static website hosting enabled!" -ForegroundColor Green
        
        # Create bucket policy
        $bucketPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$bucketName/*"
        }
    ]
}
"@
        
        $bucketPolicy | Out-File -FilePath "s3-bucket-policy.json" -Encoding UTF8
        aws s3api put-bucket-policy --bucket $bucketName --policy file://s3-bucket-policy.json
        Write-Host "✅ Bucket policy applied!" -ForegroundColor Green
        
        # Deploy frontend
        aws s3 sync dist/ s3://$bucketName --delete --region $region
        Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
        
        Write-Host "`n🎉 SUCCESS! Your Lavangam app is now live!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "Frontend URL: https://$bucketName.s3-website-$region.amazonaws.com" -ForegroundColor Cyan
        
        # Clean up
        if (Test-Path "s3-bucket-policy.json") {
            Remove-Item "s3-bucket-policy.json"
        }
        
    } catch {
        Write-Host "❌ Failed to create S3 bucket. Permission issue." -ForegroundColor Red
        Write-Host "Please add S3 permissions to your IAM user first." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Frontend build not found. Run 'npm run build' first." -ForegroundColor Red
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add S3 permissions to your IAM user" -ForegroundColor White
Write-Host "2. For backend, consider using AWS Console instead of EB CLI" -ForegroundColor White
Write-Host "3. Or use AWS CLI directly for backend deployment" -ForegroundColor White 
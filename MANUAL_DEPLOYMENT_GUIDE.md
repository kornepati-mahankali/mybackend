# Manual AWS Deployment Guide

## 🚀 Quick Deployment Steps

Since EB CLI has issues on Windows, here's how to deploy manually:

### Step 1: Test Locally First
```powershell
# Test the unified backend
.\start-backend-simple.ps1
```

### Step 2: Create Deployment Package
```powershell
# Go to backend directory
cd backend

# Create zip file
Compress-Archive -Path * -DestinationPath "../backend-deployment.zip" -Force
```

### Step 3: Deploy via AWS Console

1. **Go to AWS Console**: https://console.aws.amazon.com/elasticbeanstalk/
2. **Create Application**:
   - Application name: `lavangam-backend`
   - Platform: Python 3.11
   - Region: us-west-2

3. **Create Environment**:
   - Environment name: `lavangam-backend-env`
   - Platform: Python 3.11
   - Instance type: t3.medium
   - Single instance (for cost)

4. **Upload Code**:
   - Upload the `backend-deployment.zip` file
   - Deploy

### Step 4: Get Your URL
After deployment, you'll get a URL like:
`https://lavangam-backend-env.elasticbeanstalk.com`

### Step 5: Update Frontend
Update `src/services/api.ts`:
```typescript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://YOUR-ACTUAL-URL.elasticbeanstalk.com';
```

## 📊 Service Endpoints

Once deployed, your services will be available at:
- **Health Check**: `https://your-url.elasticbeanstalk.com/health`
- **Main API**: `https://your-url.elasticbeanstalk.com/main/*`
- **Scrapers API**: `https://your-url.elasticbeanstalk.com/scrapers/*`
- **System API**: `https://your-url.elasticbeanstalk.com/system/*`
- **Dashboard API**: `https://your-url.elasticbeanstalk.com/dashboard/*`

## 🔧 Alternative: Use AWS CLI Script

If you prefer automation, try:
```powershell
.\deploy-aws-cli.ps1
```

## 📱 Mobile Access

Once deployed to AWS:
1. **Single Domain**: All services under one URL
2. **HTTPS**: Automatic SSL certificates
3. **No Port Issues**: Mobile can access directly
4. **CORS**: Properly configured for all origins

## 🎯 Benefits

1. **All Services Unified**: One deployment instead of 8+ ports
2. **Mobile Friendly**: Single domain access
3. **Cost Effective**: Single instance instead of multiple
4. **Scalable**: Easy to scale and maintain
5. **Secure**: HTTPS and proper CORS

## 🚨 Troubleshooting

### Common Issues:
1. **Import Errors**: Check requirements.txt
2. **CORS Errors**: Verify domain in unified_api.py
3. **Port Issues**: All services now use port 8000
4. **Database**: Ensure credentials are correct

### Test Commands:
```powershell
# Test local
.\test-backend-connection.ps1

# Test AWS (replace with your URL)
.\test-backend-connection.ps1 -BackendUrl "https://your-url.elasticbeanstalk.com"
```

## 📞 Support

If you encounter issues:
1. Check AWS EB logs in console
2. Verify all files are in the zip
3. Test locally first
4. Check CORS configuration 
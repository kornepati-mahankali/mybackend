# Backend Deployment Guide for AWS

## 🚀 Quick Start

### Prerequisites
1. AWS CLI installed and configured
2. EB CLI installed: `pip install awsebcli`
3. Python 3.11
4. Your AWS credentials configured

### Step 1: Test Local Backend
```powershell
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the backend locally
uvicorn main:app --reload --port 8000

# Test in another terminal
.\test-backend-connection.ps1
```

### Step 2: Deploy to AWS Elastic Beanstalk
```powershell
# Run the deployment script
.\deploy-backend.ps1
```

### Step 3: Update Frontend Configuration
After deployment, update your frontend API configuration:

1. Get your Elastic Beanstalk URL from the deployment output
2. Update `src/services/api.ts`:
```typescript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://YOUR-ELASTIC-BEANSTALK-URL.elasticbeanstalk.com';
```

## 🔧 Manual Deployment Steps

### 1. Initialize EB Application
```bash
cd backend
eb init lavangam-backend --platform python-3.11 --region us-west-2
```

### 2. Create Environment
```bash
eb create lavangam-backend-env --instance-type t3.small --single-instance
```

### 3. Deploy
```bash
eb deploy
```

### 4. Get Application URL
```bash
eb status
```

## 📁 File Structure for Deployment

```
backend/
├── main.py                 # FastAPI application
├── app.py                  # EB entry point
├── requirements.txt        # Python dependencies
├── Procfile               # EB process definition
├── runtime.txt            # Python version
├── .ebextensions/         # EB configuration
│   └── environment.config
└── scrapers/              # Scraping modules
```

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check that your frontend domain is in the CORS allow_origins list
   - Update main.py if needed

2. **Port Issues**
   - EB uses environment variable $PORT
   - Procfile should use: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Dependencies Missing**
   - Ensure all packages in requirements.txt are compatible with Python 3.11
   - Check for missing system dependencies

4. **Database Connection**
   - Ensure your Supabase credentials are correct
   - Check network connectivity

### Testing Commands

```powershell
# Test local backend
.\test-backend-connection.ps1

# Test AWS backend (replace with your URL)
.\test-backend-connection.ps1 -BackendUrl "https://your-eb-url.elasticbeanstalk.com"

# Check EB logs
eb logs

# SSH into EB instance (if needed)
eb ssh
```

## 🌐 Environment Variables

Set these in your EB environment:
- `SUPABASE_URL`: Your Supabase URL
- `SUPABASE_KEY`: Your Supabase service key
- `PYTHONPATH`: `/var/app/current:$PYTHONPATH`

## 📊 Monitoring

- **EB Dashboard**: Monitor application health
- **CloudWatch**: View logs and metrics
- **Health Checks**: `/api/dashboard-overview` endpoint

## 🔄 Update Process

1. Make changes to your code
2. Test locally: `uvicorn main:app --reload --port 8000`
3. Deploy: `eb deploy`
4. Verify: Check the deployed URL

## 📱 Mobile Compatibility

For mobile access:
1. Ensure your EB environment is publicly accessible
2. Update CORS to allow mobile app domains
3. Test with mobile browsers
4. Consider using a custom domain with SSL

## 🛡️ Security Considerations

1. **HTTPS**: EB provides SSL certificates
2. **CORS**: Restrict origins in production
3. **Environment Variables**: Use EB environment variables for secrets
4. **Rate Limiting**: Consider adding rate limiting middleware

## 📞 Support

If you encounter issues:
1. Check EB logs: `eb logs`
2. Verify configuration files
3. Test endpoints individually
4. Check AWS EB documentation 
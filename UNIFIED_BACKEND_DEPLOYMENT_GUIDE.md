# Unified Backend Deployment Guide

## 🚀 Overview

This guide deploys all your backend services as a unified API on AWS Elastic Beanstalk. Instead of running multiple services on different ports, everything is now consolidated into one deployment.

## 📦 Services Included

- **Main API** (formerly port 8000) → `/main`
- **Scrapers API** (formerly port 5022) → `/scrapers`
- **System Usage API** (formerly port 5024) → `/system`
- **Dashboard API** (formerly port 8004) → `/dashboard`
- **File Manager** → Integrated into main API
- **Scraper WebSocket** → Integrated into scrapers API
- **Admin Metrics API** → Integrated into main API
- **E-Procurement Server** → Integrated into main API
- **Dashboard WebSocket** → Integrated into dashboard API

## 🔧 Quick Start

### Step 1: Test Locally
```powershell
# Start the unified backend locally
.\start-unified-backend.ps1

# Test the connection
.\test-backend-connection.ps1
```

### Step 2: Deploy to AWS
```powershell
# Deploy all services to AWS
.\deploy-all-services.ps1
```

### Step 3: Update Frontend
After deployment, update your frontend configuration with the new AWS URL.

## 📊 API Endpoints

### Root Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - API documentation

### Service Endpoints
- `GET /main/*` - Main API endpoints
- `GET /scrapers/*` - Scrapers API endpoints
- `GET /system/*` - System usage endpoints
- `GET /dashboard/*` - Dashboard API endpoints

## 🔄 Migration from Multi-Port Setup

### Before (Multiple Ports)
```bash
uvicorn main:app --reload --port 8000
uvicorn scrapers.api:app --reload --port 5022
uvicorn system_usage_api:app --reload --port 5024
python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8004
```

### After (Unified API)
```bash
uvicorn unified_api:app --reload --port 8000
```

### Frontend API Changes

#### Before
```typescript
const API_BASE_URL = 'http://localhost:8000';
// Different services on different ports
```

#### After
```typescript
const API_BASE_URL = 'https://your-eb-url.elasticbeanstalk.com';
const API_ENDPOINTS = {
  main: '/main',
  scrapers: '/scrapers',
  system: '/system',
  dashboard: '/dashboard'
};
```

## 🛠️ File Structure

```
backend/
├── unified_api.py          # Main unified API
├── main.py                 # Original main API
├── scrapers/
│   └── api.py             # Scrapers API
├── system_usage_api.py     # System usage API
├── dashboard_api.py        # Dashboard API
├── app.py                  # EB entry point
├── Procfile               # Updated for unified API
├── requirements.txt       # All dependencies
└── .ebextensions/         # EB configuration
```

## 🔍 Testing

### Local Testing
```powershell
# Test unified backend
.\test-backend-connection.ps1

# Test individual services
.\test-backend-connection.ps1 -BackendUrl "http://localhost:8000"
```

### AWS Testing
```powershell
# Test deployed backend
.\test-backend-connection.ps1 -BackendUrl "https://your-eb-url.elasticbeanstalk.com"
```

## 📱 Mobile Compatibility

The unified approach solves mobile access issues because:
1. **Single Domain**: All services are under one domain
2. **HTTPS**: AWS provides SSL certificates
3. **CORS**: Properly configured for all origins
4. **No Port Issues**: No need to open multiple ports

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python path configuration

2. **CORS Errors**
   - Verify CORS configuration in unified_api.py
   - Check frontend domain is in allow_origins

3. **Service Not Found**
   - Check service mounting in unified_api.py
   - Verify endpoint paths

4. **Database Connection**
   - Ensure database credentials are correct
   - Check network connectivity

### Debug Commands

```powershell
# Check if unified API imports
python -c "from unified_api import app; print('OK')"

# Test individual services
curl http://localhost:8000/health
curl http://localhost:8000/main
curl http://localhost:8000/scrapers
curl http://localhost:8000/system
curl http://localhost:8000/dashboard

# Check EB logs
eb logs
```

## 🔄 Update Process

1. **Make Changes**: Update your service code
2. **Test Locally**: `.\start-unified-backend.ps1`
3. **Deploy**: `.\deploy-all-services.ps1`
4. **Verify**: Test the deployed endpoints

## 📊 Monitoring

- **Health Check**: `GET /health`
- **Service Status**: Check individual service endpoints
- **EB Dashboard**: Monitor application health
- **CloudWatch**: View logs and metrics

## 🛡️ Security

- **HTTPS**: Automatic SSL certificates
- **CORS**: Configured for your domains
- **Environment Variables**: Use EB for secrets
- **Rate Limiting**: Consider adding middleware

## 📞 Support

If you encounter issues:
1. Check the unified API logs
2. Test individual services
3. Verify frontend configuration
4. Check AWS EB documentation

## 🎯 Benefits of Unified Approach

1. **Simplified Deployment**: One deployment instead of multiple
2. **Better Resource Usage**: Single instance instead of multiple
3. **Easier Management**: One codebase to maintain
4. **Mobile Friendly**: Single domain access
5. **Cost Effective**: Lower AWS costs
6. **Better Monitoring**: Centralized logging and metrics 
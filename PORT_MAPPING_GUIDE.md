# Port Mapping Guide - All Ports to AWS

## 🚀 **Complete Port Mapping Solution**

This guide shows how to map ALL your local ports to AWS URLs after deployment.

## 📊 **Port to AWS URL Mapping**

### **Before (Local Development):**
```
http://127.0.0.1:8000  → Main API
http://127.0.0.1:5022  → Scrapers API  
http://127.0.0.1:5024  → System Usage API
http://127.0.0.1:8004  → Dashboard API
http://127.0.0.1:5002  → Service 5002
http://127.0.0.1:5003  → Service 5003
http://127.0.0.1:8001  → Service 8001
http://127.0.0.1:5021  → Service 5021
http://127.0.0.1:5023  → Service 5023
http://127.0.0.1:8002  → Service 8002
```

### **After (AWS Deployment):**
```
https://your-eb-url.elasticbeanstalk.com/main      → Main API (Port 8000)
https://your-eb-url.elasticbeanstalk.com/scrapers  → Scrapers API (Port 5022)
https://your-eb-url.elasticbeanstalk.com/system    → System API (Port 5024)
https://your-eb-url.elasticbeanstalk.com/dashboard → Dashboard API (Port 8004)
https://your-eb-url.elasticbeanstalk.com/port-5002 → Service 5002
https://your-eb-url.elasticbeanstalk.com/port-5003 → Service 5003
https://your-eb-url.elasticbeanstalk.com/port-8001 → Service 8001
https://your-eb-url.elasticbeanstalk.com/port-5021 → Service 5021
https://your-eb-url.elasticbeanstalk.com/port-5023 → Service 5023
https://your-eb-url.elasticbeanstalk.com/port-8002 → Service 8002
```

## 🔧 **Frontend Configuration Update**

### **Update your frontend API configuration:**

```typescript
// src/services/api.ts
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://your-eb-url.elasticbeanstalk.com';

// Port mapping for different services
const PORT_MAPPINGS = {
  '8000': '/main',
  '5022': '/scrapers',
  '5024': '/system', 
  '8004': '/dashboard',
  '5002': '/port-5002',
  '5003': '/port-5003',
  '8001': '/port-8001',
  '5021': '/port-5021',
  '5023': '/port-5023',
  '8002': '/port-8002'
};

// Helper function to get AWS URL for any port
function getAwsUrl(port: string): string {
  if (window.location.hostname === 'localhost') {
    return `http://localhost:${port}`;
  }
  return `${API_BASE_URL}${PORT_MAPPINGS[port] || ''}`;
}
```

## 📱 **Mobile Access Fixed**

### **Before (Mobile Issues):**
- ❌ Mobile can't access `localhost:8000`
- ❌ Mobile can't access `127.0.0.1:5022`
- ❌ Multiple ports cause connection issues

### **After (AWS Deployment):**
- ✅ Mobile can access `https://your-eb-url.elasticbeanstalk.com/main`
- ✅ Mobile can access `https://your-eb-url.elasticbeanstalk.com/scrapers`
- ✅ Single domain, all services accessible
- ✅ HTTPS certificates included
- ✅ CORS properly configured

## 🎯 **Deployment Steps**

### **Step 1: Deploy to AWS**
```powershell
# Deploy all ports to AWS
.\deploy-all-ports.ps1
```

### **Step 2: Get Your AWS URL**
After deployment, you'll get a URL like:
`https://lavangam-all-ports-env.elasticbeanstalk.com`

### **Step 3: Update Frontend**
Replace all localhost URLs with AWS URLs using the mapping above.

### **Step 4: Test All Services**
```powershell
# Test the complete deployment
.\test-backend-connection.ps1 -BackendUrl "https://your-eb-url.elasticbeanstalk.com"
```

## 🔍 **Testing All Ports**

### **Health Check:**
```
GET https://your-eb-url.elasticbeanstalk.com/health
```

### **Port Mapping Info:**
```
GET https://your-eb-url.elasticbeanstalk.com/port-mapping
```

### **API Documentation:**
```
GET https://your-eb-url.elasticbeanstalk.com/docs
```

## 🚨 **Troubleshooting**

### **If a port doesn't work:**
1. Check the port mapping at `/port-mapping`
2. Verify the service is included in the unified API
3. Check AWS EB logs for errors

### **If mobile still can't access:**
1. Ensure you're using HTTPS URLs
2. Check CORS configuration
3. Verify the AWS URL is correct

## 📞 **Support**

- **Health Check**: `/health` - Shows all active services
- **Port Mapping**: `/port-mapping` - Shows all port mappings
- **Documentation**: `/docs` - API documentation
- **AWS Console**: Monitor deployment status

## 🎉 **Benefits**

1. **Single Deployment**: All 10 ports in one AWS instance
2. **Mobile Friendly**: Single domain access
3. **Cost Effective**: One instance instead of 10
4. **Scalable**: Easy to add more services
5. **Secure**: HTTPS and proper CORS
6. **Maintainable**: Centralized configuration 
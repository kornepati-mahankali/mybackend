# Manual AWS Deployment - All Ports

## 🚀 **Deploy All Your Ports to AWS (Manual Method)**

Your deployment package is ready! Here's how to deploy it manually via AWS Console.

## 📦 **What's Ready:**

✅ **Deployment Package**: `all-ports-deployment-20250805-102740.zip`
✅ **S3 Bucket**: `lavangam-all-ports-deployments-1005`
✅ **All Services Included**: Ports 8000, 5022, 5024, 8004, 5002, 5003, 8001, 5021, 5023, 8002

## 🎯 **Step-by-Step Manual Deployment:**

### **Step 1: Go to AWS Elastic Beanstalk Console**
1. Open: https://console.aws.amazon.com/elasticbeanstalk/
2. Make sure you're in **US West (Oregon)** region
3. Click **"Create Application"**

### **Step 2: Configure Application**
1. **Application name**: `lavangam-all-ports-backend`
2. **Description**: `Complete backend with all ports unified`
3. Click **"Next"**

### **Step 3: Choose Platform**
1. **Platform**: `Python`
2. **Platform branch**: `Python 3.9` (or latest available)
3. **Platform version**: Select the latest available
4. Click **"Next"**

### **Step 4: Configure Instance**
1. **Environment type**: `Single instance (free tier eligible)`
2. **Instance type**: `t3.small` (or t2.micro for free tier)
3. Click **"Next"**

### **Step 5: Upload Your Code**
1. **Source**: Choose `Upload your code`
2. **Upload**: Click **"Choose file"**
3. **Select**: `all-ports-deployment-20250805-102740.zip` from your project folder
4. Click **"Next"**

### **Step 6: Configure Environment**
1. **Environment name**: `lavangam-all-ports-env`
2. **Domain**: Leave default (AWS will assign)
3. Click **"Next"**

### **Step 7: Review and Launch**
1. Review all settings
2. Click **"Submit"**

## ⏱️ **Deployment Time:**
- **Expected time**: 5-10 minutes
- **Status**: Watch the environment status change from "Creating" to "Ready"

## 🔗 **After Deployment:**

### **Get Your AWS URL:**
1. Go to your environment dashboard
2. Copy the **Environment URL** (e.g., `https://lavangam-all-ports-env.elasticbeanstalk.com`)

### **Test All Your Ports:**
Replace `your-eb-url` with your actual URL:

```
Main API (Port 8000): https://your-eb-url.elasticbeanstalk.com/main
Scrapers API (Port 5022): https://your-eb-url.elasticbeanstalk.com/scrapers
System API (Port 5024): https://your-eb-url.elasticbeanstalk.com/system
Dashboard API (Port 8004): https://your-eb-url.elasticbeanstalk.com/dashboard
Port 5002: https://your-eb-url.elasticbeanstalk.com/port-5002
Port 5003: https://your-eb-url.elasticbeanstalk.com/port-5003
Port 8001: https://your-eb-url.elasticbeanstalk.com/port-8001
Port 5021: https://your-eb-url.elasticbeanstalk.com/port-5021
Port 5023: https://your-eb-url.elasticbeanstalk.com/port-5023
Port 8002: https://your-eb-url.elasticbeanstalk.com/port-8002
```

### **Health Check:**
```
https://your-eb-url.elasticbeanstalk.com/health
```

### **Port Mapping Info:**
```
https://your-eb-url.elasticbeanstalk.com/port-mapping
```

## 📱 **Mobile Access Fixed:**

✅ **Before**: Mobile couldn't access `localhost:8000`, `127.0.0.1:5022`, etc.
✅ **After**: Mobile can access `https://your-eb-url.elasticbeanstalk.com/main`, etc.

## 🔧 **Update Frontend:**

Once you have your AWS URL, update your frontend configuration:

```typescript
// src/services/api.ts
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://your-eb-url.elasticbeanstalk.com'; // Replace with your actual URL
```

## 🚨 **Troubleshooting:**

### **If deployment fails:**
1. Check the **Events** tab in your EB environment
2. Look for error messages
3. Common issues:
   - Python version mismatch
   - Missing dependencies
   - Port configuration issues

### **If services don't work:**
1. Test the health endpoint first
2. Check the port mapping endpoint
3. Verify CORS settings

## 📞 **Support:**

- **AWS Console**: Monitor deployment status
- **Health Check**: `/health` - Shows all active services
- **Port Mapping**: `/port-mapping` - Shows all port mappings
- **Documentation**: `/docs` - API documentation

## 🎉 **Benefits Achieved:**

1. ✅ **All 10 ports deployed** to single AWS instance
2. ✅ **Mobile access fixed** - single domain access
3. ✅ **Cost effective** - one instance instead of 10
4. ✅ **Scalable** - easy to add more services
5. ✅ **Secure** - HTTPS and proper CORS
6. ✅ **Maintainable** - centralized configuration 
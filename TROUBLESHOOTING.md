# 🔧 Troubleshooting Guide: Frontend-Backend Connection

## 🚨 **Issue: Frontend Showing "0" Values and Connection Refused Errors**

### **Symptoms:**
- Performance Analytics shows all metrics as "0"
- Console errors: `net::ERR_CONNECTION_REFUSED`
- `Failed to fetch` errors in browser console

### **Root Cause:**
The frontend is trying to connect to the wrong port or the backend isn't running.

---

## ✅ **Solution Steps**

### **Step 1: Verify Backend is Running**

1. **Check if backend is running on port 8000:**
   ```bash
   # In PowerShell
   Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
   ```

2. **If not running, start the backend:**
   ```bash
   cd backend
   python main.py
   ```

3. **Test backend directly:**
   ```bash
   python test_analytics.py
   ```
   Should show:
   ```
   ✅ Health endpoint: 200
   ✅ Performance endpoint: 200
   ✅ Recent jobs endpoint: 200
   ```

### **Step 2: Verify API Configuration**

1. **Check API base URL in `src/services/api.ts`:**
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
   ```

2. **Create/update `.env` file in project root:**
   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

### **Step 3: Restart Frontend Development Server**

1. **Stop the current frontend server** (Ctrl+C)

2. **Restart with new environment:**
   ```bash
   npm run dev
   ```

3. **Clear browser cache** and refresh the page

### **Step 4: Test Connection**

1. **Run the connection test:**
   ```bash
   node test_frontend_backend.js
   ```

2. **Check browser console** for API request logs:
   ```
   🌐 API Request: http://localhost:8000/analytics/performance
   ✅ Performance data received: {...}
   ```

---

## 🔍 **Debugging Steps**

### **Check Browser Console**

1. **Open Developer Tools** (F12)
2. **Go to Console tab**
3. **Look for these logs:**
   ```
   🌐 API Request: http://localhost:8000/analytics/performance
   🔄 Fetching performance data...
   ✅ Performance data received: {...}
   ```

### **Check Network Tab**

1. **Open Developer Tools** (F12)
2. **Go to Network tab**
3. **Refresh the page**
4. **Look for requests to:**
   - `http://localhost:8000/analytics/performance`
   - `http://localhost:8000/analytics/recent-jobs`

### **Common Error Messages**

| Error | Solution |
|-------|----------|
| `net::ERR_CONNECTION_REFUSED` | Backend not running on port 8000 |
| `Failed to fetch` | CORS issue or wrong port |
| `API Error: 404` | Wrong endpoint path |
| `API Error: 500` | Backend database error |

---

## 🛠️ **Manual Testing**

### **Test Backend API Directly**

```bash
# Test health endpoint
curl http://localhost:8000/analytics/health

# Test performance endpoint
curl http://localhost:8000/analytics/performance

# Test recent jobs endpoint
curl http://localhost:8000/analytics/recent-jobs
```

### **Expected Responses**

**Health Endpoint:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-07-30T13:00:07.617499"
}
```

**Performance Endpoint:**
```json
{
  "metrics": {
    "totalJobs": { "value": 1247, "change": "+12.5%", "trend": "up" },
    "successRate": { "value": "94.2%", "change": "+2.1%", "trend": "up" },
    "avgDuration": { "value": "4.2m", "change": "-8.3%", "trend": "down" },
    "dataVolume": { "value": "847GB", "change": "+15.7%", "trend": "up" }
  },
  "jobTrends": [...],
  "toolUsage": [...]
}
```

---

## 🔄 **Auto-Recovery Features**

The system includes several fallback mechanisms:

1. **Mock Data Fallback:** If API fails, shows realistic mock data
2. **Loading States:** Shows skeleton screens while loading
3. **Error Handling:** Graceful error messages
4. **Auto-refresh:** Retries every 30 seconds

---

## 📞 **Still Having Issues?**

If the problem persists:

1. **Check firewall settings** - ensure port 8000 is not blocked
2. **Try different browser** - test in incognito mode
3. **Check antivirus software** - may be blocking local connections
4. **Restart computer** - clears any port conflicts

### **Contact Information:**
- Check the browser console for detailed error messages
- Verify all steps in this guide have been followed
- Ensure both backend and frontend are running simultaneously 
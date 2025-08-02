# Real-Time Dashboard Setup Guide

This guide will help you set up the real-time dashboard for monitoring data scraping jobs.

## 🎯 Overview

The dashboard provides real-time monitoring of:
- **Total Active Jobs**: Count of jobs with status 'queued'
- **Completed Today**: Count of jobs completed on the current date
- **Total Downloads**: Sum of downloads from metadata
- **Success Rate**: Percentage of completed vs failed jobs
- **Recent Activity**: Latest 5 jobs with status and timestamps
- **Weekly Chart**: Job activity over the last 7 days
- **System Status**: API Server, Database, and Queue System status

## 🏗️ Architecture

```
Frontend (React) ←→ WebSocket (ws://localhost:8002) ←→ Dashboard API (http://localhost:8001) ←→ MySQL Database
```

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **MySQL Database** running on port 3307
3. **Node.js** for the React frontend
4. **Required Python packages** (will be installed automatically)

## 🚀 Quick Start

### 1. Database Setup

First, set up the MySQL database with the jobs table:

```sql
-- Run this in your MySQL client
source backend/create_jobs_table.sql
```

Or manually execute the SQL commands in the `backend/create_jobs_table.sql` file.

### 2. Start Dashboard Services

#### Option A: Windows (Recommended)
```bash
cd backend
start_dashboard_services.bat
```

#### Option B: Python Script
```bash
cd backend
python start_dashboard_services.py
```

#### Option C: Manual Start
```bash
# Terminal 1 - Start API Server
cd backend
python -m uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Start WebSocket Server
cd backend
python dashboard_websocket.py
```

### 3. Start Frontend

```bash
# In a new terminal
npm run dev
```

The dashboard will be available at: http://localhost:5173

## 🔧 Configuration

### Database Configuration

Edit `backend/dashboard_api.py` to match your MySQL settings:

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinformation'
}
```

### Frontend Configuration

The frontend is configured to connect to:
- API: `http://localhost:8001`
- WebSocket: `ws://localhost:8002`

To change these, edit `src/components/Dashboard/DashboardHome.tsx`:

```typescript
const API_BASE_URL = 'http://localhost:8001';
const WS_URL = 'ws://localhost:8002';
```

## 📊 API Endpoints

### Dashboard Metrics
- `GET /api/dashboard/metrics` - All dashboard data
- `GET /api/dashboard/active-jobs` - Active jobs count
- `GET /api/dashboard/completed-today` - Today's completed jobs
- `GET /api/dashboard/total-downloads` - Total downloads
- `GET /api/dashboard/success-rate` - Success rate percentage
- `GET /api/dashboard/recent-activity` - Recent activity logs
- `GET /api/dashboard/weekly-chart` - Weekly chart data
- `GET /api/dashboard/system-status` - System status

### Health Check
- `GET /health` - Service health status

## 🔌 WebSocket Events

The WebSocket server sends real-time updates every 10 seconds:

```json
{
  "type": "dashboard_update",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "active_jobs": 7,
    "completed_today": 24,
    "total_downloads": 1247,
    "success_rate": 94.2,
    "recent_activity": [...],
    "weekly_chart_data": [...],
    "system_status": {...}
  }
}
```

## 📁 File Structure

```
backend/
├── dashboard_api.py              # FastAPI server
├── dashboard_websocket.py        # WebSocket server
├── start_dashboard_services.py   # Python startup script
├── start_dashboard_services.bat  # Windows startup script
└── create_jobs_table.sql         # Database schema

src/components/Dashboard/
└── DashboardHome.tsx             # React dashboard component
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL is running on port 3307
   - Verify database credentials in `dashboard_api.py`
   - Ensure `toolinformation` database exists

2. **WebSocket Connection Failed**
   - Check if WebSocket server is running on port 8002
   - Verify firewall settings
   - Check browser console for connection errors

3. **API Server Not Responding**
   - Check if API server is running on port 8001
   - Verify no other service is using port 8001
   - Check logs for error messages

4. **Frontend Not Loading Data**
   - Check browser network tab for API calls
   - Verify CORS settings in API server
   - Check if both API and WebSocket servers are running

### Debug Mode

To run with debug logging:

```bash
# API Server with debug
python -m uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload --log-level debug

# WebSocket Server with debug
python dashboard_websocket.py
```

### Manual Database Test

Test database connection:

```bash
cd backend
python -c "
import pymysql
from dashboard_api import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## 🔄 Real-Time Updates

The dashboard updates in real-time through:

1. **WebSocket Connection**: Primary method for live updates
2. **Fallback Polling**: If WebSocket fails, falls back to API polling
3. **Auto-reconnection**: Automatically reconnects if connection is lost

### Update Frequency
- **WebSocket**: Every 10 seconds
- **Fallback Polling**: Every 30 seconds
- **Manual Refresh**: Available via browser refresh

## 📈 Performance Monitoring

The dashboard includes system monitoring:

- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Current memory consumption
- **Disk Usage**: Available disk space
- **Uptime**: Service availability percentage

## 🔐 Security Considerations

- API endpoints are currently open (no authentication)
- Consider adding authentication for production use
- WebSocket connections are not encrypted (use WSS for production)
- Database credentials should be stored in environment variables

## 🚀 Production Deployment

For production deployment:

1. **Use HTTPS/WSS**: Secure WebSocket connections
2. **Add Authentication**: Implement user authentication
3. **Environment Variables**: Store sensitive configuration
4. **Load Balancing**: Use reverse proxy for multiple instances
5. **Monitoring**: Add application monitoring and logging
6. **Backup**: Regular database backups

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review server logs for error messages
3. Verify all prerequisites are met
4. Test database connection manually
5. Check network connectivity between services

## 🎉 Success!

Once everything is running, you should see:

- ✅ Dashboard API running on http://localhost:8001
- ✅ WebSocket server running on ws://localhost:8002
- ✅ Frontend dashboard with real-time data
- ✅ Live updates every 10 seconds
- ✅ System status indicators
- ✅ Weekly activity chart
- ✅ Recent activity logs

The dashboard will automatically display real data from your MySQL database and update in real-time! 
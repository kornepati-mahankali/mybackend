# Real-Time Performance Analytics System

This document describes the implementation of real-time performance metrics for the Super Scraper Pro Dashboard, matching the metrics shown in the Performance Analytics screenshot.

## 🎯 Overview

The analytics system provides real-time performance metrics including:
- **Total Jobs** (1,247) - Count of all scraping jobs
- **Success Rate** (94.2%) - Percentage of successful jobs
- **Average Duration** (4.2m) - Average job execution time
- **Data Volume** (847GB) - Total data processed
- **Job Success Trends** - Monthly job performance over 6 months
- **Tool Usage Statistics** - Usage breakdown by tool

## 🏗️ Architecture

### Backend Components

1. **Analytics API** (`backend/analytics_api.py`)
   - FastAPI-based analytics endpoints
   - Real-time data aggregation
   - Database queries for metrics calculation

2. **Database Schema**
   - `jobs` table - Stores job execution data
   - `tools` table - Tool definitions
   - `users` table - User management

3. **Main Application** (`backend/main.py`)
   - Mounts analytics API at `/analytics`
   - Integrates with existing backend

### Frontend Components

1. **Performance View** (`src/components/Performance/PerformanceView.tsx`)
   - Real-time metrics display
   - Auto-refresh every 30 seconds
   - Interactive charts and tables

2. **API Service** (`src/services/api.ts`)
   - Analytics API integration
   - Data fetching and caching

## 📊 Key Metrics Implementation

### 1. Total Jobs
```sql
SELECT COUNT(*) FROM jobs WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### 2. Success Rate
```sql
SELECT 
  ROUND(
    (SELECT COUNT(*) FROM jobs WHERE status = 'completed') * 100.0 /
    (SELECT COUNT(*) FROM jobs),
    2
  ) AS success_rate;
```

### 3. Average Duration
```sql
SELECT 
  ROUND(AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) / 60, 1) AS avg_duration_min
FROM jobs 
WHERE start_time IS NOT NULL AND end_time IS NOT NULL;
```

### 4. Data Volume
```sql
SELECT 
  ROUND(SUM(data_volume) / 1024, 2) AS total_data_gb
FROM jobs 
WHERE data_volume IS NOT NULL;
```

### 5. Job Success Trends
```sql
SELECT 
  DATE_FORMAT(created_at, '%Y-%m') as month,
  COUNT(*) as total_jobs,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM jobs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month;
```

### 6. Tool Usage Statistics
```sql
SELECT 
  t.name as tool_name,
  COUNT(*) as usage_count
FROM jobs j
JOIN tools t ON j.tool_id = t.id
GROUP BY t.name
ORDER BY usage_count DESC;
```

## 🚀 API Endpoints

### Performance Analytics
- **GET** `/analytics/performance` - Get comprehensive performance data
  - Query params: `userId` (optional), `period` (default: 30 days)
  - Returns: metrics, job trends, tool usage

### Recent Jobs
- **GET** `/analytics/recent-jobs` - Get recent jobs for dashboard table
  - Query params: `userId` (optional), `limit` (default: 10)
  - Returns: recent jobs with status and timing

### Health Check
- **GET** `/analytics/health` - Check analytics service health

## 🔄 Real-Time Updates

### Auto-Refresh
- Frontend automatically refreshes data every 30 seconds
- Manual refresh button available
- Loading states and skeleton screens

### Data Flow
1. Frontend calls analytics API
2. Backend queries database for real-time metrics
3. Data is formatted and returned
4. Frontend updates charts and metrics
5. Process repeats every 30 seconds

## 🛠️ Setup Instructions

### 1. Database Setup
```bash
cd backend
python setup_analytics_db.py
```

### 2. Start Backend
```bash
cd backend
python main.py
```

### 3. Start Frontend
```bash
npm run dev
```

### 4. Access Analytics
- Navigate to Performance Analytics section
- Data will load automatically
- Use refresh button for manual updates

## 📈 Customization

### Adding New Metrics
1. Add SQL query in `analytics_api.py`
2. Update API response structure
3. Add frontend display component
4. Update TypeScript types

### Changing Refresh Interval
```typescript
// In PerformanceView.tsx
useEffect(() => {
  const interval = setInterval(() => {
    // Refresh logic
  }, 30000); // Change this value (in milliseconds)
}, []);
```

### Database Configuration
Update `DB_CONFIG` in `analytics_api.py`:
```python
DB_CONFIG = {
    'host': 'your_host',
    'port': your_port,
    'user': 'your_user',
    'password': 'your_password',
    'db': 'your_database',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in `DB_CONFIG`
   - Ensure MySQL server is running
   - Verify database exists

2. **No Data Displayed**
   - Check if jobs table exists
   - Verify sample data was inserted
   - Check browser console for API errors

3. **Charts Not Loading**
   - Verify Recharts library is installed
   - Check data format matches chart expectations
   - Ensure animations are properly configured

### Debug Mode
Enable debug logging in `analytics_api.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Sample Data

The system includes sample data for testing:
- 4 sample tools (Gem Portal, Global Trade, E-Procurement, etc.)
- 4 sample jobs with different statuses
- Realistic timing and data volume values

## 🔮 Future Enhancements

1. **Caching Layer**
   - Redis integration for improved performance
   - Cache metrics for 1-5 minutes to reduce database load

2. **Advanced Analytics**
   - Predictive analytics for job success
   - Performance forecasting
   - Anomaly detection

3. **Export Features**
   - PDF reports generation
   - Excel export of metrics
   - Scheduled report delivery

4. **Real-time Notifications**
   - WebSocket integration for live updates
   - Email alerts for failed jobs
   - Slack/Discord integration

## 📚 Dependencies

### Backend
- FastAPI
- PyMySQL
- psutil (for system metrics)

### Frontend
- React
- Recharts (for charts)
- Framer Motion (for animations)
- Lucide React (for icons)

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include TypeScript types for new features
4. Test with both mock and real data
5. Update documentation for new endpoints 
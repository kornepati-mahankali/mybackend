# Admin Metrics API

This API provides real-time system metrics for the Admin Dashboard, including system load, database size, and job information.

## 🚀 Features

### ✅ System Load Metrics
- **CPU Usage**: Real-time CPU percentage using `psutil`
- **Memory Usage**: Current memory usage percentage
- **Storage Usage**: Disk usage percentage for the main drive
- **Additional Info**: Memory/disk sizes in human-readable format, system uptime

### ✅ Database Size Tracking
- **Total Database Size**: Current size of the entire MySQL database
- **Daily Growth**: Tracks how much the database grew today
- **Growth Percentage**: Calculates percentage growth from previous day
- **Persistent Tracking**: Stores size history in `db_size_history.json`

### ✅ Job Information
- **Active Jobs**: Count of jobs with status "active"
- **Queued Jobs**: Count of jobs with status "queued"
- **Completed Jobs**: Count of jobs with status "completed"
- **Total Jobs**: Sum of all jobs
- **Fallback Data**: Returns mock data if jobs table doesn't exist

## 📡 API Endpoints

### 1. System Load
```
GET /admin/system-load
```

**Response:**
```json
{
  "cpu_percent": 76.2,
  "memory_percent": 65.8,
  "disk_percent": 82.1,
  "memory_used": "8.2GB",
  "memory_total": "16.0GB",
  "disk_used": "1.2TB",
  "disk_total": "2.0TB",
  "uptime_seconds": 86400,
  "uptime_formatted": "1 day, 0:00:00",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Database Size
```
GET /admin/database-size
```

**Response:**
```json
{
  "total_size": "2.4TB",
  "total_size_bytes": 2638827906662,
  "today_growth": "120GB",
  "today_growth_bytes": 128849018880,
  "growth_percentage": 5.12
}
```

### 3. Jobs Information
```
GET /admin/jobs-info
```

**Response:**
```json
{
  "active_jobs": 12,
  "queued_jobs": 8,
  "completed_jobs": 45,
  "total_jobs": 65
}
```

### 4. All Metrics (Combined)
```
GET /admin/admin-metrics
```

**Response:**
```json
{
  "system_load": { /* system load data */ },
  "database_size": { /* database size data */ },
  "jobs_info": { /* jobs data */ },
  "timestamp": "2024-01-15T10:30:00"
}
```

### 5. Health Check
```
GET /admin/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🛠️ Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Configuration
The API uses the following MySQL configuration:
- **Host**: 127.0.0.1
- **Port**: 3307
- **User**: root
- **Password**: thanuja
- **Database**: toolinformation

### 3. Jobs Table (Optional)
If you want real job data instead of mock data, create a `jobs` table:

```sql
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    status ENUM('active', 'queued', 'completed') DEFAULT 'queued',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🚀 Running the API

### Method 1: Integrated with Main Server
The admin metrics API is automatically included in the main FastAPI server:

```bash
cd backend
python main.py
```

Access endpoints at: `http://localhost:8000/admin/`

### Method 2: Standalone Server
Run the admin metrics API independently:

```bash
cd backend
python admin_metrics_api.py
```

Access endpoints at: `http://localhost:8001/`

## 🧪 Testing

Run the test script to verify all endpoints work:

```bash
cd backend
python test_admin_metrics.py
```

## 📊 Frontend Integration

### React/TypeScript Example
```typescript
// Fetch system load
const getSystemLoad = async () => {
  const response = await fetch('http://localhost:8000/admin/system-load');
  const data = await response.json();
  return data;
};

// Fetch all metrics
const getAllMetrics = async () => {
  const response = await fetch('http://localhost:8000/admin/admin-metrics');
  const data = await response.json();
  return data;
};
```

### Real-time Updates
For real-time dashboard updates, poll the endpoints every 5-10 seconds:

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    const metrics = await getAllMetrics();
    setMetrics(metrics);
  }, 5000);

  return () => clearInterval(interval);
}, []);
```

## 🔧 Configuration

### Environment Variables
You can customize the database connection by setting environment variables:

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3307
export DB_USER=root
export DB_PASSWORD=thanuja
export DB_NAME=toolinformation
```

### Database Size Tracking
The API automatically creates a `db_size_history.json` file to track database growth. This file stores daily size snapshots for growth calculations.

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL is running on port 3307
   - Check credentials in `admin_metrics_api.py`
   - Ensure the `toolinformation` database exists

2. **Permission Errors**
   - Ensure the application has read access to system metrics
   - Check file permissions for `db_size_history.json`

3. **Mock Data Showing**
   - If jobs table doesn't exist, the API returns mock data
   - Create the jobs table to get real job statistics

### Logs
Check the console output for detailed error messages and debugging information.

## 📈 Performance Considerations

- **CPU Usage**: The `psutil.cpu_percent()` call has a 1-second interval
- **Database Queries**: Optimized to use minimal queries
- **Caching**: Consider implementing Redis caching for high-frequency requests
- **Rate Limiting**: Add rate limiting for production use

## 🔒 Security Notes

- The API currently allows all origins (`*`) for CORS
- Consider restricting CORS origins in production
- Database credentials are hardcoded - use environment variables in production
- Add authentication/authorization for production deployment

## 📝 License

This API is part of the Super Scraper Pro Dashboard v3.0 project. 
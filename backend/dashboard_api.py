from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import psutil
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dashboard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinformation'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def convert_decimals(obj):
    """Convert Decimal objects to regular numbers for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

def get_dashboard_metrics() -> Dict[str, Any]:
    """Get all dashboard metrics in a single query"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Get total active jobs (queued status)
                cursor.execute("""
                    SELECT COUNT(*) as active_jobs
                    FROM jobs 
                    WHERE status = 'queued'
                """)
                active_jobs = cursor.fetchone()['active_jobs']
                
                # Get completed jobs today
                cursor.execute("""
                    SELECT COUNT(*) as completed_today
                    FROM jobs 
                    WHERE status = 'completed' 
                    AND DATE(completed_at) = CURDATE()
                """)
                completed_today = cursor.fetchone()['completed_today']
                
                # Get total downloads from metadata
                cursor.execute("""
                    SELECT COALESCE(SUM(CAST(JSON_EXTRACT(metadata, '$.downloads') AS UNSIGNED)), 0) as total_downloads
                    FROM jobs 
                    WHERE metadata IS NOT NULL
                """)
                total_downloads = cursor.fetchone()['total_downloads']
                
                # Get success rate
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                    FROM jobs
                """)
                success_data = cursor.fetchone()
                completed_count = success_data['completed_count']
                failed_count = success_data['failed_count']
                total_jobs = completed_count + failed_count
                success_rate = round((completed_count / total_jobs * 100), 1) if total_jobs > 0 else 0
                
                # Get recent activity (5 latest jobs)
                cursor.execute("""
                    SELECT 
                        title,
                        status,
                        updated_at,
                        JSON_EXTRACT(metadata, '$.downloads') as downloads,
                        JSON_EXTRACT(metadata, '$.records_extracted') as records_extracted,
                        JSON_EXTRACT(metadata, '$.error') as error
                    FROM jobs 
                    ORDER BY updated_at DESC 
                    LIMIT 5
                """)
                recent_activity = cursor.fetchall()
                
                # Convert datetime fields in recent activity
                for activity in recent_activity:
                    if 'updated_at' in activity and activity['updated_at']:
                        activity['updated_at'] = activity['updated_at'].isoformat()
                
                # Get weekly activity data (last 7 days)
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as total_jobs,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_jobs
                    FROM jobs 
                    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                weekly_data = cursor.fetchall()
                
                # Format weekly data for chart
                weekly_chart_data = []
                for i in range(7):
                    chart_date = date.today() - timedelta(days=6-i)
                    day_name = chart_date.strftime('%a')[:3]  # Mon, Tue, etc.
                    
                    # Find matching data
                    day_data = next((item for item in weekly_data if item['date'] == chart_date), None)
                    
                    weekly_chart_data.append({
                        'name': day_name,
                        'jobs': day_data['total_jobs'] if day_data else 0,
                        'success': day_data['successful_jobs'] if day_data else 0
                    })
                
                # Get system status
                system_status = get_system_status()
                
                # Convert all data to ensure JSON serialization works
                result = {
                    "active_jobs": active_jobs,
                    "completed_today": completed_today,
                    "total_downloads": total_downloads,
                    "success_rate": success_rate,
                    "recent_activity": recent_activity,
                    "weekly_chart_data": weekly_chart_data,
                    "system_status": system_status
                }
                
                return convert_decimals(result)
                
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_system_status() -> Dict[str, Any]:
    """Get system status and uptime information"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Boot time for uptime calculation
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_hours = uptime.total_seconds() / 3600
        
        # Calculate uptime percentage (assuming 24/7 operation)
        uptime_percentage = min(99.9, 100 - (uptime_hours / (24 * 365)) * 100)  # Simplified calculation
        
        return {
            "api_server": {
                "status": "online",
                "uptime": f"{uptime_percentage:.1f}%",
                "cpu_usage": f"{cpu_percent:.1f}%",
                "memory_usage": f"{memory_percent:.1f}%"
            },
            "database": {
                "status": "online",
                "uptime": f"{uptime_percentage - 0.1:.1f}%",
                "disk_usage": f"{disk_percent:.1f}%"
            },
            "queue_system": {
                "status": "online",
                "uptime": f"{uptime_percentage - 0.2:.1f}%"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "api_server": {"status": "error", "uptime": "0%"},
            "database": {"status": "error", "uptime": "0%"},
            "queue_system": {"status": "error", "uptime": "0%"}
        }

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics_endpoint():
    """Get all dashboard metrics"""
    try:
        metrics = get_dashboard_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error in dashboard metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/active-jobs")
async def get_active_jobs():
    """Get count of active jobs"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'queued'")
                result = cursor.fetchone()
                return {"active_jobs": result['count']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/completed-today")
async def get_completed_today():
    """Get count of jobs completed today"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM jobs 
                    WHERE status = 'completed' AND DATE(completed_at) = CURDATE()
                """)
                result = cursor.fetchone()
                return {"completed_today": result['count']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/total-downloads")
async def get_total_downloads():
    """Get total downloads from all jobs"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(CAST(JSON_EXTRACT(metadata, '$.downloads') AS UNSIGNED)), 0) as total
                    FROM jobs WHERE metadata IS NOT NULL
                """)
                result = cursor.fetchone()
                return {"total_downloads": result['total']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/success-rate")
async def get_success_rate():
    """Get success rate percentage"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                    FROM jobs
                """)
                result = cursor.fetchone()
                completed = result['completed']
                failed = result['failed']
                total = completed + failed
                success_rate = round((completed / total * 100), 1) if total > 0 else 0
                return {"success_rate": success_rate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/recent-activity")
async def get_recent_activity():
    """Get recent activity logs"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        title,
                        status,
                        updated_at,
                        JSON_EXTRACT(metadata, '$.downloads') as downloads,
                        JSON_EXTRACT(metadata, '$.records_extracted') as records_extracted,
                        JSON_EXTRACT(metadata, '$.error') as error
                    FROM jobs 
                    ORDER BY updated_at DESC 
                    LIMIT 5
                """)
                activities = cursor.fetchall()
                return {"recent_activity": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/weekly-chart")
async def get_weekly_chart():
    """Get weekly chart data"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as total_jobs,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_jobs
                    FROM jobs 
                    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                weekly_data = cursor.fetchall()
                
                # Format for chart
                chart_data = []
                for i in range(7):
                    chart_date = date.today() - timedelta(days=6-i)
                    day_name = chart_date.strftime('%a')[:3]
                    day_data = next((item for item in weekly_data if item['date'] == chart_date), None)
                    
                    chart_data.append({
                        'name': day_name,
                        'jobs': day_data['total_jobs'] if day_data else 0,
                        'success': day_data['successful_jobs'] if day_data else 0
                    })
                
                return {"weekly_chart_data": chart_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/system-status")
async def get_system_status_endpoint():
    """Get system status"""
    try:
        status = get_system_status()
        return {"system_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import logging
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database configuration - using the same config as admin_metrics_api
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'db': 'toolinformation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def format_bytes(bytes_value: int) -> str:
    """Convert bytes to human readable format (KB, MB, GB, TB)"""
    if bytes_value == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(bytes_value, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_value / p, 2)
    return f"{s}{size_names[i]}"

def format_duration(seconds: float) -> str:
    """Convert seconds to human readable duration"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

@app.get("/performance")
async def get_performance_data(
    user_id: Optional[str] = Query(None, description="User ID to filter data"),
    period: str = Query("30", description="Time period in days")
):
    """Get comprehensive performance analytics data"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Check if jobs table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'jobs'
                """, (DB_CONFIG['db'],))
                
                result = cursor.fetchone()
                if not result or result['table_exists'] == 0:
                    # Return empty data if jobs table doesn't exist
                    return get_empty_performance_data(period)
                
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(period))
                
                # Build WHERE clause - using existing schema
                where_clause = "WHERE created_at >= %s AND created_at <= %s"
                params = [start_date, end_date]
                
                if user_id:
                    where_clause += " AND user_id = %s"
                    params.append(user_id)
                
                # 1. Total Jobs
                cursor.execute(f"""
                    SELECT COUNT(*) as total_jobs
                    FROM jobs 
                    {where_clause}
                """, params)
                total_jobs_result = cursor.fetchone()
                total_jobs = total_jobs_result['total_jobs'] if total_jobs_result else 0
                
                # 2. Success Rate - using existing status values
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful
                    FROM jobs 
                    {where_clause}
                """, params)
                success_result = cursor.fetchone()
                total_for_success = success_result['total'] if success_result else 0
                successful_jobs = success_result['successful'] if success_result else 0
                success_rate = round((successful_jobs / total_for_success * 100), 1) if total_for_success > 0 else 0
                
                # 3. Average Duration - using existing schema
                cursor.execute(f"""
                    SELECT AVG(TIMESTAMPDIFF(SECOND, started_at, completed_at)) as avg_duration_seconds
                    FROM jobs 
                    {where_clause} AND started_at IS NOT NULL AND completed_at IS NOT NULL
                """, params)
                duration_result = cursor.fetchone()
                avg_duration_seconds = duration_result['avg_duration_seconds'] if duration_result and duration_result['avg_duration_seconds'] else 0
                avg_duration_minutes = round(avg_duration_seconds / 60, 1) if avg_duration_seconds else 0
                
                # 4. Data Volume - estimate based on progress and metadata
                cursor.execute(f"""
                    SELECT SUM(progress) as total_progress
                    FROM jobs 
                    {where_clause} AND progress IS NOT NULL
                """, params)
                volume_result = cursor.fetchone()
                total_progress = volume_result['total_progress'] if volume_result and volume_result['total_progress'] else 0
                # Estimate data volume based on progress (rough calculation)
                total_data_volume_mb = total_progress * 10  # Assume 10MB per progress unit
                total_data_volume_gb = round(total_data_volume_mb / 1024, 1) if total_data_volume_mb else 0
                
                # 5. Job Success Trends (monthly data for the last 6 months)
                trend_months = 6
                trend_start_date = end_date - timedelta(days=trend_months * 30)
                
                cursor.execute(f"""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as total_jobs,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN status = 'failed' OR status = 'error' THEN 1 ELSE 0 END) as failed
                    FROM jobs 
                    WHERE created_at >= %s AND created_at <= %s
                    {f"AND user_id = %s" if user_id else ""}
                    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                    ORDER BY month
                """, [trend_start_date, end_date] + ([user_id] if user_id else []))
                
                trends_data = cursor.fetchall()
                
                # Format trends data
                job_trends = []
                for row in trends_data:
                    month_name = datetime.strptime(row['month'], '%Y-%m').strftime('%b')
                    job_trends.append({
                        "name": month_name,
                        "jobs": row['total_jobs'],
                        "success": row['successful'],
                        "failed": row['failed']
                    })
                
                # If no real data, create sample trends data
                if not job_trends:
                    job_trends = [
                        {"name": "Jan", "jobs": 45, "success": 42, "failed": 3},
                        {"name": "Feb", "jobs": 52, "success": 48, "failed": 4},
                        {"name": "Mar", "jobs": 38, "success": 36, "failed": 2},
                        {"name": "Apr", "jobs": 61, "success": 58, "failed": 3},
                        {"name": "May", "jobs": 55, "success": 51, "failed": 4},
                        {"name": "Jun", "jobs": 67, "success": 63, "failed": 4}
                    ]
                
                # 6. Tool Usage Statistics - using actual tool names from title column
                cursor.execute(f"""
                    SELECT 
                        title as tool_name,
                        COUNT(*) as usage_count
                    FROM jobs 
                    {where_clause}
                    GROUP BY title
                    ORDER BY usage_count DESC
                    LIMIT 10
                """, params)
                
                tool_usage_data = cursor.fetchall()
                
                # Format tool usage data
                tool_usage = []
                for row in tool_usage_data:
                    tool_usage.append({
                        "name": row['tool_name'],
                        "usage": row['usage_count']
                    })
                
                # If no real data, create sample tool usage data
                if not tool_usage:
                    tool_usage = [
                        {"name": "Gem Portal", "usage": 85},
                        {"name": "Global Trade", "usage": 72},
                        {"name": "E-Procurement", "usage": 68},
                        {"name": "Universal Extractor", "usage": 45},
                        {"name": "Market Intelligence", "usage": 38}
                    ]
                
                # Calculate change percentages (mock data for now)
                change_percentage = 5.2  # Mock change
                
                return {
                    "metrics": {
                        "totalJobs": {
                            "value": total_jobs,
                            "change": f"+{change_percentage}%",
                            "trend": "up"
                        },
                        "successRate": {
                            "value": f"{success_rate}%",
                            "change": f"+{change_percentage}%",
                            "trend": "up"
                        },
                        "avgDuration": {
                            "value": f"{avg_duration_minutes}m",
                            "change": f"+{change_percentage}%",
                            "trend": "up"
                        },
                        "dataVolume": {
                            "value": f"{total_data_volume_gb}GB",
                            "change": f"+{change_percentage}%",
                            "trend": "up"
                        }
                    },
                    "jobTrends": job_trends,
                    "toolUsage": tool_usage,
                    "period": period,
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        # Return empty data on error
        return get_empty_performance_data(period)

def get_empty_performance_data(period: str = "30"):
    """Return empty performance data when no real data is available"""
    return {
        "metrics": {
            "totalJobs": {
                "value": 0,
                "change": "0%",
                "trend": "up"
            },
            "successRate": {
                "value": "0%",
                "change": "0%",
                "trend": "up"
            },
            "avgDuration": {
                "value": "0m",
                "change": "0%",
                "trend": "up"
            },
            "dataVolume": {
                "value": "0GB",
                "change": "0%",
                "trend": "up"
            }
        },
        "jobTrends": [],
        "toolUsage": [],
        "period": period,
        "timestamp": datetime.now().isoformat(),
        "note": "No real data available - showing empty metrics"
    }

@app.get("/recent-jobs")
async def get_recent_jobs(
    user_id: Optional[str] = Query(None, description="User ID to filter data"),
    limit: int = Query(10, description="Number of recent jobs to return")
):
    """Get recent jobs for the dashboard table"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Check if jobs table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'jobs'
                """, (DB_CONFIG['db'],))
                
                result = cursor.fetchone()
                if not result or result['table_exists'] == 0:
                    # Return empty data if jobs table doesn't exist
                    return {
                        "recentJobs": [],
                        "timestamp": datetime.now().isoformat(),
                        "note": "No jobs table found - showing empty data"
                    }
                
                # Build WHERE clause
                where_clause = ""
                params = []
                
                if user_id:
                    where_clause = "WHERE j.user_id = %s"
                    params.append(user_id)
                
                # Get recent jobs with existing schema
                cursor.execute(f"""
                    SELECT 
                        j.id,
                        j.status,
                        j.started_at,
                        j.completed_at,
                        j.progress,
                        j.title as tool_name,
                        j.description,
                        j.created_at
                    FROM jobs j
                    {where_clause}
                    ORDER BY j.created_at DESC
                    LIMIT %s
                """, params + [limit])
                
                jobs_data = cursor.fetchall()
                
                recent_jobs = []
                for job in jobs_data:
                    # Calculate duration
                    duration = "N/A"
                    if job['started_at'] and job['completed_at']:
                        duration_seconds = (job['completed_at'] - job['started_at']).total_seconds()
                        duration = format_duration(duration_seconds)
                    
                    # Calculate records (estimate based on progress)
                    records = "N/A"
                    if job['progress']:
                        records = f"{job['progress']}"  # Use progress as record count
                    
                    # Format start time
                    started = "N/A"
                    if job['created_at']:
                        time_diff = datetime.now() - job['created_at']
                        if time_diff.days > 0:
                            started = f"{time_diff.days} days ago"
                        elif time_diff.seconds > 3600:
                            hours = time_diff.seconds // 3600
                            started = f"{hours} hours ago"
                        else:
                            minutes = time_diff.seconds // 60
                            started = f"{minutes} minutes ago"
                    
                    recent_jobs.append({
                        "id": job['id'],
                        "tool": job['tool_name'] or "General Scraping",
                        "state": job['description'] or "N/A",
                        "duration": duration,
                        "records": records,
                        "status": job['status'],
                        "started": started
                    })
                
                return {
                    "recentJobs": recent_jobs,
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error getting recent jobs: {e}")
        return {
            "recentJobs": [],
            "timestamp": datetime.now().isoformat(),
            "note": f"Error fetching recent jobs: {str(e)}"
        }

@app.get("/performance/real-time")
async def get_real_time_performance(
    period: str = Query("30", description="Time period in days")
):
    """Get real-time performance metrics"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Check if jobs table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'jobs'
                """, (DB_CONFIG['db'],))
                
                result = cursor.fetchone()
                if not result or result['table_exists'] == 0:
                    # Return empty data if jobs table doesn't exist
                    return {
                        "totalJobs": 0,
                        "successRate": "0%",
                        "avgDuration": "0m",
                        "dataVolume": "0GB",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # All metrics in one query for efficiency
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_jobs,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful_jobs,
                        SUM(CASE WHEN status = 'failed' OR status = 'error' THEN 1 ELSE 0 END) as failed_jobs,
                        AVG(CASE WHEN started_at IS NOT NULL AND completed_at IS NOT NULL 
                            THEN TIMESTAMPDIFF(SECOND, started_at, completed_at) 
                            ELSE NULL END) as avg_duration_seconds,
                        COUNT(CASE WHEN metadata IS NOT NULL THEN 1 END) as jobs_with_files
                    FROM jobs 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """, [int(period)])
                
                result = cursor.fetchone()
                
                total_jobs = result['total_jobs'] or 0
                successful_jobs = result['successful_jobs'] or 0
                failed_jobs = result['failed_jobs'] or 0
                avg_duration_seconds = result['avg_duration_seconds'] or 0
                jobs_with_files = result['jobs_with_files'] or 0
                
                # Calculate metrics
                success_rate = round((successful_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0
                avg_duration_min = round(avg_duration_seconds / 60, 1) if avg_duration_seconds else 0
                data_volume_gb = round(jobs_with_files * 50 / 1024, 1)  # Estimate 50MB per file
                
                # Get chart data for the same period
                # Job Success Trends (last 6 months)
                trend_start_date = datetime.now() - timedelta(days=180)
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as total_jobs,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN status = 'failed' OR status = 'error' THEN 1 ELSE 0 END) as failed
                    FROM jobs 
                    WHERE created_at >= %s
                    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                    ORDER BY month
                """, [trend_start_date])
                
                trends_data = cursor.fetchall()
                job_trends = []
                for row in trends_data:
                    month_name = datetime.strptime(row['month'], '%Y-%m').strftime('%b')
                    job_trends.append({
                        "name": month_name,
                        "jobs": row['total_jobs'],
                        "success": row['successful'],
                        "failed": row['failed']
                    })
                
                # Tool Usage Statistics - use actual tool names from title column
                cursor.execute("""
                    SELECT 
                        title as tool_name,
                        COUNT(*) as usage_count
                    FROM jobs 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY title
                    ORDER BY usage_count DESC
                    LIMIT 5
                """, [int(period)])
                
                tool_usage_data = cursor.fetchall()
                tool_usage = []
                for row in tool_usage_data:
                    tool_usage.append({
                        "name": row['tool_name'],
                        "usage": row['usage_count']
                    })
                
                # If no real data, create sample data
                if not job_trends:
                    job_trends = [
                        {"name": "Jan", "jobs": 45, "success": 42, "failed": 3},
                        {"name": "Feb", "jobs": 52, "success": 48, "failed": 4},
                        {"name": "Mar", "jobs": 38, "success": 36, "failed": 2},
                        {"name": "Apr", "jobs": 61, "success": 58, "failed": 3},
                        {"name": "May", "jobs": 55, "success": 51, "failed": 4},
                        {"name": "Jun", "jobs": 67, "success": 63, "failed": 4}
                    ]
                
                if not tool_usage:
                    tool_usage = [
                        {"name": "Gem Portal", "usage": 85},
                        {"name": "Global Trade", "usage": 72},
                        {"name": "E-Procurement", "usage": 68},
                        {"name": "Universal Extractor", "usage": 45},
                        {"name": "Market Intelligence", "usage": 38}
                    ]
        
        return {
                    "totalJobs": total_jobs,
                    "successRate": f"{success_rate}%",
                    "avgDuration": f"{avg_duration_min}m",
                    "dataVolume": f"{data_volume_gb}GB",
                    "jobTrends": job_trends,
                    "toolUsage": tool_usage,
            "timestamp": datetime.now().isoformat()
        }
                
    except Exception as e:
        logger.error(f"Error getting real-time performance: {e}")
        return {
            "totalJobs": 0,
            "successRate": "0%",
            "avgDuration": "0m",
            "dataVolume": "0GB",
            "timestamp": datetime.now().isoformat(),
            "error": "Failed to get performance data"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "analytics-api"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 
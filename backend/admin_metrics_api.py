from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psutil
import pymysql
import os
import json
from datetime import datetime, date
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Admin Metrics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database configuration - Updated to use MySQL
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinformation'
}

# File to store previous database size for growth calculation
DB_SIZE_FILE = "db_size_history.json"

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
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

def get_database_size() -> Dict[str, Any]:
    """Get total database size and calculate today's growth"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Get total database size - MySQL version
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(data_length + index_length), 0) AS total_bytes
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (DB_CONFIG['database'],))
                
                result = cursor.fetchone()
                current_size_bytes = int(result['total_bytes']) if result and result['total_bytes'] else 0
                
                # Load previous size from file
                previous_size_bytes = 0
                today_growth_bytes = 0
                
                if os.path.exists(DB_SIZE_FILE):
                    try:
                        with open(DB_SIZE_FILE, 'r') as f:
                            data = json.load(f)
                            last_date = data.get('last_date')
                            previous_size_bytes = data.get('size_bytes', 0)
                            
                            # Calculate growth if it's the same day
                            if last_date == date.today().isoformat():
                                today_growth_bytes = current_size_bytes - previous_size_bytes
                    except Exception as e:
                        logger.error(f"Error reading size history: {e}")
                
                # Save current size
                try:
                    with open(DB_SIZE_FILE, 'w') as f:
                        json.dump({
                            'last_date': date.today().isoformat(),
                            'size_bytes': current_size_bytes
                        }, f)
                except Exception as e:
                    logger.error(f"Error saving size history: {e}")
                
                return {
                    "total_size": format_bytes(current_size_bytes),
                    "total_size_bytes": current_size_bytes,
                    "today_growth": format_bytes(today_growth_bytes),
                    "today_growth_bytes": today_growth_bytes,
                    "growth_percentage": round((today_growth_bytes / previous_size_bytes * 100) if previous_size_bytes > 0 else 0, 2)
                }
                
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return {
            "total_size": "0B",
            "total_size_bytes": 0,
            "today_growth": "0B",
            "today_growth_bytes": 0,
            "growth_percentage": 0,
            "error": str(e)
        }

def get_jobs_info() -> Dict[str, Any]:
    """Get active and queued job counts from tools_1 table"""
    try:
        connection = get_db_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Check if jobs table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'jobs'
                """, (DB_CONFIG['database'],))
                
                result = cursor.fetchone()
                if not result or result['table_exists'] == 0:
                    # Return mock data if jobs table doesn't exist
                    return {
                        "active_jobs": 0,
                        "queued_jobs": 0,
                        "completed_jobs": 0,
                        "total_jobs": 0,
                        "note": "Using mock data - jobs table not found"
                    }
                
                # Get job counts by status from jobs table
                cursor.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count
                    FROM jobs 
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                
                # Initialize counts
                job_counts = {
                    "running": 0,
                    "pending": 0,
                    "queued": 0,
                    "completed": 0,
                    "failed": 0,
                    "empty": 0,
                    "total": 0
                }
                
                # Process results
                for row in results:
                    status = row['status']
                    count = int(row['count'])  # Ensure count is integer
                    
                    if status == '' or status is None:
                        job_counts["empty"] = count
                    elif status.lower() in job_counts:
                        job_counts[status.lower()] = count
                    else:
                        job_counts["empty"] += count
                    
                    job_counts["total"] += count
                
                # Map statuses for admin panel
                active_jobs = job_counts["running"]  # Running jobs are active
                queued_jobs = job_counts["queued"] + job_counts["pending"]
                
                return {
                    "active_jobs": active_jobs,
                    "queued_jobs": queued_jobs,
                    "completed_jobs": job_counts["completed"],
                    "total_jobs": job_counts["total"]
                }
                
    except Exception as e:
        logger.error(f"Error getting jobs info: {e}")
        # Return mock data on error
        return {
            "active_jobs": 0,
            "queued_jobs": 0,
            "completed_jobs": 0,
            "total_jobs": 0,
            "error": f"Database error: {str(e)}"
        }

@app.get("/system-load")
async def get_system_load():
    """Get real-time system load metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage (get the main disk)
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Get additional system info
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory_percent, 2),
            "disk_percent": round(disk_percent, 2),
            "memory_used": format_bytes(memory.used),
            "memory_total": format_bytes(memory.total),
            "disk_used": format_bytes(disk.used),
            "disk_total": format_bytes(disk.total),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],  # Remove microseconds
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system load: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system load: {str(e)}")

@app.get("/database-size")
async def get_database_size_endpoint():
    """Get database size and growth information"""
    return get_database_size()

@app.get("/jobs-info")
async def get_jobs_info_endpoint():
    """Get job statistics"""
    return get_jobs_info()

@app.get("/admin-metrics")
async def get_all_metrics():
    """Get all admin metrics in one call"""
    try:
        logger.info("Admin metrics request received")
        system_load = await get_system_load()
        database_size = get_database_size()
        jobs_info = get_jobs_info()
        
        result = {
            "system_load": system_load,
            "database_size": database_size,
            "jobs_info": jobs_info,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Admin metrics response: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting all metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        connection = get_db_connection()
        connection.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cors_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Admin Metrics API is working!",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import psutil
import pymysql
import os
import json
from supabase import create_client, Client

# Initialize Supabase client with service role key for enhanced access
supabase_url = "https://zjfjaezztfydiryzsyvd.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpqZmphZXp6dGZ5ZGlyeXpzeXZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTAyNzAyMSwiZXhwIjoyMDY2NjAzMDIxfQ.sRbGz6wbBoMmY8Ol3vEPc4VOh2oEWpcONi9DkUsTpKk"
supabase: Client = create_client(supabase_url, supabase_key)

# Security bearer token
security = HTTPBearer()
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from functools import lru_cache
import logging
import asyncio

# Cache user data for 30 seconds to reduce Supabase API calls
@lru_cache(maxsize=1)
async def get_cached_user_data():
    try:
        # Get users from auth.users table with specific fields
        users_response = supabase.table('auth.users').select(
            'id,email,last_sign_in_at,created_at,updated_at,raw_user_meta_data,phone,app_metadata'
        ).execute()
        
        if not users_response or not isinstance(users_response.data, list):
            logger.error("Invalid response from auth.users table")
            raise ValueError("Failed to fetch users data")
        
        users = users_response.data
        
        # Get user activity data with validation
        activity_response = supabase.table('user_activity').select(
            'user_id,last_active,status,metadata,session_id,device_info'
        ).execute()
        
        if not activity_response:
            logger.warning("No user activity data found")
            activities = []
        else:
            activities = activity_response.data
        
        # Map activities by user_id with additional validation
        activity_map = {}
        for act in activities:
            if 'user_id' in act:
                activity_map[act['user_id']] = {
                    'last_active': act.get('last_active'),
                    'status': act.get('status', 'offline'),
                    'metadata': act.get('metadata', {}),
                    'session_id': act.get('session_id'),
                    'device_info': act.get('device_info', {})
                }
        
        # Process and combine user data with enhanced validation
        processed_users = []
        for user in users:
            if not user.get('id'):
                logger.warning(f"Skipping user without ID: {user}")
                continue
                
            activity = activity_map.get(user['id'], {})
            processed_users.append({
                'id': user['id'],
                'email': user.get('email', 'N/A'),
                'phone': user.get('phone'),
                'last_sign_in': user.get('last_sign_in_at'),
                'created_at': user.get('created_at'),
                'updated_at': user.get('updated_at'),
                'raw_user_meta_data': user.get('raw_user_meta_data', {}),
                'app_metadata': user.get('app_metadata', {}),
                'last_active': activity.get('last_active'),
                'status': activity.get('status', 'offline'),
                'metadata': activity.get('metadata', {}),
                'session_id': activity.get('session_id'),
                'device_info': activity.get('device_info', {})
            })
        
        logger.info(f"Successfully processed {len(processed_users)} users")
        return {
            'users': processed_users,
            'total_users': len(users),
            'active_users': len([u for u in processed_users if u['status'] == 'online']),
            'timestamp': datetime.utcnow().isoformat(),
            'cache_status': 'hit'
        }
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        return {
            'users': [],
            'total_users': 0,
            'active_users': 0,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'cache_status': 'error'
        }

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

# Rate limiting settings
REQUEST_LIMIT = 100  # Maximum requests per window
TIME_WINDOW = 60  # Time window in seconds
request_history = {}

def check_rate_limit(client_id: str) -> bool:
    now = datetime.utcnow()
    if client_id not in request_history:
        request_history[client_id] = []
    
    # Clean old requests
    request_history[client_id] = [t for t in request_history[client_id] 
                                 if (now - t).total_seconds() < TIME_WINDOW]
    
    if len(request_history[client_id]) >= REQUEST_LIMIT:
        return False
    
    request_history[client_id].append(now)
    return True

@app.get("/supabase-users")
async def get_supabase_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get real-time Supabase user data with caching and rate limiting"""
    try:
        client_id = credentials.credentials[:16]  # Use part of the token as client ID
        
        # Check rate limit
        if not check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Too many requests",
                    "retry_after": TIME_WINDOW,
                    "limit": REQUEST_LIMIT,
                    "window": f"{TIME_WINDOW} seconds"
                }
            )
        
        # Get cached user data
        user_data = await get_cached_user_data()
        
        # Add request metadata
        user_data['request_id'] = f"{datetime.utcnow().timestamp()}-{client_id}"
        user_data['rate_limit'] = {
            'remaining': REQUEST_LIMIT - len(request_history.get(client_id, [])),
            'reset': TIME_WINDOW
        }
        
        return user_data
        
    except ValueError as ve:
        logger.error(f"Validation error in supabase-users endpoint: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
        
    except HTTPException as he:
        raise he  # Re-raise HTTP exceptions
        
    except Exception as e:
        logger.error(f"Unexpected error in supabase-users endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Database configuration - Updated to use AWS MySQL
DB_CONFIG = {
    'host': '54.149.111.114',
    'port': 3306,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinfomation'
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

@lru_cache(maxsize=1)
async def get_cached_user_data(cache_key: str) -> Dict[str, Any]:
    """Cache user data for 30 seconds to reduce API calls"""
    try:
        response = supabase.table('auth.users').select('id, email, last_sign_in_at, created_at, updated_at, raw_user_meta_data').execute()
        activity_response = supabase.table('user_activity').select('user_id, last_active, status, metadata').execute()
        
        return {
            "users": response.data if response.data else [],
            "activities": activity_response.data if activity_response.data else [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching Supabase data: {e}")
        return {"users": [], "activities": [], "timestamp": datetime.now().isoformat()}

async def get_active_users():
    """Get count of active users who have signed in within the last 15 minutes or have 'online' status"""
    try:
        # Get cached user data
        user_data = await get_cached_user_data()
        
        # Get current time and time 15 minutes ago
        now = datetime.utcnow()
        fifteen_minutes_ago = now - timedelta(minutes=15)
        
        # Filter active users based on last sign in or online status
        active_users = []
        for user in user_data['users']:
            last_sign_in = datetime.fromisoformat(user['last_sign_in'].replace('Z', '+00:00')) if user['last_sign_in'] else None
            is_recently_active = last_sign_in and last_sign_in >= fifteen_minutes_ago
            is_online = user['status'] == 'online'
            
            if is_recently_active or is_online:
                active_users.append(user)
        
        return {
            'count': len(active_users),
            'users': active_users,
            'total_users': user_data['total_users'],
            'cache_status': user_data['cache_status'],
            'timestamp': now.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        return {
            'count': 0,
            'users': [],
            'total_users': 0,
            'error': str(e),
            'cache_status': 'error',
            'timestamp': datetime.utcnow().isoformat()
        }

@app.get("/supabase-users")
async def get_supabase_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get real-time Supabase user data with caching"""
    try:
        user_data = await get_active_users()
        logger.info(f"Supabase users request processed. Active users: {user_data['count']}")
        return user_data
    except Exception as e:
        logger.error(f"Error fetching Supabase users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin-metrics")
async def get_all_metrics():
    """Get all admin metrics in one call with enhanced user tracking"""
    try:
        logger.info("Admin metrics request received")
        system_load = await get_system_load()
        database_size = get_database_size()
        jobs_info = get_jobs_info()
        user_data = await get_active_users()
        
        result = {
            "system_load": system_load,
            "database_size": database_size,
            "jobs_info": jobs_info,
            "active_users": {
                "count": user_data["count"],
                "total_users": user_data["total_users"],
                "users": user_data["users"],
                "error": user_data["error"],
                "cache_status": user_data["cache_status"],
                "last_updated": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Admin metrics response generated successfully")
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
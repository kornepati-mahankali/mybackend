#!/usr/bin/env python3
"""
Check real data in database
"""

import pymysql
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'db': 'toolinformation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def check_real_data():
    """Check what real data exists in the database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection:
            with connection.cursor() as cursor:
                print("🔍 Checking Real Data in Database...")
                
                # Check total jobs
                cursor.execute("SELECT COUNT(*) as total_jobs FROM jobs")
                total_jobs = cursor.fetchone()['total_jobs']
                print(f"📊 Total Jobs: {total_jobs}")
                
                # Check jobs by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM jobs 
                    GROUP BY status
                """)
                status_counts = cursor.fetchall()
                print(f"📈 Jobs by Status:")
                for status in status_counts:
                    print(f"   - {status['status']}: {status['count']}")
                
                # Check success rate
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful
                    FROM jobs
                """)
                success_data = cursor.fetchone()
                total = success_data['total']
                successful = success_data['successful']
                success_rate = round((successful / total * 100), 1) if total > 0 else 0
                print(f"✅ Success Rate: {success_rate}% ({successful}/{total})")
                
                # Check average duration
                cursor.execute("""
                    SELECT AVG(TIMESTAMPDIFF(SECOND, started_at, completed_at)) as avg_duration_seconds
                    FROM jobs 
                    WHERE started_at IS NOT NULL AND completed_at IS NOT NULL
                """)
                duration_data = cursor.fetchone()
                avg_seconds = duration_data['avg_duration_seconds']
                avg_minutes = round(avg_seconds / 60, 1) if avg_seconds else 0
                print(f"⏱️ Average Duration: {avg_minutes}m")
                
                # Check data volume (based on progress)
                cursor.execute("""
                    SELECT SUM(progress) as total_progress
                    FROM jobs 
                    WHERE progress IS NOT NULL
                """)
                progress_data = cursor.fetchone()
                total_progress = progress_data['total_progress'] or 0
                total_mb = total_progress * 10  # Estimate 10MB per progress unit
                total_gb = round(total_mb / 1024, 1)
                print(f"💾 Data Volume: {total_gb}GB (estimated from progress: {total_progress})")
                
                # Check recent jobs
                cursor.execute("""
                    SELECT id, title, status, progress, created_at, started_at, completed_at
                    FROM jobs 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                recent_jobs = cursor.fetchall()
                print(f"🕒 Recent Jobs:")
                for job in recent_jobs:
                    duration = "N/A"
                    if job['started_at'] and job['completed_at']:
                        duration_seconds = (job['completed_at'] - job['started_at']).total_seconds()
                        duration = f"{round(duration_seconds / 60, 1)}m"
                    
                    print(f"   - {job['title']}: {job['status']} (progress: {job['progress']}, duration: {duration})")
                
                # Check jobs in last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                cursor.execute("""
                    SELECT COUNT(*) as recent_jobs
                    FROM jobs 
                    WHERE created_at >= %s AND created_at <= %s
                """, [start_date, end_date])
                recent_count = cursor.fetchone()['recent_jobs']
                print(f"📅 Jobs in Last 30 Days: {recent_count}")
                
                # Check monthly trends
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as total_jobs,
                        SUM(CASE WHEN status = 'completed' OR status = 'success' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN status = 'failed' OR status = 'error' THEN 1 ELSE 0 END) as failed
                    FROM jobs
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                    ORDER BY month
                """)
                monthly_trends = cursor.fetchall()
                print(f"📈 Monthly Trends (Last 6 Months):")
                for trend in monthly_trends:
                    month_name = datetime.strptime(trend['month'], '%Y-%m').strftime('%b')
                    print(f"   - {month_name}: {trend['total_jobs']} total, {trend['successful']} success, {trend['failed']} failed")
                
    except Exception as e:
        print(f"❌ Error checking real data: {e}")
        raise

if __name__ == "__main__":
    check_real_data() 
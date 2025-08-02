#!/usr/bin/env python3
"""
Check real data in database
"""

from dashboard_api import get_db_connection

def check_real_data():
    """Check what real data is in the database"""
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                # Get recent jobs
                cursor.execute("""
                    SELECT title, status, updated_at, metadata 
                    FROM jobs 
                    ORDER BY updated_at DESC 
                    LIMIT 5
                """)
                recent_jobs = cursor.fetchall()
                
                print("🔍 Recent Jobs in Database:")
                print("=" * 50)
                for job in recent_jobs:
                    print(f"Title: {job['title']}")
                    print(f"Status: {job['status']}")
                    print(f"Updated: {job['updated_at']}")
                    print(f"Metadata: {job['metadata']}")
                    print("-" * 30)
                
                # Get completed today
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM jobs 
                    WHERE status = 'completed' AND DATE(completed_at) = CURDATE()
                """)
                completed_today = cursor.fetchone()['count']
                print(f"✅ Completed Today: {completed_today}")
                
                # Get total downloads
                cursor.execute("""
                    SELECT COALESCE(SUM(CAST(JSON_EXTRACT(metadata, '$.downloads') AS UNSIGNED)), 0) as total
                    FROM jobs WHERE metadata IS NOT NULL
                """)
                total_downloads = cursor.fetchone()['total']
                print(f"✅ Total Downloads: {total_downloads}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_real_data() 
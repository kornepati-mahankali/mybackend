#!/usr/bin/env python3
"""
Script to clear stuck jobs and reset the job queue
"""

import pymysql
import sys

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
        print(f"❌ Database connection failed: {e}")
        return None

def clear_stuck_jobs():
    """Clear stuck jobs and reset the queue"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection:
            with connection.cursor() as cursor:
                # Get current job counts
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM jobs 
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                print("📊 Current job status:")
                for row in results:
                    print(f"   {row['status']}: {row['count']} jobs")
                
                # Reset stuck jobs (running jobs that have been running for too long)
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'failed', 
                        progress = 0,
                        end_time = NOW()
                    WHERE (status = 'running' OR status = '') 
                    AND start_time < NOW() - INTERVAL '1 hour'
                """)
                
                stuck_jobs_reset = cursor.rowcount
                print(f"🔄 Reset {stuck_jobs_reset} stuck running jobs")
                
                # Reset any jobs that have been pending for too long
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'failed', 
                        progress = 0,
                        end_time = NOW()
                    WHERE (status = 'pending' OR status = '') 
                    AND created_at < NOW() - INTERVAL '30 minutes'
                """)
                
                old_pending_reset = cursor.rowcount
                print(f"🔄 Reset {old_pending_reset} old pending jobs")
                
                # Get updated job counts
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM jobs 
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                print("\n📊 Updated job status:")
                for row in results:
                    print(f"   {row['status']}: {row['count']} jobs")
                
                connection.commit()
                return True
                
    except Exception as e:
        print(f"❌ Error clearing stuck jobs: {e}")
        return False

def reset_all_jobs():
    """Reset all jobs to pending status (use with caution)"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection:
            with connection.cursor() as cursor:
                # Reset all non-completed jobs to pending
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'pending', 
                        progress = 0,
                        start_time = NULL,
                        end_time = NULL
                    WHERE status IN ('running', 'failed', '')
                """)
                
                reset_count = cursor.rowcount
                print(f"🔄 Reset {reset_count} jobs to pending status")
                
                connection.commit()
                return True
                
    except Exception as e:
        print(f"❌ Error resetting jobs: {e}")
        return False

def main():
    """Main function"""
    print("🧹 Job Queue Cleanup Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset-all':
        print("⚠️  WARNING: This will reset ALL non-completed jobs to pending!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            if reset_all_jobs():
                print("✅ All jobs reset successfully")
            else:
                print("❌ Failed to reset jobs")
        else:
            print("❌ Operation cancelled")
    else:
        if clear_stuck_jobs():
            print("✅ Stuck jobs cleared successfully")
        else:
            print("❌ Failed to clear stuck jobs")
    
    print("\n💡 Usage:")
    print("   python clear_stuck_jobs.py          # Clear stuck jobs only")
    print("   python clear_stuck_jobs.py --reset-all  # Reset all jobs to pending")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script to fix the job queue by updating empty status jobs
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

def fix_job_queue():
    """Fix the job queue by updating empty status jobs"""
    try:
        connection = pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        
        with connection:
            with connection.cursor() as cursor:
                # Get current status distribution
                cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
                status_counts = cursor.fetchall()
                print("📊 Current job status:")
                for row in status_counts:
                    print(f"   '{row['status']}': {row['count']} jobs")
                
                # Update empty status jobs based on their progress
                print("\n🔧 Fixing empty status jobs...")
                
                # Jobs with progress > 0 but no status -> set to 'running'
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'running' 
                    WHERE (status = '' OR status IS NULL) 
                    AND progress > 0
                """)
                running_updated = cursor.rowcount
                print(f"   Set {running_updated} jobs to 'running' (progress > 0)")
                
                # Jobs with progress = 100 but no status -> set to 'completed'
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'completed' 
                    WHERE (status = '' OR status IS NULL) 
                    AND progress = 100
                """)
                completed_updated = cursor.rowcount
                print(f"   Set {completed_updated} jobs to 'completed' (progress = 100)")
                
                # Remaining empty status jobs -> set to 'pending'
                cursor.execute("""
                    UPDATE jobs 
                    SET status = 'pending' 
                    WHERE status = '' OR status IS NULL
                """)
                pending_updated = cursor.rowcount
                print(f"   Set {pending_updated} jobs to 'pending' (remaining empty)")
                
                # Get updated status distribution
                cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
                updated_status_counts = cursor.fetchall()
                print("\n📊 Updated job status:")
                for row in updated_status_counts:
                    print(f"   '{row['status']}': {row['count']} jobs")
                
                connection.commit()
                print("\n✅ Job queue fixed successfully!")
                
                # Calculate admin panel metrics
                active_jobs = sum(row['count'] for row in updated_status_counts if row['status'] in ['running', 'pending'])
                queued_jobs = sum(row['count'] for row in updated_status_counts if row['status'] == 'pending')
                completed_jobs = sum(row['count'] for row in updated_status_counts if row['status'] == 'completed')
                total_jobs = sum(row['count'] for row in updated_status_counts)
                
                print(f"\n📈 Admin Panel Metrics:")
                print(f"   Active Jobs: {active_jobs}")
                print(f"   Queued Jobs: {queued_jobs}")
                print(f"   Completed Jobs: {completed_jobs}")
                print(f"   Total Jobs: {total_jobs}")
                
    except Exception as e:
        print(f"❌ Error fixing job queue: {e}")

if __name__ == "__main__":
    fix_job_queue() 
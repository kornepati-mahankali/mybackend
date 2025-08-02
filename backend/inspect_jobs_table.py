#!/usr/bin/env python3
"""
Script to inspect the jobs table structure and data
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

def inspect_jobs_table():
    """Inspect the jobs table structure and data"""
    try:
        connection = pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        
        with connection:
            with connection.cursor() as cursor:
                # Get table structure
                cursor.execute("DESCRIBE jobs")
                columns = cursor.fetchall()
                print("📋 Jobs table structure:")
                for col in columns:
                    print(f"   - {col['Field']}: {col['Type']} ({col['Null']})")
                
                print("\n📊 Sample data:")
                cursor.execute("SELECT * FROM jobs LIMIT 5")
                sample_data = cursor.fetchall()
                for row in sample_data:
                    print(f"   {row}")
                
                print("\n📈 Status distribution:")
                cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
                status_counts = cursor.fetchall()
                for row in status_counts:
                    print(f"   - '{row['status']}': {row['count']} jobs")
                
                # Check for jobs with empty status
                cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = '' OR status IS NULL")
                empty_status = cursor.fetchone()
                print(f"\n🔍 Jobs with empty/null status: {empty_status['count']}")
                
                # Check for jobs with 'queued' status
                cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'queued'")
                queued_jobs = cursor.fetchone()
                print(f"🔍 Jobs with 'queued' status: {queued_jobs['count']}")
                
    except Exception as e:
        print(f"❌ Error inspecting jobs table: {e}")

if __name__ == "__main__":
    inspect_jobs_table() 
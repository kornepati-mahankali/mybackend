#!/usr/bin/env python3
"""
Simulate job activity to make job counts more dynamic
"""

import pymysql
import random
import time
from datetime import datetime

def simulate_job_activity():
    """Simulate job activity by updating job statuses"""
    try:
        print("🎭 Simulating job activity...")
        
        # Connect to database
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3307,
            user='root',
            password='thanuja',
            db='toolinformation',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        # Get current job counts
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM jobs 
            GROUP BY status
        """)
        
        results = cursor.fetchall()
        print("📊 Current job counts:")
        for row in results:
            print(f"  - {row['status']}: {row['count']}")
        
        # Simulate job transitions
        # Move some queued jobs to active
        cursor.execute("""
            UPDATE jobs 
            SET status = 'active', updated_at = NOW()
            WHERE status = 'queued' 
            ORDER BY RAND() 
            LIMIT 2
        """)
        
        # Move some active jobs to completed
        cursor.execute("""
            UPDATE jobs 
            SET status = 'completed', updated_at = NOW()
            WHERE status = 'active' 
            ORDER BY RAND() 
            LIMIT 1
        """)
        
        # Add some new queued jobs
        new_jobs = [
            ('Data Scraping Job #21', 'Scraping new portal data', 'queued', 'medium', 0),
            ('Data Scraping Job #22', 'Scraping updated data', 'queued', 'high', 0),
        ]
        
        for title, description, status, priority, progress in new_jobs:
            cursor.execute("""
                INSERT INTO jobs (title, description, status, priority, progress) 
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, status, priority, progress))
        
        connection.commit()
        
        # Get updated job counts
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM jobs 
            GROUP BY status
        """)
        
        results = cursor.fetchall()
        print("\n📊 Updated job counts:")
        for row in results:
            print(f"  - {row['status']}: {row['count']}")
        
        cursor.close()
        connection.close()
        
        print("✅ Job activity simulation completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simulate_job_activity() 
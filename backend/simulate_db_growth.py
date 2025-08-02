#!/usr/bin/env python3
"""
Simulate database growth by adding some data
"""

import pymysql
import time

def simulate_db_growth():
    """Simulate database growth by adding data"""
    try:
        print("📈 Simulating database growth...")
        
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
        
        # Add some data to simulate growth
        # Add more jobs to increase database size
        new_jobs = [
            ('Growth Test Job #1', 'Simulating database growth', 'queued', 'medium', 0),
            ('Growth Test Job #2', 'Adding more data', 'active', 'high', 25),
            ('Growth Test Job #3', 'Database expansion test', 'completed', 'low', 100),
            ('Growth Test Job #4', 'Size increase simulation', 'queued', 'medium', 0),
            ('Growth Test Job #5', 'Growth tracking test', 'active', 'high', 50),
        ]
        
        for title, description, status, priority, progress in new_jobs:
            cursor.execute("""
                INSERT INTO jobs (title, description, status, priority, progress) 
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, status, priority, progress))
        
        connection.commit()
        
        print("✅ Database growth simulation completed!")
        print("📊 Added 5 new jobs to increase database size")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simulate_db_growth() 
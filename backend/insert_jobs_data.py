#!/usr/bin/env python3
"""
Manually insert jobs data
"""

import pymysql

def insert_jobs_data():
    """Insert sample jobs data"""
    try:
        print("📝 Inserting jobs data...")
        
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
        
        # Clear existing data
        cursor.execute("DELETE FROM jobs")
        print("🗑️ Cleared existing jobs data")
        
        # Insert sample data
        sample_jobs = [
            ('Data Scraping Job #1', 'Scraping GEM portal data', 'active', 'high', 75),
            ('Data Scraping Job #2', 'Scraping E-Procurement data', 'queued', 'medium', 0),
            ('Data Scraping Job #3', 'Scraping AP portal data', 'completed', 'low', 100),
            ('Data Scraping Job #4', 'Scraping IREPS data', 'active', 'high', 45),
            ('Data Scraping Job #5', 'Scraping KPP data', 'queued', 'medium', 0),
            ('Data Scraping Job #6', 'Scraping Tender data', 'completed', 'low', 100),
            ('Data Scraping Job #7', 'Scraping Contract data', 'active', 'high', 30),
            ('Data Scraping Job #8', 'Scraping Award data', 'queued', 'medium', 0),
            ('Data Scraping Job #9', 'Scraping Bid data', 'completed', 'low', 100),
            ('Data Scraping Job #10', 'Scraping Vendor data', 'active', 'high', 60),
            ('Data Scraping Job #11', 'Scraping Category data', 'queued', 'medium', 0),
            ('Data Scraping Job #12', 'Scraping Location data', 'completed', 'low', 100),
        ]
        
        for title, description, status, priority, progress in sample_jobs:
            cursor.execute("""
                INSERT INTO jobs (title, description, status, priority, progress) 
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, status, priority, progress))
        
        connection.commit()
        print(f"✅ Inserted {len(sample_jobs)} jobs")
        
        # Verify the data
        cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
        results = cursor.fetchall()
        print("\n📊 Job counts:")
        for row in results:
            print(f"  - {row['status']}: {row['count']}")
        
        cursor.close()
        connection.close()
        print("🎉 Jobs data inserted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    insert_jobs_data() 
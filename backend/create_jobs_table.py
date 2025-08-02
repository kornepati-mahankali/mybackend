#!/usr/bin/env python3
"""
Create jobs table and insert sample data
"""

import pymysql
from datetime import datetime, timedelta
import random

def create_jobs_table():
    """Create jobs table and insert sample data"""
    try:
        print("🔧 Creating jobs table...")
        
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
        
        with connection:
            with connection.cursor() as cursor:
                # Create jobs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        status ENUM('active', 'queued', 'completed', 'failed') DEFAULT 'queued',
                        priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        started_at TIMESTAMP NULL,
                        completed_at TIMESTAMP NULL,
                        progress INT DEFAULT 0 COMMENT 'Progress percentage (0-100)',
                        user_id VARCHAR(100),
                        metadata JSON COMMENT 'Additional job metadata'
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
                
                print("✅ Jobs table created successfully!")
                
                # Check if table already has data
                cursor.execute("SELECT COUNT(*) as count FROM jobs")
                result = cursor.fetchone()
                existing_count = result['count'] if result else 0
                
                if existing_count == 0:
                    print("📝 Inserting sample job data...")
                    
                    # Sample job data
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
                        ('Data Scraping Job #13', 'Scraping Department data', 'active', 'medium', 25),
                        ('Data Scraping Job #14', 'Scraping Region data', 'queued', 'low', 0),
                        ('Data Scraping Job #15', 'Scraping State data', 'completed', 'medium', 100),
                        ('Data Scraping Job #16', 'Scraping District data', 'active', 'high', 80),
                        ('Data Scraping Job #17', 'Scraping City data', 'queued', 'medium', 0),
                        ('Data Scraping Job #18', 'Scraping Village data', 'completed', 'low', 100),
                        ('Data Scraping Job #19', 'Scraping Block data', 'active', 'high', 55),
                        ('Data Scraping Job #20', 'Scraping Panchayat data', 'queued', 'medium', 0)
                    ]
                    
                    # Insert sample data
                    for title, description, status, priority, progress in sample_jobs:
                        cursor.execute("""
                            INSERT INTO jobs (title, description, status, priority, progress) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (title, description, status, priority, progress))
                    
                    print(f"✅ Inserted {len(sample_jobs)} sample jobs!")
                else:
                    print(f"ℹ️ Jobs table already has {existing_count} records")
                
                # Show current job counts
                cursor.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count
                    FROM jobs 
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                print("\n📊 Current job counts:")
                for row in results:
                    print(f"   - {row['status']}: {row['count']}")
        
        connection.close()
        print("🎉 Jobs table setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating jobs table: {e}")
        return False

if __name__ == "__main__":
    create_jobs_table() 
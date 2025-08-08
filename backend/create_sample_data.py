#!/usr/bin/env python3
"""
Script to create sample data for the dashboard
"""

import pymysql
import json
from datetime import datetime, timedelta
import random

# Database configuration for AWS MySQL
DB_CONFIG = {
    'host': '54.149.111.114',
    'port': 3306,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinfomation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_sample_jobs():
    """Create sample jobs in the database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
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
                    print("❌ Jobs table does not exist. Creating it...")
                    cursor.execute("""
                        CREATE TABLE jobs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(255),
                            status VARCHAR(50),
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            completed_at DATETIME NULL,
                            metadata JSON
                        )
                    """)
                    connection.commit()
                    print("✅ Jobs table created successfully")
                
                # Create sample jobs
                sample_jobs = [
                    {
                        'title': 'GEM Data Scraping',
                        'status': 'completed',
                        'created_at': datetime.now() - timedelta(hours=2),
                        'completed_at': datetime.now() - timedelta(hours=1, minutes=30),
                        'metadata': json.dumps({
                            'downloads': 150,
                            'records_extracted': 1200,
                            'error': None
                        })
                    },
                    {
                        'title': 'E-Procurement Tender Scraping',
                        'status': 'completed',
                        'created_at': datetime.now() - timedelta(hours=4),
                        'completed_at': datetime.now() - timedelta(hours=3),
                        'metadata': json.dumps({
                            'downloads': 85,
                            'records_extracted': 650,
                            'error': None
                        })
                    },
                    {
                        'title': 'IREPS Tender Scraping',
                        'status': 'completed',
                        'created_at': datetime.now() - timedelta(hours=6),
                        'completed_at': datetime.now() - timedelta(hours=5, minutes=15),
                        'metadata': json.dumps({
                            'downloads': 200,
                            'records_extracted': 1800,
                            'error': None
                        })
                    },
                    {
                        'title': 'GEM State-wise Scraping',
                        'status': 'queued',
                        'created_at': datetime.now() - timedelta(minutes=30),
                        'completed_at': None,
                        'metadata': json.dumps({
                            'downloads': 0,
                            'records_extracted': 0,
                            'error': None
                        })
                    },
                    {
                        'title': 'E-Procurement Advanced Search',
                        'status': 'queued',
                        'created_at': datetime.now() - timedelta(minutes=15),
                        'completed_at': None,
                        'metadata': json.dumps({
                            'downloads': 0,
                            'records_extracted': 0,
                            'error': None
                        })
                    }
                ]
                
                # Insert sample jobs
                for job in sample_jobs:
                    cursor.execute("""
                        INSERT INTO jobs (title, status, created_at, completed_at, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        job['title'],
                        job['status'],
                        job['created_at'],
                        job['completed_at'],
                        job['metadata']
                    ))
                
                connection.commit()
                print(f"✅ Created {len(sample_jobs)} sample jobs")
                
                # Show current job statistics
                cursor.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count
                    FROM jobs 
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                print("\n📊 Current Job Statistics:")
                for row in results:
                    print(f"  {row['status']}: {row['count']}")
                
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def create_sample_gem_data():
    """Create sample GEM data"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection:
            with connection.cursor() as cursor:
                # Check if gem_data table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'gem_data'
                """, (DB_CONFIG['database'],))
                
                result = cursor.fetchone()
                if not result or result['table_exists'] == 0:
                    print("❌ gem_data table does not exist. Creating it...")
                    cursor.execute("""
                        CREATE TABLE gem_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user_name VARCHAR(100),
                            bid_no VARCHAR(100),
                            name_of_work TEXT,
                            category VARCHAR(100),
                            ministry_and_department VARCHAR(200),
                            quantity VARCHAR(50),
                            emd DECIMAL(15, 2),
                            exemption VARCHAR(50),
                            estimation_value DECIMAL(20, 2),
                            state VARCHAR(100),
                            location VARCHAR(200),
                            apply_mode VARCHAR(50),
                            website_link TEXT,
                            document_link TEXT,
                            attachment_link TEXT,
                            end_date DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    connection.commit()
                    print("✅ gem_data table created successfully")
                
                # Create sample GEM data
                sample_gem_data = [
                    {
                        'user_name': 'Sample User 1',
                        'bid_no': 'GEM-2024-001',
                        'name_of_work': 'IT Infrastructure Development',
                        'category': 'Services',
                        'ministry_and_department': 'Ministry of Electronics and IT',
                        'quantity': '1 Unit',
                        'emd': 50000.00,
                        'exemption': 'No',
                        'estimation_value': 5000000.00,
                        'state': 'Karnataka',
                        'location': 'Bangalore',
                        'apply_mode': 'Online',
                        'website_link': 'https://gem.gov.in',
                        'document_link': 'https://gem.gov.in/docs/001.pdf',
                        'attachment_link': 'https://gem.gov.in/attachments/001.zip',
                        'end_date': '2024-12-31'
                    },
                    {
                        'user_name': 'Sample User 2',
                        'bid_no': 'GEM-2024-002',
                        'name_of_work': 'Office Equipment Supply',
                        'category': 'Goods',
                        'ministry_and_department': 'Ministry of Finance',
                        'quantity': '50 Units',
                        'emd': 25000.00,
                        'exemption': 'Yes',
                        'estimation_value': 2500000.00,
                        'state': 'Maharashtra',
                        'location': 'Mumbai',
                        'apply_mode': 'Online',
                        'website_link': 'https://gem.gov.in',
                        'document_link': 'https://gem.gov.in/docs/002.pdf',
                        'attachment_link': 'https://gem.gov.in/attachments/002.zip',
                        'end_date': '2024-11-30'
                    }
                ]
                
                # Insert sample GEM data
                for data in sample_gem_data:
                    cursor.execute("""
                        INSERT INTO gem_data (
                            user_name, bid_no, name_of_work, category, ministry_and_department,
                            quantity, emd, exemption, estimation_value, state, location,
                            apply_mode, website_link, document_link, attachment_link, end_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        data['user_name'], data['bid_no'], data['name_of_work'], data['category'],
                        data['ministry_and_department'], data['quantity'], data['emd'], data['exemption'],
                        data['estimation_value'], data['state'], data['location'], data['apply_mode'],
                        data['website_link'], data['document_link'], data['attachment_link'], data['end_date']
                    ))
                
                connection.commit()
                print(f"✅ Created {len(sample_gem_data)} sample GEM records")
                
    except Exception as e:
        print(f"❌ Error creating sample GEM data: {e}")

if __name__ == "__main__":
    print("🚀 Creating sample data for dashboard...")
    create_sample_jobs()
    create_sample_gem_data()
    print("✅ Sample data creation completed!")

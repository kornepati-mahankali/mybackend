#!/usr/bin/env python3
"""
Test database connection and check for data
"""

import pymysql
import sys

def test_database_connection():
    """Test MySQL database connection"""
    try:
        print("🔍 Testing database connection...")
        
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
        
        print("✅ Database connection successful!")
        
        with connection:
            with connection.cursor() as cursor:
                # Check if database exists and has tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"📋 Found {len(tables)} tables:")
                for table in tables:
                    table_name = list(table.values())[0]
                    print(f"   - {table_name}")
                
                # Check database size
                cursor.execute("""
                    SELECT 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 2) AS size_gb
                    FROM information_schema.tables 
                    WHERE table_schema = 'toolinformation'
                """)
                
                result = cursor.fetchone()
                if result and result['size_gb']:
                    size_gb = result['size_gb']
                    print(f"💾 Database size: {size_gb} GB")
                else:
                    print("💾 Database size: 0 GB (empty or no tables)")
                
                # Check if jobs table exists
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = 'toolinformation' AND table_name = 'jobs'
                """)
                
                result = cursor.fetchone()
                if result and result['table_exists'] > 0:
                    print("✅ Jobs table found!")
                    
                    # Get job counts
                    cursor.execute("""
                        SELECT 
                            status,
                            COUNT(*) as count
                        FROM jobs 
                        GROUP BY status
                    """)
                    
                    results = cursor.fetchall()
                    print("📊 Job counts:")
                    for row in results:
                        print(f"   - {row['status']}: {row['count']}")
                else:
                    print("❌ Jobs table not found")
                    print("💡 Run create_jobs_table.sql to create it")
                
                # Check for any data in existing tables
                cursor.execute("""
                    SELECT 
                        table_name,
                        table_rows
                    FROM information_schema.tables 
                    WHERE table_schema = 'toolinformation'
                    ORDER BY table_rows DESC
                """)
                
                results = cursor.fetchall()
                print("\n📈 Table row counts:")
                for row in results:
                    print(f"   - {row['table_name']}: {row['table_rows']} rows")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1) 
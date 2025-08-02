#!/usr/bin/env python3
"""
Debug database size calculation
"""

import pymysql

def debug_database_size():
    """Debug database size calculation"""
    try:
        print("🔍 Debugging database size calculation...")
        
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
        
        # Method 1: Standard calculation
        cursor.execute("""
            SELECT 
                COALESCE(SUM(data_length + index_length), 0) AS total_bytes
            FROM information_schema.tables 
            WHERE table_schema = 'toolinformation'
        """)
        
        result = cursor.fetchone()
        print(f"Method 1 - Total bytes: {result['total_bytes']}")
        
        # Method 2: Individual table sizes
        cursor.execute("""
            SELECT 
                table_name,
                data_length,
                index_length,
                (data_length + index_length) AS total_size,
                ROUND(((data_length + index_length) / 1024), 2) AS size_kb
            FROM information_schema.tables 
            WHERE table_schema = 'toolinformation'
            ORDER BY (data_length + index_length) DESC
        """)
        
        results = cursor.fetchall()
        print("\n📊 Individual table sizes:")
        total_bytes = 0
        for row in results:
            table_size = row['total_size'] or 0
            total_bytes += table_size
            print(f"  - {row['table_name']}: {row['size_kb']} KB ({table_size} bytes)")
        
        print(f"\n💾 Total database size: {total_bytes} bytes ({total_bytes/1024:.2f} KB)")
        
        # Method 3: Check if tables have data
        cursor.execute("""
            SELECT 
                table_name,
                table_rows
            FROM information_schema.tables 
            WHERE table_schema = 'toolinformation'
        """)
        
        results = cursor.fetchall()
        print("\n📈 Table row counts:")
        for row in results:
            print(f"  - {row['table_name']}: {row['table_rows']} rows")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_database_size() 
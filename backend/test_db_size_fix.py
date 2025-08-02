#!/usr/bin/env python3
"""
Test database size calculation fix
"""

import pymysql

def test_db_size_calculation():
    """Test the database size calculation"""
    try:
        print("🧪 Testing database size calculation...")
        
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
        
        # Test the exact query from the API
        cursor.execute("""
            SELECT 
                COALESCE(SUM(data_length + index_length), 0) AS total_bytes
            FROM information_schema.tables 
            WHERE table_schema = 'toolinformation'
        """)
        
        result = cursor.fetchone()
        total_bytes = int(result['total_bytes']) if result and result['total_bytes'] else 0
        print(f"Total bytes: {total_bytes}")
        
        # If size is 0, try alternative calculation
        if total_bytes == 0:
            print("⚠️ Size is 0, trying alternative calculation...")
            cursor.execute("""
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024), 2) AS size_kb
                FROM information_schema.tables 
                WHERE table_schema = 'toolinformation'
                ORDER BY (data_length + index_length) DESC
            """)
            
            table_sizes = cursor.fetchall()
            total_kb = sum(float(row['size_kb']) for row in table_sizes if row['size_kb'])
            total_bytes = int(total_kb * 1024) if total_kb > 0 else 0
            print(f"Alternative calculation - Total bytes: {total_bytes}")
        
        # Format the size
        def format_bytes(bytes_value):
            if bytes_value == 0:
                return "0B"
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(bytes_value, 1024)))
            p = math.pow(1024, i)
            s = round(bytes_value / p, 2)
            return f"{s}{size_names[i]}"
        
        formatted_size = format_bytes(total_bytes)
        print(f"✅ Final result: {formatted_size} ({total_bytes} bytes)")
        
        cursor.close()
        connection.close()
        
        return formatted_size
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return "0B"

if __name__ == "__main__":
    test_db_size_calculation() 
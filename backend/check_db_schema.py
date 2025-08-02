#!/usr/bin/env python3
"""
Check existing database schema
"""

import pymysql

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'db': 'toolinformation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def check_schema():
    """Check existing database schema"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection:
            with connection.cursor() as cursor:
                print("🔍 Checking existing database schema...")
                
                # Check what tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (DB_CONFIG['db'],))
                
                tables = cursor.fetchall()
                print(f"\n📋 Existing tables:")
                for table in tables:
                    print(f"  - {table['table_name']}")
                
                # Check jobs table structure if it exists
                cursor.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'jobs'
                """, (DB_CONFIG['db'],))
                
                jobs_exists = cursor.fetchone()['table_count'] > 0
                
                if jobs_exists:
                    print(f"\n📊 Jobs table structure:")
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = 'jobs'
                        ORDER BY ordinal_position
                    """, (DB_CONFIG['db'],))
                    
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                
                # Check tools table structure if it exists
                cursor.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'tools'
                """, (DB_CONFIG['db'],))
                
                tools_exists = cursor.fetchone()['table_count'] > 0
                
                if tools_exists:
                    print(f"\n🛠️ Tools table structure:")
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = 'tools'
                        ORDER BY ordinal_position
                    """, (DB_CONFIG['db'],))
                    
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                
                # Check users table structure if it exists
                cursor.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = 'users'
                """, (DB_CONFIG['db'],))
                
                users_exists = cursor.fetchone()['table_count'] > 0
                
                if users_exists:
                    print(f"\n👥 Users table structure:")
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = 'users'
                        ORDER BY ordinal_position
                    """, (DB_CONFIG['db'],))
                    
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                
                # Check for any other relevant tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND (table_name LIKE '%job%' OR table_name LIKE '%tool%' OR table_name LIKE '%user%')
                    ORDER BY table_name
                """, (DB_CONFIG['db'],))
                
                relevant_tables = cursor.fetchall()
                if relevant_tables:
                    print(f"\n🔗 Other relevant tables:")
                    for table in relevant_tables:
                        print(f"  - {table['table_name']}")
                
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        raise

if __name__ == "__main__":
    check_schema() 
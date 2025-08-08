#!/usr/bin/env python3
"""
Test script to verify AWS MySQL database connection
"""

import os
import sys

# Set environment variables
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'
os.environ['DB_NAME'] = 'toolinfomation'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'thanuja'
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:thanuja@localhost:3306/toolinfomation'

def test_mysql_connection():
    """Test direct MySQL connection"""
    try:
        import pymysql
        
        print("🔍 Testing MySQL connection...")
        print(f"Host: {os.environ['DB_HOST']}")
        print(f"Port: {os.environ['DB_PORT']}")
        print(f"Database: {os.environ['DB_NAME']}")
        print(f"User: {os.environ['DB_USER']}")
        
        conn = pymysql.connect(
            host=os.environ['DB_HOST'],
            port=int(os.environ['DB_PORT']),
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME'],
            charset='utf8mb4'
        )
        
        print("✅ MySQL connection successful!")
        
        # Test query to list tables
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ PyMySQL not installed. Install with: pip install pymysql")
        return False
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    try:
        from sqlalchemy import create_engine, text
        
        print("\n🔍 Testing SQLAlchemy connection...")
        print(f"Database URL: {os.environ['DATABASE_URL']}")
        
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful!")
            
            # Test listing tables
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"📋 Found {len(tables)} tables via SQLAlchemy:")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
        
    except ImportError:
        print("❌ SQLAlchemy not installed. Install with: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing AWS MySQL Database Connection")
    print("=" * 50)
    
    mysql_success = test_mysql_connection()
    sqlalchemy_success = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    if mysql_success and sqlalchemy_success:
        print("🎉 All database connections successful!")
        print("✅ Your backend is ready to connect to AWS MySQL!")
    else:
        print("❌ Some database connections failed!")
        print("Please check your MySQL configuration and credentials.")
        sys.exit(1) 
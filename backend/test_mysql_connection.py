#!/usr/bin/env python3
"""
Test MySQL database connection for E-Procurement system
"""

import os
import sys
from dotenv import load_dotenv
from database_operations_mysql import EProcurementDBMySQL

# Load environment variables from .env file
load_dotenv()

def test_mysql_connection():
    """Test MySQL database connection"""
    print("🔍 Testing MySQL Database Connection...")
    
    # Check environment variables
    print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', '3307')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'root')}")
    print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else '(empty)'}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'toolinformation')}")
    
    try:
        # Create database instance
        db = EProcurementDBMySQL()
        print("✅ Database instance created successfully")
        
        # Test connection
        conn = db.get_connection()
        print("✅ Database connection successful")
        
        # Test table creation
        db.create_table_if_not_exists()
        print("✅ Table creation/verification successful")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eprocurement_tenders")
        count = cursor.fetchone()[0]
        print(f"✅ Current records in table: {count}")
        
        cursor.close()
        conn.close()
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1) 
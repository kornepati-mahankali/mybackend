"""
Database configuration for AWS MySQL connection
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration for AWS MySQL
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', '54.149.111.114'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'toolinfomation'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'thanuja'),
    'charset': 'utf8mb4'
}

# SQLAlchemy connection string
DATABASE_URL = os.getenv('DATABASE_URL', 
    f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")

# For direct MySQL connection (using pymysql)
def get_mysql_connection_params():
    return {
        'host': DATABASE_CONFIG['host'],
        'port': DATABASE_CONFIG['port'],
        'user': DATABASE_CONFIG['user'],
        'password': DATABASE_CONFIG['password'],
        'database': DATABASE_CONFIG['database'],
        'charset': DATABASE_CONFIG['charset']
    }

# Test database connection
def test_database_connection():
    try:
        import pymysql
        conn = pymysql.connect(**get_mysql_connection_params())
        print("✅ Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection() 
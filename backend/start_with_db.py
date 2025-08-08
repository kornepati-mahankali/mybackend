#!/usr/bin/env python3
"""
Startup script for backend with AWS MySQL database connection
"""

import os
import sys
import subprocess

# Set database environment variables
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'
os.environ['DB_NAME'] = 'toolinfomation'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'thanuja'
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:thanuja@localhost:3306/toolinfomation'

# Set server configuration
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = '8002'
os.environ['FLASK_DEBUG'] = 'True'

print("🚀 Starting backend with AWS MySQL database connection...")
print(f"Database: {os.environ['DATABASE_URL']}")
print(f"Server: {os.environ['HOST']}:{os.environ['PORT']}")

# Test database connection first
try:
    from database_config import test_database_connection
    if test_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed! Please check your MySQL configuration.")
        sys.exit(1)
except ImportError as e:
    print(f"⚠️  Warning: Could not import database config: {e}")

# Start the main application
try:
    # Import and run the main application
    from main import app
    import uvicorn
    
    print("🌐 Starting FastAPI server...")
    uvicorn.run(
        app,
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 8002)),
        reload=True
    )
except ImportError as e:
    print(f"❌ Error importing main application: {e}")
    print("Trying alternative startup method...")
    
    # Alternative: run as subprocess
    try:
        subprocess.run([sys.executable, "analytics_api.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 
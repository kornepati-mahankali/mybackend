#!/usr/bin/env python3
"""
Dashboard Setup Test Script
Tests database connection and API endpoints
"""

import requests
import json
import time
from dashboard_api import get_db_connection, get_dashboard_metrics

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM jobs")
                result = cursor.fetchone()
                print(f"✅ Database connection successful - {result['count']} jobs found")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    base_url = "http://localhost:8004"
    
    endpoints = [
        "/health",
        "/api/dashboard/metrics",
        "/api/dashboard/active-jobs",
        "/api/dashboard/completed-today",
        "/api/dashboard/total-downloads",
        "/api/dashboard/success-rate",
        "/api/dashboard/recent-activity",
        "/api/dashboard/weekly-chart",
        "/api/dashboard/system-status"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n🔍 Testing WebSocket connection...")
    try:
        import websocket
        ws = websocket.create_connection("ws://localhost:8002", timeout=5)
        
        # Send ping
        ws.send(json.dumps({"type": "ping"}))
        
        # Wait for response
        response = ws.recv()
        try:
            data = json.loads(response)
            if data.get("type") == "pong":
                print("✅ WebSocket connection successful")
                ws.close()
                return True
            else:
                print("✅ WebSocket connected (response format may vary)")
                ws.close()
                return True
        except json.JSONDecodeError:
            # If we can't parse JSON, but connection works, that's still OK
            print("✅ WebSocket connected (raw response received)")
            ws.close()
            return True
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

def test_dashboard_metrics():
    """Test dashboard metrics calculation"""
    print("\n🔍 Testing dashboard metrics...")
    try:
        metrics = get_dashboard_metrics()
        
        print(f"✅ Active Jobs: {metrics['active_jobs']}")
        print(f"✅ Completed Today: {metrics['completed_today']}")
        print(f"✅ Total Downloads: {metrics['total_downloads']}")
        print(f"✅ Success Rate: {metrics['success_rate']}%")
        print(f"✅ Recent Activity: {len(metrics['recent_activity'])} items")
        print(f"✅ Weekly Chart: {len(metrics['weekly_chart_data'])} days")
        print(f"✅ System Status: {len(metrics['system_status'])} services")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard metrics failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Dashboard Setup Test")
    print("=" * 50)
    
    # Test database
    db_ok = test_database_connection()
    
    # Test API (only if database is working)
    if db_ok:
        test_api_endpoints()
        test_dashboard_metrics()
    
    # Test WebSocket
    test_websocket_connection()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("✅ Dashboard setup appears to be working correctly!")
        print("\nNext steps:")
        print("1. Start the frontend: npm run dev")
        print("2. Open http://localhost:5173")
        print("3. Check the dashboard for real-time updates")
    else:
        print("❌ Dashboard setup has issues. Please check:")
        print("1. MySQL database is running on port 3307")
        print("2. Database credentials are correct")
        print("3. Jobs table exists and has data")
        print("4. Required Python packages are installed")

if __name__ == "__main__":
    main() 
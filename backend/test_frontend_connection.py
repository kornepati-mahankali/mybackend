#!/usr/bin/env python3
"""
Test frontend connection to API
"""

import requests
import json

def test_frontend_connection():
    """Test if frontend can connect to API"""
    try:
        print("🧪 Testing frontend connection to API...")
        
        # Test with frontend-like headers
        headers = {
            'Origin': 'http://localhost:5173',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        
        # Test basic endpoint
        print("1. Testing /test endpoint...")
        response = requests.get('http://localhost:8001/test', headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Test admin metrics endpoint
        print("\n2. Testing /admin-metrics endpoint...")
        response = requests.get('http://localhost:8001/admin-metrics', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database Size: {data.get('database_size', {}).get('total_size', 'N/A')}")
            print(f"   Active Jobs: {data.get('jobs_info', {}).get('active_jobs', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
        
        # Test CORS preflight
        print("\n3. Testing CORS preflight...")
        response = requests.options('http://localhost:8001/admin-metrics', headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        print("\n✅ Frontend connection test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_connection() 
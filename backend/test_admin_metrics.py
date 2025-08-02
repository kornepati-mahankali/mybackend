#!/usr/bin/env python3
"""
Test script for Admin Metrics API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/admin"

def test_endpoint(endpoint, description):
    """Test a specific endpoint"""
    print(f"\n🔍 Testing {description}...")
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {description}")
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Failed: {description}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {description}")
        print(f"Exception: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Admin Metrics API Tests")
    print("=" * 50)
    
    # Test individual endpoints
    endpoints = [
        ("system-load", "System Load Metrics"),
        ("database-size", "Database Size Information"),
        ("jobs-info", "Jobs Information"),
        ("health", "Health Check"),
        ("admin-metrics", "All Metrics Combined")
    ]
    
    results = []
    for endpoint, description in endpoints:
        result = test_endpoint(endpoint, description)
        results.append((description, result))
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for description, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {description}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Admin Metrics API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs.")

if __name__ == "__main__":
    main() 
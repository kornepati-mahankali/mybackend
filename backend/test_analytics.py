#!/usr/bin/env python3
"""
Test script for Analytics API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_analytics_endpoints():
    """Test the analytics API endpoints"""
    
    print("🧪 Testing Analytics API Endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/analytics/health")
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test performance endpoint
    try:
        response = requests.get(f"{BASE_URL}/analytics/performance")
        print(f"✅ Performance endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total Jobs: {data.get('metrics', {}).get('totalJobs', {}).get('value', 'N/A')}")
            print(f"   Success Rate: {data.get('metrics', {}).get('successRate', {}).get('value', 'N/A')}")
            print(f"   Avg Duration: {data.get('metrics', {}).get('avgDuration', {}).get('value', 'N/A')}")
            print(f"   Data Volume: {data.get('metrics', {}).get('dataVolume', {}).get('value', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Performance endpoint failed: {e}")
    
    # Test recent jobs endpoint
    try:
        response = requests.get(f"{BASE_URL}/analytics/recent-jobs")
        print(f"✅ Recent jobs endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Recent jobs count: {len(data.get('recentJobs', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Recent jobs endpoint failed: {e}")
    
    # Test with period parameter
    try:
        response = requests.get(f"{BASE_URL}/analytics/performance?period=90")
        print(f"✅ Performance endpoint (90 days): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Period: {data.get('period', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Performance endpoint (90 days) failed: {e}")

if __name__ == "__main__":
    test_analytics_endpoints() 
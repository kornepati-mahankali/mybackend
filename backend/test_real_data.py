#!/usr/bin/env python3
"""
Test real data from analytics API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_data():
    """Test that analytics API returns real data"""
    
    print("🧪 Testing Real Data from Analytics API...")
    
    try:
        # Test performance endpoint
        response = requests.get(f"{BASE_URL}/analytics/performance")
        print(f"✅ Performance endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Real Data Results:")
            print(f"   Total Jobs: {data.get('metrics', {}).get('totalJobs', {}).get('value', 'N/A')}")
            print(f"   Success Rate: {data.get('metrics', {}).get('successRate', {}).get('value', 'N/A')}")
            print(f"   Avg Duration: {data.get('metrics', {}).get('avgDuration', {}).get('value', 'N/A')}")
            print(f"   Data Volume: {data.get('metrics', {}).get('dataVolume', {}).get('value', 'N/A')}")
            
            # Check if it's real data (not fake numbers)
            total_jobs = data.get('metrics', {}).get('totalJobs', {}).get('value', 0)
            if total_jobs == 19:  # Your actual job count
                print("✅ SUCCESS: API is returning REAL data!")
            elif total_jobs == 1247:  # Old fake data
                print("❌ FAILED: API is still returning FAKE data!")
            else:
                print(f"⚠️  UNKNOWN: API returned {total_jobs} jobs")
                
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_real_data() 
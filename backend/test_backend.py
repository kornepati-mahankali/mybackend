#!/usr/bin/env python3
"""
Test script for E-Procurement Backend
This script tests the basic functionality of the backend server.
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5021"
TEST_TIMEOUT = 30

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print("🔍 Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check passed: {data}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Status check error: {e}")
        return False

def test_sessions_endpoint():
    """Test the sessions endpoint"""
    print("🔍 Testing sessions endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessions check passed: {len(data.get('sessions', []))} sessions found")
            return True
        else:
            print(f"❌ Sessions check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Sessions check error: {e}")
        return False

def test_open_edge_endpoint():
    """Test the open edge endpoint"""
    print("🔍 Testing open edge endpoint...")
    try:
        test_data = {
            "url": "https://eprocurement.gov.in"
        }
        response = requests.post(
            f"{BASE_URL}/api/open-edge", 
            json=test_data, 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Open edge test passed: {data.get('message', '')}")
            return True
        else:
            print(f"❌ Open edge test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Open edge test error: {e}")
        return False

def test_start_scraping_validation():
    """Test the start scraping endpoint validation"""
    print("🔍 Testing start scraping validation...")
    try:
        # Test with missing fields
        test_data = {
            "base_url": "https://eprocurement.gov.in"
            # Missing required fields
        }
        response = requests.post(
            f"{BASE_URL}/api/start-eproc-scraping", 
            json=test_data, 
            timeout=5
        )
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Validation test passed: {data.get('error', '')}")
            return True
        else:
            print(f"❌ Validation test failed: Expected 400, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation test error: {e}")
        return False

def test_file_endpoints():
    """Test file-related endpoints"""
    print("🔍 Testing file endpoints...")
    
    # Test with a non-existent session
    test_session_id = "test_session_123"
    
    try:
        # Test get files for non-existent session
        response = requests.get(f"{BASE_URL}/api/files/{test_session_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('files') == []:
                print("✅ File endpoints test passed: Empty files list for non-existent session")
                return True
            else:
                print(f"❌ File endpoints test failed: Unexpected response")
                return False
        else:
            print(f"❌ File endpoints test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ File endpoints test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 E-Procurement Backend Test Suite")
    print("=" * 50)
    
    # Check if server is running
    print(f"🔗 Testing connection to {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Status Endpoint", test_status_endpoint),
        ("Sessions Endpoint", test_sessions_endpoint),
        ("Open Edge Endpoint", test_open_edge_endpoint),
        ("Start Scraping Validation", test_start_scraping_validation),
        ("File Endpoints", test_file_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the backend server.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1) 
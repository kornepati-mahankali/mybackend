import os
import sys
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

def test_edge_driver():
    print("Testing Edge WebDriver...")
    
    # Get the driver path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(BASE_DIR, "scrapers", "edgedriver_win64", "msedgedriver.exe")
    
    print(f"Driver path: {PATH}")
    print(f"Driver exists: {os.path.exists(PATH)}")
    
    if not os.path.exists(PATH):
        print("ERROR: Driver file not found!")
        return False
    
    # Test different methods
    methods = [
        ("Method 1: With Service", lambda: webdriver.Edge(service=Service(executable_path=PATH))),
        ("Method 2: Without Service", lambda: webdriver.Edge()),
        ("Method 3: With Service and log", lambda: webdriver.Edge(service=Service(executable_path=PATH, log_path="test_edge.log"))),
    ]
    
    for method_name, method_func in methods:
        print(f"\nTrying {method_name}...")
        try:
            driver = method_func()
            print(f"SUCCESS: {method_name} worked!")
            driver.get("https://www.google.com")
            print("Page loaded successfully!")
            driver.quit()
            return True
        except Exception as e:
            print(f"FAILED: {method_name} - {e}")
    
    return False

if __name__ == "__main__":
    success = test_edge_driver()
    if success:
        print("\n✅ Edge WebDriver is working!")
    else:
        print("\n❌ Edge WebDriver failed. Please check:")
        print("1. Microsoft Edge is installed")
        print("2. Edge driver version matches Edge browser version")
        print("3. Run as administrator if needed")
        print("4. Download correct driver from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/") 
import os
import sys
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

def simple_test():
    print("=== Simple Edge WebDriver Test ===")
    
    # Get the driver path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(BASE_DIR, "scrapers", "edgedriver_win64", "msedgedriver.exe")
    
    print(f"Driver path: {PATH}")
    print(f"Driver exists: {os.path.exists(PATH)}")
    
    if not os.path.exists(PATH):
        print("❌ Driver file not found!")
        return False
    
    try:
        print("\nTrying to start Edge...")
        
        # Simple options
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        # Try with service
        service = Service(executable_path=PATH)
        driver = webdriver.Edge(service=service, options=options)
        
        print("✅ Edge started successfully!")
        
        # Try to load a page
        print("Loading Google...")
        driver.get("https://www.google.com")
        print("✅ Page loaded successfully!")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 Edge WebDriver is working!")
    else:
        print("\n💥 Edge WebDriver failed!")
        print("\nPossible solutions:")
        print("1. Run as Administrator")
        print("2. Update Edge driver to match your Edge browser version")
        print("3. Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/") 
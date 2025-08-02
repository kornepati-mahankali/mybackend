#!/usr/bin/env python3
"""
Test growth calculation
"""

import json
from datetime import date, timedelta

def test_growth_calculation():
    """Test the growth calculation logic"""
    try:
        print("🧪 Testing growth calculation...")
        
        # Load the growth history
        with open('db_size_history.json', 'r') as f:
            history = json.load(f)
        
        print(f"📊 Growth history: {history}")
        
        # Get current size
        current_size_bytes = 245760
        
        # Calculate growth
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        previous_size_bytes = 0
        today_growth_bytes = 0
        
        if today in history:
            previous_size_bytes = history[today]
            today_growth_bytes = current_size_bytes - previous_size_bytes
        elif yesterday in history:
            previous_size_bytes = history[yesterday]
            today_growth_bytes = current_size_bytes - previous_size_bytes
        
        print(f"📈 Current size: {current_size_bytes} bytes")
        print(f"📈 Previous size: {previous_size_bytes} bytes")
        print(f"📈 Growth: {today_growth_bytes} bytes")
        
        # Format the growth
        def format_bytes(bytes_value):
            if bytes_value == 0:
                return "0B"
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(bytes_value, 1024)))
            p = math.pow(1024, i)
            s = round(bytes_value / p, 2)
            return f"{s}{size_names[i]}"
        
        formatted_growth = format_bytes(today_growth_bytes)
        print(f"📈 Formatted growth: {formatted_growth}")
        
        # Calculate percentage
        growth_percentage = round((today_growth_bytes / previous_size_bytes * 100), 2) if previous_size_bytes > 0 else 0
        print(f"📈 Growth percentage: {growth_percentage}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_growth_calculation() 
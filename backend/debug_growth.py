#!/usr/bin/env python3
"""
Debug growth calculation
"""

import json
import os
from datetime import date, timedelta

def debug_growth():
    """Debug the growth calculation"""
    try:
        print("🔍 Debugging growth calculation...")
        
        # Current database size
        current_size_bytes = 245760
        
        # Load history
        DB_SIZE_FILE = 'db_size_history.json'
        history = {}
        if os.path.exists(DB_SIZE_FILE):
            with open(DB_SIZE_FILE, 'r') as f:
                history = json.load(f)
        
        print(f"📊 History: {history}")
        
        # Calculate growth like the API does
        previous_size_bytes = 0
        today_growth_bytes = 0
        
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        print(f"📅 Today: {today}")
        print(f"📅 Yesterday: {yesterday}")
        
        if today in history:
            previous_size_bytes = history[today]
            today_growth_bytes = current_size_bytes - previous_size_bytes
            print(f"📈 Using today's previous data: {previous_size_bytes}")
        elif yesterday in history:
            previous_size_bytes = history[yesterday]
            today_growth_bytes = current_size_bytes - previous_size_bytes
            print(f"📈 Using yesterday's data: {previous_size_bytes}")
        else:
            # If no previous data, simulate some growth for demonstration
            today_growth_bytes = current_size_bytes * 0.05  # 5% growth
            print(f"📈 No previous data, simulating 5% growth")
        
        print(f"📈 Current size: {current_size_bytes}")
        print(f"📈 Previous size: {previous_size_bytes}")
        print(f"📈 Growth bytes: {today_growth_bytes}")
        
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
    debug_growth() 
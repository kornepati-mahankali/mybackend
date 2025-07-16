from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure these imports point to actual router objects
from backend.router import tool_runner, tools
from supabase import create_client, Client

supabase_url = "https://zjfjaezztfydiryzsyvd.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpqZmphZXp6dGZ5ZGlyeXpzeXZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjcwMjEsImV4cCI6MjA2NjYwMzAyMX0.6ZVMwXK4aMGmR68GTYo0yt_L7bOg5QWtElTaa8heQos"
supabase: Client = create_client(supabase_url, supabase_key)

app = FastAPI()

# Configure CORS correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin (like Vite or React dev server)
    allow_credentials=True,
    allow_methods=["*"],                      # Allow all methods: GET, POST, PUT, etc.
    allow_headers=["*"],                      # Allow all headers
)

# Include your routers
app.include_router(tool_runner.router)
app.include_router(tools.router)

@app.get("/api/dashboard-overview")
def dashboard_overview():
    # Example queries - replace with your actual table/column names
    # Active jobs: count where status = 'running'
    active_jobs = supabase.table("jobs").select("id").eq("status", "running").execute().data
    # Completed today: count where status = 'completed' and today
    completed_today = supabase.table("jobs").select("id").eq("status", "completed").gte("completed_at", "2024-07-25").execute().data
    # Total downloads: count from downloads table
    total_downloads = supabase.table("downloads").select("id").execute().data
    # Success rate: percent of jobs with status = 'completed'
    total_jobs = supabase.table("jobs").select("id").execute().data
    success_rate = (len([j for j in total_jobs if j.get('status') == 'completed']) / len(total_jobs) * 100) if total_jobs else 0

    # Weekly activity: mock data for now
    weekly_activity = [
        {"day": "Mon", "value": 12},
        {"day": "Tue", "value": 18},
        {"day": "Wed", "value": 6},
        {"day": "Thu", "value": 12},
        {"day": "Fri", "value": 18},
        {"day": "Sat", "value": 14},
        {"day": "Sun", "value": 10}
    ]
    # Recent activity: last 4 jobs
    recent_activity = supabase.table("jobs").select("status,message,details,created_at").order("created_at", desc=True).limit(4).execute().data
    # System status: mock data for now
    system_status = {
        "apiServer": {"status": "Online", "uptime": 99.9},
        "database": {"status": "Online", "uptime": 99.8},
        "queueSystem": {"status": "Online", "uptime": 99.7}
    }
    return JSONResponse({
        "summary": {
            "activeJobs": len(active_jobs),
            "completedToday": len(completed_today),
            "totalDownloads": len(total_downloads),
            "successRate": round(success_rate, 2),
            "activeJobsDelta": 2,  # Placeholder
            "completedTodayDelta": 18,  # Placeholder
            "totalDownloadsDelta": 5.2,  # Placeholder
            "successRateDelta": 2.1  # Placeholder
        },
        "weeklyActivity": weekly_activity,
        "recentActivity": recent_activity,
        "systemStatus": system_status
    })
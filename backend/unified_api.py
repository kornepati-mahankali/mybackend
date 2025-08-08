from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all your existing apps
from main import app as main_app
from scrapers.api import app as scrapers_app
from system_usage_api import app as system_app
from dashboard_api import app as dashboard_app

# Create the unified FastAPI app
app = FastAPI(title="Lavangam Unified API", version="1.0.0")

# Configure CORS for all services
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://lavangam-app-us-west-2.s3-website-us-west-2.amazonaws.com",
        "https://*.elasticbeanstalk.com",
        "https://*.amazonaws.com",
        "*"  # Allow all origins for now
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all your services under different paths
app.mount("/main", main_app)  # Main API endpoints
app.mount("/scrapers", scrapers_app)  # Scrapers API (port 5022)
app.mount("/system", system_app)  # System usage API (port 5024)
app.mount("/dashboard", dashboard_app)  # Dashboard API (port 8004)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Lavangam Unified API",
        "version": "1.0.0",
        "services": {
            "main": "/main",
            "scrapers": "/scrapers", 
            "system": "/system",
            "dashboard": "/dashboard"
        },
        "health": "healthy"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "All services are running"}

# API documentation
@app.get("/docs")
async def api_docs():
    return {
        "message": "API Documentation",
        "endpoints": {
            "main_api": "/main/docs",
            "scrapers_api": "/scrapers/docs", 
            "system_api": "/system/docs",
            "dashboard_api": "/dashboard/docs"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Unified Lavangam API Server...")
    print("📡 Main API: http://localhost:8000/main")
    print("🔧 Scrapers API: http://localhost:8000/scrapers")
    print("📊 System API: http://localhost:8000/system")
    print("📈 Dashboard API: http://localhost:8000/dashboard")
    print("📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
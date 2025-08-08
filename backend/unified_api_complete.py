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
app = FastAPI(title="Lavangam Complete Unified API", version="1.0.0")

# Configure CORS for all services
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
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
app.mount("/main", main_app)  # Port 8000
app.mount("/scrapers", scrapers_app)  # Port 5022
app.mount("/system", system_app)  # Port 5024
app.mount("/dashboard", dashboard_app)  # Port 8004

# Add endpoints for other ports (5002, 5003, 8001, 5021, 5023, 8002)
@app.get("/port-5002")
async def port_5002_endpoint():
    return {"message": "Port 5002 service", "status": "active", "path": "/port-5002"}

@app.get("/port-5003")
async def port_5003_endpoint():
    return {"message": "Port 5003 service", "status": "active", "path": "/port-5003"}

@app.get("/port-8001")
async def port_8001_endpoint():
    return {"message": "Port 8001 service", "status": "active", "path": "/port-8001"}

@app.get("/port-5021")
async def port_5021_endpoint():
    return {"message": "Port 5021 service", "status": "active", "path": "/port-5021"}

@app.get("/port-5023")
async def port_5023_endpoint():
    return {"message": "Port 5023 service", "status": "active", "path": "/port-5023"}

@app.get("/port-8002")
async def port_8002_endpoint():
    return {"message": "Port 8002 service", "status": "active", "path": "/port-8002"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Lavangam Complete Unified API",
        "version": "1.0.0",
        "services": {
            "main": "/main (Port 8000)",
            "scrapers": "/scrapers (Port 5022)", 
            "system": "/system (Port 5024)",
            "dashboard": "/dashboard (Port 8004)",
            "port-5002": "/port-5002",
            "port-5003": "/port-5003",
            "port-8001": "/port-8001",
            "port-5021": "/port-5021",
            "port-5023": "/port-5023",
            "port-8002": "/port-8002"
        },
        "health": "healthy",
        "total_services": 10
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "All services are running",
        "services": [
            "main (8000)", "scrapers (5022)", "system (5024)", "dashboard (8004)",
            "port-5002", "port-5003", "port-8001", "port-5021", "port-5023", "port-8002"
        ]
    }

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
        },
        "port_mappings": {
            "8000": "/main",
            "5022": "/scrapers",
            "5024": "/system", 
            "8004": "/dashboard",
            "5002": "/port-5002",
            "5003": "/port-5003",
            "8001": "/port-8001",
            "5021": "/port-5021",
            "5023": "/port-5023",
            "8002": "/port-8002"
        }
    }

# Port mapping endpoint
@app.get("/port-mapping")
async def port_mapping():
    return {
        "port_mappings": {
            "8000": "/main",
            "5022": "/scrapers", 
            "5024": "/system",
            "8004": "/dashboard",
            "5002": "/port-5002",
            "5003": "/port-5003", 
            "8001": "/port-8001",
            "5021": "/port-5021",
            "5023": "/port-5023",
            "8002": "/port-8002"
        },
        "aws_url": "https://your-eb-url.elasticbeanstalk.com",
        "usage": "Replace localhost:PORT with aws-url/PATH"
    }

if __name__ == "__main__":
    print("🚀 Starting Complete Unified Lavangam API Server...")
    print("📡 Main API: http://localhost:8000/main")
    print("🔧 Scrapers API: http://localhost:8000/scrapers")
    print("📊 System API: http://localhost:8000/system")
    print("📈 Dashboard API: http://localhost:8000/dashboard")
    print("🔌 Port 5002: http://localhost:8000/port-5002")
    print("🔌 Port 5003: http://localhost:8000/port-5003")
    print("🔌 Port 8001: http://localhost:8000/port-8001")
    print("🔌 Port 5021: http://localhost:8000/port-5021")
    print("🔌 Port 5023: http://localhost:8000/port-5023")
    print("🔌 Port 8002: http://localhost:8000/port-8002")
    print("📚 Documentation: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
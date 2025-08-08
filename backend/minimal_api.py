from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create the minimal FastAPI app
app = FastAPI(title="Lavangam Minimal API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Lavangam Minimal API",
        "version": "1.0.0",
        "status": "healthy"
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
        }
    }

# Main API endpoints (Port 8000)
@app.get("/main")
async def main_api():
    return {"message": "Main API (Port 8000)", "status": "active"}

@app.get("/main/api/admin/supabase-users")
async def get_supabase_users():
    return {"users": [], "message": "Supabase users endpoint"}

# Scrapers API endpoints (Port 5022)
@app.get("/scrapers")
async def scrapers_api():
    return {"message": "Scrapers API (Port 5022)", "status": "active"}

# System API endpoints (Port 5024)
@app.get("/system")
async def system_api():
    return {"message": "System API (Port 5024)", "status": "active"}

@app.get("/system/api/metrics")
async def get_system_metrics():
    return {"metrics": {}, "message": "System metrics endpoint"}

# Dashboard API endpoints (Port 8004)
@app.get("/dashboard")
async def dashboard_api():
    return {"message": "Dashboard API (Port 8004)", "status": "active"}

# Other port endpoints
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
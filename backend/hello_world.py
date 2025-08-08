from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World - Lavangam Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/main")
async def main():
    return {"message": "Main API (Port 8000)", "status": "active"}

@app.get("/scrapers")
async def scrapers():
    return {"message": "Scrapers API (Port 5022)", "status": "active"}

@app.get("/system")
async def system():
    return {"message": "System API (Port 5024)", "status": "active"}

@app.get("/dashboard")
async def dashboard():
    return {"message": "Dashboard API (Port 8004)", "status": "active"}

@app.get("/port-5002")
async def port_5002():
    return {"message": "Port 5002 service", "status": "active"}

@app.get("/port-5003")
async def port_5003():
    return {"message": "Port 5003 service", "status": "active"}

@app.get("/port-8001")
async def port_8001():
    return {"message": "Port 8001 service", "status": "active"}

@app.get("/port-5021")
async def port_5021():
    return {"message": "Port 5021 service", "status": "active"}

@app.get("/port-5023")
async def port_5023():
    return {"message": "Port 5023 service", "status": "active"}

@app.get("/port-8002")
async def port_8002():
    return {"message": "Port 8002 service", "status": "active"} 
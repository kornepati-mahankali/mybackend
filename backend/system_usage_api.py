from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
from datetime import datetime
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/system-usage")
def get_system_usage():
    now = datetime.now().strftime("%H:%M")
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    storage = random.randint(75, 85)
    return {
        "time": now,
        "cpu": cpu,
        "memory": memory,
        "storage": storage
    } 
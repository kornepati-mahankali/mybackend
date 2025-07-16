from fastapi import FastAPI, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from .search import run_eproc_scraper
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from uuid import uuid4
from threading import Lock
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session management
sessions = {}
sessions_lock = Lock()

@app.post("/test-edge-launch")
def test_edge_launch():
    options = Options()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(BASE_DIR, "edgedriver_win64", "msedgedriver.exe")
    print(f"[DEBUG] Checking for EdgeDriver at: {PATH}")
    if not os.path.exists(PATH):
        print(f"[ERROR] EdgeDriver not found at {PATH}")
        return JSONResponse(status_code=500, content={"error": f"EdgeDriver not found at {PATH}"})
    try:
        print("[DEBUG] Attempting to launch Edge browser for test...")
        servicee = Service(executable_path=PATH)
        bot = webdriver.Edge(service=servicee, options=options)
        print("[DEBUG] Edge browser should be opening now (test)...")
        bot.get("https://www.google.com")
        print("[DEBUG] Edge browser navigated to Google (test).")
        return {"status": "Edge launched and navigated to Google successfully."}
    except Exception as e:
        print(f"[ERROR] Failed to launch Edge: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/start-scraping")
def start_scraping(
    base_url: str = Query(...),
    tender_type: str = Query(...),
    days_interval: int = Query(...),
    start_page: int = Query(...),
):
    # Start Selenium, open Edge, navigate to URL, return session_id
    options = Options()
    prefs = {"download_restrictions": 3}
    options.add_experimental_option("prefs", prefs)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(BASE_DIR, "edgedriver_win64", "msedgedriver.exe")
    print(f"[DEBUG] Checking for EdgeDriver at: {PATH}")
    if not os.path.exists(PATH):
        print(f"[ERROR] EdgeDriver not found at {PATH}")
    else:
        print(f"[DEBUG] EdgeDriver found at {PATH}")
    print("[DEBUG] Attempting to launch Edge browser...")
    servicee = Service(executable_path=PATH)
    bot = webdriver.Edge(service=servicee, options=options)
    print("[DEBUG] Edge browser should be opening now...")
    bot.get(base_url + "?page=FrontEndAdvancedSearch&service=page")
    print("[DEBUG] Edge browser navigated to URL.")
    # Optionally handle popups here
    session_id = str(uuid4())
    with sessions_lock:
        sessions[session_id] = bot
    return {"session_id": session_id}

@app.post("/submit-captcha")
def submit_captcha(
    session_id: str = Body(...),
    captcha_value: str = Body(...)
):
    # Use Selenium to enter captcha and continue scraping
    with sessions_lock:
        bot = sessions.get(session_id)
    if not bot:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    try:
        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
        bot.find_element(By.ID, "captchaText").send_keys(captcha_value)
        bot.find_element(By.XPATH, "//input[@title='Search']").click()
        # Optionally, continue scraping here or return status
        return {"status": "Captcha submitted, scraping can continue."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/scrapers")
def list_tools():
    return {
        "tools": [
            {
                "id": 1,
                "name": "E-Procurement Tool",
                "category": "eprocurement",
                "icon": "shopping-cart",
                "script_path": "scrapers/search.py",
                "description": "Scrapes data from the E-Procurement website and generates Excel files for each page.",
                "inputs": [
                    { "name": "base_url", "type": "string", "required": True, "description": "Base URL for scraping" },
                    { "name": "tender_type", "type": "string", "required": True, "description": "Tender type (O/L)" },
                    { "name": "days_interval", "type": "int", "required": True, "description": "How many days back to scrape" },
                    { "name": "start_page", "type": "int", "required": True, "description": "Starting page number" }
                ]
            }
        ]
    }

@app.post("/scrape/")
def scrape(
    base_url: str = Query(...),
    tender_type: str = Query(...),
    days_interval: int = Query(...),
    start_page: int = Query(...),
):
    excel_path = run_eproc_scraper(
        base_url=base_url,
        tender_type=tender_type,
        days_interval=days_interval,
        start_page=start_page
    )
    if excel_path and os.path.exists(excel_path):
        return FileResponse(excel_path, filename=os.path.basename(excel_path))
    return {"error": "Excel file not generated."} 
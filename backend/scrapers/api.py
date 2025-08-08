from fastapi import FastAPI, Query, Body, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
from .search import run_eproc_scraper
from . import ireps
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
import shutil
from datetime import datetime
import asyncio
import json

app = FastAPI()

# CORS middleware setup (must be right after app = FastAPI())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket log manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_log(self, message: str):
        import json
        log_data = {"message": message, "timestamp": str(datetime.now())}
        print(f"[DEBUG] Sending log to {len(self.active_connections)} connections: {message}")
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(log_data))
                print(f"[DEBUG] Log sent successfully to connection")
            except Exception as e:
                print(f"[ERROR] Failed to send log to connection: {e}")
                # Remove broken connection
                try:
                    self.active_connections.remove(connection)
                except ValueError:
                    pass

log_manager = ConnectionManager()

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await log_manager.connect(websocket)
    print(f"[DEBUG] WebSocket connected. Total connections: {len(log_manager.active_connections)}")
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                if message_data.get('type') == 'test':
                    print(f"[DEBUG] Received test message from frontend: {message_data.get('message')}")
                    # Send a test response
                    test_response = {"message": "[TEST] Backend received your test message!", "timestamp": str(datetime.now())}
                    await websocket.send_text(json.dumps(test_response))
            except json.JSONDecodeError:
                print(f"[DEBUG] Received non-JSON message: {data}")
            
            # Send a ping message to keep connection alive
            ping_data = {"message": "[PING] Connection alive", "timestamp": str(datetime.now())}
            await websocket.send_text(json.dumps(ping_data))
            await asyncio.sleep(30)  # Send ping every 30 seconds
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)
        print(f"[DEBUG] WebSocket disconnected. Remaining connections: {len(log_manager.active_connections)}")
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        log_manager.disconnect(websocket)

# Example usage: await log_manager.send_log("Scraping started...")
# In your scraping logic, call this to send logs to the frontend.

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

@app.post("/ireps/open-edge")
def ireps_open_edge(name: str = Body(...), starting_page: int = Body(...)):
    # Always open Chrome for IREPS
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CHROME_PATH = os.path.join(BASE_DIR, "edgedriver_win64", "chromedriver.exe")
    browser = None
    try:
        print(f"[DEBUG] Checking for ChromeDriver at: {CHROME_PATH}")
        if not os.path.exists(CHROME_PATH):
            print(f"[ERROR] ChromeDriver not found at {CHROME_PATH}")
            return JSONResponse(
                status_code=500, 
                content={
                    "error": f"Chrome WebDriver not found at {CHROME_PATH}",
                    "path": CHROME_PATH,
                    "base_dir": BASE_DIR,
                    "files_in_dir": os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else "Directory not found"
                }
            )
        
        print("[DEBUG] ChromeDriver found, creating Chrome options...")
        options = ChromeOptions()
        # Add some common options to avoid issues
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("[DEBUG] Creating Chrome service...")
        servicec = ChromeService(executable_path=CHROME_PATH)
        
        print("[DEBUG] Launching Chrome browser...")
        bot = webdriver.Chrome(service=servicec, options=options)
        
        print("[DEBUG] Chrome browser launched, navigating to IREPS...")
        bot.get("https://www.ireps.gov.in/epsn/guestLogin.do")
        
        print("[DEBUG] Successfully navigated to IREPS website")
        browser = "chrome"
        
        session_id = str(uuid4())
        with sessions_lock:
            sessions[session_id] = {"bot": bot, "name": name, "starting_page": starting_page}
        
        print(f"[DEBUG] Session created with ID: {session_id}")
        return {"session_id": session_id, "browser": browser}
        
    except Exception as e:
        print(f"[ERROR] Failed to open Chrome: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to open Chrome: {str(e)}"})

@app.post("/ireps/start-scraping")
async def ireps_start_scraping(request: Request):
    try:
        data = await request.json()
        session_id = data.get('session_id')
        name = data.get('name')
        starting_page = data.get('starting_page')
        
        print(f"[DEBUG] Starting IREPS scraping for session: {session_id}")
        print(f"[DEBUG] Parameters: name={name}, starting_page={starting_page}")
        
        with sessions_lock:
            session = sessions.get(session_id)
        
        if not session:
            print(f"[ERROR] Session {session_id} not found")
            return JSONResponse(status_code=404, content={"error": "Session not found"})
        
        bot = session["bot"]
        # Use name and starting_page from request, fallback to session if not provided
        name = name or session.get("name")
        starting_page = starting_page or session.get("starting_page")
        
        # Add stop flag to session
        session["stop_flag"] = False
        session["scraping_thread"] = None
        
        print(f"[DEBUG] Using parameters: name={name}, starting_page={starting_page}")
        print(f"[DEBUG] Bot object: {type(bot)}")
        
        import asyncio
        def log_callback(msg):
            try:
                print(f"[IREPS LOG] {msg}")
                # Use asyncio.run for thread safety - this is the recommended approach
                asyncio.run(log_manager.send_log(msg))
            except Exception as e:
                print(f"[ERROR] Failed to send log via WebSocket: {e}")
                import traceback
                traceback.print_exc()
        
        def run_scraper():
            try:
                print(f"[DEBUG] Starting scraper thread for session {session_id}")
                log_callback("[IREPS] Scraping started...")
                log_callback(f"[IREPS] Starting page: {starting_page}")
                log_callback(f"[IREPS] Name: {name}")
                
                # Pass the session to check for stop flag
                output_files = ireps.scrape_with_selenium(bot, name, starting_page, log_callback, session_id, session)
                
                if output_files:
                    log_callback(f"[IREPS] Scraping finished! Output files: {', '.join([os.path.basename(f) for f in output_files])}")
                else:
                    log_callback("[IREPS] No output files generated.")
                print(f"[DEBUG] Scraper thread completed for session {session_id}")
            except Exception as e:
                print(f"[ERROR] Scraper thread failed: {e}")
                import traceback
                traceback.print_exc()
                log_callback(f"[ERROR] Scraping failed: {str(e)}")
        
        import threading
        thread = threading.Thread(target=run_scraper)
        thread.daemon = True
        thread.start()
        
        # Store thread reference in session
        with sessions_lock:
            session["scraping_thread"] = thread
        
        print(f"[DEBUG] Scraper thread started for session {session_id}")
        
        # Send a test log message immediately
        try:
            asyncio.run(log_manager.send_log("[IREPS] Test log message - scraping thread started"))
            print("[DEBUG] Test log message sent successfully")
        except Exception as e:
            print(f"[ERROR] Failed to send test log: {e}")
            import traceback
            traceback.print_exc()
        
        return {"status": "Scraping started", "session_id": session_id}
        
    except Exception as e:
        print(f"[ERROR] Failed to start IREPS scraping: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to start scraping: {str(e)}"})

@app.post("/ireps/delete-file")
def delete_file(session_id: str = Body(...), filename: str = Body(...)):
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
    file_path = os.path.join(OUTPUTDIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.post("/ireps/merge-files")
def merge_files(session_id: str = Body(...)):
    try:
        print(f"[DEBUG] Starting merge process for session: {session_id}")
        
        BASEDIR = os.path.dirname(os.path.abspath(__file__))
        OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
        
        if not os.path.exists(OUTPUTDIR):
            print(f"[ERROR] Output directory not found: {OUTPUTDIR}")
            return JSONResponse(status_code=404, content={"error": "Output directory not found"})
        
        import pandas as pd
        import fnmatch
        file_prefix = "tenders_page"
        filenames = [os.path.join(OUTPUTDIR, filename)
                     for filename in os.listdir(OUTPUTDIR)
                     if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")]
        print(f"[DEBUG] Files to merge: {filenames}")
        
        if not filenames:
            print("[ERROR] No files found to merge")
            return JSONResponse(status_code=400, content={"error": "No Excel files found to merge"})
        
        if len(filenames) == 1:
            print(f"[DEBUG] Only one file found, returning it as merged file: {filenames[0]}")
            from fastapi.responses import FileResponse
            return FileResponse(
                filenames[0], 
                filename=f"merged_data_{session_id}.csv",
                media_type='text/csv'
            )
        
        dataframes = []
        for file_path in filenames:
            try:
                print(f"[DEBUG] Reading file: {os.path.basename(file_path)}")
                df = pd.read_excel(file_path, engine='openpyxl')
                print(f"[DEBUG] DataFrame shape: {df.shape}")
                dataframes.append(df)
            except Exception as e:
                print(f"[ERROR] Error reading {file_path}: {e}")
                continue
        
        if not dataframes:
            print("[ERROR] No valid dataframes to merge after filtering unreadable files.")
            return JSONResponse(status_code=400, content={"error": "No valid Excel files could be read. Check file format and content."})
        
        print(f"[DEBUG] Merging {len(dataframes)} dataframes")
        merged_df = pd.concat(dataframes, ignore_index=True)
        print(f"[DEBUG] Merged DataFrame shape: {merged_df.shape}")
        
        output_csv_file = os.path.join(OUTPUTDIR, f"merged_data_{session_id}.csv")
        merged_df.to_csv(output_csv_file, index=False)
        print(f"[DEBUG] Merged CSV file saved to: {output_csv_file}")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            output_csv_file, 
            filename=f"merged_data_{session_id}.csv",
            media_type='text/csv'
        )
        
    except Exception as e:
        print(f"[ERROR] Merge process failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Merge process failed: {str(e)}"})

@app.post("/ireps/kmerge-files")
def kmerge_files(session_id: str = Body(...)):
    import pandas as pd
    import fnmatch
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
    file_prefix = "tenders_page"
    filenames = [os.path.join(OUTPUTDIR, filename)
                 for filename in os.listdir(OUTPUTDIR)
                 if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")]
    dataframes = []
    for file_path in filenames:
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            # Filter for Karnataka rows (case-insensitive, any column containing 'karnataka')
            mask = df.apply(lambda row: row.astype(str).str.contains('karnataka', case=False, na=False).any(), axis=1)
            karnataka_df = df[mask]
            if not karnataka_df.empty:
                dataframes.append(karnataka_df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        output_csv_file = os.path.join(OUTPUTDIR, f"karnataka_merged_{session_id}.csv")
        merged_df.to_csv(output_csv_file, index=False)
        from fastapi.responses import FileResponse
        return FileResponse(output_csv_file, filename=f"karnataka_merged_{session_id}.csv", media_type='text/csv')
    else:
        return JSONResponse(status_code=400, content={"error": "No Karnataka data found to merge."})

@app.post("/ireps/stop-session")
def stop_session(session_id: str = Body(...)):
    try:
        print(f"[DEBUG] Stopping session: {session_id}")
        
        with sessions_lock:
            session = sessions.get(session_id)
        
        if session:
            # Set stop flag to signal the scraping thread to stop
            session["stop_flag"] = True
            print(f"[DEBUG] Stop flag set for session: {session_id}")
            
            # Wait for thread to finish (with timeout)
            if session.get("scraping_thread"):
                import threading
                thread = session["scraping_thread"]
                if thread.is_alive():
                    print(f"[DEBUG] Waiting for scraping thread to finish...")
                    thread.join(timeout=10)  # Wait up to 10 seconds
                    if thread.is_alive():
                        print(f"[WARNING] Scraping thread did not stop within timeout")
            
            # Close browser
            if 'bot' in session:
                try:
                    print(f"[DEBUG] Closing browser for session: {session_id}")
                    session['bot'].quit()
                    print(f"[DEBUG] Browser closed for session: {session_id}")
                except Exception as e:
                    print(f"[ERROR] Error closing browser: {e}")
            
            # Remove session from memory
            sessions.pop(session_id, None)
        
        print(f"[DEBUG] Session {session_id} stopped successfully")
        return {"status": "stopped", "session_id": session_id}
        
    except Exception as e:
        print(f"[ERROR] Failed to stop session {session_id}: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to stop session: {str(e)}"})

@app.get("/ireps/files")
def ireps_list_files(session_id: str = Query(...)):
    # List output files for the session
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
    print(f"[DEBUG] Listing files for session: {session_id}")
    print(f"[DEBUG] Output directory: {OUTPUTDIR}")
    print(f"[DEBUG] Directory exists: {os.path.exists(OUTPUTDIR)}")
    
    if not os.path.exists(OUTPUTDIR):
        print(f"[DEBUG] Directory does not exist, returning empty list")
        return {"files": []}
    
    all_files = os.listdir(OUTPUTDIR)
    print(f"[DEBUG] All files in directory: {all_files}")
    
    files = [f for f in all_files if f.endswith(".xlsx")]
    print(f"[DEBUG] Excel files found: {files}")
    
    result = {"files": files}
    print(f"[DEBUG] Returning: {result}")
    return result

@app.get("/ireps/download/{session_id}/{filename}")
def ireps_download_file(session_id: str, filename: str, request: Request):
    print(f"[DEBUG] IREPS download request: {request.method} for {session_id}/{filename}")
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
    file_path = os.path.join(OUTPUTDIR, filename)
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return JSONResponse(status_code=404, content={"error": "File not found"})
    print(f"[DEBUG] Serving file: {file_path}")
    return FileResponse(file_path, filename=filename)

@app.get("/ireps/merge-download/{session_id}")
def ireps_merge_download(session_id: str):
    """GEM-style merge and download endpoint for IREPS, with DB insert"""
    import pandas as pd
    import fnmatch
    import pymysql
    try:
        BASEDIR = os.path.dirname(os.path.abspath(__file__))
        OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
        if not os.path.exists(OUTPUTDIR):
            print(f"[ERROR] Output directory not found: {OUTPUTDIR}")
            return JSONResponse(status_code=400, content={"error": "Output directory not found"})
        file_prefix = "tenders_page"
        filenames = [os.path.join(OUTPUTDIR, filename)
                     for filename in os.listdir(OUTPUTDIR)
                     if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")]
        print(f"[DEBUG] Files to merge: {filenames}")
        if not filenames:
            print("[ERROR] No files found to merge")
            return JSONResponse(status_code=400, content={"error": "No Excel files found to merge"})
        dataframes = []
        for file_path in filenames:
            try:
                print(f"[DEBUG] Reading file: {os.path.basename(file_path)}")
                df = pd.read_excel(file_path, engine='openpyxl')
                print(f"[DEBUG] DataFrame shape: {df.shape}")
                dataframes.append(df)
            except Exception as e:
                print(f"[ERROR] Error reading {file_path}: {e}")
                continue
        if not dataframes:
            print("[ERROR] No valid dataframes to merge after filtering unreadable files.")
            return JSONResponse(status_code=400, content={"error": "No valid Excel files could be read. Check file format and content."})
        print(f"[DEBUG] Merging {len(dataframes)} dataframes")
        merged_df = pd.concat(dataframes, ignore_index=True)
        print(f"[DEBUG] Merged DataFrame shape: {merged_df.shape}")
        # Remove rows where all values are null
        merged_df = merged_df.dropna(how='all')
        # Remove duplicate rows
        merged_df = merged_df.drop_duplicates()
        # Rename columns to match existing MySQL `tender` table structure
        column_rename_map = {
            'Deptt./Rly. Unit': 'department',
            'Tender No': 'tender_id',
            'Tender Title': 'name_of_work',
            'Work Area': 'location',
            'Due Date/Time': 'closing_date',
            'Website': 'website'  # if present
        }
        merged_df.rename(columns=column_rename_map, inplace=True)

        # Normalize date format for closing_date to YYYY-MM-DD
        if 'closing_date' in merged_df.columns:
            try:
                merged_df['closing_date'] = merged_df['closing_date'].astype(str).str.slice(0, 10)
            except Exception:
                pass

        # Keep only columns that exist in `tender` table
        valid_columns = [
            'tender_id', 'name_of_work', 'department', 'location', 'closing_date', 'website'
        ]
        merged_df = merged_df[[col for col in merged_df.columns if col in valid_columns]]

        # Save as CSV (for download)
        output_csv_file = os.path.join(OUTPUTDIR, f"merged_data_{session_id}.csv")
        merged_df.to_csv(output_csv_file, index=False)
        print(f"[DEBUG] Merged CSV file saved to: {output_csv_file}")
        
        # Insert into MySQL tender table (AWS) with existing columns only
        if not merged_df.empty:
            try:
                connection = pymysql.connect(
                    host='54.149.111.114',
                    port=3306,
                    user='root',
                    password='thanuja',
                    db='toolinfomation',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                with connection:
                    with connection.cursor() as cursor:
                        cols = ','.join(f'`{col}`' for col in merged_df.columns)
                        placeholders = ','.join(['%s'] * len(merged_df.columns))
                        sql = f'INSERT INTO tender ({cols}) VALUES ({placeholders})'
                        for row in merged_df.itertuples(index=False, name=None):
                            cursor.execute(sql, row)
                    connection.commit()
                    print(f"[SUCCESS] Inserted {len(merged_df)} rows into tender table (AWS)")
            except Exception as e:
                print(f"[ERROR] Failed to insert merged data into tender (AWS): {e}")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            output_csv_file,
            filename=f"merged_data_{session_id}.csv",
            media_type='text/csv'
        )
    except Exception as e:
        print(f"[ERROR] Merge process failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Merge process failed: {str(e)}"}) 
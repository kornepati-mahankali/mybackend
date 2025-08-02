import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from os import *
import os

def scrape_with_selenium(bot, name, starting_page, log_callback, session_id, session=None):
    print("[DEBUG] Entered scrape_with_selenium")
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUTDIR = os.path.join(BASEDIR, "ireps", session_id)
    os.makedirs(OUTPUTDIR, exist_ok=True)
    try:
        log_callback("[DEBUG] Scraper started")
        # 1. Copy cookies from Selenium to Requests
        cookies = bot.get_cookies()
        session_req = requests.Session()
        for cookie in cookies:
            session_req.cookies.set(cookie['name'], cookie['value'])
        # 2. Define request parameters
        base_url = "https://www.ireps.gov.in/epsn/anonymSearch.do"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.ireps.gov.in/epsn/anonymSearch.do"
        }
        today = datetime.today().strftime("%d/%m/%Y")
        payload = {
            "division": "-1",
            "unit": "-1",
            "tenderStage": "-1",
            "tenderType": "-1",
            "bidding": "-1",
            "advancedSearch": "showPageClosed",
            "searchParam": "showPageLive",
            "searchOption": "1",
            "searchOptorOption": "0",
            "railwayZone": "-1",
            "dateFrom": today,
            "dateTo": today,
            "linkVal": "department",
            "selectDate": "TENDER_OPENING_DATE",
            "submit": "All Active Tenders"
        }
        # 3. Loop through all pages and save each page to its own Excel file
        page = int(starting_page)
        output_files = []
        while True:
            # Check for stop flag
            if session and session.get("stop_flag", False):
                log_callback("🛑 Scraping stopped by user")
                print("[DEBUG] Stop flag detected, breaking loop")
                break
            payload["pageNo"] = str(page)
            # Retry logic for request
            max_retries = 3
            retry_delay = 5  # seconds
            for attempt in range(max_retries):
                try:
                    print(f"[DEBUG] Requesting page {page}, attempt {attempt+1}")
                    response = session_req.post(base_url, headers=headers, data=payload, timeout=15)
                    break  # Success
                except requests.exceptions.RequestException as e:
                    log_callback(f"⚠️ Error on page {page}, attempt {attempt+1}: {e}")
                    print(f"[ERROR] RequestException on page {page}, attempt {attempt+1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        log_callback("❌ Maximum retry attempts reached. Exiting.")
                        print("[ERROR] Maximum retry attempts reached. Exiting loop.")
                        return output_files
            soup = BeautifulSoup(response.text, "html.parser")
            # Check for session timeout or redirect
            if soup.title and "Login" in soup.title.string:
                log_callback("🔒 Session appears to have expired. Please restart and log in again.")
                print("[DEBUG] Session expired detected in HTML.")
                break
            # Locate the target table
            tables = soup.find_all("table")
            target_table = None
            header_index = None
            for table in tables:
                rows = table.find_all("tr")
                for idx, row in enumerate(rows):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                    if any("Deptt./Rly. Unit" in cell for cell in cells):
                        target_table = table
                        header_index = idx
                        break
                if target_table:
                    break
            if not target_table or header_index is None:
                log_callback(f"📭 No more data found on page {page}. Stopping.")
                print(f"[DEBUG] No target table found on page {page}, breaking loop.")
                break
            rows = target_table.find_all("tr")
            page_data = []
            for row in rows[header_index + 1:]:
                cols = [cell.get_text(strip=True) for cell in row.find_all("td")]
                if cols:
                    page_data.append(cols)
            if page_data:
                df = pd.DataFrame(page_data)
                df = df.iloc[32:56, 0:7]  # Keep only first 7 columns
                df.columns = [
                    "Deptt./Rly. Unit",
                    "Tender No",
                    "Tender Title",
                    "Status",
                    "Work Area",
                    "Due Date/Time",
                    "Due Days"
                ]
                PATH = os.path.join(OUTPUTDIR, f"tenders_page_{page}.xlsx")
                print(f"[DEBUG] Saving Excel file to: {PATH}")
                try:
                    df.to_excel(PATH, index=False)
                    print(f"[DEBUG] Saved Excel file: {PATH}")
                except Exception as e:
                    print(f"[ERROR] Exception saving Excel file: {e}")
                    log_callback(f"[ERROR] Exception saving Excel file: {e}")
                output_files.append(PATH)
                log_callback(f"✅ Saved page {page} to '{PATH}'")
            else:
                log_callback(f"📭 Page {page} had no data rows. Stopping.")
                print(f"[DEBUG] Page {page} had no data rows, breaking loop.")
                break
            page += 1
            time.sleep(3)  # Be polite to the server
        print(f"[DEBUG] scrape_with_selenium finished, output_files: {output_files}")
        return output_files
    except Exception as e:
        print(f"[ERROR] Exception in scrape_with_selenium: {e}")
        import traceback; traceback.print_exc()
        log_callback(f"[ERROR] Exception in scraper: {e}")
        return []

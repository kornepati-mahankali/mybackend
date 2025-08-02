import eventlet
eventlet.monkey_patch()

from flask import Flask, Response, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
from flask_cors import CORS

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd
from os import path, makedirs
from datetime import date, timedelta
import time
import requests
import base64
import re
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
socketio = SocketIO(app, cors_allowed_origins="*")

scraping_process_eproc = None

# --- Scraper dependencies and helpers ---
today = date.today()
TIMEOUT = 6
BASE_DIR = path.dirname(path.abspath(__file__))
OUTPUT_DIR = path.join(BASE_DIR, "scrapers", "OUTPUT")
if not path.exists(OUTPUT_DIR):
    makedirs(OUTPUT_DIR)
FILE_NAME = "open-tenders_output_page-{}.xlsx"  # default, will be set dynamically

# Add global variable to store the bot/session for captcha step
pending_eproc_sessions = {}

def debug_page_state(bot, step_name):
    """Take screenshot and save page source for debugging"""
    try:
        timestamp = str(int(time.time()))
        screenshot_path = f"debug_screenshot_{step_name}_{timestamp}.png"
        bot.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        
        page_source_path = f"debug_page_source_{step_name}_{timestamp}.html"
        with open(page_source_path, 'w', encoding='utf-8') as f:
            f.write(bot.page_source)
        print(f"Page source saved: {page_source_path}")
    except Exception as e:
        print(f"Debug save failed: {e}")

def solve_captcha_main(bot, captcha=None):
    WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
    if captcha is not None:
        solvcap = captcha.strip()
    else:
        solvcap = input("enter captcha:").strip()
    
    print(f"Entering captcha: {solvcap}")
    bot.find_element(By.ID, "captchaText").send_keys(solvcap)
    sleep(2)
    
    print("Clicking search button")
    bot.find_element(By.XPATH, "//input[@title='Search']").click()
    
    # Wait a bit for the page to process
    sleep(3)
    
    # Debug: Take screenshot after captcha submission
    debug_page_state(bot, "after_captcha")
    
    # Check for multiple success indicators
    success_indicators = [
        (By.CLASS_NAME, "list_footer"),
        (By.ID, "table"),
        (By.CLASS_NAME, "tablebg"),
        (By.XPATH, "//table[@id='table']"),
        (By.XPATH, "//div[contains(@class, 'list')]")
    ]
    
    # Also check for error messages
    error_indicators = [
        (By.CLASS_NAME, "error"),
        (By.CLASS_NAME, "alert"),
        (By.XPATH, "//*[contains(text(), 'Invalid')]"),
        (By.XPATH, "//*[contains(text(), 'incorrect')]"),
        (By.XPATH, "//*[contains(text(), 'wrong')]")
    ]
    
    # Check for errors first
    for error_selector in error_indicators:
        try:
            error_element = bot.find_element(*error_selector)
            error_text = error_element.text.strip()
            if error_text and any(keyword in error_text.lower() for keyword in ['invalid', 'incorrect', 'wrong', 'error']):
                print(f"Captcha error detected: {error_text}")
                return False
        except NoSuchElementException:
            continue
    
    # Check for success indicators
    for success_selector in success_indicators:
        try:
            WebDriverWait(bot, 5).until(EC.presence_of_element_located(success_selector))
            print(f"Success indicator found: {success_selector}")
            return True
        except:
            continue
    
    # If we can't find success indicators, check if we're still on the search page
    try:
        current_url = bot.current_url
        if "FrontEndAdvancedSearch" in current_url:
            print("Still on search page - captcha likely failed")
            return False
        else:
            print(f"Page changed to: {current_url} - captcha likely succeeded")
            return True
    except:
        print("Could not determine page state")
        return False

def get_basic_details(bot):
    organisation_chain = ""
    organisation_chain_filter = "Organisation Chain"
    tender_reference_number = ""
    tender_reference_number_filter = "Tender Reference Number"
    tender_id = ""
    tender_id_filter = "Tender ID"
    tender_type = ""
    tender_type_filter = "Tender Category"
    tender_category = ""
    tender_category_filter = "Tender Category"
    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")
        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()
            if organisation_chain_filter == captain_text:
                organisation_chain = field.text.strip()
            if tender_reference_number_filter == captain_text:
                tender_reference_number = field.text.strip()
            if tender_id_filter == captain_text:
                tender_id = field.text.strip()
            if tender_type_filter == captain_text:
                tender_type = field.text.strip()
            if tender_category_filter == captain_text:
                tender_category = field.text.strip()
    return organisation_chain, tender_reference_number, tender_id, tender_category, tender_type

def get_fee_details(bot):
    tender_fee = ""
    tender_fee_filter = "Tender Fee in ₹"
    fee_payable_to = ""
    fee_payable_to_filter = "Fee Payable To"
    exepm_allowed = ""
    exep_filter = "Tender Fee Exemption Allowed"
    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")
        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()
            if tender_fee_filter == captain_text:
                tender_fee = field.text.strip()
            if fee_payable_to_filter == captain_text:
                fee_payable_to = field.text.strip()
            if exep_filter == captain_text:
                exepm_allowed = field.text.strip()
    return tender_fee, fee_payable_to, exepm_allowed

def get_emd_details(bot):
    emd_amout = ""
    emd_amout_filter = "EMD Amount in ₹"
    emd_payable_to = ""
    emd_payable_to_filter = "EMD Payable To"
    emd_exepm_allowed = ""
    emd_exepm_allowed_filter = "EMD through BG/ST or EMD Exemption Allowed"
    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")
        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()
            if emd_amout_filter == captain_text:
                emd_amout = field.text.strip()
            if emd_payable_to_filter == captain_text:
                emd_payable_to = field.text.strip()
            if emd_exepm_allowed_filter == captain_text:
                emd_exepm_allowed = field.text.strip()
    return emd_amout, emd_payable_to, emd_exepm_allowed

def get_work_details(bot):
    title = ""
    title_filter = "Title"
    word_desc = ""
    word_desc_filter = "Work Description"
    tander_value_in = ""
    tander_value_in_filter = "Tender Value in ₹"
    location = ""
    location_filter = "Location"
    pincode = ""
    pincode_filter = "Pincode"   
    pre_bid_address = ""
    pre_bid_address_filter = "Pre Bid Meeting Address"
    pre_bid_date = ""
    pre_bid_date_filter = "Pre Bid Meeting Date"
    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")
        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()
            if title_filter in captain_text:
                title = field.text.strip()
            if tander_value_in_filter in captain_text:
                tander_value_in = field.text.strip()
            if location_filter in captain_text:
                location = field.text.strip()
            if pincode_filter in captain_text:
                pincode = field.text.strip()            
            if pre_bid_address_filter in captain_text:
                pre_bid_address = field.text.strip()
            if pre_bid_date_filter in captain_text:
                pre_bid_date = field.text.strip()
            if word_desc_filter in captain_text:
                word_desc = field.text.strip()
    return title, word_desc, tander_value_in, location, pincode, pre_bid_date, pre_bid_address

def get_critical_dates(bot):
    published_date = ""
    published_date_filter = "Published Date"
    bid_sub_end_date = ""
    bid_sub_end_date_filter = "Bid Submission End Date"
    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")
        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()
            if published_date_filter == captain_text:
                published_date = field.text.strip()
            if bid_sub_end_date_filter == captain_text:
                bid_sub_end_date = field.text.strip()
    return published_date, bid_sub_end_date

def save_to_excel(data_list, idx):
    headers = (["Bid User", "Tender ID", "Name of Work", "Tender Category", "Department", "Quantity", "EMD", "Exemption", 
                "ECV", "State Name", "Location", "Apply Mode", "Website", "Document Link", "Closing Date", "Pincode", "Attachments"])
    file_path = path.join(OUTPUT_DIR , FILE_NAME.format(idx))
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter',date_format = "dd-mm-yyyy",datetime_format = "dd-mm-yyyy hh:mm:ss")
    writer.book.strings_to_urls = False
    df = pd.DataFrame(data_list, columns=headers)
    if 'Closing Date' in df.columns:
        df['Closing Date'] = pd.to_datetime(df['Closing Date'], errors='coerce')
    df.to_excel(writer, index=False)
    workbook = writer.book
    worksheet = writer.sheets[list(writer.sheets.keys())[0]]
    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})
    date_col_idx = headers.index("Closing Date")
    worksheet.set_column(date_col_idx, date_col_idx, 22, date_format)
    writer.close()
    return file_path

def get_all_detail(bot, tender_links):
    all_detail = []
    for idx, link in enumerate(tender_links):
        bot.execute_script("window.open(arguments[0]);", link)
        bot.switch_to.window(bot.window_handles[1])
        try:
            WebDriverWait(bot, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "page_content")))
            organisation_chain, _, tender_id, _, tender_category = get_basic_details(bot)
            _, _, exepm_allowed = get_fee_details(bot)
            emd_amout, _, emd_exepm_allowed = get_emd_details(bot)
            title, word_desc, tander_value_in, location, pincode, _, _ = get_work_details(bot)
            published_date, bid_sub_end_date = get_critical_dates(bot)
            all_detail.append([
                '', tender_id, word_desc, tender_category, organisation_chain, '',
                emd_amout, emd_exepm_allowed, tander_value_in, '', location, 'Online',
                '', '', bid_sub_end_date, pincode, ''
            ])
        except Exception as e:
            print(f"[ERROR] Skipping tender due to error: {e}")
        finally:
            bot.close()
            bot.switch_to.window(bot.window_handles[0])
    return all_detail

# Add 2Captcha solver

def solve_captcha_2captcha(api_key, image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'key': api_key, 'method': 'post'}
        response = requests.post('http://2captcha.com/in.php', files=files, data=data)
    if 'OK|' not in response.text:
        raise Exception('2Captcha upload failed: ' + response.text)
    captcha_id = response.text.split('|')[1]
    for _ in range(20):
        import time; time.sleep(5)
        res = requests.get(f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}')
        if res.text == 'CAPCHA_NOT_READY':
            continue
        if 'OK|' in res.text:
            return res.text.split('|')[1]
        else:
            raise Exception('2Captcha solve failed: ' + res.text)
    raise Exception('2Captcha timeout')

# Modify run_eproc_scraper_api to use 2Captcha if captcha is 'auto'
def run_eproc_scraper_api(base_url, tender_type, days_interval, start_page, captcha=None):
    global FILE_NAME
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    prefs = {"download_restrictions": 3}
    options.add_experimental_option("prefs", prefs)
    
    PATH = BASE_DIR + "\\scrapers\\edgedriver_win64\\msedgedriver.exe"
    
    # Check if driver file exists
    if not os.path.exists(PATH):
        raise Exception(f"Edge driver not found at: {PATH}")
    
    # Try different service configurations
    try:
        # Method 1: With service
        servicee = Service(executable_path=PATH)
        bot = webdriver.Edge(service=servicee, options=options)
    except Exception as e1:
        print(f"[SCRAPER] Method 1 failed: {e1}")
        try:
            # Method 2: Without service (let Selenium find driver)
            bot = webdriver.Edge(options=options)
        except Exception as e2:
            print(f"[SCRAPER] Method 2 failed: {e2}")
            try:
                # Method 3: With service and log_path
                servicee = Service(executable_path=PATH, log_path="edge_driver.log")
                bot = webdriver.Edge(service=servicee, options=options)
            except Exception as e3:
                print(f"[SCRAPER] Method 3 failed: {e3}")
                # Method 4: Try with Chrome driver as fallback
                try:
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    from selenium.webdriver.chrome.options import Options as ChromeOptions
                    chrome_options = ChromeOptions()
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    chrome_service = ChromeService(executable_path=PATH.replace('msedgedriver.exe', 'chromedriver.exe'))
                    bot = webdriver.Chrome(service=chrome_service, options=chrome_options)
                    print("[SCRAPER] Using Chrome as fallback")
                except Exception as e4:
                    print(f"[SCRAPER] All methods failed: {e4}")
                    raise Exception(f"Could not start browser. Please check Edge driver installation. Error: {str(e1)}")
    bot.minimize_window()
    URL = f"{base_url}?page=FrontEndAdvancedSearch&service=page"
    bot.get(URL)
    try:
        close_button = bot.find_element(By.CLASS_NAME, "alertbutclose")
        close_button.click()
        print("Popup closed.")
    except NoSuchElementException:
        print("Popup not present.")
    print("[BIDALERT INFO] WELCOME ** BID ALERT *** USER :: PAGE LOADED ")    
    sleep(2)
    try:
        WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
    except Exception as e:
        print(f"[ERROR] captchaImage not clickable: {e}")
        bot.save_screenshot("error_captchaImage.png")
        raise
    # Fill all fields except captcha
    date_criteria = WebDriverWait(bot, 10).until(
        EC.element_to_be_clickable((By.ID, "dateCriteria"))
    )
    bot.execute_script("arguments[0].scrollIntoView(true);", date_criteria)
    sleep(1)
    date_criteria.click()
    date_criteria.send_keys("Published Date")
    if (tender_type.lower() == 'o'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Open Tender")
        bot.find_element(By.ID, "TenderType").click()
        global FILE_NAME
        FILE_NAME = "open-tenders_output_page-{}.xlsx"
    elif (tender_type.lower() == 'l'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Limited Tender")
        bot.find_element(By.ID, "TenderType").click()
        FILE_NAME = "limited-tenders_output_page-{}.xlsx"
    bot.execute_script('document.getElementById("fromDate").removeAttribute("readonly")')
    bot.execute_script('document.getElementById("toDate").removeAttribute("readonly")')
    days_interval = int(days_interval)
    if (days_interval == 1):
        yesterday = today - timedelta(days = 1)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday_date)
    elif (days_interval > 1):        
        yesterday = today - timedelta(days = days_interval)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        yesterday2 = today - timedelta(days = 1)
        new_yesterday2_date = yesterday2.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday2_date)
    print("[BIDALERT INFO] Waiting for user to enter captcha and click Search in Edge window...")
    try:
        # Wait up to 5 minutes for the table to appear after user solves captcha and clicks Search
        WebDriverWait(bot, 300).until(EC.presence_of_element_located((By.ID, "table")))
        print("[BIDALERT INFO] User submitted captcha, continuing scraping...")
    except Exception as e:
        print("[ERROR] Timed out waiting for user to submit captcha: ", e)
        bot.save_screenshot("error_waiting_for_captcha.png")
        bot.quit()
        return
    # Continue scraping as normal
    # GETTING TOTAL PAGES COUNT
    try:
        list_footer = bot.find_element(By.CLASS_NAME, "list_footer")
        total_pages = list_footer.find_element(By.ID, "linkLast").get_attribute("href").split("=")[-1].strip()
        total_pages = int(total_pages)
    except Exception as e:
        print(f"[ERROR] Could not find total pages: {e}")
        bot.save_screenshot("error_totalPages.png")
        total_pages = 1
    print(f"[BIDALERT INFO] FOUND {total_pages} PAGES TO SCRAPE")
    start_page = int(start_page)
    
    # Try to maximize window safely, but don't fail if it doesn't work
    try:
        bot.maximize_window()
        print("[DEBUG] Window maximized successfully")
    except Exception as e:
        print(f"[WARNING] Could not maximize window: {e}")
        # Continue without maximizing
    for idx in range(start_page, total_pages + 1):
        all_detail = []
        print(f"[BIDALERT INFO] SCRAPING PAGE [{idx}/{total_pages}]")
        try:
            list_table = bot.find_element(By.ID, "table")
            a_tags = list_table.find_elements(By.TAG_NAME, "a")
        except Exception as e:
            print(f"[ERROR] Could not find table or links: {e}")
            bot.save_screenshot(f"error_table_{idx}.png")
            break
        tender_links = []
        for a_tag in a_tags:
            link = a_tag.get_attribute("href")
            if "DirectLink" in link:
                tender_links.append(link)
        for d in get_all_detail(bot, tender_links):
            all_detail.append(d)
        print(f"[BIDALERT INFO] SAVING LAST {len(all_detail)} TENDER DETAILS TO EXCEL FILE")
        excel_path = save_to_excel(all_detail, idx)
        print(f"[BIDALERT INFO] LAST {len(all_detail)} TENDER DETAILS ARE SAVED TO EXCEL FILE {excel_path}")
        print("-" * 300)
        # GOING TO NEXT PAGE
        next_page_url = f"{base_url}?component=%24TablePages.linkPage&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=AFrontEndAdvancedSearchResult%2Ctable&sp={idx+1}"
        bot.get(next_page_url)
        sleep(2)
    print("E-PROC SCRAPING COMPLETED")
    bot.quit()
    print("[BIDALERT INFO] Edge browser closed after scraping.")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    response = jsonify({"status": "error", "message": str(e)})
    response.status_code = 500
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/')
def index():
    return "E-Procurement WebSocket server is running!"

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/api/get-captcha', methods=['POST'])
def get_captcha():
    """Get the current captcha image from the page"""
    try:
        data = request.get_json() or {}
        # url = data.get('url', 'https://mahatenders.gov.in/nicgep/app?page=FrontEndAdvancedSearch&service=page')
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        PATH = BASE_DIR + "\\scrapers\\edgedriver_win64\\msedgedriver.exe"
        servicee = Service(executable_path=PATH)
        bot = webdriver.Edge(service=servicee, options=options)
        
        try:
            bot.get(url)
            sleep(3)
            
            # Wait for captcha to be available
            WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
            
            # Get the captcha image
            captcha_element = bot.find_element(By.ID, "captchaImage")
            captcha_src = captcha_element.get_attribute("src")
            
            bot.quit()
            
            if captcha_src:
                return {"status": "success", "captcha_image": captcha_src}, 200
            else:
                return {"status": "error", "message": "Captcha image not found"}, 404
                
        except Exception as e:
            bot.quit()
            return {"status": "error", "message": str(e)}, 500
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/api/open-edge', methods=['POST'])
def open_edge():
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return {"status": "error", "message": "Missing URL"}, 400
    
    # Add the advanced search page parameter if not present
    if "FrontEndAdvancedSearch" not in url:
        url = f"{url}?page=FrontEndAdvancedSearch&service=page"
    
    try:
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        prefs = {"download_restrictions": 3}
        options.add_experimental_option("prefs", prefs)
        
        PATH = BASE_DIR + "\\scrapers\\edgedriver_win64\\msedgedriver.exe"
        
        # Check if driver file exists
        if not os.path.exists(PATH):
            return {"status": "error", "message": f"Edge driver not found at: {PATH}"}, 500
        
        print(f"[OPEN EDGE] Attempting to open Edge at {url} with driver {PATH}")
        
        # Try different service configurations
        bot = None
        last_error = None
        
        # Method 1: With service and verbose logging
        try:
            print("[OPEN EDGE] Trying Method 1: With service and verbose logging")
            servicee = Service(executable_path=PATH, log_path="edge_driver.log", log_output=subprocess.STDOUT)
            bot = webdriver.Edge(service=servicee, options=options)
            print("[OPEN EDGE] Method 1 succeeded!")
        except Exception as e1:
            last_error = e1
            print(f"[OPEN EDGE] Method 1 failed: {e1}")
            
            # Method 2: Without service (let Selenium find driver)
            try:
                print("[OPEN EDGE] Trying Method 2: Without service")
                bot = webdriver.Edge(options=options)
                print("[OPEN EDGE] Method 2 succeeded!")
            except Exception as e2:
                last_error = e2
                print(f"[OPEN EDGE] Method 2 failed: {e2}")
                
                # Method 3: With minimal options
                try:
                    print("[OPEN EDGE] Trying Method 3: With minimal options")
                    minimal_options = Options()
                    minimal_options.add_argument('--disable-gpu')
                    servicee = Service(executable_path=PATH)
                    bot = webdriver.Edge(service=servicee, options=minimal_options)
                    print("[OPEN EDGE] Method 3 succeeded!")
                except Exception as e3:
                    last_error = e3
                    print(f"[OPEN EDGE] Method 3 failed: {e3}")
                    
                    # Method 4: Try with Chrome driver as fallback
                    try:
                        print("[OPEN EDGE] Trying Method 4: Chrome as fallback")
                        from selenium.webdriver.chrome.service import Service as ChromeService
                        from selenium.webdriver.chrome.options import Options as ChromeOptions
                        chrome_options = ChromeOptions()
                        chrome_options.add_argument('--disable-gpu')
                        chrome_options.add_argument('--no-sandbox')
                        chrome_options.add_argument('--disable-dev-shm-usage')
                        chrome_service = ChromeService(executable_path=PATH.replace('msedgedriver.exe', 'chromedriver.exe'))
                        bot = webdriver.Chrome(service=chrome_service, options=chrome_options)
                        print("[OPEN EDGE] Method 4 succeeded - Using Chrome as fallback")
                    except Exception as e4:
                        last_error = e4
                        print(f"[OPEN EDGE] Method 4 failed: {e4}")
        
        if bot is None:
            error_msg = f"Could not start browser. All methods failed. Last error: {str(last_error)}"
            print(f"[OPEN EDGE ERROR] {error_msg}")
            return {"status": "error", "message": error_msg}, 500
        
        try:
            bot.minimize_window()
            bot.get(url)
            session_id = str(uuid.uuid4())
            pending_eproc_sessions[session_id] = {'bot': bot}
            print(f"[OPEN EDGE] Edge opened successfully, session_id: {session_id}")
            return {"status": "success", "session_id": session_id}, 200
        except Exception as e:
            bot.quit()
            raise e
            
    except Exception as e:
        print(f"[OPEN EDGE ERROR] {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route('/api/start-eproc-session', methods=['POST'])
def start_eproc_session():
    data = request.get_json() or {}
    required_args = ['session_id', 'tender_type', 'days_interval', 'start_page']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        return {"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}, 400
    session_id = data['session_id']
    session = pending_eproc_sessions.pop(session_id, None)
    if not session:
        return {"status": "error", "message": "Session not found or expired."}, 404
    bot = session['bot']
    tender_type = data['tender_type']
    days_interval = data['days_interval']
    start_page = data['start_page']
    try:
        # Fill all fields except captcha (assume user already entered captcha in Edge)
        date_criteria = WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable((By.ID, "dateCriteria"))
        )
        bot.execute_script("arguments[0].scrollIntoView(true);", date_criteria)
        sleep(1)
        date_criteria.click()
        date_criteria.send_keys("Published Date")
        if (tender_type.lower() == 'o'):
            bot.find_element(By.ID, "TenderType").click()
            bot.find_element(By.ID, "TenderType").send_keys("Open Tender")
            bot.find_element(By.ID, "TenderType").click()
            global FILE_NAME
            FILE_NAME = "open-tenders_output_page-{}.xlsx"
        elif (tender_type.lower() == 'l'):
            bot.find_element(By.ID, "TenderType").click()
            bot.find_element(By.ID, "TenderType").send_keys("Limited Tender")
            bot.find_element(By.ID, "TenderType").click()
            FILE_NAME = "limited-tenders_output_page-{}.xlsx"
        bot.execute_script('document.getElementById("fromDate").removeAttribute("readonly")')
        bot.execute_script('document.getElementById("toDate").removeAttribute("readonly")')
        days_interval = int(days_interval)
        if (days_interval == 1):
            yesterday = today - timedelta(days = 1)
            new_yesterday_date = yesterday.strftime("%d/%m/%Y")
            bot.find_element(By.ID, "fromDate").clear()
            bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
            bot.find_element(By.ID, "toDate").clear()
            bot.find_element(By.ID, "toDate").send_keys(new_yesterday_date)
        elif (days_interval > 1):        
            yesterday = today - timedelta(days = days_interval)
            new_yesterday_date = yesterday.strftime("%d/%m/%Y")
            yesterday2 = today - timedelta(days = 1)
            new_yesterday2_date = yesterday2.strftime("%d/%m/%Y")
            bot.find_element(By.ID, "fromDate").clear()
            bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
            bot.find_element(By.ID, "toDate").clear()
            bot.find_element(By.ID, "toDate").send_keys(new_yesterday2_date)
        print("[BIDALERT INFO] Continuing scraping after user entered captcha in Edge window...")
        # Continue scraping as normal
        # GETTING TOTAL PAGES COUNT
        try:
            list_footer = bot.find_element(By.CLASS_NAME, "list_footer")
            total_pages = list_footer.find_element(By.ID, "linkLast").get_attribute("href").split("=")[-1].strip()
            total_pages = int(total_pages)
        except Exception as e:
            print(f"[ERROR] Could not find total pages: {e}")
            bot.save_screenshot("error_totalPages.png")
            total_pages = 1
        print(f"[BIDALERT INFO] FOUND {total_pages} PAGES TO SCRAPE")
        start_page = int(start_page)
        
        # Try to maximize window safely, but don't fail if it doesn't work
        try:
            bot.maximize_window()
            print("[DEBUG] Window maximized successfully")
        except Exception as e:
            print(f"[WARNING] Could not maximize window: {e}")
            # Continue without maximizing
        for idx in range(start_page, total_pages + 1):
            all_detail = []
            print(f"[BIDALERT INFO] SCRAPING PAGE [{idx}/{total_pages}]")
            try:
                list_table = bot.find_element(By.ID, "table")
                a_tags = list_table.find_elements(By.TAG_NAME, "a")
            except Exception as e:
                print(f"[ERROR] Could not find table or links: {e}")
                bot.save_screenshot(f"error_table_{idx}.png")
                break
            tender_links = []
            for a_tag in a_tags:
                link = a_tag.get_attribute("href")
                if "DirectLink" in link:
                    tender_links.append(link)
            for d in get_all_detail(bot, tender_links):
                all_detail.append(d)
            print(f"[BIDALERT INFO] SAVING LAST {len(all_detail)} TENDER DETAILS TO EXCEL FILE")
            excel_path = save_to_excel(all_detail, idx)
            print(f"[BIDALERT INFO] LAST {len(all_detail)} TENDER DETAILS ARE SAVED TO EXCEL FILE {excel_path}")
            print("-" * 300)
            # GOING TO NEXT PAGE
            next_page_url = f"{data['base_url']}?component=%24TablePages.linkPage&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=AFrontEndAdvancedSearchResult%2Ctable&sp={idx+1}"
            bot.get(next_page_url)
            sleep(2)
        print("E-PROC SCRAPING COMPLETED")
        bot.quit()
        print("[BIDALERT INFO] Edge browser closed after scraping.")
        return {"status": "success", "message": "Scraping started and completed."}, 200
    except Exception as e:
        print(f"[ERROR] Exception in start_eproc_session: {e}")
        bot.save_screenshot("error_start_eproc_session.png")
        bot.quit()
        return {"status": "error", "message": str(e)}, 500

@app.route('/api/submit-eproc-captcha', methods=['POST'])
def submit_eproc_captcha():
    data = request.get_json() or {}
    captcha = data.get('captcha')
    session_id = data.get('session_id')
    tender_type = data.get('tender_type')
    days_interval = data.get('days_interval')
    start_page = data.get('start_page')
    if not captcha or not session_id or not tender_type or not days_interval or not start_page:
        return {"status": "error", "message": "Missing required fields (captcha, session_id, tender_type, days_interval, start_page)."}, 400
    session = pending_eproc_sessions.pop(session_id, None)
    if not session:
        return {"status": "error", "message": "Session not found or expired."}, 404
    bot = session['bot']
    base_url = session['base_url'] # This will be None, but the new logic doesn't use it for the bot
    try:
        # 1. Fill Date Criteria
        bot.find_element(By.ID, "dateCriteria").click()
        bot.find_element(By.ID, "dateCriteria").send_keys("Published Date")
        bot.find_element(By.ID, "dateCriteria").click()
        # 2. Fill Tender Type
        if (tender_type.lower() == 'o'):
            bot.find_element(By.ID, "TenderType").click()
            bot.find_element(By.ID, "TenderType").send_keys("Open Tender")
            bot.find_element(By.ID, "TenderType").click()
            global FILE_NAME
            FILE_NAME = "open-tenders_output_page-{}.xlsx"
        elif (tender_type.lower() == 'l'):
            bot.find_element(By.ID, "TenderType").click()
            bot.find_element(By.ID, "TenderType").send_keys("Limited Tender")
            bot.find_element(By.ID, "TenderType").click()
            FILE_NAME = "limited-tenders_output_page-{}.xlsx"
        # 3. Fill Days Interval (fromDate, toDate)
        bot.execute_script('document.getElementById("fromDate").removeAttribute("readonly")')
        bot.execute_script('document.getElementById("toDate").removeAttribute("readonly")')
        days_interval = int(days_interval)
        if (days_interval == 1):
            yesterday = today - timedelta(days = 1)
            new_yesterday_date = yesterday.strftime("%d/%m/%Y")
            bot.find_element(By.ID, "fromDate").clear()
            bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)
            bot.find_element(By.ID, "toDate").clear()
            bot.find_element(By.ID, "toDate").send_keys(new_yesterday_date)
        elif (days_interval > 1):
            yesterday = today - timedelta(days = days_interval)
            new_yesterday_date = yesterday.strftime("%d/%m/%Y")
            yesterday2 = today - timedelta(days = 1)
            new_yesterday2_date = yesterday2.strftime("%d/%m/%Y")
            bot.find_element(By.ID, "fromDate").clear()
            bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)
            bot.find_element(By.ID, "toDate").clear()
            bot.find_element(By.ID, "toDate").send_keys(new_yesterday2_date)
        # 4. Enter captcha
        bot.find_element(By.ID, "captchaText").clear()
        bot.find_element(By.ID, "captchaText").send_keys(captcha)
        sleep(2)
        # 5. Click Search
        bot.find_element(By.XPATH, "//input[@title='Search']").click()
        sleep(3)
        # Continue with scraping as before
        try:
            list_footer = bot.find_element(By.CLASS_NAME, "list_footer")
            total_pages = list_footer.find_element(By.ID, "linkLast").get_attribute("href").split("=")[-1].strip()
            total_pages = int(total_pages)
        except Exception as e:
            print(f"[ERROR] Could not find total pages: {e}")
            bot.save_screenshot("error_totalPages.png")
            total_pages = 1
        print(f"[BIDALERT INFO] FOUND {total_pages} PAGES TO SCRAPE")
        start_page = int(start_page)
        
        # Try to maximize window safely, but don't fail if it doesn't work
        try:
            bot.maximize_window()
            print("[DEBUG] Window maximized successfully")
        except Exception as e:
            print(f"[WARNING] Could not maximize window: {e}")
            # Continue without maximizing
        for idx in range(start_page, total_pages + 1):
            all_detail = []
            print(f"[BIDALERT INFO] SCRAPING PAGE [{idx}/{total_pages}]")
            try:
                list_table = bot.find_element(By.ID, "table")
                a_tags = list_table.find_elements(By.TAG_NAME, "a")
            except Exception as e:
                print(f"[ERROR] Could not find table or links: {e}")
                bot.save_screenshot(f"error_table_{idx}.png")
                break
            tender_links = []
            for a_tag in a_tags:
                link = a_tag.get_attribute("href")
                if "DirectLink" in link:
                    tender_links.append(link)
            for d in get_all_detail(bot, tender_links):
                all_detail.append(d)
            print(f"[BIDALERT INFO] SAVING LAST {len(all_detail)} TENDER DETAILS TO EXCEL FILE")
            excel_path = save_to_excel(all_detail, idx)
            print(f"[BIDALERT INFO] LAST {len(all_detail)} TENDER DETAILS ARE SAVED TO EXCEL FILE {excel_path}")
            print("-" * 300)
            next_page_url = f"{base_url}?component=%24TablePages.linkPage&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=AFrontEndAdvancedSearchResult%2Ctable&sp={idx+1}"
            bot.get(next_page_url)
            sleep(2)
        print("E-PROC SCRAPING COMPLETED")
        bot.quit()
        print("[BIDALERT INFO] Edge browser closed after scraping.")
        return {"status": "success", "message": "Scraping completed."}, 200
    except Exception as e:
        print(f"[ERROR] Exception in submit_eproc_captcha: {e}")
        bot.save_screenshot("error_submit_captcha.png")
        bot.quit()
        return {"status": "error", "message": str(e)}, 500

@socketio.on('start_eproc_scraping')
def handle_start_eproc_scraping(data):
    print("Received start_eproc_scraping:", data)
    required_args = ['base_url', 'tender_type', 'days_interval', 'start_page', 'run_id']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        error_msg = f"[ERROR] Missing required fields: {', '.join(missing)}\n"
        print(error_msg)
        emit('eproc_scraping_output', {'output': error_msg}, broadcast=False)
        return
    try:
        # Call the scraper function directly, passing the captcha
        run_eproc_scraper_api(
            base_url=data['base_url'],
            tender_type=data['tender_type'],
            days_interval=data['days_interval'],
            start_page=data['start_page'],
            captcha=data.get('captcha')
        )
        emit('eproc_scraping_output', {'output': 'E-PROC SCRAPING COMPLETED\n'}, broadcast=False)
    except Exception as e:
        print("Error running scraper:", e)
        emit('eproc_scraping_output', {'output': f'Error: {e}\n'}, broadcast=False)

@app.route('/api/start-scraping', methods=['POST'])
def api_start_scraping():
    data = request.get_json() or {}
    required_args = ['base_url', 'tender_type', 'days_interval', 'start_page', 'captcha']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        return {"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}, 400
    try:
        run_eproc_scraper_api(
            base_url=data['base_url'],
            tender_type=data['tender_type'],
            days_interval=data['days_interval'],
            start_page=data['start_page'],
            captcha=data.get('captcha')
        )
        return {"status": "success", "message": "Scraping started and completed."}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    socketio.run(app, port=5020, debug=True) 
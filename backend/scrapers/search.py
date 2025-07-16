#import xlsxwriter
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import argparse


# Here we are importing the attachment downloader
# moduel whch uses cookies to download
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from backend.scrapers.downloader import *

from .cap_solver import solve_captcha
from time import sleep
import pandas as pd
from os import path, makedirs
from datetime import date
from datetime import timedelta
# driver = webdriver.Chrome()
today = date.today()
#yesterday = today - timedelta(days = 1)
#new_yesterday_date = yesterday.strftime("%d/%m/%Y")
# You cnan try to chnage thi URL to other similar sites
#BASE_URL = input("PASTE YOUR URL HERE:")
#URL = f"{BASE_URL}?page=FrontEndAdvancedSearch&service=page"
#NEXT_PAGE_URL = f"{BASE_URL}?component=%24TablePages.linkPage&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=AFrontEndAdvancedSearchResult%2Ctable&sp="
TIMEOUT = 6

BASE_DIR = path.dirname(path.abspath(__file__))
OUTPUT_DIR = path.join(BASE_DIR, "OUTPUT")
DOWNLOAD_DIR = path.join(BASE_DIR, "OUTPUT", "Downloaded_Documents")

ATTACHMENT_PATHS = []

if not path.exists(DOWNLOAD_DIR):
    makedirs(DOWNLOAD_DIR)

if not path.exists(OUTPUT_DIR):
    makedirs(OUTPUT_DIR)

def solve_captcha_attachment(bot:webdriver.Chrome):
    bot.switch_to.window(bot.window_handles[1])

    WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.ID, "captchaImage")))

    image_data = bot.find_element(By.ID, "captchaImage").get_attribute("src")
    # solved_captcha = solve_captcha(image_data)       
    solvcap=input("enter captcha:").strip()
    bot.find_element(By.ID, "captchaText").send_keys(solvcap)


    sleep(2)

    bot.find_element(By.XPATH, "//input[@title='Submit']").click()

    print("[BIDALERT INFO] SUBMIT BUTTON CLICKED")

    # message_box appears with "Invalid Captcha! Please Enter Correct Captcha." text if captcha is wrong
    try:
        WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "textbold1")))
        print("[BIDALERT INFO] CAPTCHA WAS VALID")
        return True
    except:
        print("[ERROR] LAST ENTERED CAPTCHA WAS INVALID WILL TRY AGAIN")
        return False


def solve_captcha_main(bot:webdriver.Chrome):
    WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))

    image_data = bot.find_element(By.ID, "captchaImage").get_attribute("src")
    solvcap=input("enter captcha:").strip()       
    bot.find_element(By.ID, "captchaText").send_keys(solvcap)
    
    sleep(2)
    bot.find_element(By.XPATH, "//input[@title='Search']").click()

    print("[BIDALERT INFO] SUBMIT BUTTON CLICKED")

    try:
        WebDriverWait(bot, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "list_footer")))
        print("[BIDALERT INFO] CAPTCHA WAS VALID")
        return True
    except:
        print("[ERROR] LAST ENTERED CAPTCHA WAS INVALID WILL TRY AGAIN")
        return False

def select_options(bot:webdriver.Chrome):
    
    WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
    
    bot.find_element(By.ID, "dateCriteria").click()
    bot.find_element(By.ID, "dateCriteria").send_keys("Published Date")
    bot.find_element(By.ID, "dateCriteria").click()    
    
    global FILE_NAME

    tendr_type = input("[BIDALERT INFO] PLEASE ENTER *** TENDER TYPE *** O/L ?? ")
    if (tendr_type == 'o') or (tendr_type == 'O'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Open Tender")
        bot.find_element(By.ID, "TenderType").click()
        FILE_NAME = "open-tenders_output_page-{}.xlsx"
        
    if (tendr_type == 'l') or (tendr_type == 'L'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Limited Tender")
        bot.find_element(By.ID, "TenderType").click()
        FILE_NAME = "limited-tenders_output_page-{}.xlsx"
    
    bot.execute_script('document.getElementById("fromDate").removeAttribute("readonly")')
    bot.execute_script('document.getElementById("toDate").removeAttribute("readonly")')
    #bidfrm_date = input("PLEASE ENTER *** START DATE *** ")
    #bidend_date = input("PLEASE ENTER *** END DATE *** ")
    days_interval = int((input("[BIDALERT INFO] ENTER  *** HOW MANY DAYS BACK *** DATA YOU WANT TO SCRAP? ")))
    if (days_interval == 1):
        yesterday = today - timedelta(days = 1)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday_date)

    if (days_interval > 1):        
        yesterday = today - timedelta(days = days_interval)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        yesterday2 = today - timedelta(days = 1)
        new_yesterday2_date = yesterday2.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)    
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday2_date)

def get_basic_details(bot:webdriver.Chrome):

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


def get_fee_details(bot:webdriver.Chrome):

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

def get_emd_details(bot:webdriver.Chrome):
    
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

def get_work_details(bot:webdriver.Chrome):
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

def get_critical_dates(bot:webdriver.Chrome):
    
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

def get_tander_address(bot:webdriver.Chrome):

    address = ""
    address_filter = "Address"

    page_content = bot.find_element(By.CLASS_NAME, "page_content")
    tablebgs = page_content.find_elements(By.CLASS_NAME, "tablebg")
    for tablebg in tablebgs:
        td_field = tablebg.find_elements(By.CLASS_NAME, "td_field")
        td_caption = tablebg.find_elements(By.CLASS_NAME, "td_caption")

        for field, captain in zip(td_field, td_caption):
            captain_text = captain.text.strip()

            if address_filter == captain_text:
                address = field.text.strip()

    return address

def get_attachment(bot:webdriver.Chrome, tender_id, is_cap_solved=False):
    global ATTACHMENT_PATHS
    ATTACHMENT_PATHS = []
    try:
    
        doc_links = []
        print("[INFO] GETTING DOC LINKS")

        a_tags = bot.find_elements(By.XPATH, "//a[starts-with(@id,'DirectLink_')]")
        a_tags += bot.find_elements(By.XPATH, "//a[starts-with(@id,'docDownoad')]")

        for a_tag in a_tags:
            try:
                link =  a_tag.get_attribute("href").strip()
                title = a_tag.text

                if len(link) > 0:
                    if ".pdf" in title or "Downlaod" in title or "as zip" in title:
                        
                        if not link.startswith(BASE_URL):
                            link = BASE_URL + link

                        # Here we will get the captcha 1st time when we will try to download
                        # the attachment We will click the link if captcha is not solved 
                        # othewise we will use requests to download the attachment
                        if not is_cap_solved:
                            # if 'nt' in  os.name:
                                # a_tag.send_keys(Keys.CONTROL + Keys.ENTER)
                            # else:
                                # a_tag.send_keys(Keys.COMMAND + Keys.ENTER)
                            
                            # print("[INFO] CLICKED DOC DOWNLOAD LINK:- ", title)

                            while True:
                                try:
                                    # solve_captcha_attachment will return True if the capctha was solved
                                    # If it was solved we will call get_attachment with True otherwise False
                                    did_handle_cap = solve_captcha_attachment(bot)
                                    if did_handle_cap:
                                        return get_attachment(bot, tender_id, True)
                                except:
                                    bot.switch_to.window(bot.window_handles[0])
                                    break

                    # Lets download attachment using requests module 
                    all_cookies = bot.get_cookies()
                    cookie = all_cookies[0]['value']
                    # We are download the attachment it will return valid downloaded path
                    # of the attachment file
                    file_path = download_file(tender_id, DOWNLOAD_DIR, link, cookie)
                    if file_path is not None:
                        ATTACHMENT_PATHS.append(file_path)
            
            except:
                pass

        sleep(2)
        if len(bot.window_handles) > 1:
            print("[INFO] CLOSED 2nd WINDOW!")
            bot.close()
            sleep(1)
            bot.switch_to.window(bot.window_handles[0])


        doc_links = list(set(doc_links))

        return "\n".join(doc_links)
    except:
        return []

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
    
    # Create a date format
    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})

    # Find the column index of 'Closing Date'
    date_col_idx = headers.index("Closing Date")
    worksheet.set_column(date_col_idx, date_col_idx, 22, date_format)

    writer.close()

    return file_path

def get_all_detail(bot: webdriver.Chrome, tender_links):
    all_detail = []

    for idx, link in enumerate(tender_links):
        print(f"[BIDALERT INFO] GETTING TENDER [{idx+1}/{len(tender_links)}]")

        # Open link in background tab
        bot.execute_script("window.open(arguments[0]);", link)
        bot.switch_to.window(bot.window_handles[1])

        try:
            WebDriverWait(bot, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "page_content")))
            
            organisation_chain, _, tender_id, _, tender_category = get_basic_details(bot)
            _, _, exepm_allowed = get_fee_details(bot)
            emd_amout, _, emd_exepm_allowed = get_emd_details(bot)
            title, word_desc, tander_value_in, location, pincode, _, _ = get_work_details(bot)
            published_date, bid_sub_end_date = get_critical_dates(bot)

            # Skip attachment download for speed or enable if needed
            attachment_links = ""  # Skip this for now
            # attachment_links = get_attachment(bot, tender_id=tender_id)
            # attachment_links = ",".join(list(set(ATTACHMENT_PATHS)))

            all_detail.append([
                '', tender_id, word_desc, tender_category, organisation_chain, '',
                emd_amout, emd_exepm_allowed, tander_value_in, '', location, 'Online',
                BASE_URL, '', bid_sub_end_date, pincode, attachment_links
            ])
        
        except Exception as e:
            print(f"[ERROR] Skipping tender due to error: {e}")
        
        finally:
            # Close current tab and switch back
            bot.close()
            bot.switch_to.window(bot.window_handles[0])

    return all_detail

    
def start():
    options = Options()
    prefs = {"download_restrictions": 3}
    options.add_experimental_option(
        "prefs", prefs
    )
    PATH=BASE_DIR+"\\edgedriver_win64\\msedgedriver.exe"
    chromedriver_path = PATH
    servicee = Service(executable_path=chromedriver_path)
    #bot = webdriver.Chrome(service=Service(CM().install()), options=options)
    bot = webdriver.Edge(service=servicee,options=options)
    bot.minimize_window()
    bot.get(URL)
    try:
         close_button = bot.find_element(By.CLASS_NAME, "alertbutclose")
         close_button.click()
         print("Popup closed.")
    except NoSuchElementException:
         print("Popup not present.")

    print("[BIDALERT INFO] WELCOME ** BID ALERT *** USER :: PAGE LOADED ")    
    
    sleep(2)
    select_options(bot)

    while True:
        did_handle_cap = solve_captcha_main(bot)
        if did_handle_cap:
            break
    
    # GETTING TOTAL PAGES COUNT
    try:
        list_footer = bot.find_element(By.CLASS_NAME, "list_footer")
        total_pages = list_footer.find_element(By.ID, "linkLast").get_attribute("href").split("=")[-1].strip()
    except:
        total_pages = 1
    print(f"[BIDALERT INFO] FOUND {total_pages} PAGES TO SCRAPE")

    start_page = int((input("[BIDALERT INFO] ENTER  *** STARTING PAGE NUMBER *** ")))
    bot.maximize_window()

    for idx in range(start_page,int(total_pages)+1):
        # ALL THE TANDERS APPEARS ON THIS TABLE    
            
        all_detail = []
        print(f"[BIDALERT INFO] SCRAPING PAGE [{idx}/{total_pages}]")
        
        list_table = bot.find_element(By.ID, "table")
        a_tags = list_table.find_elements(By.TAG_NAME, "a")

        tender_links = []

        for a_tag in a_tags:
            link = a_tag.get_attribute("href")
            if "DirectLink" in link:
                tender_links.append(link)

        for d in get_all_detail(bot, tender_links):
            all_detail.append(d)

        # if len(all_detail) % 20 == 0:
        print(f"[BIDALERT INFO] SAVING LAST {len(all_detail)} TENDER DETAILS TO EXCEL FILE")
        excel_path = save_to_excel(all_detail, idx)
        print(f"[BIDALERT INFO] LAST {len(all_detail)} TENDER DETAILS ARE SAVED TO EXCEL FILE {excel_path}")

        print("-" * 300)
        
        #############################################
        # GOING TO NEXT PAGE
        #############################################
          
        next_page_url = NEXT_PAGE_URL + str(idx+1)
        
        bot.get(next_page_url)
       

    input("[BIDALERT INFO] DEAR BIDALERT EMPLOYEE SCAPING SUCCESS PRESS *** ENTER KEY *** TO CLOSE")

def run_eproc_scraper(
    base_url,
    tender_type,
    days_interval,
    start_page
):
    global BASE_URL, URL, NEXT_PAGE_URL, FILE_NAME
    BASE_URL = base_url
    URL = f"{BASE_URL}?page=FrontEndAdvancedSearch&service=page"
    NEXT_PAGE_URL = f"{BASE_URL}?component=%24TablePages.linkPage&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=AFrontEndAdvancedSearchResult%2Ctable&sp="

    options = Options()
    prefs = {"download_restrictions": 3}
    options.add_experimental_option(
        "prefs", prefs
    )
    PATH = BASE_DIR + "\\edgedriver_win64\\msedgedriver.exe"
    chromedriver_path = PATH
    servicee = Service(executable_path=chromedriver_path)
    bot = webdriver.Edge(service=servicee, options=options)
    bot.minimize_window()
    bot.get(URL)
    try:
        close_button = bot.find_element(By.CLASS_NAME, "alertbutclose")
        close_button.click()
        print("Popup closed.")
    except NoSuchElementException:
        print("Popup not present.")

    print("[BIDALERT INFO] WELCOME ** BID ALERT *** USER :: PAGE LOADED ")    
    sleep(2)

    # --- select_options logic, but with arguments ---
    WebDriverWait(bot, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "captchaImage")))
    bot.find_element(By.ID, "dateCriteria").click()
    bot.find_element(By.ID, "dateCriteria").send_keys("Published Date")
    bot.find_element(By.ID, "dateCriteria").click()

    if (tender_type.lower() == 'o'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Open Tender")
        bot.find_element(By.ID, "TenderType").click()
        FILE_NAME = "open-tenders_output_page-{}.xlsx"
    elif (tender_type.lower() == 'l'):
        bot.find_element(By.ID, "TenderType").click()
        bot.find_element(By.ID, "TenderType").send_keys("Limited Tender")
        bot.find_element(By.ID, "TenderType").click()
        FILE_NAME = "limited-tenders_output_page-{}.xlsx"
    else:
        FILE_NAME = "tenders_output_page-{}.xlsx"

    bot.execute_script('document.getElementById("fromDate").removeAttribute("readonly")')
    bot.execute_script('document.getElementById("toDate").removeAttribute("readonly")')
    if (days_interval == 1):
        yesterday = today - timedelta(days=1)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday_date)
    elif (days_interval > 1):
        yesterday = today - timedelta(days=days_interval)
        new_yesterday_date = yesterday.strftime("%d/%m/%Y")
        yesterday2 = today - timedelta(days=1)
        new_yesterday2_date = yesterday2.strftime("%d/%m/%Y")
        bot.find_element(By.ID, "fromDate").clear()
        bot.find_element(By.ID, "fromDate").send_keys(new_yesterday_date)
        bot.find_element(By.ID, "toDate").clear()
        bot.find_element(By.ID, "toDate").send_keys(new_yesterday2_date)

    # --- captcha handling ---
    while True:
        did_handle_cap = solve_captcha_main(bot)
        if did_handle_cap:
            break

    # GETTING TOTAL PAGES COUNT
    try:
        list_footer = bot.find_element(By.CLASS_NAME, "list_footer")
        total_pages = list_footer.find_element(By.ID, "linkLast").get_attribute("href").split("=")[-1].strip()
        total_pages = int(total_pages)
    except:
        total_pages = 1
    print(f"[BIDALERT INFO] FOUND {total_pages} PAGES TO SCRAPE")

    bot.maximize_window()
    excel_files = []
    for idx in range(start_page, total_pages + 1):
        all_detail = []
        print(f"[BIDALERT INFO] SCRAPING PAGE [{idx}/{total_pages}]")
        list_table = bot.find_element(By.ID, "table")
        a_tags = list_table.find_elements(By.TAG_NAME, "a")
        tender_links = []
        for a_tag in a_tags:
            link = a_tag.get_attribute("href")
            if link and "DirectLink" in link:
                tender_links.append(link)
        for d in get_all_detail(bot, tender_links):
            all_detail.append(d)
        print(f"[BIDALERT INFO] SAVING LAST {len(all_detail)} TENDER DETAILS TO EXCEL FILE")
        excel_path = save_to_excel(all_detail, idx)
        excel_files.append(excel_path)
        print(f"[BIDALERT INFO] LAST {len(all_detail)} TENDER DETAILS ARE SAVED TO EXCEL FILE {excel_path}")
        print("-" * 300)
        next_page_url = NEXT_PAGE_URL + str(idx + 1)
        bot.get(next_page_url)
    bot.quit()
    # Return the last excel file path (or all if needed)
    return excel_files[-1] if excel_files else None

# Comment out the __main__ block to avoid running on import
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="E-Procurement Scraper")
#     parser.add_argument('--base_url', required=True, help='Base URL for scraping')
#     parser.add_argument('--tender_type', required=True, help='Tender type (O/L)')
#     parser.add_argument('--days_interval', type=int, required=True, help='How many days back to scrape')
#     parser.add_argument('--start_page', type=int, required=True, help='Starting page number')
#     args = parser.parse_args()
#     run_eproc_scraper(
#         base_url=args.base_url,
#         tender_type=args.tender_type,
#         days_interval=args.days_interval,
#         start_page=args.start_page
#     )

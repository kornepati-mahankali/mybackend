from selenium import webdriver
from os import *
from selenium.webdriver.chrome.service import Service
import math
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import re
from selenium.common.exceptions import TimeoutException
from datetime import datetime
# Setup paths and directories
import argparse
parser = argparse.ArgumentParser(description="Scrapes data from the GeM website and saves as Excel files.")
parser.add_argument("--starting_page", type=int, required=True, help="Page number to start from.")
parser.add_argument("--run_id", type=str, required=True, help="Unique run identifier.")
parser.add_argument("--user_name", type=str, required=True, help="Username to fill the Excel.")
args = parser.parse_args()
BASE_DIR = path.dirname(path.abspath(__file__))
save_directory = path.join(BASE_DIR, "outputs", "ap", args.run_id)
username=args.user_name


if not path.exists(save_directory):
    makedirs(save_directory)

chromedriver_path = BASE_DIR+r"\edgedriver_win64\\msedgedriver.exe"
servicee = Service(executable_path=chromedriver_path)
driver = webdriver.Edge(service=servicee)

driver.get('https://tender.telangana.gov.in/login.html')
driver.minimize_window()
print("Loading page, please wait...")
sleep(14)
print("Page loaded")

# Navigate to the desired section
k=driver.find_element(By.CLASS_NAME,"tab-content")
k.find_element(By.XPATH, "//a[@class='viewCurrentall']").click()

driver.implicitly_wait(5)
page_length = driver.find_element(By.XPATH, "//span[@class='gridSmall']")
drops = page_length.find_elements(By.TAG_NAME, "option")
# drops[0].click() # 10
# drops[1].click() # 20
# drops[2].click() # 40
# drops[3].click() # 50
drops[4].click()  # Select 100 items per page

# Get the total number of pages
p = driver.find_element(By.ID, "pagetable13_info").text
numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?=\srecords)', p)
numbers = [int(number.replace(',', '')) for number in numbers]
max_number = max(numbers)
total_pages = math.ceil(max_number / 100)
print(f"TOTAL PAGES FOUND: {total_pages}")

starting_page = args.starting_page
current_page = int(driver.find_element(By.XPATH, "//a[@class='paginate_button current']").text)

if current_page != starting_page and starting_page > 1:
    print(f"Navigating to page {starting_page}...")
    for _ in range(starting_page - 1):
        try:
            driver.find_element(By.LINK_TEXT,f"{starting_page}")
        except:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Next"))).click()
            sleep(1)

print(f"You are now on page {starting_page}")

# Function to extract table data from the second layer
def second_layer(link):
    link.click()
    driver.switch_to.window(driver.window_handles[-1])
    try:
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            for index, table in enumerate(tables):
                if "Officer Inviting Bids" in table.text:
                    print("table found at index:",index)
                    # for row in table.find_elements(By.TAG_NAME, "tr"):
                    #     cells = row.find_elements(By.TAG_NAME, "td")
                    #     row_data = [cell.text for cell in cells]
                    # return row_data
                    text = table.text
                    officer_inviting_bids = re.search(r'Officer Inviting Bids\s+(.+)', text).group(1)
                    bid_opening_authority = re.search(r'Bid Opening Authority\s+(.+)', text).group(1)
                    address = re.search(r'Address\s+(.+)', text).group(1)
                    contact_details = re.search(r'Contact Details\s+(.+)', text).group(1)
                    email = re.search(r'Email\s+(.+)', text).group(1)
                    return [officer_inviting_bids, bid_opening_authority, address, contact_details, email]
        except:
            print("error finding in table")       
    except:
         # WebDriverWait(driver, 0.5).until(EC.visibility_of_element_located(('xpath',"//a[@class='errorResult']"))).click()
        driver.find_element('xpath',"//a[@class='errorResult']").click
        k = driver.find_element(By.XPATH, "//div[@class='tabContainer']")
        k.find_element(By.XPATH, "//a[@class='viewCurrentalltabs']").click()
        driver.implicitly_wait(5)
        page_length = driver.find_element(By.XPATH, "//span[@class='gridSmall']")
        drops = page_length.find_elements(By.TAG_NAME, "option")
        drops[4].click()  # Select 100 items per page       
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return [""] * 5  # Return empty values if extraction fails

# Function to extract table data and save to Excel
def extract_table_to_excel(page_num, username):
    table = driver.find_element(By.CLASS_NAME, "dataTable")

    rows = []
    document_link = "https://tender.telangana.gov.in/login.html"
    state = "Telangana"

    for row in table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip header
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 9:
            continue

        # Parse closing date to desired format
        raw_closing_date = cells[7].text.strip()
        try:
            closing_date = datetime.strptime(raw_closing_date, "%d-%m-%Y %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
        except:
            closing_date = raw_closing_date  # fallback to original

        # Extract document link if available
        try:
            doc_link = cells[9].find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            doc_link = document_link

        formatted_row = {
            "user name": username,
            "Bid No": cells[1].text.strip(),
            "Name of Work": cells[4].text.strip(),
            "category": cells[3].text.strip(),
            "Ministry and Department": cells[0].text.strip(),
            "Quantity": "N/A",
            "EMD": "N/A",
            "Exemption": "N/A",
            "Estimation Value": cells[5].text.strip(),
            "state": state,
            "location": "N/A",
            "Apply Mode": "Online",
            "Website Link": document_link,
            "Document link": doc_link,
            "Attachment link": document_link,
            "End Date": closing_date
        }

        rows.append(formatted_row)

    df = pd.DataFrame(rows)
    file_name = path.join(save_directory, f"page_{page_num}.xlsx")
    df.to_excel(file_name, index=False)
    print(f"Saved: {file_name}")

# Pagination and extraction
for page_num in range(starting_page, total_pages + 1):
    print(f"Scraping page {page_num}...")
    extract_table_to_excel(page_num,username=username)
    
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
    except TimeoutException:
        print("No more pages or loading took too much time!")
        break

driver.quit()

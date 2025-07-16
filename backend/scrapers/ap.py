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
import argparse
parser = argparse.ArgumentParser(description="Scrapes data from the GeM website and saves as Excel files.")
parser.add_argument("--starting_page", type=int, required=True, help="Page number to start from.")
parser.add_argument("--user_name", type=str, required=True, help="Username to fill the Excel.")
parser.add_argument("--run_id", type=str, required=True, help="Unique run identifier.")
args = parser.parse_args()
BASE_DIR = path.dirname(path.abspath(__file__))
save_directory = path.join(BASE_DIR, "outputs", "ap", args.run_id)
# save_directory="C:\\Users\\windows11\\Desktop\\MAHESH\\BREAKDOWN\\SCRAPPING\\AP"
if not path.exists(save_directory):
    makedirs(save_directory)
chromedriver_path = BASE_DIR+r"\edgedriver_win64\\msedgedriver.exe"
servicee = Service(executable_path=chromedriver_path)
driver=webdriver.Edge(service=servicee)
driver.get("https://tender.apeprocurement.gov.in/login.html")
driver.minimize_window()
print("loading page please wait")
sleep(14)
print("page loaded")
k=driver.find_element('xpath',"//div[@class='tabContainer']")
more=k.find_element('xpath',"//a[@class='viewCurrentalltabs']").click()
driver.implicitly_wait(5)
page_length=driver.find_element('xpath',"//span[@class='gridSmall']")
drops=page_length.find_elements(By.TAG_NAME,"option")
# drops[0].click() # 10
# drops[1].click() # 20
# drops[2].click() # 40
# drops[3].click() # 50
drops[4].click() # 100
#finding last page
# WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='current']")))
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pagetable13_info"))
    )
    p = driver.find_element(By.ID, "pagetable13_info").text
except TimeoutException:
    print("Unable to locate pagetable13_info or it's empty.")
    driver.quit()
    exit()
# p=driver.find_element(By.ID,"pagetable13_info").text
numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?=\srecords)', p)
numbers = [int(number.replace(',', '')) for number in numbers]
max_number = max(numbers)
total_pages=math.ceil(max_number/100)
print("TOTAL PAGES FOUND:",total_pages)    
starting_page=args.starting_page
current_page=driver.find_element('xpath',"//a[@class='paginate_button current']").text
current_page=int(current_page)
if current_page==starting_page:
    print(f"**********************SCRAPING STARTED FROM {starting_page}*****************")
    pages=total_pages+1
else:
    if starting_page>1:
        print(f"************GOING TO PAGE NUMBER***********{starting_page}")
        sleep(1)
        try:
            for i in range(starting_page-1):
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
                nextbutton = driver.find_element(By.LINK_TEXT,"Next").click()
            currentpage=driver.find_element('xpath',"//span[@class='current']").text
            print("current page:",currentpage)
        except Exception as e:
            print("PROGRAM UNABLE TO CLICK PAGE YOU SPECIFIED CLICK IT MANUALLY")
        input("PRESS ENTER IF YOU CLICKED THE DESIRED PAGE")
        current_page=driver.find_element('xpath',"//a[@class='paginate_button current']").text
        current_page=int(current_page)   
        print(f"***************WE ARE IN {current_page} PAGE***********************")
        pages=total_pages-current_page

print(f"YOU ARE IN {current_page} PAGE")

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dataTable")))
except TimeoutException:
    print("Loading took too much time!")
    driver.quit()

def pad_data(rows):    
    max_length = max(len(lst) for lst in rows.values())
    
    for key in rows:
        while len(rows[key]) < max_length:
            rows[key].append("NOT FOUND")

# Function to extract table data and save to Excel
def extract_table_to_excel(page_num, username):
    table = driver.find_element(By.CLASS_NAME, "dataTable")

    # Extract rows
    extracted_data = []
    for row in table.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 8:
            try:
                link_element = cells[8].find_element(By.TAG_NAME, "a")
                document_link = link_element.get_attribute("href")
            except:
                document_link = "N/A"

            extracted_data.append({
                "user name": username,
                "Bid No": cells[1].text,  # Assuming column 1 is Tender ID
                "Name of Work": cells[4].text,  # Assuming column 4 is Name of Work
                "category": "N/A",
                "Ministry and Department": cells[0].text,  # Assuming column 0 is Department Name
                "Quantity": "N/A",  # Not available in table
                "EMD": "N/A",
                "Exemption": "N/A",
                "Estimation Value": cells[5].text,
                "state": "Andhra Pradesh",
                "location": "N/A",
                "Apply Mode": "Online",
                "Website Link": document_link,
                "Document link": document_link,
                "Attachment link": document_link,
                "End Date": cells[6].text  # Assuming column 6 is Closing Date
            })

    # Create DataFrame and save
    df = pd.DataFrame(extracted_data)
    file_name = path.join(save_directory, f"page_{page_num}.xlsx")
    df.to_excel(file_name, index=False)
    print(f"Saved: {file_name}")


username=args.user_name
# Pagination handling (example: loop through 5 pages)
for page_num in range(current_page,total_pages+1):
    print("scraping first layer")
    extract_table_to_excel(page_num,username)
    print("first layer scraping done")
    
    # Find and click the "Next" button to go to the next page
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))  # wait for page to load
    except TimeoutException:
        print("No more pages or loading took too much time!")
        break
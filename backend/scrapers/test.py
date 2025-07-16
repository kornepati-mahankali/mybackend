import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd

# ----------------------------
# Step 1: Headless Browser Setup with Selenium
# ----------------------------
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("https://tender.apeprocurement.gov.in/login.html")
driver.implicitly_wait(5)

# ----------------------------
# Step 2: Extract Required Tokens
# ----------------------------
csrf_token = driver.find_element(By.NAME, "CSRFToken").get_attribute("value")
encrypt_names = driver.find_element(By.NAME, "hdnEncryptNames").get_attribute("value")
encrypt_values = driver.find_element(By.NAME, "hdnEncryptValues").get_attribute("value")
cookies = driver.get_cookies()
driver.quit()

# ----------------------------
# Step 3: Setup Requests Session
# ----------------------------
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://tender.apeprocurement.gov.in",
    "Referer": "https://tender.apeprocurement.gov.in/login.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

data = {
    "tabs": "on",
    "userName": "",
    "password": "",
    "hdnCurrDate": "04/06/2025",
    "paymentId": "",
    "popUPRequestParameter": "",
    "hdnProcurementID": "",
    "hdnPage": "",
    "hdnType": "current",
    "hdnRandomVal": "",
    "hdnSelectedCertificate": "",
    "hdncertSerialNo": "",
    "hdnCertIssuer": "",
    "hdnExpiryDate": "",
    "hdnOwnerName": "",
    "hdnThumbPrint": "",
    "hdnActiveDate": "",
    "hdnSubjectDN": "",
    "hdnPublicKey": "",
    "failCount": "",
    "hdnImmediatePreviousPage": "login.html",
    "hdnPreviousPage": "login.html",
    "hdncaptcha": "0",
    "dtBidClosing1": "",
    "hdnSignData": "",
    "hdnEnc": "1",
    "emSignIssuerName": "",
    "CSRFToken": csrf_token,
    "hdnEncryptNames": encrypt_names,
    "hdnEncryptValues": encrypt_values,
}

# ----------------------------
# Step 4: Make POST request
# ----------------------------
url = "https://tender.apeprocurement.gov.in/TenderDetailsHome.html"
resp = session.post(url, headers=headers, data=data)
soup = BeautifulSoup(resp.text, "html.parser")


# ----------------------------
# Step 5: Scrape Table Data
# ----------------------------
table = soup.find("table", {"id": "pagetable13"})
print("[+] Table found:", bool(table))
print("[+] Table HTML preview:\n", str(table)[:1000000])


if not table:
    print("❌ Table not found. Check the HTML.")
    exit()

rows = table.find_all("tr")
data_rows = []

# First row is usually the header
headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

# Extract rows
rows = []
for tr in table.find("tbody").find_all("tr"):
    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
    if cells:
        rows.append(cells)

# ----------------------------
# Step 6: Save to Excel
# ----------------------------
df = pd.DataFrame(rows, columns=headers)
# print(df)
# df.to_excel("tenders.xlsx", index=False)
print("✅ Data saved to tenders.xlsx")

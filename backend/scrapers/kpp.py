import requests
import requests.exceptions
from os import *
from datetime import *
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Scrapes data from KPP website and saves Excel files.")
parser.add_argument("--section", type=str, required=True, help="Section name to scrape (e.g., Goods, Works, Services).")
parser.add_argument("--gtotal", type=int, required=True, help="Total pages in Goods section.")
parser.add_argument("--wtotal", type=int, required=True, help="Total pages in Works section.")
parser.add_argument("--stotal", type=int, required=True, help="Total pages in Services section.")

args = parser.parse_args()

parser = argparse.ArgumentParser(description="Scrapes data from KPP website and saves Excel files.")
parser.add_argument("--run_id", type=str, required=True, help="Unique run identifier.")
args = parser.parse_args()

BASE_DIR = path.dirname(path.abspath(__file__))
OUTPUT_DIR = path.join(BASE_DIR, "outputs", "kpp", args.run_id)
GOODS = path.join(OUTPUT_DIR, "goods")
WORK = path.join(OUTPUT_DIR, "works")
SERVICES = path.join(OUTPUT_DIR, "services")

makedirs(GOODS, exist_ok=True)
makedirs(WORK, exist_ok=True)
makedirs(SERVICES, exist_ok=True)

def save_to_excel(page,exdata,section,dirr):
    # print(exdata)
    if not exdata or not isinstance(exdata, list) or not all(isinstance(item, dict) for item in exdata):
        print(f"No valid data to save for page {page}")
        return
    today=date.today()
    today=today=today.strftime("%y-%m-%d")
    df_new = pd.DataFrame(exdata)
    file = f"\\page_{page}_of_{section}_dated_{today}.xlsx"        
    name=dirr+file
    filepath=name
    print(filepath)
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df_new.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"New file '{filepath}' created and data written.")
    except Exception as e:
        print(f"Error occurred while handling Excel file: {str(e)}")    
def scrape_goods(page,sec):
    url = "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/search-eproc-tenders"
    payload = {
        "tenderNumber": "",
        "category": "GOODS",  
        "location": None,
        "publishedFromDate": None,
        "publishedToDate": None,
        "status": "PUBLISHED",
        "tenderClosureFromDate": None,
        "tenderClosureToDate": None,
        "title": ""
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0SlRLQW1QY2dFNFJtRFBvWC0tdXowN2hkQUJDcXpBOXAya3pSOWd1cjBVIn0.eyJleHAiOjE2ODE4ODgwNTIsImlhdCI6MTY4MTg4NDQ1MiwiYXV0aF90aW1lIjoxNjgxODgyNjgyLCJqdGkiOiJiZWEyYzkxYy0xN2QwLTRiOTctODE2NC1iMTZiNDIzMDFlMmYiLCJpc3MiOiJodHRwczovL3d3dy5nb2stZXByb2MyLmluL2F1dGgvcmVhbG1zL2Vwcm9jdXJlbWVudC1kZXYiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiOTNiMzcwNWMtMWE0My00OWY1LWE2OTEtZjQwYWE2MmJhN2JmIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZXByb2MtYXV0aCIsIm5vbmNlIjoiMGRjMmI3MmQtNWU3NC00OGMwLTgwNTEtNDUzYzI3ZDkyODhiIiwic2Vzc2lvbl9zdGF0ZSI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3d3dy5nb2stZXByb2MyLmluLyoiLCIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwidXNlclR5cGUiOiJTIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiczEwMDE3In0.SqnoDJ_77XzajQ7oBlXSpLzTVnjMdx3Dp87nEBPL9Yt-s54-wn4dDavGpTW2gLPwqT0F3fMd0gkeubXIQBddpM-2Ju27r4s4wbR6DuGnueNbCcQFaRQAWrb7xi37qdZIe1TulrcBdkbHAGt7MKLmXUCM7PNY9MM9XtzWRiC2Vz82yA2VxiKdKS7SHwF6agDE0oMa2OYvrviJw_JYYEggT2RFOgaiyu3_3SFxK3G96v9D5gezTK1_P4te7ZJy9M5yI_dHv-p8ghO-BgKiEwe2kNV6rhWgD-i1fD2-Kge92bY4yrk4b8rBoRk20yE_2ukZ2w_VY68q-ztVPgGWHjtZBA",  # Replace with your actual token
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    querystring = {"page": f"{page}", "size": "19", "order-by-tender-publish": "true"}
    try:
        response = requests.post(url, json=payload, headers=headers, params=querystring)
        print(f"got response for page:{page}")
        response.raise_for_status()
        response_json = response.json()

        # Check if the response is a list or dictionary
        if isinstance(response_json, dict):
            data = response_json.get('data', [])
        elif isinstance(response_json, list):
            # Ensure the list contains dictionaries suitable for saving to Excel
            if all(isinstance(item, dict) for item in response_json):
                data = response_json  # List of dictionaries
            else:
                print("List does not contain dictionaries, cannot save to Excel.")
                data = []
        else:
            print("Unexpected response format.")
            data = []
    except requests.exceptions.RequestException as e:
        print(f"an error occured:{e}")
    save_to_excel(page,data,sec,GOODS)

def scrape_works(page,sec):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0SlRLQW1QY2dFNFJtRFBvWC0tdXowN2hkQUJDcXpBOXAya3pSOWd1cjBVIn0.eyJleHAiOjE2ODE4ODgwNTIsImlhdCI6MTY4MTg4NDQ1MiwiYXV0aF90aW1lIjoxNjgxODgyNjgyLCJqdGkiOiJiZWEyYzkxYy0xN2QwLTRiOTctODE2NC1iMTZiNDIzMDFlMmYiLCJpc3MiOiJodHRwczovL3d3dy5nb2stZXByb2MyLmluL2F1dGgvcmVhbG1zL2Vwcm9jdXJlbWVudC1kZXYiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiOTNiMzcwNWMtMWE0My00OWY1LWE2OTEtZjQwYWE2MmJhN2JmIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZXByb2MtYXV0aCIsIm5vbmNlIjoiMGRjMmI3MmQtNWU3NC00OGMwLTgwNTEtNDUzYzI3ZDkyODhiIiwic2Vzc2lvbl9zdGF0ZSI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3d3dy5nb2stZXByb2MyLmluLyoiLCIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwidXNlclR5cGUiOiJTIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiczEwMDE3In0.SqnoDJ_77XzajQ7oBlXSpLzTVnjMdx3Dp87nEBPL9Yt-s54-wn4dDavGpTW2gLPwqT0F3fMd0gkeubXIQBddpM-2Ju27r4s4wbR6DuGnueNbCcQFaRQAWrb7xi37qdZIe1TulrcBdkbHAGt7MKLmXUCM7PNY9MM9XtzWRiC2Vz82yA2VxiKdKS7SHwF6agDE0oMa2OYvrviJw_JYYEggT2RFOgaiyu3_3SFxK3G96v9D5gezTK1_P4te7ZJy9M5yI_dHv-p8ghO-BgKiEwe2kNV6rhWgD-i1fD2-Kge92bY4yrk4b8rBoRk20yE_2ukZ2w_VY68q-ztVPgGWHjtZBA',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://kppp.karnataka.gov.in',
        'Post': 'CONTRACTOR-EPROC-CONTRACTOR',
        'Referer': 'https://kppp.karnataka.gov.in/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'page': f'{page}',
        'size': '18',
        'order-by-tender-publish': 'true',
    }

    data = '{"tenderNumber":"","category":"WORKS","status":"PUBLISHED","publishedFromDate":null,"publishedToDate":null,"title":"","location":null,"tenderClosureFromDate":null,"tenderClosureToDate":null,"workCategoryId":null}'
    try:    
        response = requests.post(
        'https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/works/search-eproc-tenders',
        params=params,
        headers=headers,
        data=data,
        )
        print(f"got response for page:{page}")
        response.raise_for_status()
        response_json = response.json()

        # Check if the response is a list or dictionary
        if isinstance(response_json, dict):
            data = response_json.get('data', [])
        elif isinstance(response_json, list):
            # Ensure the list contains dictionaries suitable for saving to Excel
            if all(isinstance(item, dict) for item in response_json):
                data = response_json  # List of dictionaries
            else:
                print("List does not contain dictionaries, cannot save to Excel.")
                data = []
        else:
            print("Unexpected response format.")
            data = []
    except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    save_to_excel(page,data,sec,WORK)



def scrape_services(page,sec):
    url = "https://kppp.karnataka.gov.in/supplier-registration-service/v1/api/portal-service/services/search-eproc-tenders"

    querystring = {"page": f"{page}", "size": "18", "order-by-tender-publish": "true"}

    payload = {
        "tenderNumber": "",
        "category": "SERVICES",
        "status": "PUBLISHED",
        "publishedFromDate": None,
        "publishedToDate": None,
        "tenderType": "OPEN",
        "title": "",
        "location": None,
        "tenderClosureFromDate": None,
        "tenderClosureToDate": None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0SlRLQW1QY2dFNFJtRFBvWC0tdXowN2hkQUJDcXpBOXAya3pSOWd1cjBVIn0.eyJleHAiOjE2ODE4ODgwNTIsImlhdCI6MTY4MTg4NDQ1MiwiYXV0aF90aW1lIjoxNjgxODgyNjgyLCJqdGkiOiJiZWEyYzkxYy0xN2QwLTRiOTctODE2NC1iMTZiNDIzMDFlMmYiLCJpc3MiOiJodHRwczovL3d3dy5nb2stZXByb2MyLmluL2F1dGgvcmVhbG1zL2Vwcm9jdXJlbWVudC1kZXYiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiOTNiMzcwNWMtMWE0My00OWY1LWE2OTEtZjQwYWE2MmJhN2JmIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZXByb2MtYXV0aCIsIm5vbmNlIjoiMGRjMmI3MmQtNWU3NC00OGMwLTgwNTEtNDUzYzI3ZDkyODhiIiwic2Vzc2lvbl9zdGF0ZSI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3d3dy5nb2stZXByb2MyLmluLyoiLCIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6IjIwM2UwZGRlLTlmMDEtNDMyOS1hZDU3LWY5ZGFiN2IzNDQ5ZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwidXNlclR5cGUiOiJTIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiczEwMDE3In0.SqnoDJ_77XzajQ7oBlXSpLzTVnjMdx3Dp87nEBPL9Yt-s54-wn4dDavGpTW2gLPwqT0F3fMd0gkeubXIQBddpM-2Ju27r4s4wbR6DuGnueNbCcQFaRQAWrb7xi37qdZIe1TulrcBdkbHAGt7MKLmXUCM7PNY9MM9XtzWRiC2Vz82yA2VxiKdKS7SHwF6agDE0oMa2OYvrviJw_JYYEggT2RFOgaiyu3_3SFxK3G96v9D5gezTK1_P4te7ZJy9M5yI_dHv-p8ghO-BgKiEwe2kNV6rhWgD-i1fD2-Kge92bY4yrk4b8rBoRk20yE_2ukZ2w_VY68q-ztVPgGWHjtZBA",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://kppp.karnataka.gov.in",
        "Post": "CONTRACTOR-EPROC-CONTRACTOR",
        "Referer": "https://kppp.karnataka.gov.in/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    try:
        response = requests.post(url, json=payload, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad responses
        print(f"got response for page:{page}")
        response_json = response.json()

        # Check if the response is a list or dictionary
        if isinstance(response_json, dict):
            data = response_json.get('data', [])
        elif isinstance(response_json, list):
            # Ensure the list contains dictionaries suitable for saving to Excel
            if all(isinstance(item, dict) for item in response_json):
                data = response_json  # List of dictionaries
            else:
                print("List does not contain dictionaries, cannot save to Excel.")
                data = []
        else:
            print("Unexpected response format.")
            data = []
        save_to_excel(page,data,sec,SERVICES)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

section = args.section
gtotal = args.gtotal
wtotal = args.wtotal
stotal = args.stotal
if section == "goods":    
    for g in range(gtotal+1):
        print(f"Scraping {section} {g+1} page......")
        scrape_goods(g,section)
        print(f"scraping {section} {g+1} page done")
    for w in range(wtotal+1):
        print(f"Scraping works {w+1} page......")
        scrape_works(w,"works")
        print(f"scraping works {w+1} page done")
    for s in range(stotal+1):
        print(f"Scraping services {s+1} page......")
        scrape_services(s,"services")
        print(f"scraping services {s+1} page done")
elif section == "works":
    for w in range(wtotal+1):
        print(f"Scraping {section} {w+1} page......")
        scrape_works(w,section)
        print(f"scraping {section} {w+1} page done")
    for s in range(stotal+1):
        print(f"Scraping services {s+1} page......")
        scrape_services(s,"services")
        print(f"scraping services {s+1} page done")
elif section == "services":
    for s in range(stotal+1):
        print(f"Scraping {section} {s+1} page......")
        scrape_services(s,section)
        print(f"scraping {section} {s+1} page done")
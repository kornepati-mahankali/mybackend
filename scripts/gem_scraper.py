
import requests
import pandas as pd
import json
from os import *
from datetime import *
from bs4 import BeautifulSoup
import time
import argparse
parser = argparse.ArgumentParser(description="Scrapes data from the GeM website and saves as Excel files.")
parser.add_argument("--startingpage", type=int, required=True, help="Page number to start from.")
parser.add_argument("--totalpages", type=int, required=True, help="Total pages to scrape.")
parser.add_argument("--username", type=str, required=True, help="Username to fill the Excel.")
parser.add_argument("--state_index", type=int, required=True, help="Enter the state index to scrape.")
parser.add_argument("--city_input", type=str, required=True, help="Enter city index or else skip.")
parser.add_argument("--days_interval", type=int, required=False, help="Page number to start from.")
parser.add_argument("--run_id", type=str, required=True, help="Unique run identifier.")
args = parser.parse_args()
BASEDIR=path.dirname(path.abspath(__file__))
OUTPUTDIR=path.join(BASEDIR, "outputs", "gem", args.run_id)
makedirs(OUTPUTDIR,exist_ok=True)

username=args.username
# Headers
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,te;q=0.8,ar;q=0.7,ta;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://bidplus.gem.gov.in",
    "Referer": "https://bidplus.gem.gov.in/advance-search",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

# Placeholder for valid states and cities
# These should be scraped and replaced with actual data from the website
# Valid states and cities
valid_states = [
    "ANDAMAN & NICOBAR",
    "ANDHRA PRADESH",
    "ARUNACHAL PRADESH",
    "ASSAM",
    "BIHAR",
    "CHANDIGARH",
    "CHHATTISGARH",
    "DADRA & NAGAR HAVELI",
    "DAMAN & DIU",
    "DELHI",
    "GOA",
    "GUJARAT",
    "HARYANA",
    "HIMACHAL PRADESH",
    "JAMMU & KASHMIR",
    "JHARKHAND",
    "KARNATAKA",
    "KERALA",
    "LAKSHADWEEP",
    "MADHYA PRADESH",
    "MAHARASHTRA",
    "MANIPUR",
    "MEGHALAYA",
    "MIZORAM",
    "NAGALAND",
    "ODISHA",
    "PUDUCHERRY",
    "PUNJAB",
    "RAJASTHAN",
    "SIKKIM",
    "TAMIL NADU",
    "TELANGANA",
    "TRIPURA",
    "UTTAR PRADESH",
    "UTTARAKHAND",
    "WEST BENGAL"
]

valid_cities = {
    "ANDAMAN & NICOBAR": ["NICOBAR", "NORTH AND MIDDLE ANDAMAN", "SOUTH ANDAMAN"],
    "ANDHRA PRADESH": ["ANANTHAPUR", "CHITTOOR", "CUDDAPAH", "EAST GODAVARI", "GUNTUR", "KRISHNA", "KURNOOL", "NELLORE", "PRAKASAM", "SRIKAKULAM", "VISAKHAPATNAM", "VIZIANAGARAM", "WEST GODAVARI"],
    "ARUNACHAL PRADESH": ["CHANGLANG", "DIBANG VALLEY", "EAST KAMENG", "EAST SIANG", "KURUNG KUMEY", "LOHIT", "LOWER SUBANSIRI", "PAPUM PARE", "TAWANG", "TIRAP", "UPPER SIANG", "UPPER SUBANSIRI", "WEST KAMENG", "WEST SIANG"],
    "ASSAM": ["BARPETA", "BONGAIGAON", "CACHAR", "DARRANG", "DHEMAJI", "DHUBRI", "DIBRUGARH", "GOALPARA", "GOLAGHAT", "HAILAKANDI", "JORHAT", "KAMRUP", "KARBI ANGLONG", "KARIMGANJ", "KOKRAJHAR", "LAKHIMPUR", "MARIGAON", "NAGAON", "NALBARI", "NORTH CACHAR HILLS", "SIVASAGAR", "SONITPUR", "TINSUKIA"],
    "BIHAR": ["ARARIA", "ARWAL", "AURANGABAD", "BANKA", "BEGUSARAI", "BHAGALPUR", "BHOJPUR", "BUXAR", "DARBHANGA", "EAST CHAMPARAN", "GAYA", "GOPALGANJ", "JAMUI", "JEHANABAD", "KAIMUR (BHABUA)", "KATIHAR", "KHAGARIA", "KISHANGANJ", "LAKHISARAI", "MADHEPURA", "MADHUBANI", "MUNGER", "MUZAFFARPUR", "NALANDA", "NAWADA", "PATNA", "PURNIA", "ROHTAS", "SAHARSA", "SAMASTIPUR", "SARAN", "SHEIKHPURA", "SHEOHAR", "SITAMARHI", "SIWAN", "SUPAUL", "VAISHALI", "WEST CHAMPARAN"],
    "CHANDIGARH": ["CHANDIGARH"],
    "CHHATTISGARH": ["BASTAR", "BIJAPUR", "BILASPUR", "DANTEWADA", "DHAMTARI", "DURG", "JANJGIR-CHAMPA", "JASHPUR", "KANKER", "KAWARDHA", "KORBA", "KORIYA", "MAHASAMUND", "RAIGARH", "RAIPUR", "RAJNANDGAON", "SURGUJA"],
    "DADRA & NAGAR HAVELI": ["DADRA & NAGAR HAVELI"],
    "DAMAN & DIU": ["DAMAN", "DIU"],
    "DELHI": ["CENTRAL DELHI", "EAST DELHI", "NEW DELHI", "NORTH DELHI", "NORTH EAST DELHI", "NORTH WEST DELHI", "SHAHDARA", "SOUTH DELHI", "SOUTH EAST DELHI", "SOUTH WEST DELHI", "WEST DELHI"],
    "GOA": ["NORTH GOA", "SOUTH GOA"],
    "GUJARAT": ["AHMEDABAD", "AMRELI", "ANAND", "BANASKANTHA", "BHARUCH", "BHAVNAGAR", "DAHOD", "GANDHI NAGAR", "JAMNAGAR", "JUNAGADH", "KACHCHH", "KHEDA", "MAHESANA", "NARMADA", "NAVSARI", "PANCH MAHALS", "PATAN", "PORBANDAR", "RAJKOT", "SABARKANTHA", "SURAT", "SURENDRA NAGAR", "THE DANGS", "VADODARA", "VALSAD"],
    "HARYANA": ["AMBALA", "BHIWANI", "FARIDABAD", "FATEHABAD", "GURGAON", "HISAR", "JHAJJAR", "JIND", "KAITHAL", "KARNAL", "KURUKSHETRA", "MAHENDRAGARH", "PANCHKULA", "PANIPAT", "REWARI", "ROHTAK", "SIRSA", "SONIPAT", "YAMUNA NAGAR"],
    "HIMACHAL PRADESH": ["BILASPUR (HP)", "CHAMBA", "HAMIRPUR", "KANGRA", "KINNAUR", "KULLU", "LAHUL & SPITI", "MANDI", "SHIMLA", "SIRMAUR", "SOLAN", "UNA"],
    "JAMMU & KASHMIR": ["ANANTHNAG", "BANDIPUR", "BARAMULLA", "BUDGAM", "DODA", "JAMMU", "KARGIL", "KATHUA", "KUPWARA", "LEH", "POONCH", "PULWAMA", "RAJAURI", "SAMBA", "SRINAGAR", "UDHAMPUR"],
    "JHARKHAND": ["BOKARO", "CHATRA", "DEOGHAR", "DHANBAD", "DUMKA", "EAST SINGHBHUM", "GARHWA", "GIRIDH", "GODDA", "GUMLA", "HAZARIBAG", "JAMTARA", "KHUNTI", "KODERMA", "LATEHAR", "LOHARDAGA", "PAKUR", "PALAMAU", "RAMGARH", "RANCHI", "SAHIBGANJ", "SARAIKELA KHARSAWAN", "SIMDEGA", "WEST SINGHBHUM"],
    "KARNATAKA": ["BAGALKOT", "BANGALORE", "BANGALORE RURAL", "BELGAUM", "BELLARY", "BIDAR", "BIJAPUR", "CHAMRAJNAGAR", "CHICKMAGALUR", "CHIKKABALLAPUR", "CHITRADURGA", "DAKSHINA KANNADA", "DAVANGARE", "DHARWARD", "GADAG", "GULBARGA", "HASSAN", "HAVERI", "KODAGU", "KOLAR", "KOPPAL", "MANDYA", "MYSURU", "RAICHUR", "RAMANAGAR", "SHIMOGA", "TUMKUR", "UDUPI", "UTTARA KANNADA"],
    "KERALA": ["ALAPPUZHA", "ERNAKULAM", "IDUKKI", "KANNUR", "KASARGOD", "KOLLAM", "KOTTAYAM", "KOZHIKODE", "MALAPPURAM", "PALAKKAD", "PATHANAMTHITTA", "THIRUVANANTHAPURAM", "THRISSUR", "WAYANAD"],
    "LAKSHADWEEP": ["LAKSHADWEEP"],
    "MADHYA PRADESH": ["ANUPPUR", "ASHOKNAGAR", "BALAGHAT", "BARWANI", "BETUL", "BHIND", "BHOPAL", "CHHATARPUR", "CHHINDWARA", "DAMOH", "DATIA", "DEWAS", "DHAR", "DINDORI", "GUNA", "HARDa", "HOSHANGABAD", "INDORE", "JABALPUR", "KATNI", "MANDLA", "MANDSAUR", "MORENA", "NARMADAPURAM", "NEEMUCH", "PANCHMADHI", "RAISEN", "RAJGARH", "RATLAM", "REWA", "SAGAR", "SATNA", "SEHORE", "SHIVPURI", "SIDHI", "TIKAMGARH", "UMARIA", "VIDISHA"],
    "MAHARASHTRA": ["AHMADNAGAR", "AKOLA", "AMRAVATI", "AURANGABAD", "BANDRA", "BEED", "BULDHANA", "CHANDRAPUR", "DHULE", "GADCHIROLI", "GONDIA", "HINGOLI", "JALNA", "JALGAON", "KOLHAPUR", "LATUR", "NANDURBAR", "NASHIK", "OSMANABAD", "PARBHANI", "PUNE", "RAIGAD", "RATNAGIRI", "SANGLI", "SATARA", "SINDHUDURG", "SOLAPUR", "THANE", "WASHIM", "YAVATMAL"],
    "MANIPUR": ["BISHNUPUR", "CHURACHANDPUR", "CHAMPHAI", "IMPHAL EAST", "IMPHAL WEST", "JIRIBAM", "KANGPOKPI", "KAKCHING", "NONEY", "PHEK", "SENAPATI", "TAMENGLONG", "THOUBAL", "UKHRUL"],
    "MEGHALAYA": ["EAST GARO HILLS", "EAST KHASI HILLS", "NORTH GARO HILLS", "RIBHOI", "SOUTH GARO HILLS", "SOUTH KHASI HILLS", "WEST GARO HILLS", "WEST KHASI HILLS"],
    "MIZORAM": ["AIZAWL", "CHAMPHAI", "KHAWZAWL", "LUNGLEI", "MAMIT", "SAIHA", "SIAHA", "THANHLUN"],
    "NAGALAND": ["DIMAPUR", "KIPHIRE", "MOKOKCHUNG", "MON", "PHEK", "TUENSANG", "WOKHA", "ZUNHEBOTO"],
    "ODISHA": ["ANGUL", "BALASORE", "BARGARH", "BHADRAK", "BOLANGIR", "DEOGARH", "Dhenkanal", "Ganjam", "Ganjam", "Kandhamal", "Kendrapara", "Kendujhar", "Khurda", "Malkangiri", "Nabarangpur", "Nayagarh", "Nuapada", "Rayagada", "Sambalpur", "Sonepur", "Jagatsinghpur", "Jharsuguda", "Kandhamal", "Mayurbhanj"],
    "PUDUCHERRY": ["PUDUCHERRY"],
    "PUNJAB": ["AMRITSAR", "BARNALA", "BATALA", "FATEHGARH SAHIB", "FARIDKOT", "GURDASPUR", "HOSHIARPUR", "JALANDHAR", "KAPURTHALA", "LUDHIANA", "MANSA", "MOGA", "PATHANKOT", "PATIALA", "RUPNAGAR", "SANGRUR", "SAS NAGAR", "TARN TARAN"],
    "RAJASTHAN": ["AJMER", "ALWAR", "BANSWARA", "BARAN", "BARMER", "BHARATPUR", "BHILWARA", "BIKANER", "CHITTORGARH", "CHURU", "DHAULPUR", "DUNGARPUR", "GANGANAGAR", "JAIL", "JAISALMER", "JAIPUR", "JODHPUR", "KARAULI", "KOTA", "NAGAUR", "PALI", "RAJSAMAND", "SAWAI MADHOPUR", "SIKAR", "TONK", "UDAIPUR"],
    "SIKKIM": ["EAST SIKKIM", "NORTH SIKKIM", "SOUTH SIKKIM", "WEST SIKKIM"],
    "TAMIL NADU": ["ARIYALUR", "CHENNAI", "CHENNAI (TOWN)", "COIMBATORE", "CUDDALORE", "DINDIGUL", "ERODE", "KANCHEEPURAM", "KARUR", "MADURAI", "NAGAPATTINAM", "NAMAKKAL", "PERAMBALUR", "PUDUKOTTAI", "RAMANATHAPURAM", "SALEM", "SIVAGANGA", "TIRUCHIRAPALLI", "TIRUNELVELI", "VILLUPURAM", "VIRUDHUNAGAR"],
    "TELANGANA": ["ADILABAD", "HYDERABAD", "KHAMMAM", "MAHABUBNAGAR", "MEDAK", "NALGONDA", "NALGONDA", "NIZAMABAD", "RANGAREDDY", "WARANGAL"],
    "TRIPURA": ["AGARTALA", "DHALAI", "GOMATI", "KHOWAI", "NORTH TRIPURA", "SOUTH TRIPURA", "UNAKOTI"],
    "UTTAR PRADESH": ["AGRA", "ALIGARH", "ALLAHABAD", "AMBEDKAR NAGAR", "AMROHA", "AURAIYA", "BAHRAICH", "BANDA", "BULANDSHAHR", "CHANDAULI", "CHHATARPUR", "DEORIA", "ETAH", "ETAWAH", "FARRUKHABAD", "FATEHPUR", "GHAZIPUR", "GHAZIABAD", "GORAKHPUR", "HAMIRPUR", "HAPUR", "HARDOI", "JALAUN", "JHANSI", "KANNAUJ", "KASGANJ", "KAUSHAMBI", "KUSHINAGAR", "LUCKNOW", "MAIHAR", "MAU", "MEERUT", "MIRZAPUR", "MORADABAD", "MUZAFFARNAGAR", "PILIBHIT", "RAE BARELI", "RAMPUR", "SAHARANPUR", "SANT RAVIDAS NAGAR", "SHAMLI", "SHRAWASTI", "SITAPUR", "SONBHADRA", "SULTANPUR", "UNNAO", "VARANASI", "VAISHALI", "YAJMAAN"],
    "UTTARAKHAND": ["ALMORA", "BAGESHWER", "CHAMOLI", "CHAMPAWAT", "DEHRA DUN", "HARIDWAR", "NANITAL", "PITHORAGARH", "RUHAT", "TEHRI GARHWAL", "UTTARKASHI"],
    "WEST BENGAL": ["ALIPURDUAR", "BANKURA", "BARDHAMAN", "BIRBHUM", "DARBHANGA", "DEBAGRAM", "DINAJPUR", "HOOGHLY", "HOWRAH", "JALPAIGURI", "JHARGRAM", "KALIMPONG", "KOLKATA", "MALDAH", "MURSHIDABAD", "NADIA", "NORTH 24 PARGANAS", "PURBA BARDHAMAN", "PURBA MEDINIPUR", "SOUTH 24 PARGANAS", "PASCHIM BARDHAMAN", "PASCHIM MEDINIPUR", "BANKURA"]
}

cookies = {
    "themeOption": "0",
    "TS01dc9e29": "01e393167d381c8365c11e953edae5046e488b16e30e9723021273598506edc8578825fa3d5b22bf32342a5f97aa838cd4ea867470fad65c1a0028f0f4b0aecdae74eb2235",
    "_gid": "GA1.3.1605478846.1748239703",
    "csrf_gem_cookie": "88bd48d4f34489018bbc590b787ff22f",
    "ci_session": "87b0534b6667a4dc0e976e8bc1e8ba2590475b8f",
    "GeM": "1458192740.20480.0000",
    "TS0123c430": "01e393167d3a5d83e60ee172c8038cfa0abf4f3fe145ce91a03788dfb37c10df3df67b1e128860aae9926d15a3c0cbb984f0983c316b975ed0ddde6616a2479a25f19974bd72a958b5fda3a61aed194e173e375b0cf837edf5dd3d20979a78d85981814913",
    "_gat_gtag_UA_82282508_1": "1",
    "_ga": "GA1.3.797046377.1745167984",
    "_ga_MMQ7TYBESB": "GS2.3.s1748239706$o25$g1$t1748239720$j46$l0$h0$dRwesi0qfON2yhLrcxhydPzVneefHy92o2A",
    "TS9dc197d5027": "082c9b9876ab200023aea191af68b2fba37e8f621e67346ca17d8721a9d7ec3428447ea88e33dfcc087fb24fc0113000c55ec0ada8c2d5fe73157e85ef9c8caeab7d13518d14e2cbf3503143352801633fd7ce781e9f3a108e51cfb720d70cfc"
}

# Function to display options and get the user's selection
def display_options(options):
    for index, option in enumerate(options):
        print(f"[{index + 1}] {option}")

# Function to handle user selection of state and city
def select_state_and_city():
    # Display valid states and let the user select
    print("\nSelect a state:")
    display_options(valid_states)
    
    state_index = args.startingpage - 1
    
    if state_index < 0 or state_index >= len(valid_states):
        print("Invalid state selection. Exiting.")
        return None, None

    selected_state = valid_states[state_index]
    print(f"\nYou selected: {selected_state}")
    
    # Display valid cities for the selected state
    if selected_state in valid_cities:
        cities = valid_cities[selected_state]
        print(f"\nSelect a city in {selected_state}:")
        display_options(cities)
        
        city_input = args.city_input
        
        if city_input.strip() == "":
            selected_city = ""
            print(f"\nYou selected: {selected_state} with no specific city.")
        else:
            city_index = int(city_input) - 1
            if city_index < 0 or city_index >= len(cities):
                print("Invalid city selection. Exiting.")
                return None, None
            selected_city = cities[city_index]
            print(f"\nYou selected: {selected_state}, {selected_city}")
    else:
        selected_city = ""
        print(f"\nYou selected: {selected_state} with no specific city.")
    
    return selected_state, selected_city

def select_dates():
        today=date.today()
        tomorrow = today + timedelta(days = 1)
        days_interval = args.days_interval
        if (days_interval == 1):
            tomorrow = today + timedelta(days = 1)
            tomorrow=tomorrow.strftime("%y-%m-%d") 
        elif (days_interval > 1):        
            tomorrow = today + timedelta(days = days_interval)
            tomorrow=tomorrow.strftime("%y-%m-%d")
        today=today.strftime("%y-%m-%d")
        return today,tomorrow
# Function to make the request and extract bid data
def fetch_bid_data(state, city, today, tommorrow):
    print("state:", state, "city:", city, "today:", today, "end date:", tommorrow)
    totalpages = args.totalpages
    startingpage = args.startingpage

    pgno = startingpage
    while True:
        if pgno == totalpages:
            print("SCRAPING COMPLETED")
            break

        payload = {
            "payload": json.dumps({
                "searchType": "con",
                "state_name_con": state,
                "city_name_con": city,
                "bidEndFromCon": today,
                "bidEndToCon": tommorrow,
                "page": pgno
            }),
            "csrf_bd_gem_nk": "88bd48d4f34489018bbc590b787ff22f"
        }

        url = "https://bidplus.gem.gov.in/search-bids"

        for attempt in range(2):  # Try max 2 times
            try:
                time.sleep(1.5)
                response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False,timeout=5)

                if response.status_code == 200:
                    response_data = response.json()
                    docs = response_data.get('response', {}).get('response', {}).get('docs', [])
                    if docs:
                        extracted_data = []
                        for item in docs:
                            bid_id = item.get('id', '')
                            document_link = f"https://bidplus.gem.gov.in/showbidDocument/{bid_id}"
                            extracted_data.append({
                                "user name": username,
                                'Bid No': item.get('b_bid_number', [''])[0],
                                'Name of Work': item.get('b_category_name', [''])[0],
                                "category": "N/A",
                                'Ministry and Department': f"{item.get('ba_official_details_minName', [''])[0]} - {item.get('ba_official_details_deptName', [''])[0]}",
                                'Quantity': item.get('b_total_quantity', [''])[0],
                                "EMD": "N/A",
                                "Exemption": "N/A",
                                "Estimation Value": "N/A",
                                "state": state,
                                "location": "N/A",
                                "Apply Mode": "Online",
                                "Website Link": "https://bidplus.gem.gov.in/",
                                "Document link": document_link,
                                "Attachment link": document_link,
                                'End Date': item.get('final_end_date_sort', [''])[0],
                            })

                        df = pd.DataFrame(extracted_data)
                        df['End Date'] = pd.to_datetime(df['End Date']).dt.strftime('%d-%m-%Y %H:%M:%S')
                        print(f"\nExtracted Bid Data for Page :{pgno}:")
                        print(df)

                        file = f"\\gem_output_of_page_{pgno}_dated_{today}.xlsx"
                        filepath = OUTPUTDIR + file

                        try:
                            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Sheet1')
                            print(f"New file '{filepath}' created and data written.")
                        except Exception as e:
                            print(f"Error occurred while handling Excel file: {str(e)}")

                    else:
                        print(f"No bid data found on page {pgno}.")
                    break  # Break the retry loop if successful

                else:
                    print(f"Attempt {attempt + 1}: Failed with status code {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1}: Exception occurred on page {pgno} - {str(e)}")

            if attempt == 1:
                print(f"Skipping page {pgno} after 2 failed attempts.")
        pgno += 1

# Main function to run the script
def main():
    # Step 1: User selects state and city
    state, city = select_state_and_city()
    
    if state:  # Proceed if a valid state was selected
        # Step 2: Fetch bid data for the selected state and city
        today,tommorrow=select_dates()
        fetch_bid_data(state, city,today,tommorrow)

if __name__ == "__main__":
    main()

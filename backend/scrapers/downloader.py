import requests
import os

def download_file(tender_id, download_dir, url, cookie):
    try:
        headers = {
            'Cookie': f'JSESSIONID={cookie}',
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filename = os.path.basename(url)
            file_path = os.path.join(download_dir, f"{tender_id}_{filename}")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            print(f"Failed to download file: {url}")
            return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None 
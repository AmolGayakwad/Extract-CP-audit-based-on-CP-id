import requests
import time
from datetime import datetime

BASE_URL = "https://demo.openspecimen.org"
USERNAME = "<username>"
PASSWORD = "<password>"

def get_token():
    url = f"{BASE_URL}/rest/ng/sessions"
    payload = {"loginName": USERNAME, "password": PASSWORD, "domainName": "openspecimen"}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]

def to_millis(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()) * 1000)

def export_cp_audit(cp_id, start_ms, end_ms, token):
    url = f"{BASE_URL}/rest/ng/audit/export-revisions"
    headers = {"X-OS-API-TOKEN": token, "Content-Type": "application/json"}
    payload = {
        "startDate": start_ms,
        "endDate": end_ms,
        "recordIds": [int(cp_id)],
        "entities": ["CollectionProtocol"],
        "includeModifiedProps": True
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json().get("fileId")

def download_file(file_id, cp_id, token):
    url = f"{BASE_URL}/rest/ng/audit/revisions-file?fileId={file_id}"
    headers = {"X-OS-API-TOKEN": token}
    filename = f"cp_{cp_id}_audit.zip"
    with requests.get(url, headers=headers, stream=True) as resp:
        resp.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
    print(f"Downloaded: {filename}")

def main():
    cp_id = input("Enter CP ID: ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        start_ms = to_millis(start_date)
        end_ms = to_millis(end_date) + 86399999
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    try:
        token = get_token()
        file_id = export_cp_audit(cp_id, start_ms, end_ms, token)
        if file_id:
            download_file(file_id, cp_id, token)
        else:
            print("Export running in background")
    except requests.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

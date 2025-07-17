import requests
import time
import zipfile
import os
import csv
from datetime import datetime

BASE_URL = "https://demo.openspecimen.org"
USERNAME = "amol@krishagni.com"
PASSWORD = "Login@123"

def get_token():
    url = f"{BASE_URL}/rest/ng/sessions"
    payload = {
        "loginName": USERNAME,
        "password": PASSWORD,
        "domainName": "openspecimen"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["token"]

def to_millis(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()) * 1000)

def export_audit(cp_id, start_millis, end_millis, token):
    url = f"{BASE_URL}/rest/ng/audit/export-revisions"
    headers = {
        "X-OS-API-TOKEN": token,
        "Content-Type": "application/json"
    }
    payload = {
        "startDate": start_millis,
        "endDate": end_millis,
        "recordIds": [int(cp_id)],
        "entities": ["CollectionProtocol"],
        "includeModifiedProps": True
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("fileId")

def download_zip(file_id, cp_id, token):
    url = f"{BASE_URL}/rest/ng/audit/revisions-file?fileId={file_id}"
    headers = {"X-OS-API-TOKEN": token}
    filename = f"cp_{cp_id}_audit.zip"
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded zip file: {filename}")
    return filename

def unzip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall()
        return zip_ref.namelist()

def process_csv(input_csv, output_csv, skip_header_lines=7):
    with open(input_csv, encoding='utf-8') as infile:
        # skip metadata lines before CSV header
        for _ in range(skip_header_lines):
            next(infile)

        reader = csv.DictReader(infile)
        with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['Date', 'User', 'Operation', 'Field Name', 'Old Value', 'New Value', 'Record ID', 'Record Type']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                change_log = row.get('Change Log', '')
                if change_log:
                    changes = change_log.split(',')
                    for change in changes:
                        change = change.strip()
                        if '=' in change:
                            field, new_value = change.split('=', 1)
                            writer.writerow({
                                'Date': row.get('Timestamp', '').strip(),
                                'User': row.get('User', '').strip(),
                                'Operation': row.get('Operation', '').strip(),
                                'Field Name': field.strip(),
                                'Old Value': '',  # Not available in this export
                                'New Value': new_value.strip(),
                                'Record ID': row.get('Record ID', '').strip(),
                                'Record Type': row.get('Record Type', '').strip()
                            })

def main():
    cp_id = input("Enter Collection Protocol ID: ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        start_ms = to_millis(start_date)
        end_ms = to_millis(end_date) + 86399999  # end of day
    except Exception:
        print("Invalid date format! Please use YYYY-MM-DD.")
        return

    try:
        token = get_token()
        file_id = export_audit(cp_id, start_ms, end_ms, token)

        if not file_id:
            print("Export is running in background. Please try again later.")
            return

        zip_file = download_zip(file_id, cp_id, token)
        extracted_files = unzip_file(zip_file)

        audit_csv = None
        for f in extracted_files:
            if f.startswith("os_core_objects_revisions") and f.endswith(".csv"):
                audit_csv = f
                break

        if not audit_csv:
            print("Audit CSV file not found in the extracted files.")
            return

        output_csv = f"cp_{cp_id}_audit_transformed.csv"
        process_csv(audit_csv, output_csv)
        print(f"Audit data processed and saved to {output_csv}")

        # Delete ZIP and extracted files
        if os.path.exists(zip_file):
            os.remove(zip_file)
            print(f"Deleted zip file: {zip_file}")

        for f in extracted_files:
            if os.path.exists(f):
                os.remove(f)
                print(f"Deleted extracted file: {f}")

    except requests.HTTPError as http_err:
        print(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()

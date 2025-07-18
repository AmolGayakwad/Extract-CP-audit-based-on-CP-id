import requests
import time
import zipfile
import os
import csv
from datetime import datetime
from collections import defaultdict

BASE_URL = "https://demo.openspecimen.org"
USERNAME = "amol@krishagni.com"
PASSWORD = "Login@123"

def get_token():
    url = f"{BASE_URL}/rest/ng/sessions"
    data = {
        "loginName": USERNAME,
        "password": PASSWORD,
        "domainName": "openspecimen"
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=data, headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]

def to_millis(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()) * 1000)

def export_audit(cp_id, start_ms, end_ms, token):
    url = f"{BASE_URL}/rest/ng/audit/export-revisions"
    payload = {
        "startDate": start_ms,
        "endDate": end_ms,
        "recordIds": [int(cp_id)],
        "entities": ["CollectionProtocol"],
        "includeModifiedProps": True
    }
    headers = {"X-OS-API-TOKEN": token, "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json().get("fileId")

def download_zip(file_id, cp_id, token):
    url = f"{BASE_URL}/rest/ng/audit/revisions-file?fileId={file_id}"
    headers = {"X-OS-API-TOKEN": token}
    filename = f"cp_{cp_id}_audit.zip"
    resp = requests.get(url, headers=headers, stream=True)
    resp.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {filename}")
    return filename

def unzip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall()
        return zip_ref.namelist()

def split_changes(change_log):
    parts = []
    current = ''
    level = 0
    for ch in change_log:
        if ch == ',' and level == 0:
            parts.append(current.strip())
            current = ''
        else:
            if ch in '[{':
                level += 1
            elif ch in ']}':
                level -= 1
            current += ch
    if current:
        parts.append(current.strip())
    return parts

def process_csv(input_csv, output_csv, cp_id):
    # Read CSV, parse change log, pivot to wide format and write output
    data_rows = []

    with open(input_csv, encoding='utf-8') as f:
        # skip first 7 header lines
        for _ in range(7):
            next(f)
        reader = csv.DictReader(f)

        for row in reader:
            changes_str = row.get('Change Log', '')
            if not changes_str:
                continue

            changes = split_changes(changes_str)
            base = {
                'CP ID': cp_id,
                'Date': row.get('Timestamp', '').strip(),
                'User': row.get('User', '').strip(),
                'Operation': row.get('Operation', '').strip()
            }

            for c in changes:
                if '=' in c:
                    field, val = c.split('=', 1)
                    data_rows.append({
                        'CP ID': base['CP ID'],
                        'Date': base['Date'],
                        'User': base['User'],
                        'Operation': base['Operation'],
                        'Field Name': field.strip(),
                        'Changed Value': val.strip()
                    })

    # Group rows by (CP ID, Date, User, Operation)
    grouped = {}
    for r in data_rows:
        key = (r['CP ID'], r['Date'], r['User'], r['Operation'])
        if key not in grouped:
            grouped[key] = {}
        # last value wins if duplicate field
        grouped[key][r['Field Name']] = r['Changed Value']

    # Collect all unique field names
    all_fields = set()
    for vals in grouped.values():
        all_fields.update(vals.keys())
    all_fields = sorted(all_fields)

    # Write wide CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        header = ['CP ID', 'Date', 'User', 'Operation'] + all_fields
        writer.writerow(header)
        for key, fields in grouped.items():
            row = list(key)  # CP ID, Date, User, Operation
            for field in all_fields:
                row.append(fields.get(field, ''))
            writer.writerow(row)

def main():
    cp_id = input("Enter Collection Protocol ID: ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        start_ms = to_millis(start_date)
        end_ms = to_millis(end_date) + 86399999
    except:
        print("Wrong date format, use YYYY-MM-DD")
        return

    try:
        token = get_token()
        file_id = export_audit(cp_id, start_ms, end_ms, token)
        if not file_id:
            print("Export is still running. Try again later.")
            return

        zip_file = download_zip(file_id, cp_id, token)
        files = unzip_file(zip_file)

        audit_csv = None
        for f in files:
            if f.startswith("os_core_objects_revisions") and f.endswith(".csv"):
                audit_csv = f
                break

        if not audit_csv:
            print("Audit CSV file not found!")
            return

        output_csv = f"cp_{cp_id}_audit_wide.csv"
        process_csv(audit_csv, output_csv, cp_id)
        print(f"Output saved to {output_csv}")

        os.remove(zip_file)
        for f in files:
            if os.path.exists(f):
                os.remove(f)

    except requests.HTTPError as e:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

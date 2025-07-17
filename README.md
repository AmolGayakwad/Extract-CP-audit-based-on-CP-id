# Extract CP Audit Logs from OpenSpecimen

This script exports audit logs of a Collection Protocol (CP) from OpenSpecimen using its REST API. It downloads the logs as a ZIP file for a specified date range and processes the data to create a detailed CSV report.

## Introduction

This script does the following:

- Authenticates with OpenSpecimen using the REST API  
- Takes Collection Protocol (CP) ID and date range as input from the user  
- Exports audit logs for the given CP and date range  
- Downloads and extracts the ZIP file containing audit data  
- Processes the extracted CSV to create a detailed transformed CSV with audit changes  
- Cleans up by deleting the downloaded ZIP and extracted files  

## Requirements

- Python 3.x  
- requests module  

## How to Run

1. Download or clone this repository.  
2. Open a terminal and navigate to the folder containing the script.  
3. Run the script with the command: 
   python3 cp_audit_export.py
When prompted, enter:

Collection Protocol ID

Start date (format: YYYY-MM-DD)

End date (format: YYYY-MM-DD)

The script will save the transformed audit CSV as:
cp_<CP_ID>_audit_transformed.csv

It will also delete the downloaded ZIP and extracted files after processing.

What I Learned
- How to authenticate with OpenSpecimen’s REST API and get a session token
- How to send POST and GET requests with headers and JSON payloads using Python’s requests library
- How to convert dates from YYYY-MM-DD format to Unix epoch time in milliseconds
- How to skip metadata lines and process CSV files in Python
- How to handle errors and invalid user inputs gracefully
- How to write modular, readable Python functions
- How to clean up temporary files after processing

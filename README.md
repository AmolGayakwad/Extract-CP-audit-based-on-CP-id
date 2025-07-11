# Extract CP audit based on CP ID


This script helps export audit logs of a Collection Protocol (CP) from OpenSpecimen using its REST API. The logs are downloaded as ZIP files for a given date range.

## Introduction

This script does the following:

- Authenticates with OpenSpecimen using REST API
- Takes CP ID and date range from the user
- Saves the logs as ZIP files

## Requirements

- Python 3.x
- requests module

## How to Run

1. Download or clone this repository.
2. Open a terminal and navigate to the folder where the script is saved.
3. Run the script:   python3 cp_audit_export.py
   
Enter the following when prompted:

1. CP ID:
2. Start date (YYYY-MM-DD)
3. End date (YYYY-MM-DD)

ZIP files will be saved with names like:  cp_<CP_ID>_audit_<START_DATE>_<END_DATE>.zip

## What I Learned

- How to authenticate with OpenSpecimen using REST API and retrieve a session token
- How to send POST and GET requests with headers and JSON payloads using Python's requests library
- How to convert dates from `YYYY-MM-DD` format to Unix epoch time in milliseconds
- How to handle invalid user inputs and date format errors
- How to write modular and reusable Python functions
- How to structure a command-line script that interacts with an API
- How to manage and handle HTTP errors using raise_for_status() and exception blocks

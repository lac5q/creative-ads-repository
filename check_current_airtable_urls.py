#!/usr/bin/env python3
"""
Check current URLs in Airtable to understand what needs to be fixed
"""

import requests
import json

# Airtable configuration
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "apptaYco3MXfoLI9M"
TABLE_NAME = "Veo3 Videos"

def get_airtable_records():
    """Get all records from Airtable"""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    params = {"pageSize": 100}
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get("records", []))
            
            # Check if there are more pages
            if "offset" in data:
                params["offset"] = data["offset"]
            else:
                break
        else:
            print(f"Error fetching records: {response.status_code}")
            print(response.text)
            return []
    
    return all_records

def main():
    """Check current URLs in Airtable"""
    
    print("=== Current Airtable URLs Analysis ===")
    
    # Get all records
    records = get_airtable_records()
    print(f"Found {len(records)} total records")
    
    # Analyze each record
    for i, record in enumerate(records, 1):
        fields = record.get("fields", {})
        ad_id = fields.get("Ad_ID", "")
        ad_name = fields.get("Ad_Name", "")
        account = fields.get("Account", "")
        current_url = fields.get("Media_Download_URL", "")
        
        print(f"\n--- Record {i} ---")
        print(f"Ad Name: {ad_name}")
        print(f"Account: {account}")
        print(f"Ad ID: {ad_id}")
        print(f"Current URL: {current_url}")
        
        # Check if URL is working
        if current_url:
            try:
                response = requests.head(current_url, timeout=5)
                if response.status_code == 200:
                    print(f"URL Status: ✅ Working (200)")
                elif response.status_code == 404:
                    print(f"URL Status: ❌ 404 Not Found")
                else:
                    print(f"URL Status: ⚠️ {response.status_code}")
            except Exception as e:
                print(f"URL Status: ❌ Error: {str(e)}")
        else:
            print("URL Status: ❌ No URL provided")
    
    # Summary
    working_urls = 0
    broken_urls = 0
    no_urls = 0
    
    for record in records:
        fields = record.get("fields", {})
        current_url = fields.get("Media_Download_URL", "")
        
        if not current_url:
            no_urls += 1
        else:
            try:
                response = requests.head(current_url, timeout=5)
                if response.status_code == 200:
                    working_urls += 1
                else:
                    broken_urls += 1
            except:
                broken_urls += 1
    
    print(f"\n=== Summary ===")
    print(f"Total records: {len(records)}")
    print(f"Working URLs: {working_urls}")
    print(f"Broken URLs: {broken_urls}")
    print(f"No URLs: {no_urls}")
    
    if broken_urls > 0:
        print(f"\n⚠️ Found {broken_urls} broken URLs that need to be fixed!")
    else:
        print(f"\n✅ All URLs are working properly!")

if __name__ == "__main__":
    main() 
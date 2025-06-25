#!/usr/bin/env python3
"""
Examine Airtable data to understand what needs to be updated
"""

import requests
import json

# Airtable configuration
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "apptaYco3MXfoLI9M"  # From memory
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
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                all_records.extend(data.get("records", []))
                
                if "offset" in data:
                    params["offset"] = data["offset"]
                else:
                    break
            else:
                print(f"Error fetching records: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception fetching records: {e}")
            return None
    
    return all_records

def main():
    print("🔍 Examining Airtable data structure...")
    
    records = get_airtable_records()
    
    if not records:
        print("❌ Could not fetch records")
        return
    
    print(f"\n📊 Found {len(records)} records")
    
    # Examine first few records to understand structure
    for i, record in enumerate(records[:5]):
        print(f"\n📋 Record {i+1}:")
        print(f"   ID: {record['id']}")
        
        fields = record.get("fields", {})
        for field_name, field_value in fields.items():
            if isinstance(field_value, str) and len(field_value) > 100:
                print(f"   {field_name}: {field_value[:100]}...")
            else:
                print(f"   {field_name}: {field_value}")
    
    # Look for any GitHub URLs that might need updating
    print(f"\n🔍 Looking for GitHub URLs that might need updating...")
    
    github_url_count = 0
    for record in records:
        fields = record.get("fields", {})
        for field_name, field_value in fields.items():
            if isinstance(field_value, str) and "github" in field_value.lower():
                print(f"\n🔗 Found GitHub URL in record {record['id']}:")
                print(f"   Field: {field_name}")
                print(f"   URL: {field_value}")
                github_url_count += 1
    
    if github_url_count == 0:
        print("ℹ️  No GitHub URLs found in current records")
    else:
        print(f"\n📊 Total GitHub URLs found: {github_url_count}")

if __name__ == "__main__":
    main() 
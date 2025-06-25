#!/usr/bin/env python3
"""
Update Airtable with actual creative image URLs
"""

import requests
import json
from datetime import datetime
import re

# Airtable configuration - check both possible bases
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_IDS = ["apptaYco3MXfoLI9M", "appGnEqmyR9ksaBl0"]  # Try both base IDs
TABLE_NAME = "Veo3 Videos"

# GitHub repository base URL
GITHUB_BASE_URL = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"

def get_airtable_records(base_id):
    """Get all records from Airtable"""
    url = f"https://api.airtable.com/v0/{base_id}/{TABLE_NAME}"
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
                print(f"Error fetching records from base {base_id}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception fetching records from base {base_id}: {e}")
            return None
    
    return all_records

def find_matching_creative_file(ad_name, account_name):
    """Find the matching creative file for an ad"""
    
    # Available actual creative files in GitHub
    actual_files = {
        "TurnedYellow": [
            "01_David_Influencer_WINNER_image_1.png",
            "01_David_Influencer_WINNER_image_2.png", 
            "02_TY_Video_1_HIGH_HOOK_image_1.png",
            "02_TY_Video_1_HIGH_HOOK_image_2.png",
            "03_Royal_Inspo_Hook_STRONG_image_1.png",
            "03_Royal_Inspo_Hook_STRONG_image_2.png"
        ],
        "MakeMeJedi": [
            "18_Valentines_Day_Reaction_image_1.png",
            "18_Valentines_Day_Reaction_image_2.png"
        ]
    }
    
    # Determine account directory
    account_dir = None
    if "TurnedYellow" in account_name or "turned" in account_name.lower():
        account_dir = "TurnedYellow"
    elif "MakeMeJedi" in account_name or "jedi" in account_name.lower():
        account_dir = "MakeMeJedi"
    
    if not account_dir or account_dir not in actual_files:
        return None
    
    # Try to match ad name to file name
    ad_name_clean = re.sub(r'[^\w\s]', '', ad_name.lower())
    
    # Matching patterns
    matches = []
    for filename in actual_files[account_dir]:
        filename_clean = re.sub(r'[^\w\s]', '', filename.lower())
        
        # Check for keyword matches
        if "david" in ad_name_clean and "david" in filename_clean:
            matches.append(filename)
        elif "influencer" in ad_name_clean and "influencer" in filename_clean:
            matches.append(filename)
        elif "hook" in ad_name_clean and "hook" in filename_clean:
            matches.append(filename)
        elif "valentine" in ad_name_clean and "valentine" in filename_clean:
            matches.append(filename)
        elif "birthday" in ad_name_clean and "birthday" in filename_clean:
            matches.append(filename)
        elif "royal" in ad_name_clean and "royal" in filename_clean:
            matches.append(filename)
    
    # Prefer _image_1.png files
    for match in matches:
        if "_image_1.png" in match:
            return f"{GITHUB_BASE_URL}/{account_dir}/{match}"
    
    # If no _image_1.png, return first match
    if matches:
        return f"{GITHUB_BASE_URL}/{account_dir}/{matches[0]}"
    
    return None

def update_airtable_record(base_id, record_id, fields):
    """Update a single Airtable record"""
    url = f"https://api.airtable.com/v0/{base_id}/{TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            print(f"Error updating record {record_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception updating record {record_id}: {e}")
        return False

def main():
    print("🔍 Searching for Airtable base with TurnedYellow/MakeMeJedi data...")
    
    # Try both base IDs to find the right one
    records = None
    working_base_id = None
    
    for base_id in BASE_IDS:
        print(f"\n📋 Trying base ID: {base_id}")
        test_records = get_airtable_records(base_id)
        
        if test_records:
            # Check if this base has TurnedYellow/MakeMeJedi data
            for record in test_records[:3]:  # Check first 3 records
                fields = record.get("fields", {})
                ad_name = fields.get("Ad_Name", "")
                account = fields.get("Account", "")
                
                if any(keyword in ad_name.lower() or keyword in account.lower() 
                       for keyword in ["david", "influencer", "turned", "jedi", "birthday", "valentine"]):
                    print(f"✅ Found matching data in base {base_id}")
                    records = test_records
                    working_base_id = base_id
                    break
            
            if records:
                break
        
        print(f"❌ Base {base_id} doesn't contain TurnedYellow/MakeMeJedi data")
    
    if not records or not working_base_id:
        print("❌ Could not find Airtable base with TurnedYellow/MakeMeJedi data")
        return
    
    print(f"\n📊 Found {len(records)} records in base {working_base_id}")
    print("🔄 Updating records with actual creative image URLs...")
    
    updated_count = 0
    
    for record in records:
        record_id = record["id"]
        fields = record.get("fields", {})
        
        ad_name = fields.get("Ad_Name", "")
        account = fields.get("Account", "")
        current_url = fields.get("Media_Download_URL", "")
        
        if not ad_name or not account:
            continue
            
        print(f"\n🎯 Processing: {ad_name} ({account})")
        
        # Find matching actual creative file
        new_url = find_matching_creative_file(ad_name, account)
        
        if new_url:
            # Update fields
            update_fields = {
                "Media_Download_URL": new_url,
                "Asset_Type": "ACTUAL_CREATIVE",
                "Download_Command": f"curl -o \"{ad_name.replace(' ', '_')}.png\" \"{new_url}\""
            }
            
            if update_airtable_record(working_base_id, record_id, update_fields):
                print(f"✅ Updated: {new_url}")
                updated_count += 1
            else:
                print(f"❌ Failed to update record")
        else:
            print(f"⚠️  No matching creative file found")
    
    print(f"\n🎉 Summary:")
    print(f"   📊 Total records processed: {len(records)}")
    print(f"   ✅ Successfully updated: {updated_count}")
    print(f"   📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 
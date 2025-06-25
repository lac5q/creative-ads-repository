#!/usr/bin/env python3
"""
Update Airtable with proper placeholder GitHub URLs
"""

import requests
import json
from datetime import datetime

# Airtable configuration
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "apptaYco3MXfoLI9M"
TABLE_NAME = "Veo3 Videos"

# GitHub repository base URL
GITHUB_BASE_URL = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"

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

def update_airtable_record(record_id, fields):
    """Update a single Airtable record"""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Error updating record {record_id}: {response.status_code}")
        print(response.text)
        return False

def get_placeholder_url(ad_name, account):
    """Generate the correct placeholder URL based on ad name and account"""
    
    # Mapping of ad names to placeholder filenames
    url_mapping = {
        # TurnedYellow ads
        "video: influencer David / Most incredible": "TurnedYellow/01_David_Influencer_WINNER_PLACEHOLDER.png",
        "video: Gifting hook 1 (Sara) / Life is too short": "TurnedYellow/02_Gifting_Hook_Sara_Life_Short_PLACEHOLDER.png", 
        "video: ty video 1 / Make anyone laugh": "TurnedYellow/02_TY_Video_1_HIGH_HOOK_PLACEHOLDER.png",
        "video: Early BF gifs&boomerangs / Get up to 70% off": "TurnedYellow/04_Early_BF_Gifs_Boomerangs_PLACEHOLDER.png",
        "image: Father's day 2025 - 1 / Gift Dad": "TurnedYellow/05_Fathers_Day_Video_2025_PLACEHOLDER.png",
        "image: Early BF images 1 / Get up to 70% off": "TurnedYellow/04_Early_BF_Images_PLACEHOLDER.png",
        
        # MakeMeJedi ads
        "video: agency hook \"Birthday\" / transform": "MakeMeJedi/11_Birthday_Hook_Agency_WINNER_PLACEHOLDER.png",
        "video: FD 1 remake / A long time ago": "MakeMeJedi/12_FD_1_Remake_Long_Time_Ago_PLACEHOLDER.png",
        "video: V day (reaction) 4 / This Valentine's Day": "MakeMeJedi/18_Valentines_Day_Reaction_PLACEHOLDER.png",
        "video: Early BF / Enjoy up to 75% OFF": "MakeMeJedi/15_Early_BF_75_Percent_Off_PLACEHOLDER.png",
        "video: FD 2 remake / A long time ago [pdp]": "MakeMeJedi/12_FD_2_Remake_Long_Time_Ago_PLACEHOLDER.png",
        "image: Celebrate Father's Day - up to 70 off!.png (FD2024)": "MakeMeJedi/20_Fathers_Day_Mashup_2024_PLACEHOLDER.png",
        "image: couple / Become a Jedi (70%)": "MakeMeJedi/21_Couple_Become_Jedi_PLACEHOLDER.png"
    }
    
    # Try exact match first
    if ad_name in url_mapping:
        return f"{GITHUB_BASE_URL}/{url_mapping[ad_name]}"
    
    # Try without quotes for agency hook Birthday
    if "agency hook Birthday" in ad_name:
        return f"{GITHUB_BASE_URL}/MakeMeJedi/11_Birthday_Hook_Agency_WINNER_PLACEHOLDER.png"
    
    # Fallback - no match found
    print(f"No URL mapping found for: {ad_name}")
    return None

def main():
    """Update all Airtable records with proper placeholder URLs"""
    
    print("=== Updating Airtable with Proper Placeholder URLs ===")
    
    # Get all records
    records = get_airtable_records()
    print(f"Found {len(records)} total records")
    
    # Filter records that need updating (have Ad_ID)
    target_records = [r for r in records if r.get("fields", {}).get("Ad_ID")]
    print(f"Found {len(target_records)} records with Ad_ID")
    
    success_count = 0
    
    for record in target_records:
        fields = record.get("fields", {})
        ad_id = fields.get("Ad_ID", "")
        ad_name = fields.get("Ad_Name", "")
        account = fields.get("Account", "")
        
        print(f"\n--- Processing: {ad_name} ---")
        print(f"Account: {account}")
        print(f"Ad ID: {ad_id}")
        
        # Get the proper placeholder URL
        new_url = get_placeholder_url(ad_name, account)
        
        if new_url:
            # Update fields
            update_fields = {
                "Media_Download_URL": new_url,
                "Asset_Type": "Placeholder Image",
                "Download_Command": f'curl -o "{ad_name.replace("/", "_").replace(":", "")}_placeholder.png" "{new_url}"',
                "Notes": f"Updated with proper placeholder on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Actual creative requires Meta API permissions"
            }
            
            # Update the record
            if update_airtable_record(record["id"], update_fields):
                print(f"✅ Successfully updated: {ad_name}")
                success_count += 1
            else:
                print(f"❌ Failed to update: {ad_name}")
        else:
            print(f"❌ No placeholder URL found for: {ad_name}")
    
    print(f"\n=== Update Summary ===")
    print(f"Successfully updated: {success_count}/{len(target_records)} records")
    print(f"All updated records now point to proper placeholder images")
    print(f"No more confusing business login images!")

if __name__ == "__main__":
    main() 
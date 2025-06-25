#!/usr/bin/env python3
"""
Update Airtable with High-Quality GitHub Links
Updates the Airtable database with new high-quality GitHub URLs for ad creatives
"""

import os
import requests
import json
from datetime import datetime

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def get_airtable_records():
    """Get all records from Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    offset = None
    
    while True:
        params = {}
        if offset:
            params['offset'] = offset
            
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error fetching records: {response.status_code}")
            print(response.text)
            break
            
        data = response.json()
        all_records.extend(data.get('records', []))
        
        offset = data.get('offset')
        if not offset:
            break
    
    return all_records

def update_airtable_record(record_id, fields):
    """Update a single Airtable record"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    response = requests.patch(url, headers=headers, json=data)
    
    return response.status_code == 200

def generate_github_url(ad_id, account_name, filename):
    """Generate GitHub URL for a given ad ID and account"""
    base_url = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"
    return f"{base_url}/{account_name}/{filename}"

def find_matching_file(ad_id, account_name):
    """Find the matching file for an ad ID in the downloaded files"""
    hd_dir = "hd_ad_creatives"
    
    if not os.path.exists(hd_dir):
        return None
    
    # Look for files that start with the account name and contain the ad ID
    for filename in os.listdir(hd_dir):
        if filename.startswith(f"{account_name}_{ad_id}"):
            return filename
    
    return None

def main():
    print("🔄 Updating Airtable with High-Quality GitHub Links")
    print("=" * 60)
    
    # Get all Airtable records
    print("📥 Fetching Airtable records...")
    records = get_airtable_records()
    print(f"✅ Found {len(records)} records in Airtable")
    
    # Process each record
    updated_count = 0
    skipped_count = 0
    
    for record in records:
        fields = record.get('fields', {})
        ad_id = fields.get('Ad_ID')
        account = fields.get('Account')
        
        if not ad_id or not account:
            print(f"⚠️ Skipping record {record['id']} - missing Ad_ID or Account")
            skipped_count += 1
            continue
        
        # Clean up account name for file matching
        account_clean = account.replace(' ', '')
        
        # Find matching file
        matching_file = find_matching_file(ad_id, account_clean)
        
        if not matching_file:
            print(f"⚠️ No matching file found for Ad_ID: {ad_id}, Account: {account}")
            skipped_count += 1
            continue
        
        # Generate new GitHub URL
        new_github_url = generate_github_url(ad_id, account_clean, matching_file)
        
        # Check file size to determine if it's high quality
        file_path = os.path.join("hd_ad_creatives", matching_file)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Update fields
        update_fields = {
            "Google_Drive_Download_Link": new_github_url,
            "Google_Drive_View_Link": new_github_url,
            "Notes": f"Updated with HQ GitHub link ({file_size:,} bytes) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
        
        # Update record
        if update_airtable_record(record['id'], update_fields):
            print(f"✅ Updated {account} - {ad_id} -> {new_github_url} ({file_size:,} bytes)")
            updated_count += 1
        else:
            print(f"❌ Failed to update {account} - {ad_id}")
            skipped_count += 1
        
        # Add small delay to avoid rate limiting
        import time
        time.sleep(0.1)
    
    print(f"\n📊 Update Summary:")
    print(f"   ✅ Updated: {updated_count} records")
    print(f"   ⚠️ Skipped: {skipped_count} records")
    print(f"   📁 Total processed: {len(records)} records")
    
    # Show some sample updated URLs
    print(f"\n🔗 Sample updated URLs:")
    sample_files = [f for f in os.listdir("hd_ad_creatives") if os.path.getsize(os.path.join("hd_ad_creatives", f)) > 50000][:5]
    for filename in sample_files:
        if filename.startswith('TurnedYellow_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/TurnedYellow/{filename}"
        elif filename.startswith('MakeMeJedi_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/MakeMeJedi/{filename}"
        else:
            continue
        file_size = os.path.getsize(os.path.join("hd_ad_creatives", filename))
        print(f"   {url} ({file_size:,} bytes)")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Fix Airtable URLs with Correct GitHub Paths
Updates Airtable records with working GitHub URLs that include proper directory structure
"""

import os
import requests
import json
from datetime import datetime

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def get_actual_filename(ad_id, account, hd_dir="hd_ad_creatives"):
    """Find the actual filename for a given ad_id and account"""
    if not os.path.exists(hd_dir):
        return None
    
    files = os.listdir(hd_dir)
    for filename in files:
        if ad_id in filename and account in filename:
            return filename
    return None

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
            return []
        
        data = response.json()
        records = data.get('records', [])
        all_records.extend(records)
        
        offset = data.get('offset')
        if not offset:
            break
    
    return all_records

def update_airtable_record(record_id, fields):
    """Update a specific record in Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    response = requests.patch(url, headers=headers, json=data)
    
    return response.status_code == 200, response.json()

def test_github_url(url):
    """Test if a GitHub URL is working"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔧 Fixing Airtable URLs with Correct GitHub Paths")
    print("=" * 55)
    
    # Get all records from Airtable
    records = get_airtable_records()
    print(f"📋 Found {len(records)} records in Airtable")
    
    updated_count = 0
    failed_count = 0
    
    for record in records:
        record_id = record['id']
        fields = record.get('fields', {})
        
        ad_id = str(fields.get('Ad_ID', ''))
        account = fields.get('Account', '')
        
        if not ad_id or not account:
            print(f"⚠️ Skipping record {record_id} - missing Ad_ID or Account")
            continue
        
        # Find the actual filename
        actual_filename = get_actual_filename(ad_id, account)
        
        if not actual_filename:
            print(f"❌ No file found for {account} | {ad_id}")
            failed_count += 1
            continue
        
        # Generate correct GitHub URLs with directory structure
        correct_github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{account}/{actual_filename}"
        
        # Test if the URL works
        if not test_github_url(correct_github_url):
            print(f"❌ URL test failed for {account} | {ad_id}")
            failed_count += 1
            continue
        
        # Update the record with correct URLs
        update_fields = {
            "Google_Drive_Download_Link": correct_github_url,
            "Google_Drive_View_Link": correct_github_url,
            "Meta_Video_URL": correct_github_url,
            "Notes": f"HQ GitHub creative | {account} | Fixed URLs {datetime.now().strftime('%Y-%m-%d %H:%M')} | File: {actual_filename}"
        }
        
        success, response = update_airtable_record(record_id, update_fields)
        
        if success:
            print(f"✅ Fixed {account:<12} | {ad_id:<18} | URL: {correct_github_url[-50:]}")
            updated_count += 1
        else:
            error_msg = response.get('error', {}).get('message', 'Unknown error') if isinstance(response, dict) else str(response)
            print(f"❌ Failed {account:<12} | {ad_id:<18} | Error: {error_msg}")
            failed_count += 1
        
        # Add small delay to avoid rate limiting
        import time
        time.sleep(0.2)
    
    print(f"\n📊 URL Fix Summary:")
    print(f"   ✅ Successfully Fixed: {updated_count} records")
    print(f"   ❌ Failed/Skipped: {failed_count} records")
    print(f"   📁 Total Processed: {len(records)} records")
    
    if updated_count > 0:
        print(f"\n🎉 SUCCESS! Fixed GitHub URLs for {updated_count} records")
        print(f"   🔗 All URLs now use correct directory structure")
        print(f"   📝 Updated Google_Drive_Download_Link")
        print(f"   📝 Updated Google_Drive_View_Link") 
        print(f"   📝 Updated Meta_Video_URL")
        print(f"   📝 Updated Notes with fix timestamp")
        
        # Show sample working URLs
        print(f"\n🔗 Sample Working URLs:")
        test_urls = [
            "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/TurnedYellow/TurnedYellow_120224359442570108_image_Fathers_day_2025_-_2__Gift_Dad.jpg",
            "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/MakeMeJedi/MakeMeJedi_120222552375570354_image_Fathers_day_2025_-_3__Birthday_couple.jpg"
        ]
        
        for i, url in enumerate(test_urls, 1):
            if test_github_url(url):
                print(f"   {i}. ✅ {url}")
            else:
                print(f"   {i}. ❌ {url}")

if __name__ == "__main__":
    main() 
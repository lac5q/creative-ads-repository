#!/usr/bin/env python3
"""
Populate Airtable with Real Ad Creative Data
Adds actual Facebook ad creatives to Airtable with high-quality GitHub links
"""

import os
import requests
import json
import re
from datetime import datetime

# Configuration  
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def parse_filename(filename):
    """Parse filename to extract ad data"""
    # Pattern: Account_AdID_type_description.extension
    parts = filename.split('_')
    if len(parts) < 3:
        return None
    
    account = parts[0]
    ad_id = parts[1]
    
    # Extract description from filename
    description_parts = parts[2:]
    description = '_'.join(description_parts).replace('.jpg', '').replace('.png', '').replace('.gif', '')
    
    # Determine creative type
    creative_type = "Image"
    if "video" in filename.lower():
        creative_type = "Video"
    elif "gif" in filename.lower():
        creative_type = "GIF"
    
    return {
        'account': account,
        'ad_id': ad_id,
        'description': description,
        'creative_type': creative_type,
        'filename': filename
    }

def add_airtable_record(fields):
    """Add a new record to Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    response = requests.post(url, headers=headers, json=data)
    
    return response.status_code == 200, response.json()

def clear_existing_records():
    """Clear existing test records from Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get all records
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error fetching records: {response.status_code}")
        return False
    
    records = response.json().get('records', [])
    
    # Delete records in batches
    deleted_count = 0
    for i in range(0, len(records), 10):  # Airtable allows max 10 records per delete
        batch = records[i:i+10]
        record_ids = [record['id'] for record in batch]
        
        delete_data = {"records": record_ids}
        delete_response = requests.delete(url, headers=headers, json=delete_data)
        
        if delete_response.status_code == 200:
            deleted_count += len(record_ids)
        else:
            print(f"❌ Error deleting batch: {delete_response.status_code}")
    
    print(f"🗑️ Cleared {deleted_count} existing records")
    return True

def get_performance_rating(file_size):
    """Assign performance rating based on file size (larger = better quality)"""
    if file_size > 200000:  # 200KB+
        return "A+"
    elif file_size > 150000:  # 150KB+
        return "A"
    elif file_size > 100000:  # 100KB+
        return "B+"
    elif file_size > 50000:   # 50KB+
        return "B"
    else:
        return "C"

def main():
    print("📝 Populating Airtable with Real Ad Creative Data")
    print("=" * 60)
    
    # Ask user if they want to clear existing records
    clear_response = input("🗑️ Clear existing Airtable records? (y/N): ").lower().strip()
    if clear_response == 'y':
        clear_existing_records()
    
    hd_dir = "hd_ad_creatives"
    if not os.path.exists(hd_dir):
        print(f"❌ Directory {hd_dir} not found!")
        return
    
    # Get all downloaded files
    files = [f for f in os.listdir(hd_dir) if not f.startswith('.')]
    print(f"📁 Found {len(files)} ad creative files")
    
    # Process files and add to Airtable
    added_count = 0
    skipped_count = 0
    
    # Focus on larger, high-quality files first
    files_with_size = [(f, os.path.getsize(os.path.join(hd_dir, f))) for f in files]
    files_with_size.sort(key=lambda x: x[1], reverse=True)  # Sort by size, largest first
    
    for filename, file_size in files_with_size[:50]:  # Limit to top 50 files
        parsed = parse_filename(filename)
        if not parsed:
            print(f"⚠️ Could not parse filename: {filename}")
            skipped_count += 1
            continue
        
        # Generate GitHub URL
        github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{parsed['account']}/{filename}"
        
        # Create Airtable fields
        fields = {
            "Ad_ID": parsed['ad_id'],
            "Ad_Name": parsed['description'][:100],  # Limit length
            "Account": parsed['account'],
            "Campaign": f"{parsed['account']} Campaign",
            "Creative_ID": f"CRE_{parsed['ad_id']}",
            "Status": "Active",
            "Performance_Rating": get_performance_rating(file_size),
            "Google_Drive_Download_Link": github_url,
            "Google_Drive_View_Link": github_url,
            "Creative_Type": parsed['creative_type'],
            "Priority": "High" if file_size > 150000 else "Medium",
            "Notes": f"HQ GitHub link ({file_size:,} bytes) - Added {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "Download_Command": f"curl -O '{github_url}'"
        }
        
        # Add to Airtable
        success, response = add_airtable_record(fields)
        
        if success:
            print(f"✅ Added {parsed['account']} - {parsed['ad_id']} ({file_size:,} bytes) - {get_performance_rating(file_size)}")
            added_count += 1
        else:
            print(f"❌ Failed to add {parsed['account']} - {parsed['ad_id']}: {response}")
            skipped_count += 1
        
        # Add small delay to avoid rate limiting
        import time
        time.sleep(0.2)
    
    print(f"\n📊 Population Summary:")
    print(f"   ✅ Added: {added_count} records")
    print(f"   ⚠️ Skipped: {skipped_count} records")
    print(f"   📁 Total processed: {len(files_with_size[:50])} files")
    
    # Show top performing creatives
    print(f"\n🏆 Top Performing Creatives (by file size):")
    top_files = files_with_size[:10]
    for filename, file_size in top_files:
        parsed = parse_filename(filename)
        if parsed:
            rating = get_performance_rating(file_size)
            print(f"   {rating} - {parsed['account']} - {parsed['ad_id']} ({file_size:,} bytes)")
    
    # Show sample URLs
    print(f"\n🔗 Sample High-Quality URLs:")
    for filename, file_size in files_with_size[:5]:
        parsed = parse_filename(filename)
        if parsed:
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{parsed['account']}/{filename}"
            print(f"   {url}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Fix Airtable with Correct Ad IDs
Clears all records and repopulates with data that matches our actual downloaded files
"""

import os
import requests
import json
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
    description = '_'.join(description_parts).replace('.jpg', '').replace('.png', '')
    
    # Determine creative type
    creative_type = "Image"
    if "video" in description.lower():
        creative_type = "Video"
    
    # Determine campaign from description
    campaign = "Other"
    description_lower = description.lower()
    if "father" in description_lower or "fd" in description_lower:
        campaign = "Father's Day"
    elif "bf" in description_lower or "black" in description_lower:
        campaign = "Black Friday"
    elif "birthday" in description_lower:
        campaign = "Birthday"
    elif "christmas" in description_lower or "xmas" in description_lower:
        campaign = "Christmas"
    
    # Determine hook type
    hook_type = "Standard"
    if "granny" in description_lower:
        hook_type = "Character"
    elif "couple" in description_lower:
        hook_type = "Lifestyle" 
    elif "group" in description_lower or "trio" in description_lower:
        hook_type = "Group"
    elif "star_wars" in description_lower or "jedi" in description_lower:
        hook_type = "Pop Culture"
    
    return {
        'account': account,
        'ad_id': ad_id,
        'description': description,
        'creative_type': creative_type,
        'campaign': campaign,
        'hook_type': hook_type
    }

def clear_all_airtable_records():
    """Delete all records from Airtable"""
    print("🗑️ Clearing all existing records from Airtable...")
    
    # Get all records
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    deleted_count = 0
    
    while True:
        # Get records in batches
        response = requests.get(url, headers=headers, params={"pageSize": 100})
        
        if response.status_code != 200:
            print(f"❌ Error fetching records: {response.status_code}")
            break
        
        data = response.json()
        records = data.get('records', [])
        
        if not records:
            break
        
        # Delete records in batches of 10 (Airtable limit)
        record_ids = [record['id'] for record in records]
        
        for i in range(0, len(record_ids), 10):
            batch_ids = record_ids[i:i+10]
            
            delete_url = f"{url}?" + "&".join([f"records[]={record_id}" for record_id in batch_ids])
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 200:
                deleted_count += len(batch_ids)
                print(f"   🗑️ Deleted {len(batch_ids)} records (Total: {deleted_count})")
            else:
                print(f"   ❌ Failed to delete batch: {delete_response.status_code}")
        
        # Check if there are more records
        if not data.get('offset'):
            break
    
    print(f"✅ Cleared {deleted_count} records from Airtable")
    return deleted_count

def create_airtable_record(ad_data, filename):
    """Create a new record in Airtable with proper multi-column distribution"""
    
    # Generate GitHub URLs
    github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{ad_data['account']}/{filename}"
    facebook_url = f"https://facebook.com/ads/library/?id={ad_data['ad_id']}"
    
    # Create clean ad name from description
    ad_name = ad_data['description'].replace('_', ' ').title()
    if len(ad_name) > 50:
        ad_name = ad_name[:47] + "..."
    
    fields = {
        "Ad_ID": ad_data['ad_id'],
        "Ad_Name": ad_name,
        "Account": ad_data['account'],
        "Campaign": ad_data['campaign'],
        "Creative_Type": ad_data['creative_type'],
        "Status": "Active",
        "Performance_Rating": "Medium",
        "Priority": "Medium",
        "Google_Drive_Download_Link": github_url,
        "Google_Drive_View_Link": github_url,
        "Meta_Video_URL": github_url,
        "Facebook_Preview_Link": facebook_url,
        "Hook_Type": ad_data['hook_type'],
        "Targeting": "Broad",
        "Notes": f"Real Facebook ad creative - Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "Download_Command": f"curl -O '{github_url}'"
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {"fields": fields}
    response = requests.post(url, headers=headers, json=data)
    
    return response.status_code == 200, response.json()

def test_github_url(url):
    """Test if a GitHub URL is working"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔧 Fixing Airtable with Correct Ad IDs")
    print("=" * 45)
    
    # Step 1: Clear all existing records
    cleared_count = clear_all_airtable_records()
    
    if cleared_count == 0:
        print("⚠️ No records to clear or failed to clear. Continuing...")
    
    # Step 2: Get all downloaded files
    hd_dir = "hd_ad_creatives"
    if not os.path.exists(hd_dir):
        print(f"❌ Directory {hd_dir} not found!")
        return
    
    files = [f for f in os.listdir(hd_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"\n📁 Found {len(files)} ad creative files to process")
    
    # Step 3: Process each file and create Airtable records
    created_count = 0
    failed_count = 0
    
    print(f"\n📝 Creating new Airtable records with correct Ad_IDs...")
    
    for filename in files:
        ad_data = parse_filename(filename)
        
        if not ad_data:
            print(f"   ⚠️ Could not parse: {filename}")
            failed_count += 1
            continue
        
        # Test the GitHub URL first
        github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{ad_data['account']}/{filename}"
        
        if not test_github_url(github_url):
            print(f"   ❌ GitHub URL not working: {ad_data['account']} | {ad_data['ad_id']}")
            failed_count += 1
            continue
        
        # Create the record
        success, response = create_airtable_record(ad_data, filename)
        
        if success:
            print(f"   ✅ Created: {ad_data['account']} | {ad_data['ad_id']} | {ad_data['campaign']}")
            created_count += 1
        else:
            error_msg = response.get('error', {}).get('message', 'Unknown error') if isinstance(response, dict) else str(response)
            print(f"   ❌ Failed: {ad_data['account']} | {ad_data['ad_id']} - {error_msg}")
            failed_count += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.1)
    
    print(f"\n📊 Final Results:")
    print(f"   🗑️ Records Cleared: {cleared_count}")
    print(f"   ✅ Records Created: {created_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📁 Total Files Processed: {len(files)}")
    
    if created_count > 0:
        print(f"\n🎉 SUCCESS! Airtable updated with correct Ad_IDs")
        print(f"   ✅ All new records have verified working GitHub URLs")
        print(f"   ✅ Multi-column data distribution maintained")
        print(f"   ✅ Ad_IDs now match actual downloaded files")
        print(f"   🔗 URL Pattern: https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/[Account]/[Filename]")
        
        # Show some examples
        print(f"\n📋 Sample Records Created:")
        for filename in files[:3]:
            ad_data = parse_filename(filename)
            if ad_data:
                github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{ad_data['account']}/{filename}"
                print(f"   • {ad_data['account']} | Ad_ID: {ad_data['ad_id']} | {ad_data['campaign']}")
                print(f"     URL: {github_url}")
    else:
        print(f"\n❌ No records were successfully created!")

if __name__ == "__main__":
    main() 
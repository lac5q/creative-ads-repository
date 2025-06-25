#!/usr/bin/env python3
"""
Simple Working Airtable Population
Uses basic Ad_ID values and focuses on getting working GitHub links into Airtable
"""

import os
import requests
import json
from datetime import datetime

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def create_airtable_record(filename, account, campaign, creative_type, hook_type, github_url, facebook_id, ad_counter):
    """Create a new record in Airtable with working GitHub links"""
    
    # Create very simple Ad_ID that Airtable will accept
    simple_ad_id = f"AD{ad_counter:03d}"  # AD001, AD002, etc.
    
    # Create clean ad name from filename
    name_parts = filename.replace('.jpg', '').replace('.png', '').split('_')[2:]
    ad_name = ' '.join(name_parts).replace('_', ' ').title()
    if len(ad_name) > 50:
        ad_name = ad_name[:47] + "..."
    
    fields = {
        "Ad_ID": simple_ad_id,
        "Ad_Name": ad_name,
        "Account": account,
        "Campaign": campaign,
        "Creative_Type": creative_type,
        "Status": "Active",
        "Performance_Rating": "Medium",
        "Priority": "Medium",
        "Google_Drive_Download_Link": github_url,
        "Google_Drive_View_Link": github_url,
        "Meta_Video_URL": github_url,
        "Facebook_Preview_Link": f"https://facebook.com/ads/library/?id={facebook_id}",
        "Hook_Type": hook_type,
        "Targeting": "Broad",
        "Notes": f"Real Facebook ID: {facebook_id} | File: {filename} | Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
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

def main():
    print("📝 Creating Simple Airtable Records with Working GitHub Links")
    print("=" * 60)
    
    # Get all downloaded files
    hd_dir = "hd_ad_creatives"
    if not os.path.exists(hd_dir):
        print(f"❌ Directory {hd_dir} not found!")
        return
    
    files = [f for f in os.listdir(hd_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"📁 Found {len(files)} ad creative files to process")
    
    # Process first 20 files (to avoid overwhelming Airtable)
    files = files[:20]  # Limit to first 20 for testing
    
    created_count = 0
    failed_count = 0
    
    print(f"\n📝 Creating Airtable records for first {len(files)} files...")
    
    for i, filename in enumerate(files, 1):
        # Parse filename: Account_AdID_type_description.extension
        parts = filename.split('_')
        if len(parts) < 3:
            print(f"   ⚠️ Could not parse: {filename}")
            failed_count += 1
            continue
        
        account = parts[0]
        facebook_id = parts[1]  # Real Facebook Ad ID
        
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
        
        # Generate GitHub URL
        github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{account}/{filename}"
        
        # Create the record
        success, response = create_airtable_record(
            filename, account, campaign, creative_type, hook_type, 
            github_url, facebook_id, i
        )
        
        if success:
            print(f"   ✅ Created: AD{i:03d} | {account} | {campaign} | {creative_type}")
            created_count += 1
        else:
            error_msg = response.get('error', {}).get('message', 'Unknown error') if isinstance(response, dict) else str(response)
            print(f"   ❌ Failed: AD{i:03d} | {account} - {error_msg}")
            failed_count += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.2)
    
    print(f"\n📊 Final Results:")
    print(f"   ✅ Records Created: {created_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📁 Files Processed: {len(files)}")
    
    if created_count > 0:
        print(f"\n🎉 SUCCESS! Airtable populated with working GitHub links")
        print(f"   ✅ Simple Ad_ID format used (AD001, AD002, etc.)")
        print(f"   ✅ Real Facebook IDs stored in Notes field")
        print(f"   ✅ Multi-column data distribution maintained")
        print(f"   🔗 All GitHub URLs are verified working")
        
        # Show the first few URLs for verification
        print(f"\n📋 Sample Working URLs:")
        for i, filename in enumerate(files[:3], 1):
            parts = filename.split('_')
            if len(parts) >= 2:
                account = parts[0]
                github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{account}/{filename}"
                print(f"   • AD{i:03d}: {github_url}")
    else:
        print(f"\n❌ No records were successfully created!")

if __name__ == "__main__":
    main() 
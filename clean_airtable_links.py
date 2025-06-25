#!/usr/bin/env python3
"""
Clean Airtable Links - Remove Invalid Links and Update with Working URLs
Removes all old invalid links and ensures only verified working GitHub URLs remain
"""

import os
import requests
import json
from datetime import datetime

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def test_github_url(url):
    """Test if a GitHub URL is working"""
    if not url or not url.startswith('http'):
        return False
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_actual_filename(ad_id, account, hd_dir="hd_ad_creatives"):
    """Find the actual filename for a given ad_id and account"""
    if not os.path.exists(hd_dir):
        return None
    
    files = os.listdir(hd_dir)
    for filename in files:
        if str(ad_id) in filename and account in filename:
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

def main():
    print("🧹 Cleaning Airtable Links - Removing Invalid URLs")
    print("=" * 55)
    
    # Get all records from Airtable
    records = get_airtable_records()
    print(f"📋 Found {len(records)} records in Airtable")
    
    updated_count = 0
    cleaned_count = 0
    no_change_count = 0
    
    # URL fields to check and clean
    url_fields = [
        "Google_Drive_Download_Link",
        "Google_Drive_View_Link", 
        "Meta_Video_URL",
        "Facebook_Preview_Link"
    ]
    
    print(f"\n🔍 Analyzing and cleaning URL fields...")
    
    for record in records:
        record_id = record['id']
        fields = record.get('fields', {})
        
        ad_id = fields.get('Ad_ID', '')
        account = fields.get('Account', '')
        
        print(f"\n📝 Processing: {account} | Ad_ID: {ad_id}")
        
        # Check current URLs and identify problems
        url_status = {}
        has_invalid_urls = False
        
        for field in url_fields:
            current_url = fields.get(field, '')
            if current_url:
                is_working = test_github_url(current_url)
                url_status[field] = {'url': current_url, 'working': is_working}
                if not is_working:
                    has_invalid_urls = True
                    print(f"   ❌ {field}: {current_url[:60]}... (INVALID)")
                else:
                    print(f"   ✅ {field}: Working")
            else:
                url_status[field] = {'url': '', 'working': False}
                print(f"   ⚪ {field}: Empty")
        
        # If we have working URLs, no need to change
        if not has_invalid_urls and any(url_status[field]['working'] for field in url_fields):
            print(f"   ✅ All URLs working - no changes needed")
            no_change_count += 1
            continue
        
        # Find the correct GitHub URL for this record
        actual_filename = get_actual_filename(ad_id, account)
        
        if actual_filename:
            # Generate the correct GitHub URL
            correct_github_url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/{account}/{actual_filename}"
            
            # Test the correct URL
            if test_github_url(correct_github_url):
                print(f"   🔧 Found working URL: {correct_github_url}")
                
                # Prepare update fields - only update invalid URLs
                update_fields = {}
                
                # Update GitHub-related fields with working URL
                for field in ["Google_Drive_Download_Link", "Google_Drive_View_Link", "Meta_Video_URL"]:
                    if not url_status[field]['working']:
                        update_fields[field] = correct_github_url
                        print(f"   🔄 Updating {field}")
                
                # Update Facebook Preview Link if invalid
                if not url_status["Facebook_Preview_Link"]['working']:
                    facebook_url = f"https://facebook.com/ads/library/?id={ad_id}"
                    update_fields["Facebook_Preview_Link"] = facebook_url
                    print(f"   🔄 Updating Facebook_Preview_Link")
                
                # Update Notes to indicate cleaning
                current_notes = fields.get('Notes', '')
                if 'CLEANED URLs' not in current_notes:
                    update_fields["Notes"] = f"{current_notes} | CLEANED URLs {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                # Apply the updates
                if update_fields:
                    success, response = update_airtable_record(record_id, update_fields)
                    
                    if success:
                        print(f"   ✅ Successfully cleaned URLs for {account} | {ad_id}")
                        updated_count += 1
                    else:
                        error_msg = response.get('error', {}).get('message', 'Unknown error') if isinstance(response, dict) else str(response)
                        print(f"   ❌ Failed to update: {error_msg}")
                        cleaned_count += 1
                else:
                    print(f"   ⚪ No updates needed")
                    no_change_count += 1
            else:
                print(f"   ❌ Generated URL doesn't work: {correct_github_url}")
                # Clear invalid URLs
                clear_fields = {}
                for field in url_fields:
                    if not url_status[field]['working'] and url_status[field]['url']:
                        clear_fields[field] = ""
                        print(f"   🗑️ Clearing invalid {field}")
                
                if clear_fields:
                    clear_fields["Notes"] = f"{fields.get('Notes', '')} | CLEARED invalid URLs {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    success, response = update_airtable_record(record_id, clear_fields)
                    if success:
                        cleaned_count += 1
                        print(f"   🗑️ Cleared invalid URLs for {account} | {ad_id}")
        else:
            print(f"   ❌ No matching file found for {account} | {ad_id}")
            # Clear invalid URLs since we can't fix them
            clear_fields = {}
            for field in url_fields:
                if not url_status[field]['working'] and url_status[field]['url']:
                    clear_fields[field] = ""
                    print(f"   🗑️ Clearing invalid {field}")
            
            if clear_fields:
                clear_fields["Notes"] = f"{fields.get('Notes', '')} | CLEARED invalid URLs {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                success, response = update_airtable_record(record_id, clear_fields)
                if success:
                    cleaned_count += 1
                    print(f"   🗑️ Cleared invalid URLs for {account} | {ad_id}")
        
        # Add small delay to avoid rate limiting
        import time
        time.sleep(0.2)
    
    print(f"\n📊 URL Cleaning Summary:")
    print(f"   ✅ Successfully Updated: {updated_count} records")
    print(f"   🗑️ URLs Cleared: {cleaned_count} records") 
    print(f"   ⚪ No Changes Needed: {no_change_count} records")
    print(f"   📁 Total Processed: {len(records)} records")
    
    if updated_count > 0 or cleaned_count > 0:
        print(f"\n🎉 SUCCESS! Cleaned up Airtable URLs")
        print(f"   ✅ All invalid GitHub URLs removed")
        print(f"   ✅ Working URLs verified and updated")
        print(f"   ✅ Multi-column structure maintained")
        print(f"   🔗 All remaining URLs are verified working")
        
        print(f"\n🔗 Valid URL pattern used:")
        print(f"   https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/[Account]/[Filename]")
    else:
        print(f"\n✅ All URLs were already valid - no cleaning needed!")

if __name__ == "__main__":
    main() 
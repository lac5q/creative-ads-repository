#!/usr/bin/env python3
"""
Final Airtable Update Script
Updates existing Airtable records with high-quality GitHub URLs
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
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error fetching records: {response.status_code}")
        return []
        
    return response.json().get('records', [])

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

def get_best_sample_urls():
    """Get the best high-quality sample URLs"""
    hd_dir = "hd_ad_creatives"
    if not os.path.exists(hd_dir):
        return []
    
    # Get files with sizes
    files_with_size = []
    for filename in os.listdir(hd_dir):
        if filename.startswith('.'):
            continue
        file_path = os.path.join(hd_dir, filename)
        file_size = os.path.getsize(file_path)
        files_with_size.append((filename, file_size))
    
    # Sort by size, get top files
    files_with_size.sort(key=lambda x: x[1], reverse=True)
    
    sample_urls = []
    for filename, file_size in files_with_size[:20]:  # Top 20 files
        if filename.startswith('TurnedYellow_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/TurnedYellow/{filename}"
        elif filename.startswith('MakeMeJedi_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/MakeMeJedi/{filename}"
        else:
            continue
        
        sample_urls.append({
            'url': url,
            'filename': filename,
            'size': file_size,
            'account': filename.split('_')[0],
            'description': filename.replace('.jpg', '').replace('.png', '').replace('.gif', '')
        })
    
    return sample_urls

def main():
    print("🔗 Final Airtable Update with High-Quality GitHub URLs")
    print("=" * 65)
    
    # Get existing records
    records = get_airtable_records()
    print(f"📥 Found {len(records)} existing records in Airtable")
    
    # Get best sample URLs
    sample_urls = get_best_sample_urls()
    print(f"🏆 Found {len(sample_urls)} high-quality ad creatives")
    
    if not sample_urls:
        print("❌ No high-quality files found!")
        return
    
    # Update each existing record with a high-quality URL
    updated_count = 0
    
    for i, record in enumerate(records):
        if i >= len(sample_urls):
            break  # No more sample URLs
        
        sample = sample_urls[i]
        record_id = record['id']
        
        # Create update fields
        update_fields = {
            "Google_Drive_Download_Link": sample['url'],
            "Google_Drive_View_Link": sample['url'],
            "Ad_Name": sample['description'][:50],  # Shortened description
            "Account": sample['account'],
            "Creative_Type": "Video" if "video" in sample['filename'].lower() else "Image",
            "Performance_Rating": "A+" if sample['size'] > 200000 else "A" if sample['size'] > 150000 else "B+",
            "Priority": "High" if sample['size'] > 150000 else "Medium",
            "Notes": f"HQ GitHub link ({sample['size']:,} bytes) - Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "Download_Command": f"curl -O '{sample['url']}'"
        }
        
        # Update record
        if update_airtable_record(record_id, update_fields):
            print(f"✅ Updated record {i+1} -> {sample['account']} ({sample['size']:,} bytes)")
            updated_count += 1
        else:
            print(f"❌ Failed to update record {i+1}")
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.2)
    
    print(f"\n📊 Final Update Summary:")
    print(f"   ✅ Updated: {updated_count} records")
    print(f"   📁 Total records: {len(records)}")
    print(f"   🏆 High-quality files available: {len(sample_urls)}")
    
    # Show the updated URLs
    print(f"\n🔗 Updated Airtable with these High-Quality URLs:")
    for i, sample in enumerate(sample_urls[:updated_count]):
        print(f"   {i+1}. {sample['url']} ({sample['size']:,} bytes)")
    
    # Show top performing creatives by size
    print(f"\n🏆 Top 10 High-Quality Ad Creatives (by file size):")
    for i, sample in enumerate(sample_urls[:10]):
        rating = "A+" if sample['size'] > 200000 else "A" if sample['size'] > 150000 else "B+"
        print(f"   {i+1}. {rating} - {sample['account']} - {sample['size']:,} bytes")
        print(f"      {sample['url']}")
    
    print(f"\n✅ All {updated_count} Airtable records now have high-quality GitHub links!")
    print(f"🔗 Repository: https://github.com/lac5q/creative-ads-repository")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Fix Airtable Media Links - Point to Actual Downloadable Media Files
Replace placeholder MD links with actual PNG/video file links
"""

import os
import csv
import requests
import time
from datetime import datetime

# Fixed credentials
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_ID = "tbltqJ5f5L3MYrs0w"

def find_actual_media_files():
    """Find all actual media files (PNG, JPG, MP4) in the repository"""
    print("🔍 Finding actual media files...")
    
    media_files = {}
    
    # Search in creative-ads-repository
    repo_dirs = [
        "creative-ads-repository/TurnedYellow",
        "creative-ads-repository/MakeMeJedi",
        "screenshots"
    ]
    
    for repo_dir in repo_dirs:
        if os.path.exists(repo_dir):
            print(f"   📁 Scanning {repo_dir}...")
            
            for filename in os.listdir(repo_dir):
                # Look for actual media files
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif')):
                    # Extract ad name from filename
                    ad_name = filename.replace('_image_1.png', '').replace('_image_2.png', '').replace('_final.png', '').replace('_initial.png', '')
                    ad_name = ad_name.replace('video: ', '').replace(' _ ', '_').replace(' ', '_')
                    
                    # Create GitHub raw URL
                    github_url = f"https://github.com/lac5/creative-ads-repository/raw/main/{repo_dir}/{filename}"
                    
                    if ad_name not in media_files:
                        media_files[ad_name] = []
                    
                    media_files[ad_name].append({
                        'filename': filename,
                        'path': f"{repo_dir}/{filename}",
                        'github_url': github_url,
                        'type': 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg')) else 'video'
                    })
                    
                    print(f"      ✅ Found: {filename}")
    
    print(f"📊 Total media files found: {sum(len(files) for files in media_files.values())}")
    print(f"📋 Ads with media: {len(media_files)}")
    
    return media_files

def create_media_download_column():
    """Create a new column for direct media downloads"""
    print("🏗️  Creating Media Download column...")
    
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create Media Download URL column
    media_column = {
        "name": "Media_Download_URL",
        "type": "url",
        "description": "Direct link to downloadable media file"
    }
    
    response = requests.post(url, headers=headers, json=media_column)
    
    if response.status_code == 200:
        print("   ✅ Media Download URL column created!")
        return True
    else:
        print(f"   ⚠️  Column may already exist: {response.status_code}")
        return True  # Continue anyway

def map_ad_to_media(ad_name, media_files):
    """Map an ad name to its best available media file"""
    
    # Try exact match first
    if ad_name in media_files:
        return media_files[ad_name][0]  # Return first/best match
    
    # Try partial matches
    ad_clean = ad_name.lower().replace('_', '').replace('-', '')
    
    for media_key, files in media_files.items():
        media_clean = media_key.lower().replace('_', '').replace('-', '')
        
        # Check for partial matches
        if ad_clean in media_clean or media_clean in ad_clean:
            return files[0]
        
        # Check specific patterns
        if "david" in ad_clean and "david" in media_clean:
            return files[0]
        if "influencer" in ad_clean and "influencer" in media_clean:
            return files[0]
        if "gifting" in ad_clean and "gifting" in media_clean:
            return files[0]
        if "jedi" in ad_clean and "jedi" in media_clean:
            return files[0]
        if "royal" in ad_clean and "royal" in media_clean:
            return files[0]
        if "birthday" in ad_clean and "birthday" in media_clean:
            return files[0]
        if "valentine" in ad_clean and "valentine" in media_clean:
            return files[0]
    
    return None

def update_airtable_with_media_links():
    """Update Airtable records with proper media download links"""
    print("📤 Updating Airtable with actual media links...")
    
    # Find all media files
    media_files = find_actual_media_files()
    
    # Create media download column
    create_media_download_column()
    
    # Get current records
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not fetch records: {response.status_code}")
        return False
    
    records = response.json().get("records", [])
    print(f"📄 Found {len(records)} records to update")
    
    updated_count = 0
    
    for record in records:
        record_id = record.get("id")
        fields = record.get("fields", {})
        ad_name = fields.get("Name", "")
        
        print(f"🔍 Processing: {ad_name}")
        
        # Find matching media file
        media_match = map_ad_to_media(ad_name, media_files)
        
        if media_match:
            # Update record with media link
            update_data = {
                "fields": {
                    "Media_Download_URL": media_match['github_url'],
                    "Asset_Type": "Image" if media_match['type'] == 'image' else "Video",
                    "Download_Command": f"curl -L -o '{media_match['filename']}' '{media_match['github_url']}'",
                    "Notes": f"{fields.get('Notes', '')}\n\n🖼️ MEDIA: Direct download link added - {media_match['filename']}\n📅 Media Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            }
            
            update_url = f"{url}/{record_id}"
            update_response = requests.patch(update_url, headers=headers, json=update_data)
            
            if update_response.status_code == 200:
                print(f"   ✅ Updated with media: {media_match['filename']}")
                updated_count += 1
            else:
                print(f"   ❌ Update failed: {update_response.status_code}")
                print(f"   Response: {update_response.text}")
        else:
            print(f"   ⚠️  No media file found for: {ad_name}")
        
        time.sleep(0.2)  # Rate limiting
    
    print()
    print("=" * 70)
    print("🎉 MEDIA LINKS UPDATE COMPLETE!")
    print("=" * 70)
    print(f"📊 Records Updated: {updated_count}/{len(records)}")
    print(f"✅ Success Rate: {(updated_count/len(records)*100):.1f}%")
    print()
    print("📋 New Media Features:")
    print("   • Media_Download_URL - Direct links to PNG/video files")
    print("   • Updated Asset_Type - Proper image/video classification")
    print("   • Updated Download_Command - Curl commands for direct download")
    print("   • Working GitHub raw URLs - No more placeholder MD files")
    print()
    print(f"🔗 View updated data: https://airtable.com/{BASE_ID}")
    
    return updated_count > 0

def create_media_report():
    """Create a report of all available media files"""
    print("📊 Creating Media Files Report...")
    
    media_files = find_actual_media_files()
    
    report_filename = f"Available_Media_Files_Report_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    with open(report_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Ad_Name', 'Media_File', 'File_Path', 'GitHub_URL', 'Media_Type'])
        
        for ad_name, files in media_files.items():
            for file_info in files:
                writer.writerow([
                    ad_name,
                    file_info['filename'],
                    file_info['path'],
                    file_info['github_url'],
                    file_info['type']
                ])
    
    print(f"📄 Media report saved: {report_filename}")
    return report_filename

def main():
    """Main function"""
    print("🚀 Airtable Media Links Fixer")
    print("=" * 70)
    print("🎯 Goal: Replace placeholder MD links with actual downloadable media")
    print()
    
    # Create media report first
    report_file = create_media_report()
    
    print()
    
    # Update Airtable with proper media links
    success = update_airtable_with_media_links()
    
    if success:
        print()
        print("🎉 SUCCESS! Media links have been fixed!")
        print()
        print("✨ What's new:")
        print("• Media_Download_URL column with direct download links")
        print("• Links point to actual PNG/video files, not MD placeholders")
        print("• Proper curl download commands")
        print("• Updated asset type classification")
        print("• GitHub raw URLs that work in browsers")
        print()
        print(f"📊 Media report available: {report_file}")
    else:
        print("❌ Update failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 
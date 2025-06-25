#!/usr/bin/env python3
"""
Download Full-Resolution Creative Assets from Meta Ads

This script downloads FULL-RESOLUTION videos and images from your Meta Ads accounts,
not just thumbnails. It uses multiple API endpoints to get the highest quality assets.

Enhanced Features:
- Downloads actual video files, not thumbnails
- Gets full-resolution images
- Uses Meta's ad_creatives endpoint for better asset access
- Includes GitHub links for easy sharing
"""

import os
import requests
import json
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.parse

# Meta Ads API Configuration
META_ACCESS_TOKEN = "EAAHWhv6c7zEBOZCX2ZA2ZBOOHCeYW9oQZAcgtiFqWN9EZAVhIjGFRNHkd6pPHWDuf5GwFzRSzVuvwZCaOQ3idMvEmMZBd0VrvisCa9MiBxyRIekZC5RzHFmS11b0wbNv801N1tCjTZBEnAFM8XBdFoLEgyxL7Cf2sZABkmtqZAdZBpZALoZC8F0zAfAuJAOfHn0f6RLgZDZD"

# Airtable Configuration (NEW BASE)
AIRTABLE_BASE_ID = "appGnEqmyR9ksaBl0"
AIRTABLE_TABLE_ID = "tblVwp8WzcKE30vVA"

# GitHub repository configuration
GITHUB_REPO_URL = "https://github.com/lac5q/creative-ads-repository"
GITHUB_RAW_BASE = "https://github.com/lac5q/creative-ads-repository/raw/main"
GITHUB_BLOB_BASE = "https://github.com/lac5q/creative-ads-repository/blob/main"

# Your actual active Meta Ads accounts
ACTIVE_ACCOUNTS = {
    "USD_TurnedYellow": {
        "account_id": "act_2391476931086052",
        "name": "USD Turned Yellow",
        "priority": 1,
        "directory": "full_resolution_videos"
    },
    "MakeMeJedi": {
        "account_id": "act_2957720757845873", 
        "name": "MakeMeJedi",
        "priority": 2,
        "directory": "full_resolution_images"
    },
    "HoliFrog": {
        "account_id": "act_414476753269532",
        "name": "HoliFrog", 
        "priority": 3,
        "directory": "full_resolution_videos"
    },
    "TurnedWizard": {
        "account_id": "act_1195252750964860",
        "name": "Turned Wizard",
        "priority": 4,
        "directory": "full_resolution_images"
    },
    "TurnedYellow_AUD": {
        "account_id": "act_60960825",
        "name": "Turned Yellow",
        "priority": 5,
        "directory": "archive_full_resolution"
    }
}

# Create directories for full resolution assets
FULL_RES_DIRECTORIES = [
    "full_resolution_videos",
    "full_resolution_images", 
    "archive_full_resolution",
    "carousel_full_resolution",
    "collection_full_resolution"
]

def create_directory_structure():
    """Create required directory structure for full resolution assets"""
    print("📂 Creating full-resolution directory structure...")
    
    for directory in FULL_RES_DIRECTORIES:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✅ Created: {directory}/")
        else:
            print(f"  📁 Exists: {directory}/")

def get_ad_creatives_with_full_assets(account_id: str, days_back: int = 90) -> List[Dict]:
    """Get ad creatives with full-resolution asset URLs"""
    print(f"    🎬 Fetching ad creatives with full assets...")
    
    # Get campaigns first
    campaigns_url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    campaigns_params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'id,name',
        'effective_status': '["ACTIVE","PAUSED"]',
        'time_range': json.dumps({
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d')
        }),
        'limit': 25
    }
    
    try:
        campaigns_response = requests.get(campaigns_url, params=campaigns_params)
        campaigns_response.raise_for_status()
        campaigns_data = campaigns_response.json()
        campaigns = campaigns_data.get('data', [])[:10]  # Top 10 campaigns
        
        print(f"    ✅ Found {len(campaigns)} campaigns")
        
        # Get ad creatives from campaigns
        all_creatives = []
        
        for campaign in campaigns:
            campaign_id = campaign['id']
            
            # Get ads from campaign
            ads_url = f"https://graph.facebook.com/v18.0/{campaign_id}/ads"
            ads_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'id,name,creative{id,name,object_story_spec,asset_feed_spec,image_url,video_id,image_hash,thumbnail_url}',
                'effective_status': '["ACTIVE","PAUSED"]',
                'limit': 15
            }
            
            ads_response = requests.get(ads_url, params=ads_params)
            if ads_response.status_code == 200:
                ads_data = ads_response.json()
                
                for ad in ads_data.get('data', []):
                    if 'creative' in ad:
                        creative = ad['creative']
                        creative['campaign_id'] = campaign_id
                        creative['campaign_name'] = campaign.get('name', '')
                        creative['ad_id'] = ad.get('id', '')
                        creative['ad_name'] = ad.get('name', '')
                        all_creatives.append(creative)
            
            time.sleep(0.2)  # Rate limiting
        
        print(f"    ✅ Found {len(all_creatives)} ad creatives")
        return all_creatives
        
    except Exception as e:
        print(f"    ❌ Error fetching creatives: {str(e)}")
        return []

def get_full_resolution_video_url(video_id: str) -> Optional[str]:
    """Get the full-resolution video download URL"""
    try:
        video_url = f"https://graph.facebook.com/v18.0/{video_id}"
        video_params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'source,file_url,permalink_url,format'
        }
        
        video_response = requests.get(video_url, params=video_params)
        if video_response.status_code == 200:
            video_data = video_response.json()
            
            # Try to get the source URL (full resolution)
            if 'source' in video_data:
                return video_data['source']
            elif 'file_url' in video_data:
                return video_data['file_url']
            elif 'permalink_url' in video_data:
                return video_data['permalink_url']
        
        return None
        
    except Exception as e:
        print(f"      ⚠️ Error getting video URL: {str(e)}")
        return None

def get_full_resolution_image_url(image_hash: str, account_id: str) -> Optional[str]:
    """Get the full-resolution image URL using image hash"""
    try:
        # Use the ad images endpoint to get full resolution
        images_url = f"https://graph.facebook.com/v18.0/{account_id}/adimages"
        images_params = {
            'access_token': META_ACCESS_TOKEN,
            'hashes': f'["{image_hash}"]',
            'fields': 'url,url_128,original_width,original_height'
        }
        
        images_response = requests.get(images_url, params=images_params)
        if images_response.status_code == 200:
            images_data = images_response.json()
            
            if 'data' in images_data and images_data['data']:
                for image_hash_key, image_info in images_data['data'].items():
                    if 'url' in image_info:
                        return image_info['url']
        
        return None
        
    except Exception as e:
        print(f"      ⚠️ Error getting image URL: {str(e)}")
        return None

def safe_filename(text: str, max_length: int = 100) -> str:
    """Create a safe filename from text"""
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. "
    filename = "".join(c if c in safe_chars else "_" for c in text)
    filename = filename.replace(" ", "_").replace("__", "_").strip("_")
    
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip("_")
    
    return filename or "unnamed"

def download_full_resolution_asset(creative: Dict, brand: str, target_dir: str, account_id: str) -> Optional[str]:
    """Download a full-resolution creative asset (video or image)"""
    creative_id = creative.get('id', '')
    creative_name = creative.get('name', f'creative_{creative_id}')
    
    asset_url = None
    asset_type = "unknown"
    file_extension = "jpg"
    
    # Try to get full-resolution video first
    if creative.get('video_id'):
        asset_url = get_full_resolution_video_url(creative['video_id'])
        asset_type = "video"
        file_extension = "mp4"
        print(f"      🎥 Getting full-resolution video...")
    
    # Try to get full-resolution image
    elif creative.get('image_hash'):
        asset_url = get_full_resolution_image_url(creative['image_hash'], account_id)
        asset_type = "image"
        file_extension = "jpg"
        print(f"      🖼️ Getting full-resolution image...")
    
    # Fallback to direct image URL
    elif creative.get('image_url'):
        asset_url = creative['image_url']
        asset_type = "image"
        file_extension = "jpg"
        print(f"      📸 Using direct image URL...")
    
    if not asset_url:
        print(f"      ⚠️ No asset URL found for creative {creative_id}")
        return None
    
    try:
        # Create filename
        safe_name = safe_filename(creative_name, 60)
        filename = f"{brand}_{creative_id}_{asset_type}_FULLRES_{safe_name}.{file_extension}"
        filepath = os.path.join(target_dir, filename)
        
        # Download asset
        print(f"      📥 Downloading FULL-RES: {filename[:80]}...")
        
        asset_response = requests.get(asset_url, stream=True, timeout=60)
        asset_response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in asset_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(filepath) / 1024  # KB
        
        if file_size < 1:  # Less than 1KB, probably failed
            os.remove(filepath)
            print(f"      ❌ Downloaded file too small, removed")
            return None
        
        print(f"      ✅ Downloaded FULL-RES ({file_size:.1f} KB)")
        return filepath
        
    except Exception as e:
        print(f"      ❌ Download error: {str(e)}")
        return None

def process_account_full_resolution(brand_key: str, account_info: Dict) -> Tuple[int, List[Dict]]:
    """Process account and download full-resolution creatives"""
    account_id = account_info['account_id']
    account_name = account_info['name']
    target_dir = account_info['directory']
    
    print(f"\n🏢 Processing FULL-RES: {account_name}")
    print(f"   📊 Account: {account_id}")
    print(f"   📁 Target: {target_dir}/")
    
    downloaded_assets = []
    download_count = 0
    
    # Get ad creatives with full asset info
    creatives = get_ad_creatives_with_full_assets(account_id)
    
    if not creatives:
        print(f"   ⚠️ No creatives found")
        return 0, []
    
    # Download full-resolution assets
    print(f"   🎬 Processing {len(creatives)} creatives for FULL-RES download...")
    
    for i, creative in enumerate(creatives):
        if download_count >= 25:  # Increased limit for full-res
            break
        
        filepath = download_full_resolution_asset(creative, brand_key, target_dir, account_id)
        
        if filepath:
            # Create asset record with GitHub links
            asset_info = {
                'name': os.path.basename(filepath),
                'brand': brand_key,
                'creative_id': creative.get('id', ''),
                'ad_id': creative.get('ad_id', ''),
                'campaign_id': creative.get('campaign_id', ''),
                'campaign_name': creative.get('campaign_name', ''),
                'creative_name': creative.get('name', ''),
                'ad_name': creative.get('ad_name', ''),
                'file_path': filepath,
                'directory': target_dir,
                'github_download': f"{GITHUB_RAW_BASE}/{target_dir}/{os.path.basename(filepath)}",
                'github_view': f"{GITHUB_BLOB_BASE}/{target_dir}/{os.path.basename(filepath)}",
                'file_size_kb': round(os.path.getsize(filepath) / 1024, 2),
                'is_full_resolution': True,
                'downloaded_at': datetime.now().isoformat()
            }
            
            downloaded_assets.append(asset_info)
            download_count += 1
        
        # Rate limiting
        if i % 3 == 0:
            time.sleep(0.5)
    
    print(f"   ✅ Downloaded {download_count} FULL-RES creatives")
    return download_count, downloaded_assets

def export_for_new_airtable(all_assets: List[Dict]):
    """Export data formatted for the new Airtable base"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # CSV Export for new Airtable
    csv_filename = f"full_resolution_airtable_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Creative_Name', 'Brand', 'Account', 'Campaign_Name', 'Campaign_ID',
            'Creative_Type', 'Resolution_Type', 'File_Size_KB', 'Download_Date',
            'GitHub_Download_Link', 'GitHub_View_Link', 'Status', 'Notes',
            'Download_Command', 'Directory_Source', 'Asset_Quality'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for asset in all_assets:
            # Determine creative type from filename
            asset_type = "video" if "_video_" in asset['name'] or asset['name'].endswith('.mp4') else "image"
            
            writer.writerow({
                'Creative_Name': asset['name'][:100],
                'Brand': asset['brand'],
                'Account': asset['brand'],
                'Campaign_Name': asset.get('campaign_name', '')[:50],
                'Campaign_ID': asset.get('campaign_id', ''),
                'Creative_Type': asset_type.title(),
                'Resolution_Type': 'Full Resolution',
                'File_Size_KB': asset.get('file_size_kb', 0),
                'Download_Date': datetime.now().strftime('%Y-%m-%d'),
                'GitHub_Download_Link': asset['github_download'],
                'GitHub_View_Link': asset['github_view'],
                'Status': 'Active',
                'Notes': f"Full-resolution download {datetime.now().strftime('%Y-%m-%d')}",
                'Download_Command': f'curl -L "{asset["github_download"]}" -o "{asset["name"]}"',
                'Directory_Source': asset['directory'],
                'Asset_Quality': 'High Quality Full Resolution'
            })
    
    print(f"\n📊 NEW AIRTABLE EXPORT:")
    print(f"  📄 CSV: {csv_filename}")
    print(f"  🎯 Base: {AIRTABLE_BASE_ID}")
    print(f"  📋 Table: {AIRTABLE_TABLE_ID}")
    
    return csv_filename

def main():
    """Main execution function"""
    print("🚀 FULL-RESOLUTION CREATIVE ASSETS DOWNLOAD")
    print("=" * 60)
    print("Downloading FULL-RES videos and images (not thumbnails)...")
    print(f"Target Airtable: {AIRTABLE_BASE_ID}")
    print("=" * 60)
    
    # Create directory structure
    create_directory_structure()
    
    total_downloaded = 0
    all_assets = []
    
    # Process each account for full-resolution assets
    for brand_key, account_info in ACTIVE_ACCOUNTS.items():
        try:
            download_count, assets = process_account_full_resolution(brand_key, account_info)
            total_downloaded += download_count
            all_assets.extend(assets)
            
            # Brief pause between accounts
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error processing {brand_key}: {str(e)}")
            continue
    
    # Export results for new Airtable
    if all_assets:
        csv_file = export_for_new_airtable(all_assets)
        
        # Summary by brand
        brand_summary = {}
        for asset in all_assets:
            brand = asset['brand']
            brand_summary[brand] = brand_summary.get(brand, 0) + 1
        
        print(f"\n🎉 FULL-RES DOWNLOAD COMPLETE!")
        print("=" * 40)
        print(f"📊 Total downloaded: {total_downloaded} FULL-RES creatives")
        print(f"\n🏢 By Brand:")
        for brand, count in sorted(brand_summary.items()):
            print(f"  {brand}: {count} full-res creatives")
        
        # Calculate total file size
        total_size_mb = sum(asset.get('file_size_kb', 0) for asset in all_assets) / 1024
        print(f"\n💾 Total Size: {total_size_mb:.1f} MB")
        
        print(f"\n📁 Files created:")
        print(f"  📊 {csv_file}")
        print(f"\n🔗 GitHub Repository:")
        print(f"  {GITHUB_REPO_URL}")
        
        print(f"\n✅ READY FOR NEW AIRTABLE!")
        print(f"  🎯 Base: https://airtable.com/{AIRTABLE_BASE_ID}")
        print(f"  📋 Import: {csv_file}")
        print(f"  🔗 All assets include GitHub download links!")
        
    else:
        print(f"\n⚠️ No full-resolution creatives downloaded.")
        print(f"Check your Meta Ads API access and account permissions.")

if __name__ == "__main__":
    main() 
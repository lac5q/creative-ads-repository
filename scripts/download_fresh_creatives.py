#!/usr/bin/env python3
"""
Download Fresh Creative Assets from Meta Ads

This script downloads creative assets from your active Meta Ads accounts
and organizes them in your GitHub repository structure.

Based on your actual accounts:
- USD Turned Yellow: act_2391476931086052 (Active, $2.5M spent)
- MakeMeJedi: act_2957720757845873 (Active, $1.1M spent)  
- HoliFrog: act_414476753269532 (Active, $163K spent)
- Turned Wizard: act_1195252750964860 (Active, $56K spent)
- Turned Yellow (AUD): act_60960825 (Active, $18K spent)
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

# GitHub repository configuration
GITHUB_REPO_URL = "https://github.com/lac5q/creative-ads-repository"
GITHUB_RAW_BASE = "https://github.com/lac5q/creative-ads-repository/raw/main"
GITHUB_BLOB_BASE = "https://github.com/lac5q/creative-ads-repository/blob/main"

# Your actual active Meta Ads accounts
ACTIVE_ACCOUNTS = {
    "USD_TurnedYellow": {
        "account_id": "act_2391476931086052",
        "name": "USD Turned Yellow",
        "priority": 1,  # Highest spend
        "directory": "hd_ad_creatives"
    },
    "MakeMeJedi": {
        "account_id": "act_2957720757845873", 
        "name": "MakeMeJedi",
        "priority": 2,
        "directory": "hd_ad_creatives"
    },
    "HoliFrog": {
        "account_id": "act_414476753269532",
        "name": "HoliFrog", 
        "priority": 3,
        "directory": "video_creatives"
    },
    "TurnedWizard": {
        "account_id": "act_1195252750964860",
        "name": "Turned Wizard",
        "priority": 4,
        "directory": "image_creatives"
    },
    "TurnedYellow_AUD": {
        "account_id": "act_60960825",
        "name": "Turned Yellow",
        "priority": 5,
        "directory": "archive_creatives"
    }
}

# Create directories if they don't exist
REQUIRED_DIRECTORIES = [
    "hd_ad_creatives",
    "video_creatives", 
    "image_creatives",
    "carousel_creatives",
    "dynamic_creatives",
    "archive_creatives"
]

def create_directory_structure():
    """Create required directory structure"""
    print("📂 Creating directory structure...")
    
    for directory in REQUIRED_DIRECTORIES:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✅ Created: {directory}/")
        else:
            print(f"  📁 Exists: {directory}/")

def get_campaigns_from_account(account_id: str, days_back: int = 90) -> List[Dict]:
    """Get recent campaigns from an account"""
    print(f"    📊 Fetching campaigns...")
    
    url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns"
    
    # Get campaigns from past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'id,name,status,effective_status,created_time,objective,spend',
        'effective_status': '["ACTIVE","PAUSED"]',  # Only active/paused campaigns
        'time_range': json.dumps({
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d')
        }),
        'limit': 50
    }
    
    campaigns = []
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        campaigns.extend(data.get('data', []))
        
        # Handle pagination if needed
        while 'paging' in data and 'next' in data['paging'] and len(campaigns) < 100:
            response = requests.get(data['paging']['next'])
            response.raise_for_status()
            data = response.json()
            campaigns.extend(data.get('data', []))
            time.sleep(0.1)
        
        print(f"    ✅ Found {len(campaigns)} campaigns")
        return campaigns[:50]  # Limit to 50 most recent
        
    except Exception as e:
        print(f"    ❌ Error fetching campaigns: {str(e)}")
        return []

def get_ads_from_campaigns(account_id: str, campaign_ids: List[str]) -> List[Dict]:
    """Get ads with creatives from campaigns"""
    print(f"    🎬 Fetching ads from {len(campaign_ids)} campaigns...")
    
    all_ads = []
    processed_campaigns = 0
    
    for campaign_id in campaign_ids:
        if processed_campaigns >= 10:  # Limit to prevent rate limiting
            break
            
        try:
            # Get ads for this campaign
            ads_url = f"https://graph.facebook.com/v18.0/{campaign_id}/ads"
            ads_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'id,name,status,effective_status,creative{id,name,object_story_spec,image_url,video_id,body,title}',
                'effective_status': '["ACTIVE","PAUSED"]',
                'limit': 25
            }
            
            ads_response = requests.get(ads_url, params=ads_params)
            ads_response.raise_for_status()
            ads_data = ads_response.json()
            
            campaign_ads = ads_data.get('data', [])
            for ad in campaign_ads:
                if 'creative' in ad:
                    ad['campaign_id'] = campaign_id
                    all_ads.append(ad)
            
            processed_campaigns += 1
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            print(f"    ⚠️ Error fetching ads for campaign {campaign_id}: {str(e)}")
            continue
    
    print(f"    ✅ Found {len(all_ads)} ads with creatives")
    return all_ads

def safe_filename(text: str, max_length: int = 100) -> str:
    """Create a safe filename from text"""
    # Remove/replace unsafe characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. "
    filename = "".join(c if c in safe_chars else "_" for c in text)
    
    # Replace spaces with underscores and clean up
    filename = filename.replace(" ", "_").replace("__", "_").strip("_")
    
    # Truncate if too long
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip("_")
    
    return filename or "unnamed"

def download_creative_image(creative: Dict, brand: str, target_dir: str) -> Optional[str]:
    """Download a creative image/video thumbnail"""
    creative_id = creative.get('id', '')
    creative_name = creative.get('name', f'creative_{creative_id}')
    
    # Try to get image URL from different sources
    image_url = None
    asset_type = "image"
    
    # Check for direct image URL
    if creative.get('image_url'):
        image_url = creative['image_url']
        asset_type = "image"
    
    # Check for video thumbnail
    elif creative.get('video_id'):
        try:
            video_url = f"https://graph.facebook.com/v18.0/{creative['video_id']}"
            video_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'picture,thumbnails'
            }
            
            video_response = requests.get(video_url, params=video_params)
            if video_response.status_code == 200:
                video_data = video_response.json()
                image_url = video_data.get('picture')
                asset_type = "video"
        except:
            pass
    
    # Check object_story_spec for more image sources
    elif creative.get('object_story_spec'):
        story_spec = creative['object_story_spec']
        
        # Check link_data
        if 'link_data' in story_spec:
            link_data = story_spec['link_data']
            if 'image_hash' in link_data:
                # Would need to resolve image hash to URL - skip for now
                pass
    
    if not image_url:
        print(f"      ⚠️ No image URL found for creative {creative_id}")
        return None
    
    try:
        # Create filename
        safe_name = safe_filename(creative_name, 60)
        filename = f"{brand}_{creative_id}_{asset_type}_{safe_name}.jpg"
        filepath = os.path.join(target_dir, filename)
        
        # Download image
        print(f"      📥 Downloading: {filename[:80]}...")
        
        image_response = requests.get(image_url, stream=True, timeout=30)
        image_response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in image_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(filepath) / 1024  # KB
        
        if file_size < 1:  # Less than 1KB, probably failed
            os.remove(filepath)
            print(f"      ❌ Downloaded file too small, removed")
            return None
        
        print(f"      ✅ Downloaded ({file_size:.1f} KB)")
        return filepath
        
    except Exception as e:
        print(f"      ❌ Download error: {str(e)}")
        return None

def process_account(brand_key: str, account_info: Dict) -> Tuple[int, List[Dict]]:
    """Process a single account and download its creatives"""
    account_id = account_info['account_id']
    account_name = account_info['name']
    target_dir = account_info['directory']
    
    print(f"\n🏢 Processing: {account_name}")
    print(f"   📊 Account: {account_id}")
    print(f"   📁 Target: {target_dir}/")
    
    downloaded_assets = []
    download_count = 0
    
    # Step 1: Get campaigns
    campaigns = get_campaigns_from_account(account_id)
    if not campaigns:
        print(f"   ⚠️ No campaigns found")
        return 0, []
    
    # Step 2: Get ads from top campaigns
    campaign_ids = [c['id'] for c in campaigns[:10]]  # Top 10 campaigns
    ads = get_ads_from_campaigns(account_id, campaign_ids)
    
    if not ads:
        print(f"   ⚠️ No ads found")
        return 0, []
    
    # Step 3: Download creatives
    print(f"   🎬 Processing {len(ads)} ads...")
    
    for i, ad in enumerate(ads):
        if download_count >= 20:  # Limit per account
            break
            
        creative = ad.get('creative', {})
        if not creative:
            continue
        
        filepath = download_creative_image(creative, brand_key, target_dir)
        
        if filepath:
            # Create asset record
            asset_info = {
                'name': os.path.basename(filepath),
                'brand': brand_key,
                'creative_id': creative.get('id', ''),
                'ad_id': ad.get('id', ''),
                'campaign_id': ad.get('campaign_id', ''),
                'creative_name': creative.get('name', ''),
                'ad_name': ad.get('name', ''),
                'file_path': filepath,
                'directory': target_dir,
                'github_download': f"{GITHUB_RAW_BASE}/{target_dir}/{os.path.basename(filepath)}",
                'github_view': f"{GITHUB_BLOB_BASE}/{target_dir}/{os.path.basename(filepath)}",
                'downloaded_at': datetime.now().isoformat()
            }
            
            downloaded_assets.append(asset_info)
            download_count += 1
        
        # Rate limiting
        if i % 5 == 0:
            time.sleep(0.5)
    
    print(f"   ✅ Downloaded {download_count} creatives")
    return download_count, downloaded_assets

def export_download_results(all_assets: List[Dict]):
    """Export download results to CSV and JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON Export
    json_filename = f"fresh_download_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_assets, f, indent=2, ensure_ascii=False)
    
    # CSV Export for Airtable
    csv_filename = f"fresh_airtable_import_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Name', 'Brand', 'Creative_Type', 'Performance_Tier', 'Campaign_ID',
            'File_Size_KB', 'Created_Date', 'Days_Ago', 'Directory_Source',
            'GitHub_Download_Link', 'GitHub_View_Link', 'File_Type', 
            'Quality_Priority', 'Notes'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for asset in all_assets:
            # Calculate file size
            file_size_kb = 0
            if os.path.exists(asset['file_path']):
                file_size_kb = os.path.getsize(asset['file_path']) / 1024
            
            # Determine creative type
            creative_type = "video" if "_video_" in asset['name'] else "image"
            
            writer.writerow({
                'Name': asset['name'],
                'Brand': asset['brand'],
                'Creative_Type': creative_type,
                'Performance_Tier': '',  # Will be determined later
                'Campaign_ID': asset['campaign_id'],
                'File_Size_KB': round(file_size_kb, 2),
                'Created_Date': datetime.now().strftime('%Y-%m-%d'),
                'Days_Ago': 0,
                'Directory_Source': asset['directory'],
                'GitHub_Download_Link': asset['github_download'],
                'GitHub_View_Link': asset['github_view'],
                'File_Type': 'jpg',
                'Quality_Priority': 1,
                'Notes': f"Fresh download on {datetime.now().strftime('%Y-%m-%d')}"
            })
    
    print(f"\n📊 EXPORT COMPLETE:")
    print(f"  📄 JSON: {json_filename}")
    print(f"  📊 CSV: {csv_filename}")
    
    return json_filename, csv_filename

def main():
    """Main execution function"""
    print("🚀 FRESH CREATIVE ASSETS DOWNLOAD")
    print("=" * 50)
    print("Downloading from your active Meta Ads accounts...")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    total_downloaded = 0
    all_assets = []
    
    # Process each account
    for brand_key, account_info in ACTIVE_ACCOUNTS.items():
        try:
            download_count, assets = process_account(brand_key, account_info)
            total_downloaded += download_count
            all_assets.extend(assets)
            
            # Brief pause between accounts
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing {brand_key}: {str(e)}")
            continue
    
    # Export results
    if all_assets:
        json_file, csv_file = export_download_results(all_assets)
        
        # Summary by brand
        brand_summary = {}
        for asset in all_assets:
            brand = asset['brand']
            brand_summary[brand] = brand_summary.get(brand, 0) + 1
        
        print(f"\n🎉 DOWNLOAD COMPLETE!")
        print("=" * 30)
        print(f"📊 Total downloaded: {total_downloaded} creatives")
        print(f"\n🏢 By Brand:")
        for brand, count in sorted(brand_summary.items()):
            print(f"  {brand}: {count} creatives")
        
        print(f"\n📁 Files created:")
        print(f"  📄 {json_file}")
        print(f"  📊 {csv_file}")
        print(f"\n✅ Ready for Airtable import!")
        
    else:
        print(f"\n⚠️ No creatives downloaded.")
        print(f"Check your Meta Ads API access and account permissions.")

if __name__ == "__main__":
    main() 
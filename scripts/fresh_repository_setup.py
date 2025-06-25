#!/usr/bin/env python3
"""
Fresh Repository Setup - Complete Creative Assets Reset

This script will:
1. Clear all existing creative assets from GitHub repository directories
2. Re-download all creative assets from Meta Ads API (past 3 months)
3. Organize them properly in the repository structure
4. Generate fresh GitHub links and inventory

Features:
- Complete repository cleanup
- Fresh Meta Ads API downloads
- Proper file organization
- Quality-based directory structure
- New GitHub link generation
"""

import os
import shutil
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

# Meta Ads API Configuration
META_ACCESS_TOKEN = "EAAHWhv6c7zEBOZCX2ZA2ZBOOHCeYW9oQZAcgtiFqWN9EZAVhIjGFRNHkd6pPHWDuf5GwFzRSzVuvwZCaOQ3idMvEmMZBd0VrvisCa9MiBxyRIekZC5RzHFmS11b0wbNv801N1tCjTZBEnAFM8XBdFoLEgyxL7Cf2sZABkmtqZAdZBpZALoZC8F0zAfAuJAOfHn0f6RLgZDZD"

# GitHub repository configuration
GITHUB_REPO_URL = "https://github.com/lac5q/creative-ads-repository"
GITHUB_RAW_BASE = "https://github.com/lac5q/creative-ads-repository/raw/main"
GITHUB_BLOB_BASE = "https://github.com/lac5q/creative-ads-repository/blob/main"

# Directory structure for organization
REPO_DIRECTORIES = {
    "hd_ad_creatives": "High-quality creative assets",
    "video_creatives": "Video creative assets", 
    "image_creatives": "Image creative assets",
    "carousel_creatives": "Carousel creative assets",
    "dynamic_creatives": "Dynamic creative assets",
    "archive_creatives": "Archive/backup creative assets"
}

# Brand account mappings (add your actual account IDs)
BRAND_ACCOUNTS = {
    "TurnedYellow": "act_your_turnedyellow_account_id",
    "MakeMeJedi": "act_your_makemejedi_account_id",
    "TurnedWizard": "act_your_turnedwizard_account_id",
    "TurnedThrones": "act_your_turnedthrones_account_id",
    "HoliFrog": "act_your_holifrog_account_id",
    "Portrified": "act_your_portrified_account_id",
    "TurnSuperHero": "act_your_turnsuperhero_account_id",
    "TurnedToAnime": "act_your_turnedtoanime_account_id"
}

def clear_repository_directories():
    """Clear all existing creative asset directories"""
    print("🧹 CLEARING EXISTING REPOSITORY DIRECTORIES")
    print("=" * 50)
    
    cleared_count = 0
    total_size_cleared = 0
    
    for directory in REPO_DIRECTORIES.keys():
        if os.path.exists(directory):
            print(f"📂 Clearing directory: {directory}")
            
            # Calculate size before clearing
            dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(directory)
                          for filename in filenames) / (1024 * 1024)  # MB
            
            # Count files
            file_count = sum(len(filenames) for _, _, filenames in os.walk(directory))
            
            print(f"  📊 Found {file_count} files ({dir_size:.2f} MB)")
            
            # Remove directory and recreate
            shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)
            
            cleared_count += file_count
            total_size_cleared += dir_size
            
            print(f"  ✅ Cleared {file_count} files")
        else:
            print(f"📂 Creating new directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # Also clear root level creative files
    root_creatives = []
    for file in os.listdir("."):
        if any(file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov']):
            if not file.startswith('.'):  # Skip hidden files
                root_creatives.append(file)
    
    if root_creatives:
        print(f"📂 Found {len(root_creatives)} creative files in root directory")
        for file in root_creatives:
            try:
                os.remove(file)
                print(f"  🗑️ Removed: {file}")
                cleared_count += 1
            except Exception as e:
                print(f"  ❌ Error removing {file}: {str(e)}")
    
    print(f"\n✅ CLEANUP COMPLETE!")
    print(f"📊 Total files cleared: {cleared_count}")
    print(f"💾 Total space cleared: {total_size_cleared:.2f} MB")
    
    return cleared_count, total_size_cleared

def get_meta_ads_campaigns(account_id: str, days_back: int = 90) -> List[Dict]:
    """Get campaigns from Meta Ads API for the past N days"""
    print(f"📊 Fetching campaigns for account: {account_id}")
    
    url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns"
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'id,name,status,effective_status,created_time,updated_time,objective',
        'effective_status': '["ACTIVE","PAUSED","PENDING_REVIEW","DISAPPROVED","PREAPPROVED","PENDING_BILLING_INFO","CAMPAIGN_PAUSED","ARCHIVED"]',
        'time_range': json.dumps({
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d')
        }),
        'limit': 100
    }
    
    campaigns = []
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        campaigns.extend(data.get('data', []))
        
        # Handle pagination
        while 'paging' in data and 'next' in data['paging']:
            response = requests.get(data['paging']['next'])
            response.raise_for_status()
            data = response.json()
            campaigns.extend(data.get('data', []))
            time.sleep(0.1)  # Rate limiting
        
        print(f"  ✅ Found {len(campaigns)} campaigns")
        return campaigns
        
    except Exception as e:
        print(f"  ❌ Error fetching campaigns: {str(e)}")
        return []

def get_ads_with_creatives(account_id: str, campaign_ids: List[str]) -> List[Dict]:
    """Get ads with their creative information"""
    print(f"🎬 Fetching ads and creatives...")
    
    all_ads = []
    
    for campaign_id in campaign_ids:
        print(f"  📊 Processing campaign: {campaign_id}")
        
        # Get ad sets for this campaign
        adsets_url = f"https://graph.facebook.com/v18.0/{campaign_id}/adsets"
        adsets_params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'id,name,status,effective_status',
            'limit': 100
        }
        
        try:
            adsets_response = requests.get(adsets_url, params=adsets_params)
            adsets_response.raise_for_status()
            adsets_data = adsets_response.json()
            
            for adset in adsets_data.get('data', []):
                # Get ads for this ad set
                ads_url = f"https://graph.facebook.com/v18.0/{adset['id']}/ads"
                ads_params = {
                    'access_token': META_ACCESS_TOKEN,
                    'fields': 'id,name,status,effective_status,creative{id,name,object_story_spec,image_url,video_id,body,title,call_to_action}',
                    'limit': 100
                }
                
                try:
                    ads_response = requests.get(ads_url, params=ads_params)
                    ads_response.raise_for_status()
                    ads_data = ads_response.json()
                    
                    for ad in ads_data.get('data', []):
                        if 'creative' in ad:
                            ad['campaign_id'] = campaign_id
                            ad['adset_id'] = adset['id']
                            all_ads.append(ad)
                    
                except Exception as e:
                    print(f"    ❌ Error fetching ads for adset {adset['id']}: {str(e)}")
                
                time.sleep(0.1)  # Rate limiting
                
        except Exception as e:
            print(f"  ❌ Error fetching adsets for campaign {campaign_id}: {str(e)}")
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"  ✅ Found {len(all_ads)} ads with creatives")
    return all_ads

def download_creative_asset(creative_info: Dict, brand: str, download_dir: str) -> Optional[str]:
    """Download a creative asset from Meta Ads"""
    creative_id = creative_info.get('id', '')
    creative_name = creative_info.get('name', f'creative_{creative_id}')
    
    # Try to get image URL
    image_url = creative_info.get('image_url')
    video_id = creative_info.get('video_id')
    
    if not image_url and not video_id:
        print(f"    ⚠️ No downloadable asset found for creative {creative_id}")
        return None
    
    try:
        # Determine asset type and URL
        if video_id:
            # For videos, we need to get the thumbnail or video URL
            video_url = f"https://graph.facebook.com/v18.0/{video_id}"
            video_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'source,picture,format'
            }
            
            video_response = requests.get(video_url, params=video_params)
            video_response.raise_for_status()
            video_data = video_response.json()
            
            # Use video source if available, otherwise picture
            download_url = video_data.get('source') or video_data.get('picture')
            file_extension = '.mp4' if video_data.get('source') else '.jpg'
            asset_type = 'video'
            
        else:
            download_url = image_url
            file_extension = '.jpg'
            asset_type = 'image'
        
        if not download_url:
            print(f"    ⚠️ No download URL found for creative {creative_id}")
            return None
        
        # Create safe filename
        safe_name = "".join(c for c in creative_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        filename = f"{brand}_{creative_id}_{asset_type}_{safe_name}{file_extension}"
        filepath = os.path.join(download_dir, filename)
        
        # Download the asset
        print(f"    📥 Downloading: {filename}")
        
        asset_response = requests.get(download_url, stream=True)
        asset_response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in asset_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"    ✅ Downloaded {filename} ({file_size:.2f} KB)")
        
        return filepath
        
    except Exception as e:
        print(f"    ❌ Error downloading creative {creative_id}: {str(e)}")
        return None

def organize_downloaded_assets():
    """Organize downloaded assets into proper directory structure"""
    print("\n📂 ORGANIZING DOWNLOADED ASSETS")
    print("=" * 50)
    
    moved_count = 0
    
    for directory in REPO_DIRECTORIES.keys():
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov'))]
            print(f"📁 {directory}: {len(files)} files")
            moved_count += len(files)
    
    # Move files based on type and quality
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov')):
                if root == ".":  # Files in root directory
                    filepath = os.path.join(root, file)
                    
                    # Determine target directory based on file characteristics
                    if '_video_' in file.lower():
                        target_dir = "video_creatives"
                    elif '_image_' in file.lower():
                        target_dir = "image_creatives" 
                    elif file.lower().endswith('.mp4'):
                        target_dir = "video_creatives"
                    elif file.lower().endswith('.gif'):
                        target_dir = "dynamic_creatives"
                    else:
                        target_dir = "hd_ad_creatives"  # Default to HD
                    
                    target_path = os.path.join(target_dir, file)
                    
                    try:
                        shutil.move(filepath, target_path)
                        print(f"  📁 Moved {file} → {target_dir}/")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ❌ Error moving {file}: {str(e)}")
    
    print(f"\n✅ Organization complete! Moved {moved_count} files")
    return moved_count

def fresh_download_all_creatives():
    """Download all creative assets fresh from Meta Ads API"""
    print("\n🔄 FRESH DOWNLOAD FROM META ADS API")
    print("=" * 50)
    
    total_downloaded = 0
    download_summary = {}
    
    for brand, account_id in BRAND_ACCOUNTS.items():
        if account_id.startswith("act_your_"):  # Skip placeholder IDs
            print(f"⚠️ Skipping {brand} - Please configure actual account ID")
            continue
            
        print(f"\n🏢 Processing brand: {brand}")
        print(f"📊 Account ID: {account_id}")
        
        # Get campaigns for this account
        campaigns = get_meta_ads_campaigns(account_id)
        if not campaigns:
            print(f"  ⚠️ No campaigns found for {brand}")
            continue
        
        campaign_ids = [c['id'] for c in campaigns]
        
        # Get ads with creatives
        ads_with_creatives = get_ads_with_creatives(account_id, campaign_ids)
        if not ads_with_creatives:
            print(f"  ⚠️ No ads with creatives found for {brand}")
            continue
        
        # Download creatives
        brand_downloaded = 0
        download_dir = "hd_ad_creatives"  # Start with HD directory
        
        for ad in ads_with_creatives:
            creative = ad.get('creative', {})
            filepath = download_creative_asset(creative, brand, download_dir)
            
            if filepath:
                brand_downloaded += 1
                total_downloaded += 1
            
            time.sleep(0.2)  # Rate limiting
        
        download_summary[brand] = brand_downloaded
        print(f"  ✅ Downloaded {brand_downloaded} creatives for {brand}")
    
    print(f"\n📊 DOWNLOAD SUMMARY:")
    for brand, count in download_summary.items():
        print(f"  🏢 {brand}: {count} creatives")
    
    print(f"\n✅ Total downloaded: {total_downloaded} creative assets")
    return total_downloaded, download_summary

def generate_fresh_github_inventory():
    """Generate fresh GitHub links inventory after download"""
    print("\n🔗 GENERATING FRESH GITHUB INVENTORY")
    print("=" * 50)
    
    inventory = []
    
    for directory in REPO_DIRECTORIES.keys():
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov'))]
            
            for file in files:
                filepath = os.path.join(directory, file)
                
                # Extract metadata from filename
                parts = file.split('_')
                brand = parts[0] if parts else "Unknown"
                creative_id = parts[1] if len(parts) > 1 else ""
                asset_type = parts[2] if len(parts) > 2 else "unknown"
                
                # Generate GitHub URLs
                download_url = f"{GITHUB_RAW_BASE}/{directory}/{file}"
                view_url = f"{GITHUB_BLOB_BASE}/{directory}/{file}"
                
                # Get file stats
                file_size = os.path.getsize(filepath) / 1024  # KB
                file_type = Path(file).suffix[1:].lower()
                
                asset_info = {
                    "name": file,
                    "brand": brand,
                    "creative_type": asset_type,
                    "creative_id": creative_id,
                    "file_size_kb": round(file_size, 2),
                    "file_type": file_type,
                    "directory_source": directory,
                    "github_download_link": download_url,
                    "github_view_link": view_url,
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "days_ago": 0,
                    "quality_priority": 1 if directory == "hd_ad_creatives" else 2,
                    "status": "Fresh Download",
                    "notes": f"Freshly downloaded from Meta Ads API on {datetime.now().strftime('%Y-%m-%d')}"
                }
                
                inventory.append(asset_info)
    
    # Export inventory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON export
    json_filename = f"fresh_creative_inventory_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    # CSV export for Airtable
    csv_filename = f"fresh_airtable_import_{timestamp}.csv"
    import csv
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Brand', 'Creative_Type', 'Performance_Tier', 'Campaign_ID', 
                     'File_Size_KB', 'Created_Date', 'Days_Ago', 'Directory_Source',
                     'GitHub_Download_Link', 'GitHub_View_Link', 'File_Type', 
                     'Quality_Priority', 'Notes']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for asset in inventory:
            writer.writerow({
                'Name': asset['name'],
                'Brand': asset['brand'],
                'Creative_Type': asset['creative_type'],
                'Performance_Tier': '',  # Will be determined later
                'Campaign_ID': asset['creative_id'],
                'File_Size_KB': asset['file_size_kb'],
                'Created_Date': asset['created_date'],
                'Days_Ago': asset['days_ago'],
                'Directory_Source': asset['directory_source'],
                'GitHub_Download_Link': asset['github_download_link'],
                'GitHub_View_Link': asset['github_view_link'],
                'File_Type': asset['file_type'],
                'Quality_Priority': asset['quality_priority'],
                'Notes': asset['notes']
            })
    
    print(f"✅ Generated fresh inventory:")
    print(f"  📊 JSON: {json_filename}")
    print(f"  📊 CSV: {csv_filename}")
    print(f"  📈 Total assets: {len(inventory)}")
    
    return inventory, json_filename, csv_filename

def main():
    """Main execution function"""
    print("🚀 FRESH REPOSITORY SETUP - COMPLETE RESET")
    print("=" * 60)
    print("This will completely clear and re-download all creative assets")
    print("=" * 60)
    
    # Step 1: Clear existing directories
    cleared_files, cleared_mb = clear_repository_directories()
    
    # Step 2: Fresh download from Meta Ads API
    print(f"\n⚠️ IMPORTANT NOTE:")
    print(f"Before proceeding, please update the BRAND_ACCOUNTS dictionary")
    print(f"with your actual Meta Ads account IDs in this script.")
    print(f"\nCurrent placeholder accounts:")
    for brand, account_id in BRAND_ACCOUNTS.items():
        print(f"  {brand}: {account_id}")
    
    proceed = input(f"\nProceed with fresh download? (y/N): ").lower().strip()
    
    if proceed == 'y':
        downloaded_count, download_summary = fresh_download_all_creatives()
        
        # Step 3: Organize assets
        organized_count = organize_downloaded_assets()
        
        # Step 4: Generate fresh inventory
        inventory, json_file, csv_file = generate_fresh_github_inventory()
        
        # Final summary
        print(f"\n🎉 FRESH REPOSITORY SETUP COMPLETE!")
        print(f"=" * 50)
        print(f"📊 Files cleared: {cleared_files} ({cleared_mb:.2f} MB)")
        print(f"📥 Files downloaded: {downloaded_count}")
        print(f"📁 Files organized: {organized_count}")
        print(f"📋 Fresh inventory: {len(inventory)} assets")
        print(f"\n📄 Generated files:")
        print(f"  🔗 {json_file}")
        print(f"  📊 {csv_file}")
        print(f"\n✅ Your repository is now completely fresh with new assets!")
        
    else:
        print(f"\n🛑 Fresh download cancelled.")
        print(f"Repository directories have been cleared.")
        print(f"Update the account IDs and run again when ready.")

if __name__ == "__main__":
    main() 
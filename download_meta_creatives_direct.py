#!/usr/bin/env python3
"""
Download Meta Ad Creatives Directly from Graph API
Update GitHub repository with actual creative assets
"""

import os
import requests
import json
import subprocess
from datetime import datetime
import time
from typing import Dict, List, Optional, Any
from pyairtable import Api

# Configuration
GITHUB_REPO = "https://github.com/lac5q/creative-ads-repository"
RAW_BASE_URL = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"

# Meta API Configuration - Try to get from environment or use the MCP server config
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

# If not in environment, try to read from MCP server config
if not META_ACCESS_TOKEN:
    try:
        with open('meta-ads-mcp-server/.env', 'r') as f:
            for line in f:
                if line.startswith('META_ACCESS_TOKEN=') and not line.startswith('META_ACCESS_TOKEN=your_'):
                    META_ACCESS_TOKEN = line.split('=', 1)[1].strip()
                    break
    except:
        pass

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = "appJlUfKfRBHBvGME"
AIRTABLE_TABLE_NAME = "Creative Ads"

# Account mapping
ACCOUNTS = {
    'TurnedYellow': 'act_2391476931086052',
    'MakeMeJedi': 'act_2957720757845873'
}

def get_meta_access_token():
    """Try to get the Meta access token from various sources"""
    # Try environment variable first
    token = os.getenv('META_ACCESS_TOKEN')
    if token and not token.startswith('your_'):
        return token
    
    # Try reading from MCP server .env file
    env_files = [
        'meta-ads-mcp-server/.env',
        '.env',
        '../.env'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('META_ACCESS_TOKEN=') and not 'your_' in line:
                            token = line.split('=', 1)[1].strip().strip('"\'')
                            if len(token) > 20:  # Valid tokens are much longer
                                return token
            except Exception as e:
                print(f"Error reading {env_file}: {e}")
    
    return None

def make_meta_api_request(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the Meta Graph API"""
    token = get_meta_access_token()
    if not token:
        print("ERROR: No Meta access token found")
        print("Please set META_ACCESS_TOKEN environment variable or update meta-ads-mcp-server/.env")
        return {}
    
    base_url = "https://graph.facebook.com/v22.0"
    url = f"{base_url}/{endpoint}"
    
    default_params = {'access_token': token}
    if params:
        default_params.update(params)
    
    try:
        print(f"Making API request to: {endpoint}")
        response = requests.get(url, params=default_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return {}

def download_image_from_url(image_url: str, filepath: str) -> bool:
    """Download an image from URL and save it to filepath"""
    try:
        print(f"Downloading: {image_url}")
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {image_url}: {e}")
        return False

def get_ad_creative_image_url(ad_id: str) -> Optional[str]:
    """Get the image URL for an ad creative"""
    print(f"\n--- Getting creative for ad {ad_id} ---")
    
    # First get the ad data to find the creative
    ad_data = make_meta_api_request(f"{ad_id}", {
        'fields': 'creative,name,status'
    })
    
    if not ad_data or 'creative' not in ad_data:
        print(f"Could not get creative for ad {ad_id}")
        return None
    
    creative_id = ad_data['creative']['id']
    print(f"Creative ID: {creative_id}")
    
    # Get the creative details
    creative_data = make_meta_api_request(f"{creative_id}", {
        'fields': 'id,name,title,body,image_hash,image_url,video_id,object_story_spec,thumbnail_url'
    })
    
    if not creative_data:
        print(f"Could not get creative data for {creative_id}")
        return None
    
    print(f"Creative data keys: {list(creative_data.keys())}")
    
    # Try to find an image URL
    image_url = None
    
    # Check direct image URL
    if 'image_url' in creative_data and creative_data['image_url']:
        image_url = creative_data['image_url']
        print(f"Found direct image URL: {image_url}")
        return image_url
    
    # Check thumbnail URL
    if 'thumbnail_url' in creative_data and creative_data['thumbnail_url']:
        image_url = creative_data['thumbnail_url']
        print(f"Found thumbnail URL: {image_url}")
        return image_url
    
    # Check object story spec
    if 'object_story_spec' in creative_data:
        story_spec = creative_data['object_story_spec']
        
        # Check link data
        if 'link_data' in story_spec:
            link_data = story_spec['link_data']
            if 'picture' in link_data:
                image_url = link_data['picture']
                print(f"Found image in link_data: {image_url}")
                return image_url
        
        # Check page post data
        if 'page_post_data' in story_spec:
            page_data = story_spec['page_post_data']
            if 'picture' in page_data:
                image_url = page_data['picture']
                print(f"Found image in page_post_data: {image_url}")
                return image_url
    
    # If it's a video, try to get video thumbnail
    if 'video_id' in creative_data and creative_data['video_id']:
        video_id = creative_data['video_id']
        print(f"This is a video creative: {video_id}")
        
        video_data = make_meta_api_request(f"{video_id}", {
            'fields': 'picture,thumbnails'
        })
        
        if video_data and 'picture' in video_data:
            image_url = video_data['picture']
            print(f"Found video thumbnail: {image_url}")
            return image_url
    
    print(f"No image URL found for ad {ad_id}")
    return None

def process_airtable_ads():
    """Get ads from Airtable and try to download their creatives"""
    if not AIRTABLE_API_KEY:
        print("ERROR: AIRTABLE_API_KEY not set in environment")
        return []
    
    try:
        # Connect to Airtable
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Get all records
        records = list(table.all())
        print(f"Found {len(records)} records in Airtable")
        
        downloaded_files = []
        
        for record in records:
            fields = record['fields']
            ad_name = fields.get('Ad_Name', 'Unknown')
            account = fields.get('Account', 'Unknown')
            
            # Try to extract ad ID from various fields
            ad_id = None
            
            # Check if there's an Ad_ID field
            if 'Ad_ID' in fields:
                ad_id = str(fields['Ad_ID'])
            
            # Check Media_Download_URL for ad ID
            elif 'Media_Download_URL' in fields:
                url = fields['Media_Download_URL']
                if 'facebook.com' in url and '_' in url:
                    # Try to extract ID from URL
                    parts = url.split('_')
                    for part in parts:
                        if part.isdigit() and len(part) > 10:
                            ad_id = part
                            break
            
            if not ad_id:
                print(f"No ad ID found for: {ad_name}")
                continue
            
            print(f"\n=== Processing: {ad_name} (ID: {ad_id}) ===")
            
            # Get the image URL
            image_url = get_ad_creative_image_url(ad_id)
            if not image_url:
                continue
            
            # Create safe filename
            safe_name = ad_name.replace('/', '_').replace(':', '_').replace('"', '').replace("'", '')
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '._- ')
            safe_name = safe_name.strip()[:50]  # Limit length
            
            # Determine file extension
            if '.png' in image_url.lower():
                ext = 'png'
            elif '.jpg' in image_url.lower() or '.jpeg' in image_url.lower():
                ext = 'jpg'
            elif '.gif' in image_url.lower():
                ext = 'gif'
            else:
                ext = 'png'  # Default
            
            # Create filepath
            account_dir = account if account in ['TurnedYellow', 'MakeMeJedi'] else 'other'
            filename = f"{ad_id}_{safe_name}.{ext}"
            filepath = f"creative-ads-media/{account_dir}/{filename}"
            
            # Download the image
            if download_image_from_url(image_url, filepath):
                # Create GitHub URL
                github_url = f"{RAW_BASE_URL}/{account_dir}/{filename}"
                downloaded_files.append({
                    'record_id': record['id'],
                    'filepath': filepath,
                    'github_url': github_url,
                    'ad_name': ad_name
                })
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        return downloaded_files
        
    except Exception as e:
        print(f"Error processing Airtable: {e}")
        return []

def update_github_repository():
    """Update GitHub repository with new files"""
    print("\n=== Updating GitHub Repository ===")
    
    os.chdir("creative-ads-media")
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            # Commit and push
            commit_msg = f"Add downloaded Meta ad creatives - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("✅ Repository updated successfully")
            return True
        else:
            print("No new files to commit")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    finally:
        os.chdir("..")

def update_airtable_with_new_urls(downloaded_files: List[Dict]):
    """Update Airtable records with new GitHub URLs"""
    if not downloaded_files or not AIRTABLE_API_KEY:
        return
    
    print(f"\n=== Updating Airtable with {len(downloaded_files)} new URLs ===")
    
    try:
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        for file_info in downloaded_files:
            try:
                # Update the record
                table.update(file_info['record_id'], {
                    'Media_Download_URL': file_info['github_url'],
                    'Asset_Type': 'Real Creative Asset',
                    'Download_Command': f"curl -L -o \"{file_info['ad_name']}.png\" \"{file_info['github_url']}\""
                })
                print(f"✅ Updated: {file_info['ad_name']}")
            except Exception as e:
                print(f"❌ Failed to update {file_info['ad_name']}: {e}")
        
        print("Airtable update completed")
        
    except Exception as e:
        print(f"Error updating Airtable: {e}")

def main():
    """Main function"""
    print("=== Meta Ad Creative Downloader ===")
    
    # Check if we have the required tokens
    if not get_meta_access_token():
        print("❌ Meta access token not found")
        print("Please set META_ACCESS_TOKEN environment variable")
        return
    
    if not AIRTABLE_API_KEY:
        print("❌ Airtable API key not found")
        print("Please set AIRTABLE_API_KEY environment variable")
        return
    
    print("✅ API credentials found")
    
    # Process ads from Airtable
    downloaded_files = process_airtable_ads()
    
    if downloaded_files:
        print(f"\n✅ Successfully downloaded {len(downloaded_files)} creative assets")
        
        # Update GitHub repository
        if update_github_repository():
            # Wait for GitHub to process
            print("Waiting for GitHub to process changes...")
            time.sleep(10)
            
            # Update Airtable with new URLs
            update_airtable_with_new_urls(downloaded_files)
            
            print("\n🎉 Process completed successfully!")
            print(f"Downloaded {len(downloaded_files)} real creative assets")
            print("GitHub repository updated with actual ad creatives")
            print("Airtable updated with working download URLs")
        else:
            print("❌ Failed to update GitHub repository")
    else:
        print("❌ No creative assets were downloaded")

if __name__ == "__main__":
    main() 
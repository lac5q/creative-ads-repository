#!/usr/bin/env python3
"""
Download Actual Ad Creatives from Meta Ads API
Fix GitHub repository with real media files instead of placeholders
"""

import os
import json
import requests
import base64
from io import BytesIO
from PIL import Image
import subprocess
from datetime import datetime
import time
from typing import Dict, List, Optional, Any

# Meta Ads API configuration
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    print("ERROR: META_ACCESS_TOKEN environment variable not set")
    print("Please set your Meta Ads API access token:")
    print("export META_ACCESS_TOKEN='your_token_here'")
    exit(1)

# Account IDs from the API response
ACCOUNTS = {
    'TurnedYellow': 'act_2391476931086052',
    'MakeMeJedi': 'act_2957720757845873'
}

# Ad IDs we want to download (from the API responses above)
TARGET_ADS = {
    # TurnedYellow ads
    '120207192312690108': {'name': 'video: influencer David / Most incredible', 'account': 'TurnedYellow'},
    '120205926791290108': {'name': 'video: Gifting hook 1 (Sara) / Life is too short', 'account': 'TurnedYellow'},
    '120203471547490108': {'name': 'video: ty video 1 / Make anyone laugh', 'account': 'TurnedYellow'},
    '120213125762460108': {'name': 'video: Early BF gifs&boomerangs / Get up to 70% off', 'account': 'TurnedYellow'},
    '120224359442580108': {'name': 'image: Father\'s day 2025 - 1 / Gift Dad', 'account': 'TurnedYellow'},
    '120213125622300108': {'name': 'image: Early BF images 1 / Get up to 70% off', 'account': 'TurnedYellow'},
    
    # MakeMeJedi ads
    '120204695398070354': {'name': 'video: agency hook "Birthday" / transform', 'account': 'MakeMeJedi'},
    '120204514881640354': {'name': 'video: FD 1 remake / A long time ago', 'account': 'MakeMeJedi'},
    '120205316284580354': {'name': 'video: V day (reaction) 4 / This Valentine\'s Day', 'account': 'MakeMeJedi'},
    '120215085545760354': {'name': 'video: Early BF / Enjoy up to 75% OFF', 'account': 'MakeMeJedi'},
    '120222552375440354': {'name': 'video: FD 2 remake / A long time ago [pdp]', 'account': 'MakeMeJedi'},
    '120210978877980354': {'name': 'image: Celebrate Father\'s Day - up to 70 off!.png (FD2024)', 'account': 'MakeMeJedi'},
    '120214266364150354': {'name': 'image: couple / Become a Jedi (70%)', 'account': 'MakeMeJedi'},
}

def make_api_request(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the Meta Graph API"""
    base_url = "https://graph.facebook.com/v22.0"
    url = f"{base_url}/{endpoint}"
    
    default_params = {'access_token': ACCESS_TOKEN}
    if params:
        default_params.update(params)
    
    try:
        response = requests.get(url, params=default_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return {}

def get_ad_creative_data(ad_id: str) -> Dict[str, Any]:
    """Get creative data for a specific ad"""
    print(f"Getting creative data for ad {ad_id}...")
    
    # First get the ad to find the creative ID
    ad_data = make_api_request(f"{ad_id}", {
        'fields': 'creative,name,status'
    })
    
    if not ad_data or 'creative' not in ad_data:
        print(f"Could not get creative ID for ad {ad_id}")
        return {}
    
    creative_id = ad_data['creative']['id']
    print(f"Found creative ID: {creative_id}")
    
    # Get the creative details
    creative_data = make_api_request(f"{creative_id}", {
        'fields': 'id,name,title,body,call_to_action_type,image_hash,image_url,video_id,object_story_spec,link_url,thumbnail_url'
    })
    
    return creative_data

def download_image_from_url(image_url: str, filename: str) -> bool:
    """Download an image from URL and save it"""
    try:
        print(f"Downloading image from: {image_url}")
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Save the image
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False

def sanitize_filename(name: str) -> str:
    """Create a safe filename from ad name"""
    # Remove problematic characters
    safe_name = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe_name = safe_name.replace('"', '').replace("'", '').replace('?', '')
    safe_name = safe_name.replace('<', '').replace('>', '').replace('|', '')
    safe_name = safe_name.replace('*', '').replace('\n', ' ').replace('\r', ' ')
    
    # Limit length and clean up spaces
    safe_name = ' '.join(safe_name.split())  # Remove extra whitespace
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    
    return safe_name.strip()

def process_ad_creative(ad_id: str, ad_info: Dict[str, str]) -> Optional[str]:
    """Process a single ad creative and download media"""
    print(f"\n=== Processing Ad: {ad_id} ===")
    print(f"Name: {ad_info['name']}")
    print(f"Account: {ad_info['account']}")
    
    # Get creative data
    creative_data = get_ad_creative_data(ad_id)
    if not creative_data:
        print(f"Failed to get creative data for {ad_id}")
        return None
    
    print(f"Creative data keys: {list(creative_data.keys())}")
    
    # Try to find an image URL
    image_url = None
    file_extension = 'png'
    
    # Check different possible image URL fields
    for field in ['image_url', 'thumbnail_url']:
        if field in creative_data and creative_data[field]:
            image_url = creative_data[field]
            print(f"Found image URL in {field}: {image_url}")
            break
    
    # Check object_story_spec for more complex creatives
    if not image_url and 'object_story_spec' in creative_data:
        story_spec = creative_data['object_story_spec']
        if 'link_data' in story_spec:
            link_data = story_spec['link_data']
            if 'picture' in link_data:
                image_url = link_data['picture']
                print(f"Found image URL in object_story_spec: {image_url}")
            elif 'image_hash' in link_data:
                # For image hash, we need to construct the URL
                image_hash = link_data['image_hash']
                account_id = ACCOUNTS[ad_info['account']]
                image_url = f"https://graph.facebook.com/v22.0/{account_id}/adimages?hashes=[%22{image_hash}%22]&access_token={ACCESS_TOKEN}"
                print(f"Constructed image URL from hash: {image_url}")
    
    # Check for video
    if 'video_id' in creative_data and creative_data['video_id']:
        print(f"This is a video creative with video_id: {creative_data['video_id']}")
        # For videos, we might get a thumbnail
        if not image_url:
            video_id = creative_data['video_id']
            # Try to get video thumbnail
            video_data = make_api_request(f"{video_id}", {
                'fields': 'picture,thumbnails'
            })
            if video_data and 'picture' in video_data:
                image_url = video_data['picture']
                print(f"Found video thumbnail: {image_url}")
    
    if not image_url:
        print(f"No image URL found for ad {ad_id}")
        return None
    
    # Create filename
    safe_name = sanitize_filename(ad_info['name'])
    account_name = ad_info['account']
    
    # Determine if it's an image or video from the name
    if 'video:' in ad_info['name'].lower():
        filename = f"{ad_id}_{safe_name}_video_thumbnail.{file_extension}"
    else:
        filename = f"{ad_id}_{safe_name}_image.{file_extension}"
    
    # Create account directory
    account_dir = f"creative-ads-media/{account_name}"
    os.makedirs(account_dir, exist_ok=True)
    
    filepath = os.path.join(account_dir, filename)
    
    # Download the image
    if download_image_from_url(image_url, filepath):
        return filepath
    else:
        return None

def update_github_repository():
    """Update the GitHub repository with new files"""
    print("\n=== Updating GitHub Repository ===")
    
    os.chdir("creative-ads-media")
    
    # Add all new files
    subprocess.run(["git", "add", "."], check=True)
    
    # Check if there are changes to commit
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        # Commit changes
        commit_message = f"Add actual ad creatives downloaded from Meta Ads API - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed updates to GitHub!")
    else:
        print("No changes to commit")

def main():
    """Main function to download all ad creatives"""
    print("=== Meta Ads Creative Downloader ===")
    print(f"Target ads: {len(TARGET_ADS)}")
    
    downloaded_files = []
    failed_ads = []
    
    for ad_id, ad_info in TARGET_ADS.items():
        try:
            filepath = process_ad_creative(ad_id, ad_info)
            if filepath:
                downloaded_files.append(filepath)
                print(f"✅ Successfully processed: {ad_id}")
            else:
                failed_ads.append(ad_id)
                print(f"❌ Failed to process: {ad_id}")
        except Exception as e:
            print(f"❌ Error processing {ad_id}: {e}")
            failed_ads.append(ad_id)
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    print(f"\n=== Download Summary ===")
    print(f"Successfully downloaded: {len(downloaded_files)} files")
    print(f"Failed downloads: {len(failed_ads)} ads")
    
    if downloaded_files:
        print("\nDownloaded files:")
        for filepath in downloaded_files:
            print(f"  - {filepath}")
    
    if failed_ads:
        print("\nFailed ads:")
        for ad_id in failed_ads:
            print(f"  - {ad_id}: {TARGET_ADS[ad_id]['name']}")
    
    # Update GitHub repository if we have new files
    if downloaded_files:
        try:
            update_github_repository()
        except Exception as e:
            print(f"Failed to update GitHub repository: {e}")
    
    print("\n=== Process Complete ===")

if __name__ == "__main__":
    main() 
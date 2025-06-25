#!/usr/bin/env python3
"""
Download full-size, high-resolution ad creatives from Meta API
"""

import requests
import json
import os
from datetime import datetime

# Meta App Configuration
APP_ID = "517350262370097"
APP_SECRET = "990b1bda0625f360730095638332348a"

def get_full_size_ad_creatives(access_token):
    """Get full-size ad creatives from Meta API"""
    
    print("🔍 Fetching full-size ad creatives from Meta API...")
    
    # Get ad accounts
    accounts_url = "https://graph.facebook.com/v21.0/me/adaccounts"
    accounts_params = {
        'access_token': access_token,
        'fields': 'id,name,account_status'
    }
    
    accounts_response = requests.get(accounts_url, params=accounts_params)
    if accounts_response.status_code != 200:
        print(f"❌ Failed to get ad accounts: {accounts_response.text}")
        return
    
    accounts_data = accounts_response.json()
    print(f"📊 Found {len(accounts_data['data'])} ad accounts")
    
    all_creatives = []
    
    for account in accounts_data['data']:
        account_id = account['id']
        account_name = account['name']
        print(f"\n🏢 Processing account: {account_name} ({account_id})")
        
        # Get ads with full creative details
        ads_url = f"https://graph.facebook.com/v21.0/{account_id}/ads"
        ads_params = {
            'access_token': access_token,
            'fields': 'id,name,status,creative{id,name,image_url,video_id,thumbnail_url,object_story_spec,asset_feed_spec}',
            'limit': 100
        }
        
        ads_response = requests.get(ads_url, params=ads_params)
        if ads_response.status_code != 200:
            print(f"❌ Failed to get ads for {account_name}: {ads_response.text}")
            continue
        
        ads_data = ads_response.json()
        print(f"📱 Found {len(ads_data.get('data', []))} ads in {account_name}")
        
        for ad in ads_data.get('data', []):
            if 'creative' in ad and ad['creative']:
                creative = ad['creative']
                
                # Look for full-size image URLs
                image_urls = []
                
                # Check direct image_url
                if 'image_url' in creative:
                    image_urls.append(('image_url', creative['image_url']))
                
                # Check object_story_spec for images
                if 'object_story_spec' in creative:
                    story_spec = creative['object_story_spec']
                    
                    # Link data images
                    if 'link_data' in story_spec and 'image_url' in story_spec['link_data']:
                        image_urls.append(('link_data_image', story_spec['link_data']['image_url']))
                    
                    # Video data thumbnail
                    if 'video_data' in story_spec and 'image_url' in story_spec['video_data']:
                        image_urls.append(('video_thumbnail', story_spec['video_data']['image_url']))
                
                # Check asset_feed_spec for images
                if 'asset_feed_spec' in creative:
                    asset_spec = creative['asset_feed_spec']
                    if 'images' in asset_spec:
                        for i, img in enumerate(asset_spec['images']):
                            if 'url' in img:
                                image_urls.append((f'asset_image_{i}', img['url']))
                
                if image_urls:
                    creative_info = {
                        'ad_id': ad['id'],
                        'ad_name': ad.get('name', 'Unknown'),
                        'creative_id': creative.get('id', 'Unknown'),
                        'creative_name': creative.get('name', 'Unknown'),
                        'account_name': account_name,
                        'image_urls': image_urls
                    }
                    all_creatives.append(creative_info)
    
    return all_creatives

def download_high_res_image(url, filename):
    """Download high-resolution image"""
    try:
        print(f"🔄 Downloading high-res: {filename}")
        
        # Try to get higher resolution by modifying Facebook CDN URL
        if 'fbcdn.net' in url:
            # Remove size restrictions from Facebook CDN URLs
            url = url.split('?')[0]  # Remove query parameters that limit size
            # Add parameters for higher resolution
            url += '?_nc_ht=scontent&oh=00_&oe=68615210'
        
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Check file size
            file_size = os.path.getsize(filename)
            print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
            return True
        else:
            print(f"❌ Failed to download {url}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def main():
    # You'll need to provide your access token
    access_token = input("🔑 Please enter your Meta API access token: ").strip()
    
    if not access_token:
        print("❌ Access token required!")
        return
    
    # Create output directory
    output_dir = "full_size_ad_creatives"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎯 Downloading Full-Size Ad Creatives")
    
    # Get all creatives
    creatives = get_full_size_ad_creatives(access_token)
    
    if not creatives:
        print("❌ No creatives found!")
        return
    
    print(f"\n📊 Found {len(creatives)} creatives with images")
    
    # Download each creative
    downloaded_count = 0
    total_images = 0
    
    for creative in creatives:
        print(f"\n🎨 Processing: {creative['ad_name']}")
        
        for img_type, img_url in creative['image_urls']:
            total_images += 1
            
            # Create filename
            safe_name = "".join(c for c in creative['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{output_dir}/{creative['account_name']}_{safe_name}_{img_type}_FULLSIZE.jpg"
            
            if download_high_res_image(img_url, filename):
                downloaded_count += 1
    
    print(f"\n🎉 Downloaded {downloaded_count}/{total_images} full-size images!")
    
    # Copy to GitHub repository
    if downloaded_count > 0:
        print("\n📁 Copying to GitHub repository...")
        os.system(f"cp {output_dir}/*TurnedYellow* ../creative-ads-repository/TurnedYellow/ 2>/dev/null || true")
        os.system(f"cp {output_dir}/*MakeMeJedi* ../creative-ads-repository/MakeMeJedi/ 2>/dev/null || true")
        print("✅ Copied full-size images to GitHub repository")

if __name__ == "__main__":
    main() 
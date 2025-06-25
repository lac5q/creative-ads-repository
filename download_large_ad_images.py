#!/usr/bin/env python3
"""
Download full-size ad creative images directly from Meta API
"""

import requests
import os
import json
from datetime import datetime

# Meta App Configuration
APP_ID = "517350262370097"
APP_SECRET = "990b1bda0625f360730095638332348a"

def get_ad_creative_image_url(ad_id, access_token):
    """Get the full-size image URL for an ad creative"""
    try:
        # First get the ad details
        ad_url = f"https://graph.facebook.com/v21.0/{ad_id}"
        ad_params = {
            'access_token': access_token,
            'fields': 'creative{id,name,image_url,image_hash,thumbnail_url,object_story_spec,asset_feed_spec}'
        }
        
        ad_response = requests.get(ad_url, params=ad_params)
        if ad_response.status_code != 200:
            print(f"❌ Failed to get ad {ad_id}: {ad_response.text}")
            return None
        
        ad_data = ad_response.json()
        
        if 'creative' not in ad_data:
            print(f"❌ No creative found for ad {ad_id}")
            return None
        
        creative = ad_data['creative']
        print(f"🎨 Creative ID: {creative.get('id', 'Unknown')}")
        print(f"📝 Creative Name: {creative.get('name', 'Unknown')}")
        
        # Try to get the image URL from various sources
        image_urls = []
        
        # Direct image_url
        if 'image_url' in creative:
            image_urls.append(('direct_image', creative['image_url']))
        
        # Thumbnail URL (often higher quality than expected)
        if 'thumbnail_url' in creative:
            image_urls.append(('thumbnail', creative['thumbnail_url']))
        
        # Object story spec images
        if 'object_story_spec' in creative:
            story_spec = creative['object_story_spec']
            
            # Link data image
            if 'link_data' in story_spec and 'image_url' in story_spec['link_data']:
                image_urls.append(('link_data', story_spec['link_data']['image_url']))
            
            # Video data image
            if 'video_data' in story_spec and 'image_url' in story_spec['video_data']:
                image_urls.append(('video_data', story_spec['video_data']['image_url']))
        
        # Asset feed spec images
        if 'asset_feed_spec' in creative:
            asset_spec = creative['asset_feed_spec']
            if 'images' in asset_spec:
                for i, img in enumerate(asset_spec['images']):
                    if 'url' in img:
                        image_urls.append((f'asset_{i}', img['url']))
        
        # If we have an image_hash, try to construct the full URL
        if 'image_hash' in creative:
            hash_url = f"https://scontent.xx.fbcdn.net/v/t45.1600-4/{creative['image_hash']}_n.jpg"
            image_urls.append(('hash_constructed', hash_url))
        
        return image_urls
        
    except Exception as e:
        print(f"❌ Error getting creative for ad {ad_id}: {str(e)}")
        return None

def download_image_full_size(url, filename):
    """Download image at full resolution"""
    try:
        print(f"🔄 Downloading: {filename}")
        print(f"🔗 URL: {url}")
        
        # Try to get the highest resolution by modifying Facebook CDN URLs
        if 'fbcdn.net' in url:
            # Remove size restrictions and get original
            base_url = url.split('?')[0]
            # Try different approaches to get full size
            full_size_urls = [
                base_url,  # Original without parameters
                base_url.replace('_s.', '_o.'),  # Small to original
                base_url.replace('_n.', '_o.'),  # Normal to original
                base_url.replace('_t.', '_o.'),  # Thumbnail to original
                url  # Fallback to original URL
            ]
        else:
            full_size_urls = [url]
        
        for attempt_url in full_size_urls:
            try:
                response = requests.get(attempt_url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = os.path.getsize(filename)
                    print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
                    
                    # If it's larger than 50KB, it's probably a good quality image
                    if file_size > 50000:
                        print(f"🎉 High quality image! ({file_size/1024:.1f} KB)")
                        return True
                    elif file_size > 5000:
                        print(f"📸 Standard quality image ({file_size/1024:.1f} KB)")
                        return True
                    else:
                        print(f"⚠️ Small image, trying next URL...")
                        continue
                        
            except Exception as e:
                print(f"❌ Failed to download from {attempt_url}: {str(e)}")
                continue
        
        return False
        
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def main():
    print("🎯 Downloading Large Ad Creative Images")
    
    # Get access token
    access_token = input("🔑 Please enter your Meta API access token: ").strip()
    
    if not access_token:
        print("❌ Access token required!")
        return
    
    # Create output directory
    output_dir = "large_ad_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # TurnedYellow ad IDs from your CSV
    ad_data = [
        ("120207192312690108", "01_David_Influencer_WINNER"),
        ("120203471547490108", "02_TY_Video_1_HIGH_HOOK"),
        ("120208078497390108", "03_Royal_Inspo_Hook_STRONG"),
        ("120213125762460108", "04_Early_BF_Gifs_Boomerangs")
    ]
    
    print(f"📊 Processing {len(ad_data)} TurnedYellow ads")
    
    downloaded_count = 0
    total_attempts = 0
    
    for ad_id, ad_name in ad_data:
        print(f"\n🎨 Processing: {ad_name} (ID: {ad_id})")
        
        # Get image URLs for this ad
        image_urls = get_ad_creative_image_url(ad_id, access_token)
        
        if not image_urls:
            print(f"❌ No image URLs found for {ad_name}")
            continue
        
        print(f"🔍 Found {len(image_urls)} image sources")
        
        # Try each image URL
        for img_type, img_url in image_urls:
            total_attempts += 1
            filename = f"{output_dir}/{ad_name}_{img_type}_LARGE.jpg"
            
            if download_image_full_size(img_url, filename):
                downloaded_count += 1
                break  # Stop after first successful download for this ad
    
    print(f"\n🎉 Downloaded {downloaded_count} large images from {total_attempts} attempts!")
    
    # Copy best images to GitHub repository
    if downloaded_count > 0:
        print("\n📁 Copying to GitHub repository...")
        
        # Copy all large images to the repository
        for file in os.listdir(output_dir):
            if file.endswith('_LARGE.jpg'):
                src = os.path.join(output_dir, file)
                dst = f"creative-ads-repository/TurnedYellow/{file}"
                
                try:
                    import shutil
                    shutil.copy2(src, dst)
                    print(f"✅ Copied {file} to repository")
                except Exception as e:
                    print(f"❌ Failed to copy {file}: {str(e)}")
        
        print("✅ Copied large images to GitHub repository")
        
        # Show file sizes
        print("\n📊 Downloaded file sizes:")
        for file in os.listdir(output_dir):
            if os.path.isfile(os.path.join(output_dir, file)):
                size = os.path.getsize(os.path.join(output_dir, file))
                print(f"  {file}: {size:,} bytes ({size/1024:.1f} KB)")

if __name__ == "__main__":
    main() 
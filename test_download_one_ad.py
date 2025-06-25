#!/usr/bin/env python3
"""
Test script to download one ad creative
"""

import os
import requests
import json

# Configuration
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
TEST_AD_ID = "120207192312690108"  # TurnedYellow ad

def test_meta_api():
    """Test Meta API access"""
    print("Testing Meta API access...")
    
    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not set")
        return False
    
    print(f"Token: {META_ACCESS_TOKEN[:20]}...")
    
    # Test basic API access
    url = "https://graph.facebook.com/v22.0/me"
    params = {'access_token': META_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"✅ API access working. User: {data.get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ API access failed: {e}")
        return False

def get_ad_creative_url(ad_id):
    """Get creative URL for a specific ad"""
    print(f"\nGetting creative for ad {ad_id}...")
    
    # Get ad data
    url = f"https://graph.facebook.com/v22.0/{ad_id}"
    params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'creative,name,status'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        ad_data = response.json()
        
        print(f"Ad name: {ad_data.get('name', 'Unknown')}")
        print(f"Ad status: {ad_data.get('status', 'Unknown')}")
        
        if 'creative' not in ad_data:
            print("❌ No creative found in ad data")
            return None
        
        creative_id = ad_data['creative']['id']
        print(f"Creative ID: {creative_id}")
        
        # Get creative data
        creative_url = f"https://graph.facebook.com/v22.0/{creative_id}"
        creative_params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'id,name,title,body,image_hash,image_url,video_id,object_story_spec,thumbnail_url'
        }
        
        creative_response = requests.get(creative_url, params=creative_params)
        creative_response.raise_for_status()
        creative_data = creative_response.json()
        
        print(f"Creative data keys: {list(creative_data.keys())}")
        
        # Look for image URL
        image_url = None
        
        if 'image_url' in creative_data:
            image_url = creative_data['image_url']
            print(f"Found direct image URL: {image_url}")
        elif 'thumbnail_url' in creative_data:
            image_url = creative_data['thumbnail_url']
            print(f"Found thumbnail URL: {image_url}")
        elif 'object_story_spec' in creative_data:
            story_spec = creative_data['object_story_spec']
            if 'link_data' in story_spec and 'picture' in story_spec['link_data']:
                image_url = story_spec['link_data']['picture']
                print(f"Found image in link_data: {image_url}")
        
        if not image_url and 'video_id' in creative_data:
            video_id = creative_data['video_id']
            print(f"This is a video creative: {video_id}")
            
            # Get video thumbnail
            video_url = f"https://graph.facebook.com/v22.0/{video_id}"
            video_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'picture,thumbnails'
            }
            
            video_response = requests.get(video_url, params=video_params)
            if video_response.status_code == 200:
                video_data = video_response.json()
                if 'picture' in video_data:
                    image_url = video_data['picture']
                    print(f"Found video thumbnail: {image_url}")
        
        return image_url
        
    except Exception as e:
        print(f"❌ Error getting creative: {e}")
        return None

def download_image(image_url, filename):
    """Download image from URL"""
    print(f"\nDownloading image...")
    print(f"URL: {image_url}")
    print(f"File: {filename}")
    
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create directory
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check file size
        file_size = os.path.getsize(filename)
        print(f"✅ Downloaded successfully: {file_size} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Test Download One Ad Creative ===")
    
    # Test API access
    if not test_meta_api():
        return
    
    # Get creative URL
    image_url = get_ad_creative_url(TEST_AD_ID)
    if not image_url:
        print("❌ Could not get image URL")
        return
    
    # Download image
    filename = f"test_downloads/{TEST_AD_ID}_test.png"
    if download_image(image_url, filename):
        print(f"\n🎉 Success! Downloaded ad creative to: {filename}")
        
        # Show file info
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"File size: {size:,} bytes")
    else:
        print("❌ Download failed")

if __name__ == "__main__":
    main() 
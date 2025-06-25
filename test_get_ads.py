#!/usr/bin/env python3
"""
Test script to get available ads from Meta accounts
"""

import os
import requests
import json

# Configuration
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
ACCOUNTS = {
    'TurnedYellow': 'act_2391476931086052',
    'MakeMeJedi': 'act_2957720757845873'
}

def get_ads_from_account(account_id, account_name):
    """Get ads from a specific account"""
    print(f"\n=== Getting ads from {account_name} ({account_id}) ===")
    
    url = f"https://graph.facebook.com/v22.0/{account_id}/ads"
    params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'id,name,status,creative',
        'limit': 10
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        ads = data.get('data', [])
        print(f"Found {len(ads)} ads:")
        
        for i, ad in enumerate(ads[:5]):  # Show first 5
            print(f"  {i+1}. ID: {ad['id']}")
            print(f"     Name: {ad.get('name', 'No name')}")
            print(f"     Status: {ad.get('status', 'Unknown')}")
            if 'creative' in ad:
                print(f"     Creative ID: {ad['creative']['id']}")
            print()
        
        return ads
        
    except Exception as e:
        print(f"❌ Error getting ads: {e}")
        return []

def test_creative_download(ad_id, ad_name):
    """Test downloading creative for a specific ad"""
    print(f"\n=== Testing creative download for {ad_name} ===")
    print(f"Ad ID: {ad_id}")
    
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
        
        print(f"✅ Ad data retrieved")
        print(f"   Name: {ad_data.get('name', 'Unknown')}")
        print(f"   Status: {ad_data.get('status', 'Unknown')}")
        
        if 'creative' not in ad_data:
            print("❌ No creative found")
            return False
        
        creative_id = ad_data['creative']['id']
        print(f"   Creative ID: {creative_id}")
        
        # Get creative data
        creative_url = f"https://graph.facebook.com/v22.0/{creative_id}"
        creative_params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'id,name,image_url,video_id,object_story_spec,thumbnail_url'
        }
        
        creative_response = requests.get(creative_url, params=creative_params)
        creative_response.raise_for_status()
        creative_data = creative_response.json()
        
        print(f"✅ Creative data retrieved")
        print(f"   Available fields: {list(creative_data.keys())}")
        
        # Look for image URLs
        image_urls = []
        
        if 'image_url' in creative_data:
            image_urls.append(('Direct image URL', creative_data['image_url']))
        
        if 'thumbnail_url' in creative_data:
            image_urls.append(('Thumbnail URL', creative_data['thumbnail_url']))
        
        if 'object_story_spec' in creative_data:
            story_spec = creative_data['object_story_spec']
            if 'link_data' in story_spec and 'picture' in story_spec['link_data']:
                image_urls.append(('Link data picture', story_spec['link_data']['picture']))
        
        if 'video_id' in creative_data:
            video_id = creative_data['video_id']
            print(f"   Video ID: {video_id}")
            
            # Try to get video thumbnail
            video_url = f"https://graph.facebook.com/v22.0/{video_id}"
            video_params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'picture'
            }
            
            try:
                video_response = requests.get(video_url, params=video_params)
                if video_response.status_code == 200:
                    video_data = video_response.json()
                    if 'picture' in video_data:
                        image_urls.append(('Video thumbnail', video_data['picture']))
            except:
                pass
        
        print(f"   Found {len(image_urls)} potential image URLs:")
        for url_type, url in image_urls:
            print(f"     - {url_type}: {url}")
        
        return len(image_urls) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return False

def main():
    """Main function"""
    print("=== Meta Ads API Test ===")
    
    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not set")
        return
    
    print(f"Token: {META_ACCESS_TOKEN[:20]}...")
    
    all_ads = []
    
    # Get ads from both accounts
    for account_name, account_id in ACCOUNTS.items():
        ads = get_ads_from_account(account_id, account_name)
        all_ads.extend(ads)
    
    if not all_ads:
        print("❌ No ads found")
        return
    
    # Test creative download for first few ads
    print("\n" + "="*60)
    print("TESTING CREATIVE DOWNLOADS")
    print("="*60)
    
    for i, ad in enumerate(all_ads[:3]):  # Test first 3 ads
        success = test_creative_download(ad['id'], ad.get('name', f'Ad {i+1}'))
        if success:
            print(f"✅ Creative download test passed for ad {ad['id']}")
        else:
            print(f"❌ Creative download test failed for ad {ad['id']}")
        print("-" * 40)

if __name__ == "__main__":
    main() 
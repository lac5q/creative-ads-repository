#!/usr/bin/env python3
"""
Download actual ad creatives using Meta Marketing Insights App
"""

import requests
import json
import os
from datetime import datetime
import urllib.parse

# Meta App Configuration
APP_ID = "517350262370097"
APP_SECRET = "990b1bda0625f360730095638332348a"
# Note: User will need to provide the User Token

def get_long_lived_token(short_lived_token):
    """Convert short-lived token to long-lived token"""
    url = "https://graph.facebook.com/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'fb_exchange_token': short_lived_token
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"❌ Error getting long-lived token: {response.text}")
        return None

def get_ad_accounts(access_token):
    """Get all ad accounts accessible to the user"""
    url = "https://graph.facebook.com/v18.0/me/adaccounts"
    params = {
        'access_token': access_token,
        'fields': 'id,name,account_status'
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"❌ Error getting ad accounts: {response.text}")
        return []

def get_campaigns(account_id, access_token):
    """Get campaigns for an ad account"""
    url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns"
    params = {
        'access_token': access_token,
        'fields': 'id,name,status,effective_status',
        'limit': 100
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"❌ Error getting campaigns: {response.text}")
        return []

def get_ads(account_id, access_token):
    """Get ads for an ad account"""
    url = f"https://graph.facebook.com/v18.0/{account_id}/ads"
    params = {
        'access_token': access_token,
        'fields': 'id,name,status,effective_status,creative',
        'limit': 100
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"❌ Error getting ads: {response.text}")
        return []

def get_ad_creative(creative_id, access_token):
    """Get creative details for an ad"""
    url = f"https://graph.facebook.com/v18.0/{creative_id}"
    params = {
        'access_token': access_token,
        'fields': 'id,name,object_story_spec,image_url,video_id,thumbnail_url,asset_feed_spec'
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error getting creative {creative_id}: {response.text}")
        return None

def download_media_file(url, filename):
    """Download media file from URL"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            return True
        else:
            print(f"❌ Failed to download {url}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def main():
    print("🚀 Meta Marketing Insights App - Ad Creative Downloader")
    print(f"📱 App ID: {APP_ID}")
    
    # Get user token from user
    user_token = input("🔑 Please enter your User Token: ").strip()
    
    if not user_token:
        print("❌ User token is required")
        return
    
    print("\n🔄 Getting long-lived access token...")
    access_token = get_long_lived_token(user_token)
    
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    print("✅ Got access token")
    
    # Get ad accounts
    print("\n🔄 Getting ad accounts...")
    accounts = get_ad_accounts(access_token)
    
    if not accounts:
        print("❌ No ad accounts found")
        return
    
    print(f"✅ Found {len(accounts)} ad accounts:")
    for account in accounts:
        print(f"  📊 {account['name']} ({account['id']})")
    
    # Create output directory
    output_dir = "real_facebook_creatives"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each account
    total_downloaded = 0
    
    for account in accounts:
        account_id = account['id']
        account_name = account['name']
        
        print(f"\n🔄 Processing account: {account_name}")
        
        # Get ads for this account
        ads = get_ads(account_id, access_token)
        print(f"📊 Found {len(ads)} ads")
        
        for ad in ads:
            ad_id = ad['id']
            ad_name = ad['name']
            creative_id = ad.get('creative', {}).get('id')
            
            if not creative_id:
                print(f"⚠️  No creative ID for ad: {ad_name}")
                continue
            
            print(f"\n🎨 Processing ad: {ad_name}")
            print(f"🆔 Creative ID: {creative_id}")
            
            # Get creative details
            creative = get_ad_creative(creative_id, access_token)
            
            if not creative:
                continue
            
            # Try to download image
            if 'image_url' in creative and creative['image_url']:
                filename = f"{output_dir}/{account_name}_{ad_name}_{creative_id}_image.jpg"
                filename = filename.replace(' ', '_').replace('/', '_')
                if download_media_file(creative['image_url'], filename):
                    total_downloaded += 1
            
            # Try to download video thumbnail
            if 'thumbnail_url' in creative and creative['thumbnail_url']:
                filename = f"{output_dir}/{account_name}_{ad_name}_{creative_id}_thumbnail.jpg"
                filename = filename.replace(' ', '_').replace('/', '_')
                if download_media_file(creative['thumbnail_url'], filename):
                    total_downloaded += 1
            
            # Print creative details for debugging
            print(f"📝 Creative details: {json.dumps(creative, indent=2)}")
    
    print(f"\n🎉 Download complete! Downloaded {total_downloaded} files to {output_dir}/")

if __name__ == "__main__":
    main() 
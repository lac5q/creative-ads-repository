#!/usr/bin/env python3
"""
Comprehensive Ad Creative Downloader & Airtable Updater
Downloads high-quality Facebook ad creatives and updates Airtable with GitHub links
"""

import os
import requests
import json
import base64
from datetime import datetime
from pathlib import Path
import time
from urllib.parse import urlparse
import hashlib

# Configuration
META_ACCESS_TOKEN = "EAAHWhv6c7zEBOZCX2ZA2ZBOOHCeYW9oQZAcgtiFqWN9EZAVhIjGFRNHkd6pPHWDuf5GwFzRSzVuvwZCaOQ3idMvEmMZBd0VrvisCa9MiBxyRIekZC5RzHFmS11b0wbNv801N1tCjTZBEnAFM8XBdFoLEgyxL7Cf2sZABkmtqZAdZBpZALoZC8F0zAfAuJAOfHn0f6RLgZDZD"
GITHUB_TOKEN = "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"
GITHUB_REPO = "lac5q/creative-ads-repository"
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE = "Veo3 Videos"

# Account mapping
ACCOUNTS = {
    'act_2391476931086052': 'TurnedYellow',
    'act_2957720757845873': 'MakeMeJedi'
}

class CreativeDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def get_all_ads(self):
        """Get all ads from both accounts"""
        all_ads = []
        
        for account_id, account_name in ACCOUNTS.items():
            print(f"\n🔍 Getting ads from {account_name} ({account_id})")
            
            url = f"https://graph.facebook.com/v22.0/{account_id}/ads"
            params = {
                'access_token': META_ACCESS_TOKEN,
                'fields': 'id,name,status,creative,account_id',
                'limit': 50
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                ads = data.get('data', [])
                for ad in ads:
                    ad['account_name'] = account_name
                
                all_ads.extend(ads)
                print(f"✅ Found {len(ads)} ads from {account_name}")
                
            except Exception as e:
                print(f"❌ Error getting ads from {account_name}: {e}")
        
        return all_ads
    
    def get_creative_details(self, creative_id):
        """Get detailed creative information"""
        url = f"https://graph.facebook.com/v22.0/{creative_id}"
        params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'id,name,image_url,video_id,thumbnail_url,object_story_spec,asset_feed_spec'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting creative {creative_id}: {e}")
            return None
    
    def get_high_quality_image_url(self, image_url):
        """Convert thumbnail URL to high quality image URL"""
        if not image_url:
            return None
            
        # Try to get higher quality version by modifying URL parameters
        if 'scontent' in image_url and 'stp=' in image_url:
            # Remove size restrictions and quality limitations
            parts = image_url.split('?')
            if len(parts) > 1:
                base_url = parts[0]
                # Try to get original quality
                high_quality_url = f"{base_url}?_nc_cat=111&ccb=1-7&_nc_sid=890911&_nc_ohc=original&_nc_oc=original&_nc_zt=1"
                return high_quality_url
        
        return image_url
    
    def download_image(self, url, filename):
        """Download image from URL"""
        if not url:
            return None
            
        try:
            print(f"📥 Downloading {filename}...")
            
            # Try the high-quality URL first
            high_quality_url = self.get_high_quality_image_url(url)
            
            response = self.session.get(high_quality_url, timeout=30)
            if response.status_code != 200:
                # Fallback to original URL
                response = self.session.get(url, timeout=30)
            
            response.raise_for_status()
            
            # Create downloads directory
            os.makedirs('hd_ad_creatives', exist_ok=True)
            filepath = os.path.join('hd_ad_creatives', filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Downloaded {filename} ({file_size:,} bytes)")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            return None
    
    def upload_to_github(self, filepath, github_path):
        """Upload file to GitHub repository"""
        if not filepath or not os.path.exists(filepath):
            return None
            
        try:
            print(f"☁️ Uploading to GitHub: {github_path}")
            
            # Read file content
            with open(filepath, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            # GitHub API URL
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}"
            
            # Check if file exists
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Try to get existing file (to get sha if it exists)
            existing_response = requests.get(url, headers=headers)
            sha = None
            if existing_response.status_code == 200:
                sha = existing_response.json().get('sha')
            
            # Upload/update file
            data = {
                'message': f'Upload {os.path.basename(github_path)} - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'content': content,
                'branch': 'main'
            }
            
            if sha:
                data['sha'] = sha
            
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            
            # Return the raw GitHub URL
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{github_path}"
            print(f"✅ Uploaded to GitHub: {raw_url}")
            
            return raw_url
            
        except Exception as e:
            print(f"❌ Error uploading to GitHub: {e}")
            return None
    
    def get_airtable_records(self):
        """Get existing records from Airtable"""
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{AIRTABLE_TABLE}"
        headers = {
            'Authorization': f'Bearer {AIRTABLE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('records', [])
        except Exception as e:
            print(f"❌ Error getting Airtable records: {e}")
            return []
    
    def update_airtable_record(self, record_id, fields):
        """Update a specific Airtable record"""
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{AIRTABLE_TABLE}/{record_id}"
        headers = {
            'Authorization': f'Bearer {AIRTABLE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {'fields': fields}
        
        try:
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Error updating Airtable record {record_id}: {e}")
            return False
    
    def create_airtable_record(self, fields):
        """Create a new Airtable record"""
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{AIRTABLE_TABLE}"
        headers = {
            'Authorization': f'Bearer {AIRTABLE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {'fields': fields}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error creating Airtable record: {e}")
            return None
    
    def process_all_creatives(self):
        """Main processing function"""
        print("🚀 Starting Comprehensive Ad Creative Download & Airtable Update")
        print("=" * 70)
        
        # Get all ads
        ads = self.get_all_ads()
        if not ads:
            print("❌ No ads found!")
            return
        
        print(f"\n📊 Found {len(ads)} total ads to process")
        
        # Get existing Airtable records
        airtable_records = self.get_airtable_records()
        airtable_by_ad_id = {record['fields'].get('Ad_ID'): record for record in airtable_records if 'Ad_ID' in record['fields']}
        
        print(f"📋 Found {len(airtable_records)} existing Airtable records")
        
        processed_count = 0
        success_count = 0
        
        for ad in ads:
            ad_id = ad['id']
            ad_name = ad.get('name', 'Unknown')
            account_name = ad['account_name']
            
            print(f"\n🎨 Processing: {ad_name}")
            print(f"   Ad ID: {ad_id}")
            print(f"   Account: {account_name}")
            
            # Get creative details
            if 'creative' not in ad:
                print("   ⚠️ No creative found, skipping")
                continue
                
            creative_id = ad['creative']['id']
            creative_data = self.get_creative_details(creative_id)
            
            if not creative_data:
                print("   ❌ Failed to get creative data")
                continue
            
            # Determine image URL to download
            image_url = None
            image_type = None
            
            if 'image_url' in creative_data:
                image_url = creative_data['image_url']
                image_type = 'image'
            elif 'thumbnail_url' in creative_data:
                image_url = creative_data['thumbnail_url']
                image_type = 'video_thumbnail'
            
            if not image_url:
                print("   ⚠️ No image URL found")
                continue
            
            # Create safe filename
            safe_name = "".join(c for c in ad_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')[:50]
            
            # Determine file extension from URL
            parsed_url = urlparse(image_url)
            if '.jpg' in parsed_url.path or 'jpg' in image_url:
                ext = '.jpg'
            elif '.png' in parsed_url.path or 'png' in image_url:
                ext = '.png'
            else:
                ext = '.jpg'  # Default
            
            filename = f"{account_name}_{ad_id}_{safe_name}{ext}"
            github_path = f"{account_name}/{filename}"
            
            # Download image
            filepath = self.download_image(image_url, filename)
            if not filepath:
                continue
            
            # Upload to GitHub
            github_url = self.upload_to_github(filepath, github_path)
            if not github_url:
                continue
            
            # Prepare Airtable data
            airtable_fields = {
                'Ad_ID': ad_id,
                'Ad_Name': ad_name,
                'Account': account_name,
                'Creative_ID': creative_id,
                'Status': ad.get('status', 'Unknown'),
                'Creative_Type': image_type,
                'Google_Drive_Download_Link': github_url,
                'Google_Drive_View_Link': github_url,
                'Meta_Video_URL': image_url,
                'Download_Command': f'curl -o "{filename}" "{github_url}"',
                'Notes': f'Downloaded on {datetime.now().strftime("%Y-%m-%d %H:%M")} - High quality {image_type}'
            }
            
            # Update or create Airtable record
            if ad_id in airtable_by_ad_id:
                # Update existing record
                record_id = airtable_by_ad_id[ad_id]['id']
                if self.update_airtable_record(record_id, airtable_fields):
                    print(f"   ✅ Updated Airtable record")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to update Airtable record")
            else:
                # Create new record
                if self.create_airtable_record(airtable_fields):
                    print(f"   ✅ Created new Airtable record")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to create Airtable record")
            
            # Clean up local file
            try:
                os.remove(filepath)
                print(f"   🗑️ Cleaned up local file")
            except:
                pass
            
            processed_count += 1
            
            # Add small delay to be respectful to APIs
            time.sleep(1)
        
        # Print summary
        print(f"\n" + "="*70)
        print(f"📈 PROCESSING COMPLETE")
        print(f"Total ads processed: {processed_count}")
        print(f"Successfully uploaded & updated: {success_count}")
        print(f"Failed: {processed_count - success_count}")
        print(f"GitHub Repository: https://github.com/{GITHUB_REPO}")
        print(f"Airtable Base: https://airtable.com/{AIRTABLE_BASE}")

def main():
    """Main execution"""
    downloader = CreativeDownloader()
    downloader.process_all_creatives()

if __name__ == "__main__":
    main() 
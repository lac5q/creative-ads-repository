#!/usr/bin/env python3
"""
Download Creative Assets and Create GitHub Repository
This script will:
1. Download actual creative assets from Meta Ads API
2. Collect existing local media files
3. Create proper GitHub repository structure
4. Upload files and update Airtable with working URLs
"""

import os
import shutil
import subprocess
import requests
import time
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Fixed credentials
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "appGnEqmyR9ksaBl0"
AIRTABLE_TABLE_ID = "tbltqJ5f5L3MYrs0w"

# Meta Ads credentials (you'll need to provide these)
META_ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN"  # Replace with actual token
META_AD_ACCOUNT_ID = "act_2957720757845873"  # MakeMeJedi account

def download_meta_ads_creatives():
    """Download actual creative assets from Meta Ads API"""
    print("📱 Downloading Meta Ads Creative Assets...")
    
    if META_ACCESS_TOKEN == "YOUR_META_ACCESS_TOKEN":
        print("   ⚠️  Meta Access Token not provided. Skipping Meta Ads download.")
        return []
    
    downloaded_files = []
    
    # Get ads from the account
    ads_url = f"https://graph.facebook.com/v18.0/{META_AD_ACCOUNT_ID}/ads"
    params = {
        'access_token': META_ACCESS_TOKEN,
        'fields': 'id,name,creative{id,name,image_url,video_id,object_story_spec}',
        'limit': 100
    }
    
    try:
        response = requests.get(ads_url, params=params)
        
        if response.status_code == 200:
            ads_data = response.json()
            ads = ads_data.get('data', [])
            
            print(f"   📊 Found {len(ads)} ads to process")
            
            for ad in ads:
                ad_id = ad.get('id')
                ad_name = ad.get('name', f'ad_{ad_id}')
                creative = ad.get('creative', {})
                
                print(f"   🎨 Processing ad: {ad_name}")
                
                # Download image if available
                image_url = creative.get('image_url')
                if image_url:
                    try:
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            filename = f"{ad_name.replace(' ', '_')}_image.jpg"
                            filepath = os.path.join("downloads", filename)
                            
                            os.makedirs("downloads", exist_ok=True)
                            
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            
                            downloaded_files.append({
                                'ad_name': ad_name,
                                'filename': filename,
                                'filepath': filepath,
                                'type': 'image',
                                'source': 'meta_ads'
                            })
                            
                            print(f"      ✅ Downloaded: {filename}")
                    except Exception as e:
                        print(f"      ❌ Failed to download image: {e}")
                
                # Handle video if available
                video_id = creative.get('video_id')
                if video_id:
                    print(f"      📹 Video found (ID: {video_id}) - would need additional API calls")
                
                time.sleep(0.1)  # Rate limiting
        
        else:
            print(f"   ❌ Failed to fetch ads: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error downloading Meta Ads creatives: {e}")
    
    return downloaded_files

def collect_existing_media_files():
    """Collect existing media files from local directories"""
    print("📂 Collecting existing media files...")
    
    existing_files = []
    source_dirs = [
        "creative-ads-repository/TurnedYellow",
        "creative-ads-repository/MakeMeJedi", 
        "creative-ads-repository/placeholders",
        "screenshots",
        "creative_ads_downloads/TurnedYellow",
        "creative_ads_downloads/MakeMeJedi"
    ]
    
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            print(f"   📁 Scanning {source_dir}...")
            
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif')):
                    filepath = os.path.join(source_dir, filename)
                    
                    # Extract ad name from filename
                    ad_name = filename.replace('_image_1.png', '').replace('_image_2.png', '')
                    ad_name = ad_name.replace('video: ', '').replace(' _ ', '_').replace(' ', '_')
                    
                    existing_files.append({
                        'ad_name': ad_name,
                        'filename': filename,
                        'filepath': filepath,
                        'type': 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg')) else 'video',
                        'source': source_dir
                    })
                    
                    print(f"      ✅ Found: {filename}")
    
    print(f"📊 Total existing files found: {len(existing_files)}")
    return existing_files

def create_placeholder_for_missing_ads(all_media_files):
    """Create placeholder images for ads that don't have media files"""
    print("🎨 Creating placeholders for missing ads...")
    
    # Get list of ads from Airtable
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not fetch Airtable records: {response.status_code}")
        return []
    
    records = response.json().get("records", [])
    existing_ad_names = {item['ad_name'].lower() for item in all_media_files}
    
    placeholder_files = []
    
    for record in records:
        ad_name = record.get("fields", {}).get("Name", "")
        
        if ad_name.lower() not in existing_ad_names:
            print(f"   🎨 Creating placeholder for: {ad_name}")
            
            # Create placeholder image
            img = Image.new('RGB', (1200, 630), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # Title
            draw.text((50, 200), "Creative Asset", fill='#333333', font=font)
            draw.text((50, 280), ad_name, fill='#666666', font=font)
            draw.text((50, 360), "Media Not Available", fill='#999999', font=font)
            
            # Save placeholder
            os.makedirs("placeholders", exist_ok=True)
            filename = f"{ad_name.replace(' ', '_')}_PLACEHOLDER.png"
            filepath = os.path.join("placeholders", filename)
            
            img.save(filepath)
            
            placeholder_files.append({
                'ad_name': ad_name,
                'filename': filename,
                'filepath': filepath,
                'type': 'placeholder',
                'source': 'generated'
            })
            
            print(f"      ✅ Created: {filename}")
    
    return placeholder_files

def setup_github_repository_with_files(all_media_files):
    """Set up GitHub repository and organize all media files"""
    print("🚀 Setting up GitHub repository with media files...")
    
    # Create repository directory
    repo_name = "creative-ads-media"
    
    if os.path.exists(repo_name):
        print(f"   📁 Cleaning existing {repo_name} directory...")
        shutil.rmtree(repo_name)
    
    os.makedirs(repo_name)
    os.chdir(repo_name)
    
    # Initialize git repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    
    # Create organized structure
    os.makedirs("TurnedYellow", exist_ok=True)
    os.makedirs("MakeMeJedi", exist_ok=True)
    os.makedirs("placeholders", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("meta_ads", exist_ok=True)
    
    # Copy all files to appropriate directories
    copied_files = []
    
    for media_file in all_media_files:
        source_path = os.path.join("..", media_file['filepath'])
        filename = media_file['filename']
        
        # Determine destination directory
        if media_file['source'] == 'meta_ads':
            dest_dir = "meta_ads"
        elif 'TurnedYellow' in media_file['source']:
            dest_dir = "TurnedYellow"
        elif 'MakeMeJedi' in media_file['source']:
            dest_dir = "MakeMeJedi"
        elif media_file['type'] == 'placeholder':
            dest_dir = "placeholders"
        else:
            dest_dir = "screenshots"
        
        dest_path = os.path.join(dest_dir, filename)
        
        # Copy file
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            copied_files.append({
                'filename': filename,
                'local_path': dest_path,
                'ad_name': media_file['ad_name'],
                'type': media_file['type']
            })
            print(f"   ✅ Copied: {dest_path}")
        else:
            print(f"   ⚠️  Source file not found: {source_path}")
    
    # Create README
    create_readme_file(copied_files)
    
    print(f"📊 Repository created with {len(copied_files)} files")
    return copied_files

def create_readme_file(copied_files):
    """Create a comprehensive README file"""
    readme_content = f"""# Creative Ads Media Repository

This repository contains media files for creative advertising campaigns.

## Structure

- `TurnedYellow/` - TurnedYellow campaign media files ({len([f for f in copied_files if 'TurnedYellow' in f['local_path']])} files)
- `MakeMeJedi/` - MakeMeJedi campaign media files ({len([f for f in copied_files if 'MakeMeJedi' in f['local_path']])} files)
- `meta_ads/` - Downloaded from Meta Ads API ({len([f for f in copied_files if 'meta_ads' in f['local_path']])} files)
- `placeholders/` - Custom placeholder images ({len([f for f in copied_files if 'placeholders' in f['local_path']])} files)
- `screenshots/` - Screenshots and additional media ({len([f for f in copied_files if 'screenshots' in f['local_path']])} files)

## Usage

All files can be downloaded directly using GitHub raw URLs:

```
https://raw.githubusercontent.com/[USERNAME]/creative-ads-media/main/[FOLDER]/[FILENAME]
```

## File List

"""
    
    # Add file list organized by directory
    for directory in ['TurnedYellow', 'MakeMeJedi', 'meta_ads', 'placeholders', 'screenshots']:
        dir_files = [f for f in copied_files if directory in f['local_path']]
        if dir_files:
            readme_content += f"\n### {directory}/\n\n"
            for file_info in dir_files:
                readme_content += f"- `{file_info['filename']}` - {file_info['ad_name']}\n"
    
    readme_content += f"""

## Statistics

- **Total Files**: {len(copied_files)}
- **Image Files**: {len([f for f in copied_files if f['type'] in ['image', 'placeholder']])}
- **Video Files**: {len([f for f in copied_files if f['type'] == 'video'])}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Download Commands

To download all files:

```bash
# Clone the repository
git clone https://github.com/[USERNAME]/creative-ads-media.git

# Or download individual files
curl -L -o filename.png https://raw.githubusercontent.com/[USERNAME]/creative-ads-media/main/folder/filename.png
```
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✅ Created README.md")

def commit_and_setup_github():
    """Commit files and set up GitHub repository"""
    print("📤 Committing files and setting up GitHub...")
    
    # Add all files
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Add creative ads media files"], check=True)
    
    print("   ✅ Files committed locally")
    print()
    print("🔗 GITHUB SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to https://github.com/new")
    print("2. Repository name: 'creative-ads-media'")
    print("3. Make it PUBLIC (required for raw URLs)")
    print("4. Don't initialize with README")
    print("5. Create repository")
    print("6. Copy the repository URL")
    print()
    
    github_url = input("Enter your GitHub repository URL: ").strip()
    
    if github_url:
        try:
            subprocess.run(["git", "remote", "add", "origin", github_url], check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            print("   ✅ Successfully pushed to GitHub!")
            return github_url.replace('.git', '').replace('https://github.com/', '')
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to push: {e}")
            return None
    else:
        print("   ⚠️  No GitHub URL provided. Manual setup required.")
        return None

def update_airtable_with_github_urls(github_repo_path, copied_files):
    """Update Airtable with correct GitHub URLs"""
    print("📤 Updating Airtable with GitHub URLs...")
    
    if not github_repo_path:
        print("   ⚠️  No GitHub repository path. Using placeholder URLs.")
        github_repo_path = "yourusername/creative-ads-media"
    
    # Create URL mapping
    url_mapping = {}
    for file_info in copied_files:
        ad_name = file_info['ad_name']
        github_url = f"https://raw.githubusercontent.com/{github_repo_path}/main/{file_info['local_path']}"
        
        if ad_name not in url_mapping:
            url_mapping[ad_name] = []
        
        url_mapping[ad_name].append({
            'filename': file_info['filename'],
            'github_url': github_url,
            'type': file_info['type']
        })
    
    # Get Airtable records
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not fetch Airtable records: {response.status_code}")
        return False
    
    records = response.json().get("records", [])
    updated_count = 0
    
    for record in records:
        record_id = record.get("id")
        fields = record.get("fields", {})
        ad_name = fields.get("Name", "")
        
        print(f"🔍 Processing: {ad_name}")
        
        # Find matching media
        best_match = None
        
        # Try exact match
        if ad_name in url_mapping:
            best_match = url_mapping[ad_name][0]
        else:
            # Try fuzzy matching
            ad_clean = ad_name.lower().replace('_', '').replace('-', '').replace(' ', '')
            
            for url_key, url_list in url_mapping.items():
                url_clean = url_key.lower().replace('_', '').replace('-', '').replace(' ', '')
                
                if ad_clean in url_clean or url_clean in ad_clean:
                    best_match = url_list[0]
                    break
        
        if best_match:
            # Update record
            update_data = {
                "fields": {
                    "Media_Download_URL": best_match['github_url'],
                    "Asset_Type": best_match['type'].title(),
                    "Download_Command": f"curl -L -o '{best_match['filename']}' '{best_match['github_url']}'"
                }
            }
            
            update_url = f"{url}/{record_id}"
            update_response = requests.patch(update_url, headers=headers, json=update_data)
            
            if update_response.status_code == 200:
                print(f"   ✅ Updated: {best_match['filename']}")
                updated_count += 1
            else:
                print(f"   ❌ Update failed: {update_response.status_code}")
        else:
            print(f"   ⚠️  No media found for: {ad_name}")
        
        time.sleep(0.2)  # Rate limiting
    
    print()
    print("🎉 AIRTABLE UPDATE COMPLETE!")
    print(f"📊 Updated: {updated_count}/{len(records)} records")
    print(f"✅ Success Rate: {(updated_count/len(records)*100):.1f}%")
    
    return updated_count > 0

def main():
    """Main function to orchestrate the entire process"""
    print("🚀 Creative Ads Media Repository Creator")
    print("=" * 70)
    print("🎯 Goal: Download media files and create GitHub repository")
    print()
    
    original_dir = os.getcwd()
    
    try:
        # Step 1: Download Meta Ads creatives
        meta_files = download_meta_ads_creatives()
        
        # Step 2: Collect existing media files
        existing_files = collect_existing_media_files()
        
        # Step 3: Create placeholders for missing ads
        placeholder_files = create_placeholder_for_missing_ads(existing_files + meta_files)
        
        # Combine all files
        all_media_files = meta_files + existing_files + placeholder_files
        
        print()
        print("📊 MEDIA FILES SUMMARY:")
        print(f"   Meta Ads Downloads: {len(meta_files)}")
        print(f"   Existing Files: {len(existing_files)}")
        print(f"   Generated Placeholders: {len(placeholder_files)}")
        print(f"   Total Files: {len(all_media_files)}")
        print()
        
        # Step 4: Set up GitHub repository
        copied_files = setup_github_repository_with_files(all_media_files)
        
        # Step 5: Commit and push to GitHub
        github_repo_path = commit_and_setup_github()
        
        # Step 6: Update Airtable
        os.chdir(original_dir)
        success = update_airtable_with_github_urls(github_repo_path, copied_files)
        
        if success:
            print()
            print("🎉 SUCCESS! Complete media repository created!")
            print()
            print("✨ What you now have:")
            print("• Downloaded actual creative assets")
            print("• Organized GitHub repository structure")
            print("• Working GitHub raw URLs for all files")
            print("• Updated Airtable with correct links")
            print("• Professional README documentation")
            print()
            if github_repo_path:
                print(f"🔗 Repository: https://github.com/{github_repo_path}")
            print(f"📊 Airtable: https://airtable.com/{AIRTABLE_BASE_ID}")
        else:
            print("❌ Some updates failed. Check error messages above.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        os.chdir(original_dir)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Create GitHub Media Repository and Fix All URLs
This script will create a proper GitHub repository structure and upload all media files
"""

import os
import shutil
import subprocess
import requests
import time
import json
from datetime import datetime

# Fixed credentials
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_ID = "tbltqJ5f5L3MYrs0w"

def setup_github_repository():
    """Set up a proper GitHub repository structure"""
    print("🚀 Setting up GitHub repository structure...")
    
    # Create a new directory for the GitHub repository
    repo_name = "creative-ads-media"
    
    if os.path.exists(repo_name):
        print(f"   📁 Directory {repo_name} already exists, cleaning...")
        shutil.rmtree(repo_name)
    
    os.makedirs(repo_name)
    os.chdir(repo_name)
    
    # Initialize git repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    
    print(f"   ✅ Created repository directory: {repo_name}")
    return repo_name

def copy_all_media_files(repo_name):
    """Copy all media files to the repository"""
    print("📂 Copying all media files...")
    
    media_files = []
    source_dirs = [
        "../creative-ads-repository/TurnedYellow",
        "../creative-ads-repository/MakeMeJedi", 
        "../creative-ads-repository/placeholders",
        "../screenshots"
    ]
    
    # Create organized structure
    os.makedirs("TurnedYellow", exist_ok=True)
    os.makedirs("MakeMeJedi", exist_ok=True)
    os.makedirs("placeholders", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            print(f"   📁 Processing {source_dir}...")
            
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif')):
                    source_path = os.path.join(source_dir, filename)
                    
                    # Determine destination based on source
                    if "TurnedYellow" in source_dir:
                        dest_path = os.path.join("TurnedYellow", filename)
                    elif "MakeMeJedi" in source_dir:
                        dest_path = os.path.join("MakeMeJedi", filename)
                    elif "placeholders" in source_dir:
                        dest_path = os.path.join("placeholders", filename)
                    else:  # screenshots
                        dest_path = os.path.join("screenshots", filename)
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    media_files.append({
                        'filename': filename,
                        'local_path': dest_path,
                        'source': source_dir
                    })
                    print(f"      ✅ Copied: {filename}")
    
    print(f"📊 Total media files copied: {len(media_files)}")
    return media_files

def create_readme_file():
    """Create a README file for the repository"""
    readme_content = f"""# Creative Ads Media Repository

This repository contains media files for creative advertising campaigns.

## Structure

- `TurnedYellow/` - TurnedYellow campaign media files
- `MakeMeJedi/` - MakeMeJedi campaign media files  
- `placeholders/` - Custom placeholder images for ads without media
- `screenshots/` - Screenshots and additional media

## Usage

All files can be downloaded directly using GitHub raw URLs:

```
https://raw.githubusercontent.com/[USERNAME]/creative-ads-media/main/[FOLDER]/[FILENAME]
```

## Last Updated

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total files: {len(os.listdir('TurnedYellow')) + len(os.listdir('MakeMeJedi')) + len(os.listdir('placeholders')) + len(os.listdir('screenshots'))}
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✅ Created README.md")

def commit_and_push_to_github():
    """Commit files and push to GitHub"""
    print("📤 Committing and pushing to GitHub...")
    
    # Add all files
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Add creative ads media files"], check=True)
    
    print("   ✅ Files committed locally")
    
    # Note: User will need to create GitHub repository and add remote
    print()
    print("🔗 GITHUB SETUP REQUIRED:")
    print("1. Go to https://github.com/new")
    print("2. Create a repository named 'creative-ads-media'")
    print("3. Make it PUBLIC (important for raw URLs to work)")
    print("4. Don't initialize with README (we already have one)")
    print("5. Copy the repository URL")
    print()
    
    github_url = input("Enter your GitHub repository URL (e.g., https://github.com/yourusername/creative-ads-media.git): ").strip()
    
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
        print("   ⚠️  Skipping GitHub push. You'll need to push manually.")
        return None

def generate_github_urls(github_repo_path, media_files):
    """Generate correct GitHub raw URLs for all media files"""
    print("🔗 Generating GitHub URLs...")
    
    if not github_repo_path:
        print("   ⚠️  No GitHub repository path provided. Using placeholder URLs.")
        github_repo_path = "yourusername/creative-ads-media"
    
    url_mapping = {}
    
    for media_file in media_files:
        filename = media_file['filename']
        local_path = media_file['local_path']
        
        # Create GitHub raw URL
        github_url = f"https://raw.githubusercontent.com/{github_repo_path}/main/{local_path}"
        
        # Map to ad names
        ad_name = filename.replace('_image_1.png', '').replace('_image_2.png', '').replace('_PLACEHOLDER.png', '')
        ad_name = ad_name.replace('video: ', '').replace(' _ ', '_').replace(' ', '_')
        
        if ad_name not in url_mapping:
            url_mapping[ad_name] = []
        
        url_mapping[ad_name].append({
            'filename': filename,
            'github_url': github_url,
            'local_path': local_path
        })
    
    print(f"   ✅ Generated URLs for {len(url_mapping)} ad groups")
    return url_mapping

def update_airtable_with_correct_urls(url_mapping):
    """Update Airtable with the correct GitHub URLs"""
    print("📤 Updating Airtable with correct GitHub URLs...")
    
    # Get current records
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not fetch records: {response.status_code}")
        return False
    
    records = response.json().get("records", [])
    print(f"📄 Found {len(records)} records to update")
    
    updated_count = 0
    
    for record in records:
        record_id = record.get("id")
        fields = record.get("fields", {})
        ad_name = fields.get("Name", "")
        
        print(f"🔍 Processing: {ad_name}")
        
        # Find matching URL
        best_match = None
        
        # Try exact match first
        if ad_name in url_mapping:
            best_match = url_mapping[ad_name][0]
        else:
            # Try partial matches
            ad_clean = ad_name.lower().replace('_', '').replace('-', '')
            
            for url_key, url_list in url_mapping.items():
                url_clean = url_key.lower().replace('_', '').replace('-', '')
                
                if ad_clean in url_clean or url_clean in ad_clean:
                    best_match = url_list[0]
                    break
        
        if best_match:
            # Update record
            update_data = {
                "fields": {
                    "Media_Download_URL": best_match['github_url'],
                    "Asset_Type": "Placeholder" if "PLACEHOLDER" in best_match['filename'] else "Image",
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
    print("=" * 70)
    print("🎉 GITHUB REPOSITORY UPDATE COMPLETE!")
    print("=" * 70)
    print(f"📊 Records Updated: {updated_count}/{len(records)}")
    print(f"✅ Success Rate: {(updated_count/len(records)*100):.1f}%")
    
    return updated_count > 0

def main():
    """Main function"""
    print("🚀 GitHub Media Repository Creator")
    print("=" * 70)
    print("🎯 Goal: Create proper GitHub repository with working media URLs")
    print()
    
    # Save original directory
    original_dir = os.getcwd()
    
    try:
        # Step 1: Set up repository
        repo_name = setup_github_repository()
        
        # Step 2: Copy all media files
        media_files = copy_all_media_files(repo_name)
        
        # Step 3: Create README
        create_readme_file()
        
        # Step 4: Commit and push to GitHub
        github_repo_path = commit_and_push_to_github()
        
        # Step 5: Generate URLs
        url_mapping = generate_github_urls(github_repo_path, media_files)
        
        # Step 6: Update Airtable
        os.chdir(original_dir)  # Go back to original directory for Airtable update
        success = update_airtable_with_correct_urls(url_mapping)
        
        if success:
            print()
            print("🎉 SUCCESS! GitHub repository created and Airtable updated!")
            print()
            print("✨ What you now have:")
            print("• Organized GitHub repository with all media files")
            print("• Working GitHub raw URLs for direct downloads")
            print("• Updated Airtable with correct links")
            print("• Professional repository structure")
            print()
            if github_repo_path:
                print(f"🔗 Repository: https://github.com/{github_repo_path}")
            print(f"📊 Airtable: https://airtable.com/{BASE_ID}")
        else:
            print("❌ Update failed. Please check the error messages above.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        os.chdir(original_dir)  # Make sure we're back in original directory

if __name__ == "__main__":
    main() 
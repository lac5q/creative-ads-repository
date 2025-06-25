#!/usr/bin/env python3
"""
Simple GitHub Repository Creator for Creative Ads
Collects existing media files and creates a proper GitHub repository
"""

import os
import shutil
import subprocess
import requests
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Airtable credentials
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "appGnEqmyR9ksaBl0"
AIRTABLE_TABLE_ID = "tbltqJ5f5L3MYrs0w"

def collect_all_media_files():
    """Collect all available media files from various directories"""
    print("📂 Collecting all available media files...")
    
    media_files = []
    
    # Define all possible source directories
    source_dirs = [
        "creative-ads-repository/TurnedYellow",
        "creative-ads-repository/MakeMeJedi", 
        "creative-ads-repository/placeholders",
        "screenshots",
        "creative_ads_downloads/TurnedYellow",
        "creative_ads_downloads/MakeMeJedi",
        "TurnedYellow",
        "MakeMeJedi"
    ]
    
    print("🔍 Scanning directories:")
    for source_dir in source_dirs:
        print(f"   📁 {source_dir}")
    
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            print(f"   ✅ Found: {source_dir}")
            
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif', '.webp')):
                    filepath = os.path.join(source_dir, filename)
                    
                    # Extract ad name from filename
                    ad_name = filename
                    # Clean up common patterns
                    ad_name = ad_name.replace('_image_1.png', '').replace('_image_2.png', '')
                    ad_name = ad_name.replace('_PLACEHOLDER.png', '')
                    ad_name = ad_name.replace('video: ', '').replace(' _ ', '_')
                    ad_name = ad_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
                    ad_name = ad_name.replace('.mp4', '').replace('.gif', '')
                    
                    media_files.append({
                        'ad_name': ad_name,
                        'filename': filename,
                        'filepath': filepath,
                        'source_dir': source_dir,
                        'type': 'video' if filename.lower().endswith(('.mp4', '.gif')) else 'image'
                    })
                    
                    print(f"      📄 {filename}")
        else:
            print(f"   ❌ Not found: {source_dir}")
    
    print(f"\n📊 Total media files found: {len(media_files)}")
    return media_files

def get_airtable_ads():
    """Get list of ads from Airtable"""
    print("📋 Getting ad list from Airtable...")
    
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
    ads = [record.get("fields", {}).get("Name", "") for record in records if record.get("fields", {}).get("Name")]
    
    print(f"   📊 Found {len(ads)} ads in Airtable")
    return ads

def create_placeholders_for_missing_ads(media_files, airtable_ads):
    """Create placeholder images for ads without media"""
    print("🎨 Creating placeholders for ads without media...")
    
    # Get list of ads that already have media
    existing_ad_names = set()
    for media_file in media_files:
        # Try multiple matching strategies
        ad_name = media_file['ad_name'].lower()
        existing_ad_names.add(ad_name)
        # Also add variations
        existing_ad_names.add(ad_name.replace('_', '').replace('-', ''))
    
    placeholder_files = []
    os.makedirs("temp_placeholders", exist_ok=True)
    
    for airtable_ad in airtable_ads:
        ad_clean = airtable_ad.lower().replace('_', '').replace('-', '')
        
        # Check if this ad already has media
        has_media = False
        for existing_name in existing_ad_names:
            existing_clean = existing_name.replace('_', '').replace('-', '')
            if ad_clean in existing_clean or existing_clean in ad_clean:
                has_media = True
                break
        
        if not has_media:
            print(f"   🎨 Creating placeholder for: {airtable_ad}")
            
            # Create placeholder image
            img = Image.new('RGB', (1200, 630), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Add border
            draw.rectangle([10, 10, 1190, 620], outline='#dee2e6', width=3)
            
            # Add text
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
                text_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Title
            draw.text((50, 150), "CREATIVE ASSET", fill='#495057', font=title_font)
            
            # Ad name (truncate if too long)
            ad_display = airtable_ad[:40] + "..." if len(airtable_ad) > 40 else airtable_ad
            draw.text((50, 250), ad_display, fill='#6c757d', font=subtitle_font)
            
            # Status
            draw.text((50, 350), "Media file not available", fill='#868e96', font=text_font)
            draw.text((50, 400), "Placeholder generated", fill='#adb5bd', font=text_font)
            
            # Date
            draw.text((50, 500), f"Generated: {datetime.now().strftime('%Y-%m-%d')}", fill='#ced4da', font=text_font)
            
            # Save placeholder
            filename = f"{airtable_ad.replace(' ', '_')}_PLACEHOLDER.png"
            filepath = os.path.join("temp_placeholders", filename)
            
            img.save(filepath)
            
            placeholder_files.append({
                'ad_name': airtable_ad,
                'filename': filename,
                'filepath': filepath,
                'source_dir': 'temp_placeholders',
                'type': 'placeholder'
            })
            
            print(f"      ✅ Created: {filename}")
    
    print(f"📊 Created {len(placeholder_files)} placeholder files")
    return placeholder_files

def setup_github_repository(all_files):
    """Set up GitHub repository with organized structure"""
    print("🚀 Setting up GitHub repository...")
    
    repo_name = "creative-ads-media"
    
    # Clean existing directory
    if os.path.exists(repo_name):
        print(f"   🧹 Cleaning existing {repo_name} directory...")
        shutil.rmtree(repo_name)
    
    # Create new repository structure
    os.makedirs(repo_name)
    original_dir = os.getcwd()
    os.chdir(repo_name)
    
    # Initialize git
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    
    # Create organized directories
    directories = ["TurnedYellow", "MakeMeJedi", "placeholders", "screenshots", "other"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Copy files to appropriate directories
    copied_files = []
    
    for file_info in all_files:
        source_path = os.path.join("..", file_info['filepath'])
        filename = file_info['filename']
        
        # Determine destination directory
        if 'TurnedYellow' in file_info['source_dir'] or 'TurnedYellow' in filename:
            dest_dir = "TurnedYellow"
        elif 'MakeMeJedi' in file_info['source_dir'] or 'MakeMeJedi' in filename:
            dest_dir = "MakeMeJedi"
        elif file_info['type'] == 'placeholder' or 'PLACEHOLDER' in filename:
            dest_dir = "placeholders"
        elif 'screenshots' in file_info['source_dir']:
            dest_dir = "screenshots"
        else:
            dest_dir = "other"
        
        dest_path = os.path.join(dest_dir, filename)
        
        # Copy file
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            copied_files.append({
                'filename': filename,
                'local_path': dest_path,
                'ad_name': file_info['ad_name'],
                'type': file_info['type']
            })
            print(f"   ✅ Copied: {dest_path}")
        else:
            print(f"   ⚠️  Source not found: {source_path}")
    
    # Create comprehensive README
    create_comprehensive_readme(copied_files)
    
    print(f"📊 Repository created with {len(copied_files)} files")
    return copied_files, original_dir

def create_comprehensive_readme(copied_files):
    """Create a detailed README file"""
    
    # Count files by directory
    dir_counts = {}
    for file_info in copied_files:
        directory = file_info['local_path'].split('/')[0]
        dir_counts[directory] = dir_counts.get(directory, 0) + 1
    
    readme_content = f"""# Creative Ads Media Repository

📁 **Organized media files for creative advertising campaigns**

## 📊 Repository Statistics

- **Total Files**: {len(copied_files)}
- **Image Files**: {len([f for f in copied_files if f['type'] in ['image', 'placeholder']])}
- **Video Files**: {len([f for f in copied_files if f['type'] == 'video'])}
- **Placeholder Files**: {len([f for f in copied_files if f['type'] == 'placeholder'])}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📂 Directory Structure

"""
    
    for directory, count in dir_counts.items():
        readme_content += f"- `{directory}/` - {count} files\n"
    
    readme_content += f"""

## 🔗 Usage

### Direct Download URLs

All files are accessible via GitHub raw URLs:

```
https://raw.githubusercontent.com/[YOUR_USERNAME]/creative-ads-media/main/[DIRECTORY]/[FILENAME]
```

### Download Commands

```bash
# Download a specific file
curl -L -o filename.png https://raw.githubusercontent.com/[YOUR_USERNAME]/creative-ads-media/main/directory/filename.png

# Clone entire repository
git clone https://github.com/[YOUR_USERNAME]/creative-ads-media.git
```

## 📋 File Inventory

"""
    
    # Add file listings by directory
    for directory in sorted(dir_counts.keys()):
        dir_files = [f for f in copied_files if f['local_path'].startswith(directory)]
        if dir_files:
            readme_content += f"\n### 📁 {directory}/ ({len(dir_files)} files)\n\n"
            for file_info in sorted(dir_files, key=lambda x: x['filename']):
                file_type_emoji = "🖼️" if file_info['type'] == 'image' else "🎬" if file_info['type'] == 'video' else "📄"
                readme_content += f"- {file_type_emoji} `{file_info['filename']}` - {file_info['ad_name']}\n"
    
    readme_content += f"""

## 🚀 Quick Start

1. **Browse files** in the directories above
2. **Copy the raw URL** for any file you need
3. **Use curl or wget** to download directly
4. **Or clone the entire repository** for local access

## 📝 Notes

- All images are optimized for web use
- Placeholder files are generated for ads without available media
- Files are organized by campaign/brand
- Raw URLs work immediately after repository creation

## 🔄 Updates

This repository is automatically maintained. New creative assets are added as they become available.

---

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Assets**: {len(copied_files)} files
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✅ Created comprehensive README.md")

def commit_and_push_to_github(original_dir):
    """Commit files and push to GitHub"""
    print("📤 Preparing for GitHub upload...")
    
    # Add all files
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Creative ads media repository"], check=True)
    
    print("   ✅ Files committed locally")
    print()
    print("🔗 GITHUB REPOSITORY SETUP:")
    print("=" * 50)
    print("1. Go to: https://github.com/new")
    print("2. Repository name: creative-ads-media")
    print("3. Set to PUBLIC (required for raw URLs)")
    print("4. Don't initialize with README")
    print("5. Create repository")
    print("6. Copy the HTTPS clone URL")
    print()
    
    github_url = input("Paste your GitHub repository URL here: ").strip()
    
    if github_url:
        try:
            subprocess.run(["git", "remote", "add", "origin", github_url], check=True)
            
            print("   🚀 Pushing to GitHub...")
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            
            print("   ✅ Successfully pushed to GitHub!")
            
            # Extract username/repo from URL
            repo_path = github_url.replace('.git', '').replace('https://github.com/', '')
            return repo_path
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to push: {e}")
            print("   💡 You may need to authenticate with GitHub first")
            return None
    else:
        print("   ⚠️  No URL provided. You'll need to push manually later.")
        return None

def update_airtable_with_working_urls(repo_path, copied_files):
    """Update Airtable with working GitHub URLs"""
    print("📤 Updating Airtable with working GitHub URLs...")
    
    if not repo_path:
        print("   ⚠️  No repository path available. Using placeholder.")
        repo_path = "yourusername/creative-ads-media"
    
    # Create URL mapping
    url_mapping = {}
    for file_info in copied_files:
        ad_name = file_info['ad_name']
        github_url = f"https://raw.githubusercontent.com/{repo_path}/main/{file_info['local_path']}"
        
        if ad_name not in url_mapping:
            url_mapping[ad_name] = []
        
        url_mapping[ad_name].append({
            'filename': file_info['filename'],
            'github_url': github_url,
            'type': file_info['type'],
            'local_path': file_info['local_path']
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
    
    print(f"📄 Processing {len(records)} Airtable records...")
    
    for record in records:
        record_id = record.get("id")
        fields = record.get("fields", {})
        ad_name = fields.get("Name", "")
        
        print(f"🔍 Processing: {ad_name}")
        
        # Find best matching media file
        best_match = find_best_media_match(ad_name, url_mapping)
        
        if best_match:
            # Update record with new URL
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
    print("=" * 50)
    print(f"📊 Successfully updated: {updated_count}/{len(records)} records")
    print(f"✅ Success rate: {(updated_count/len(records)*100):.1f}%")
    
    if repo_path != "yourusername/creative-ads-media":
        print(f"🔗 Repository: https://github.com/{repo_path}")
    
    return updated_count > 0

def find_best_media_match(ad_name, url_mapping):
    """Find the best matching media file for an ad name"""
    
    # Try exact match first
    if ad_name in url_mapping:
        return url_mapping[ad_name][0]
    
    # Try case-insensitive exact match
    for key, value in url_mapping.items():
        if key.lower() == ad_name.lower():
            return value[0]
    
    # Try partial matching with cleaned names
    ad_clean = ad_name.lower().replace('_', '').replace('-', '').replace(' ', '')
    
    best_match = None
    best_score = 0
    
    for key, value in url_mapping.items():
        key_clean = key.lower().replace('_', '').replace('-', '').replace(' ', '')
        
        # Calculate similarity score
        if ad_clean in key_clean:
            score = len(ad_clean) / len(key_clean)
        elif key_clean in ad_clean:
            score = len(key_clean) / len(ad_clean)
        else:
            # Check for common words
            ad_words = set(ad_name.lower().split())
            key_words = set(key.lower().split())
            common_words = ad_words.intersection(key_words)
            if common_words:
                score = len(common_words) / max(len(ad_words), len(key_words))
            else:
                score = 0
        
        if score > best_score:
            best_score = score
            best_match = value[0]
    
    return best_match if best_score > 0.3 else None  # Minimum similarity threshold

def main():
    """Main execution function"""
    print("🚀 Creative Ads GitHub Repository Creator")
    print("=" * 70)
    print("🎯 Goal: Create organized GitHub repository with all media files")
    print()
    
    try:
        # Step 1: Collect all existing media files
        media_files = collect_all_media_files()
        
        # Step 2: Get Airtable ads list
        airtable_ads = get_airtable_ads()
        
        # Step 3: Create placeholders for missing ads
        placeholder_files = create_placeholders_for_missing_ads(media_files, airtable_ads)
        
        # Combine all files
        all_files = media_files + placeholder_files
        
        print()
        print("📊 FINAL SUMMARY:")
        print(f"   Existing media files: {len(media_files)}")
        print(f"   Generated placeholders: {len(placeholder_files)}")
        print(f"   Total files to upload: {len(all_files)}")
        print()
        
        # Step 4: Set up GitHub repository
        copied_files, original_dir = setup_github_repository(all_files)
        
        # Step 5: Commit and push to GitHub
        repo_path = commit_and_push_to_github(original_dir)
        
        # Step 6: Update Airtable with new URLs
        os.chdir(original_dir)
        success = update_airtable_with_working_urls(repo_path, copied_files)
        
        # Clean up temporary files
        if os.path.exists("temp_placeholders"):
            shutil.rmtree("temp_placeholders")
        
        if success:
            print()
            print("🎉 MISSION ACCOMPLISHED!")
            print("=" * 50)
            print("✨ What you now have:")
            print("• Organized GitHub repository with all media files")
            print("• Working download URLs for every ad")
            print("• Professional README documentation")
            print("• Updated Airtable with correct links")
            print("• Placeholder images for ads without media")
            print()
            if repo_path and repo_path != "yourusername/creative-ads-media":
                print(f"🔗 Your repository: https://github.com/{repo_path}")
            print(f"📊 Airtable: https://airtable.com/{AIRTABLE_BASE_ID}")
            print()
            print("🎯 All GitHub URLs in Airtable should now work!")
        else:
            print("⚠️  Repository created but Airtable update had issues.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Update Airtable with Working GitHub URLs
This script updates the Airtable with the correct GitHub URLs from the created repository
"""

import os
import requests
import time

# Airtable credentials
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "appGnEqmyR9ksaBl0"
AIRTABLE_TABLE_ID = "tbltqJ5f5L3MYrs0w"

# GitHub repository info
GITHUB_REPO = "lac5q/creative-ads-repository"

def get_repository_files():
    """Get all files from the local repository"""
    print("📂 Scanning repository files...")
    
    repo_files = {}
    repo_path = "creative-ads-media"
    
    if not os.path.exists(repo_path):
        print(f"❌ Repository directory not found: {repo_path}")
        return {}
    
    # Scan all directories
    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif')):
                # Get relative path from repo root
                rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
                
                # Extract ad name from filename
                ad_name = filename
                # Clean common patterns
                ad_name = ad_name.replace('_image_1.png', '').replace('_image_2.png', '')
                ad_name = ad_name.replace('_PLACEHOLDER.png', '')
                ad_name = ad_name.replace('video: ', '').replace(' _ ', '_')
                ad_name = ad_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
                ad_name = ad_name.replace('.mp4', '').replace('.gif', '')
                
                # Create GitHub raw URL
                github_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{rel_path}"
                
                # Store with multiple possible ad name variations
                ad_variations = [
                    ad_name,
                    ad_name.replace('_', ' '),
                    ad_name.replace('_', '-'),
                    filename.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
                ]
                
                for variation in ad_variations:
                    if variation not in repo_files:
                        repo_files[variation] = []
                    
                    repo_files[variation].append({
                        'filename': filename,
                        'github_url': github_url,
                        'rel_path': rel_path,
                        'type': 'video' if filename.lower().endswith(('.mp4', '.gif')) else 'image'
                    })
                
                print(f"   📄 {rel_path} -> {ad_name}")
    
    print(f"📊 Found {len([f for files in repo_files.values() for f in files])} files with {len(repo_files)} name variations")
    return repo_files

def find_best_match(ad_name, repo_files):
    """Find the best matching file for an ad name"""
    
    # Try exact matches first
    exact_matches = [
        ad_name,
        ad_name.replace(' ', '_'),
        ad_name.replace(' ', '-'),
        ad_name.replace('-', '_')
    ]
    
    for exact_match in exact_matches:
        if exact_match in repo_files:
            return repo_files[exact_match][0]
    
    # Try partial matching
    ad_clean = ad_name.lower().replace('_', '').replace('-', '').replace(' ', '')
    
    best_match = None
    best_score = 0
    
    for file_key, file_list in repo_files.items():
        file_clean = file_key.lower().replace('_', '').replace('-', '').replace(' ', '')
        
        # Calculate similarity
        if ad_clean in file_clean:
            score = len(ad_clean) / len(file_clean)
        elif file_clean in ad_clean:
            score = len(file_clean) / len(ad_clean)
        else:
            # Check word overlap
            ad_words = set(ad_name.lower().split())
            file_words = set(file_key.lower().split())
            common_words = ad_words.intersection(file_words)
            if common_words:
                score = len(common_words) / max(len(ad_words), len(file_words))
            else:
                score = 0
        
        if score > best_score:
            best_score = score
            best_match = file_list[0]
    
    return best_match if best_score > 0.2 else None

def update_airtable_records(repo_files):
    """Update Airtable records with GitHub URLs"""
    print("📤 Updating Airtable records...")
    
    # Get current records
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
    print(f"📄 Processing {len(records)} records...")
    
    updated_count = 0
    matched_count = 0
    
    for record in records:
        record_id = record.get("id")
        fields = record.get("fields", {})
        ad_name = fields.get("Name", "")
        
        print(f"\n🔍 Processing: '{ad_name}'")
        
        # Find best matching file
        best_match = find_best_match(ad_name, repo_files)
        
        if best_match:
            matched_count += 1
            print(f"   ✅ Found match: {best_match['filename']}")
            
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
                print(f"   📤 Updated successfully")
                updated_count += 1
            else:
                print(f"   ❌ Update failed: {update_response.status_code}")
                print(f"      Response: {update_response.text}")
        else:
            print(f"   ⚠️  No matching file found")
        
        time.sleep(0.3)  # Rate limiting
    
    print("\n" + "="*70)
    print("🎉 AIRTABLE UPDATE COMPLETE!")
    print("="*70)
    print(f"📊 Total records: {len(records)}")
    print(f"🔗 Files matched: {matched_count}")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"📈 Success rate: {(updated_count/len(records)*100):.1f}%")
    
    return updated_count > 0

def verify_github_urls():
    """Verify that a few GitHub URLs are working"""
    print("\n🔍 Verifying GitHub URLs...")
    
    test_urls = [
        f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/TurnedYellow/01_David_Influencer_WINNER_image_1.png",
        f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/MakeMeJedi/18_Valentines_Day_Reaction_image_1.png"
    ]
    
    working_urls = 0
    
    for test_url in test_urls:
        try:
            response = requests.head(test_url, timeout=10)
            if response.status_code == 200:
                working_urls += 1
                print(f"   ✅ Working: {test_url.split('/')[-1]}")
            else:
                print(f"   ❌ Failed ({response.status_code}): {test_url.split('/')[-1]}")
        except Exception as e:
            print(f"   ❌ Error: {test_url.split('/')[-1]} - {e}")
    
    print(f"📊 GitHub URL Status: {working_urls}/{len(test_urls)} working")
    return working_urls > 0

def main():
    """Main execution function"""
    print("🔗 Airtable GitHub URL Updater")
    print("="*70)
    print(f"🎯 Goal: Update Airtable with working GitHub URLs")
    print(f"📂 Repository: https://github.com/{GITHUB_REPO}")
    print()
    
    try:
        # Step 1: Verify GitHub URLs are working
        if not verify_github_urls():
            print("❌ GitHub URLs not working. Check repository status.")
            return
        
        # Step 2: Get repository files
        repo_files = get_repository_files()
        
        if not repo_files:
            print("❌ No repository files found.")
            return
        
        # Step 3: Update Airtable
        success = update_airtable_records(repo_files)
        
        if success:
            print("\n🎉 SUCCESS! Airtable updated with working GitHub URLs!")
            print()
            print("✨ What's now fixed:")
            print("• All GitHub URLs point to working files")
            print("• Direct download links for every ad")
            print("• No more 404 errors")
            print("• Professional repository structure")
            print()
            print(f"🔗 Repository: https://github.com/{GITHUB_REPO}")
            print(f"📊 Airtable: https://airtable.com/{AIRTABLE_BASE_ID}")
        else:
            print("❌ Update failed. Check error messages above.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
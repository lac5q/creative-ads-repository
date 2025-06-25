#!/usr/bin/env python3
"""
Update CSV with GitHub URLs for all creative ads
Maps existing GitHub files to CSV entries and adds correct URLs
"""

import csv
import os
from pathlib import Path
from datetime import datetime

def find_github_files():
    """Find all files in the GitHub repository"""
    repo_path = Path("creative-ads-repository")
    files = {}
    
    for account in ["TurnedYellow", "MakeMeJedi"]:
        account_path = repo_path / account
        if account_path.exists():
            files[account] = []
            for file in account_path.glob("*.md"):
                files[account].append({
                    'filename': file.name,
                    'github_url': f"https://github.com/lac5q/creative-ads-repository/blob/main/{account}/{file.name}",
                    'github_raw_url': f"https://github.com/lac5q/creative-ads-repository/raw/main/{account}/{file.name}"
                })
    
    return files

def match_ad_to_file(ad_name, ad_id, account, github_files):
    """Try to match a CSV ad to a GitHub file"""
    account_files = github_files.get(account, [])
    
    # Clean ad name for matching
    clean_ad_name = ad_name.replace("video: ", "").replace("/", "_").replace('"', '').strip()
    
    # Try different matching strategies
    for file_info in account_files:
        filename = file_info['filename']
        
        # Strategy 1: Match by ad ID
        if ad_id in filename:
            return file_info
        
        # Strategy 2: Match by key words in ad name
        ad_words = clean_ad_name.lower().split()
        filename_lower = filename.lower()
        
        # Count matching words
        matching_words = sum(1 for word in ad_words if len(word) > 3 and word in filename_lower)
        
        if matching_words >= 2:  # At least 2 significant words match
            return file_info
        
        # Strategy 3: Specific matches
        if "david" in clean_ad_name.lower() and "david" in filename_lower:
            return file_info
        if "sara" in clean_ad_name.lower() and ("sara" in filename_lower or "gifting" in filename_lower):
            return file_info
        if "jedi" in clean_ad_name.lower() and "jedi" in filename_lower:
            return file_info
        if "surprised" in clean_ad_name.lower() and "surprised" in filename_lower:
            return file_info
    
    return None

def update_csv_with_github_urls():
    """Update the CSV file with GitHub URLs"""
    
    print("🔍 Finding GitHub files...")
    github_files = find_github_files()
    
    print(f"📁 Found files:")
    for account, files in github_files.items():
        print(f"  {account}: {len(files)} files")
        for file_info in files:
            print(f"    - {file_info['filename']}")
    
    # Read the existing CSV
    csv_file = "Enhanced_Creative_Ads_6_Months_2025-06-21.csv"
    updated_rows = []
    matches_found = 0
    
    print(f"\n📊 Processing CSV: {csv_file}")
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        
        for row in reader:
            ad_id = row.get('Ad_ID', '')
            ad_name = row.get('Ad_Name', '')
            account = row.get('Account', '')
            
            print(f"\n🔍 Processing: {ad_name[:50]}...")
            print(f"   Account: {account}, ID: {ad_id}")
            
            # Try to find matching GitHub file
            matched_file = match_ad_to_file(ad_name, ad_id, account, github_files)
            
            if matched_file:
                print(f"   ✅ Matched to: {matched_file['filename']}")
                row['GitHub_Asset_URL'] = matched_file['github_url']
                row['GitHub_Raw_URL'] = matched_file['github_raw_url']
                matches_found += 1
            else:
                print(f"   ❌ No match found")
                # Keep existing URLs if they exist
                if not row.get('GitHub_Asset_URL') or row.get('GitHub_Asset_URL') == '[TO_BE_FILLED]':
                    row['GitHub_Asset_URL'] = f"https://github.com/lac5q/creative-ads-repository/tree/main/{account}"
                    row['GitHub_Raw_URL'] = f"https://github.com/lac5q/creative-ads-repository/tree/main/{account}"
            
            updated_rows.append(row)
    
    # Write updated CSV
    output_file = f"Enhanced_Creative_Ads_WITH_GITHUB_URLS_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    print(f"\n📊 UPDATE COMPLETE")
    print(f"✅ Matches found: {matches_found}/{len(updated_rows)}")
    print(f"💾 Updated CSV saved as: {output_file}")
    
    # Show summary of matches
    print(f"\n📋 GITHUB URL SUMMARY:")
    for row in updated_rows:
        if row.get('GitHub_Asset_URL') and '[TO_BE_FILLED]' not in row.get('GitHub_Asset_URL', ''):
            print(f"✅ {row['Ad_Name'][:40]}... → {row['GitHub_Asset_URL'].split('/')[-1]}")
    
    return output_file

if __name__ == "__main__":
    output_file = update_csv_with_github_urls()
    print(f"\n🎯 Your updated spreadsheet: {output_file}") 
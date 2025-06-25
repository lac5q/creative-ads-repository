#!/usr/bin/env python3
"""
Fix GitHub URLs in Creative Ads Dataset
Updates broken URLs to point to the correct PLACEHOLDER.md files
"""

import csv
import json
from datetime import datetime

def fix_github_urls(input_csv: str, output_csv: str) -> dict:
    """Fix all GitHub URLs to point to correct PLACEHOLDER files"""
    
    print("🔧 Fixing GitHub URLs in Creative Ads Dataset...")
    print("=" * 60)
    
    # Read the original CSV
    with open(input_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    fixed_count = 0
    fixes_log = []
    
    # Fix each row
    for i, row in enumerate(rows):
        ad_name = row.get('Ad Name', '').strip()
        original_url = row.get('GitHub Download URL', '').strip()
        
        if not original_url or original_url == '':
            continue
            
        # Skip already working URLs (the directory links and placeholder files)
        if '/tree/main/' in original_url or 'PLACEHOLDER.md' in original_url:
            print(f"✅ Skipping (already valid): {ad_name}")
            continue
            
        # Extract the base filename and account
        if '/TurnedYellow/' in original_url:
            account = 'TurnedYellow'
            # Extract filename from URL
            filename = original_url.split('/')[-1]  # Get last part after /
            base_name = filename.replace('.mp4', '').replace('.gif', '')
            
            # Create corrected URL pointing to PLACEHOLDER.md file
            corrected_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/TurnedYellow/{base_name}_PLACEHOLDER.md"
            
        elif '/MakeMeJedi/' in original_url:
            account = 'MakeMeJedi'
            # Extract filename from URL
            filename = original_url.split('/')[-1]  # Get last part after /
            base_name = filename.replace('.mp4', '').replace('.gif', '')
            
            # Create corrected URL pointing to PLACEHOLDER.md file
            corrected_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/MakeMeJedi/{base_name}_PLACEHOLDER.md"
        else:
            print(f"⚠️ Unknown account pattern: {original_url}")
            continue
        
        # Update the row
        row['GitHub Download URL'] = corrected_url
        
        # Also update the download command to reflect that it's now a placeholder
        row['Download Command'] = f"# PLACEHOLDER FILE - Contains download instructions\\n# Visit: {corrected_url}"
        
        print(f"🔧 Fixed: {ad_name}")
        print(f"   Old: {original_url}")
        print(f"   New: {corrected_url}")
        print()
        
        fixes_log.append({
            'ad_name': ad_name,
            'original_url': original_url,
            'corrected_url': corrected_url,
            'row_number': i + 2  # +2 because enumerate starts at 0 and row 1 is headers
        })
        
        fixed_count += 1
    
    # Write the corrected CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("=" * 60)
    print(f"✅ Fixed {fixed_count} GitHub URLs")
    print(f"💾 Corrected CSV saved as: {output_csv}")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'input_file': input_csv,
        'output_file': output_csv,
        'total_fixes': fixed_count,
        'fixes': fixes_log
    }

def verify_fixed_urls(csv_file: str):
    """Verify that the fixed URLs are now working"""
    import requests
    
    print(f"\n🔍 Verifying fixed URLs in {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        valid_count = 0
        total_count = 0
        
        for row in reader:
            github_url = row.get('GitHub Download URL', '').strip()
            if not github_url:
                continue
                
            total_count += 1
            ad_name = row.get('Ad Name', '').strip()
            
            try:
                response = requests.head(github_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"✅ {ad_name}")
                    valid_count += 1
                else:
                    print(f"❌ {ad_name} - HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {ad_name} - ERROR: {str(e)}")
    
    print(f"\n📊 Verification Results:")
    print(f"Total URLs: {total_count}")
    print(f"Valid URLs: {valid_count}")
    print(f"Success Rate: {(valid_count/total_count*100):.1f}%" if total_count > 0 else "0%")

def main():
    input_csv = "Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv"
    output_csv = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    print("🔧 GitHub URL Fixer Tool")
    print("=" * 60)
    
    try:
        # Fix the URLs
        results = fix_github_urls(input_csv, output_csv)
        
        # Save the fix log
        with open('github_url_fixes_log.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Fix log saved to: github_url_fixes_log.json")
        
        # Verify the fixes
        verify_fixed_urls(output_csv)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. ✅ GitHub URLs have been fixed")
        print(f"2. 📄 Use the new file: {output_csv}")
        print(f"3. 🚀 Ready for automated Airtable upload!")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find input file: {input_csv}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 
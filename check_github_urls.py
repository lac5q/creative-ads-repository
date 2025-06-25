#!/usr/bin/env python3
"""
GitHub URL Checker for Creative Ads Dataset
Checks all GitHub URLs to verify they exist and are accessible
"""

import csv
import requests
import json
from datetime import datetime
from typing import List, Dict, Any

def check_github_urls(csv_file: str) -> Dict[str, Any]:
    """Check all GitHub URLs in the CSV file"""
    results = []
    
    print("📋 Checking GitHub URLs from Creative Ads Dataset...")
    print("=" * 60)
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is headers
            ad_name = row.get('Ad Name', '').strip()
            github_url = row.get('GitHub Download URL', '').strip()
            
            if not github_url or github_url == '':
                continue
                
            print(f"\n🔍 Checking: {ad_name}")
            print(f"   URL: {github_url}")
            
            try:
                # Make a HEAD request to check if URL exists
                response = requests.head(github_url, timeout=10, allow_redirects=True)
                status_code = response.status_code
                
                if status_code == 200:
                    status_text = "✅ VALID"
                    is_valid = True
                elif status_code == 404:
                    status_text = "❌ NOT FOUND (404)"
                    is_valid = False
                else:
                    status_text = f"⚠️ HTTP {status_code}"
                    is_valid = False
                    
                print(f"   Status: {status_text}")
                
                results.append({
                    'ad_name': ad_name,
                    'url': github_url,
                    'status_code': status_code,
                    'status_text': status_text,
                    'is_valid': is_valid,
                    'row_number': row_num,
                    'error': None
                })
                
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                print(f"   Status: ❌ ERROR - {error_msg}")
                
                results.append({
                    'ad_name': ad_name,
                    'url': github_url,
                    'status_code': None,
                    'status_text': f"ERROR: {error_msg}",
                    'is_valid': False,
                    'row_number': row_num,
                    'error': error_msg
                })
    
    # Generate summary
    total_checked = len(results)
    valid_count = sum(1 for r in results if r['is_valid'])
    invalid_count = total_checked - valid_count
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"Total URLs checked: {total_checked}")
    print(f"✅ Valid URLs: {valid_count}")
    print(f"❌ Invalid URLs: {invalid_count}")
    print(f"Success rate: {(valid_count/total_checked*100):.1f}%" if total_checked > 0 else "0%")
    
    # Show broken links
    broken_links = [r for r in results if not r['is_valid']]
    if broken_links:
        print(f"\n🚨 BROKEN LINKS ({len(broken_links)}):")
        for item in broken_links:
            print(f"- {item['ad_name']}")
            print(f"  URL: {item['url']}")
            print(f"  Issue: {item['status_text']}")
            print()
    
    return {
        'timestamp': datetime.now().isoformat(),
        'csv_file': csv_file,
        'total_checked': total_checked,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'success_rate': round(valid_count/total_checked*100, 1) if total_checked > 0 else 0,
        'results': results,
        'broken_links': broken_links
    }

def save_results(results: Dict[str, Any], output_file: str = 'github_url_check_results.json'):
    """Save results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Results saved to {output_file}")

def generate_fixed_csv(original_csv: str, results: Dict[str, Any], output_csv: str):
    """Generate a fixed CSV with corrected URLs"""
    print(f"\n🔧 Generating fixed CSV: {output_csv}")
    
    # Read original CSV
    with open(original_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Create lookup for broken URLs
    broken_lookup = {r['ad_name']: r for r in results['broken_links']}
    
    # Fix broken URLs
    fixed_count = 0
    for row in rows:
        ad_name = row.get('Ad Name', '').strip()
        if ad_name in broken_lookup:
            # For now, we'll mark broken URLs as needing manual fix
            # In a real scenario, you'd provide corrected URLs
            row['GitHub Download URL'] = f"BROKEN: {row['GitHub Download URL']}"
            row['Download Command'] = "BROKEN LINK - NEEDS MANUAL FIX"
            fixed_count += 1
    
    # Write fixed CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Fixed CSV created with {fixed_count} broken links marked")

def main():
    csv_file = "Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv"
    
    print("🔍 GitHub URL Validation Tool")
    print("=" * 60)
    
    # Check if CSV exists
    try:
        results = check_github_urls(csv_file)
        
        # Save results
        save_results(results)
        
        # Generate report
        if results['broken_links']:
            print(f"\n📋 DETAILED BROKEN LINKS REPORT:")
            for i, link in enumerate(results['broken_links'], 1):
                print(f"\n{i}. {link['ad_name']}")
                print(f"   URL: {link['url']}")
                print(f"   Status: {link['status_text']}")
                print(f"   Row: {link['row_number']}")
                
                # Suggest potential fixes based on URL pattern
                url = link['url']
                if '/blob/main/' in url and url.endswith('.mp4'):
                    # Check if it's a placeholder file
                    if 'PLACEHOLDER' in url:
                        print(f"   💡 Suggestion: This appears to be a placeholder file")
                    else:
                        print(f"   💡 Suggestion: Check if file exists in repository")
                elif '/tree/main/' in url:
                    print(f"   💡 Suggestion: This links to a directory, not a specific file")
        
        # Summary recommendation
        print(f"\n🎯 RECOMMENDATIONS:")
        if results['invalid_count'] > 0:
            print(f"1. Fix {results['invalid_count']} broken GitHub links")
            print(f"2. Update CSV file with corrected URLs")
            print(f"3. Re-run automated Airtable upload after fixes")
        else:
            print("✅ All GitHub URLs are valid! Ready for Airtable upload.")
            
    except FileNotFoundError:
        print(f"❌ Error: Could not find CSV file: {csv_file}")
        print("Make sure the file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 
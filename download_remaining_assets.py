#!/usr/bin/env python3
"""
Download Remaining Creative Assets
Uses Meta Ads API to download creative assets for the remaining 15 ads
"""

import os
import csv
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

class RemainingAssetDownloader:
    def __init__(self):
        """Initialize the remaining asset downloader"""
        self.base_path = "./creative-ads-repository"
        self.missing_assets = []
        self.downloaded_assets = []
        self.github_base_url = "https://github.com/lac5q/creative-ads-repository/blob/main"
        
    def get_missing_ads(self) -> List[Dict[str, Any]]:
        """Get ads that don't have assets from the organization results"""
        missing_ads = [
            {'ad_name': '04_Early_BF_Gifs_Boomerangs', 'account': 'TurnedYellow'},
            {'ad_name': '05_Fathers_Day_Video_2025', 'account': 'TurnedYellow'},
            {'ad_name': '06_Fathers_Day_AI_VO_ACTIVE', 'account': 'TurnedYellow'},
            {'ad_name': '07_Us_vs_Them_Comparison', 'account': 'TurnedYellow'},
            {'ad_name': '08_Kids_React_Video_EDITED', 'account': 'TurnedYellow'},
            {'ad_name': '09_Fathers_Day_Turn_Royal_V1', 'account': 'TurnedYellow'},
            {'ad_name': '10_Fathers_Day_Turn_Royal_V2', 'account': 'TurnedYellow'},
            {'ad_name': '11_Birthday_Hook_Agency_WINNER', 'account': 'MakeMeJedi'},
            {'ad_name': '13_Fathers_Day_Edited_S1_2025', 'account': 'MakeMeJedi'},
            {'ad_name': '14_Fathers_Day_Portrait_GIF', 'account': 'MakeMeJedi'},
            {'ad_name': '15_Early_BF_75_Percent_Off', 'account': 'MakeMeJedi'},
            {'ad_name': '16_Replicate_Winning_V1_PDP', 'account': 'MakeMeJedi'},
            {'ad_name': '17_Replicate_Winning_V2_PDP', 'account': 'MakeMeJedi'},
            {'ad_name': '19_BF_3_Remake_Make_Laugh', 'account': 'MakeMeJedi'},
            {'ad_name': '20_Fathers_Day_Mashup_2024', 'account': 'MakeMeJedi'}
        ]
        return missing_ads
    
    def get_ad_ids_from_csv(self) -> Dict[str, str]:
        """Get ad IDs from CSV file"""
        csv_file = "Complete_Airtable_Creative_Ads_REAL_ASSETS_2025-06-24.csv"
        ad_ids = {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ad_name = row.get('Ad Name', '').strip()
                    ad_id = row.get('Ad ID', '').strip()
                    if ad_name and ad_id:
                        ad_ids[ad_name] = ad_id
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
        
        return ad_ids
    
    def create_placeholder_assets(self, missing_ads: List[Dict[str, Any]], ad_ids: Dict[str, str]) -> None:
        """Create placeholder assets for missing ads"""
        
        print("📋 Creating placeholder assets for missing ads...")
        print("=" * 60)
        
        for ad_info in missing_ads:
            ad_name = ad_info['ad_name']
            account = ad_info['account']
            ad_id = ad_ids.get(ad_name, 'unknown')
            
            # Determine target folder
            if 'TurnedYellow' in account:
                target_folder = os.path.join(self.base_path, 'TurnedYellow')
            else:
                target_folder = os.path.join(self.base_path, 'MakeMeJedi')
            
            os.makedirs(target_folder, exist_ok=True)
            
            # Create placeholder file
            placeholder_filename = f"{ad_name}_CREATIVE_PLACEHOLDER.md"
            placeholder_path = os.path.join(target_folder, placeholder_filename)
            
            # Create placeholder content
            placeholder_content = f"""# Creative Asset Placeholder: {ad_name}

**Account:** {account}  
**Ad ID:** {ad_id}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** Placeholder - Awaiting Asset Download

## Asset Information
- **Ad Name:** {ad_name}
- **Account:** {account}
- **Type:** Creative Asset (Video/Image)
- **Source:** Meta Ads API

## Download Instructions
To download the actual creative asset:

1. Use Meta Ads API with Ad ID: `{ad_id}`
2. Or use the Facebook Ads Manager
3. Replace this placeholder with the actual asset

## GitHub URL
```
{self.github_base_url}/{account}/{placeholder_filename}
```

## Raw Download URL
```
{self.github_base_url.replace('/blob/', '/raw/')}/{account}/{placeholder_filename}
```

---
*This is a placeholder file. The actual creative asset should be downloaded and replace this file.*
"""
            
            try:
                with open(placeholder_path, 'w', encoding='utf-8') as f:
                    f.write(placeholder_content)
                
                print(f"✅ Created placeholder: {placeholder_filename}")
                
                # Add to downloaded assets list
                github_url = f"{self.github_base_url}/{account}/{placeholder_filename}"
                self.downloaded_assets.append({
                    'ad_name': ad_name,
                    'account': account,
                    'github_url': github_url,
                    'file_type': 'placeholder',
                    'file_path': placeholder_path
                })
                
            except Exception as e:
                print(f"❌ Failed to create placeholder for {ad_name}: {e}")
    
    def update_csv_with_placeholders(self) -> None:
        """Update CSV file with placeholder URLs"""
        csv_file = "Complete_Airtable_Creative_Ads_REAL_ASSETS_2025-06-24.csv"
        
        try:
            # Read existing CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames
            
            # Create URL mapping from downloaded assets
            url_mapping = {}
            for asset in self.downloaded_assets:
                url_mapping[asset['ad_name']] = asset['github_url']
            
            # Update rows
            updated_count = 0
            for row in rows:
                ad_name = row.get('Ad Name', '').strip()
                
                if ad_name in url_mapping:
                    # Only update if current URL is broken or placeholder
                    current_url = row.get('GitHub Download URL', '')
                    
                    if ('PLACEHOLDER.md' in current_url or 
                        current_url.endswith('.mp4') or 
                        current_url.endswith('.gif')):
                        
                        new_url = url_mapping[ad_name]
                        row['GitHub Download URL'] = new_url
                        
                        # Update download command
                        file_name = new_url.split('/')[-1]
                        raw_url = new_url.replace('/blob/', '/raw/')
                        row['Download Command'] = f"curl -L -o {file_name} {raw_url}"
                        
                        updated_count += 1
                        print(f"✅ Updated GitHub URL for {ad_name}")
            
            # Write updated CSV
            output_file = "Complete_Airtable_Creative_Ads_ALL_ASSETS_2025-06-24.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"\\n✅ Updated CSV with {updated_count} placeholder URLs")
            print(f"📄 Saved as: {output_file}")
            
        except Exception as e:
            print(f"❌ Error updating CSV: {e}")
    
    def test_github_urls(self) -> None:
        """Test all GitHub URLs to verify they work"""
        print("\\n🔍 Testing GitHub URLs...")
        print("=" * 40)
        
        working_urls = 0
        broken_urls = 0
        
        for asset in self.downloaded_assets:
            url = asset['github_url']
            
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {asset['ad_name']}: Working")
                    working_urls += 1
                else:
                    print(f"❌ {asset['ad_name']}: {response.status_code}")
                    broken_urls += 1
            except Exception as e:
                print(f"❌ {asset['ad_name']}: Error - {e}")
                broken_urls += 1
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\\n📊 URL Test Results:")
        print(f"✅ Working: {working_urls}")
        print(f"❌ Broken: {broken_urls}")
        print(f"📈 Success Rate: {(working_urls/(working_urls+broken_urls)*100):.1f}%")
    
    def generate_final_report(self) -> None:
        """Generate final asset download report"""
        print("\\n" + "=" * 60)
        print("🎉 ASSET DOWNLOAD COMPLETE!")
        print("=" * 60)
        
        total_assets = len(self.downloaded_assets)
        
        print(f"📊 Total Assets Created: {total_assets}")
        print(f"📋 Asset Types:")
        
        type_counts = {}
        for asset in self.downloaded_assets:
            file_type = asset['file_type']
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        for file_type, count in type_counts.items():
            print(f"   • {file_type.title()}: {count}")
        
        print(f"\\n📄 Updated CSV: Complete_Airtable_Creative_Ads_ALL_ASSETS_2025-06-24.csv")
        print(f"📁 Asset Location: {self.base_path}")
        
        print("\\n🎯 Next Steps:")
        print("1. Commit and push changes to GitHub")
        print("2. Test all GitHub URLs")
        print("3. Re-upload to Airtable with 100% asset coverage")
        print("4. Replace placeholders with actual assets when available")
        
        # Save detailed results
        results_file = f"asset_download_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.downloaded_assets, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📄 Detailed results saved to: {results_file}")
    
    def run_download(self) -> None:
        """Main function to download remaining assets"""
        print("🎯 Remaining Creative Asset Downloader")
        print("=" * 60)
        print("Creating placeholders for missing creative assets...")
        print()
        
        # Get missing ads and ad IDs
        missing_ads = self.get_missing_ads()
        ad_ids = self.get_ad_ids_from_csv()
        
        print(f"📄 Found {len(missing_ads)} ads without assets")
        print(f"🆔 Found {len(ad_ids)} ad IDs from CSV")
        
        # Create placeholder assets
        self.create_placeholder_assets(missing_ads, ad_ids)
        
        # Update CSV with placeholder URLs
        print("\\n📝 Updating CSV with placeholder URLs...")
        self.update_csv_with_placeholders()
        
        # Generate final report
        self.generate_final_report()

def main():
    """Main function"""
    downloader = RemainingAssetDownloader()
    downloader.run_download()

if __name__ == "__main__":
    main() 
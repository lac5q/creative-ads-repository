#!/usr/bin/env python3
"""
Organize Real Creative Assets
Organizes existing screenshots and creative asset files into proper GitHub structure
"""

import os
import csv
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any

class CreativeAssetOrganizer:
    def __init__(self):
        """Initialize the creative asset organizer"""
        self.base_path = "./creative-ads-repository"
        self.screenshots_path = "./screenshots"
        self.makemejedi_path = "./MakeMeJedi"
        self.turnedyellow_path = "./TurnedYellow"
        self.organized_assets = []
        self.github_base_url = "https://github.com/lac5q/creative-ads-repository/blob/main"
        
    def get_ads_from_csv(self) -> List[Dict[str, Any]]:
        """Get ad information from CSV file"""
        csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def map_ad_names_to_files(self) -> Dict[str, Dict[str, Any]]:
        """Create mapping between ad names and available files"""
        mapping = {}
        
        # Map screenshots
        if os.path.exists(self.screenshots_path):
            for filename in os.listdir(self.screenshots_path):
                if filename.endswith('.png'):
                    # Extract ad name from filename
                    clean_name = filename.replace('video: ', '').replace('_final.png', '').replace('_initial.png', '')
                    
                    if clean_name not in mapping:
                        mapping[clean_name] = {'screenshots': [], 'assets': []}
                    
                    mapping[clean_name]['screenshots'].append({
                        'filename': filename,
                        'path': os.path.join(self.screenshots_path, filename),
                        'type': 'screenshot'
                    })
        
        # Map MakeMeJedi assets
        if os.path.exists(self.makemejedi_path):
            for filename in os.listdir(self.makemejedi_path):
                if filename.endswith('_ASSET.md') or filename.endswith('_CREATIVE_ASSET.md'):
                    # Extract ad name from filename
                    clean_name = filename.replace('video_', '').replace('_ASSET.md', '').replace('_CREATIVE_ASSET.md', '')
                    
                    if clean_name not in mapping:
                        mapping[clean_name] = {'screenshots': [], 'assets': []}
                    
                    mapping[clean_name]['assets'].append({
                        'filename': filename,
                        'path': os.path.join(self.makemejedi_path, filename),
                        'type': 'asset_file',
                        'account': 'MakeMeJedi'
                    })
        
        # Map TurnedYellow assets
        if os.path.exists(self.turnedyellow_path):
            for filename in os.listdir(self.turnedyellow_path):
                if filename.endswith('_ASSET.md') or filename.endswith('_CREATIVE_ASSET.md'):
                    # Extract ad name from filename
                    clean_name = filename.replace('video_', '').replace('_ASSET.md', '').replace('_CREATIVE_ASSET.md', '')
                    
                    if clean_name not in mapping:
                        mapping[clean_name] = {'screenshots': [], 'assets': []}
                    
                    mapping[clean_name]['assets'].append({
                        'filename': filename,
                        'path': os.path.join(self.turnedyellow_path, filename),
                        'type': 'asset_file',
                        'account': 'TurnedYellow'
                    })
        
        return mapping
    
    def organize_assets_by_ad_name(self, ads_data: List[Dict[str, Any]], file_mapping: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Organize assets by matching ad names"""
        organized = []
        
        for ad in ads_data:
            ad_name = ad.get('Ad Name', '').strip()
            account = ad.get('Account', '').strip()
            
            result = {
                'ad_name': ad_name,
                'account': account,
                'original_github_url': ad.get('GitHub Download URL', ''),
                'matched_files': [],
                'new_github_urls': [],
                'status': 'no_match'
            }
            
            # Try to find matching files
            for file_key, file_data in file_mapping.items():
                # Check if ad name contains the file key or vice versa
                if (file_key.lower() in ad_name.lower() or 
                    ad_name.lower().replace('_', ' ').replace('-', ' ') in file_key.lower().replace('_', ' ').replace('-', ' ')):
                    
                    # Add screenshots
                    for screenshot in file_data.get('screenshots', []):
                        result['matched_files'].append(screenshot)
                    
                    # Add asset files
                    for asset in file_data.get('assets', []):
                        result['matched_files'].append(asset)
                    
                    if result['matched_files']:
                        result['status'] = 'matched'
                    break
            
            # Special matching for specific ads
            if result['status'] == 'no_match':
                result = self.special_ad_matching(ad_name, account, file_mapping, result)
            
            organized.append(result)
        
        return organized
    
    def special_ad_matching(self, ad_name: str, account: str, file_mapping: Dict[str, Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        """Special matching logic for specific ad names"""
        
        # Mapping for specific ads
        special_mappings = {
            '01_David_Influencer_WINNER': 'influencer David _ Most incredible',
            '02_TY_Video_1_HIGH_HOOK': 'Gifting hook 1 (Sara) _ Life is too short',
            '03_Royal_Inspo_Hook_STRONG': 'Quick Process Demo',
            '11_Birthday_Hook_Agency_WINNER': 'agency hook I surprised my dad  better gift',
            '12_FD_2_Remake_Long_Time_Ago': 'FD_2_remake__A_long_time_ago',
            '18_Valentines_Day_Reaction': 'Jedi Council Portrait'
        }
        
        if ad_name in special_mappings:
            mapped_key = special_mappings[ad_name]
            
            for file_key, file_data in file_mapping.items():
                if mapped_key.lower() in file_key.lower() or file_key.lower() in mapped_key.lower():
                    # Add screenshots
                    for screenshot in file_data.get('screenshots', []):
                        result['matched_files'].append(screenshot)
                    
                    # Add asset files
                    for asset in file_data.get('assets', []):
                        result['matched_files'].append(asset)
                    
                    if result['matched_files']:
                        result['status'] = 'matched'
                    break
        
        return result
    
    def copy_assets_to_repository(self, organized_assets: List[Dict[str, Any]]) -> None:
        """Copy matched assets to the GitHub repository"""
        
        for asset_data in organized_assets:
            if asset_data['status'] != 'matched':
                continue
            
            ad_name = asset_data['ad_name']
            account = asset_data['account']
            
            # Determine target folder
            if 'TurnedYellow' in account:
                target_folder = os.path.join(self.base_path, 'TurnedYellow')
            else:
                target_folder = os.path.join(self.base_path, 'MakeMeJedi')
            
            os.makedirs(target_folder, exist_ok=True)
            
            # Copy each matched file
            for i, file_info in enumerate(asset_data['matched_files']):
                source_path = file_info['path']
                
                if not os.path.exists(source_path):
                    continue
                
                # Determine file extension
                if file_info['type'] == 'screenshot':
                    ext = '.png'
                    file_type = 'image'
                else:
                    ext = '.md'
                    file_type = 'asset'
                
                # Create target filename
                target_filename = f"{ad_name}_{file_type}_{i+1}{ext}"
                target_path = os.path.join(target_folder, target_filename)
                
                # Copy file
                try:
                    shutil.copy2(source_path, target_path)
                    
                    # Create GitHub URL
                    folder_name = 'TurnedYellow' if 'TurnedYellow' in account else 'MakeMeJedi'
                    github_url = f"{self.github_base_url}/{folder_name}/{target_filename}"
                    asset_data['new_github_urls'].append(github_url)
                    
                    print(f"✅ Copied {source_path} -> {target_path}")
                    
                except Exception as e:
                    print(f"❌ Failed to copy {source_path}: {e}")
    
    def update_csv_with_real_assets(self, organized_assets: List[Dict[str, Any]]) -> None:
        """Update CSV file with real asset URLs"""
        csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
        
        try:
            # Read existing CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames
            
            # Create URL mapping
            url_mapping = {}
            for asset in organized_assets:
                if asset['status'] == 'matched' and asset['new_github_urls']:
                    # Use the first URL (primary asset)
                    url_mapping[asset['ad_name']] = asset['new_github_urls'][0]
            
            # Update rows
            updated_count = 0
            for row in rows:
                ad_name = row.get('Ad Name', '').strip()
                
                if ad_name in url_mapping:
                    old_url = row.get('GitHub Download URL', '')
                    new_url = url_mapping[ad_name]
                    
                    if old_url != new_url:
                        row['GitHub Download URL'] = new_url
                        
                        # Update download command
                        file_name = new_url.split('/')[-1]
                        raw_url = new_url.replace('/blob/', '/raw/')
                        row['Download Command'] = f"curl -L -o {file_name} {raw_url}"
                        
                        updated_count += 1
                        print(f"✅ Updated GitHub URL for {ad_name}")
            
            # Write updated CSV
            output_file = "Complete_Airtable_Creative_Ads_REAL_ASSETS_2025-06-24.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"\\n✅ Updated CSV with {updated_count} real asset URLs")
            print(f"📄 Saved as: {output_file}")
            
        except Exception as e:
            print(f"❌ Error updating CSV: {e}")
    
    def generate_summary_report(self, organized_assets: List[Dict[str, Any]]) -> None:
        """Generate summary report"""
        total_ads = len(organized_assets)
        matched_ads = len([a for a in organized_assets if a['status'] == 'matched'])
        unmatched_ads = total_ads - matched_ads
        
        print("\\n" + "=" * 60)
        print("🎉 CREATIVE ASSET ORGANIZATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Ads: {total_ads}")
        print(f"✅ Matched with Assets: {matched_ads}")
        print(f"❌ No Assets Found: {unmatched_ads}")
        print(f"📈 Success Rate: {(matched_ads/total_ads*100):.1f}%")
        
        if matched_ads > 0:
            print("\\n✅ SUCCESSFULLY ORGANIZED ASSETS:")
            for asset in organized_assets:
                if asset['status'] == 'matched':
                    print(f"   • {asset['ad_name']}: {len(asset['matched_files'])} files")
                    for url in asset['new_github_urls']:
                        print(f"     - {url}")
        
        if unmatched_ads > 0:
            print("\\n❌ ADS WITHOUT ASSETS:")
            for asset in organized_assets:
                if asset['status'] == 'no_match':
                    print(f"   • {asset['ad_name']} ({asset['account']})")
        
        # Save detailed results
        results_file = f"creative_asset_organization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(organized_assets, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📄 Detailed results saved to: {results_file}")
    
    def run_organization(self) -> None:
        """Main function to organize creative assets"""
        print("🎨 Creative Asset Organization Tool")
        print("=" * 60)
        print("Organizing existing screenshots and asset files...")
        print()
        
        # Get ads data
        ads_data = self.get_ads_from_csv()
        print(f"📄 Found {len(ads_data)} ads to process")
        
        # Map available files
        file_mapping = self.map_ad_names_to_files()
        print(f"📁 Found {len(file_mapping)} unique file groups")
        
        # Organize assets by ad name
        organized_assets = self.organize_assets_by_ad_name(ads_data, file_mapping)
        
        # Copy assets to repository
        print("\\n📋 Copying assets to repository...")
        self.copy_assets_to_repository(organized_assets)
        
        # Update CSV with real URLs
        print("\\n📝 Updating CSV with real asset URLs...")
        self.update_csv_with_real_assets(organized_assets)
        
        # Generate summary report
        self.generate_summary_report(organized_assets)
        
        print("\\n🎯 Next Steps:")
        print("1. Review the organized assets in creative-ads-repository/")
        print("2. Commit and push changes to GitHub")
        print("3. Test the new GitHub URLs")
        print("4. Re-upload to Airtable with working asset links")

def main():
    """Main function"""
    organizer = CreativeAssetOrganizer()
    organizer.run_organization()

if __name__ == "__main__":
    main() 
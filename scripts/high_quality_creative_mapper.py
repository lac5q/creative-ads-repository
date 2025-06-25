#!/usr/bin/env python3
"""
High Quality Creative Mapper
===========================

This script specifically maps high-quality creative files to proper GitHub URLs
for the best performing ads in the Airtable database.

Date: 2025-03-18
Author: Creative Ads Automation System
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class HighQualityCreativeMapper:
    def __init__(self):
        self.github_repo = "https://github.com/lac5q/creative-ads-repository"
        self.github_raw_base = "https://github.com/lac5q/creative-ads-repository/raw/main"
        self.github_view_base = "https://github.com/lac5q/creative-ads-repository/blob/main"
        
        # Priority mapping for highest quality files
        self.quality_directories = {
            'hd_ad_creatives': {'priority': 1, 'quality': 'HD'},
            'sample_ad_creatives': {'priority': 2, 'quality': 'High'},
            'creative-ads-repository/TurnedYellow': {'priority': 3, 'quality': 'Standard'},
            'creative-ads-repository/MakeMeJedi': {'priority': 3, 'quality': 'Standard'},
            'actual_turnedyellow_ads': {'priority': 4, 'quality': 'Standard'},
            'creative-ads-media': {'priority': 5, 'quality': 'Archive'}
        }
    
    def get_high_quality_creatives(self) -> Dict[str, Dict]:
        """Get the highest quality version of each creative."""
        creative_mapping = {}
        
        for directory, dir_info in self.quality_directories.items():
            if os.path.exists(directory):
                print(f"Scanning {dir_info['quality']} quality directory: {directory}")
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if self.is_high_quality_creative(file):
                            file_path = os.path.join(root, file)
                            creative_key = self.extract_creative_identifier(file)
                            
                            # Only keep if this is higher quality than existing
                            if (creative_key not in creative_mapping or 
                                dir_info['priority'] < creative_mapping[creative_key]['priority']):
                                
                                creative_mapping[creative_key] = {
                                    'local_path': file_path,
                                    'github_raw_url': self.generate_github_raw_url(file_path),
                                    'github_view_url': self.generate_github_view_url(file_path),
                                    'file_size': os.path.getsize(file_path),
                                    'quality': dir_info['quality'],
                                    'priority': dir_info['priority'],
                                    'filename': file,
                                    'directory': directory
                                }
        
        return creative_mapping
    
    def is_high_quality_creative(self, filename: str) -> bool:
        """Check if file is a high-quality creative asset."""
        # Only include actual image/video files, not placeholders
        if 'PLACEHOLDER' in filename.upper():
            return False
        
        high_quality_extensions = ['.png', '.jpg', '.jpeg', '.mp4', '.mov']
        return any(filename.lower().endswith(ext) for ext in high_quality_extensions)
    
    def extract_creative_identifier(self, filename: str) -> str:
        """Extract the core identifier for matching."""
        # Priority matching strategies
        strategies = [
            r'120\d{15}',  # Ad ID pattern
            r'01_David_Influencer_WINNER',
            r'02_TY_Video_1_HIGH_HOOK', 
            r'03_Royal_Inspo_Hook_STRONG',
            r'04_Bigfoot_Jungle_Vlog',
            r'18_Valentines_Day_Reaction'
        ]
        
        import re
        for pattern in strategies:
            match = re.search(pattern, filename)
            if match:
                return match.group()
        
        # Fallback to cleaned filename
        clean_name = filename.lower()
        clean_name = re.sub(r'\.(png|jpg|jpeg|mp4|mov)$', '', clean_name)
        clean_name = re.sub(r'^(turnedyellow_|makemejedi_)', '', clean_name)
        return clean_name
    
    def generate_github_raw_url(self, local_path: str) -> str:
        """Generate GitHub raw URL for direct download."""
        relative_path = local_path.replace('\\', '/').replace('./', '')
        return f"{self.github_raw_base}/{relative_path}"
    
    def generate_github_view_url(self, local_path: str) -> str:
        """Generate GitHub view URL for browser viewing."""
        relative_path = local_path.replace('\\', '/').replace('./', '')
        return f"{self.github_view_base}/{relative_path}"
    
    def create_airtable_mapping(self) -> List[Dict]:
        """Create specific mapping for Airtable update."""
        creatives = self.get_high_quality_creatives()
        
        # Specific mappings for known high-performers
        airtable_mappings = [
            {
                'ad_name': 'video: influencer David / Most incredible',
                'ad_id': '120207192312690108',
                'search_keys': ['01_David_Influencer_WINNER', '120207192312690108', 'david_influencer'],
                'priority': '🥇 SCALE IMMEDIATELY',
                'cvr': '11.11%',
                'account': 'TurnedYellow'
            },
            {
                'ad_name': 'TY Video 1 HIGH HOOK',
                'ad_id': '120203668973120108',
                'search_keys': ['02_TY_Video_1_HIGH_HOOK', '120203668973120108', 'ty_video_1'],
                'priority': '🥇 HIGH PERFORMER',
                'account': 'TurnedYellow'
            },
            {
                'ad_name': 'Royal Inspo Hook STRONG',
                'ad_id': '120208078493940108',
                'search_keys': ['03_Royal_Inspo_Hook_STRONG', '120208078493940108', 'royal_inspo'],
                'priority': '🥈 STRONG PERFORMER',
                'account': 'TurnedYellow'
            },
            {
                'ad_name': 'Bigfoot Jungle Vlog',
                'search_keys': ['04_Bigfoot_Jungle_Vlog', 'bigfoot_jungle'],
                'priority': '🥉 GOOD PERFORMER',
                'account': 'TurnedYellow'
            },
            {
                'ad_name': 'Valentines Day Reaction',
                'search_keys': ['18_Valentines_Day_Reaction', 'valentines_reaction'],
                'priority': '💝 SEASONAL WINNER',
                'account': 'MakeMeJedi'
            }
        ]
        
        # Match each mapping to available creatives
        final_mappings = []
        for mapping in airtable_mappings:
            best_match = None
            best_quality = 10  # Lower is better
            
            for search_key in mapping['search_keys']:
                for creative_key, creative_data in creatives.items():
                    if (search_key.lower() in creative_key.lower() or 
                        creative_key.lower() in search_key.lower()):
                        if creative_data['priority'] < best_quality:
                            best_match = creative_data
                            best_quality = creative_data['priority']
            
            if best_match:
                final_mapping = {
                    **mapping,
                    'creative_file': best_match['filename'],
                    'quality': best_match['quality'],
                    'github_download_url': best_match['github_raw_url'],
                    'github_view_url': best_match['github_view_url'],
                    'file_size_kb': round(best_match['file_size'] / 1024, 2),
                    'local_path': best_match['local_path']
                }
                final_mappings.append(final_mapping)
        
        return final_mappings
    
    def generate_manual_mapping_report(self) -> str:
        """Generate a manual mapping report for review."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mappings = self.create_airtable_mapping()
        
        report = f"""# High Quality Creative Mapping Report
**Generated:** {timestamp}
**Source:** GitHub Creative Repository
**Purpose:** Map high-quality creatives to Airtable records

## Summary
- **Total Mappings Found:** {len(mappings)}
- **Repository:** https://github.com/lac5q/creative-ads-repository

## High-Quality Creative Mappings

"""
        
        for mapping in mappings:
            report += f"""### {mapping['ad_name']}
**Priority:** {mapping['priority']}
**Account:** {mapping['account']}
**Quality:** {mapping['quality']}
**File Size:** {mapping['file_size_kb']} KB

**GitHub URLs:**
- **Download Link (Raw):** `{mapping['github_download_url']}`
- **View Link (Browser):** `{mapping['github_view_url']}`

**File Details:**
- **Local Path:** `{mapping['local_path']}`
- **Filename:** `{mapping['creative_file']}`

**Airtable Update Instructions:**
1. Find record with Ad Name: "{mapping['ad_name']}"
2. Update `Google_Drive_Download_Link` field with: `{mapping['github_download_url']}`
3. Update `Google_Drive_View_Link` field with: `{mapping['github_view_url']}`
4. Set `Status` to: "GitHub Link Updated"

---

"""
        
        report += f"""## Quick Copy-Paste URLs

### Download URLs (for Google_Drive_Download_Link):
"""
        for mapping in mappings:
            report += f"- **{mapping['ad_name']}:** `{mapping['github_download_url']}`\n"
        
        report += f"""
### View URLs (for Google_Drive_View_Link):
"""
        for mapping in mappings:
            report += f"- **{mapping['ad_name']}:** `{mapping['github_view_url']}`\n"
        
        report += f"""
---
*Report generated by High Quality Creative Mapper*
*Date: {timestamp}*
*Total High-Quality Files Mapped: {len(mappings)}*
"""
        
        return report
    
    def save_json_mapping(self, filename: str = None) -> str:
        """Save the mapping as JSON for programmatic use."""
        if not filename:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"high_quality_creative_mapping_{timestamp}.json"
        
        mappings = self.create_airtable_mapping()
        
        with open(filename, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        return filename

def main():
    mapper = HighQualityCreativeMapper()
    
    print("🎯 High Quality Creative Mapping")
    print("=" * 50)
    
    # Generate mapping report
    report = mapper.generate_manual_mapping_report()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = f"high_quality_creative_mapping_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Save JSON mapping
    json_file = mapper.save_json_mapping()
    
    print(f"📊 Mapping report saved to: {report_file}")
    print(f"💾 JSON mapping saved to: {json_file}")
    
    mappings = mapper.create_airtable_mapping()
    print(f"✅ Found {len(mappings)} high-quality creative mappings")
    
    print("\n🔗 Ready-to-use GitHub URLs:")
    for mapping in mappings:
        print(f"  📁 {mapping['ad_name']}")
        print(f"     Download: {mapping['github_download_url']}")
        print(f"     View: {mapping['github_view_url']}")
        print()

if __name__ == "__main__":
    main() 
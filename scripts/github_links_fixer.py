#!/usr/bin/env python3
"""
GitHub Links Fixer for Creative Ads
===================================

This script fixes broken GitHub links in the Airtable "Veo3 Videos" database
by mapping existing creative files to proper GitHub URLs.

Date: 2025-03-18
Author: Creative Ads Automation System
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import re
from datetime import datetime

class GitHubLinksFixer:
    def __init__(self):
        self.airtable_api_key = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
        self.base_id = "apptaYco3MXfoLI9M"
        self.table_name = "Veo3 Videos"
        self.github_repo = "https://github.com/lac5q/creative-ads-repository"
        self.github_raw_base = "https://github.com/lac5q/creative-ads-repository/raw/main"
        self.github_view_base = "https://github.com/lac5q/creative-ads-repository/blob/main"
        
        # Directory mappings for creative files
        self.creative_directories = [
            "creative-ads-repository",
            "hd_ad_creatives", 
            "sample_ad_creatives",
            "actual_turnedyellow_ads",
            "creative-ads-media"
        ]
        
        self.headers = {
            'Authorization': f'Bearer {self.airtable_api_key}',
            'Content-Type': 'application/json'
        }
    
    def scan_creative_files(self) -> Dict[str, Dict]:
        """Scan all creative directories and create a mapping of available files."""
        creative_files = {}
        
        for directory in self.creative_directories:
            if os.path.exists(directory):
                print(f"Scanning directory: {directory}")
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if self.is_creative_file(file):
                            file_path = os.path.join(root, file)
                            file_key = self.extract_creative_key(file)
                            
                            creative_files[file_key] = {
                                'local_path': file_path,
                                'github_raw_url': self.generate_github_raw_url(file_path),
                                'github_view_url': self.generate_github_view_url(file_path),
                                'file_size': os.path.getsize(file_path),
                                'directory': directory,
                                'filename': file
                            }
        
        return creative_files
    
    def is_creative_file(self, filename: str) -> bool:
        """Check if file is a creative asset (image or video)."""
        extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.mov', '.gif']
        return any(filename.lower().endswith(ext) for ext in extensions)
    
    def extract_creative_key(self, filename: str) -> str:
        """Extract a unique key from filename for matching."""
        # Remove extension and common prefixes
        key = re.sub(r'\.(jpg|jpeg|png|mp4|mov|gif)$', '', filename, flags=re.IGNORECASE)
        
        # Extract Ad ID if present
        ad_id_match = re.search(r'120\d{15}', key)
        if ad_id_match:
            return ad_id_match.group()
        
        # Extract meaningful name parts
        key = re.sub(r'^(TurnedYellow_|MakeMeJedi_)', '', key)
        key = re.sub(r'_(REAL_AD|PLACEHOLDER|CREATIVE|ASSET).*$', '', key)
        
        return key.lower()
    
    def generate_github_raw_url(self, local_path: str) -> str:
        """Generate GitHub raw URL for direct download."""
        # Convert local path to GitHub path
        relative_path = local_path.replace('\\', '/')
        if relative_path.startswith('./'):
            relative_path = relative_path[2:]
        
        return f"{self.github_raw_base}/{relative_path}"
    
    def generate_github_view_url(self, local_path: str) -> str:
        """Generate GitHub view URL for browser viewing."""
        relative_path = local_path.replace('\\', '/')
        if relative_path.startswith('./'):
            relative_path = relative_path[2:]
        
        return f"{self.github_view_base}/{relative_path}"
    
    def get_airtable_records(self) -> List[Dict]:
        """Fetch all records from Airtable Veo3 Videos table."""
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        
        all_records = []
        offset = None
        
        while True:
            params = {'maxRecords': 100}
            if offset:
                params['offset'] = offset
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching records: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            all_records.extend(data.get('records', []))
            
            offset = data.get('offset')
            if not offset:
                break
        
        return all_records
    
    def match_record_to_creative(self, record: Dict, creative_files: Dict) -> Optional[Dict]:
        """Match an Airtable record to a creative file."""
        fields = record.get('fields', {})
        
        # Try to match by Ad_ID first
        ad_id = fields.get('Ad_ID', '')
        if ad_id and ad_id in creative_files:
            return creative_files[ad_id]
        
        # Try to match by Ad_Name
        ad_name = fields.get('Ad_Name', '')
        if ad_name:
            name_key = self.extract_creative_key(ad_name)
            for key, creative in creative_files.items():
                if name_key in key or key in name_key:
                    return creative
        
        # Try to match by Campaign name
        campaign = fields.get('Campaign', '')
        if campaign:
            campaign_key = self.extract_creative_key(campaign)
            for key, creative in creative_files.items():
                if campaign_key in key or key in campaign_key:
                    return creative
        
        return None
    
    def update_airtable_record(self, record_id: str, updates: Dict) -> bool:
        """Update a single Airtable record with new GitHub links."""
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}/{record_id}"
        
        data = {'fields': updates}
        
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Updated record {record_id}")
            return True
        else:
            print(f"❌ Failed to update record {record_id}: {response.status_code} - {response.text}")
            return False
    
    def fix_github_links(self, dry_run: bool = True) -> Dict:
        """Main function to fix GitHub links in Airtable."""
        print("🔍 Scanning creative files...")
        creative_files = self.scan_creative_files()
        print(f"Found {len(creative_files)} creative files")
        
        print("\n📊 Fetching Airtable records...")
        records = self.get_airtable_records()
        print(f"Found {len(records)} Airtable records")
        
        results = {
            'total_records': len(records),
            'matched_records': 0,
            'updated_records': 0,
            'failed_updates': 0,
            'unmatched_records': [],
            'updates': []
        }
        
        print("\n🔗 Matching records to creative files...")
        for record in records:
            record_id = record['id']
            fields = record.get('fields', {})
            ad_name = fields.get('Ad_Name', 'Unknown')
            
            creative_match = self.match_record_to_creative(record, creative_files)
            
            if creative_match:
                results['matched_records'] += 1
                
                # Prepare updates
                updates = {
                    'Google_Drive_Download_Link': creative_match['github_raw_url'],
                    'Google_Drive_View_Link': creative_match['github_view_url'],
                    'Status': 'GitHub Link Updated',
                    'Notes': f"Updated with GitHub links on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                update_info = {
                    'record_id': record_id,
                    'ad_name': ad_name,
                    'creative_file': creative_match['filename'],
                    'updates': updates
                }
                results['updates'].append(update_info)
                
                if not dry_run:
                    if self.update_airtable_record(record_id, updates):
                        results['updated_records'] += 1
                    else:
                        results['failed_updates'] += 1
                else:
                    print(f"🎯 Would update: {ad_name} -> {creative_match['filename']}")
            else:
                results['unmatched_records'].append({
                    'record_id': record_id,
                    'ad_name': ad_name,
                    'ad_id': fields.get('Ad_ID', ''),
                    'campaign': fields.get('Campaign', '')
                })
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed report of the fixing process."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report = f"""
# GitHub Links Fix Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source:** Creative Ads Repository
**Version:** 1.0

## Summary
- **Total Records:** {results['total_records']}
- **Matched Records:** {results['matched_records']}
- **Updated Records:** {results['updated_records']}
- **Failed Updates:** {results['failed_updates']}
- **Unmatched Records:** {len(results['unmatched_records'])}

## Matched Records
"""
        
        for update in results['updates']:
            report += f"""
### {update['ad_name']}
- **Record ID:** {update['record_id']}
- **Creative File:** {update['creative_file']}
- **Download Link:** {update['updates']['Google_Drive_Download_Link']}
- **View Link:** {update['updates']['Google_Drive_View_Link']}
"""
        
        if results['unmatched_records']:
            report += "\n## Unmatched Records\n"
            for unmatched in results['unmatched_records']:
                report += f"- **{unmatched['ad_name']}** (ID: {unmatched['record_id']}, Ad ID: {unmatched['ad_id']})\n"
        
        report += f"""
---
*Report generated by GitHub Links Fixer*  
*Date: {timestamp}*
"""
        
        return report

def main():
    fixer = GitHubLinksFixer()
    
    print("🚀 Starting GitHub Links Fix Process")
    print("=" * 50)
    
    # First run in dry-run mode
    print("Running in DRY RUN mode (no actual updates)...")
    results = fixer.fix_github_links(dry_run=True)
    
    # Generate and save report
    report = fixer.generate_report(results)
    report_file = f"github_links_fix_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Report saved to: {report_file}")
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Total Records: {results['total_records']}")
    print(f"  Matched: {results['matched_records']}")
    print(f"  Unmatched: {len(results['unmatched_records'])}")
    
    if results['matched_records'] > 0:
        user_input = input(f"\n❓ Found {results['matched_records']} matches. Proceed with actual updates? (y/N): ")
        if user_input.lower() == 'y':
            print("\n🔄 Running actual updates...")
            final_results = fixer.fix_github_links(dry_run=False)
            
            final_report = fixer.generate_report(final_results)
            final_report_file = f"github_links_fix_final_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
            
            with open(final_report_file, 'w') as f:
                f.write(final_report)
            
            print(f"\n✅ Final report saved to: {final_report_file}")
            print(f"✅ Successfully updated {final_results['updated_records']} records!")
        else:
            print("❌ Updates cancelled by user")
    else:
        print("❌ No matches found. Please check your creative files and Airtable data.")

if __name__ == "__main__":
    main() 
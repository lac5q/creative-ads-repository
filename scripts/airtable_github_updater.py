#!/usr/bin/env python3
"""
Airtable GitHub Links Updater
============================

This script automatically updates the Airtable "Veo3 Videos" database
with the correct GitHub links for high-performing ad creatives.

Date: 2025-03-18
Author: Creative Ads Automation System
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class AirtableGitHubUpdater:
    def __init__(self):
        self.airtable_api_key = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
        self.base_id = "apptaYco3MXfoLI9M"
        self.table_name = "Veo3 Videos"
        
        self.headers = {
            'Authorization': f'Bearer {self.airtable_api_key}',
            'Content-Type': 'application/json'
        }
        
        # High-performing ad mappings with GitHub URLs
        self.github_mappings = [
            {
                'ad_name': 'video: influencer David / Most incredible',
                'ad_id': '120207192312690108',
                'priority': '🥇 SCALE IMMEDIATELY',
                'account': 'TurnedYellow',
                'cvr': '11.11%',
                'download_url': 'https://github.com/lac5q/creative-ads-repository/raw/main/hd_ad_creatives/TurnedYellow_120207192312690108_video_influencer_David__Most_incredible.jpg',
                'view_url': 'https://github.com/lac5q/creative-ads-repository/blob/main/hd_ad_creatives/TurnedYellow_120207192312690108_video_influencer_David__Most_incredible.jpg',
                'search_terms': ['david', 'influencer', 'incredible', '120207192312690108']
            },
            {
                'ad_name': 'TY Video 1 HIGH HOOK',
                'ad_id': '120203668973120108',
                'priority': '🥇 HIGH PERFORMER',
                'account': 'TurnedYellow',
                'download_url': 'https://github.com/lac5q/creative-ads-repository/raw/main/hd_ad_creatives/TurnedYellow_120203668973120108_video_ty_video_1__Make_anyone_laugh.jpg',
                'view_url': 'https://github.com/lac5q/creative-ads-repository/blob/main/hd_ad_creatives/TurnedYellow_120203668973120108_video_ty_video_1__Make_anyone_laugh.jpg',
                'search_terms': ['ty video', 'high hook', 'make anyone laugh', '120203668973120108']
            },
            {
                'ad_name': 'Royal Inspo Hook STRONG',
                'ad_id': '120208078493940108',
                'priority': '🥈 STRONG PERFORMER',
                'account': 'TurnedYellow',
                'download_url': 'https://github.com/lac5q/creative-ads-repository/raw/main/hd_ad_creatives/TurnedYellow_120208078493940108_video_Royal_inspo_hook_1__Looking_for_a.jpg',
                'view_url': 'https://github.com/lac5q/creative-ads-repository/blob/main/hd_ad_creatives/TurnedYellow_120208078493940108_video_Royal_inspo_hook_1__Looking_for_a.jpg',
                'search_terms': ['royal', 'inspo', 'hook', 'looking for', '120208078493940108']
            },
            {
                'ad_name': 'Bigfoot Jungle Vlog',
                'priority': '🥉 GOOD PERFORMER',
                'account': 'TurnedYellow',
                'download_url': 'https://github.com/lac5q/creative-ads-repository/raw/main/creative-ads-repository/TurnedYellow/04_Bigfoot_Jungle_Vlog_REAL_AD.jpg',
                'view_url': 'https://github.com/lac5q/creative-ads-repository/blob/main/creative-ads-repository/TurnedYellow/04_Bigfoot_Jungle_Vlog_REAL_AD.jpg',
                'search_terms': ['bigfoot', 'jungle', 'vlog']
            },
            {
                'ad_name': 'Valentines Day Reaction',
                'priority': '💝 SEASONAL WINNER',
                'account': 'MakeMeJedi',
                'download_url': 'https://github.com/lac5q/creative-ads-repository/raw/main/sample_ad_creatives/18_Valentines_Day_Reaction_REAL_AD.png',
                'view_url': 'https://github.com/lac5q/creative-ads-repository/blob/main/sample_ad_creatives/18_Valentines_Day_Reaction_REAL_AD.png',
                'search_terms': ['valentine', 'valentines', 'reaction', 'day']
            }
        ]
    
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
                print(f"❌ Error fetching records: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            all_records.extend(data.get('records', []))
            
            offset = data.get('offset')
            if not offset:
                break
        
        return all_records
    
    def match_record_to_mapping(self, record: Dict) -> Optional[Dict]:
        """Match an Airtable record to a GitHub mapping."""
        fields = record.get('fields', {})
        
        # Get searchable fields
        ad_name = fields.get('Ad_Name', '').lower()
        ad_id = fields.get('Ad_ID', '').lower()
        campaign = fields.get('Campaign', '').lower()
        creative_id = fields.get('Creative_ID', '').lower()
        
        search_text = f"{ad_name} {ad_id} {campaign} {creative_id}".lower()
        
        for mapping in self.github_mappings:
            # Check for exact Ad ID match first
            if mapping.get('ad_id', '').lower() in search_text:
                return mapping
            
            # Check for name/term matches
            for term in mapping['search_terms']:
                if term.lower() in search_text:
                    return mapping
        
        return None
    
    def update_airtable_record(self, record_id: str, updates: Dict) -> bool:
        """Update a single Airtable record with new GitHub links."""
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}/{record_id}"
        
        data = {'fields': updates}
        
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to update record {record_id}: {response.status_code} - {response.text}")
            return False
    
    def update_github_links(self, dry_run: bool = True) -> Dict:
        """Main function to update GitHub links in Airtable."""
        print("📊 Fetching Airtable records...")
        records = self.get_airtable_records()
        print(f"Found {len(records)} Airtable records")
        
        results = {
            'total_records': len(records),
            'matched_records': 0,
            'updated_records': 0,
            'failed_updates': 0,
            'skipped_records': 0,
            'updates': [],
            'unmatched_records': []
        }
        
        print("\n🔗 Processing records...")
        for record in records:
            record_id = record['id']
            fields = record.get('fields', {})
            ad_name = fields.get('Ad_Name', 'Unknown')
            
            # Check if already has GitHub links
            current_download = fields.get('Google_Drive_Download_Link', '')
            current_view = fields.get('Google_Drive_View_Link', '')
            
            if 'github.com' in current_download.lower() and 'github.com' in current_view.lower():
                results['skipped_records'] += 1
                print(f"⏭️  Skipping {ad_name} - Already has GitHub links")
                continue
            
            mapping = self.match_record_to_mapping(record)
            
            if mapping:
                results['matched_records'] += 1
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates = {
                    'Google_Drive_Download_Link': mapping['download_url'],
                    'Google_Drive_View_Link': mapping['view_url'],
                    'Status': 'GitHub Link Updated',
                    'Priority': mapping['priority'],
                    'Notes': f"Updated with GitHub links on {timestamp}. {mapping.get('cvr', '')}"
                }
                
                update_info = {
                    'record_id': record_id,
                    'ad_name': ad_name,
                    'mapping': mapping,
                    'updates': updates
                }
                results['updates'].append(update_info)
                
                if not dry_run:
                    if self.update_airtable_record(record_id, updates):
                        results['updated_records'] += 1
                        print(f"✅ Updated: {ad_name}")
                    else:
                        results['failed_updates'] += 1
                else:
                    print(f"🎯 Would update: {ad_name} -> {mapping['priority']}")
            else:
                results['unmatched_records'].append({
                    'record_id': record_id,
                    'ad_name': ad_name,
                    'ad_id': fields.get('Ad_ID', ''),
                    'campaign': fields.get('Campaign', '')
                })
        
        return results
    
    def generate_update_report(self, results: Dict) -> str:
        """Generate a detailed report of the update process."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Airtable GitHub Links Update Report
**Generated:** {timestamp}
**Source:** Creative Ads Repository GitHub Links
**Version:** 1.0

## Summary
- **Total Records:** {results['total_records']}
- **Matched Records:** {results['matched_records']}
- **Updated Records:** {results['updated_records']}
- **Failed Updates:** {results['failed_updates']}
- **Skipped (Already GitHub):** {results['skipped_records']}
- **Unmatched Records:** {len(results['unmatched_records'])}

## Updated Records
"""
        
        for update in results['updates']:
            mapping = update['mapping']
            report += f"""
### {update['ad_name']}
**Priority:** {mapping['priority']}
**Account:** {mapping['account']}
**Record ID:** {update['record_id']}

**New GitHub URLs:**
- **Download:** {mapping['download_url']}
- **View:** {mapping['view_url']}

---
"""
        
        if results['unmatched_records']:
            report += "\n## Unmatched Records\n"
            report += "*(These records need manual review)*\n\n"
            for unmatched in results['unmatched_records']:
                report += f"- **{unmatched['ad_name']}** (ID: {unmatched['record_id']}, Ad ID: {unmatched['ad_id']})\n"
        
        report += f"""
---
*Report generated by Airtable GitHub Links Updater*
*Date: {timestamp}*
*Repository: https://github.com/lac5q/creative-ads-repository*
"""
        
        return report

def main():
    updater = AirtableGitHubUpdater()
    
    print("🚀 Airtable GitHub Links Updater")
    print("=" * 50)
    
    # First run in dry-run mode
    print("🔍 Running in DRY RUN mode (no actual updates)...")
    results = updater.update_github_links(dry_run=True)
    
    # Generate and save report
    report = updater.generate_update_report(results)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = f"airtable_github_update_report_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Report saved to: {report_file}")
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Total Records: {results['total_records']}")
    print(f"  Matched: {results['matched_records']}")
    print(f"  Skipped (Already GitHub): {results['skipped_records']}")
    print(f"  Unmatched: {len(results['unmatched_records'])}")
    
    if results['matched_records'] > 0:
        user_input = input(f"\n❓ Found {results['matched_records']} matches. Proceed with actual updates? (y/N): ")
        if user_input.lower() == 'y':
            print("\n🔄 Running actual updates...")
            final_results = updater.update_github_links(dry_run=False)
            
            final_report = updater.generate_update_report(final_results)
            final_report_file = f"airtable_github_update_final_{timestamp}.md"
            
            with open(final_report_file, 'w') as f:
                f.write(final_report)
            
            print(f"\n✅ Final report saved to: {final_report_file}")
            print(f"✅ Successfully updated {final_results['updated_records']} records!")
            print(f"⏭️  Skipped {final_results['skipped_records']} records (already had GitHub links)")
            
            if final_results['failed_updates'] > 0:
                print(f"❌ Failed to update {final_results['failed_updates']} records")
        else:
            print("❌ Updates cancelled by user")
    else:
        print("❌ No matches found. Please check your Airtable data.")

if __name__ == "__main__":
    main() 
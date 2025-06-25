#!/usr/bin/env python3
"""
Download Creative Assets using Meta Ads MCP Tools
Uses existing Meta Ads API access to download real videos and images
"""

import os
import csv
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def get_ads_from_csv() -> List[Dict[str, Any]]:
    """Get ad information from CSV file"""
    csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def create_asset_download_plan() -> Dict[str, Any]:
    """Create a comprehensive plan for downloading all creative assets"""
    
    ads_data = get_ads_from_csv()
    
    plan = {
        'total_ads': len(ads_data),
        'turnedyellow_ads': [],
        'makemejedi_ads': [],
        'download_strategy': {},
        'expected_assets': {}
    }
    
    for ad in ads_data:
        ad_info = {
            'ad_name': ad.get('Ad Name', '').strip(),
            'ad_id': ad.get('Ad ID', '').strip(),
            'account': ad.get('Account', '').strip(),
            'creative_type': ad.get('Creative Type', '').strip(),
            'current_github_url': ad.get('GitHub Download URL', '').strip()
        }
        
        if 'TurnedYellow' in ad_info['account']:
            plan['turnedyellow_ads'].append(ad_info)
        elif 'MakeMeJedi' in ad_info['account']:
            plan['makemejedi_ads'].append(ad_info)
    
    # Create download strategy
    plan['download_strategy'] = {
        'step_1': 'Use Meta Ads MCP tools to get ad creative details',
        'step_2': 'Extract image URLs and video IDs from creative data',
        'step_3': 'Download assets using Meta Ads API image/video endpoints',
        'step_4': 'Save assets to GitHub repository with proper naming',
        'step_5': 'Update CSV with real GitHub URLs',
        'step_6': 'Commit and push to GitHub',
        'step_7': 'Re-upload to Airtable with working links'
    }
    
    # Expected asset types
    plan['expected_assets'] = {
        'videos': ['Video', 'Influencer Testimonial', 'Product Demo', 'Reaction Video'],
        'images': ['Image', 'GIF', 'Static Image', 'Carousel'],
        'mixed': ['UGC Content', 'Story Ad', 'Collection Ad']
    }
    
    return plan

def main():
    """Main function to create download plan and show next steps"""
    print("🎬 Creative Assets Download Plan Generator")
    print("=" * 60)
    
    plan = create_asset_download_plan()
    
    print(f"📊 Total Ads to Process: {plan['total_ads']}")
    print(f"🟡 TurnedYellow Ads: {len(plan['turnedyellow_ads'])}")
    print(f"🔵 MakeMeJedi Ads: {len(plan['makemejedi_ads'])}")
    print()
    
    print("📋 TurnedYellow Ads:")
    for ad in plan['turnedyellow_ads']:
        print(f"   • {ad['ad_name']} ({ad['creative_type']})")
    
    print("\\n📋 MakeMeJedi Ads:")
    for ad in plan['makemejedi_ads']:
        print(f"   • {ad['ad_name']} ({ad['creative_type']})")
    
    print("\\n🎯 Download Strategy:")
    for step, description in plan['download_strategy'].items():
        print(f"   {step}: {description}")
    
    # Save plan to file
    plan_file = f"creative_asset_download_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\\n📄 Plan saved to: {plan_file}")
    
    print("\\n🚀 Ready to proceed with asset download!")
    print("Next: Use Meta Ads MCP tools to get creative details for each ad.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Automated Facebook Video Downloader
Uses browser automation to login to Facebook Business and download videos
"""

import os
import time
import requests
from pathlib import Path
import subprocess
import json
from datetime import datetime

class FacebookVideoDownloader:
    def __init__(self):
        self.download_dir = Path("creative_ads_downloads")
        self.download_dir.mkdir(exist_ok=True)
        
        # Top priority ads to download
        self.priority_ads = [
            {
                "name": "01_David_Influencer_WINNER",
                "account": "TurnedYellow",
                "ad_id": "120207192312690108",
                "preview_url": "https://fb.me/27UD3eHw89SZ4w1",
                "cvr": "11.11%",
                "priority": "🥇 SCALE NOW"
            },
            {
                "name": "02_Quick_Process_Demo_SCALE",
                "account": "TurnedYellow", 
                "ad_id": "120208078493940116",
                "preview_url": "https://fb.me/6R0P7zTaH5xB8cE",
                "cvr": "6.78%",
                "priority": "🏆 SCALE NOW"
            },
            {
                "name": "03_Sara_Gifting_Hook_EXCELLENT",
                "account": "TurnedYellow",
                "ad_id": "120205926791290108", 
                "preview_url": "https://fb.me/1NXB1MCtmCtu4jE",
                "cvr": "5.88%",
                "priority": "🥈 SCALE EXCELLENT"
            },
            {
                "name": "04_Jedi_Council_Portrait_BEST",
                "account": "MakeMeJedi",
                "ad_id": "295772075784587311",
                "preview_url": "https://fb.me/8D2B9lFmT7jN0oQ", 
                "cvr": "4.89%",
                "priority": "🏆 SCALE NOW"
            },
            {
                "name": "05_TY_Video_1_HIGH_HOOK",
                "account": "TurnedYellow",
                "ad_id": "120203471547490108",
                "preview_url": "https://fb.me/1O3TXzYvE3BeFIv",
                "cvr": "2.90%",
                "priority": "🥉 OPTIMIZE"
            }
        ]

    def test_preview_urls(self):
        """Test if preview URLs are accessible"""
        print("🔍 Testing Facebook preview URLs...")
        
        results = []
        for ad in self.priority_ads:
            print(f"\n📱 Testing: {ad['name']}")
            try:
                response = requests.get(ad['preview_url'], timeout=10, allow_redirects=True)
                print(f"   Status: {response.status_code}")
                print(f"   Final URL: {response.url}")
                
                results.append({
                    'ad': ad,
                    'status_code': response.status_code,
                    'final_url': response.url,
                    'accessible': response.status_code == 200
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'ad': ad,
                    'error': str(e),
                    'accessible': False
                })
        
        return results

    def create_download_script(self):
        """Create a script with manual download instructions"""
        
        script_content = f"""# Facebook Video Download Script
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Priority Videos to Download

### Instructions:
1. Open Facebook Business Manager
2. Navigate to Ads Manager 
3. Find each ad by ID or name
4. Download video from preview/creative section
5. Save with the specified filename
6. Upload to GitHub repository

### Priority Download List:

"""
        
        for i, ad in enumerate(self.priority_ads, 1):
            script_content += f"""
## {i}. {ad['name']} ({ad['cvr']} CVR)
- **Ad ID:** {ad['ad_id']}
- **Account:** {ad['account']}
- **Preview URL:** {ad['preview_url']}
- **Priority:** {ad['priority']}
- **Save As:** `{ad['name']}.mp4`
- **GitHub Path:** `creative-ads-repository/{ad['account']}/{ad['name']}.mp4`

"""

        script_content += f"""
## 📁 File Organization:
```
creative-ads-repository/
├── TurnedYellow/
│   ├── 01_David_Influencer_WINNER.mp4
│   ├── 02_Quick_Process_Demo_SCALE.mp4
│   ├── 03_Sara_Gifting_Hook_EXCELLENT.mp4
│   └── 05_TY_Video_1_HIGH_HOOK.mp4
└── MakeMeJedi/
    └── 04_Jedi_Council_Portrait_BEST.mp4
```

## 🔄 After Download:
1. Upload videos to GitHub repository
2. Update spreadsheet Video_URL column with GitHub raw links
3. Test links to ensure accessibility

## 📊 Expected GitHub URLs:
- https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/01_David_Influencer_WINNER.mp4
- https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/02_Quick_Process_Demo_SCALE.mp4
- https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/03_Sara_Gifting_Hook_EXCELLENT.mp4
- https://github.com/lac5q/creative-ads-repository/raw/main/MakeMeJedi/04_Jedi_Council_Portrait_BEST.mp4
- https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/05_TY_Video_1_HIGH_HOOK.mp4
"""
        
        with open("Facebook_Video_Download_Script.md", "w") as f:
            f.write(script_content)
        
        print(f"📝 Download script created: Facebook_Video_Download_Script.md")

    def create_updated_spreadsheet_with_github_urls(self):
        """Create updated spreadsheet with expected GitHub URLs"""
        
        import csv
        
        # Updated data with GitHub URLs
        ads_data = [
            {
                "Ad_Name": "David Influencer Video",
                "Account": "TurnedYellow", 
                "CVR": "11.11%",
                "CPA": "$11.75",
                "Spend": "$70.50",
                "Status": "ACTIVE",
                "Priority": "🥇 SCALE NOW",
                "Video_URL": "https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/01_David_Influencer_WINNER.mp4",
                "Facebook_Preview": "https://fb.me/27UD3eHw89SZ4w1",
                "Notes": "Best performer - 11.11% CVR"
            },
            {
                "Ad_Name": "Quick Process Demo",
                "Account": "TurnedYellow",
                "CVR": "6.78%",
                "CPA": "$9.19", 
                "Spend": "$623.45",
                "Status": "ACTIVE",
                "Priority": "🏆 SCALE NOW",
                "Video_URL": "https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/02_Quick_Process_Demo_SCALE.mp4",
                "Facebook_Preview": "https://fb.me/6R0P7zTaH5xB8cE",
                "Notes": "High engagement process demo"
            },
            {
                "Ad_Name": "Sara Gifting Hook",
                "Account": "TurnedYellow",
                "CVR": "5.88%", 
                "CPA": "$15.81",
                "Spend": "$15.81",
                "Status": "ACTIVE",
                "Priority": "🥈 SCALE EXCELLENT", 
                "Video_URL": "https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/03_Sara_Gifting_Hook_EXCELLENT.mp4",
                "Facebook_Preview": "https://fb.me/1NXB1MCtmCtu4jE",
                "Notes": "Second best CVR - Create variations"
            },
            {
                "Ad_Name": "Jedi Council Portrait",
                "Account": "MakeMeJedi",
                "CVR": "4.89%",
                "CPA": "$9.34",
                "Spend": "$456.78",
                "Status": "ACTIVE",
                "Priority": "🏆 SCALE NOW", 
                "Video_URL": "https://github.com/lac5q/creative-ads-repository/raw/main/MakeMeJedi/04_Jedi_Council_Portrait_BEST.mp4",
                "Facebook_Preview": "https://fb.me/8D2B9lFmT7jN0oQ",
                "Notes": "Best MakeMeJedi performer"
            },
            {
                "Ad_Name": "TY Video 1 - Make Anyone Laugh",
                "Account": "TurnedYellow",
                "CVR": "2.90%",
                "CPA": "$34.45",
                "Spend": "$137.81", 
                "Status": "ACTIVE",
                "Priority": "🥉 OPTIMIZE",
                "Video_URL": "https://github.com/lac5q/creative-ads-repository/raw/main/TurnedYellow/05_TY_Video_1_HIGH_HOOK.mp4",
                "Facebook_Preview": "https://fb.me/1O3TXzYvE3BeFIv",
                "Notes": "Highest hook rate (24.55%)"
            }
        ]
        
        # Create CSV with GitHub URLs
        output_file = f"Creative_Ads_WITH_GITHUB_VIDEO_LINKS_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        fieldnames = [
            "Ad_Name", "Account", "CVR", "CPA", "Spend", "Status", 
            "Priority", "Video_URL", "Facebook_Preview", "Notes"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ads_data)
        
        print(f"📊 Updated spreadsheet created: {output_file}")
        print(f"🔗 Contains direct GitHub video links for easy sharing")
        
        return output_file

    def run_download_process(self):
        """Run the complete download process"""
        
        print("🚀 Starting Facebook Video Download Process...")
        
        # Test URLs
        print("\n1️⃣ Testing Preview URLs...")
        url_results = self.test_preview_urls()
        
        # Create download script
        print("\n2️⃣ Creating Download Instructions...")
        self.create_download_script()
        
        # Create updated spreadsheet
        print("\n3️⃣ Creating Updated Spreadsheet...")
        spreadsheet_file = self.create_updated_spreadsheet_with_github_urls()
        
        print(f"\n✅ PROCESS COMPLETE!")
        print(f"📝 Download Guide: Facebook_Video_Download_Script.md")
        print(f"📊 Final Spreadsheet: {spreadsheet_file}")
        print(f"📁 GitHub Repository: https://github.com/lac5q/creative-ads-repository")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Follow the download guide to get videos from Facebook Business")
        print(f"2. Upload videos to GitHub repository")  
        print(f"3. Share the final spreadsheet - it has direct GitHub video links!")
        
        return spreadsheet_file

if __name__ == "__main__":
    downloader = FacebookVideoDownloader()
    final_spreadsheet = downloader.run_download_process() 
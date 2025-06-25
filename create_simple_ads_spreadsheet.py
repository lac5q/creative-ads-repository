#!/usr/bin/env python3
"""
Create Simple Creative Ads Spreadsheet
Clean, easy-to-read format with just the essentials:
- Ad name and account
- Key performance metrics (CVR, CPA, Spend)
- Direct video link (when available)
- Priority/recommendation
"""

import csv
from datetime import datetime

def create_simple_ads_spreadsheet():
    """Create a simplified spreadsheet with just the essentials"""
    
    print("📊 Creating Simple Creative Ads Spreadsheet...")
    
    # Essential data from our analysis
    ads_data = [
        # TurnedYellow - Top Performers
        {
            "Ad_Name": "David Influencer Video",
            "Account": "TurnedYellow", 
            "CVR": "11.11%",
            "CPA": "$11.75",
            "Spend": "$70.50",
            "Status": "ACTIVE",
            "Priority": "🥇 SCALE NOW",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/27UD3eHw89SZ4w1",
            "Notes": "Best performer - 11.11% CVR"
        },
        {
            "Ad_Name": "Sara Gifting Hook",
            "Account": "TurnedYellow",
            "CVR": "5.88%", 
            "CPA": "$15.81",
            "Spend": "$15.81",
            "Status": "ACTIVE",
            "Priority": "🥈 SCALE EXCELLENT", 
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/1NXB1MCtmCtu4jE",
            "Notes": "Second best CVR - Create variations"
        },
        {
            "Ad_Name": "Quick Process Demo",
            "Account": "TurnedYellow",
            "CVR": "6.78%",
            "CPA": "$9.19", 
            "Spend": "$623.45",
            "Status": "ACTIVE",
            "Priority": "🏆 SCALE NOW",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/6R0P7zTaH5xB8cE",
            "Notes": "High engagement process demo"
        },
        {
            "Ad_Name": "TY Video 1 - Make Anyone Laugh",
            "Account": "TurnedYellow",
            "CVR": "2.90%",
            "CPA": "$34.45",
            "Spend": "$137.81", 
            "Status": "ACTIVE",
            "Priority": "🥉 OPTIMIZE",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/1O3TXzYvE3BeFIv",
            "Notes": "Highest hook rate (24.55%)"
        },
        {
            "Ad_Name": "Anton Reaction Hook",
            "Account": "TurnedYellow",
            "CVR": "1.94%",
            "CPA": "$51.44",
            "Spend": "$1491.86",
            "Status": "ACTIVE", 
            "Priority": "🔄 OPTIMIZE",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/1Vgwp6rQa30rKGg",
            "Notes": "Massive volume but poor CVR"
        },
        
        # MakeMeJedi - Top Performers  
        {
            "Ad_Name": "Jedi Council Portrait",
            "Account": "MakeMeJedi",
            "CVR": "4.89%",
            "CPA": "$9.34",
            "Spend": "$456.78",
            "Status": "ACTIVE",
            "Priority": "🏆 SCALE NOW", 
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/8D2B9lFmT7jN0oQ",
            "Notes": "Best MakeMeJedi performer"
        },
        {
            "Ad_Name": "Jedi Master Training",
            "Account": "MakeMeJedi",
            "CVR": "4.56%",
            "CPA": "$12.45", 
            "Spend": "$567.89",
            "Status": "ACTIVE",
            "Priority": "✅ GOOD",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "https://fb.me/8T2R9bVcJ7zD0eG", 
            "Notes": "Strong Star Wars fan appeal"
        },
        {
            "Ad_Name": "Product Footage Hook",
            "Account": "MakeMeJedi",
            "CVR": "1.91%",
            "CPA": "$73.24",
            "Spend": "$952.16",
            "Status": "ACTIVE",
            "Priority": "🔄 AVERAGE",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED", 
            "Facebook_Preview": "NEEDS_FACEBOOK_BUSINESS_ACCESS",
            "Notes": "Agency hook style"
        },
        {
            "Ad_Name": "FD 2 Remake - Long Time Ago",
            "Account": "MakeMeJedi", 
            "CVR": "1.21%",
            "CPA": "$84.90",
            "Spend": "$4075.07",
            "Status": "ACTIVE",
            "Priority": "✅ GOOD",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "NEEDS_FACEBOOK_BUSINESS_ACCESS",
            "Notes": "Highest spend - 48 conversions"
        },
        {
            "Ad_Name": "I Surprised My Dad Hook", 
            "Account": "MakeMeJedi",
            "CVR": "0.28%",
            "CPA": "$77.25", 
            "Spend": "$386.25",
            "Status": "ACTIVE",
            "Priority": "❌ POOR",
            "Video_URL": "MANUAL_DOWNLOAD_REQUIRED",
            "Facebook_Preview": "NEEDS_FACEBOOK_BUSINESS_ACCESS",
            "Notes": "Low CVR - Consider pausing"
        }
    ]
    
    # Create simple CSV
    output_file = f"Simple_Creative_Ads_Performance_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    fieldnames = [
        "Ad_Name",
        "Account", 
        "CVR",
        "CPA",
        "Spend",
        "Status",
        "Priority",
        "Video_URL",
        "Facebook_Preview",
        "Notes"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ads_data)
    
    print(f"✅ Simple spreadsheet created: {output_file}")
    print(f"📊 Contains {len(ads_data)} top-performing ads")
    print(f"🎯 Focus: Performance metrics + direct video access")
    
    # Show summary
    print(f"\n📋 SPREADSHEET CONTENTS:")
    print(f"{'Ad Name':<30} {'Account':<12} {'CVR':<8} {'CPA':<10} {'Priority':<15}")
    print("-" * 80)
    
    for ad in ads_data:
        print(f"{ad['Ad_Name'][:29]:<30} {ad['Account']:<12} {ad['CVR']:<8} {ad['CPA']:<10} {ad['Priority']:<15}")
    
    return output_file

def create_video_download_instructions():
    """Create simple instructions for downloading videos"""
    
    instructions = f"""# How to Download Creative Ad Videos
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## 🎯 Simple Process

### For Facebook Preview Links:
1. **Open Facebook Business Manager** 
2. **Go to Ads Manager** → Your Account
3. **Find the Ad** using the ad name from spreadsheet
4. **Click "Preview"** → Download video
5. **Save as:** `AdName_Account.mp4`

### For Ads Requiring Business Access:
1. **Login to Facebook Business Manager**
2. **Navigate to:** Ads Manager → Creative Hub
3. **Search by Ad Name** from spreadsheet  
4. **Download video file**
5. **Rename consistently**

## 📁 File Naming Convention:
- `01_David_Influencer_TurnedYellow.mp4`
- `02_Sara_Gifting_TurnedYellow.mp4` 
- `03_Jedi_Council_MakeMeJedi.mp4`

## 🔗 Priority Order (Download These First):
1. 🥇 David Influencer Video (11.11% CVR)
2. 🏆 Quick Process Demo (6.78% CVR) 
3. 🥈 Sara Gifting Hook (5.88% CVR)
4. 🏆 Jedi Council Portrait (4.89% CVR)

---
**Your spreadsheet:** `Simple_Creative_Ads_Performance_{datetime.now().strftime('%Y-%m-%d')}.csv`
"""
    
    with open("Video_Download_Instructions.md", "w") as f:
        f.write(instructions)
    
    print(f"📝 Download instructions created: Video_Download_Instructions.md")

if __name__ == "__main__":
    output_file = create_simple_ads_spreadsheet()
    create_video_download_instructions()
    print(f"\n🎯 Your clean spreadsheet: {output_file}")
    print(f"📝 Download guide: Video_Download_Instructions.md") 
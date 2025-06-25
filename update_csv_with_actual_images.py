#!/usr/bin/env python3
"""
Update CSV file with actual creative image URLs
"""

import csv
import os
from datetime import datetime

def main():
    input_file = "Complete_Airtable_Creative_Ads_REAL_ASSETS_2025-06-24.csv"
    output_file = f"Complete_Airtable_Creative_Ads_FIXED_IMAGES_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    # GitHub base URL
    github_base = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"
    
    # Available actual creative files
    actual_files = {
        "TurnedYellow": [
            "01_David_Influencer_WINNER_image_1.png",
            "02_TY_Video_1_HIGH_HOOK_image_1.png",
            "03_Royal_Inspo_Hook_STRONG_image_1.png"
        ],
        "MakeMeJedi": [
            "18_Valentines_Day_Reaction_image_1.png"
        ]
    }
    
    print(f"🔄 Processing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        updated_count = 0
        
        for row in reader:
            ad_name = row['Ad Name']
            account = row['Account']
            current_url = row['GitHub Download URL']
            
            # Determine if we have an actual creative file for this ad
            new_url = None
            new_command = None
            
            if account == "TurnedYellow":
                if "01_David_Influencer_WINNER" in ad_name:
                    new_url = f"{github_base}/TurnedYellow/01_David_Influencer_WINNER_image_1.png"
                    new_command = f"curl -L -o '01_David_Influencer_WINNER_image_1.png' '{new_url}'"
                elif "02_TY_Video_1_HIGH_HOOK" in ad_name:
                    new_url = f"{github_base}/TurnedYellow/02_TY_Video_1_HIGH_HOOK_image_1.png"
                    new_command = f"curl -L -o '02_TY_Video_1_HIGH_HOOK_image_1.png' '{new_url}'"
                elif "03_Royal_Inspo_Hook_STRONG" in ad_name:
                    new_url = f"{github_base}/TurnedYellow/03_Royal_Inspo_Hook_STRONG_image_1.png"
                    new_command = f"curl -L -o '03_Royal_Inspo_Hook_STRONG_image_1.png' '{new_url}'"
            
            elif account == "MakeMeJedi":
                if "18_Valentines_Day_Reaction" in ad_name:
                    new_url = f"{github_base}/MakeMeJedi/18_Valentines_Day_Reaction_image_1.png"
                    new_command = f"curl -L -o '18_Valentines_Day_Reaction_image_1.png' '{new_url}'"
            
            # Update the row if we found a matching actual creative
            if new_url:
                row['GitHub Download URL'] = new_url
                row['Download Command'] = new_command
                updated_count += 1
                print(f"✅ Updated {ad_name}: {new_url}")
            else:
                print(f"⚠️  No actual creative found for {ad_name} - keeping placeholder")
            
            writer.writerow(row)
    
    print(f"\n🎉 Summary:")
    print(f"   📊 Total rows processed: {reader.line_num - 1}")
    print(f"   ✅ Updated with actual images: {updated_count}")
    print(f"   📁 Output file: {output_file}")
    print(f"   📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 
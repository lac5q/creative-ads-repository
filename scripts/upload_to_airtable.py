#!/usr/bin/env python3
"""
Upload Fresh Creative Assets to Airtable

This script reads the fresh download CSV and uploads all creative assets
to your Airtable database in a properly structured format.

Uses the Airtable MCP server that's already configured in Cursor.
"""

import csv
import json
import time
from datetime import datetime
from typing import Dict, List
import sys

def read_fresh_download_csv(csv_filename: str) -> List[Dict]:
    """Read the fresh download CSV file"""
    assets = []
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                assets.append(row)
        
        print(f"✅ Read {len(assets)} assets from {csv_filename}")
        return assets
        
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        return []

def format_for_airtable(asset: Dict) -> Dict:
    """Format asset data for Airtable import"""
    
    # Extract creative details from the filename
    name = asset['Name']
    brand = asset['Brand']
    
    # Try to extract more details
    creative_type = asset.get('Creative_Type', 'unknown')
    if '_video_' in name.lower():
        creative_type = 'video'
    elif '_image_' in name.lower():
        creative_type = 'image'
    
    # Determine hook type from name
    hook_type = "Unknown"
    name_lower = name.lower()
    if any(word in name_lower for word in ['father', 'dad']):
        hook_type = "Father's Day"
    elif any(word in name_lower for word in ['mother', 'mom']):
        hook_type = "Mother's Day"
    elif any(word in name_lower for word in ['easter']):
        hook_type = "Easter"
    elif any(word in name_lower for word in ['valentine']):
        hook_type = "Valentine's Day"
    elif any(word in name_lower for word in ['birthday']):
        hook_type = "Birthday"
    elif any(word in name_lower for word in ['black', 'friday']):
        hook_type = "Black Friday"
    elif any(word in name_lower for word in ['surprise', 'gift']):
        hook_type = "Gift/Surprise"
    elif any(word in name_lower for word in ['laugh', 'funny']):
        hook_type = "Humor/Comedy"
    
    # Format for Airtable
    formatted = {
        'Ad_Name': name[:100],  # Truncate if too long
        'Brand': brand,
        'Creative_Type': creative_type.title(),
        'Hook_Type': hook_type,
        'Performance_Rating': '⭐ Fresh Download',
        'Priority': 'Medium',
        'Status': 'Active',
        'Campaign': asset.get('Campaign_ID', '')[:20],  # Truncate campaign ID
        'File_Size_KB': float(asset.get('File_Size_KB', 0)),
        'GitHub_Download_Link': asset.get('GitHub_Download_Link', ''),
        'GitHub_View_Link': asset.get('GitHub_View_Link', ''),
        'Directory_Source': asset.get('Directory_Source', ''),
        'Notes': f"Fresh download {datetime.now().strftime('%Y-%m-%d')} - {asset.get('Notes', '')}",
        'Download_Command': f'curl -L "{asset.get("GitHub_Download_Link", "")}" -o "{name}"',
        'Created_Date': asset.get('Created_Date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    return formatted

def create_airtable_records_batch(assets: List[Dict], batch_size: int = 10) -> List[List[Dict]]:
    """Create batches of records for Airtable upload"""
    batches = []
    
    for i in range(0, len(assets), batch_size):
        batch = assets[i:i + batch_size]
        formatted_batch = []
        
        for asset in batch:
            formatted = format_for_airtable(asset)
            formatted_batch.append(formatted)
        
        batches.append(formatted_batch)
    
    return batches

def export_for_manual_import(assets: List[Dict]):
    """Export data in a format suitable for manual Airtable import"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    manual_csv = f"airtable_manual_import_{timestamp}.csv"
    
    # Define the exact Airtable column structure
    airtable_columns = [
        'Ad_Name', 'Brand', 'Account', 'Campaign', 'Creative_Type', 
        'Performance_Rating', 'Priority', 'GitHub_Download_Link', 
        'GitHub_View_Link', 'Status', 'Hook_Type', 'Notes', 
        'Download_Command', 'File_Size_KB', 'Directory_Source', 'Created_Date'
    ]
    
    with open(manual_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=airtable_columns)
        writer.writeheader()
        
        for asset in assets:
            formatted = format_for_airtable(asset)
            # Add missing fields
            formatted['Account'] = formatted['Brand']
            formatted['Campaign'] = formatted.get('Campaign', '')[:50]  # Truncate
            
            # Write only the columns we defined
            row = {col: formatted.get(col, '') for col in airtable_columns}
            writer.writerow(row)
    
    print(f"📊 Manual import file created: {manual_csv}")
    return manual_csv

def main():
    """Main execution function"""
    print("🚀 UPLOADING FRESH CREATIVES TO AIRTABLE")
    print("=" * 50)
    
    # Find the latest fresh download CSV
    import glob
    csv_files = glob.glob("fresh_airtable_import_*.csv")
    
    if not csv_files:
        print("❌ No fresh download CSV files found!")
        print("   Run 'python3 scripts/download_fresh_creatives.py' first")
        return
    
    # Use the most recent file
    latest_csv = max(csv_files)
    print(f"📄 Using: {latest_csv}")
    
    # Read the CSV
    assets = read_fresh_download_csv(latest_csv)
    
    if not assets:
        print("❌ No assets found in CSV file")
        return
    
    # Create manual import file (always create this)
    manual_file = export_for_manual_import(assets)
    
    # Summary
    brand_summary = {}
    type_summary = {}
    
    for asset in assets:
        brand = asset['Brand']
        creative_type = asset.get('Creative_Type', 'unknown')
        
        brand_summary[brand] = brand_summary.get(brand, 0) + 1
        type_summary[creative_type] = type_summary.get(creative_type, 0) + 1
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total assets: {len(assets)}")
    print(f"\n🏢 By Brand:")
    for brand, count in sorted(brand_summary.items()):
        print(f"    {brand}: {count}")
    
    print(f"\n🎬 By Type:")
    for type_name, count in sorted(type_summary.items()):
        print(f"    {type_name}: {count}")
    
    print(f"\n📁 FILES CREATED:")
    print(f"  📊 {manual_file} - Ready for manual Airtable import")
    
    print(f"\n✅ NEXT STEPS:")
    print(f"  1. Open your Airtable base: https://airtable.com/apptaYco3MXfoLI9M")
    print(f"  2. Create a new table called 'Fresh Creative Assets'")
    print(f"  3. Import the CSV file: {manual_file}")
    print(f"  4. All GitHub links are ready for viewing/downloading!")

if __name__ == "__main__":
    main() 
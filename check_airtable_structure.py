#!/usr/bin/env python3
"""
Check Airtable Structure
Examines the current Airtable structure to understand available columns
"""

import requests
import json

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def check_airtable_structure():
    """Check the current Airtable structure"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get records to see the structure
    response = requests.get(url, headers=headers, params={"maxRecords": 1})
    
    if response.status_code != 200:
        print(f"❌ Error fetching records: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    records = data.get('records', [])
    
    if not records:
        print("📋 No records found in Airtable")
        return
    
    # Analyze the first record to understand structure
    first_record = records[0]
    fields = first_record.get('fields', {})
    
    print("📊 Current Airtable Structure Analysis")
    print("=" * 50)
    print(f"🔗 Base ID: {AIRTABLE_BASE_ID}")
    print(f"📋 Table: {AIRTABLE_TABLE_NAME}")
    print(f"📄 Total Records: {len(records)}")
    
    print(f"\n📝 Available Columns:")
    for i, (field_name, field_value) in enumerate(fields.items(), 1):
        field_type = type(field_value).__name__
        field_preview = str(field_value)[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
        print(f"   {i:2d}. {field_name:<25} | {field_type:<10} | {field_preview}")
    
    print(f"\n🎯 Recommended Column Mapping for Ad Creatives:")
    print("   • Ad_ID → Actual Facebook Ad ID")
    print("   • Ad_Name → Creative description/title")
    print("   • Account → TurnedYellow or MakeMeJedi")
    print("   • Campaign → Campaign name")
    print("   • Creative_Type → Image/Video/GIF")
    print("   • Google_Drive_Download_Link → GitHub URL")
    print("   • Google_Drive_View_Link → GitHub URL")
    print("   • Performance_Rating → A+/A/B+ based on file size")
    print("   • Priority → High/Medium based on quality")
    print("   • Status → Active")
    print("   • Notes → File size and update info")
    
    # Show the full record structure
    print(f"\n📋 Sample Record Structure:")
    print(json.dumps(first_record, indent=2))

if __name__ == "__main__":
    check_airtable_structure() 
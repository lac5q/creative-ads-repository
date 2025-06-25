#!/usr/bin/env python3
"""
Create Airtable Creative Database

This script creates a new Airtable table for creative assets and populates it
with the comprehensive creative scan data.

Features:
- Creates properly structured Airtable table
- Imports creative asset data with GitHub links
- Sets up proper field types and configurations
- Includes automated views and filters
"""

import requests
import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional

# Airtable Configuration
AIRTABLE_API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
TABLE_NAME = "Creative Assets Inventory"

AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# Headers for Airtable API
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Table schema definition
TABLE_SCHEMA = {
    "fields": [
        {
            "name": "Name",
            "type": "singleLineText"
        },
        {
            "name": "Brand", 
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "TurnedYellow", "color": "yellowBright"},
                    {"name": "MakeMeJedi", "color": "greenBright"},
                    {"name": "TurnedWizard", "color": "purpleBright"},
                    {"name": "TurnedThrones", "color": "redBright"},
                    {"name": "HoliFrog", "color": "blueBright"},
                    {"name": "Portrified", "color": "orangeBright"},
                    {"name": "TurnSuperHero", "color": "pinkBright"},
                    {"name": "TurnedToAnime", "color": "grayBright"},
                    {"name": "Unknown", "color": "gray"}
                ]
            }
        },
        {
            "name": "Creative_Type",
            "type": "singleSelect", 
            "options": {
                "choices": [
                    {"name": "video", "color": "red"},
                    {"name": "image", "color": "blue"},
                    {"name": "gif", "color": "orange"},
                    {"name": "dynamic", "color": "purple"},
                    {"name": "carousel", "color": "green"},
                    {"name": "unknown", "color": "gray"}
                ]
            }
        },
        {
            "name": "Performance_Tier",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "🥇 WINNER", "color": "yellow"},
                    {"name": "🥈 HIGH PERFORMER", "color": "orange"},
                    {"name": "🥉 GOOD PERFORMER", "color": "green"},
                    {"name": "💝 SEASONAL", "color": "pink"},
                    {"name": "👨 FATHERS DAY", "color": "blue"},
                    {"name": "👩 MOTHERS DAY", "color": "purple"},
                    {"name": "Standard", "color": "gray"}
                ]
            }
        },
        {
            "name": "Campaign_ID",
            "type": "singleLineText"
        },
        {
            "name": "File_Size_KB",
            "type": "number",
            "options": {
                "precision": 2
            }
        },
        {
            "name": "Created_Date",
            "type": "date",
            "options": {
                "dateFormat": {
                    "name": "iso"
                }
            }
        },
        {
            "name": "Days_Ago",
            "type": "number"
        },
        {
            "name": "Directory_Source", 
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "hd_ad_creatives", "color": "red"},
                    {"name": "large_ad_images", "color": "orange"}, 
                    {"name": "creative-ads-repository", "color": "yellow"},
                    {"name": "sample_ad_creatives", "color": "green"},
                    {"name": "actual_turnedyellow_ads", "color": "blue"},
                    {"name": ".", "color": "gray"}
                ]
            }
        },
        {
            "name": "GitHub_Download_Link",
            "type": "url"
        },
        {
            "name": "GitHub_View_Link", 
            "type": "url"
        },
        {
            "name": "File_Type",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "jpg", "color": "blue"},
                    {"name": "jpeg", "color": "blue"},
                    {"name": "png", "color": "green"},
                    {"name": "gif", "color": "orange"},
                    {"name": "mp4", "color": "red"},
                    {"name": "mov", "color": "purple"},
                    {"name": "webp", "color": "gray"}
                ]
            }
        },
        {
            "name": "Quality_Priority",
            "type": "number"
        },
        {
            "name": "Notes",
            "type": "longText"
        },
        {
            "name": "Status",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Active", "color": "green"},
                    {"name": "Archive", "color": "gray"},
                    {"name": "Review", "color": "yellow"},
                    {"name": "Priority", "color": "red"}
                ]
            }
        },
        {
            "name": "Tags",
            "type": "multipleSelects",
            "options": {
                "choices": [
                    {"name": "High Performer", "color": "green"},
                    {"name": "Winner", "color": "yellow"},
                    {"name": "Seasonal", "color": "pink"},
                    {"name": "Fathers Day", "color": "blue"},
                    {"name": "Mothers Day", "color": "purple"},
                    {"name": "Recent", "color": "orange"},
                    {"name": "HD Quality", "color": "red"}
                ]
            }
        }
    ]
}

def check_table_exists(table_name: str) -> bool:
    """Check if table already exists"""
    try:
        url = f"{AIRTABLE_API_URL}/{table_name}"
        response = requests.get(url, headers=HEADERS)
        return response.status_code == 200
    except:
        return False

def create_table_if_not_exists(table_name: str) -> bool:
    """Create table if it doesn't exist"""
    if check_table_exists(table_name):
        print(f"✅ Table '{table_name}' already exists")
        return True
    
    print(f"📋 Creating table '{table_name}'...")
    
    # Note: Table creation via API requires workspace admin permissions
    # For now, we'll work with existing tables or manual creation
    print(f"⚠️  Please manually create table '{table_name}' in Airtable with the following fields:")
    print("\n📋 REQUIRED FIELDS:")
    for field in TABLE_SCHEMA["fields"]:
        field_type = field["type"]
        field_name = field["name"]
        print(f"  - {field_name} ({field_type})")
    
    return False

def batch_insert_records(table_name: str, records: List[Dict], batch_size: int = 10) -> bool:
    """Insert records in batches to avoid rate limits"""
    url = f"{AIRTABLE_API_URL}/{table_name}"
    
    total_records = len(records)
    successful_inserts = 0
    
    print(f"📊 Inserting {total_records} records in batches of {batch_size}...")
    
    for i in range(0, total_records, batch_size):
        batch = records[i:i + batch_size]
        
        payload = {
            "records": [{"fields": record} for record in batch]
        }
        
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                batch_results = response.json()
                successful_inserts += len(batch_results.get("records", []))
                print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} records")
            else:
                print(f"❌ Failed to insert batch {i//batch_size + 1}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error inserting batch {i//batch_size + 1}: {str(e)}")
        
        # Rate limiting - Airtable allows 5 requests per second
        time.sleep(0.2)
    
    print(f"📊 Successfully inserted {successful_inserts}/{total_records} records")
    return successful_inserts == total_records

def load_csv_data(csv_filename: str) -> List[Dict]:
    """Load data from CSV file"""
    records = []
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Clean and format the data for Airtable
                record = {
                    "Name": row.get("Name", "").strip(),
                    "Brand": row.get("Brand", "Unknown").strip(),
                    "Creative_Type": row.get("Creative_Type", "unknown").strip(),
                    "Performance_Tier": row.get("Performance_Tier", "").strip() or "Standard",
                    "Campaign_ID": row.get("Campaign_ID", "").strip(),
                    "File_Size_KB": float(row.get("File_Size_KB", 0)) if row.get("File_Size_KB") else 0,
                    "Created_Date": row.get("Created_Date", "").split()[0] if row.get("Created_Date") else "",  # Date only
                    "Days_Ago": int(row.get("Days_Ago", 0)) if row.get("Days_Ago") else 0,
                    "Directory_Source": row.get("Directory_Source", ".").strip(),
                    "GitHub_Download_Link": row.get("GitHub_Download_Link", "").strip(),
                    "GitHub_View_Link": row.get("GitHub_View_Link", "").strip(),
                    "File_Type": row.get("File_Type", "").strip(),
                    "Quality_Priority": int(row.get("Quality_Priority", 99)) if row.get("Quality_Priority") else 99,
                    "Notes": row.get("Notes", "").strip(),
                    "Status": "Active"  # Default status
                }
                
                # Add tags based on performance and characteristics
                tags = []
                performance = record["Performance_Tier"]
                if "WINNER" in performance:
                    tags.extend(["Winner", "High Performer"])
                elif "HIGH PERFORMER" in performance:
                    tags.append("High Performer")
                elif "SEASONAL" in performance:
                    tags.append("Seasonal")
                elif "FATHERS DAY" in performance:
                    tags.append("Fathers Day")
                elif "MOTHERS DAY" in performance:
                    tags.append("Mothers Day")
                
                if record["Days_Ago"] <= 30:
                    tags.append("Recent")
                
                if record["Directory_Source"] == "hd_ad_creatives":
                    tags.append("HD Quality")
                
                if tags:
                    record["Tags"] = tags
                
                records.append(record)
                
        print(f"📊 Loaded {len(records)} records from CSV")
        return records
        
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return []

def create_views_configuration() -> Dict:
    """Define view configurations for the table"""
    return {
        "views": [
            {
                "name": "All Creative Assets",
                "type": "grid",
                "sort": [
                    {"field": "Quality_Priority", "direction": "asc"},
                    {"field": "Days_Ago", "direction": "asc"}
                ]
            },
            {
                "name": "Winners Only",
                "type": "grid", 
                "filter": {
                    "filterByFormula": "SEARCH('🥇 WINNER', {Performance_Tier})"
                }
            },
            {
                "name": "Recent Assets (30 days)",
                "type": "grid",
                "filter": {
                    "filterByFormula": "{Days_Ago} <= 30"
                }
            },
            {
                "name": "By Brand",
                "type": "grid",
                "groupBy": [{"field": "Brand"}]
            },
            {
                "name": "High Quality HD",
                "type": "grid",
                "filter": {
                    "filterByFormula": "{Directory_Source} = 'hd_ad_creatives'"
                }
            }
        ]
    }

def get_latest_csv_file() -> Optional[str]:
    """Find the most recent airtable_import CSV file"""
    import glob
    
    csv_files = glob.glob("airtable_import_*.csv")
    if not csv_files:
        print("❌ No airtable_import CSV files found")
        return None
    
    # Sort by filename (which includes timestamp)
    latest_file = sorted(csv_files)[-1]
    print(f"📁 Found latest CSV file: {latest_file}")
    return latest_file

def main():
    """Main execution function"""
    print("🚀 AIRTABLE CREATIVE DATABASE CREATOR")
    print("=" * 50)
    
    # Step 1: Check for latest CSV file
    print("\n1️⃣ Looking for latest creative inventory CSV...")
    csv_file = get_latest_csv_file()
    
    if not csv_file:
        print("❌ Please run the comprehensive_creative_scanner.py first to generate CSV data")
        return
    
    # Step 2: Load CSV data
    print("\n2️⃣ Loading CSV data...")
    records = load_csv_data(csv_file)
    
    if not records:
        print("❌ No records loaded from CSV")
        return
    
    # Step 3: Check/Create table
    print("\n3️⃣ Checking Airtable setup...")
    table_exists = check_table_exists(TABLE_NAME)
    
    if not table_exists:
        print(f"\n📋 MANUAL SETUP REQUIRED:")
        print(f"Please create a table named '{TABLE_NAME}' in your Airtable base with these fields:")
        print("\n" + "="*60)
        
        for field in TABLE_SCHEMA["fields"]:
            field_name = field["name"]
            field_type = field["type"]
            
            if field_type == "singleSelect" and "options" in field:
                choices = [choice["name"] for choice in field["options"]["choices"]]
                print(f"📋 {field_name} ({field_type})")
                print(f"   Options: {', '.join(choices[:5])}{'...' if len(choices) > 5 else ''}")
            else:
                print(f"📋 {field_name} ({field_type})")
        
        print("\n" + "="*60)
        print("After creating the table, run this script again.")
        
        # Save configuration for reference
        with open(f'airtable_table_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(TABLE_SCHEMA, f, indent=2)
        print(f"💾 Table configuration saved for reference")
        return
    
    # Step 4: Insert records
    print(f"\n4️⃣ Inserting records into '{TABLE_NAME}'...")
    success = batch_insert_records(TABLE_NAME, records)
    
    if success:
        print(f"\n✅ SUCCESS!")
        print(f"📊 All {len(records)} creative assets imported to Airtable")
        print(f"🔗 View your table: https://airtable.com/{AIRTABLE_BASE_ID}")
        
        # Print summary stats
        brands = {}
        types = {}
        for record in records:
            brand = record.get("Brand", "Unknown")
            creative_type = record.get("Creative_Type", "unknown")
            brands[brand] = brands.get(brand, 0) + 1
            types[creative_type] = types.get(creative_type, 0) + 1
        
        print(f"\n📈 IMPORT SUMMARY:")
        print(f"🏢 Brands: {', '.join([f'{b}({c})' for b, c in sorted(brands.items())])}")
        print(f"🎬 Types: {', '.join([f'{t}({c})' for t, c in sorted(types.items())])}")
        
        # Suggested views info
        views_config = create_views_configuration()
        print(f"\n👁️ SUGGESTED VIEWS TO CREATE:")
        for view in views_config["views"]:
            print(f"  📋 {view['name']}")
            
    else:
        print(f"\n❌ Import completed with errors")
        print(f"Please check the error messages above")

if __name__ == "__main__":
    main() 
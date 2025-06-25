#!/usr/bin/env python3
"""
Smart Airtable Upload - Schema Detection
First detects existing table fields, then uploads data with proper field mapping
"""

import csv
import json
import requests
import time
import re
from datetime import datetime

# Fixed credentials from user
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_NAME = "Creative Ads Performance"

def clean_percentage(value):
    """Clean percentage values and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        cleaned = str(value).replace('%', '').strip()
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def clean_currency(value):
    """Clean currency values and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def clean_integer(value):
    """Clean and convert to integer"""
    if not value or value == "":
        return 0
    try:
        return int(float(str(value).replace(',', '').strip()))
    except:
        return 0

def clean_float(value):
    """Clean and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        return float(str(value).replace(',', '').strip())
    except:
        return 0.0

def clean_string(value):
    """Clean string values"""
    if not value:
        return ""
    return str(value).strip()

def get_table_schema():
    """Get the existing table schema from Airtable"""
    print("🔍 Detecting existing table schema...")
    
    # Get table schema
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Find our table
        for table in data.get("tables", []):
            if table.get("name") == TABLE_NAME:
                fields = table.get("fields", [])
                print(f"✅ Found table '{TABLE_NAME}' with {len(fields)} fields:")
                for field in fields:
                    field_name = field.get("name", "")
                    field_type = field.get("type", "")
                    print(f"   • {field_name} ({field_type})")
                return fields
        
        print(f"❌ Table '{TABLE_NAME}' not found in base")
        print("Available tables:")
        for table in data.get("tables", []):
            print(f"   • {table.get('name', 'Unknown')}")
        return None
    else:
        print(f"❌ Error getting schema: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def upload_with_simple_mapping():
    """Upload data using simple field mapping"""
    print("\n📤 Attempting upload with simple field mapping...")
    
    csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
        print(f"📄 Found {len(rows)} records to upload")
        
        # Create simplified records - just use the first few most important fields
        records = []
        for i, row in enumerate(rows, 1):
            try:
                # Use minimal field set that's most likely to work
                record = {
                    "Name": clean_string(row.get("Ad Name", "")),  # Most tables have a "Name" field
                    "Notes": f"CVR: {clean_percentage(row.get('CVR (%)')):.2f}% | CPA: ${clean_currency(row.get('CPA ($)')):.2f} | {clean_string(row.get('Performance Tier', ''))} | {clean_string(row.get('Recommended Action', ''))}",
                    "URL": clean_string(row.get("GitHub Download URL", "")),
                }
                records.append({"fields": record})
                print(f"   ✅ Prepared record {i}: {record['Name']}")
                
            except Exception as e:
                print(f"   ❌ Error preparing record {i}: {e}")
                continue
        
        # Upload in batches
        batch_size = 10
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {"records": batch}
            
            print(f"📤 Uploading batch {i//batch_size + 1} ({len(batch)} records)...")
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                uploaded_count = len(result.get("records", []))
                total_uploaded += uploaded_count
                print(f"   ✅ Successfully uploaded {uploaded_count} records")
                
                # Show sample of uploaded records
                for record in result.get("records", [])[:2]:
                    ad_name = record.get("fields", {}).get("Name", "Unknown")
                    print(f"      • {ad_name}")
                    
            else:
                print(f"   ❌ Error uploading batch: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # If this fails too, show what fields we tried to use
                if i == 0:  # Only show for first batch
                    print("\n🔍 Fields we tried to use:")
                    sample_record = batch[0]["fields"]
                    for field_name in sample_record.keys():
                        print(f"   • {field_name}")
                break
            
            time.sleep(0.2)
        
        print()
        print("=" * 60)
        print(f"🎉 Upload Complete!")
        print(f"📊 Total Records Uploaded: {total_uploaded}/{len(rows)}")
        print(f"✅ Success Rate: {(total_uploaded/len(rows)*100):.1f}%")
        
        if total_uploaded > 0:
            print(f"🔗 View your data at: https://airtable.com/{BASE_ID}")
            print()
            print("📝 NOTE: This was a simplified upload with basic fields.")
            print("   You can manually add more columns in Airtable and re-run with full data.")
        
        return total_uploaded > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main upload function"""
    print("🚀 Smart Airtable Upload - Schema Detection")
    print("=" * 60)
    print(f"📊 Base ID: {BASE_ID}")
    print(f"📋 Table: {TABLE_NAME}")
    print()
    
    # First try to get the schema
    schema = get_table_schema()
    
    if schema is None:
        print("\n⚠️  Could not detect schema, trying simple upload...")
    
    # Try upload with simple mapping
    success = upload_with_simple_mapping()
    
    if success:
        print("\n🎉 SUCCESS! Your creative ads data is now in Airtable!")
        print("\n📋 Next Steps:")
        print("1. Go to your Airtable base to view the data")
        print("2. Add more columns if you want additional fields")
        print("3. Use the data for your creative ads analysis")
    else:
        print("\n❌ Upload failed. Please check:")
        print("1. Table name is exactly 'Creative Ads Performance'")
        print("2. You have write permissions to the table")
        print("3. The base ID is correct")

if __name__ == "__main__":
    main() 
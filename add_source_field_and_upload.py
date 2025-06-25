#!/usr/bin/env python3
"""
Add Source_File Field and Upload Veo 3 Data
Creation Date: June 24, 2025
Version: 1.0

This script adds the missing Source_File field to the existing Veo3 Videos table
and then uploads all the consolidated video data.
"""

import requests
import json
import pandas as pd
import time

def add_source_file_field(api_key, app_id, table_name="Veo3 Videos"):
    """Add the Source_File field to the existing table"""
    
    print(f"🔧 ADDING SOURCE_FILE FIELD TO TABLE: {table_name}")
    print("="*50)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Define the new field
    new_field = {
        "name": "Source_File",
        "type": "singleLineText"
    }
    
    try:
        # Add the field to the table
        url = f"https://api.airtable.com/v0/meta/bases/{app_id}/tables/{table_name}/fields"
        response = requests.post(url, headers=headers, data=json.dumps(new_field))
        
        if response.status_code == 200:
            result = response.json()
            field_id = result.get('id')
            print(f"✅ Successfully added Source_File field!")
            print(f"   📋 Field ID: {field_id}")
            return True
        else:
            print(f"❌ Error adding field: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception adding field: {e}")
        return False

def upload_to_table(api_key, app_id, table_name, csv_file):
    """Upload data to the table"""
    
    print(f"\n📤 UPLOADING DATA TO {table_name}")
    print("="*50)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Load the CSV data
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} records from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return 0
    
    # Format records for Airtable - keep everything as strings for compatibility
    records = []
    for idx, row in df.iterrows():
        record = {"fields": {}}
        
        for key, value in row.items():
            if pd.isna(value):
                continue
            
            # Convert everything to string for maximum compatibility
            record["fields"][key] = str(value)
        
        records.append(record)
    
    # Upload in batches
    base_url = f"https://api.airtable.com/v0/{app_id}/{table_name}"
    batch_size = 10
    successful_uploads = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        payload = {
            "records": batch,
            "typecast": True
        }
        
        print(f"📤 Uploading batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1} ({len(batch)} records)...")
        
        try:
            response = requests.post(base_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                successful_uploads += len(result.get('records', []))
                print(f"   ✅ Success! Uploaded {len(batch)} records")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                # Print first few records for debugging
                if i == 0:
                    print(f"   🔍 Sample record: {json.dumps(batch[0], indent=2)[:200]}...")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"   📊 Total records: {len(records)}")
    print(f"   ✅ Successfully uploaded: {successful_uploads}")
    
    return successful_uploads

def main():
    print("🚀 AIRTABLE SOURCE FIELD ADDER & DATA UPLOADER")
    print("="*60)
    
    # Configuration
    API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
    APP_ID = "apptaYco3MXfoLI9M"
    TABLE_NAME = "Veo3 Videos"
    
    # Find the consolidated CSV file
    import glob
    csv_files = glob.glob("GoogleFlow_Veo3_CONSOLIDATED_*.csv")
    
    if not csv_files:
        print("❌ No consolidated CSV file found!")
        return
    
    csv_file = sorted(csv_files)[-1]
    print(f"📁 Using file: {csv_file}")
    
    # Add the missing field
    field_added = add_source_file_field(API_KEY, APP_ID, TABLE_NAME)
    
    if field_added:
        print(f"\n⏳ Waiting 2 seconds for field to be ready...")
        time.sleep(2)
    else:
        print(f"\n⚠️ Field addition failed, but continuing with upload (field might already exist)...")
    
    # Upload the data
    uploaded_count = upload_to_table(API_KEY, APP_ID, TABLE_NAME, csv_file)
    
    if uploaded_count > 0:
        print(f"\n🎉 SUCCESS! Your Veo 3 videos are now in Airtable!")
        print(f"   🔗 View at: https://airtable.com/{APP_ID}")
        print(f"   📋 Table: {TABLE_NAME}")
        print(f"   📊 Records: {uploaded_count}")
    else:
        print(f"\n❌ Upload failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 
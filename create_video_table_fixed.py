#!/usr/bin/env python3
"""
Fixed Airtable Table Creator for Video Data
Creation Date: June 24, 2025
Version: 1.1

This script creates a new table in Airtable with the proper structure
for video creative data, then uploads the Veo 3 videos.
"""

import requests
import json
import pandas as pd
import time

def create_video_table(api_key, app_id, table_name="Veo3 Videos"):
    """Create a new table with video data structure"""
    
    print(f"🏗️ CREATING NEW TABLE: {table_name}")
    print("="*50)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Define the table structure based on your CSV with proper field types
    table_structure = {
        "name": table_name,
        "fields": [
            {"name": "Ad_ID", "type": "number", "options": {"precision": 0}},
            {"name": "Ad_Name", "type": "singleLineText"},
            {"name": "Account", "type": "singleLineText"},
            {"name": "Campaign", "type": "singleLineText"},
            {"name": "Creative_ID", "type": "number", "options": {"precision": 0}},
            {"name": "Status", "type": "singleSelect", "options": {
                "choices": [
                    {"name": "ACTIVE", "color": "greenLight2"},
                    {"name": "PAUSED", "color": "yellowLight2"},
                    {"name": "ARCHIVED", "color": "grayLight2"}
                ]
            }},
            {"name": "Performance_Rating", "type": "singleSelect", "options": {
                "choices": [
                    {"name": "EXCELLENT", "color": "greenLight2"},
                    {"name": "GOOD", "color": "blueLight2"},
                    {"name": "AVERAGE", "color": "yellowLight2"},
                    {"name": "POOR", "color": "redLight2"},
                    {"name": "PENDING_ANALYSIS", "color": "grayLight2"}
                ]
            }},
            {"name": "CPA", "type": "singleLineText"},
            {"name": "CVR", "type": "singleLineText"},
            {"name": "CTR", "type": "singleLineText"},
            {"name": "Spend", "type": "currency", "options": {"precision": 2, "symbol": "USD"}},
            {"name": "Purchases", "type": "number", "options": {"precision": 0}},
            {"name": "Video_Views", "type": "number", "options": {"precision": 0}},
            {"name": "Hook_Rate", "type": "singleLineText"},
            {"name": "Facebook_Preview_Link", "type": "url"},
            {"name": "Meta_Video_URL", "type": "url"},
            {"name": "Google_Drive_Download_Link", "type": "url"},
            {"name": "Google_Drive_View_Link", "type": "url"},
            {"name": "Creative_Type", "type": "singleLineText"},
            {"name": "Hook_Type", "type": "singleLineText"},
            {"name": "Targeting", "type": "singleLineText"},
            {"name": "Priority", "type": "singleLineText"},
            {"name": "Notes", "type": "multilineText"},
            {"name": "Download_Command", "type": "multilineText"}
        ]
    }
    
    try:
        # Create the table
        url = f"https://api.airtable.com/v0/meta/bases/{app_id}/tables"
        response = requests.post(url, headers=headers, data=json.dumps(table_structure))
        
        if response.status_code == 200:
            result = response.json()
            table_id = result.get('id')
            print(f"✅ Successfully created table '{table_name}'!")
            print(f"   📋 Table ID: {table_id}")
            return table_name, table_id
        else:
            print(f"❌ Error creating table: {response.status_code} - {response.text}")
            
            # If table creation fails, try a simpler approach with basic field types
            print(f"\n🔄 Trying with simplified field types...")
            return create_simple_table(api_key, app_id, table_name)
            
    except Exception as e:
        print(f"❌ Exception creating table: {e}")
        return None, None

def create_simple_table(api_key, app_id, table_name):
    """Create a table with simpler field types if the complex one fails"""
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Simplified table structure - all text fields except key numbers
    simple_structure = {
        "name": table_name,
        "fields": [
            {"name": "Ad_ID", "type": "singleLineText"},
            {"name": "Ad_Name", "type": "singleLineText"},
            {"name": "Account", "type": "singleLineText"},
            {"name": "Campaign", "type": "singleLineText"},
            {"name": "Creative_ID", "type": "singleLineText"},
            {"name": "Status", "type": "singleLineText"},
            {"name": "Performance_Rating", "type": "singleLineText"},
            {"name": "CPA", "type": "singleLineText"},
            {"name": "CVR", "type": "singleLineText"},
            {"name": "CTR", "type": "singleLineText"},
            {"name": "Spend", "type": "singleLineText"},
            {"name": "Purchases", "type": "singleLineText"},
            {"name": "Video_Views", "type": "singleLineText"},
            {"name": "Hook_Rate", "type": "singleLineText"},
            {"name": "Facebook_Preview_Link", "type": "url"},
            {"name": "Meta_Video_URL", "type": "url"},
            {"name": "Google_Drive_Download_Link", "type": "url"},
            {"name": "Google_Drive_View_Link", "type": "url"},
            {"name": "Creative_Type", "type": "singleLineText"},
            {"name": "Hook_Type", "type": "singleLineText"},
            {"name": "Targeting", "type": "singleLineText"},
            {"name": "Priority", "type": "singleLineText"},
            {"name": "Notes", "type": "multilineText"},
            {"name": "Download_Command", "type": "multilineText"}
        ]
    }
    
    try:
        url = f"https://api.airtable.com/v0/meta/bases/{app_id}/tables"
        response = requests.post(url, headers=headers, data=json.dumps(simple_structure))
        
        if response.status_code == 200:
            result = response.json()
            table_id = result.get('id')
            print(f"✅ Successfully created simplified table '{table_name}'!")
            print(f"   📋 Table ID: {table_id}")
            return table_name, table_id
        else:
            print(f"❌ Error creating simplified table: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Exception creating simplified table: {e}")
        return None, None

def upload_to_new_table(api_key, app_id, table_name, csv_file):
    """Upload data to the newly created table"""
    
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
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"   📊 Total records: {len(records)}")
    print(f"   ✅ Successfully uploaded: {successful_uploads}")
    
    return successful_uploads

def main():
    print("🚀 AIRTABLE VIDEO TABLE CREATOR & UPLOADER (FIXED)")
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
    
    # Create the new table
    table_name, table_id = create_video_table(API_KEY, APP_ID, TABLE_NAME)
    
    if table_name:
        print(f"\n⏳ Waiting 3 seconds for table to be ready...")
        time.sleep(3)
        
        # Upload the data
        uploaded_count = upload_to_new_table(API_KEY, APP_ID, table_name, csv_file)
        
        if uploaded_count > 0:
            print(f"\n🎉 SUCCESS! Your Veo 3 videos are now in Airtable!")
            print(f"   🔗 View at: https://airtable.com/{APP_ID}")
            print(f"   📋 Table: {table_name}")
            print(f"   📊 Records: {uploaded_count}")
        else:
            print(f"\n❌ Upload failed. Please check the error messages above.")
    else:
        print(f"\n❌ Failed to create table. Cannot proceed with upload.")

if __name__ == "__main__":
    main() 
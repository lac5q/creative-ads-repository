#!/usr/bin/env python3
"""
Clean CSV and Upload to Existing Table
Creation Date: June 24, 2025
Version: 1.0

This script removes the Source_File column from the CSV and uploads
the clean data to the existing Veo3 Videos table.
"""

import requests
import json
import pandas as pd
import time

def create_clean_csv(input_csv, output_csv):
    """Remove the Source_File column and create a clean CSV"""
    
    print(f"🧹 CLEANING CSV DATA")
    print("="*50)
    
    try:
        # Load the original CSV
        df = pd.read_csv(input_csv)
        print(f"📊 Loaded {len(df)} records from {input_csv}")
        
        # Remove the Source_File column if it exists
        if 'Source_File' in df.columns:
            df = df.drop('Source_File', axis=1)
            print(f"✅ Removed Source_File column")
        
        # Save the clean CSV
        df.to_csv(output_csv, index=False)
        print(f"💾 Saved clean CSV to {output_csv}")
        print(f"📋 Columns: {list(df.columns)}")
        
        return output_csv, len(df)
        
    except Exception as e:
        print(f"❌ Error cleaning CSV: {e}")
        return None, 0

def upload_to_table(api_key, app_id, table_name, csv_file):
    """Upload data to the table"""
    
    print(f"\n📤 UPLOADING CLEAN DATA TO {table_name}")
    print("="*50)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Load the clean CSV data
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} records from clean CSV")
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
                
                # Show sample record IDs for first batch
                if i == 0 and result.get('records'):
                    sample_ids = [r.get('id') for r in result['records'][:3]]
                    print(f"   📋 Sample record IDs: {sample_ids}")
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                # Print first record for debugging
                if i == 0:
                    print(f"   🔍 Sample record fields: {list(batch[0]['fields'].keys())}")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"   📊 Total records: {len(records)}")
    print(f"   ✅ Successfully uploaded: {successful_uploads}")
    
    return successful_uploads

def main():
    print("🚀 CLEAN CSV AND UPLOAD TO AIRTABLE")
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
    
    input_csv = sorted(csv_files)[-1]
    output_csv = "GoogleFlow_Veo3_CLEAN_FOR_UPLOAD.csv"
    
    print(f"📁 Input file: {input_csv}")
    print(f"📁 Output file: {output_csv}")
    
    # Clean the CSV
    clean_csv, record_count = create_clean_csv(input_csv, output_csv)
    
    if clean_csv and record_count > 0:
        print(f"\n⏳ Proceeding with upload...")
        
        # Upload the clean data
        uploaded_count = upload_to_table(API_KEY, APP_ID, TABLE_NAME, clean_csv)
        
        if uploaded_count > 0:
            print(f"\n🎉 SUCCESS! Your Veo 3 videos are now in Airtable!")
            print(f"   🔗 View at: https://airtable.com/{APP_ID}")
            print(f"   📋 Table: {TABLE_NAME}")
            print(f"   📊 Records: {uploaded_count}")
            print(f"   📁 Clean CSV saved as: {output_csv}")
        else:
            print(f"\n❌ Upload failed. Please check the error messages above.")
    else:
        print(f"\n❌ Failed to create clean CSV. Cannot proceed with upload.")

if __name__ == "__main__":
    main() 
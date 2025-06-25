#!/usr/bin/env python3
"""
Airtable Upload Script for Veo 3 Videos
Creation Date: June 24, 2025
Version: 1.0

This script uploads the consolidated Veo 3 video data to Airtable
using the provided API credentials.
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime

class AirtableUploader:
    def __init__(self, api_key, app_id, table_name="Creative Ads Analysis"):
        """Initialize the Airtable uploader"""
        self.api_key = api_key
        self.app_id = app_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{app_id}/{table_name}"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def format_record_for_airtable(self, row):
        """Format a CSV row for Airtable API"""
        # Convert pandas row to dictionary and handle NaN values
        record = {}
        for key, value in row.items():
            if pd.isna(value) or value == 'TBD' or value == '':
                continue  # Skip empty/TBD values
            
            # Convert numeric strings to proper types
            if key in ['CPA', 'Spend']:
                try:
                    record[key] = float(value) if value != 'TBD' else None
                except (ValueError, TypeError):
                    record[key] = str(value)
            elif key in ['Purchases', 'Video_Views', 'Ad_ID', 'Creative_ID']:
                try:
                    record[key] = int(float(value)) if value != 'TBD' else None
                except (ValueError, TypeError):
                    record[key] = str(value)
            elif key in ['CVR', 'CTR', 'Hook_Rate']:
                # Handle percentage values
                try:
                    if isinstance(value, str) and '%' in value:
                        record[key] = value
                    elif value != 'TBD':
                        record[key] = f"{float(value)}%" if float(value) < 1 else f"{float(value)/100}%"
                except (ValueError, TypeError):
                    record[key] = str(value)
            else:
                record[key] = str(value)
        
        return {"fields": record}
    
    def upload_records_batch(self, records, batch_size=10):
        """Upload records in batches to respect Airtable rate limits"""
        all_results = []
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            payload = {
                "records": batch,
                "typecast": True  # Automatically convert field types
            }
            
            print(f"📤 Uploading batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1} ({len(batch)} records)...")
            
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    all_results.extend(result.get('records', []))
                    print(f"   ✅ Success! Uploaded {len(batch)} records")
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text}")
                    
                    # Try to parse error details
                    try:
                        error_details = response.json()
                        if 'error' in error_details:
                            print(f"      Error details: {error_details['error']}")
                    except:
                        pass
                
                # Rate limiting - wait between batches
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Exception during upload: {e}")
        
        return all_results
    
    def get_table_schema(self):
        """Get the current table schema to understand field types"""
        try:
            # Get a few records to understand the schema
            response = requests.get(
                f"{self.base_url}?maxRecords=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('records'):
                    fields = data['records'][0].get('fields', {})
                    print(f"📋 Current table fields: {list(fields.keys())}")
                    return fields
                else:
                    print("📋 Table exists but is empty")
                    return {}
            else:
                print(f"❌ Error getting schema: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception getting schema: {e}")
            return {}

def main():
    print("🚀 AIRTABLE UPLOAD - VEO 3 VIDEOS")
    print("="*60)
    
    # Configuration
    API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
    APP_ID = "apptaYco3MXfoLI9M"
    TABLE_NAME = "Creative Ads Analysis"  # Adjust if your table name is different
    
    # Find the consolidated CSV file
    import glob
    csv_files = glob.glob("GoogleFlow_Veo3_CONSOLIDATED_*.csv")
    
    if not csv_files:
        print("❌ No consolidated CSV file found!")
        print("   Please run the consolidation script first.")
        return
    
    # Use the most recent file
    csv_file = sorted(csv_files)[-1]
    print(f"📁 Using file: {csv_file}")
    
    # Load the data
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} records from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Initialize uploader
    uploader = AirtableUploader(API_KEY, APP_ID, TABLE_NAME)
    
    # Get table schema (optional, for debugging)
    print(f"\n🔍 Checking Airtable connection...")
    schema = uploader.get_table_schema()
    
    # Format records for Airtable
    print(f"\n🔄 Formatting {len(df)} records for Airtable...")
    airtable_records = []
    
    for idx, row in df.iterrows():
        try:
            record = uploader.format_record_for_airtable(row)
            airtable_records.append(record)
        except Exception as e:
            print(f"   ⚠️ Error formatting record {idx}: {e}")
            continue
    
    print(f"   ✅ Successfully formatted {len(airtable_records)} records")
    
    # Upload to Airtable
    print(f"\n📤 Starting upload to Airtable...")
    print(f"   📍 App ID: {APP_ID}")
    print(f"   📍 Table: {TABLE_NAME}")
    
    results = uploader.upload_records_batch(airtable_records)
    
    # Summary
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"   📊 Total records processed: {len(df)}")
    print(f"   📤 Records uploaded successfully: {len(results)}")
    print(f"   ⚠️ Records with errors: {len(df) - len(results)}")
    
    if results:
        print(f"\n✅ SUCCESS! Your Veo 3 videos are now in Airtable!")
        print(f"   🔗 View at: https://airtable.com/{APP_ID}")
    else:
        print(f"\n❌ No records were uploaded successfully.")
        print(f"   Please check your Airtable credentials and table name.")

if __name__ == "__main__":
    main() 
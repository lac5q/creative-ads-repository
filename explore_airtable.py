#!/usr/bin/env python3
"""
Airtable Explorer Script
Creation Date: June 24, 2025
Version: 1.0

This script explores the Airtable base to find available tables
and their schemas.
"""

import requests
import json

def explore_airtable_base(api_key, app_id):
    """Explore the Airtable base to find tables and their schemas"""
    
    print("🔍 AIRTABLE BASE EXPLORER")
    print("="*50)
    print(f"📍 App ID: {app_id}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Try to get base metadata (this might not work with all API tokens)
    print(f"\n🔍 Attempting to get base metadata...")
    try:
        meta_url = f"https://api.airtable.com/v0/meta/bases/{app_id}/tables"
        response = requests.get(meta_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get('tables', [])
            print(f"✅ Found {len(tables)} tables in base:")
            
            for table in tables:
                print(f"   📋 Table: {table.get('name', 'Unknown')} (ID: {table.get('id', 'Unknown')})")
                fields = table.get('fields', [])
                print(f"      📝 Fields ({len(fields)}): {[f.get('name') for f in fields[:5]]}{'...' if len(fields) > 5 else ''}")
            
            return tables
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Try common table names by attempting to access them
    print(f"\n🔍 Trying common table names...")
    common_names = [
        "Creative Ads Analysis",
        "Table 1",
        "tblMain",
        "Main",
        "Ads",
        "Creative",
        "Videos",
        "Data",
        "Sheet1"
    ]
    
    working_tables = []
    
    for table_name in common_names:
        try:
            url = f"https://api.airtable.com/v0/{app_id}/{table_name}?maxRecords=1"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"   ✅ Table '{table_name}' exists! ({len(records)} sample records)")
                
                if records:
                    fields = list(records[0].get('fields', {}).keys())
                    print(f"      📝 Sample fields: {fields[:5]}{'...' if len(fields) > 5 else ''}")
                
                working_tables.append(table_name)
            elif response.status_code == 404:
                print(f"   ❌ Table '{table_name}' not found")
            elif response.status_code == 403:
                print(f"   🔒 Table '{table_name}' - permission denied")
            else:
                print(f"   ⚠️ Table '{table_name}' - error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error checking '{table_name}': {e}")
    
    return working_tables

def main():
    # Configuration
    API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
    APP_ID = "apptaYco3MXfoLI9M"
    
    working_tables = explore_airtable_base(API_KEY, APP_ID)
    
    print(f"\n📊 SUMMARY:")
    if working_tables:
        print(f"✅ Found {len(working_tables)} accessible table(s):")
        for table in working_tables:
            print(f"   📋 {table}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Use one of these table names in your upload script:")
        for table in working_tables:
            print(f"   TABLE_NAME = \"{table}\"")
    else:
        print(f"❌ No accessible tables found.")
        print(f"   This could mean:")
        print(f"   1. The API token doesn't have permission to access tables")
        print(f"   2. The App ID is incorrect")
        print(f"   3. The tables have different names than expected")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Check your Airtable base URL to confirm the App ID")
        print(f"   2. Verify your API token has 'data.records:read' and 'data.records:write' permissions")
        print(f"   3. Make sure the token is associated with the correct workspace")

if __name__ == "__main__":
    main() 
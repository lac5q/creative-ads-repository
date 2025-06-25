#!/usr/bin/env python3
"""
Debug Airtable Table Information
Find the correct table name and ID for field creation
"""

import requests
import json

# Fixed credentials from user
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"

def debug_base_info():
    """Get detailed information about the base and its tables"""
    print("🔍 Debugging Airtable Base Information...")
    print("=" * 60)
    
    # Get base metadata
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"📊 Base ID: {BASE_ID}")
    print(f"🔗 URL: {url}")
    print()
    
    response = requests.get(url, headers=headers)
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ Successfully connected to Airtable!")
        print(f"📋 Found {len(data.get('tables', []))} table(s):")
        print()
        
        for i, table in enumerate(data.get("tables", []), 1):
            table_name = table.get("name", "Unknown")
            table_id = table.get("id", "Unknown")
            fields = table.get("fields", [])
            
            print(f"🏷️  Table {i}: {table_name}")
            print(f"   📍 Table ID: {table_id}")
            print(f"   📝 Fields ({len(fields)}):")
            
            for j, field in enumerate(fields, 1):
                field_name = field.get("name", "Unknown")
                field_type = field.get("type", "Unknown")
                print(f"      {j:2d}. {field_name} ({field_type})")
            
            print()
            
            # If this looks like our target table, try to add a field
            if "creative" in table_name.lower() or "ads" in table_name.lower() or "performance" in table_name.lower():
                print(f"🎯 This looks like our target table: {table_name}")
                print(f"   Using Table ID: {table_id}")
                
                # Try to create a test field
                print("   🧪 Testing field creation...")
                
                test_field = {
                    "name": "Test Field", 
                    "type": "singleLineText"
                }
                
                create_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_id}/fields"
                
                test_response = requests.post(create_url, headers=headers, json=test_field)
                
                if test_response.status_code == 200:
                    print("   ✅ Field creation works! This is the correct table.")
                    
                    # Delete the test field
                    test_field_id = test_response.json().get("id")
                    if test_field_id:
                        delete_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_id}/fields/{test_field_id}"
                        delete_response = requests.delete(delete_url, headers=headers)
                        if delete_response.status_code == 200:
                            print("   🧹 Test field cleaned up successfully")
                    
                    return table_id, table_name
                else:
                    print(f"   ❌ Field creation failed: {test_response.status_code}")
                    print(f"   Response: {test_response.text}")
        
        return None, None
        
    else:
        print(f"❌ Error connecting to Airtable: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("🔑 This looks like an authentication issue.")
            print("   - Check if your API key is correct")
            print("   - Make sure the API key has proper permissions")
        elif response.status_code == 404:
            print("🔍 This looks like a 'not found' issue.")
            print("   - Check if your Base ID is correct")
            print("   - Make sure the base exists and you have access")
        
        return None, None

def test_data_upload(table_id, table_name):
    """Test uploading a simple record to verify everything works"""
    print(f"🧪 Testing data upload to table: {table_name}")
    
    # Get existing records first
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        records = response.json().get("records", [])
        print(f"   📄 Found {len(records)} existing records")
        
        # Try to upload a test record
        test_record = {
            "records": [{
                "fields": {
                    "Name": "TEST RECORD - DELETE ME"
                }
            }]
        }
        
        upload_response = requests.post(url, headers=headers, json=test_record)
        
        if upload_response.status_code == 200:
            print("   ✅ Data upload works!")
            
            # Delete the test record
            test_record_id = upload_response.json().get("records", [{}])[0].get("id")
            if test_record_id:
                delete_url = f"{url}/{test_record_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 200:
                    print("   🧹 Test record cleaned up")
            
            return True
        else:
            print(f"   ❌ Data upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text}")
            return False
    else:
        print(f"   ❌ Could not read existing records: {response.status_code}")
        return False

def main():
    """Main debugging function"""
    print("🔍 Airtable Connection Debugger")
    print("=" * 60)
    
    table_id, table_name = debug_base_info()
    
    if table_id and table_name:
        print("=" * 60)
        success = test_data_upload(table_id, table_name)
        
        if success:
            print("=" * 60)
            print("🎉 SUCCESS! Everything is working correctly.")
            print(f"✅ Correct Table ID: {table_id}")
            print(f"✅ Correct Table Name: {table_name}")
            print()
            print("📝 Use these values in your upload script:")
            print(f'TABLE_ID = "{table_id}"')
            print(f'TABLE_NAME = "{table_name}"')
        else:
            print("❌ Data upload test failed")
    else:
        print("❌ Could not identify the correct table")

if __name__ == "__main__":
    main() 
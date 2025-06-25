#!/usr/bin/env python3
"""
Check Airtable Status
Verify current records and test if links are working
"""

import requests

# Configuration
AIRTABLE_TOKEN = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
AIRTABLE_BASE_ID = "apptaYco3MXfoLI9M"
AIRTABLE_TABLE_NAME = "Veo3 Videos"

def test_url(url):
    """Test if a URL is working"""
    if not url or not url.startswith('http'):
        return False
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def check_airtable():
    """Check current Airtable status"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, params={"maxRecords": 10})
    
    if response.status_code != 200:
        print(f"❌ Error fetching records: {response.status_code}")
        return
    
    data = response.json()
    records = data.get('records', [])
    
    print(f"📊 Current Airtable Status:")
    print(f"   📋 Total Records Found: {len(records)}")
    
    if not records:
        print("   ⚠️ No records found in Airtable!")
        return
    
    # Test a few sample records
    print(f"\n🔗 Testing Sample Links:")
    
    working_count = 0
    broken_count = 0
    
    for i, record in enumerate(records[:5]):  # Test first 5 records
        fields = record.get('fields', {})
        ad_id = fields.get('Ad_ID', 'N/A')
        account = fields.get('Account', 'N/A')
        
        # Test Google Drive Download Link
        download_link = fields.get('Google_Drive_Download_Link', '')
        
        if download_link:
            is_working = test_url(download_link)
            status = "✅ WORKING" if is_working else "❌ BROKEN"
            
            print(f"   {i+1}. {account} | {ad_id}")
            print(f"      {status}: {download_link[:80]}...")
            
            if is_working:
                working_count += 1
            else:
                broken_count += 1
        else:
            print(f"   {i+1}. {account} | {ad_id}")
            print(f"      ⚪ NO URL: Empty download link")
            broken_count += 1
    
    print(f"\n📈 Link Status Summary:")
    print(f"   ✅ Working Links: {working_count}")
    print(f"   ❌ Broken Links: {broken_count}")
    
    if working_count > 0:
        print(f"   🎉 SUCCESS! Links are working correctly")
    else:
        print(f"   ⚠️ All tested links are broken - need to fix")
    
    # Show sample record structure
    if records:
        print(f"\n📋 Sample Record Structure:")
        fields = records[0].get('fields', {})
        for key, value in fields.items():
            if isinstance(value, str) and len(value) > 80:
                value = value[:77] + "..."
            print(f"   • {key}: {value}")

if __name__ == "__main__":
    check_airtable() 
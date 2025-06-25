#!/usr/bin/env python3
"""
Create Proper Airtable Columns for Creative Ads Performance Data
This will add structured columns instead of cramming everything into Notes
"""

import requests
import json
import time

# Fixed credentials
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_ID = "tbltqJ5f5L3MYrs0w"  # Performance Tracker table

def create_airtable_columns():
    """Create proper columns for creative ads performance data"""
    
    print("🏗️  Creating Airtable Columns for Creative Ads Performance")
    print("=" * 70)
    
    # Define the columns we need
    columns_to_create = [
        # Performance Metrics
        {"name": "CVR", "type": "percent", "description": "Conversion Rate"},
        {"name": "CTR", "type": "percent", "description": "Click-Through Rate"},
        {"name": "CPC", "type": "currency", "options": {"precision": 2}},
        {"name": "CPA", "type": "currency", "options": {"precision": 2}},
        {"name": "Spend", "type": "currency", "options": {"precision": 2}},
        {"name": "Impressions", "type": "number", "options": {"precision": 0}},
        {"name": "Clicks", "type": "number", "options": {"precision": 0}},
        {"name": "Conversions", "type": "number", "options": {"precision": 0}},
        
        # Creative Details
        {"name": "Platform", "type": "singleSelect", "options": {"choices": [
            {"name": "TurnedYellow", "color": "yellowBright"},
            {"name": "MakeMeJedi", "color": "purpleBright"}
        ]}},
        {"name": "Campaign_Season", "type": "singleSelect", "options": {"choices": [
            {"name": "Fathers Day", "color": "blueBright"},
            {"name": "Valentines Day", "color": "redBright"},
            {"name": "Birthday", "color": "greenBright"},
            {"name": "General", "color": "grayBright"}
        ]}},
        {"name": "Hook_Category", "type": "singleSelect", "options": {"choices": [
            {"name": "Influencer", "color": "orangeBright"},
            {"name": "Product Demo", "color": "tealBright"},
            {"name": "Emotional", "color": "pinkBright"},
            {"name": "Comparison", "color": "cyanBright"}
        ]}},
        {"name": "Performance_Tier", "type": "singleSelect", "options": {"choices": [
            {"name": "Exceptional", "color": "greenBright"},
            {"name": "Excellent", "color": "blueBright"},
            {"name": "Good", "color": "yellowBright"},
            {"name": "Average", "color": "orangeBright"}
        ]}},
        
        # Cross-Platform Analysis
        {"name": "TikTok_Potential", "type": "rating", "options": {"max": 5, "icon": "star", "color": "yellowBright"}},
        {"name": "Google_Potential", "type": "rating", "options": {"max": 5, "icon": "star", "color": "blueBright"}},
        {"name": "Priority_Score", "type": "rating", "options": {"max": 5, "icon": "heart", "color": "redBright"}},
        
        # Asset Management
        {"name": "GitHub_URL", "type": "url"},
        {"name": "Asset_Type", "type": "singleSelect", "options": {"choices": [
            {"name": "Video", "color": "redBright"},
            {"name": "Image", "color": "blueBright"},
            {"name": "Placeholder", "color": "grayBright"}
        ]}},
        {"name": "Download_Command", "type": "singleLineText"},
        
        # Demographics (Top Performing)
        {"name": "Top_Age_Group", "type": "singleLineText"},
        {"name": "Top_Gender", "type": "singleLineText"},
        {"name": "Top_Location", "type": "singleLineText"},
        
        # Recommendations
        {"name": "Recommendations", "type": "multilineText"}
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    successful_columns = []
    failed_columns = []
    
    print(f"📊 Creating {len(columns_to_create)} columns...")
    print()
    
    for i, column in enumerate(columns_to_create, 1):
        print(f"🏗️  Creating column {i:2d}/{len(columns_to_create)}: {column['name']}")
        
        url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{TABLE_ID}/fields"
        
        try:
            response = requests.post(url, headers=headers, json=column)
            
            if response.status_code == 200:
                print(f"   ✅ Success!")
                successful_columns.append(column['name'])
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                failed_columns.append(column['name'])
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            failed_columns.append(column['name'])
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully created: {len(successful_columns)} columns")
    print(f"❌ Failed to create: {len(failed_columns)} columns")
    
    if successful_columns:
        print()
        print("✅ Successful columns:")
        for col in successful_columns:
            print(f"   • {col}")
    
    if failed_columns:
        print()
        print("❌ Failed columns:")
        for col in failed_columns:
            print(f"   • {col}")
    
    return len(successful_columns), len(failed_columns)

def verify_table_structure():
    """Verify the current table structure after column creation"""
    print()
    print("🔍 Verifying updated table structure...")
    
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        for table in data.get("tables", []):
            if table.get("id") == TABLE_ID:
                fields = table.get("fields", [])
                print(f"📋 Table now has {len(fields)} fields:")
                
                for field in fields:
                    field_name = field.get("name", "Unknown")
                    field_type = field.get("type", "Unknown")
                    print(f"   • {field_name} ({field_type})")
                
                return True
    
    print("❌ Could not verify table structure")
    return False

def main():
    """Main function"""
    success_count, fail_count = create_airtable_columns()
    
    if success_count > 0:
        verify_table_structure()
        
        print()
        print("🎉 Column creation completed!")
        print()
        print("📝 Next steps:")
        print("1. Check your Airtable table to see the new columns")
        print("2. Run the upload script to populate data in structured columns")
        print("3. The data will now be properly organized instead of in one Notes column")
    else:
        print("❌ No columns were created successfully")
        print("Please check the error messages above")

if __name__ == "__main__":
    main() 
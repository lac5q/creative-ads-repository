#!/usr/bin/env python3
"""
Upload Creative Ads Data to Structured Airtable Columns
This uploads data to individual columns instead of one Notes column
"""

import csv
import requests
import time
from datetime import datetime

# Fixed credentials
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_ID = "tbltqJ5f5L3MYrs0w"

def clean_percentage(value):
    """Clean percentage values - keep as number for existing number fields"""
    if not value or value == "":
        return 0.0
    try:
        cleaned = str(value).replace('%', '').strip()
        return float(cleaned) if cleaned else 0.0  # Keep as percentage number
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

def clean_string(value):
    """Clean string values"""
    if not value:
        return ""
    return str(value).strip()

def map_performance_tier(tier):
    """Map performance tier to match dropdown options"""
    tier_mapping = {
        "Exceptional": "Exceptional",
        "Excellent": "Excellent", 
        "Good": "Good",
        "Average": "Average",
        "Poor": "Average"  # Map Poor to Average since we don't have Poor option
    }
    return tier_mapping.get(clean_string(tier), "Average")

def map_platform(account):
    """Map account to platform"""
    if "TurnedYellow" in str(account):
        return "TurnedYellow"
    elif "MakeMeJedi" in str(account):
        return "MakeMeJedi"
    else:
        return "MakeMeJedi"  # Default

def map_campaign_season(campaign_name):
    """Extract campaign season from campaign name"""
    campaign = str(campaign_name).lower()
    if "father" in campaign or "dad" in campaign:
        return "Fathers Day"
    elif "valentine" in campaign:
        return "Valentines Day"
    elif "birthday" in campaign:
        return "Birthday"
    else:
        return "General"

def map_hook_category(ad_name):
    """Extract hook category from ad name"""
    name = str(ad_name).lower()
    if "influencer" in name or "david" in name:
        return "Influencer"
    elif "comparison" in name or "vs" in name:
        return "Comparison"
    elif "emotion" in name or "react" in name or "surprise" in name:
        return "Emotional"
    else:
        return "Product Demo"

def map_asset_type(github_url):
    """Determine asset type from GitHub URL"""
    url = str(github_url).lower()
    if "placeholder" in url:
        return "Placeholder"
    elif ".mp4" in url or "video" in url:
        return "Video"
    else:
        return "Image"

def clear_existing_records():
    """Clear existing records from the table"""
    print("🧹 Clearing existing records...")
    
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        existing_records = response.json().get("records", [])
        print(f"   Found {len(existing_records)} existing records")
        
        if existing_records:
            # Delete in batches of 10
            record_ids = [record["id"] for record in existing_records]
            
            for i in range(0, len(record_ids), 10):
                batch_ids = record_ids[i:i+10]
                delete_url = f"{url}?" + "&".join([f"records[]={rid}" for rid in batch_ids])
                
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 200:
                    print(f"   ✅ Deleted {len(batch_ids)} records")
                else:
                    print(f"   ⚠️  Could not delete batch: {delete_response.text}")
                
                time.sleep(0.2)
    else:
        print(f"   ⚠️  Could not fetch existing records: {response.status_code}")

def upload_structured_data():
    """Upload data to structured columns"""
    print("📤 Uploading data to structured columns...")
    
    csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        print(f"📄 Found {len(rows)} records to upload")
        
        # Prepare records for upload using existing column names
        records = []
        for i, row in enumerate(rows, 1):
            try:
                # Extract key metrics
                cvr = clean_percentage(row.get("CVR (%)"))
                ctr = clean_percentage(row.get("CTR (%)"))
                cpa = clean_string(row.get("CPA ($)"))  # Use string field for now
                spend = clean_string(row.get("Spend ($)"))  # Use string field for now
                conversions = clean_integer(row.get("Conversions"))
                impressions = clean_integer(row.get("Impressions", 0))
                clicks = clean_integer(row.get("Clicks", 0))
                
                ad_name = clean_string(row.get("Ad Name", ""))
                account = clean_string(row.get("Account", ""))
                campaign_name = clean_string(row.get("Campaign Name", ""))
                
                record = {
                    "Name": ad_name,
                    
                    # Use existing column names from table structure
                    "Ad ID": clean_string(row.get("Ad ID", "")),
                    "Account": account,
                    "Campaign Name": campaign_name,
                    
                    # Performance Metrics (using existing columns)
                    "CVR (%)": cvr,
                    "CTR (%)": ctr,
                    "CPA": cpa,  # String field
                    "Spend": spend,  # String field
                    "Conversions": conversions,
                    "Impressions": impressions,
                    "Clicks": clicks,
                    
                    # Use new structured columns where available
                    "Platform": map_platform(account),
                    "Campaign_Season": map_campaign_season(campaign_name),
                    "Hook_Category": map_hook_category(ad_name),
                    "Performance_Tier": map_performance_tier(row.get("Performance Tier")),
                    
                    # Cross-Platform Analysis (using new rating fields)
                    "TikTok_Potential": min(5, max(1, clean_integer(row.get("TikTok Score", 3)))),
                    "Google_Potential": min(5, max(1, clean_integer(row.get("Google Score", 3)))),
                    "Priority_Score": min(5, max(1, clean_integer(row.get("Priority Score", 3)))),
                    
                    # Asset Management (using new fields)
                    "GitHub_URL": clean_string(row.get("GitHub Download URL", "")),
                    "Asset_Type": map_asset_type(row.get("GitHub Download URL", "")),
                    "Download_Command": clean_string(row.get("Download Command", "")),
                    
                    # Demographics (using new fields)
                    "Top_Age_Group": clean_string(row.get("Primary Age Group", "")),
                    "Top_Gender": clean_string(row.get("Primary Gender", "")),
                    "Top_Location": clean_string(row.get("Top Location", "")),
                    
                    # Recommendations (using new field)
                    "Recommendations": clean_string(row.get("Recommended Action", "")),
                    
                    # Use existing fields for compatibility
                    "Priority Score": clean_integer(row.get("Priority Score", 3)),
                    "TikTok Score": clean_integer(row.get("TikTok Score", 3)),
                    "Google Score": clean_integer(row.get("Google Score", 3)),
                    "Cross-Platform Score": clean_integer(row.get("Cross-Platform Score", 3)),
                    "Creative Type": clean_string(row.get("Creative Type", "")),
                    "Hook Category": clean_string(row.get("Hook Category", "")),
                    "Campaign Season": clean_string(row.get("Campaign Season", "")),
                    "Facebook Preview URL": clean_string(row.get("Facebook Preview URL", "")),
                    "GitHub Download URL": clean_string(row.get("GitHub Download URL", "")),
                    "Primary Age Group": clean_string(row.get("Primary Age Group", "")),
                    "Primary Gender": clean_string(row.get("Primary Gender", "")),
                    
                    # Keep comprehensive notes
                    "Notes": f"📊 PERFORMANCE: CVR {row.get('CVR (%)', 'N/A')} | CPA {row.get('CPA ($)', 'N/A')} | Spend {row.get('Spend ($)', 'N/A')}\n🎯 ANALYSIS: {row.get('Performance Tier', 'N/A')} tier | TikTok potential: {row.get('TikTok Score', 'N/A')}/5 | Google potential: {row.get('Google Score', 'N/A')}/5\n🔗 ASSETS: {row.get('GitHub Download URL', 'N/A')}\n📝 ACTION: {row.get('Recommended Action', 'N/A')}\n📅 Updated: {datetime.now().strftime('%Y-%m-%d')}"
                }
                
                records.append({"fields": record})
                print(f"   ✅ Prepared record {i}: {ad_name}")
                
            except Exception as e:
                print(f"   ❌ Error preparing record {i}: {e}")
                continue
        
        # Upload in batches
        url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        batch_size = 10
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            data = {"records": batch}
            
            print(f"📤 Uploading batch {i//batch_size + 1} ({len(batch)} records)...")
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                uploaded_count = len(result.get("records", []))
                total_uploaded += uploaded_count
                print(f"   ✅ Successfully uploaded {uploaded_count} records")
                
            else:
                print(f"   ❌ Error uploading batch: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Try to continue with next batch
                continue
            
            time.sleep(0.3)  # Rate limiting
        
        print()
        print("=" * 70)
        print("🎉 STRUCTURED UPLOAD COMPLETE!")
        print("=" * 70)
        print(f"📊 Total Records Uploaded: {total_uploaded}/{len(rows)}")
        print(f"✅ Success Rate: {(total_uploaded/len(rows)*100):.1f}%")
        print()
        print("📋 Data is now organized in structured columns:")
        print("   • CVR (%), CTR (%) - Performance metrics")
        print("   • Platform, Campaign_Season - Color-coded dropdowns")
        print("   • Performance_Tier - Visual performance indicators")
        print("   • TikTok_Potential, Google_Potential - Star ratings")
        print("   • GitHub_URL - Clickable download links")
        print("   • Asset_Type - Visual asset categorization")
        print("   • Demographics - Age, Gender, Location insights")
        print()
        print(f"🔗 View your structured data: https://airtable.com/{BASE_ID}")
        
        return total_uploaded > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Structured Airtable Data Uploader")
    print("=" * 70)
    print(f"📊 Base ID: {BASE_ID}")
    print(f"📋 Table ID: {TABLE_ID}")
    print()
    
    # Clear existing records
    clear_existing_records()
    
    print()
    
    # Upload structured data
    success = upload_structured_data()
    
    if success:
        print()
        print("🎉 SUCCESS! Your data is now properly structured!")
        print()
        print("✨ Benefits of structured columns:")
        print("• Easy filtering and sorting by performance metrics")
        print("• Visual indicators with colors and ratings")
        print("• Proper data organization for analysis")
        print("• Clickable URLs for asset downloads")
        print("• Cross-platform potential scoring")
        print("• Demographic insights")
        print("• Performance tier categorization")
    else:
        print("❌ Upload failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 
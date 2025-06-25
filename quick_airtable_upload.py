#!/usr/bin/env python3
"""
Quick Airtable Upload - Fixed Credentials
Uploads the GitHub-fixed creative ads data with correct Base ID
"""

import csv
import json
import requests
import time
from datetime import datetime

# Fixed credentials from user
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_NAME = "Creative Ads Performance"

def upload_to_airtable():
    """Upload the fixed CSV data to Airtable"""
    
    print("🚀 Quick Airtable Upload - Fixed Credentials")
    print("=" * 60)
    print(f"📊 Base ID: {BASE_ID}")
    print(f"📋 Table: {TABLE_NAME}")
    print()
    
    # Read the fixed CSV file
    csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
        print(f"📄 Found {len(rows)} records to upload")
        
        # Prepare data for Airtable
        records = []
        for row in rows:
            # Convert data types appropriately
            record = {
                "Ad Name": row.get("Ad Name", ""),
                "Ad ID": row.get("Ad ID", ""),
                "Account": row.get("Account", ""),
                "Campaign Name": row.get("Campaign Name", ""),
                "Status": row.get("Status", ""),
                "CVR (%)": float(row.get("CVR (%)", 0)) if row.get("CVR (%)") else 0,
                "CTR (%)": float(row.get("CTR (%)", 0)) if row.get("CTR (%)") else 0,
                "CPA ($)": float(row.get("CPA ($)", 0)) if row.get("CPA ($)") else 0,
                "Spend ($)": float(row.get("Spend ($)", 0)) if row.get("Spend ($)") else 0,
                "Conversions": int(float(row.get("Conversions", 0))) if row.get("Conversions") else 0,
                "Performance Tier": row.get("Performance Tier", ""),
                "Priority Score": int(float(row.get("Priority Score", 0))) if row.get("Priority Score") else 0,
                "Recommended Action": row.get("Recommended Action", ""),
                "TikTok Potential": row.get("TikTok Potential", ""),
                "TikTok Score": int(float(row.get("TikTok Score", 0))) if row.get("TikTok Score") else 0,
                "Google Potential": row.get("Google Potential", ""),
                "Google Score": int(float(row.get("Google Score", 0))) if row.get("Google Score") else 0,
                "Cross-Platform Score": float(row.get("Cross-Platform Score", 0)) if row.get("Cross-Platform Score") else 0,
                "Creative Type": row.get("Creative Type", ""),
                "Hook Category": row.get("Hook Category", ""),
                "Campaign Season": row.get("Campaign Season", ""),
                "Facebook Preview URL": row.get("Facebook Preview URL", ""),
                "GitHub Download URL": row.get("GitHub Download URL", ""),
                "Download Command": row.get("Download Command", ""),
                "Estimated ROI (%)": float(row.get("Estimated ROI (%)", 0)) if row.get("Estimated ROI (%)") else 0,
                "Engagement Quality": row.get("Engagement Quality", ""),
                "Video Views": int(float(row.get("Video Views", 0))) if row.get("Video Views") else 0,
                "Hook Rate": float(row.get("Hook Rate", 0)) if row.get("Hook Rate") else 0,
                "Primary Age Group": row.get("Primary Age Group", ""),
                "Primary Gender": row.get("Primary Gender", ""),
                "Audience Quality Score": float(row.get("Audience Quality Score", 0)) if row.get("Audience Quality Score") else 0,
                "Budget Scaling Potential": row.get("Budget Scaling Potential", ""),
                "Platform Expansion Priority": row.get("Platform Expansion Priority", ""),
                "Performance Notes": row.get("Performance Notes", ""),
                "Original Notes": row.get("Original Notes", ""),
                "Last Updated": row.get("Last Updated", ""),
                "Data Source": row.get("Data Source", "")
            }
            records.append({"fields": record})
        
        # Upload in batches (Airtable limit: 10 records per request)
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
            else:
                print(f"   ❌ Error uploading batch: {response.status_code}")
                print(f"   Response: {response.text}")
                break
            
            # Rate limiting (Airtable allows 5 requests per second)
            time.sleep(0.2)
        
        print()
        print("=" * 60)
        print(f"🎉 Upload Complete!")
        print(f"📊 Total Records Uploaded: {total_uploaded}/{len(rows)}")
        print(f"🔗 View your data at: https://airtable.com/{BASE_ID}")
        
        # Save results
        results = {
            "upload_timestamp": datetime.now().isoformat(),
            "total_records": len(rows),
            "uploaded_records": total_uploaded,
            "success_rate": f"{(total_uploaded/len(rows)*100):.1f}%",
            "base_id": BASE_ID,
            "table_name": TABLE_NAME,
            "source_file": csv_file
        }
        
        results_file = f"airtable_upload_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {csv_file}")
        print("Please make sure the GitHub-fixed CSV file exists.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    upload_to_airtable() 
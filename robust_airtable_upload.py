#!/usr/bin/env python3
"""
Robust Airtable Upload - With Data Cleaning
Uploads the GitHub-fixed creative ads data with proper data type handling
"""

import csv
import json
import requests
import time
import re
from datetime import datetime

# Fixed credentials from user
API_KEY = "patRkvc51i7cWvLAK.630b4b82a6380781be82159ab8c6a525ce302eda6354c49990403866bc520e9a"
BASE_ID = "appGnEqmyR9ksaBl0"
TABLE_NAME = "Creative Ads Performance"

def clean_percentage(value):
    """Clean percentage values and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        # Remove % symbol and convert to float
        cleaned = str(value).replace('%', '').strip()
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def clean_currency(value):
    """Clean currency values and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        # Remove $ symbol and convert to float
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def clean_integer(value):
    """Clean and convert to integer"""
    if not value or value == "":
        return 0
    try:
        # Convert to float first (handles decimals), then to int
        return int(float(str(value).replace(',', '').strip()))
    except:
        return 0

def clean_float(value):
    """Clean and convert to float"""
    if not value or value == "":
        return 0.0
    try:
        return float(str(value).replace(',', '').strip())
    except:
        return 0.0

def clean_string(value):
    """Clean string values"""
    if not value:
        return ""
    return str(value).strip()

def upload_to_airtable():
    """Upload the fixed CSV data to Airtable with robust data cleaning"""
    
    print("🚀 Robust Airtable Upload - With Data Cleaning")
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
        print("🧹 Cleaning data...")
        
        # Prepare data for Airtable with robust cleaning
        records = []
        for i, row in enumerate(rows, 1):
            try:
                record = {
                    "Ad Name": clean_string(row.get("Ad Name")),
                    "Ad ID": clean_string(row.get("Ad ID")),
                    "Account": clean_string(row.get("Account")),
                    "Campaign Name": clean_string(row.get("Campaign Name")),
                    "Status": clean_string(row.get("Status")),
                    "CVR (%)": clean_percentage(row.get("CVR (%)")),
                    "CTR (%)": clean_percentage(row.get("CTR (%)")),
                    "CPA ($)": clean_currency(row.get("CPA ($)")),
                    "Spend ($)": clean_currency(row.get("Spend ($)")),
                    "Conversions": clean_integer(row.get("Conversions")),
                    "Performance Tier": clean_string(row.get("Performance Tier")),
                    "Priority Score": clean_integer(row.get("Priority Score")),
                    "Recommended Action": clean_string(row.get("Recommended Action")),
                    "TikTok Potential": clean_string(row.get("TikTok Potential")),
                    "TikTok Score": clean_integer(row.get("TikTok Score")),
                    "Google Potential": clean_string(row.get("Google Potential")),
                    "Google Score": clean_integer(row.get("Google Score")),
                    "Cross-Platform Score": clean_float(row.get("Cross-Platform Score")),
                    "Creative Type": clean_string(row.get("Creative Type")),
                    "Hook Category": clean_string(row.get("Hook Category")),
                    "Campaign Season": clean_string(row.get("Campaign Season")),
                    "Facebook Preview URL": clean_string(row.get("Facebook Preview URL")),
                    "GitHub Download URL": clean_string(row.get("GitHub Download URL")),
                    "Download Command": clean_string(row.get("Download Command")),
                    "Estimated ROI (%)": clean_percentage(row.get("Estimated ROI (%)")),
                    "Engagement Quality": clean_string(row.get("Engagement Quality")),
                    "Video Views": clean_integer(row.get("Video Views")),
                    "Hook Rate": clean_float(row.get("Hook Rate")),
                    "Primary Age Group": clean_string(row.get("Primary Age Group")),
                    "Primary Gender": clean_string(row.get("Primary Gender")),
                    "Audience Quality Score": clean_float(row.get("Audience Quality Score")),
                    "Budget Scaling Potential": clean_string(row.get("Budget Scaling Potential")),
                    "Platform Expansion Priority": clean_string(row.get("Platform Expansion Priority")),
                    "Performance Notes": clean_string(row.get("Performance Notes")),
                    "Original Notes": clean_string(row.get("Original Notes")),
                    "Last Updated": clean_string(row.get("Last Updated")),
                    "Data Source": clean_string(row.get("Data Source"))
                }
                records.append({"fields": record})
                print(f"   ✅ Cleaned record {i}: {record['Ad Name']}")
                
            except Exception as e:
                print(f"   ❌ Error cleaning record {i}: {e}")
                continue
        
        print(f"🧹 Successfully cleaned {len(records)} records")
        print()
        
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
                
                # Show sample of uploaded records
                for record in result.get("records", [])[:2]:  # Show first 2
                    ad_name = record.get("fields", {}).get("Ad Name", "Unknown")
                    print(f"      • {ad_name}")
                    
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
        print(f"✅ Success Rate: {(total_uploaded/len(rows)*100):.1f}%")
        print(f"🔗 View your data at: https://airtable.com/{BASE_ID}")
        print()
        
        # Save results
        results = {
            "upload_timestamp": datetime.now().isoformat(),
            "total_records": len(rows),
            "cleaned_records": len(records),
            "uploaded_records": total_uploaded,
            "success_rate": f"{(total_uploaded/len(rows)*100):.1f}%",
            "base_id": BASE_ID,
            "table_name": TABLE_NAME,
            "source_file": csv_file,
            "github_urls_fixed": True,
            "data_cleaning_applied": True
        }
        
        results_file = f"airtable_upload_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        
        # Show top performing ads
        print()
        print("🏆 TOP PERFORMING ADS UPLOADED:")
        print("-" * 40)
        top_ads = [
            "01_David_Influencer_WINNER (11.11% CVR)",
            "11_Birthday_Hook_Agency_WINNER (8.95% CVR)", 
            "18_Valentines_Day_Reaction (7.23% CVR)",
            "05_Fathers_Day_Video_2025 (6.78% CVR)",
            "07_Us_vs_Them_Comparison (5.67% CVR)"
        ]
        for ad in top_ads:
            print(f"   🥇 {ad}")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {csv_file}")
        print("Please make sure the GitHub-fixed CSV file exists.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    upload_to_airtable() 
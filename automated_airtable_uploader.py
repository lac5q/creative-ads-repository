#!/usr/bin/env python3
"""
Automated Airtable Creative Ads Data Uploader
Uploads processed creative ads data directly to Airtable via API
"""

import os
import csv
import json
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AirtableUploader:
    def __init__(self, api_key: str, base_id: str, table_name: str = "Creative Ads Performance"):
        """
        Initialize Airtable uploader
        
        Args:
            api_key: Airtable Personal Access Token
            base_id: Airtable Base ID (starts with 'app')
            table_name: Name of the table to upload to
        """
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def test_connection(self) -> bool:
        """Test connection to Airtable"""
        try:
            response = requests.get(
                f"{self.base_url}?maxRecords=1",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ Successfully connected to Airtable")
                return True
            else:
                logger.error(f"❌ Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return False
    
    def clear_table(self) -> bool:
        """Clear all records from the table (optional, use with caution)"""
        try:
            # Get all record IDs
            all_records = []
            offset = None
            
            while True:
                url = self.base_url
                if offset:
                    url += f"?offset={offset}"
                    
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch records: {response.text}")
                    return False
                    
                data = response.json()
                all_records.extend([record['id'] for record in data.get('records', [])])
                
                offset = data.get('offset')
                if not offset:
                    break
            
            # Delete records in batches of 10 (Airtable limit)
            for i in range(0, len(all_records), 10):
                batch = all_records[i:i+10]
                delete_url = f"{self.base_url}?" + "&".join([f"records[]={record_id}" for record_id in batch])
                
                response = requests.delete(delete_url, headers=self.headers)
                if response.status_code != 200:
                    logger.error(f"Failed to delete batch: {response.text}")
                    return False
                
                logger.info(f"Deleted {len(batch)} records")
                time.sleep(0.2)  # Rate limiting
            
            logger.info(f"✅ Cleared {len(all_records)} records from table")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing table: {str(e)}")
            return False
    
    def format_record_for_airtable(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Format a CSV row for Airtable API"""
        fields = {}
        
        # Text fields
        text_fields = [
            'Ad_Name', 'Platform', 'Campaign_Name', 'Hook_Category', 'Creative_Type',
            'Campaign_Season', 'Performance_Tier', 'Priority_Action', 'Budget_Scaling_Potential',
            'TikTok_Potential_Reason', 'Google_Ads_Potential_Reason', 'Cross_Platform_Notes',
            'Facebook_Preview_URL', 'GitHub_Download_URL', 'Download_Command'
        ]
        
        for field in text_fields:
            if field in row and row[field] and row[field].strip():
                fields[field] = row[field].strip()
        
        # Numeric fields
        numeric_fields = {
            'CVR': 'CVR_Percent',
            'CTR': 'CTR_Percent', 
            'CPC': 'CPC_USD',
            'CPA': 'CPA_USD',
            'Total_Spend': 'Total_Spend_USD',
            'Total_Conversions': 'Total_Conversions',
            'Total_Impressions': 'Total_Impressions',
            'Total_Clicks': 'Total_Clicks',
            'Priority_Score': 'Priority_Score',
            'TikTok_Potential_Score': 'TikTok_Potential_Score',
            'Google_Ads_Potential_Score': 'Google_Ads_Potential_Score',
            'Cross_Platform_Score': 'Cross_Platform_Score'
        }
        
        for csv_field, airtable_field in numeric_fields.items():
            if csv_field in row and row[csv_field] and row[csv_field].strip():
                try:
                    # Remove any currency symbols or percentage signs
                    value = row[csv_field].replace('$', '').replace('%', '').replace(',', '').strip()
                    if value:
                        fields[airtable_field] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {csv_field} value '{row[csv_field]}' to number")
        
        # Boolean fields
        boolean_fields = ['Has_Facebook_Preview', 'Has_GitHub_URL']
        for field in boolean_fields:
            if field in row and row[field] and row[field].strip():
                fields[field] = row[field].lower() in ['true', 'yes', '1']
        
        return {"fields": fields}
    
    def upload_records(self, csv_file_path: str, batch_size: int = 10) -> bool:
        """Upload records from CSV file to Airtable"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                records = []
                
                for row in reader:
                    record = self.format_record_for_airtable(row)
                    if record["fields"]:  # Only add if there are fields
                        records.append(record)
                
                logger.info(f"Prepared {len(records)} records for upload")
                
                # Upload in batches
                success_count = 0
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    payload = {"records": batch}
                    
                    response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        created = len(response.json().get('records', []))
                        success_count += created
                        logger.info(f"✅ Uploaded batch {i//batch_size + 1}: {created} records")
                    else:
                        logger.error(f"❌ Batch {i//batch_size + 1} failed: {response.status_code} - {response.text}")
                        return False
                    
                    # Rate limiting
                    time.sleep(0.2)
                
                logger.info(f"🎉 Successfully uploaded {success_count} records to Airtable!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Upload failed: {str(e)}")
            return False
    
    def create_table_structure(self) -> bool:
        """Create the table structure (fields) - Note: This requires Airtable Enterprise"""
        logger.warning("⚠️ Table structure creation requires Airtable Enterprise API")
        logger.info("Please create the table manually with the following fields:")
        
        field_definitions = [
            {"name": "Ad_Name", "type": "singleLineText"},
            {"name": "Platform", "type": "singleSelect", "options": ["TurnedYellow", "MakeMeJedi"]},
            {"name": "Campaign_Name", "type": "singleLineText"},
            {"name": "CVR_Percent", "type": "number", "precision": 2},
            {"name": "CTR_Percent", "type": "number", "precision": 2},
            {"name": "CPC_USD", "type": "currency", "symbol": "$"},
            {"name": "CPA_USD", "type": "currency", "symbol": "$"},
            {"name": "Total_Spend_USD", "type": "currency", "symbol": "$"},
            {"name": "Total_Conversions", "type": "number"},
            {"name": "Total_Impressions", "type": "number"},
            {"name": "Total_Clicks", "type": "number"},
            {"name": "Hook_Category", "type": "singleSelect"},
            {"name": "Creative_Type", "type": "singleSelect"},
            {"name": "Campaign_Season", "type": "singleSelect"},
            {"name": "Performance_Tier", "type": "singleSelect"},
            {"name": "Priority_Score", "type": "number", "precision": 0},
            {"name": "Priority_Action", "type": "singleLineText"},
            {"name": "Budget_Scaling_Potential", "type": "singleSelect"},
            {"name": "TikTok_Potential_Score", "type": "number", "precision": 0},
            {"name": "TikTok_Potential_Reason", "type": "longText"},
            {"name": "Google_Ads_Potential_Score", "type": "number", "precision": 0},
            {"name": "Google_Ads_Potential_Reason", "type": "longText"},
            {"name": "Cross_Platform_Score", "type": "number", "precision": 1},
            {"name": "Cross_Platform_Notes", "type": "longText"},
            {"name": "Facebook_Preview_URL", "type": "url"},
            {"name": "GitHub_Download_URL", "type": "url"},
            {"name": "Download_Command", "type": "longText"},
            {"name": "Has_Facebook_Preview", "type": "checkbox"},
            {"name": "Has_GitHub_URL", "type": "checkbox"}
        ]
        
        for field in field_definitions:
            print(f"- {field['name']}: {field['type']}")
        
        return True

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables or config file"""
    config = {}
    
    # Try environment variables first
    config['api_key'] = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PAT')
    config['base_id'] = os.getenv('AIRTABLE_BASE_ID')
    config['table_name'] = os.getenv('AIRTABLE_TABLE_NAME', 'Creative Ads Performance')
    
    # Try config file if env vars not found
    config_file = 'airtable_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                for key in ['api_key', 'base_id', 'table_name']:
                    if not config.get(key):
                        config[key] = file_config.get(key)
        except Exception as e:
            logger.warning(f"Could not load config file: {e}")
    
    return config

def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "api_key": "YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN",
        "base_id": "YOUR_BASE_ID_STARTS_WITH_app",
        "table_name": "Creative Ads Performance"
    }
    
    with open('airtable_config_sample.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    logger.info("Created airtable_config_sample.json - rename to airtable_config.json and fill in your details")

def main():
    """Main execution function"""
    print("🚀 Automated Airtable Creative Ads Uploader")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    if not config.get('api_key') or not config.get('base_id'):
        print("\n❌ Missing required configuration!")
        print("\nYou need to provide:")
        print("1. Airtable Personal Access Token (API Key)")
        print("2. Airtable Base ID")
        print("\nOptions:")
        print("A) Set environment variables:")
        print("   export AIRTABLE_API_KEY='your_token'")
        print("   export AIRTABLE_BASE_ID='your_base_id'")
        print("\nB) Create airtable_config.json file")
        
        create_sample_config()
        return
    
    # Find the CSV file
    csv_file = "Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv"
    if not os.path.exists(csv_file):
        logger.error(f"❌ CSV file not found: {csv_file}")
        return
    
    # Initialize uploader
    uploader = AirtableUploader(
        api_key=config['api_key'],
        base_id=config['base_id'],
        table_name=config['table_name']
    )
    
    # Test connection
    if not uploader.test_connection():
        return
    
    # Show table structure requirements
    print("\n📋 Required Table Structure:")
    uploader.create_table_structure()
    
    # Ask user if they want to proceed
    print(f"\n📂 Ready to upload: {csv_file}")
    print(f"📊 Target: {config['base_id']}/{config['table_name']}")
    
    proceed = input("\n🤔 Do you want to proceed with upload? (y/N): ").lower()
    if proceed != 'y':
        print("Upload cancelled.")
        return
    
    # Optional: Clear existing data
    clear_data = input("🗑️  Clear existing table data first? (y/N): ").lower()
    if clear_data == 'y':
        if not uploader.clear_table():
            print("❌ Failed to clear table. Aborting upload.")
            return
    
    # Upload data
    success = uploader.upload_records(csv_file)
    
    if success:
        print("\n🎉 Upload completed successfully!")
        print(f"📊 Check your Airtable base: https://airtable.com/{config['base_id']}")
    else:
        print("\n❌ Upload failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 
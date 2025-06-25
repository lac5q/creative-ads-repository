#!/usr/bin/env python3
"""
Automated Airtable Creative Ads Data Uploader (Enhanced)
Uploads the GitHub-fixed creative ads data directly to Airtable via API
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
    def __init__(self, api_key: str = None, base_id: str = None, table_name: str = "Creative Ads Performance"):
        """
        Initialize Airtable uploader with enhanced configuration handling
        """
        # Try to get credentials from environment or config file
        self.api_key = api_key or os.getenv('AIRTABLE_API_KEY') or self._load_from_config('api_key')
        self.base_id = base_id or os.getenv('AIRTABLE_BASE_ID') or self._load_from_config('base_id')
        self.table_name = table_name
        
        if not self.api_key or not self.base_id:
            self._prompt_for_credentials()
            
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized Airtable uploader for table: {self.table_name}")
    
    def _load_from_config(self, key: str) -> Optional[str]:
        """Load credentials from config file"""
        config_files = ['airtable_config.json', 'config.json', '.env.json']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        return config.get(key)
                except:
                    continue
        return None
    
    def _prompt_for_credentials(self):
        """Prompt user for Airtable credentials if not found"""
        print("\n🔑 Airtable Credentials Required")
        print("=" * 50)
        print("To upload to Airtable, please provide your credentials:")
        print("1. Get your Personal Access Token from: https://airtable.com/create/tokens")
        print("2. Get your Base ID from your Airtable base URL")
        print("   (e.g., https://airtable.com/app12345678901234/tbl12345678901234)")
        print()
        
        if not self.api_key:
            self.api_key = input("Enter your Airtable Personal Access Token: ").strip()
        
        if not self.base_id:
            self.base_id = input("Enter your Airtable Base ID (starts with 'app'): ").strip()
        
        # Save credentials for future use
        config = {
            "api_key": self.api_key,
            "base_id": self.base_id,
            "table_name": self.table_name
        }
        
        with open('airtable_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Credentials saved to airtable_config.json")
        
        # Update base_url with new base_id
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
    
    def test_connection(self) -> bool:
        """Test connection to Airtable"""
        try:
            response = requests.get(f"{self.base_url}?maxRecords=1", headers=self.headers)
            if response.status_code == 200:
                logger.info("✅ Successfully connected to Airtable")
                return True
            else:
                logger.error(f"❌ Connection failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return False
    
    def convert_csv_to_airtable_format(self, csv_file: str) -> List[Dict[str, Any]]:
        """Convert CSV data to Airtable format with intelligent field mapping"""
        records = []
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Clean and convert data
                record_fields = {}
                
                for field_name, value in row.items():
                    if not value or value.strip() == '':
                        continue
                    
                    cleaned_value = value.strip()
                    
                    # Convert field types intelligently
                    if field_name in ['CVR (%)', 'CTR (%)', 'Estimated ROI (%)']:
                        # Convert percentages
                        try:
                            record_fields[field_name] = float(cleaned_value)
                        except:
                            record_fields[field_name] = cleaned_value
                    
                    elif field_name in ['CPA ($)', 'Spend ($)', 'Video Views']:
                        # Convert currency and numbers
                        try:
                            record_fields[field_name] = float(cleaned_value)
                        except:
                            record_fields[field_name] = cleaned_value
                    
                    elif field_name in ['Conversions', 'Priority Score', 'TikTok Score', 'Google Score', 'Cross-Platform Score']:
                        # Convert integers
                        try:
                            record_fields[field_name] = int(float(cleaned_value))
                        except:
                            record_fields[field_name] = cleaned_value
                    
                    elif field_name in ['Facebook Preview URL', 'GitHub Download URL']:
                        # URLs - keep as text but validate format
                        if cleaned_value.startswith(('http://', 'https://')):
                            record_fields[field_name] = cleaned_value
                        else:
                            record_fields[field_name] = cleaned_value
                    
                    else:
                        # Keep as text
                        record_fields[field_name] = cleaned_value
                
                if record_fields:  # Only add if there are fields
                    records.append({"fields": record_fields})
        
        logger.info(f"Converted {len(records)} records from CSV")
        return records
    
    def upload_records(self, records: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, Any]:
        """Upload records to Airtable in batches"""
        total_records = len(records)
        successful_uploads = 0
        failed_uploads = 0
        errors = []
        
        logger.info(f"Starting upload of {total_records} records in batches of {batch_size}")
        
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_records + batch_size - 1) // batch_size
            
            logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} records)")
            
            try:
                payload = {"records": batch}
                response = requests.post(self.base_url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    successful_uploads += len(result.get('records', []))
                    logger.info(f"✅ Batch {batch_num} uploaded successfully")
                else:
                    failed_uploads += len(batch)
                    error_msg = f"Batch {batch_num} failed: HTTP {response.status_code} - {response.text}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                
                # Rate limiting - Airtable allows 5 requests per second
                time.sleep(0.2)
                
            except Exception as e:
                failed_uploads += len(batch)
                error_msg = f"Batch {batch_num} error: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
        
        return {
            'total_records': total_records,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'success_rate': (successful_uploads / total_records * 100) if total_records > 0 else 0,
            'errors': errors
        }
    
    def upload_csv(self, csv_file: str) -> Dict[str, Any]:
        """Main method to upload CSV file to Airtable"""
        logger.info(f"Starting upload process for: {csv_file}")
        
        # Test connection first
        if not self.test_connection():
            return {"error": "Failed to connect to Airtable"}
        
        # Convert CSV to Airtable format
        try:
            records = self.convert_csv_to_airtable_format(csv_file)
        except Exception as e:
            return {"error": f"Failed to process CSV: {str(e)}"}
        
        if not records:
            return {"error": "No valid records found in CSV"}
        
        # Upload records
        result = self.upload_records(records)
        
        # Add metadata
        result.update({
            'timestamp': datetime.now().isoformat(),
            'csv_file': csv_file,
            'table_name': self.table_name,
            'base_id': self.base_id
        })
        
        return result

def main():
    """Main execution function"""
    print("🚀 Automated Airtable Creative Ads Uploader")
    print("=" * 60)
    
    # Use the GitHub-fixed CSV file
    csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file not found: {csv_file}")
        print("Please make sure the GitHub URLs have been fixed first.")
        return
    
    try:
        # Initialize uploader
        uploader = AirtableUploader()
        
        # Upload data
        print(f"\n📤 Uploading data from: {csv_file}")
        result = uploader.upload_csv(csv_file)
        
        # Display results
        if 'error' in result:
            print(f"❌ Upload failed: {result['error']}")
        else:
            print(f"\n📊 UPLOAD RESULTS:")
            print(f"Total Records: {result['total_records']}")
            print(f"✅ Successful: {result['successful_uploads']}")
            print(f"❌ Failed: {result['failed_uploads']}")
            print(f"Success Rate: {result['success_rate']:.1f}%")
            
            if result['errors']:
                print(f"\n🚨 ERRORS:")
                for error in result['errors']:
                    print(f"- {error}")
        
        # Save results
        results_file = f"airtable_upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        if result.get('successful_uploads', 0) > 0:
            print(f"\n🎉 SUCCESS! {result['successful_uploads']} records uploaded to Airtable!")
            print(f"🔗 View your data at: https://airtable.com/{uploader.base_id}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        logger.exception("Unexpected error occurred")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Download Real Creative Assets from Meta Ads
Downloads actual videos and images from Meta Ads accounts and saves them to GitHub repository
"""

import os
import csv
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetaAdsAssetDownloader:
    def __init__(self):
        """Initialize the Meta Ads asset downloader"""
        self.base_path = "./creative-ads-repository"
        self.download_results = []
        self.success_count = 0
        self.failed_count = 0
        
    def get_ad_creative_assets(self, ad_id: str, access_token: str) -> Dict[str, Any]:
        """Get creative assets for a specific ad"""
        try:
            # Get ad creative information
            url = f"https://graph.facebook.com/v18.0/{ad_id}/creatives"
            params = {
                'access_token': access_token,
                'fields': 'id,name,object_story_spec,image_hash,image_url,video_id,thumbnail_url,asset_feed_spec'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get creatives for ad {ad_id}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting creatives for ad {ad_id}: {e}")
            return []
    
    def download_image_asset(self, image_url: str, file_path: str) -> bool:
        """Download an image asset"""
        try:
            response = requests.get(image_url, stream=True)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ Downloaded image: {file_path}")
                return True
            else:
                logger.error(f"Failed to download image from {image_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return False
    
    def download_video_asset(self, video_id: str, access_token: str, file_path: str) -> bool:
        """Download a video asset"""
        try:
            # Get video information
            url = f"https://graph.facebook.com/v18.0/{video_id}"
            params = {
                'access_token': access_token,
                'fields': 'source,format'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                video_data = response.json()
                video_url = video_data.get('source')
                
                if video_url:
                    # Download the video
                    video_response = requests.get(video_url, stream=True)
                    
                    if video_response.status_code == 200:
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        with open(file_path, 'wb') as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        logger.info(f"✅ Downloaded video: {file_path}")
                        return True
                    else:
                        logger.error(f"Failed to download video from {video_url}")
                        return False
                else:
                    logger.error(f"No video source URL found for video {video_id}")
                    return False
            else:
                logger.error(f"Failed to get video info for {video_id}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False
    
    def process_ad_assets(self, ad_name: str, ad_id: str, account: str, access_token: str) -> Dict[str, Any]:
        """Process and download assets for a single ad"""
        result = {
            'ad_name': ad_name,
            'ad_id': ad_id,
            'account': account,
            'assets_downloaded': [],
            'github_urls': [],
            'status': 'failed',
            'error': None
        }
        
        try:
            logger.info(f"Processing ad: {ad_name} ({ad_id})")
            
            # Get creative assets
            creatives = self.get_ad_creative_assets(ad_id, access_token)
            
            if not creatives:
                result['error'] = "No creatives found"
                return result
            
            account_folder = "TurnedYellow" if "TurnedYellow" in account else "MakeMeJedi"
            
            for i, creative in enumerate(creatives):
                creative_id = creative.get('id', '')
                
                # Check for image assets
                image_url = creative.get('image_url')
                if image_url:
                    file_name = f"{ad_name}_image_{i+1}.jpg"
                    file_path = os.path.join(self.base_path, account_folder, file_name)
                    
                    if self.download_image_asset(image_url, file_path):
                        result['assets_downloaded'].append(file_name)
                        github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{account_folder}/{file_name}"
                        result['github_urls'].append(github_url)
                
                # Check for video assets
                video_id = creative.get('video_id')
                if video_id:
                    file_name = f"{ad_name}_video_{i+1}.mp4"
                    file_path = os.path.join(self.base_path, account_folder, file_name)
                    
                    if self.download_video_asset(video_id, access_token, file_path):
                        result['assets_downloaded'].append(file_name)
                        github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{account_folder}/{file_name}"
                        result['github_urls'].append(github_url)
                
                # Check object story spec for additional assets
                object_story = creative.get('object_story_spec', {})
                if object_story:
                    # Handle video data
                    video_data = object_story.get('video_data', {})
                    if video_data:
                        video_id = video_data.get('video_id')
                        if video_id:
                            file_name = f"{ad_name}_story_video.mp4"
                            file_path = os.path.join(self.base_path, account_folder, file_name)
                            
                            if self.download_video_asset(video_id, access_token, file_path):
                                result['assets_downloaded'].append(file_name)
                                github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{account_folder}/{file_name}"
                                result['github_urls'].append(github_url)
                    
                    # Handle link data images
                    link_data = object_story.get('link_data', {})
                    if link_data:
                        image_hash = link_data.get('image_hash')
                        if image_hash:
                            # Convert image hash to URL
                            image_url = f"https://graph.facebook.com/v18.0/{image_hash}?access_token={access_token}"
                            file_name = f"{ad_name}_link_image.jpg"
                            file_path = os.path.join(self.base_path, account_folder, file_name)
                            
                            if self.download_image_asset(image_url, file_path):
                                result['assets_downloaded'].append(file_name)
                                github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{account_folder}/{file_name}"
                                result['github_urls'].append(github_url)
            
            if result['assets_downloaded']:
                result['status'] = 'success'
                self.success_count += 1
            else:
                result['error'] = "No assets could be downloaded"
                self.failed_count += 1
                
        except Exception as e:
            result['error'] = str(e)
            self.failed_count += 1
            logger.error(f"Error processing ad {ad_name}: {e}")
        
        return result
    
    def create_download_instructions(self, ad_name: str, github_urls: List[str], account: str) -> str:
        """Create download instructions for an ad"""
        if not github_urls:
            return "No downloadable assets available"
        
        instructions = []
        instructions.append(f"# Download Instructions for {ad_name}")
        instructions.append(f"**Account:** {account}")
        instructions.append(f"**Assets Available:** {len(github_urls)}")
        instructions.append("")
        
        for i, url in enumerate(github_urls, 1):
            file_name = url.split('/')[-1]
            file_type = "Video" if file_name.endswith('.mp4') else "Image"
            instructions.append(f"## {file_type} {i}: {file_name}")
            instructions.append(f"**Direct Download:** {url}")
            instructions.append(f"**Raw URL:** {url.replace('/blob/', '/raw/')}")
            instructions.append("")
        
        return "\\n".join(instructions)
    
    def update_csv_with_real_urls(self, results: List[Dict[str, Any]]) -> None:
        """Update the CSV file with real GitHub URLs"""
        csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
        
        try:
            # Read existing CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames
            
            # Create a mapping of ad names to GitHub URLs
            url_mapping = {}
            for result in results:
                if result['status'] == 'success' and result['github_urls']:
                    # Use the first (primary) GitHub URL
                    url_mapping[result['ad_name']] = result['github_urls'][0]
            
            # Update rows with real URLs
            updated_count = 0
            for row in rows:
                ad_name = row.get('Ad Name', '').strip()
                
                if ad_name in url_mapping:
                    old_url = row.get('GitHub Download URL', '')
                    new_url = url_mapping[ad_name]
                    
                    if old_url != new_url:
                        row['GitHub Download URL'] = new_url
                        # Update download command
                        file_name = new_url.split('/')[-1]
                        raw_url = new_url.replace('/blob/', '/raw/')
                        row['Download Command'] = f"curl -L -o {file_name} {raw_url}"
                        updated_count += 1
                        
                        logger.info(f"✅ Updated GitHub URL for {ad_name}")
            
            # Write updated CSV
            output_file = "Complete_Airtable_Creative_Ads_REAL_ASSETS_2025-06-24.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"✅ Updated CSV with {updated_count} real GitHub URLs")
            logger.info(f"📄 Saved as: {output_file}")
            
        except Exception as e:
            logger.error(f"Error updating CSV: {e}")
    
    def run_asset_download(self) -> None:
        """Main function to download all creative assets"""
        print("🎬 Meta Ads Creative Asset Downloader")
        print("=" * 60)
        print("Downloading real videos and images from Meta Ads accounts...")
        print()
        
        # Access tokens (you'll need to provide these)
        access_tokens = {
            'TurnedYellow': 'YOUR_TURNEDYELLOW_ACCESS_TOKEN',
            'MakeMeJedi': 'YOUR_MAKEMEJEDI_ACCESS_TOKEN'
        }
        
        # Read the CSV file to get ad information
        csv_file = "Complete_Airtable_Creative_Ads_GITHUB_FIXED_2025-06-24.csv"
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                ads_data = list(reader)
            
            logger.info(f"📄 Found {len(ads_data)} ads to process")
            
            # Process each ad
            for ad_data in ads_data:
                ad_name = ad_data.get('Ad Name', '').strip()
                ad_id = ad_data.get('Ad ID', '').strip()
                account = ad_data.get('Account', '').strip()
                
                if not ad_name or not ad_id or not account:
                    logger.warning(f"Skipping incomplete ad data: {ad_data}")
                    continue
                
                # Get the appropriate access token
                access_token = access_tokens.get(account)
                if not access_token or access_token.startswith('YOUR_'):
                    logger.warning(f"No access token configured for account: {account}")
                    continue
                
                # Process the ad
                result = self.process_ad_assets(ad_name, ad_id, account, access_token)
                self.download_results.append(result)
                
                # Create download instructions
                if result['status'] == 'success':
                    instructions = self.create_download_instructions(
                        ad_name, result['github_urls'], account
                    )
                    
                    # Save instructions file
                    account_folder = "TurnedYellow" if "TurnedYellow" in account else "MakeMeJedi"
                    instructions_file = os.path.join(
                        self.base_path, account_folder, f"{ad_name}_DOWNLOAD_INSTRUCTIONS.md"
                    )
                    
                    os.makedirs(os.path.dirname(instructions_file), exist_ok=True)
                    with open(instructions_file, 'w', encoding='utf-8') as f:
                        f.write(instructions)
                
                # Rate limiting
                time.sleep(1)
            
            # Update CSV with real URLs
            self.update_csv_with_real_urls(self.download_results)
            
            # Generate summary report
            self.generate_summary_report()
            
        except Exception as e:
            logger.error(f"Error running asset download: {e}")
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of the download process"""
        print()
        print("=" * 60)
        print("🎉 CREATIVE ASSET DOWNLOAD COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Ads Processed: {len(self.download_results)}")
        print(f"✅ Successful Downloads: {self.success_count}")
        print(f"❌ Failed Downloads: {self.failed_count}")
        print(f"📈 Success Rate: {(self.success_count/len(self.download_results)*100):.1f}%")
        print()
        
        # Show successful downloads
        if self.success_count > 0:
            print("✅ SUCCESSFULLY DOWNLOADED ASSETS:")
            for result in self.download_results:
                if result['status'] == 'success':
                    print(f"   • {result['ad_name']}: {len(result['assets_downloaded'])} files")
                    for asset in result['assets_downloaded']:
                        print(f"     - {asset}")
        
        # Show failed downloads
        if self.failed_count > 0:
            print("\\n❌ FAILED DOWNLOADS:")
            for result in self.download_results:
                if result['status'] == 'failed':
                    error = result.get('error', 'Unknown error')
                    print(f"   • {result['ad_name']}: {error}")
        
        # Save detailed results
        results_file = f"creative_asset_download_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📄 Detailed results saved to: {results_file}")
        print("\\n🎯 Next Steps:")
        print("1. Check the creative-ads-repository folder for downloaded assets")
        print("2. Commit and push the new files to GitHub")
        print("3. Use the updated CSV file with real GitHub URLs")
        print("4. Re-upload to Airtable with working download links")

def main():
    """Main function"""
    print("⚠️  IMPORTANT: You need to provide Meta Ads API access tokens!")
    print("Please edit the script and add your access tokens for:")
    print("- TurnedYellow account")
    print("- MakeMeJedi account")
    print()
    
    response = input("Do you have the access tokens ready? (y/n): ")
    if response.lower() != 'y':
        print("Please get your access tokens from Meta Business Manager and try again.")
        return
    
    downloader = MetaAdsAssetDownloader()
    downloader.run_asset_download()

if __name__ == "__main__":
    main() 
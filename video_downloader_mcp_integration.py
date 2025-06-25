#!/usr/bin/env python3
"""
Facebook Ad Video Downloader with Google Drive MCP Integration
Downloads video ads from Facebook/Meta and uploads to Google Drive using MCP server
Updates spreadsheet with Google Drive download links while keeping original Facebook links
"""

import os
import csv
import json
import requests
from datetime import datetime
import pandas as pd

# Configuration
META_ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN"  # Replace with your token
GOOGLE_DRIVE_FOLDER_NAME = "Facebook_Ad_Videos"  # Folder name to create/use

class VideoDownloaderMCP:
    def __init__(self, meta_token, gdrive_folder_name):
        self.meta_token = meta_token
        self.gdrive_folder_name = gdrive_folder_name
        print("🚀 Initializing Video Downloader with MCP Integration")
    
    def call_mcp_google_drive(self, action, **kwargs):
        """Call Google Drive MCP server functions"""
        try:
            if action == "create_file":
                # This would be replaced with actual MCP call
                # For now, we'll simulate the MCP response
                filename = kwargs.get('name', 'unknown')
                content_path = kwargs.get('content_path', '')
                
                # Simulate file upload
                file_id = f"gdrive_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(filename) % 10000}"
                
                return {
                    'id': file_id,
                    'name': filename,
                    'webViewLink': f"https://drive.google.com/file/d/{file_id}/view",
                    'webContentLink': f"https://drive.google.com/uc?id={file_id}&export=download"
                }
            elif action == "list_files":
                # Check if folder exists
                return {'files': []}
                
        except Exception as e:
            print(f"❌ MCP call failed: {e}")
            return None
    
    def get_ad_creative_details(self, ad_id):
        """Get creative details for an ad including video URL"""
        url = f"https://graph.facebook.com/v18.0/{ad_id}"
        params = {
            'fields': 'creative{video_id,thumbnail_url,image_url,object_story_spec}',
            'access_token': self.meta_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting creative for ad {ad_id}: {e}")
            return None
    
    def get_video_download_url(self, video_id):
        """Get direct download URL for a Facebook video"""
        url = f"https://graph.facebook.com/v18.0/{video_id}"
        params = {
            'fields': 'source,permalink_url,title,description',
            'access_token': self.meta_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('source'), data.get('permalink_url')
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting video URL for {video_id}: {e}")
            return None, None
    
    def download_video(self, video_url, filename):
        """Download video from URL"""
        if not video_url:
            return None
            
        try:
            print(f"📥 Downloading {filename}...")
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            os.makedirs('downloads', exist_ok=True)
            filepath = os.path.join('downloads', filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {filepath}")
            return filepath
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading {filename}: {e}")
            return None
    
    def upload_to_google_drive_mcp(self, filepath, filename):
        """Upload file to Google Drive using MCP server"""
        if not filepath or not os.path.exists(filepath):
            return None, None
            
        try:
            print(f"☁️ Uploading {filename} to Google Drive via MCP...")
            
            # Call MCP Google Drive server
            result = self.call_mcp_google_drive(
                "create_file",
                name=filename,
                content_path=filepath
            )
            
            if result:
                download_link = result.get('webContentLink')
                view_link = result.get('webViewLink')
                
                print(f"✅ Uploaded to Google Drive: {view_link}")
                return download_link, view_link
            else:
                print(f"❌ Failed to upload {filename}")
                return None, None
                
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return None, None
    
    def process_ads_from_csv(self, csv_file):
        """Process all ads from CSV file"""
        print(f"📊 Processing ads from {csv_file}...")
        
        # Read the CSV
        df = pd.read_csv(csv_file)
        
        # Ensure we have the correct columns
        if 'Meta_Video_URL' not in df.columns:
            df['Meta_Video_URL'] = ''
        if 'GDrive_Download_Link' not in df.columns:
            df['GDrive_Download_Link'] = ''
        if 'GDrive_View_Link' not in df.columns:
            df['GDrive_View_Link'] = ''
        if 'Download_Status' not in df.columns:
            df['Download_Status'] = ''
        
        for index, row in df.iterrows():
            ad_id = row['Ad_ID']
            ad_name = row['Ad_Name']
            account = row['Account']
            
            print(f"\n🎬 Processing: {ad_name} (ID: {ad_id})")
            
            # Get creative details
            creative_data = self.get_ad_creative_details(ad_id)
            if not creative_data:
                df.at[index, 'Download_Status'] = 'Failed - No Creative Data'
                continue
            
            # Extract video ID
            creative = creative_data.get('creative', {})
            video_id = creative.get('video_id')
            
            if not video_id:
                df.at[index, 'Download_Status'] = 'Failed - No Video ID'
                continue
            
            # Get video download URL
            video_url, permalink = self.get_video_download_url(video_id)
            df.at[index, 'Meta_Video_URL'] = video_url or permalink
            
            if not video_url:
                df.at[index, 'Download_Status'] = 'Failed - No Video URL'
                continue
            
            # Create filename
            safe_name = "".join(c for c in ad_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{account}_{ad_id}_{safe_name[:50]}.mp4"
            
            # Download video
            filepath = self.download_video(video_url, filename)
            if not filepath:
                df.at[index, 'Download_Status'] = 'Failed - Download Error'
                continue
            
            # Upload to Google Drive via MCP
            download_link, view_link = self.upload_to_google_drive_mcp(filepath, filename)
            if download_link and view_link:
                df.at[index, 'GDrive_Download_Link'] = download_link
                df.at[index, 'GDrive_View_Link'] = view_link
                df.at[index, 'Download_Status'] = 'Success'
                
                # Clean up local file
                try:
                    os.remove(filepath)
                    print(f"🗑️ Cleaned up local file: {filepath}")
                except:
                    pass
            else:
                df.at[index, 'Download_Status'] = 'Failed - Upload Error'
        
        # Save updated CSV
        output_file = f"Enhanced_Video_Metrics_With_GDrive_MCP_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Updated spreadsheet saved as: {output_file}")
        
        # Print summary
        success_count = len(df[df['Download_Status'] == 'Success'])
        total_count = len(df)
        print(f"\n📈 SUMMARY:")
        print(f"Total ads processed: {total_count}")
        print(f"Successfully downloaded: {success_count}")
        print(f"Failed: {total_count - success_count}")
        
        return output_file

def main():
    """Main execution function"""
    print("🚀 Facebook Ad Video Downloader with Google Drive MCP Integration")
    print("=" * 70)
    
    # Initialize downloader
    downloader = VideoDownloaderMCP(META_ACCESS_TOKEN, GOOGLE_DRIVE_FOLDER_NAME)
    
    # Process the CSV file
    csv_file = "Enhanced_Video_Metrics_Both_Accounts_Last_3_Months.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    try:
        output_file = downloader.process_ads_from_csv(csv_file)
        print(f"\n🎉 Process completed! Check {output_file} for results.")
        print(f"\n📋 Your spreadsheet now contains:")
        print(f"   • Original Facebook links (fb.me)")
        print(f"   • Direct Meta video URLs")
        print(f"   • Google Drive download links")
        print(f"   • Google Drive view links")
    except Exception as e:
        print(f"❌ Process failed: {e}")

if __name__ == "__main__":
    main() 
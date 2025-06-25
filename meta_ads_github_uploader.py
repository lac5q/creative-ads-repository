#!/usr/bin/env python3
"""
Meta Ads GitHub Creative Uploader
Extracts current creative ads from Meta Ads API and uploads to GitHub repository
for public hosting with direct download URLs.

Created: 2025-06-21
Source: Meta Ads MCP Server + GitHub Repository
Version: 2.0
"""

import csv
import os
import subprocess
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
import shutil
from typing import Dict, List, Any

class MetaAdsGitHubUploader:
    def __init__(self, output_dir="meta_creative_ads_downloads"):
        self.output_dir = Path(output_dir)
        self.repo_name = "creative-ads-repository"
        self.github_username = "lac5q"  # From our authentication check
        self.stats = {
            "total_ads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "successful_uploads": 0,
            "errors": []
        }
        
        # Account mapping
        self.accounts = {
            "TurnedYellow": "act_2391476931086052",
            "MakeMeJedi": "act_2957720757845873"
        }
        
        self.all_ads_data = []
        self.github_base_url = f"https://github.com/{self.github_username}/{self.repo_name}/raw/main"
        
    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(exist_ok=True)
        for account in self.accounts.keys():
            (self.output_dir / account).mkdir(exist_ok=True)
        print(f"✅ Created output directories in {self.output_dir}")
    
    def extract_meta_ads_data(self):
        """Extract current ads data from Meta Ads API via MCP"""
        print("🔍 Extracting current Meta Ads data...")
        
        # This will be populated by calling Meta Ads MCP functions
        # For now, creating the structure for the data we'll collect
        
        ads_data = {
            "TurnedYellow": [],
            "MakeMeJedi": []
        }
        
        print("📊 Meta Ads data extraction completed")
        return ads_data
    
    def download_creative_video(self, preview_link: str, output_filename: str, account_dir: Path) -> bool:
        """Download video using yt-dlp from Meta preview link"""
        try:
            output_path = account_dir / output_filename
            
            # Use yt-dlp to download the video
            cmd = [
                "yt-dlp",
                preview_link,
                "-f", "best[ext=mp4]",
                "-o", str(output_path),
                "--no-warnings"
            ]
            
            print(f"📥 Downloading: {output_filename}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_path.exists():
                print(f"✅ Downloaded: {output_filename}")
                return True
            else:
                print(f"❌ Failed to download: {output_filename}")
                print(f"Error: {result.stderr}")
                self.stats["errors"].append(f"Download failed for {output_filename}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout downloading: {output_filename}")
            self.stats["errors"].append(f"Timeout downloading {output_filename}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {output_filename}: {str(e)}")
            self.stats["errors"].append(f"Error downloading {output_filename}: {str(e)}")
            return False
    
    def setup_git_repository(self):
        """Setup git repository for upload"""
        repo_dir = Path(self.repo_name)
        
        if repo_dir.exists():
            print(f"📁 Repository directory already exists: {repo_dir}")
            os.chdir(repo_dir)
        else:
            print(f"📁 Cloning repository...")
            subprocess.run([
                "git", "clone", 
                f"https://github.com/{self.github_username}/{self.repo_name}.git"
            ], check=True)
            os.chdir(repo_dir)
        
        # Ensure Git LFS is set up
        subprocess.run(["git", "lfs", "install"], check=True)
        
        # Add LFS tracking for video files
        with open(".gitattributes", "w") as f:
            f.write("*.mp4 filter=lfs diff=lfs merge=lfs -text\n")
            f.write("*.mov filter=lfs diff=lfs merge=lfs -text\n")
            f.write("*.avi filter=lfs diff=lfs merge=lfs -text\n")
            f.write("*.webm filter=lfs diff=lfs merge=lfs -text\n")
        
        subprocess.run(["git", "add", ".gitattributes"], check=True)
        
        print("✅ Git repository setup completed")
    
    def upload_files_to_github(self):
        """Upload downloaded files to GitHub repository"""
        print("📤 Uploading files to GitHub...")
        
        # Copy files to repository directory
        for account in self.accounts.keys():
            source_dir = self.output_dir / account
            dest_dir = Path(account)
            dest_dir.mkdir(exist_ok=True)
            
            if source_dir.exists():
                for file_path in source_dir.glob("*.mp4"):
                    dest_file = dest_dir / file_path.name
                    shutil.copy2(file_path, dest_file)
                    print(f"📋 Copied: {file_path.name}")
        
        # Add, commit, and push
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m", 
                f"Add Meta Ads creative videos - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ], check=True)
            subprocess.run(["git", "push"], check=True)
            
            print("✅ Files uploaded to GitHub successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upload to GitHub: {e}")
            self.stats["errors"].append(f"GitHub upload failed: {e}")
            return False
    
    def generate_github_urls(self, filename: str, account: str) -> Dict[str, str]:
        """Generate GitHub URLs for uploaded files"""
        base_url = f"https://github.com/{self.github_username}/{self.repo_name}"
        raw_url = f"https://raw.githubusercontent.com/{self.github_username}/{self.repo_name}/main"
        
        return {
            "github_download_url": f"{raw_url}/{account}/{filename}",
            "github_view_url": f"{base_url}/blob/main/{account}/{filename}",
            "github_raw_url": f"{raw_url}/{account}/{filename}"
        }
    
    def create_updated_csv(self, ads_data: Dict[str, List[Dict]]):
        """Create updated CSV with current Meta Ads data and GitHub URLs"""
        output_file = f"Meta_Ads_Creative_Repository_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        fieldnames = [
            "Account", "Ad_ID", "Ad_Name", "Campaign_ID", "Campaign_Name", 
            "Creative_ID", "Status", "Created_Date", "Updated_Date",
            "Preview_Link", "Creative_Type", "Performance_Status",
            "GitHub_Download_URL", "GitHub_View_URL", "GitHub_Raw_URL",
            "Local_Filename", "Download_Success", "Upload_Success"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for account, ads in ads_data.items():
                for ad in ads:
                    # Generate filename
                    safe_name = "".join(c for c in ad['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"{ad['id']}_{safe_name[:50]}.mp4"
                    
                    # Generate GitHub URLs
                    github_urls = self.generate_github_urls(filename, account)
                    
                    writer.writerow({
                        "Account": account,
                        "Ad_ID": ad['id'],
                        "Ad_Name": ad['name'],
                        "Campaign_ID": ad.get('campaign_id', ''),
                        "Campaign_Name": ad.get('campaign_name', ''),
                        "Creative_ID": ad.get('creative', {}).get('id', ''),
                        "Status": ad.get('status', ''),
                        "Created_Date": ad.get('created_time', ''),
                        "Updated_Date": ad.get('updated_time', ''),
                        "Preview_Link": ad.get('preview_shareable_link', ''),
                        "Creative_Type": self.determine_creative_type(ad['name']),
                        "Performance_Status": self.determine_performance_status(ad.get('status', '')),
                        "GitHub_Download_URL": github_urls["github_download_url"],
                        "GitHub_View_URL": github_urls["github_view_url"], 
                        "GitHub_Raw_URL": github_urls["github_raw_url"],
                        "Local_Filename": filename,
                        "Download_Success": "Pending",
                        "Upload_Success": "Pending"
                    })
        
        print(f"📄 Created updated CSV: {output_file}")
        return output_file
    
    def determine_creative_type(self, ad_name: str) -> str:
        """Determine creative type from ad name"""
        ad_name_lower = ad_name.lower()
        if "video:" in ad_name_lower:
            return "Video"
        elif "image:" in ad_name_lower:
            return "Image"
        elif "gif:" in ad_name_lower:
            return "GIF"
        else:
            return "Unknown"
    
    def determine_performance_status(self, status: str) -> str:
        """Determine performance status"""
        status_map = {
            "ACTIVE": "🟢 Active",
            "PAUSED": "🟡 Paused", 
            "ARCHIVED": "🔴 Archived",
            "DELETED": "❌ Deleted"
        }
        return status_map.get(status, "❓ Unknown")
    
    def print_stats(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 FINAL STATISTICS")
        print("="*60)
        print(f"Total Ads Processed: {self.stats['total_ads']}")
        print(f"Successful Downloads: {self.stats['successful_downloads']}")
        print(f"Failed Downloads: {self.stats['failed_downloads']}")
        print(f"Successful Uploads: {self.stats['successful_uploads']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors Encountered ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more errors")
        
        print(f"\n🔗 GitHub Repository: https://github.com/{self.github_username}/{self.repo_name}")
        print("="*60)

def main():
    uploader = MetaAdsGitHubUploader()
    
    print("🚀 Meta Ads GitHub Creative Uploader v2.0")
    print("="*60)
    
    try:
        # Step 1: Setup
        uploader.setup_directories()
        
        # Step 2: Extract Meta Ads data (this will be populated with MCP calls)
        print("\n📡 Step 1: Extracting Meta Ads data...")
        ads_data = uploader.extract_meta_ads_data()
        
        # Step 3: Create CSV first (so we have the structure)
        print("\n📄 Step 2: Creating updated CSV structure...")
        csv_file = uploader.create_updated_csv(ads_data)
        
        # Step 4: Setup Git repository
        print("\n📁 Step 3: Setting up GitHub repository...")
        # Change to parent directory first
        os.chdir("..")
        uploader.setup_git_repository()
        
        print("\n✅ Setup completed! Ready for Meta Ads data extraction and video downloads.")
        print("\nNext steps:")
        print("1. Call Meta Ads MCP functions to populate ads_data")
        print("2. Download videos using preview links")
        print("3. Upload to GitHub repository")
        print(f"4. Update CSV with success/failure status")
        
        uploader.print_stats()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
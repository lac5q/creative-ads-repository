#!/usr/bin/env python3
"""
Direct Meta Ads Creative Uploader
Downloads creative ads using preview links from Meta Ads API and uploads to GitHub
for public hosting with direct download URLs.

Created: 2025-06-21
Source: Meta Ads API + GitHub Repository
Version: 3.0
"""

import csv
import os
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import shutil

class DirectMetaAdsUploader:
    def __init__(self, output_dir="creative_ads_downloads"):
        self.output_dir = Path(output_dir)
        self.repo_name = "creative-ads-repository"
        self.github_username = "lac5q"
        self.base_url = f"https://github.com/{self.github_username}/{self.repo_name}/raw/main"
        
        # Sample data from our Meta Ads API extraction
        self.current_ads = [
            {
                "id": "120225691159680108",
                "name": "video: Father's day (AI VO edited L) / Bring a smile",
                "account": "TurnedYellow",
                "preview_link": "https://fb.me/1Kn6nGAOEr7iOrY",
                "status": "ACTIVE",
                "campaign_id": "120223458675550108",
                "adset_id": "120225691159690108",
                "creative_id": "1772644153290572"
            },
            {
                "id": "120225691172150108", 
                "name": "video: influencer David / Most incredible",
                "account": "TurnedYellow",
                "preview_link": "https://fb.me/27UD3eHw89SZ4w1",
                "status": "ACTIVE",
                "campaign_id": "120223458675550108",
                "adset_id": "120225691172160108",
                "creative_id": "1772644156623905"
            },
            {
                "id": "120225691186840108",
                "name": "video: influencer David / Most incredible",
                "account": "TurnedYellow", 
                "preview_link": "https://fb.me/27UD3eHw89SZ4w1",
                "status": "ACTIVE",
                "campaign_id": "120223458675550108",
                "adset_id": "120225691186850108",
                "creative_id": "1772644156623905"
            }
        ]
        
        self.stats = {
            "total_ads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "successful_uploads": 0,
            "failed_uploads": 0
        }

    def setup_directories(self):
        """Create necessary directories"""
        print("🔧 Setting up directories...")
        
        # Create main output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Create account-specific directories
        for account in ["TurnedYellow", "MakeMeJedi"]:
            account_dir = self.output_dir / account
            account_dir.mkdir(exist_ok=True)
            
        print(f"✅ Directories created: {self.output_dir}")

    def check_dependencies(self):
        """Check if required tools are installed"""
        print("🔍 Checking dependencies...")
        
        dependencies = {
            "yt-dlp": "yt-dlp --version",
            "git": "git --version", 
            "gh": "gh --version"
        }
        
        for tool, command in dependencies.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool}: Available")
                else:
                    print(f"❌ {tool}: Not available")
                    return False
            except FileNotFoundError:
                print(f"❌ {tool}: Not found")
                return False
                
        return True

    def download_creative(self, ad_data):
        """Download a creative ad using yt-dlp"""
        print(f"\n📥 Downloading: {ad_data['name']}")
        
        # Create safe filename
        safe_name = self.create_safe_filename(ad_data['name'])
        account_dir = self.output_dir / ad_data['account']
        output_path = account_dir / f"{ad_data['id']}_{safe_name}"
        
        # Prepare yt-dlp command
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--format", "best[ext=mp4]",
            "--output", str(output_path) + ".%(ext)s",
            ad_data['preview_link']
        ]
        
        try:
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Find the downloaded file
                downloaded_files = list(account_dir.glob(f"{ad_data['id']}_{safe_name}.*"))
                if downloaded_files:
                    downloaded_file = downloaded_files[0]
                    print(f"✅ Downloaded: {downloaded_file.name}")
                    self.stats["successful_downloads"] += 1
                    return downloaded_file
                else:
                    print("❌ Download completed but file not found")
                    self.stats["failed_downloads"] += 1
                    return None
            else:
                print(f"❌ Download failed: {result.stderr}")
                self.stats["failed_downloads"] += 1
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Download timeout")
            self.stats["failed_downloads"] += 1
            return None
        except Exception as e:
            print(f"❌ Download error: {e}")
            self.stats["failed_downloads"] += 1
            return None

    def create_safe_filename(self, name):
        """Create a safe filename from ad name"""
        # Remove special characters and limit length
        safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        return safe[:50].replace(' ', '_')

    def setup_git_repository(self):
        """Setup the Git repository for uploads"""
        print("\n🔧 Setting up Git repository...")
        
        repo_dir = Path(self.repo_name)
        
        if repo_dir.exists():
            print(f"✅ Repository directory exists: {repo_dir}")
            os.chdir(repo_dir)
        else:
            print("❌ Repository directory not found")
            print("Creating repository...")
            
            # Clone the repository
            try:
                subprocess.run([
                    "gh", "repo", "clone", f"{self.github_username}/{self.repo_name}"
                ], check=True)
                os.chdir(repo_dir)
                print(f"✅ Repository cloned: {repo_dir}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone repository: {e}")
                return False
        
        # Setup Git LFS for video files
        try:
            subprocess.run(["git", "lfs", "track", "*.mp4"], check=True)
            subprocess.run(["git", "lfs", "track", "*.mov"], check=True)
            subprocess.run(["git", "lfs", "track", "*.avi"], check=True)
            subprocess.run(["git", "add", ".gitattributes"], check=True)
            print("✅ Git LFS configured")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git LFS setup warning: {e}")
            
        return True

    def upload_to_github(self, file_path, ad_data):
        """Upload file to GitHub repository"""
        print(f"\n📤 Uploading: {file_path.name}")
        
        # Create directory structure in repo
        repo_subdir = Path(ad_data['account'])
        repo_subdir.mkdir(exist_ok=True)
        
        # Copy file to repository
        dest_path = repo_subdir / file_path.name
        shutil.copy2(file_path, dest_path)
        
        try:
            # Add to git
            subprocess.run(["git", "add", str(dest_path)], check=True)
            
            # Commit
            commit_msg = f"Add creative ad: {ad_data['name']} (ID: {ad_data['id']})"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            # Push to GitHub
            subprocess.run(["git", "push"], check=True)
            
            # Generate URLs
            github_raw_url = f"{self.base_url}/{ad_data['account']}/{file_path.name}"
            github_view_url = f"https://github.com/{self.github_username}/{self.repo_name}/blob/main/{ad_data['account']}/{file_path.name}"
            
            print(f"✅ Uploaded successfully")
            print(f"   📱 Direct URL: {github_raw_url}")
            print(f"   👁️  View URL: {github_view_url}")
            
            self.stats["successful_uploads"] += 1
            
            return {
                "direct_url": github_raw_url,
                "view_url": github_view_url,
                "local_path": str(dest_path)
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Upload failed: {e}")
            self.stats["failed_uploads"] += 1
            return None

    def create_updated_csv(self, results):
        """Create updated CSV with GitHub URLs"""
        print("\n📊 Creating updated CSV...")
        
        # Go back to original directory
        os.chdir("..")
        
        csv_filename = f"Meta_Ads_Creative_GitHub_URLs_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Ad_ID', 'Ad_Name', 'Account', 'Status', 'Campaign_ID', 'AdSet_ID', 
                'Creative_ID', 'Preview_Link', 'GitHub_Direct_URL', 'GitHub_View_URL',
                'Local_File_Path', 'Upload_Status', 'Upload_Date'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for ad_data_tuple, result in results.items():
                # Convert tuple back to dict
                ad_data = dict(ad_data_tuple)
                
                row = {
                    'Ad_ID': ad_data['id'],
                    'Ad_Name': ad_data['name'],
                    'Account': ad_data['account'],
                    'Status': ad_data['status'],
                    'Campaign_ID': ad_data['campaign_id'],
                    'AdSet_ID': ad_data['adset_id'],
                    'Creative_ID': ad_data['creative_id'],
                    'Preview_Link': ad_data['preview_link'],
                    'Upload_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if result:
                    row.update({
                        'GitHub_Direct_URL': result['direct_url'],
                        'GitHub_View_URL': result['view_url'],
                        'Local_File_Path': result['local_path'],
                        'Upload_Status': 'SUCCESS'
                    })
                else:
                    row.update({
                        'GitHub_Direct_URL': '[FAILED]',
                        'GitHub_View_URL': '[FAILED]',
                        'Local_File_Path': '[FAILED]',
                        'Upload_Status': 'FAILED'
                    })
                
                writer.writerow(row)
        
        print(f"✅ CSV created: {csv_filename}")
        return csv_filename

    def print_final_report(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 FINAL REPORT")
        print("="*60)
        print(f"Total ads processed: {self.stats['total_ads']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Successful uploads: {self.stats['successful_uploads']}")
        print(f"Failed uploads: {self.stats['failed_uploads']}")
        print(f"Repository: https://github.com/{self.github_username}/{self.repo_name}")
        print("="*60)

    def run(self):
        """Main execution function"""
        print("🚀 Starting Meta Ads Creative Upload Process")
        print(f"Timestamp: {datetime.now()}")
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Missing dependencies. Please install required tools.")
            return
            
        # Setup directories
        self.setup_directories()
        
        # Setup repository
        if not self.setup_git_repository():
            print("❌ Repository setup failed")
            return
            
        # Process each ad
        results = {}
        self.stats["total_ads"] = len(self.current_ads)
        
        for ad_data in self.current_ads:
            print(f"\n{'='*60}")
            print(f"Processing Ad {ad_data['id']}: {ad_data['name']}")
            print(f"{'='*60}")
            
            # Download creative
            downloaded_file = self.download_creative(ad_data)
            
            if downloaded_file:
                # Upload to GitHub
                upload_result = self.upload_to_github(downloaded_file, ad_data)
                results[tuple(ad_data.items())] = upload_result
            else:
                results[tuple(ad_data.items())] = None
        
        # Go back to original directory for CSV creation
        os.chdir("..")
        
        # Create updated CSV
        csv_file = self.create_updated_csv(results)
        
        # Print final report
        self.print_final_report()
        
        return csv_file

if __name__ == "__main__":
    uploader = DirectMetaAdsUploader()
    result_csv = uploader.run()
    print(f"\n🎉 Process complete! Results saved to: {result_csv}") 
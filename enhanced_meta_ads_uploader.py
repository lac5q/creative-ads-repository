#!/usr/bin/env python3
"""
Enhanced Meta Ads Creative Uploader with Browser Authentication
Uses browser automation to authenticate with Facebook Business and download creative videos
then uploads to GitHub repository for public hosting.

Created: 2025-06-21
Source: Meta Ads API + Browser Automation + GitHub Repository
Version: 4.0 - Browser Authentication
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
from typing import Dict, List, Any, Optional

class EnhancedMetaAdsUploader:
    def __init__(self, output_dir="creative_ads_downloads"):
        self.output_dir = Path(output_dir)
        self.repo_name = "creative-ads-repository"
        self.github_username = "lac5q"
        self.base_url = f"https://github.com/{self.github_username}/{self.repo_name}/raw/main"
        
        # Load ad data from CSV
        self.csv_file = "TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv"
        self.ads_data = []
        self.load_ads_from_csv()
        
        self.stats = {
            "total_ads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "browser_auth_attempts": 0,
            "browser_auth_success": 0
        }

    def load_ads_from_csv(self):
        """Load ad data from the CSV file"""
        print(f"📊 Loading ad data from {self.csv_file}...")
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Status'] == 'ACTIVE':  # Only process active ads
                        ad_data = {
                            "id": row['Ad_ID'],
                            "name": row['Ad_Name'].strip('"'),
                            "account": row['Account'],
                            "campaign": row['Campaign'],
                            "status": row['Status'],
                            "performance_rating": row['Performance_Rating'],
                            "preview_link": row['Facebook_Preview_Link'],
                            "download_command": row['Download_Command'],
                            "priority": row['Priority'],
                            "notes": row['Notes']
                        }
                        self.ads_data.append(ad_data)
            
            print(f"✅ Loaded {len(self.ads_data)} active ads from CSV")
            
        except FileNotFoundError:
            print(f"❌ CSV file not found: {self.csv_file}")
            return False
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
        return True

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

    def setup_directories(self):
        """Create necessary directories"""
        print("🔧 Setting up directories...")
        
        self.output_dir.mkdir(exist_ok=True)
        
        for account in ["TurnedYellow", "MakeMeJedi"]:
            account_dir = self.output_dir / account
            account_dir.mkdir(exist_ok=True)
            
        print(f"✅ Directories created: {self.output_dir}")

    def download_creative_enhanced(self, ad_data: Dict) -> Optional[Path]:
        """Download creative with enhanced methods"""
        print(f"\n📥 Downloading: {ad_data['name']}")
        print(f"   Priority: {ad_data['priority']}")
        print(f"   Performance: {ad_data['performance_rating']}")
        
        safe_name = self.create_safe_filename(ad_data['name'])
        account_dir = self.output_dir / ad_data['account']
        output_path = account_dir / f"{ad_data['id']}_{safe_name}"
        
        # Try multiple download strategies
        strategies = [
            self.try_youtube_dl_cookies,
            self.try_youtube_dl_headers,
            self.try_direct_download
        ]
        
        for strategy in strategies:
            try:
                result = strategy(ad_data['preview_link'], output_path)
                if result:
                    self.stats["successful_downloads"] += 1
                    return result
            except Exception as e:
                print(f"   ⚠️ Strategy failed: {e}")
                continue
        
        self.stats["failed_downloads"] += 1
        return None

    def try_youtube_dl_cookies(self, url: str, output_path: Path) -> Optional[Path]:
        """Try download with cookies"""
        print("   🍪 Trying with cookies...")
        
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", "chrome",
            "--format", "best[ext=mp4]",
            "--output", str(output_path) + ".%(ext)s",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            files = list(output_path.parent.glob(f"{output_path.name}.*"))
            if files:
                print(f"✅ Downloaded with cookies: {files[0].name}")
                return files[0]
        
        return None

    def try_youtube_dl_headers(self, url: str, output_path: Path) -> Optional[Path]:
        """Try download with custom headers"""
        print("   📱 Trying with custom headers...")
        
        cmd = [
            "yt-dlp",
            "--add-header", "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "--add-header", "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--format", "best[ext=mp4]",
            "--output", str(output_path) + ".%(ext)s",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            files = list(output_path.parent.glob(f"{output_path.name}.*"))
            if files:
                print(f"✅ Downloaded with headers: {files[0].name}")
                return files[0]
        
        return None

    def try_direct_download(self, url: str, output_path: Path) -> Optional[Path]:
        """Try basic download"""
        print("   🔄 Trying direct download...")
        
        cmd = [
            "yt-dlp",
            "--format", "best[ext=mp4]",
            "--output", str(output_path) + ".%(ext)s",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            files = list(output_path.parent.glob(f"{output_path.name}.*"))
            if files:
                print(f"✅ Downloaded directly: {files[0].name}")
                return files[0]
        
        return None

    def create_safe_filename(self, name: str) -> str:
        """Create a safe filename from ad name"""
        safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        return safe[:50].replace(' ', '_')

    def setup_git_repository(self) -> bool:
        """Setup the Git repository for uploads"""
        print("\n🔧 Setting up Git repository...")
        
        repo_dir = Path(self.repo_name)
        
        if repo_dir.exists():
            print(f"✅ Repository directory exists: {repo_dir}")
            os.chdir(repo_dir)
        else:
            try:
                subprocess.run([
                    "gh", "repo", "clone", f"{self.github_username}/{self.repo_name}"
                ], check=True)
                os.chdir(repo_dir)
                print(f"✅ Repository cloned: {repo_dir}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone repository: {e}")
                return False
        
        try:
            subprocess.run(["git", "lfs", "track", "*.mp4"], check=True)
            subprocess.run(["git", "lfs", "track", "*.mov"], check=True)
            subprocess.run(["git", "add", ".gitattributes"], check=True)
            print("✅ Git LFS configured")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git LFS setup warning: {e}")
            
        return True

    def upload_to_github(self, file_path: Path, ad_data: Dict) -> Optional[Dict]:
        """Upload file to GitHub repository"""
        print(f"\n📤 Uploading: {file_path.name}")
        
        repo_subdir = Path(ad_data['account'])
        repo_subdir.mkdir(exist_ok=True)
        
        dest_path = repo_subdir / file_path.name
        shutil.copy2(file_path, dest_path)
        
        try:
            subprocess.run(["git", "add", str(dest_path)], check=True)
            
            commit_msg = f"Add {ad_data['performance_rating']} creative: {ad_data['name']} (ID: {ad_data['id']})"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            subprocess.run(["git", "push"], check=True)
            
            github_raw_url = f"{self.base_url}/{ad_data['account']}/{file_path.name}"
            github_view_url = f"https://github.com/{self.github_username}/{self.repo_name}/blob/main/{ad_data['account']}/{file_path.name}"
            
            print(f"✅ Uploaded successfully")
            print(f"   📱 Direct URL: {github_raw_url}")
            
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

    def create_updated_csv(self, results: Dict) -> str:
        """Create updated CSV with GitHub URLs"""
        print("\n📊 Creating updated CSV...")
        
        os.chdir("..")
        
        csv_filename = f"Creative_Ads_GitHub_URLs_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Ad_ID', 'Ad_Name', 'Account', 'Campaign', 'Performance_Rating',
                'Priority', 'GitHub_Direct_URL', 'GitHub_View_URL', 'Upload_Status'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for ad_data in self.ads_data:
                result = results.get(ad_data['id'])
                
                row = {
                    'Ad_ID': ad_data['id'],
                    'Ad_Name': ad_data['name'],
                    'Account': ad_data['account'],
                    'Campaign': ad_data['campaign'],
                    'Performance_Rating': ad_data['performance_rating'],
                    'Priority': ad_data['priority']
                }
                
                if result:
                    row.update({
                        'GitHub_Direct_URL': result['direct_url'],
                        'GitHub_View_URL': result['view_url'],
                        'Upload_Status': 'SUCCESS'
                    })
                else:
                    row.update({
                        'GitHub_Direct_URL': '[FAILED]',
                        'GitHub_View_URL': '[FAILED]',
                        'Upload_Status': 'FAILED'
                    })
                
                writer.writerow(row)
        
        print(f"✅ CSV created: {csv_filename}")
        return csv_filename

    def run(self):
        """Main execution function"""
        print("🚀 Starting Enhanced Meta Ads Creative Upload")
        print(f"Timestamp: {datetime.now()}")
        
        if not self.load_ads_from_csv():
            return None
            
        if not self.check_dependencies():
            print("❌ Missing dependencies")
            return None
            
        self.setup_directories()
        
        if not self.setup_git_repository():
            print("❌ Repository setup failed")
            return None
            
        results = {}
        self.stats["total_ads"] = len(self.ads_data)
        
        # Process ads by priority
        priority_order = {"EXCELLENT": 1, "GOOD": 2, "AVERAGE": 3, "POOR": 4}
        sorted_ads = sorted(self.ads_data, 
                          key=lambda x: priority_order.get(x['performance_rating'], 5))
        
        for i, ad_data in enumerate(sorted_ads, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(sorted_ads)}: {ad_data['name']}")
            print(f"{'='*60}")
            
            downloaded_file = self.download_creative_enhanced(ad_data)
            
            if downloaded_file:
                upload_result = self.upload_to_github(downloaded_file, ad_data)
                results[ad_data['id']] = upload_result
            else:
                results[ad_data['id']] = None
        
        os.chdir("..")
        csv_file = self.create_updated_csv(results)
        
        print(f"\n🎉 Process complete!")
        print(f"✅ Successful: {self.stats['successful_uploads']}")
        print(f"❌ Failed: {self.stats['failed_uploads']}")
        print(f"📊 CSV: {csv_file}")
        
        return csv_file

if __name__ == "__main__":
    uploader = EnhancedMetaAdsUploader()
    uploader.run() 
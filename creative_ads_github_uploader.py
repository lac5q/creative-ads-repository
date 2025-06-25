#!/usr/bin/env python3
"""
Creative Ads GitHub Uploader
Downloads creative ads from Facebook preview links and uploads to GitHub repository
for public hosting with direct download URLs.

Created: 2025-01-18
Source: TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv
Version: 1.0
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

class CreativeAdsUploader:
    def __init__(self, csv_file, output_dir="creative_ads_downloads"):
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.repo_name = "creative-ads-repository"
        self.github_username = None
        self.stats = {
            "total_ads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "uploaded_files": 0,
            "failed_uploads": 0
        }
        
    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "TurnedYellow").mkdir(exist_ok=True)
        (self.output_dir / "MakeMeJedi").mkdir(exist_ok=True)
        print(f"✅ Created directories in {self.output_dir}")
    
    def check_github_auth(self):
        """Check if GitHub CLI is authenticated"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Extract username from auth status
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'account' in line.lower() and '(' in line:
                        self.github_username = line.split('account')[1].split('(')[0].strip()
                        break
                
                # If we couldn't parse it, try the API
                if not self.github_username:
                    api_result = subprocess.run(['gh', 'api', 'user'], 
                                              capture_output=True, text=True)
                    if api_result.returncode == 0:
                        try:
                            user_data = json.loads(api_result.stdout)
                            self.github_username = user_data.get('login')
                        except:
                            self.github_username = 'lac5q'  # fallback based on auth status
                
                print(f"✅ GitHub authenticated as: {self.github_username}")
                return True
            else:
                print("❌ GitHub not authenticated. Run: gh auth login")
                return False
        except FileNotFoundError:
            print("❌ GitHub CLI not found. Install with: brew install gh")
            return False
    
    def create_github_repo(self):
        """Create GitHub repository for hosting"""
        try:
            # Check if repo already exists
            result = subprocess.run(['gh', 'repo', 'view', self.repo_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Repository {self.repo_name} already exists")
                return True
            
            # Create new public repository
            result = subprocess.run([
                'gh', 'repo', 'create', self.repo_name,
                '--public',
                '--description', 'Creative ads repository for TurnedYellow and MakeMeJedi campaigns',
                '--clone'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created repository: {self.repo_name}")
                return True
            else:
                print(f"❌ Failed to create repository: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error creating repository: {e}")
            return False
    
    def parse_csv(self):
        """Parse the CSV file and extract ad information"""
        ads_data = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Skip paused ads
                    if row.get('Status', '').upper() == 'PAUSED':
                        continue
                        
                    ads_data.append({
                        'ad_id': row.get('Ad_ID'),
                        'ad_name': row.get('Ad_Name'),
                        'account': row.get('Account'),
                        'campaign': row.get('Campaign'),
                        'status': row.get('Status'),
                        'performance_rating': row.get('Performance_Rating'),
                        'facebook_link': row.get('Facebook_Preview_Link'),
                        'download_command': row.get('Download_Command', ''),
                        'priority': row.get('Priority', ''),
                        'notes': row.get('Notes', '')
                    })
            
            self.stats["total_ads"] = len(ads_data)
            print(f"✅ Parsed {len(ads_data)} active ads from CSV")
            return ads_data
        except Exception as e:
            print(f"❌ Error parsing CSV: {e}")
            return []
    
    def extract_filename_from_command(self, download_command):
        """Extract filename from yt-dlp command"""
        try:
            # Look for -o parameter with filename
            parts = download_command.split('-o')
            if len(parts) > 1:
                filename_part = parts[1].strip().strip('"').strip("'")
                # Remove .%(ext)s and add .mp4
                filename = filename_part.replace('.%(ext)s', '.mp4')
                return filename
            return None
        except:
            return None
    
    def download_video(self, ad_data):
        """Download video using yt-dlp"""
        facebook_link = ad_data['facebook_link']
        account = ad_data['account']
        
        if not facebook_link or facebook_link in ['[TO_BE_FILLED]', '']:
            print(f"⚠️  Skipping {ad_data['ad_name']}: No Facebook link")
            return None
        
        # Determine output filename
        if ad_data['download_command']:
            filename = self.extract_filename_from_command(ad_data['download_command'])
        else:
            # Generate filename from ad data
            safe_name = "".join(c for c in ad_data['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{ad_data['ad_id']}_{safe_name}.mp4"
        
        if not filename:
            filename = f"{ad_data['ad_id']}_video.mp4"
        
        # Set output path
        output_path = self.output_dir / account / filename
        
        try:
            print(f"📥 Downloading: {ad_data['ad_name']}")
            print(f"   Link: {facebook_link}")
            print(f"   Output: {output_path}")
            
            # Use yt-dlp to download
            cmd = [
                'yt-dlp',
                facebook_link,
                '-f', 'best[ext=mp4]',
                '-o', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and output_path.exists():
                self.stats["successful_downloads"] += 1
                print(f"✅ Downloaded: {filename}")
                return output_path
            else:
                self.stats["failed_downloads"] += 1
                print(f"❌ Failed to download {filename}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.stats["failed_downloads"] += 1
            print(f"❌ Download timeout for {filename}")
            return None
        except Exception as e:
            self.stats["failed_downloads"] += 1
            print(f"❌ Download error for {filename}: {e}")
            return None
    
    def setup_git_lfs(self):
        """Setup Git LFS for video files"""
        try:
            os.chdir(self.repo_name)
            
            # Initialize Git LFS
            subprocess.run(['git', 'lfs', 'install'], check=True)
            
            # Track video files
            subprocess.run(['git', 'lfs', 'track', '*.mp4'], check=True)
            subprocess.run(['git', 'add', '.gitattributes'], check=True)
            
            print("✅ Git LFS configured for video files")
            return True
        except Exception as e:
            print(f"❌ Error setting up Git LFS: {e}")
            return False
    
    def upload_to_github(self, file_path, ad_data):
        """Upload file to GitHub repository"""
        try:
            # Copy file to repository
            account_dir = Path(self.repo_name) / ad_data['account']
            account_dir.mkdir(exist_ok=True)
            
            dest_path = account_dir / file_path.name
            shutil.copy2(file_path, dest_path)
            
            # Add to git
            subprocess.run(['git', 'add', str(dest_path)], check=True, cwd=self.repo_name)
            
            self.stats["uploaded_files"] += 1
            print(f"✅ Staged for upload: {dest_path}")
            return True
            
        except Exception as e:
            self.stats["failed_uploads"] += 1
            print(f"❌ Error uploading {file_path}: {e}")
            return False
    
    def commit_and_push(self):
        """Commit and push all changes to GitHub"""
        try:
            os.chdir(self.repo_name)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if not result.stdout.strip():
                print("ℹ️  No changes to commit")
                return True
            
            # Commit changes
            commit_message = f"Add creative ads - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to GitHub
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Successfully pushed to GitHub")
            return True
            
        except Exception as e:
            print(f"❌ Error committing/pushing: {e}")
            return False
    
    def generate_github_urls(self, ads_data):
        """Generate GitHub raw URLs for downloaded files"""
        base_url = f"https://github.com/{self.github_username}/{self.repo_name}/raw/main"
        
        for ad_data in ads_data:
            account = ad_data['account']
            if ad_data.get('local_file'):
                filename = ad_data['local_file'].name
                download_url = f"{base_url}/{account}/{filename}"
                view_url = f"https://github.com/{self.github_username}/{self.repo_name}/blob/main/{account}/{filename}"
                
                ad_data['github_download_url'] = download_url
                ad_data['github_view_url'] = view_url
        
        return ads_data
    
    def update_csv_with_urls(self, ads_data):
        """Update the original CSV with GitHub URLs"""
        output_csv = f"updated_{Path(self.csv_file).name}"
        
        try:
            # Read original CSV to preserve all data
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                fieldnames = reader.fieldnames
            
            # Update rows with GitHub URLs
            ads_dict = {ad['ad_id']: ad for ad in ads_data}
            
            for row in rows:
                ad_id = row.get('Ad_ID')
                if ad_id in ads_dict and ads_dict[ad_id].get('github_download_url'):
                    row['Meta_Video_URL'] = ads_dict[ad_id]['github_download_url']
                    row['Google_Drive_Download_Link'] = ads_dict[ad_id]['github_download_url']
                    row['Google_Drive_View_Link'] = ads_dict[ad_id]['github_view_url']
            
            # Write updated CSV
            with open(output_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"✅ Updated CSV saved as: {output_csv}")
            return output_csv
            
        except Exception as e:
            print(f"❌ Error updating CSV: {e}")
            return None
    
    def print_summary_report(self):
        """Print summary report"""
        print("\n" + "="*60)
        print("CREATIVE ADS UPLOAD SUMMARY REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print(f"Total ads processed: {self.stats['total_ads']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Files uploaded: {self.stats['uploaded_files']}")
        print(f"Upload failures: {self.stats['failed_uploads']}")
        if self.stats['total_ads'] > 0:
            print(f"Success rate: {(self.stats['successful_downloads']/self.stats['total_ads']*100):.1f}%")
        
        if self.github_username:
            print(f"\nRepository: https://github.com/{self.github_username}/{self.repo_name}")
            print(f"Raw files base URL: https://github.com/{self.github_username}/{self.repo_name}/raw/main/")
        
        print("="*60)

    def run(self):
        """Main execution flow"""
        print("🚀 Starting Creative Ads GitHub Upload Process")
        print(f"Source file: {self.csv_file}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup
        self.setup_directories()
        
        if not self.check_github_auth():
            return False
        
        if not self.create_github_repo():
            return False
        
        # Parse CSV
        ads_data = self.parse_csv()
        if not ads_data:
            return False
        
        # Setup Git LFS
        if not self.setup_git_lfs():
            return False
        
        # Download and upload videos (process first 3 for testing)
        original_cwd = os.getcwd()
        try:
            for i, ad_data in enumerate(ads_data[:3]):  # Process first 3 for testing
                print(f"\n--- Processing ad {i+1}/3 ---")
                downloaded_file = self.download_video(ad_data)
                if downloaded_file:
                    ad_data['local_file'] = downloaded_file
                    self.upload_to_github(downloaded_file, ad_data)
                time.sleep(2)  # Rate limiting
        finally:
            os.chdir(original_cwd)
        
        # Commit and push all changes
        if not self.commit_and_push():
            return False
        
        # Generate URLs and update CSV
        ads_data = self.generate_github_urls(ads_data)
        updated_csv = self.update_csv_with_urls(ads_data)
        
        # Print summary
        self.print_summary_report()
        
        return True

if __name__ == "__main__":
    # Configuration
    csv_file = "TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    uploader = CreativeAdsUploader(csv_file)
    success = uploader.run()
    
    if success:
        print("🎉 Creative ads upload process completed successfully!")
    else:
        print("❌ Upload process failed. Check errors above.")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Facebook Ad Video Downloader
Downloads videos from Facebook ad preview URLs and uploads to GitHub
"""

import requests
import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import subprocess
import shutil
from pathlib import Path

class FacebookVideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Create download directory
        self.download_dir = Path("creative_ads_downloads")
        self.download_dir.mkdir(exist_ok=True)
        
        # Load test results
        with open('facebook_url_test_results.json', 'r') as f:
            self.ads_data = json.load(f)
    
    def extract_video_from_business_page(self, final_url, ad_data):
        """Extract video URL from Facebook Business confirmation page"""
        print(f"🔍 Analyzing Facebook Business page for: {ad_data['ad_name']}")
        
        try:
            response = self.session.get(final_url, timeout=15)
            html_content = response.text
            
            # Look for video URLs in the page source
            video_patterns = [
                r'https://[^"]*\.mp4[^"]*',
                r'https://[^"]*video[^"]*\.mp4',
                r'https://scontent[^"]*\.mp4',
                r'https://video[^"]*\.mp4'
            ]
            
            import re
            found_videos = []
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    # Clean up the URL
                    clean_url = match.split('"')[0].split("'")[0]
                    if clean_url not in found_videos:
                        found_videos.append(clean_url)
            
            print(f"📦 Found {len(found_videos)} potential video URLs")
            
            # Try to download each video URL
            for i, video_url in enumerate(found_videos[:3]):  # Try first 3
                print(f"🎬 Attempting download {i+1}: {video_url[:80]}...")
                
                if self.download_video(video_url, ad_data):
                    return True
            
            # If no direct video URLs found, try alternative methods
            return self.try_alternative_methods(final_url, ad_data)
            
        except Exception as e:
            print(f"❌ Error extracting video: {str(e)}")
            return False
    
    def download_video(self, video_url, ad_data):
        """Download video from direct URL"""
        try:
            print(f"⬇️ Downloading video...")
            
            # Create filename
            safe_name = "".join(c for c in ad_data['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{ad_data['account']}_{safe_name}_{ad_data['ad_id']}.mp4"
            filepath = self.download_dir / filename
            
            # Download the video
            video_response = self.session.get(video_url, stream=True, timeout=30)
            video_response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = filepath.stat().st_size
            print(f"✅ Downloaded: {filepath} ({file_size:,} bytes)")
            
            # Update ad data with download info
            ad_data['downloaded'] = True
            ad_data['local_file'] = str(filepath)
            ad_data['file_size'] = file_size
            ad_data['download_timestamp'] = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return False
    
    def try_alternative_methods(self, final_url, ad_data):
        """Try alternative methods to get the video"""
        print("🔄 Trying alternative methods...")
        
        # Method 1: Try yt-dlp if available
        if self.try_ytdlp(ad_data['facebook_url'], ad_data):
            return True
        
        # Method 2: Try to extract from page metadata
        if self.extract_from_metadata(final_url, ad_data):
            return True
        
        # Method 3: Create a placeholder with the URL for manual download
        return self.create_placeholder(ad_data)
    
    def try_ytdlp(self, url, ad_data):
        """Try using yt-dlp to download the video"""
        try:
            print("🎭 Trying yt-dlp...")
            
            # Check if yt-dlp is available
            result = subprocess.run(['which', 'yt-dlp'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ yt-dlp not found")
                return False
            
            # Create filename
            safe_name = "".join(c for c in ad_data['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{ad_data['account']}_{safe_name}_{ad_data['ad_id']}.%(ext)s"
            filepath = self.download_dir / filename
            
            # Run yt-dlp
            cmd = [
                'yt-dlp',
                url,
                '-f', 'best[ext=mp4]',
                '-o', str(filepath),
                '--no-warnings'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ yt-dlp download successful")
                ad_data['downloaded'] = True
                ad_data['download_method'] = 'yt-dlp'
                ad_data['download_timestamp'] = datetime.now().isoformat()
                return True
            else:
                print(f"❌ yt-dlp failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ yt-dlp error: {str(e)}")
            return False
    
    def extract_from_metadata(self, url, ad_data):
        """Try to extract video URL from page metadata"""
        try:
            print("🔍 Checking page metadata...")
            
            response = self.session.get(url)
            html_content = response.text
            
            # Look for Open Graph video tags
            import re
            og_video_patterns = [
                r'<meta property="og:video" content="([^"]*)"',
                r'<meta property="og:video:url" content="([^"]*)"',
                r'<meta name="twitter:player:stream" content="([^"]*)"'
            ]
            
            for pattern in og_video_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    print(f"🎬 Found metadata video URL: {match}")
                    if self.download_video(match, ad_data):
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Metadata extraction error: {str(e)}")
            return False
    
    def create_placeholder(self, ad_data):
        """Create a placeholder file with download instructions"""
        print("📝 Creating placeholder file...")
        
        try:
            safe_name = "".join(c for c in ad_data['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{ad_data['account']}_{safe_name}_{ad_data['ad_id']}_PLACEHOLDER.md"
            filepath = self.download_dir / filename
            
            placeholder_content = f"""# {ad_data['ad_name']}

**Account:** {ad_data['account']}
**Ad ID:** {ad_data['ad_id']}
**CVR:** {ad_data['cvr']}
**Priority:** {ad_data['priority']}

## Download Instructions

**Facebook URL:** {ad_data['facebook_url']}
**Final URL:** {ad_data['final_url']}

### Manual Download Steps:
1. Open the Facebook URL in a browser
2. Log in to Facebook if required
3. Right-click on the video and select "Save video as..."
4. Save as: `{ad_data['expected_filename']}`

### Alternative Methods:
```bash
# Try with yt-dlp
yt-dlp "{ad_data['facebook_url']}" -f "best[ext=mp4]" -o "{ad_data['expected_filename']}"

# Try with browser automation
# Use Playwright or Selenium to automate the download
```

**Status:** REQUIRES_MANUAL_DOWNLOAD
**Created:** {datetime.now().isoformat()}
"""
            
            with open(filepath, 'w') as f:
                f.write(placeholder_content)
            
            print(f"📝 Placeholder created: {filepath}")
            
            ad_data['placeholder_created'] = True
            ad_data['placeholder_file'] = str(filepath)
            ad_data['status'] = 'REQUIRES_MANUAL_DOWNLOAD'
            
            return True
            
        except Exception as e:
            print(f"❌ Placeholder creation failed: {str(e)}")
            return False
    
    def upload_to_github(self, ad_data):
        """Upload downloaded files to GitHub repository"""
        print(f"📤 Uploading to GitHub...")
        
        try:
            # Change to the repository directory
            repo_dir = Path("creative-ads-repository")
            account_dir = repo_dir / ad_data['account']
            account_dir.mkdir(exist_ok=True)
            
            # Copy the downloaded file to the repository
            if ad_data.get('local_file'):
                source_file = Path(ad_data['local_file'])
                dest_file = account_dir / source_file.name
                shutil.copy2(source_file, dest_file)
                
                # Git add and commit
                subprocess.run(['git', 'add', str(dest_file)], cwd=repo_dir)
                subprocess.run(['git', 'commit', '-m', f'Add video: {ad_data["ad_name"]}'], cwd=repo_dir)
                subprocess.run(['git', 'push'], cwd=repo_dir)
                
                # Generate GitHub URLs
                github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{ad_data['account']}/{source_file.name}"
                raw_url = f"https://github.com/lac5q/creative-ads-repository/raw/main/{ad_data['account']}/{source_file.name}"
                
                ad_data['github_url'] = github_url
                ad_data['github_raw_url'] = raw_url
                
                print(f"✅ Uploaded to GitHub: {github_url}")
                return True
            
            elif ad_data.get('placeholder_file'):
                # Upload placeholder
                source_file = Path(ad_data['placeholder_file'])
                dest_file = account_dir / source_file.name
                shutil.copy2(source_file, dest_file)
                
                subprocess.run(['git', 'add', str(dest_file)], cwd=repo_dir)
                subprocess.run(['git', 'commit', '-m', f'Add placeholder: {ad_data["ad_name"]}'], cwd=repo_dir)
                subprocess.run(['git', 'push'], cwd=repo_dir)
                
                github_url = f"https://github.com/lac5q/creative-ads-repository/blob/main/{ad_data['account']}/{source_file.name}"
                ad_data['github_placeholder_url'] = github_url
                
                print(f"📝 Placeholder uploaded to GitHub: {github_url}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ GitHub upload failed: {str(e)}")
            return False
    
    def process_all_ads(self):
        """Process all ads in the test results"""
        print("🚀 Starting Facebook Video Download Process")
        print("=" * 60)
        
        results = []
        
        for ad_data in self.ads_data:
            print(f"\n📱 Processing: {ad_data['ad_name']}")
            print(f"🏢 Account: {ad_data['account']}")
            print(f"📊 CVR: {ad_data['cvr']} | Priority: {ad_data['priority']}")
            print("-" * 40)
            
            # Try to extract and download video
            success = self.extract_video_from_business_page(ad_data['final_url'], ad_data)
            
            if success:
                # Upload to GitHub
                self.upload_to_github(ad_data)
            
            results.append(ad_data)
            
            # Small delay between requests
            time.sleep(2)
        
        # Save final results
        with open('facebook_download_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n📊 DOWNLOAD PROCESS COMPLETE")
        print("=" * 60)
        
        downloaded_count = sum(1 for r in results if r.get('downloaded', False))
        placeholder_count = sum(1 for r in results if r.get('placeholder_created', False))
        
        print(f"✅ Successfully downloaded: {downloaded_count}")
        print(f"📝 Placeholders created: {placeholder_count}")
        print(f"📁 Total processed: {len(results)}")
        print(f"💾 Results saved to: facebook_download_results.json")
        
        return results

if __name__ == "__main__":
    downloader = FacebookVideoDownloader()
    results = downloader.process_all_ads() 
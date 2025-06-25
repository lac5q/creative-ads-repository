#!/usr/bin/env python3
"""
Download actual ad creatives from Facebook preview URLs
"""

import subprocess
import os
import csv
from datetime import datetime

def download_facebook_video(url, output_filename):
    """Download video from Facebook URL using yt-dlp"""
    try:
        print(f"🔄 Downloading from: {url}")
        print(f"📁 Output file: {output_filename}")
        
        # Use yt-dlp to download the video
        cmd = [
            'yt-dlp',
            url,
            '-f', 'best[ext=mp4]',
            '-o', output_filename,
            '--no-check-certificate'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded: {output_filename}")
            return True
        else:
            print(f"❌ Failed to download: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Download timeout for: {url}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return False

def main():
    # Facebook URLs from CSV
    facebook_urls = {
        "01_David_Influencer_WINNER": "https://fb.me/27UD3eHw89SZ4w1",
        "02_TY_Video_1_HIGH_HOOK": "https://fb.me/1O3TXzYvE3BeFIv",
        "03_Royal_Inspo_Hook_STRONG": "https://fb.me/2ayqQiBBS6lTK5g"
    }
    
    print("🎬 Downloading Real Facebook Ad Creatives")
    print("=" * 50)
    
    # Create output directory
    output_dir = "real_facebook_creatives"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    
    for ad_name, fb_url in facebook_urls.items():
        output_file = f"{output_dir}/{ad_name}.%(ext)s"
        
        print(f"\n📺 Processing: {ad_name}")
        
        if download_facebook_video(fb_url, output_file):
            success_count += 1
        
        print("-" * 30)
    
    print(f"\n🎉 Summary:")
    print(f"   ✅ Successfully downloaded: {success_count}/{len(facebook_urls)}")
    print(f"   📁 Output directory: {output_dir}/")
    print(f"   📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List downloaded files
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"\n📋 Downloaded files:")
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                size = os.path.getsize(file_path)
                print(f"   - {file} ({size:,} bytes)")

if __name__ == "__main__":
    main() 
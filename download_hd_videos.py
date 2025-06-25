#!/usr/bin/env python3
"""
Download high-quality videos from Facebook URLs
"""

import subprocess
import os
import csv
from datetime import datetime

def download_facebook_video_hd(url, output_filename):
    """Download highest quality video from Facebook URL using yt-dlp"""
    try:
        print(f"🔄 Downloading HD video from: {url}")
        print(f"📁 Output file: {output_filename}")
        
        # Use yt-dlp with highest quality settings
        cmd = [
            'yt-dlp',
            url,
            '-f', 'best[height>=720]/best',  # Prefer 720p or higher, fallback to best
            '-o', output_filename,
            '--no-check-certificate',
            '--write-thumbnail',  # Also download thumbnail
            '--write-info-json',  # Save metadata
            '--extract-flat', 'false',
            '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            '--referer', 'https://www.facebook.com/',
            '--cookies-from-browser', 'chrome'  # Use Chrome cookies for authentication
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded: {output_filename}")
            
            # Check file size
            if os.path.exists(output_filename):
                file_size = os.path.getsize(output_filename)
                print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            
            return True
        else:
            print(f"❌ yt-dlp failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout downloading {url}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def download_image_hd(url, output_filename):
    """Download high-resolution image"""
    try:
        import requests
        
        print(f"🔄 Downloading HD image from: {url}")
        
        # Try to get original resolution by modifying URL
        if 'fbcdn.net' in url:
            # Remove size restrictions
            original_url = url.split('?')[0]
            print(f"🔍 Trying original URL: {original_url}")
            
            response = requests.get(original_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(output_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(output_filename)
                print(f"✅ Downloaded: {output_filename} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Failed to download original: {response.status_code}")
        
        # Fallback to original URL
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(output_filename)
            print(f"✅ Downloaded: {output_filename} ({file_size:,} bytes)")
            return True
        else:
            print(f"❌ Failed to download: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return False

def main():
    print("🎯 Downloading High-Quality TurnedYellow Ad Creatives")
    
    # Create output directory
    output_dir = "hd_ad_creatives"
    os.makedirs(output_dir, exist_ok=True)
    
    # Facebook URLs from your CSV (Facebook_Preview_Link column)
    facebook_urls = [
        "https://www.facebook.com/ads/library/?id=1712278179654694",
        "https://www.facebook.com/ads/library/?id=3929466347265050", 
        "https://www.facebook.com/ads/library/?id=2590438734496446",
        "https://www.facebook.com/ads/library/?id=9832566163478379"
    ]
    
    ad_names = [
        "01_David_Influencer_WINNER",
        "02_TY_Video_1_HIGH_HOOK",
        "03_Royal_Inspo_Hook_STRONG", 
        "04_Bigfoot_Jungle_Vlog"
    ]
    
    print(f"📊 Found {len(facebook_urls)} Facebook ad URLs to download")
    
    downloaded_count = 0
    
    for i, (url, ad_name) in enumerate(zip(facebook_urls, ad_names)):
        print(f"\n🎨 Processing {i+1}/{len(facebook_urls)}: {ad_name}")
        
        # Try to download as video first
        video_filename = f"{output_dir}/{ad_name}_HD_VIDEO.%(ext)s"
        if download_facebook_video_hd(url, video_filename):
            downloaded_count += 1
            continue
        
        # If video fails, try to extract image
        image_filename = f"{output_dir}/{ad_name}_HD_IMAGE.jpg"
        print(f"🔄 Video download failed, trying to extract image...")
        
        # Use yt-dlp to extract thumbnail
        try:
            cmd = [
                'yt-dlp',
                url,
                '--write-thumbnail',
                '--skip-download',
                '-o', f"{output_dir}/{ad_name}_HD_THUMBNAIL.%(ext)s"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ Extracted thumbnail for {ad_name}")
                downloaded_count += 1
            else:
                print(f"❌ Failed to extract thumbnail: {result.stderr}")
        except Exception as e:
            print(f"❌ Error extracting thumbnail: {str(e)}")
    
    print(f"\n🎉 Downloaded {downloaded_count}/{len(facebook_urls)} high-quality creatives!")
    
    # Copy to GitHub repository
    if downloaded_count > 0:
        print("\n📁 Copying to GitHub repository...")
        os.system(f"cp {output_dir}/* creative-ads-repository/TurnedYellow/ 2>/dev/null || true")
        print("✅ Copied HD creatives to GitHub repository")
        
        # Show file sizes
        print("\n📊 File sizes:")
        for file in os.listdir(output_dir):
            if os.path.isfile(os.path.join(output_dir, file)):
                size = os.path.getsize(os.path.join(output_dir, file))
                print(f"  {file}: {size:,} bytes ({size/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main() 
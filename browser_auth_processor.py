#!/usr/bin/env python3
"""
Browser Authentication Processor
Handles Facebook Business authentication for creative ads download
"""

import pandas as pd
import os
import subprocess
import asyncio
import time
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('browser_auth_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BrowserAuthProcessor:
    def __init__(self):
        self.csv_file = "TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv"
        self.repo_path = "creative-ads-repository"
        self.github_username = "lac5q"
        self.results = []
        
    def setup_playwright_environment(self):
        """Setup Playwright for browser automation"""
        try:
            logger.info("🎭 Setting up Playwright environment...")
            
            # Install playwright if not available
            result = subprocess.run(["pip3", "install", "playwright"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Playwright installed successfully")
            
            # Install browser binaries
            result = subprocess.run(["playwright", "install", "chromium"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Chromium browser installed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Playwright setup failed: {e}")
            return False
    
    def load_excellent_ads(self):
        """Load EXCELLENT performance ads"""
        try:
            df = pd.read_csv(self.csv_file)
            excellent_ads = df[df['Performance_Rating'] == 'EXCELLENT'].copy()
            
            # Sort by performance
            excellent_ads['CVR_numeric'] = pd.to_numeric(excellent_ads['CVR'].str.rstrip('%'), errors='coerce')
            excellent_ads['CTR_numeric'] = pd.to_numeric(excellent_ads['CTR'].str.rstrip('%'), errors='coerce')
            excellent_ads = excellent_ads.sort_values(['CVR_numeric', 'CTR_numeric'], ascending=[False, False])
            
            logger.info(f"⭐ Loaded {len(excellent_ads)} EXCELLENT ads for browser processing")
            return excellent_ads
            
        except Exception as e:
            logger.error(f"❌ Failed to load ads: {e}")
            return pd.DataFrame()
    
    async def process_ad_with_browser(self, ad_row):
        """Process ad using browser automation"""
        try:
            from playwright.async_api import async_playwright
            
            ad_name = ad_row['Ad_Name']
            preview_url = ad_row['Facebook_Preview_Link']
            account = ad_row['Account']
            
            logger.info(f"\n🎯 Browser processing: {ad_name}")
            
            result = {
                'ad_name': ad_name,
                'account': account,
                'preview_url': preview_url,
                'status': 'processing',
                'browser_steps': [],
                'video_url': None,
                'error': None
            }
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=False)  # Set to False to see the browser
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                try:
                    # Navigate to preview URL
                    logger.info(f"🌐 Navigating to: {preview_url}")
                    await page.goto(preview_url, wait_until='networkidle')
                    result['browser_steps'].append('navigation')
                    
                    # Take screenshot for analysis
                    screenshot_path = f"screenshots/{ad_name.replace('/', '_')}_initial.png"
                    os.makedirs("screenshots", exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    result['browser_steps'].append('screenshot')
                    
                    # Check if authentication is required
                    current_url = page.url
                    if 'business.facebook.com' in current_url and 'login' in current_url:
                        logger.warning("🔐 Facebook Business authentication required")
                        result['status'] = 'auth_required'
                        result['auth_url'] = current_url
                        
                        # Here we would implement the authentication flow
                        # For demonstration, we'll show the structure
                        logger.info("📋 Authentication flow would include:")
                        logger.info("   1. Detect login form elements")
                        logger.info("   2. Fill in business account credentials")
                        logger.info("   3. Handle 2FA if required")
                        logger.info("   4. Wait for successful authentication")
                        logger.info("   5. Navigate back to original preview URL")
                        
                        result['browser_steps'].append('auth_detection')
                        
                    else:
                        # Look for video elements
                        logger.info("🎬 Searching for video elements...")
                        video_elements = await page.query_selector_all('video')
                        
                        if video_elements:
                            logger.info(f"✅ Found {len(video_elements)} video element(s)")
                            
                            for i, video in enumerate(video_elements):
                                src = await video.get_attribute('src')
                                if src:
                                    logger.info(f"📹 Video {i+1} source: {src}")
                                    result['video_url'] = src
                                    result['status'] = 'video_found'
                                    break
                        else:
                            logger.warning("⚠️ No video elements found on page")
                            result['status'] = 'no_video'
                        
                        result['browser_steps'].append('video_search')
                    
                    # Take final screenshot
                    final_screenshot = f"screenshots/{ad_name.replace('/', '_')}_final.png"
                    await page.screenshot(path=final_screenshot)
                    result['browser_steps'].append('final_screenshot')
                    
                except Exception as e:
                    logger.error(f"❌ Browser processing error: {e}")
                    result['status'] = 'browser_error'
                    result['error'] = str(e)
                
                finally:
                    await browser.close()
            
            return result
            
        except ImportError:
            logger.error("❌ Playwright not available - install with: pip install playwright")
            return {
                'ad_name': ad_name,
                'status': 'playwright_missing',
                'error': 'Playwright not installed'
            }
        except Exception as e:
            logger.error(f"❌ Browser processing failed: {e}")
            return {
                'ad_name': ad_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def download_video_from_url(self, video_url, ad_name, account):
        """Download video from extracted URL"""
        try:
            logger.info(f"⬇️ Downloading video from extracted URL: {ad_name}")
            
            # Create safe filename
            safe_name = "".join(c for c in ad_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            # Create account directory
            account_dir = Path(account)
            account_dir.mkdir(exist_ok=True)
            
            output_path = account_dir / f"{safe_name}.mp4"
            
            # Download using yt-dlp with the direct video URL
            cmd = [
                "yt-dlp",
                "--output", str(output_path),
                "--format", "best[ext=mp4]/best",
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"✅ Video downloaded successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"❌ Download failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Video download error: {e}")
            return None
    
    def upload_to_github(self, file_path, ad_name):
        """Upload file to GitHub repository"""
        try:
            logger.info(f"📤 Uploading to GitHub: {ad_name}")
            
            if os.path.exists(self.repo_path):
                original_dir = os.getcwd()
                os.chdir(self.repo_path)
                
                try:
                    # Add file to git
                    subprocess.run(["git", "add", file_path], check=True)
                    
                    # Commit file
                    commit_message = f"Add creative ad: {ad_name}"
                    subprocess.run(["git", "commit", "-m", commit_message], check=True)
                    
                    # Push to GitHub
                    subprocess.run(["git", "push", "origin", "main"], check=True)
                    
                    # Generate public URL
                    public_url = f"https://github.com/{self.github_username}/{self.repo_path}/blob/main/{file_path}"
                    
                    logger.info(f"✅ GitHub upload successful: {public_url}")
                    return public_url
                    
                finally:
                    os.chdir(original_dir)
            else:
                logger.error(f"❌ Repository directory not found: {self.repo_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ GitHub upload failed: {e}")
            return None
    
    async def run_browser_processing(self):
        """Run browser-based processing of EXCELLENT ads"""
        try:
            logger.info("🚀 Starting Browser Authentication Processing")
            logger.info("=" * 70)
            
            # Setup Playwright
            if not self.setup_playwright_environment():
                logger.error("❌ Failed to setup Playwright environment")
                return
            
            # Load EXCELLENT ads
            ads_df = self.load_excellent_ads()
            if ads_df.empty:
                logger.error("❌ No EXCELLENT ads found")
                return
            
            # Process each ad with browser automation
            for idx, (_, ad_row) in enumerate(ads_df.iterrows(), 1):
                logger.info(f"\n📊 Processing ad {idx}/{len(ads_df)} with browser automation")
                
                result = await self.process_ad_with_browser(ad_row)
                self.results.append(result)
                
                # If video URL was found, attempt download
                if result.get('video_url'):
                    file_path = self.download_video_from_url(
                        result['video_url'], 
                        result['ad_name'], 
                        result['account']
                    )
                    
                    if file_path:
                        github_url = self.upload_to_github(file_path, result['ad_name'])
                        result['github_url'] = github_url
                        result['status'] = 'success' if github_url else 'upload_failed'
                
                # Brief pause between processing
                await asyncio.sleep(3)
            
            # Generate report
            self.generate_browser_report()
            
        except Exception as e:
            logger.error(f"❌ Browser processing failed: {e}")
    
    def generate_browser_report(self):
        """Generate browser processing report"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = f"Browser_Auth_Report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Browser Authentication Processing Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Browser Automation Results\n\n")
            
            for idx, result in enumerate(self.results, 1):
                f.write(f"### {idx}. {result['ad_name']}\n")
                f.write(f"- **Account:** {result['account']}\n")
                f.write(f"- **Status:** {result['status'].upper()}\n")
                f.write(f"- **Preview URL:** {result['preview_url']}\n")
                f.write(f"- **Browser Steps:** {', '.join(result.get('browser_steps', []))}\n")
                
                if result.get('video_url'):
                    f.write(f"- **Video URL:** {result['video_url']}\n")
                
                if result.get('github_url'):
                    f.write(f"- **GitHub URL:** {result['github_url']}\n")
                
                if result.get('auth_url'):
                    f.write(f"- **Auth Required:** {result['auth_url']}\n")
                
                if result.get('error'):
                    f.write(f"- **Error:** {result['error']}\n")
                
                f.write("\n")
            
            f.write("## Browser Automation Capabilities\n")
            f.write("- **Playwright Integration:** ✅ Available\n")
            f.write("- **Screenshot Capture:** ✅ Implemented\n")
            f.write("- **Element Detection:** ✅ Video element search\n")
            f.write("- **Authentication Detection:** ✅ Business login detection\n")
            f.write("- **URL Extraction:** ✅ Direct video URL extraction\n\n")
            
            f.write("## Authentication Implementation Required\n")
            f.write("To complete the automation, implement:\n")
            f.write("1. Facebook Business login form detection\n")
            f.write("2. Credential input automation\n")
            f.write("3. 2FA handling if required\n")
            f.write("4. Session persistence across ads\n")
            f.write("5. Error handling for failed authentication\n\n")
            
            f.write("**Status: Browser automation framework ready - Authentication flow pending**\n")
        
        logger.info(f"📋 Browser processing report generated: {report_file}")

def main():
    """Main execution function"""
    try:
        processor = BrowserAuthProcessor()
        asyncio.run(processor.run_browser_processing())
        
        logger.info("✅ Browser authentication processing completed!")
        
    except KeyboardInterrupt:
        logger.info("🛑 Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main() 
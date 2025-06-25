#!/usr/bin/env python3
"""
Live Creative Ads Processor
Processes EXCELLENT performance ads with real browser automation
"""

import pandas as pd
import os
import subprocess
import json
import time
from datetime import datetime
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveCreativeAdsProcessor:
    def __init__(self):
        self.csv_file = "TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv"
        self.repo_path = "creative-ads-repository"
        self.github_username = "lac5q"
        self.results = []
        
    def load_excellent_ads(self):
        """Load and prioritize EXCELLENT performance ads"""
        try:
            logger.info("🎯 Loading EXCELLENT performance creative ads...")
            
            df = pd.read_csv(self.csv_file)
            excellent_ads = df[df['Performance_Rating'] == 'EXCELLENT'].copy()
            
            # Sort by performance metrics
            excellent_ads['CVR_numeric'] = pd.to_numeric(excellent_ads['CVR'].str.rstrip('%'), errors='coerce')
            excellent_ads['CTR_numeric'] = pd.to_numeric(excellent_ads['CTR'].str.rstrip('%'), errors='coerce')
            excellent_ads = excellent_ads.sort_values(['CVR_numeric', 'CTR_numeric'], ascending=[False, False])
            
            logger.info(f"⭐ Found {len(excellent_ads)} EXCELLENT performance ads:")
            for idx, row in excellent_ads.iterrows():
                logger.info(f"  • {row['Ad_Name']} - CVR: {row['CVR']}, CTR: {row['CTR']}")
            
            return excellent_ads
            
        except Exception as e:
            logger.error(f"❌ Failed to load ads: {e}")
            return pd.DataFrame()
    
    def test_facebook_preview_access(self, preview_url, ad_name):
        """Test access to Facebook preview link"""
        try:
            logger.info(f"🔗 Testing preview access: {ad_name}")
            logger.info(f"   URL: {preview_url}")
            
            # Test with requests to see what we get
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(preview_url, headers=headers, allow_redirects=True, timeout=10)
            
            result = {
                'ad_name': ad_name,
                'preview_url': preview_url,
                'status_code': response.status_code,
                'final_url': response.url,
                'requires_auth': False,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': len(response.content)
            }
            
            # Check if redirected to login
            if 'business.facebook.com' in response.url or 'login' in response.url.lower():
                result['requires_auth'] = True
                logger.warning(f"🔐 Authentication required - redirected to: {response.url}")
            else:
                logger.info(f"✅ Direct access successful - Content type: {result['content_type']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Preview access test failed: {e}")
            return {
                'ad_name': ad_name,
                'preview_url': preview_url,
                'error': str(e),
                'requires_auth': True
            }
    
    def attempt_video_download(self, preview_url, ad_name, account):
        """Attempt to download video using yt-dlp"""
        try:
            logger.info(f"⬇️ Attempting video download: {ad_name}")
            
            # Create safe filename
            safe_name = "".join(c for c in ad_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            # Create account directory
            account_dir = Path(account)
            account_dir.mkdir(exist_ok=True)
            
            output_path = account_dir / f"{safe_name}.%(ext)s"
            
            # Try yt-dlp download
            cmd = [
                "yt-dlp",
                "--no-check-certificate",
                "--user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "--format", "best[ext=mp4]/best",
                "--output", str(output_path),
                preview_url
            ]
            
            logger.info(f"   Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ Download successful!")
                return {
                    'success': True,
                    'output_path': str(output_path),
                    'stdout': result.stdout
                }
            else:
                logger.warning(f"⚠️ Download failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timed out after 60 seconds")
            return {'success': False, 'error': 'Download timeout'}
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return {'success': False, 'error': str(e)}
    
    def upload_to_github(self, file_path, ad_name):
        """Upload file to GitHub repository"""
        try:
            logger.info(f"📤 Uploading to GitHub: {ad_name}")
            
            # Change to repository directory
            if os.path.exists(self.repo_path):
                os.chdir(self.repo_path)
                
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
            else:
                logger.error(f"❌ Repository directory not found: {self.repo_path}")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ GitHub upload failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return None
    
    def process_excellent_ad(self, ad_row):
        """Process a single EXCELLENT ad through the complete pipeline"""
        ad_name = ad_row['Ad_Name']
        preview_url = ad_row['Facebook_Preview_Link']
        account = ad_row['Account']
        cvr = ad_row['CVR']
        ctr = ad_row['CTR']
        
        logger.info(f"\n🎯 Processing EXCELLENT ad: {ad_name}")
        logger.info(f"📊 Performance: CVR {cvr}, CTR {ctr}")
        logger.info(f"🏢 Account: {account}")
        
        result = {
            'ad_name': ad_name,
            'account': account,
            'cvr': cvr,
            'ctr': ctr,
            'preview_url': preview_url,
            'status': 'processing',
            'steps_completed': [],
            'github_url': None,
            'error': None
        }
        
        try:
            # Step 1: Test preview access
            logger.info("🔍 Step 1: Testing preview link access...")
            access_result = self.test_facebook_preview_access(preview_url, ad_name)
            result['steps_completed'].append('preview_access_test')
            result['access_result'] = access_result
            
            # Step 2: Attempt video download
            logger.info("⬇️ Step 2: Attempting video download...")
            download_result = self.attempt_video_download(preview_url, ad_name, account)
            result['steps_completed'].append('download_attempt')
            result['download_result'] = download_result
            
            if download_result.get('success'):
                # Step 3: Upload to GitHub
                logger.info("📤 Step 3: Uploading to GitHub...")
                github_url = self.upload_to_github(download_result['output_path'], ad_name)
                result['steps_completed'].append('github_upload')
                result['github_url'] = github_url
                result['status'] = 'success' if github_url else 'upload_failed'
            else:
                result['status'] = 'download_failed'
                result['error'] = download_result.get('error', 'Unknown download error')
            
            logger.info(f"✅ Processing completed for: {ad_name}")
            
        except Exception as e:
            logger.error(f"❌ Processing failed for {ad_name}: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def run_live_processing(self):
        """Run live processing of EXCELLENT creative ads"""
        try:
            logger.info("🚀 Starting Live Creative Ads Processing")
            logger.info("=" * 70)
            
            # Load EXCELLENT ads
            ads_df = self.load_excellent_ads()
            if ads_df.empty:
                logger.error("❌ No EXCELLENT ads found")
                return
            
            # Process each EXCELLENT ad
            total_ads = len(ads_df)
            successful_downloads = 0
            successful_uploads = 0
            
            for idx, (_, ad_row) in enumerate(ads_df.iterrows(), 1):
                logger.info(f"\n📊 Processing ad {idx}/{total_ads}")
                
                result = self.process_excellent_ad(ad_row)
                self.results.append(result)
                
                if result['status'] == 'success':
                    successful_downloads += 1
                    successful_uploads += 1
                elif 'download_attempt' in result['steps_completed']:
                    if result.get('download_result', {}).get('success'):
                        successful_downloads += 1
                
                # Brief pause between processing
                time.sleep(2)
            
            # Generate comprehensive report
            self.generate_live_report(total_ads, successful_downloads, successful_uploads)
            
        except Exception as e:
            logger.error(f"❌ Live processing failed: {e}")
    
    def generate_live_report(self, total_ads, successful_downloads, successful_uploads):
        """Generate comprehensive live processing report"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = f"Live_Processing_Report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Live Creative Ads Processing Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Executive Summary\n")
            f.write(f"- **Total EXCELLENT Ads:** {total_ads}\n")
            f.write(f"- **Successful Downloads:** {successful_downloads}\n")
            f.write(f"- **Successful GitHub Uploads:** {successful_uploads}\n")
            f.write(f"- **Success Rate:** {(successful_uploads/total_ads)*100:.1f}%\n\n")
            
            f.write("## Processing Results\n\n")
            
            for idx, result in enumerate(self.results, 1):
                f.write(f"### {idx}. {result['ad_name']}\n")
                f.write(f"- **Account:** {result['account']}\n")
                f.write(f"- **Performance:** CVR {result['cvr']}, CTR {result['ctr']}\n")
                f.write(f"- **Status:** {result['status'].upper()}\n")
                f.write(f"- **Preview URL:** {result['preview_url']}\n")
                f.write(f"- **Steps Completed:** {', '.join(result['steps_completed'])}\n")
                
                if result.get('github_url'):
                    f.write(f"- **GitHub URL:** {result['github_url']}\n")
                
                if result.get('error'):
                    f.write(f"- **Error:** {result['error']}\n")
                
                # Access result details
                if 'access_result' in result:
                    access = result['access_result']
                    f.write(f"- **Access Test:**\n")
                    f.write(f"  - Status Code: {access.get('status_code', 'N/A')}\n")
                    f.write(f"  - Requires Auth: {access.get('requires_auth', 'Unknown')}\n")
                    f.write(f"  - Final URL: {access.get('final_url', 'N/A')}\n")
                
                f.write("\n")
            
            f.write("## Technical Findings\n")
            f.write("### Facebook Preview Links\n")
            auth_required = sum(1 for r in self.results if r.get('access_result', {}).get('requires_auth'))
            f.write(f"- **Authentication Required:** {auth_required}/{total_ads} ads\n")
            f.write("- **Common Pattern:** Most preview links redirect to business.facebook.com login\n")
            f.write("- **Security Model:** Facebook requires business account authentication for ad previews\n\n")
            
            f.write("### Download Attempts\n")
            f.write("- **Tool Used:** yt-dlp with custom user agent\n")
            f.write("- **Success Rate:** Depends on authentication bypass\n")
            f.write("- **Primary Blocker:** Facebook business login requirement\n\n")
            
            f.write("## Recommendations\n")
            f.write("1. **Implement Facebook Business Authentication:**\n")
            f.write("   - Use browser automation to handle login flow\n")
            f.write("   - Store session cookies for batch processing\n")
            f.write("   - Handle 2FA if required\n\n")
            
            f.write("2. **Alternative Access Methods:**\n")
            f.write("   - Explore Meta Marketing API for direct creative access\n")
            f.write("   - Use Facebook Graph API for video asset retrieval\n")
            f.write("   - Consider Facebook Business SDK integration\n\n")
            
            f.write("3. **Infrastructure Optimization:**\n")
            f.write("   - Implement retry logic for failed downloads\n")
            f.write("   - Add progress tracking and resumption\n")
            f.write("   - Enhance error handling and reporting\n\n")
            
            f.write(f"## Next Steps\n")
            f.write(f"- Implement Facebook Business authentication\n")
            f.write(f"- Test browser automation with login flow\n")
            f.write(f"- Validate video extraction and download\n")
            f.write(f"- Complete GitHub upload automation\n")
            f.write(f"- Scale to additional creative ads\n\n")
            
            f.write("**Status: Live testing completed - Authentication implementation required for full automation**\n")
        
        logger.info(f"📋 Live processing report generated: {report_file}")
        
        # Display summary
        logger.info("\n" + "="*60)
        logger.info("🎯 LIVE PROCESSING SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ EXCELLENT Ads Processed: {total_ads}")
        logger.info(f"⬇️ Successful Downloads: {successful_downloads}")
        logger.info(f"📤 GitHub Uploads: {successful_uploads}")
        logger.info(f"📊 Success Rate: {(successful_uploads/total_ads)*100:.1f}%")
        logger.info(f"🔐 Authentication Required: {auth_required}/{total_ads} ads")
        logger.info("="*60)

def main():
    """Main execution function"""
    try:
        processor = LiveCreativeAdsProcessor()
        processor.run_live_processing()
        
        logger.info("✅ Live creative ads processing completed!")
        
    except KeyboardInterrupt:
        logger.info("🛑 Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main() 
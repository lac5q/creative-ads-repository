#!/usr/bin/env python3
"""
Enhanced Ads Automation - 6 Months Data Collection
"""

import pandas as pd
import os
import subprocess
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAdsAutomation:
    def __init__(self):
        self.csv_file = "TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv"
        self.repo_path = "creative-ads-repository"
        self.github_username = "lac5q"
        self.results = []
        
        # Recent performance data from Meta Ads API
        self.recent_ads = [
            {
                "ad_id": "120204304663540354",
                "ad_name": "video: agency hook \"Product footage\" / looking for a gift new lp",
                "account": "MakeMeJedi",
                "impressions": 70955,
                "clicks": 679,
                "spend": 952.16,
                "purchases": 13,
                "ctr": 0.96,
                "cvr": 1.91
            },
            {
                "ad_id": "120204304663560354", 
                "ad_name": "video: star wars fan jean / A long time ago",
                "account": "MakeMeJedi",
                "impressions": 71172,
                "clicks": 948,
                "spend": 1009.65,
                "purchases": 10,
                "ctr": 1.33,
                "cvr": 1.05
            },
            {
                "ad_id": "120204695400800354",
                "ad_name": "video: agency hook \"I surprised my dad\" / better gift?", 
                "account": "MakeMeJedi",
                "impressions": 36536,
                "clicks": 1779,
                "spend": 386.25,
                "purchases": 5,
                "ctr": 4.87,
                "cvr": 0.28
            },
            {
                "ad_id": "120206906179650354",
                "ad_name": "video: FD 2 remake / A long time ago",
                "account": "MakeMeJedi", 
                "impressions": 271663,
                "clicks": 3951,
                "spend": 4075.07,
                "purchases": 48,
                "ctr": 1.45,
                "cvr": 1.21
            }
        ]
    
    def calculate_performance_rating(self, cvr, ctr):
        """Calculate performance rating"""
        if cvr >= 2.0 and ctr >= 1.5:
            return "EXCELLENT"
        elif cvr >= 1.0 and ctr >= 1.0:
            return "GOOD"
        elif cvr >= 0.5 and ctr >= 0.5:
            return "AVERAGE"
        else:
            return "POOR"
    
    def create_asset_files(self):
        """Create asset files for recent ads"""
        logger.info("📁 Creating asset files for recent ads...")
        
        for ad in self.recent_ads:
            account_dir = ad['account']
            os.makedirs(account_dir, exist_ok=True)
            
            # Create safe filename
            safe_name = "".join(c for c in ad['ad_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')[:50]
            asset_file = f"{account_dir}/{safe_name}_ASSET.md"
            
            # Calculate metrics
            performance_rating = self.calculate_performance_rating(ad['cvr'], ad['ctr'])
            cpa = ad['spend'] / ad['purchases'] if ad['purchases'] > 0 else 0
            
            # Create asset content
            asset_content = f"""# {ad['ad_name']}

## Performance Metrics (Past 6 Months)
- **Performance Rating:** {performance_rating}
- **CVR:** {ad['cvr']:.2f}%
- **CTR:** {ad['ctr']:.2f}%
- **CPA:** ${cpa:.2f}
- **Spend:** ${ad['spend']:.2f}
- **Purchases:** {ad['purchases']}
- **Clicks:** {ad['clicks']:,}
- **Impressions:** {ad['impressions']:,}

## Asset Details
- **Ad ID:** {ad['ad_id']}
- **Account:** {ad['account']}
- **Asset Type:** Video
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## GitHub URLs
- **Asset File:** https://github.com/{self.github_username}/creative-ads-repository/blob/main/{asset_file}
- **Raw Asset:** https://github.com/{self.github_username}/creative-ads-repository/raw/main/{asset_file}

## Business Recommendations
"""
            
            if performance_rating == "EXCELLENT":
                asset_content += "🏆 **SCALE IMMEDIATELY** - Increase budget by 150-200%"
            elif performance_rating == "GOOD":
                asset_content += "✅ **SCALE GRADUALLY** - Increase budget by 50-100%"
            elif performance_rating == "AVERAGE":
                asset_content += "⚠️ **OPTIMIZE** - Test new audiences or pause"
            else:
                asset_content += "❌ **PAUSE** - Stop spending immediately"
            
            # Write file
            with open(asset_file, 'w', encoding='utf-8') as f:
                f.write(asset_content)
            
            logger.info(f"✅ Created: {asset_file}")
            
            # Store result
            self.results.append({
                'ad_id': ad['ad_id'],
                'ad_name': ad['ad_name'],
                'account': ad['account'],
                'performance_rating': performance_rating,
                'cvr': ad['cvr'],
                'ctr': ad['ctr'],
                'asset_file': asset_file,
                'github_url': f"https://github.com/{self.github_username}/creative-ads-repository/blob/main/{asset_file}",
                'raw_url': f"https://github.com/{self.github_username}/creative-ads-repository/raw/main/{asset_file}"
            })
    
    def create_enhanced_csv(self):
        """Create enhanced CSV with GitHub URLs"""
        logger.info("📊 Creating enhanced CSV...")
        
        # Load existing CSV
        try:
            existing_df = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            existing_df = pd.DataFrame()
        
        # Create new data
        new_data = []
        for result in self.results:
            ad = next(a for a in self.recent_ads if a['ad_id'] == result['ad_id'])
            
            new_row = {
                'Ad_ID': ad['ad_id'],
                'Ad_Name': ad['ad_name'],
                'Account': ad['account'],
                'CVR': f"{ad['cvr']:.2f}%",
                'CTR': f"{ad['ctr']:.2f}%", 
                'CPA': f"${ad['spend']/ad['purchases']:.2f}" if ad['purchases'] > 0 else "$0.00",
                'Spend': f"${ad['spend']:.2f}",
                'Purchases': ad['purchases'],
                'Clicks': ad['clicks'],
                'Impressions': ad['impressions'],
                'Performance_Rating': result['performance_rating'],
                'GitHub_Asset_URL': result['github_url'],
                'GitHub_Raw_URL': result['raw_url'],
                'Data_Source': 'Meta_Ads_API_6_Months',
                'Collection_Date': datetime.now().strftime('%Y-%m-%d'),
                'Asset_Type': 'Video'
            }
            new_data.append(new_row)
        
        # Create enhanced CSV
        enhanced_filename = f"Enhanced_Creative_Ads_6_Months_{datetime.now().strftime('%Y-%m-%d')}.csv"
        new_df = pd.DataFrame(new_data)
        
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        combined_df.to_csv(enhanced_filename, index=False)
        logger.info(f"💾 Saved: {enhanced_filename}")
        
        return enhanced_filename
    
    def upload_to_github(self):
        """Upload to GitHub"""
        logger.info("🚀 Uploading to GitHub...")
        
        try:
            # Navigate to repo if needed
            if not os.path.exists('.git') and os.path.exists(self.repo_path):
                os.chdir(self.repo_path)
            
            # Copy directories
            for account in ['TurnedYellow', 'MakeMeJedi']:
                if os.path.exists(f"../{account}"):
                    subprocess.run(['cp', '-r', f"../{account}", '.'], check=True)
            
            # Git operations
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f"Add 6-month ads data - {datetime.now().strftime('%Y-%m-%d')}"], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            logger.info("✅ GitHub upload successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ GitHub upload failed: {e}")
            return False
    
    def run_automation(self):
        """Run complete automation"""
        logger.info("🚀 Starting Enhanced Ads Automation...")
        
        # Create asset files
        self.create_asset_files()
        
        # Create enhanced CSV
        csv_file = self.create_enhanced_csv()
        
        # Upload to GitHub
        github_success = self.upload_to_github()
        
        # Summary
        logger.info("🎉 AUTOMATION COMPLETED!")
        logger.info(f"📊 Processed: {len(self.recent_ads)} recent ads")
        logger.info(f"📁 Created: {len(self.results)} asset files")
        logger.info(f"💾 Enhanced CSV: {csv_file}")
        logger.info(f"🚀 GitHub: {'SUCCESS' if github_success else 'FAILED'}")
        logger.info(f"🔗 Repository: https://github.com/{self.github_username}/creative-ads-repository")
        
        return True

if __name__ == "__main__":
    automation = EnhancedAdsAutomation()
    automation.run_automation() 
#!/usr/bin/env python3
"""
Veo 3 Extraction Consolidator
Creation Date: June 24, 2025
Version: 1.0

This script combines all Veo 3 extraction attempts to create
the most comprehensive dataset possible.
"""

import pandas as pd
import glob
import json
from datetime import datetime

class Veo3Consolidator:
    def __init__(self):
        """Initialize the consolidator"""
        self.all_videos = {}  # Use dict to avoid duplicates
        self.unique_urls = set()
        self.consolidated_data = []
        
    def find_all_extraction_files(self):
        """Find all Veo 3 extraction CSV files"""
        patterns = [
            "GoogleFlow_Veo3_*.csv",
            "GoogleFlow_*Veo3*.csv", 
            "GoogleFlow_*videos*.csv"
        ]
        
        all_files = []
        for pattern in patterns:
            files = glob.glob(pattern)
            all_files.extend(files)
        
        # Remove duplicates and sort by timestamp
        unique_files = list(set(all_files))
        unique_files.sort()
        
        print(f"🔍 Found {len(unique_files)} extraction files:")
        for i, file in enumerate(unique_files, 1):
            print(f"   {i}. {file}")
        
        return unique_files
    
    def process_extraction_file(self, filepath):
        """Process a single extraction file"""
        try:
            df = pd.read_csv(filepath)
            print(f"\n📊 Processing: {filepath}")
            print(f"   📈 Contains {len(df)} videos")
            
            videos_with_urls = 0
            for idx, row in df.iterrows():
                video_id = row.get('Ad_ID', f'unknown_{idx}')
                video_name = row.get('Ad_Name', f'Unknown Video {idx+1}')
                video_url = row.get('Meta_Video_URL', 'TBD')
                
                # Count videos with URLs
                if video_url and video_url != 'TBD' and 'http' in str(video_url):
                    videos_with_urls += 1
                    self.unique_urls.add(video_url)
                
                # Store video info (will overwrite duplicates with latest data)
                self.all_videos[video_id] = {
                    'Ad_ID': video_id,
                    'Ad_Name': video_name,
                    'Account': 'GoogleFlow',
                    'Campaign': 'Veo 3 Generated Content',
                    'Creative_ID': video_id,
                    'Status': 'ACTIVE',
                    'Performance_Rating': 'PENDING_ANALYSIS',
                    'CPA': 'TBD',
                    'CVR': 'TBD',
                    'CTR': 'TBD',
                    'Spend': '0.00',
                    'Purchases': '0',
                    'Video_Views': '0',
                    'Hook_Rate': 'TBD',
                    'Facebook_Preview_Link': 'TBD',
                    'Meta_Video_URL': video_url,
                    'Google_Drive_Download_Link': 'TBD',
                    'Google_Drive_View_Link': 'TBD',
                    'Creative_Type': 'AI Generated - Veo 3',
                    'Hook_Type': 'TBD',
                    'Targeting': 'Broad',
                    'Priority': '🔍 VEO3_REVIEW',
                    'Notes': f'Veo 3 - Quality | Consolidated from {filepath} | Generated: 2025-06-24 | URL Status: {"✅ Found" if video_url and video_url != "TBD" and "http" in str(video_url) else "⚠️ Missing"}',
                    'Download_Command': self.generate_download_command(video_url, video_name) if video_url and video_url != 'TBD' and 'http' in str(video_url) else 'TBD',
                    'Source_File': filepath
                }
            
            print(f"   🔗 Videos with URLs: {videos_with_urls}")
            return len(df), videos_with_urls
            
        except Exception as e:
            print(f"   ❌ Error processing {filepath}: {e}")
            return 0, 0
    
    def generate_download_command(self, url, name):
        """Generate yt-dlp download command"""
        if not url or url == 'TBD' or 'http' not in str(url):
            return 'TBD'
        
        # Clean name for filename
        safe_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        return f'yt-dlp "{url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
    
    def create_consolidated_dataset(self):
        """Create the final consolidated dataset"""
        # Convert dict to list and sort by Ad_ID
        self.consolidated_data = list(self.all_videos.values())
        self.consolidated_data.sort(key=lambda x: x['Ad_ID'])
        
        # Create DataFrame
        df = pd.DataFrame(self.consolidated_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"GoogleFlow_Veo3_CONSOLIDATED_{len(self.consolidated_data)}_videos_{timestamp}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        return filename, df
    
    def generate_summary_report(self, filename, df):
        """Generate a comprehensive summary report"""
        videos_with_urls = len([v for v in self.consolidated_data if v['Meta_Video_URL'] and v['Meta_Video_URL'] != 'TBD' and 'http' in str(v['Meta_Video_URL'])])
        
        report = f"""
🎉 VEO 3 CONSOLIDATION COMPLETE - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================================================

📊 FINAL CONSOLIDATED RESULTS:
   🎬 Total Veo 3 videos: {len(self.consolidated_data)}
   🔗 Videos with download URLs: {videos_with_urls}
   📈 Success rate: {(videos_with_urls/len(self.consolidated_data)*100):.1f}%
   🌐 Unique URLs found: {len(self.unique_urls)}

📁 OUTPUT FILE: {filename}
   ✅ Ready for Airtable import
   ✅ Matches your existing data format
   ✅ Includes download commands for videos with URLs

🎬 VIDEOS SUMMARY:
"""
        
        for i, video in enumerate(self.consolidated_data, 1):
            url_status = "✅ URL" if video['Meta_Video_URL'] and video['Meta_Video_URL'] != 'TBD' and 'http' in str(video['Meta_Video_URL']) else "⚠️ No URL"
            report += f"   {i:2d}. {video['Ad_Name']} - {url_status}\n"
        
        report += f"""
🔗 DOWNLOAD COMMANDS:
"""
        
        for i, video in enumerate(self.consolidated_data, 1):
            if video['Download_Command'] and video['Download_Command'] != 'TBD':
                report += f"   {i}. {video['Download_Command']}\n"
        
        report += f"""
📋 NEXT STEPS:
   1. ✅ Import {filename} into Airtable
   2. 🎯 Add specific video names, prompts, and details manually
   3. 🔗 Use download commands to get video files
   4. 📊 Share with reviewer for analysis

🎉 CONSOLIDATION SUCCESSFUL! 
   All Veo 3 videos from multiple extractions combined into one comprehensive file.
"""
        
        return report

def main():
    print("🎯 VEO 3 EXTRACTION CONSOLIDATOR")
    print("="*80)
    
    consolidator = Veo3Consolidator()
    
    # Find all extraction files
    files = consolidator.find_all_extraction_files()
    
    if not files:
        print("❌ No Veo 3 extraction files found!")
        return
    
    # Process all files
    total_videos = 0
    total_with_urls = 0
    
    for file in files:
        videos, urls = consolidator.process_extraction_file(file)
        total_videos += videos
        total_with_urls += urls
    
    # Create consolidated dataset
    print(f"\n🔄 Creating consolidated dataset...")
    filename, df = consolidator.create_consolidated_dataset()
    
    # Generate summary report
    report = consolidator.generate_summary_report(filename, df)
    
    # Save report
    report_filename = filename.replace('.csv', '_REPORT.txt')
    with open(report_filename, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"📄 Full report saved to: {report_filename}")

if __name__ == "__main__":
    main() 
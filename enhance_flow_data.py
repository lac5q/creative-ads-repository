#!/usr/bin/env python3
"""
Enhanced Google Flow Data Collector
Creation Date: June 24, 2025
Version: 1.0

This script helps enhance the basic extracted data with detailed information
about each video from your Google Flow project.
"""

import pandas as pd
import json
from datetime import datetime
import os

class FlowDataEnhancer:
    def __init__(self, csv_file):
        """Initialize with the base CSV file"""
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.enhanced_data = []
        
    def display_current_data(self):
        """Display current data for reference"""
        print("\n" + "="*80)
        print("CURRENT DATA TO ENHANCE")
        print("="*80)
        for idx, row in self.df.iterrows():
            print(f"\nVideo {idx + 1}:")
            print(f"  ID: {row['Ad_ID']}")
            print(f"  Name: {row['Ad_Name']}")
            print(f"  Notes: {row['Notes']}")
        print("="*80)
        
    def get_creative_type_choice(self):
        """Get creative type from user"""
        print("\n📋 CREATIVE TYPES:")
        creative_types = {
            '1': 'Influencer Testimonial',
            '2': 'Lifestyle', 
            '3': 'Product Demo',
            '4': 'Reaction Video',
            '5': 'Process Demo',
            '6': 'Transformation',
            '7': 'Celebrity',
            '8': 'Star Wars',
            '9': 'Comedy/Humor',
            '10': 'Educational',
            '11': 'Other'
        }
        
        for key, value in creative_types.items():
            print(f"  {key}. {value}")
            
        while True:
            choice = input("\nSelect Creative Type (1-11): ").strip()
            if choice in creative_types:
                return creative_types[choice]
            print("❌ Invalid choice. Please select 1-11.")
    
    def get_hook_type_choice(self):
        """Get hook type from user"""
        print("\n🎣 HOOK TYPES:")
        hook_types = {
            '1': 'Authority Hook',
            '2': 'Gifting/Emotional',
            '3': 'Problem/Solution',
            '4': 'Reaction Hook',
            '5': 'Custom Hook',
            '6': 'How-To',
            '7': 'Family',
            '8': 'Before/After',
            '9': 'Celebrity Comp',
            '10': 'Curiosity Gap',
            '11': 'Shock/Surprise',
            '12': 'Other'
        }
        
        for key, value in hook_types.items():
            print(f"  {key}. {value}")
            
        while True:
            choice = input("\nSelect Hook Type (1-12): ").strip()
            if choice in hook_types:
                return hook_types[choice]
            print("❌ Invalid choice. Please select 1-12.")
    
    def collect_video_details(self, video_num, current_row):
        """Collect enhanced details for a specific video"""
        print(f"\n{'='*60}")
        print(f"ENHANCING VIDEO {video_num}")
        print(f"{'='*60}")
        print(f"Current ID: {current_row['Ad_ID']}")
        print(f"Current Name: {current_row['Ad_Name']}")
        
        # Enhanced data collection
        enhanced_row = current_row.copy()
        
        print("\n🎬 VIDEO DETAILS:")
        print("Look at your Google Flow project and provide the following:")
        
        # Video name
        new_name = input(f"\nActual video name/title (or press ENTER to keep current): ").strip()
        if new_name:
            enhanced_row['Ad_Name'] = f"video: Flow Generated / {new_name}"
        
        # Original prompt
        prompt = input("Original prompt used to generate this video: ").strip()
        
        # Video URL
        video_url = input("Video URL (if available for download): ").strip()
        if video_url:
            enhanced_row['Meta_Video_URL'] = video_url
            # Generate download command
            safe_name = new_name.replace(' ', '_').replace('/', '_') if new_name else f"Flow_Video_{video_num}"
            enhanced_row['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
        
        # Creative classification
        enhanced_row['Creative_Type'] = self.get_creative_type_choice()
        enhanced_row['Hook_Type'] = self.get_hook_type_choice()
        
        # Additional details
        duration = input("\nVideo duration (optional): ").strip()
        additional_notes = input("Additional notes about this video (optional): ").strip()
        
        # Update notes
        notes_parts = [
            f"Original Prompt: {prompt}" if prompt else "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            f"Duration: {duration}" if duration else "",
            f"Additional Notes: {additional_notes}" if additional_notes else ""
        ]
        enhanced_row['Notes'] = " | ".join([part for part in notes_parts if part])
        
        return enhanced_row
    
    def enhance_all_videos(self):
        """Enhance all videos with detailed information"""
        self.display_current_data()
        
        print(f"\n🚀 Ready to enhance {len(self.df)} videos!")
        print("For each video, you'll provide:")
        print("  • Actual video name")
        print("  • Original prompt")
        print("  • Video URL (if available)")
        print("  • Creative type classification")
        print("  • Hook type classification")
        print("  • Additional details")
        
        proceed = input(f"\nEnhance all {len(self.df)} videos? (y/n): ").strip().lower()
        if proceed != 'y':
            print("❌ Enhancement cancelled.")
            return False
        
        for idx, row in self.df.iterrows():
            enhanced_row = self.collect_video_details(idx + 1, row)
            self.enhanced_data.append(enhanced_row)
            
            # Ask if user wants to continue
            if idx < len(self.df) - 1:
                continue_choice = input(f"\n✅ Video {idx + 1} enhanced! Continue to next video? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("⚠️ Enhancement stopped by user.")
                    break
        
        return True
    
    def save_enhanced_data(self):
        """Save the enhanced data to a new CSV file"""
        if not self.enhanced_data:
            print("❌ No enhanced data to save.")
            return None
        
        # Create enhanced DataFrame
        enhanced_df = pd.DataFrame(self.enhanced_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'GoogleFlow_Creative_Ads_Enhanced_{timestamp}.csv'
        
        # Save to CSV
        enhanced_df.to_csv(filename, index=False)
        
        # Also save as JSON for backup
        json_filename = filename.replace('.csv', '.json')
        enhanced_df.to_json(json_filename, orient='records', indent=2)
        
        return filename
    
    def print_summary(self):
        """Print summary of enhanced data"""
        if not self.enhanced_data:
            print("❌ No enhanced data available.")
            return
        
        print(f"\n{'='*80}")
        print("ENHANCEMENT SUMMARY")
        print(f"{'='*80}")
        print(f"Total videos enhanced: {len(self.enhanced_data)}")
        print(f"Enhancement completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for i, video in enumerate(self.enhanced_data, 1):
            print(f"\n🎬 Video {i}:")
            print(f"   Name: {video.get('Ad_Name', 'N/A')}")
            print(f"   Type: {video.get('Creative_Type', 'N/A')}")
            print(f"   Hook: {video.get('Hook_Type', 'N/A')}")
            print(f"   URL: {'Available' if video.get('Meta_Video_URL', 'TBD') != 'TBD' else 'Not Available'}")

def main():
    """Main execution function"""
    print("🎬 Google Flow Data Enhancer")
    print("="*50)
    
    # Find the most recent CSV file
    csv_files = [f for f in os.listdir('.') if f.startswith('GoogleFlow_Creative_Ads_Analysis_') and f.endswith('.csv')]
    if not csv_files:
        print("❌ No GoogleFlow CSV files found. Please run the extractor first.")
        return
    
    # Use the most recent file
    csv_file = sorted(csv_files)[-1]
    print(f"📁 Using file: {csv_file}")
    
    try:
        enhancer = FlowDataEnhancer(csv_file)
        
        if enhancer.enhance_all_videos():
            filename = enhancer.save_enhanced_data()
            if filename:
                enhancer.print_summary()
                print(f"\n🎉 Enhanced data saved to: {filename}")
                print("✅ Ready for Airtable import!")
            else:
                print("❌ Failed to save enhanced data.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 
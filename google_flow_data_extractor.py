#!/usr/bin/env python3
"""
Google Flow Data Extractor
Creation Date: January 18, 2025
Version: 1.0

This script helps extract video data from Google Flow projects
and formats it for Airtable import.

Requirements:
- selenium
- pandas
- beautifulsoup4
- webdriver-manager
"""

import json
import csv
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleFlowExtractor:
    def __init__(self, headless=False):
        """Initialize the extractor with Chrome webdriver"""
        self.setup_driver(headless)
        self.data = []
        self.base_ad_id = 300001000000000  # Starting ID for GoogleFlow content
        
    def setup_driver(self, headless=False):
        """Setup Chrome webdriver with necessary options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if headless:
            options.add_argument('--headless')
            
        # Add user data directory to maintain login session
        # options.add_argument('--user-data-dir=/tmp/chrome_user_data')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login_prompt(self):
        """Prompt user to login manually"""
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("1. The browser will open to Google Flow")
        print("2. Please log in with your Google account")
        print("3. Navigate to your Flow project")
        print("4. Press ENTER here when you're ready to continue...")
        print("="*60)
        
    def extract_flow_data(self, project_url):
        """Extract data from Google Flow project"""
        try:
            logger.info(f"Opening Flow project: {project_url}")
            self.driver.get(project_url)
            
            # Prompt for manual login
            self.login_prompt()
            input("Press ENTER when you're logged in and ready to continue...")
            
            # Wait for page to load
            logger.info("Waiting for Flow project to load...")
            time.sleep(10)
            
            # Try to find video elements (these selectors may need adjustment)
            video_selectors = [
                '[data-testid*="video"]',
                '.video-card',
                '.flow-video',
                '[class*="video"]',
                'video',
                '.media-item'
            ]
            
            videos_found = []
            for selector in video_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        videos_found.extend(elements)
                        break
                except:
                    continue
            
            if not videos_found:
                logger.warning("No video elements found. Manual extraction required.")
                self.manual_extraction_mode()
                return
                
            # Extract data from found videos
            for i, video_element in enumerate(videos_found):
                video_data = self.extract_video_data(video_element, i)
                if video_data:
                    self.data.append(video_data)
                    
            logger.info(f"Extracted data from {len(self.data)} videos")
            
        except Exception as e:
            logger.error(f"Error extracting Flow data: {str(e)}")
            self.manual_extraction_mode()
            
    def manual_extraction_mode(self):
        """Guide user through manual data extraction"""
        print("\n" + "="*60)
        print("MANUAL EXTRACTION MODE")
        print("="*60)
        print("Since automatic extraction isn't working, let's collect data manually.")
        print("Please look at your Flow project and provide the following information:")
        print("="*60)
        
        video_count = input("How many videos are in your Flow project? ")
        try:
            video_count = int(video_count)
        except ValueError:
            video_count = 1
            
        for i in range(video_count):
            print(f"\n--- VIDEO {i+1} ---")
            video_data = self.collect_manual_video_data(i)
            self.data.append(video_data)
            
    def collect_manual_video_data(self, index):
        """Collect video data manually from user input"""
        video_data = {}
        
        # Basic info
        video_data['Ad_ID'] = self.base_ad_id + index + 1
        video_data['Ad_Name'] = input("Video name/title: ").strip()
        video_data['Original_Prompt'] = input("Original prompt used: ").strip()
        video_data['Video_URL'] = input("Video URL (if available): ").strip()
        
        # Classification
        print("\nCreative Types:")
        print("1. Influencer Testimonial  2. Lifestyle  3. Product Demo")
        print("4. Reaction Video  5. Process Demo  6. Transformation")
        print("7. Celebrity  8. Star Wars  9. Other")
        
        creative_type_map = {
            '1': 'Influencer Testimonial', '2': 'Lifestyle', '3': 'Product Demo',
            '4': 'Reaction Video', '5': 'Process Demo', '6': 'Transformation',
            '7': 'Celebrity', '8': 'Star Wars', '9': 'Other'
        }
        
        creative_choice = input("Select Creative Type (1-9): ").strip()
        video_data['Creative_Type'] = creative_type_map.get(creative_choice, 'Other')
        
        print("\nHook Types:")
        print("1. Authority Hook  2. Gifting/Emotional  3. Problem/Solution")
        print("4. Reaction Hook  5. Custom Hook  6. How-To")
        print("7. Family  8. Before/After  9. Celebrity Comp  10. Other")
        
        hook_type_map = {
            '1': 'Authority Hook', '2': 'Gifting/Emotional', '3': 'Problem/Solution',
            '4': 'Reaction Hook', '5': 'Custom Hook', '6': 'How-To',
            '7': 'Family', '8': 'Before/After', '9': 'Celebrity Comp', '10': 'Other'
        }
        
        hook_choice = input("Select Hook Type (1-10): ").strip()
        video_data['Hook_Type'] = hook_type_map.get(hook_choice, 'Other')
        
        # Additional details
        video_data['Duration'] = input("Video duration (optional): ").strip()
        video_data['Additional_Notes'] = input("Additional notes (optional): ").strip()
        
        return video_data
        
    def extract_video_data(self, element, index):
        """Extract data from a video element"""
        try:
            video_data = {
                'Ad_ID': self.base_ad_id + index + 1,
                'Creative_ID': self.base_ad_id + index + 1,
                'Account': 'GoogleFlow',
                'Campaign': 'Flow Generated Content',
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
                'Google_Drive_Download_Link': 'TBD',
                'Google_Drive_View_Link': 'TBD',
                'Targeting': 'Broad',
                'Priority': '🔍 NEEDS_REVIEW'
            }
            
            # Try to extract title/name
            title_selectors = ['title', '[data-title]', '.title', '.name', 'h1', 'h2', 'h3']
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    video_data['Ad_Name'] = f"video: Flow Generated / {title_elem.text.strip()}"
                    break
                except:
                    continue
                    
            if 'Ad_Name' not in video_data:
                video_data['Ad_Name'] = f"video: Flow Generated / Video {index + 1}"
            
            # Try to extract video URL
            try:
                video_elem = element.find_element(By.TAG_NAME, 'video')
                video_url = video_elem.get_attribute('src')
                if video_url:
                    video_data['Meta_Video_URL'] = video_url
            except:
                video_data['Meta_Video_URL'] = 'TBD'
                
            # Placeholder for prompt extraction (would need specific selectors)
            video_data['Notes'] = f"Generated: {datetime.now().strftime('%Y-%m-%d')} | Flow Project Video {index + 1}"
            
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting video data: {str(e)}")
            return None
            
    def format_for_airtable(self):
        """Format extracted data for Airtable import"""
        if not self.data:
            logger.warning("No data to format")
            return None
            
        # Define the exact column order from the user's CSV
        columns = [
            'Ad_ID', 'Ad_Name', 'Account', 'Campaign', 'Creative_ID', 'Status',
            'Performance_Rating', 'CPA', 'CVR', 'CTR', 'Spend', 'Purchases',
            'Video_Views', 'Hook_Rate', 'Facebook_Preview_Link', 'Meta_Video_URL',
            'Google_Drive_Download_Link', 'Google_Drive_View_Link', 'Creative_Type',
            'Hook_Type', 'Targeting', 'Priority', 'Notes', 'Download_Command'
        ]
        
        formatted_data = []
        for item in self.data:
            row = {}
            for col in columns:
                if col == 'Download_Command' and item.get('Meta_Video_URL', 'TBD') != 'TBD':
                    # Generate download command if video URL is available
                    video_name = item.get('Ad_Name', 'Flow_Video').replace('video: ', '').replace('/', '_')
                    row[col] = f'yt-dlp "{item["Meta_Video_URL"]}" -f "best[ext=mp4]" -o "{video_name}.%(ext)s"'
                else:
                    row[col] = item.get(col, 'TBD')
            formatted_data.append(row)
            
        return formatted_data
        
    def save_to_csv(self, filename=None):
        """Save extracted data to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Creative_Ads_Analysis_{timestamp}.csv'
            
        formatted_data = self.format_for_airtable()
        if not formatted_data:
            logger.error("No data to save")
            return None
            
        df = pd.DataFrame(formatted_data)
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        
        # Also save raw data for debugging
        raw_filename = filename.replace('.csv', '_raw.json')
        with open(raw_filename, 'w') as f:
            json.dump(self.data, f, indent=2)
            
        return filename
        
    def print_summary(self):
        """Print summary of extracted data"""
        if not self.data:
            print("No data extracted.")
            return
            
        print(f"\n{'='*60}")
        print(f"EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total videos processed: {len(self.data)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for i, item in enumerate(self.data, 1):
            print(f"\nVideo {i}:")
            print(f"  Name: {item.get('Ad_Name', 'N/A')}")
            print(f"  Type: {item.get('Creative_Type', 'N/A')}")
            print(f"  Hook: {item.get('Hook_Type', 'N/A')}")
            print(f"  URL: {item.get('Meta_Video_URL', 'N/A')}")
            
    def close(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main execution function"""
    print("Google Flow Data Extractor")
    print("=" * 40)
    
    project_url = input("Enter your Google Flow project URL: ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = GoogleFlowExtractor(headless=False)
    
    try:
        extractor.extract_flow_data(project_url)
        extractor.print_summary()
        
        if extractor.data:
            filename = extractor.save_to_csv()
            print(f"\n✅ Data exported to: {filename}")
            print("You can now import this CSV file into Airtable!")
        else:
            print("\n❌ No data was extracted.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Extraction cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
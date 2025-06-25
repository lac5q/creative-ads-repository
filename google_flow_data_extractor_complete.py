#!/usr/bin/env python3
"""
Complete Google Flow Data Extractor
Creation Date: June 24, 2025
Version: 2.0

This script scrolls through the entire Google Flow page to capture ALL videos,
not just the ones visible in the initial viewport.

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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteGoogleFlowExtractor:
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
        
        # Set window size for better visibility
        options.add_argument('--window-size=1920,1080')
        
        if headless:
            options.add_argument('--headless')
            
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
        print("4. Wait for ALL content to load")
        print("5. Press ENTER here when you're ready to continue...")
        print("="*60)
        
    def scroll_and_load_all_content(self):
        """Scroll through the entire page to load all videos"""
        logger.info("Starting comprehensive scroll to load all content...")
        
        # Get initial page height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll down to the bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(3)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            logger.info(f"Scroll attempt {scroll_attempts + 1}: Height {last_height} -> {new_height}")
            
            if new_height == last_height:
                # Try a few more scrolls to be sure
                logger.info("No new content detected, trying additional scrolls...")
                for extra_scroll in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    extra_height = self.driver.execute_script("return document.body.scrollHeight")
                    if extra_height > new_height:
                        new_height = extra_height
                        break
                
                if new_height == last_height:
                    logger.info("Confirmed: No more content to load")
                    break
                    
            last_height = new_height
            scroll_attempts += 1
            
        # Final scroll to top and then to bottom to ensure everything is loaded
        logger.info("Final comprehensive scroll pass...")
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        logger.info(f"Completed scrolling after {scroll_attempts} attempts")
        return scroll_attempts
        
    def find_all_video_elements(self):
        """Find all video elements using multiple strategies"""
        logger.info("Searching for video elements using multiple strategies...")
        
        # Multiple selectors to try
        video_selectors = [
            'video',  # Direct video tags
            '[data-testid*="video"]',  # Test ID attributes
            '[class*="video"]',  # Class names containing "video"
            '[id*="video"]',  # ID attributes containing "video"
            '.video-card',  # Common video card classes
            '.flow-video',  # Flow-specific classes
            '.media-item',  # Generic media items
            '[src*=".mp4"]',  # Direct MP4 sources
            '[src*=".webm"]',  # WebM sources
            'iframe[src*="video"]',  # Video iframes
            'div[data-video]',  # Divs with video data
            'article',  # Article tags (common for content cards)
            '[role="article"]',  # ARIA article roles
            '.card',  # Generic card classes
            '.item',  # Generic item classes
            '[data-id]',  # Elements with data-id (common for generated content)
        ]
        
        all_videos = []
        found_selectors = []
        
        for selector in video_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    found_selectors.append(f"{selector}: {len(elements)}")
                    all_videos.extend(elements)
                else:
                    logger.debug(f"No elements found with selector: {selector}")
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
        
        # Remove duplicates while preserving order
        unique_videos = []
        seen_elements = set()
        
        for video in all_videos:
            element_id = id(video)
            if element_id not in seen_elements:
                unique_videos.append(video)
                seen_elements.add(element_id)
        
        logger.info(f"Total unique video elements found: {len(unique_videos)}")
        logger.info("Selectors that found elements:")
        for found in found_selectors:
            logger.info(f"  - {found}")
            
        return unique_videos
        
    def extract_flow_data(self, project_url):
        """Extract data from Google Flow project with comprehensive scrolling"""
        try:
            logger.info(f"Opening Flow project: {project_url}")
            self.driver.get(project_url)
            
            # Prompt for manual login
            self.login_prompt()
            input("Press ENTER when you're logged in and ready to continue...")
            
            # Wait for initial page load
            logger.info("Waiting for Flow project to load...")
            time.sleep(5)
            
            # Comprehensive scrolling to load all content
            scroll_attempts = self.scroll_and_load_all_content()
            
            # Find all video elements
            videos_found = self.find_all_video_elements()
            
            if not videos_found:
                logger.warning("No video elements found even after scrolling. Switching to manual extraction...")
                self.manual_extraction_mode()
                return
                
            logger.info(f"Processing {len(videos_found)} video elements...")
            
            # Extract data from found videos
            for i, video_element in enumerate(videos_found):
                try:
                    video_data = self.extract_video_data(video_element, i)
                    if video_data:
                        self.data.append(video_data)
                        logger.info(f"Successfully extracted data from video {i+1}")
                    else:
                        logger.warning(f"Failed to extract data from video {i+1}")
                except Exception as e:
                    logger.error(f"Error processing video {i+1}: {str(e)}")
                    # Create placeholder entry
                    placeholder_data = self.create_placeholder_video_data(i)
                    self.data.append(placeholder_data)
                    
            logger.info(f"Successfully extracted data from {len(self.data)} videos")
            
        except Exception as e:
            logger.error(f"Error extracting Flow data: {str(e)}")
            self.manual_extraction_mode()
            
    def create_placeholder_video_data(self, index):
        """Create placeholder data for videos that couldn't be processed"""
        return {
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
            'Meta_Video_URL': 'TBD',
            'Google_Drive_Download_Link': 'TBD',
            'Google_Drive_View_Link': 'TBD',
            'Creative_Type': 'TBD',
            'Hook_Type': 'TBD',
            'Targeting': 'Broad',
            'Priority': '🔍 NEEDS_REVIEW',
            'Ad_Name': f'video: Flow Generated / Video {index + 1}',
            'Notes': f'Generated: {datetime.now().strftime("%Y-%m-%d")} | Flow Project Video {index + 1} | Needs manual review',
            'Download_Command': 'TBD'
        }
            
    def manual_extraction_mode(self):
        """Guide user through manual data extraction"""
        print("\n" + "="*60)
        print("MANUAL EXTRACTION MODE")
        print("="*60)
        print("The automatic extraction needs your help!")
        print("Please look at your Flow project and provide information:")
        print("="*60)
        
        video_count = input("How many videos do you see in your Flow project? ")
        try:
            video_count = int(video_count)
        except ValueError:
            video_count = 1
            
        logger.info(f"User reported {video_count} videos for manual extraction")
            
        for i in range(video_count):
            print(f"\n--- VIDEO {i+1} of {video_count} ---")
            video_data = self.collect_manual_video_data(i)
            self.data.append(video_data)
            
    def collect_manual_video_data(self, index):
        """Collect video data manually from user input"""
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
        
        # Basic info
        video_name = input("Video name/title: ").strip()
        video_data['Ad_Name'] = f"video: Flow Generated / {video_name}" if video_name else f"video: Flow Generated / Video {index + 1}"
        
        prompt = input("Original prompt used: ").strip()
        video_url = input("Video URL (if available): ").strip()
        
        if video_url:
            video_data['Meta_Video_URL'] = video_url
            safe_name = video_name.replace(' ', '_').replace('/', '_') if video_name else f"Flow_Video_{index + 1}"
            video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
        else:
            video_data['Meta_Video_URL'] = 'TBD'
            video_data['Download_Command'] = 'TBD'
        
        # Quick classification
        print("\nQuick Creative Type:")
        print("1=Influencer, 2=Lifestyle, 3=Demo, 4=Reaction, 5=Comedy, 6=Other")
        creative_choice = input("Creative type (1-6): ").strip()
        creative_map = {'1': 'Influencer Testimonial', '2': 'Lifestyle', '3': 'Product Demo', 
                       '4': 'Reaction Video', '5': 'Comedy/Humor', '6': 'Other'}
        video_data['Creative_Type'] = creative_map.get(creative_choice, 'Other')
        
        print("Hook Type:")
        print("1=Authority, 2=Emotional, 3=Problem/Solution, 4=Reaction, 5=Curiosity, 6=Other")
        hook_choice = input("Hook type (1-6): ").strip()
        hook_map = {'1': 'Authority Hook', '2': 'Gifting/Emotional', '3': 'Problem/Solution',
                   '4': 'Reaction Hook', '5': 'Curiosity Gap', '6': 'Other'}
        video_data['Hook_Type'] = hook_map.get(hook_choice, 'Other')
        
        # Notes
        notes_parts = []
        if prompt:
            notes_parts.append(f"Original Prompt: {prompt}")
        notes_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        notes_parts.append(f"Flow Project Video {index + 1}")
        
        video_data['Notes'] = " | ".join(notes_parts)
        
        return video_data
        
    def extract_video_data(self, element, index):
        """Extract data from a video element with enhanced detection"""
        try:
            video_data = self.create_placeholder_video_data(index)
            
            # Try to extract more detailed information
            try:
                # Look for text content in the element and its children
                element_text = element.text.strip() if element.text else ""
                
                # Try to find title or name
                title_selectors = [
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    '.title', '.name', '.caption', '.label',
                    '[data-title]', '[title]', '[aria-label]'
                ]
                
                title_found = False
                for selector in title_selectors:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, selector)
                        if title_elem.text.strip():
                            video_data['Ad_Name'] = f"video: Flow Generated / {title_elem.text.strip()}"
                            title_found = True
                            break
                    except:
                        continue
                
                # If no specific title found, use element text
                if not title_found and element_text and len(element_text) < 100:
                    video_data['Ad_Name'] = f"video: Flow Generated / {element_text[:50]}..."
                
                # Try to extract video URL
                video_url_found = False
                
                # Check for video source
                try:
                    video_elem = element.find_element(By.TAG_NAME, 'video')
                    video_url = video_elem.get_attribute('src')
                    if video_url:
                        video_data['Meta_Video_URL'] = video_url
                        video_url_found = True
                except:
                    pass
                
                # Check for data attributes that might contain URLs
                if not video_url_found:
                    url_attributes = ['data-src', 'data-video-url', 'data-url', 'href']
                    for attr in url_attributes:
                        try:
                            url = element.get_attribute(attr)
                            if url and ('mp4' in url or 'webm' in url or 'video' in url):
                                video_data['Meta_Video_URL'] = url
                                video_url_found = True
                                break
                        except:
                            continue
                
                # Generate download command if URL found
                if video_url_found and video_data['Meta_Video_URL'] != 'TBD':
                    safe_name = f"Flow_Video_{index + 1}"
                    video_data['Download_Command'] = f'yt-dlp "{video_data["Meta_Video_URL"]}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
                
                # Enhanced notes with element information
                notes_parts = [
                    f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                    f"Flow Project Video {index + 1}",
                    f"Element Type: {element.tag_name}",
                ]
                
                if element_text:
                    notes_parts.append(f"Text: {element_text[:100]}...")
                
                video_data['Notes'] = " | ".join(notes_parts)
                
            except Exception as e:
                logger.debug(f"Error extracting detailed info from video {index + 1}: {str(e)}")
                # Keep the placeholder data
                pass
                
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting video data for index {index}: {str(e)}")
            return self.create_placeholder_video_data(index)
            
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
                row[col] = item.get(col, 'TBD')
            formatted_data.append(row)
            
        return formatted_data
        
    def save_to_csv(self, filename=None):
        """Save extracted data to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Complete_Analysis_{timestamp}.csv'
            
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
            
        print(f"\n{'='*80}")
        print(f"COMPLETE EXTRACTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total videos processed: {len(self.data)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Group by data completeness
        complete_data = []
        partial_data = []
        placeholder_data = []
        
        for i, item in enumerate(self.data, 1):
            if item.get('Meta_Video_URL', 'TBD') != 'TBD':
                complete_data.append((i, item))
            elif 'Needs manual review' in item.get('Notes', ''):
                placeholder_data.append((i, item))
            else:
                partial_data.append((i, item))
        
        print(f"\n📊 Data Quality Summary:")
        print(f"  ✅ Complete data (with video URLs): {len(complete_data)}")
        print(f"  🔄 Partial data (needs enhancement): {len(partial_data)}")
        print(f"  ⚠️  Placeholder data (needs manual review): {len(placeholder_data)}")
        
        # Show first few videos as examples
        print(f"\n🎬 First 10 Videos:")
        for i, item in enumerate(self.data[:10], 1):
            name = item.get('Ad_Name', 'N/A')
            if len(name) > 60:
                name = name[:57] + "..."
            print(f"  {i:2d}. {name}")
            
        if len(self.data) > 10:
            print(f"  ... and {len(self.data) - 10} more videos")
            
    def close(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main execution function"""
    print("🎬 Complete Google Flow Data Extractor")
    print("="*50)
    print("This version scrolls through the ENTIRE page to find ALL videos!")
    
    project_url = input("Enter your Google Flow project URL (or press ENTER for default): ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = CompleteGoogleFlowExtractor(headless=False)
    
    try:
        extractor.extract_flow_data(project_url)
        extractor.print_summary()
        
        if extractor.data:
            filename = extractor.save_to_csv()
            print(f"\n🎉 Complete data exported to: {filename}")
            print("✅ Ready for Airtable import!")
            
            # Offer to run enhancement
            enhance = input(f"\nEnhance the data with detailed video information? (y/n): ").strip().lower()
            if enhance == 'y':
                print("💡 Run 'python enhance_flow_data.py' next to add detailed information!")
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
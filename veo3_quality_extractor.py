#!/usr/bin/env python3
"""
Veo 3 - Quality Video Extractor for Google Flow
Creation Date: June 24, 2025
Version: 1.0

This script creates a template for 30 videos and helps filter
for only "Veo 3 - Quality" labeled videos from Google Flow.
"""

import pandas as pd
import json
from datetime import datetime
import time
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

class Veo3QualityExtractor:
    def __init__(self, headless=False):
        """Initialize the extractor for Veo 3 Quality videos"""
        self.setup_driver(headless)
        self.veo3_videos = []
        self.base_ad_id = 300001000000000
        
    def setup_driver(self, headless=False):
        """Setup Chrome webdriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        
        if headless:
            options.add_argument('--headless')
            
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def create_base_template(self, count=30):
        """Create base template for specified number of videos"""
        logger.info(f"Creating base template for {count} videos...")
        
        template_data = []
        for i in range(count):
            video_data = {
                'Ad_ID': self.base_ad_id + i + 1,
                'Ad_Name': f'video: Veo 3 Quality / Video {i + 1}',
                'Account': 'GoogleFlow',
                'Campaign': 'Veo 3 Generated Content',
                'Creative_ID': self.base_ad_id + i + 1,
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
                'Creative_Type': 'AI Generated',
                'Hook_Type': 'TBD',
                'Targeting': 'Broad',
                'Priority': '🔍 VEO3_REVIEW',
                'Notes': f'Veo 3 - Quality | Generated: {datetime.now().strftime("%Y-%m-%d")} | Flow Project Video {i + 1} | Needs detailed review',
                'Download_Command': 'TBD'
            }
            template_data.append(video_data)
            
        return template_data
        
    def scan_for_veo3_videos(self, project_url):
        """Scan the Flow project for Veo 3 - Quality videos specifically"""
        try:
            logger.info(f"Opening Flow project to scan for Veo 3 videos: {project_url}")
            self.driver.get(project_url)
            
            print("\n" + "="*60)
            print("VEO 3 - QUALITY VIDEO SCANNER")
            print("="*60)
            print("1. Please log in to your Google Flow project")
            print("2. Wait for ALL content to load")
            print("3. Look for videos labeled 'Veo 3 - Quality'")
            print("4. Press ENTER when ready to scan...")
            print("="*60)
            
            input("Press ENTER when logged in and ready...")
            
            # Wait for page load
            time.sleep(5)
            
            # Comprehensive scroll to load all content
            self.comprehensive_scroll()
            
            # Look for Veo 3 specific elements
            veo3_elements = self.find_veo3_elements()
            
            logger.info(f"Found {len(veo3_elements)} potential Veo 3 elements")
            
            # Process each element
            for i, element in enumerate(veo3_elements):
                video_data = self.extract_veo3_data(element, i)
                if video_data:
                    self.veo3_videos.append(video_data)
                    
            if not self.veo3_videos:
                logger.warning("No Veo 3 videos found automatically. Switching to manual mode...")
                self.manual_veo3_extraction()
                
        except Exception as e:
            logger.error(f"Error scanning for Veo 3 videos: {str(e)}")
            self.manual_veo3_extraction()
            
    def comprehensive_scroll(self):
        """Scroll through entire page multiple times to ensure all content loads"""
        logger.info("Starting comprehensive scroll for dynamic content...")
        
        # Multiple scroll passes
        for pass_num in range(3):
            logger.info(f"Scroll pass {pass_num + 1}/3")
            
            # Scroll to bottom
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Wait for dynamic loading
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            # Scroll back to top for next pass
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
        logger.info("Comprehensive scrolling completed")
        
    def find_veo3_elements(self):
        """Find elements that contain 'Veo 3' or 'Quality' text"""
        logger.info("Searching for Veo 3 - Quality elements...")
        
        # Search strategies for Veo 3 content
        veo3_selectors = [
            # Text-based searches
            "//*[contains(text(), 'Veo 3')]",
            "//*[contains(text(), 'veo 3')]",
            "//*[contains(text(), 'VEO 3')]",
            "//*[contains(text(), 'Quality')]",
            "//*[contains(text(), 'quality')]",
            "//*[contains(text(), 'QUALITY')]",
            
            # Attribute-based searches
            "//*[contains(@title, 'Veo 3')]",
            "//*[contains(@aria-label, 'Veo 3')]",
            "//*[contains(@data-label, 'Veo 3')]",
            "//*[contains(@alt, 'Veo 3')]",
        ]
        
        all_elements = []
        
        for selector in veo3_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    all_elements.extend(elements)
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
                
        # Remove duplicates
        unique_elements = []
        seen_elements = set()
        
        for element in all_elements:
            element_id = id(element)
            if element_id not in seen_elements:
                # Additional filter: check if element or parent contains video-related content
                try:
                    element_html = element.get_attribute('outerHTML')
                    parent_html = element.find_element(By.XPATH, './..').get_attribute('outerHTML')
                    
                    if any(keyword in element_html.lower() or keyword in parent_html.lower() 
                           for keyword in ['video', 'mp4', 'webm', 'play', 'media']):
                        unique_elements.append(element)
                        seen_elements.add(element_id)
                except:
                    # If we can't check, include it anyway
                    unique_elements.append(element)
                    seen_elements.add(element_id)
                    
        logger.info(f"Found {len(unique_elements)} unique Veo 3 related elements")
        return unique_elements
        
    def extract_veo3_data(self, element, index):
        """Extract data from a Veo 3 element"""
        try:
            video_data = {
                'Ad_ID': self.base_ad_id + index + 1,
                'Creative_ID': self.base_ad_id + index + 1,
                'Account': 'GoogleFlow',
                'Campaign': 'Veo 3 Generated Content',
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
                'Creative_Type': 'AI Generated - Veo 3',
                'Hook_Type': 'TBD',
                'Targeting': 'Broad',
                'Priority': '🔍 VEO3_REVIEW'
            }
            
            # Extract text content
            element_text = element.text.strip() if element.text else ""
            
            # Try to find video name/title
            video_name = f"Veo 3 Video {index + 1}"
            if element_text and len(element_text) < 100:
                # Clean up the text for use as video name
                clean_text = element_text.replace('\n', ' ').strip()
                if clean_text and not clean_text.lower().startswith('veo 3'):
                    video_name = f"Veo 3 - {clean_text[:50]}"
                elif clean_text:
                    video_name = clean_text[:60]
                    
            video_data['Ad_Name'] = f"video: {video_name}"
            
            # Try to extract video URL
            try:
                # Look for video elements in vicinity
                video_elem = element.find_element(By.XPATH, ".//video | ./ancestor::*//video | ./following::video[1] | ./preceding::video[1]")
                video_url = video_elem.get_attribute('src')
                if video_url:
                    video_data['Meta_Video_URL'] = video_url
                    safe_name = video_name.replace(' ', '_').replace('/', '_')
                    video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
            except:
                pass
                
            # Enhanced notes
            notes_parts = [
                "Veo 3 - Quality",
                f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                f"Flow Project Video {index + 1}",
            ]
            
            if element_text:
                notes_parts.append(f"Text: {element_text[:100]}...")
                
            video_data['Notes'] = " | ".join(notes_parts)
            
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting Veo 3 data for index {index}: {str(e)}")
            return None
            
    def manual_veo3_extraction(self):
        """Manual extraction specifically for Veo 3 videos"""
        print("\n" + "="*60)
        print("MANUAL VEO 3 - QUALITY EXTRACTION")
        print("="*60)
        print("Please look at your Flow project and identify Veo 3 - Quality videos")
        print("="*60)
        
        veo3_count = input("How many 'Veo 3 - Quality' videos do you see? ")
        try:
            veo3_count = int(veo3_count)
        except ValueError:
            veo3_count = 0
            
        if veo3_count == 0:
            logger.warning("No Veo 3 videos to extract")
            return
            
        logger.info(f"Manual extraction for {veo3_count} Veo 3 videos")
        
        for i in range(veo3_count):
            print(f"\n--- VEO 3 VIDEO {i+1} of {veo3_count} ---")
            video_data = self.collect_veo3_manual_data(i)
            self.veo3_videos.append(video_data)
            
    def collect_veo3_manual_data(self, index):
        """Collect Veo 3 video data manually"""
        video_data = {
            'Ad_ID': self.base_ad_id + index + 1,
            'Creative_ID': self.base_ad_id + index + 1,
            'Account': 'GoogleFlow',
            'Campaign': 'Veo 3 Generated Content',
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
            'Creative_Type': 'AI Generated - Veo 3',
            'Targeting': 'Broad',
            'Priority': '🔍 VEO3_REVIEW'
        }
        
        # Collect basic info
        video_name = input("Video name/description: ").strip()
        if not video_name:
            video_name = f"Veo 3 Quality Video {index + 1}"
        elif not video_name.lower().startswith('veo 3'):
            video_name = f"Veo 3 - {video_name}"
            
        video_data['Ad_Name'] = f"video: {video_name}"
        
        # Original prompt
        prompt = input("Original prompt used (if known): ").strip()
        
        # Video URL
        video_url = input("Video URL (if available): ").strip()
        if video_url:
            video_data['Meta_Video_URL'] = video_url
            safe_name = video_name.replace(' ', '_').replace('/', '_')
            video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
        else:
            video_data['Meta_Video_URL'] = 'TBD'
            video_data['Download_Command'] = 'TBD'
            
        # Quick classification for Veo 3 content
        print("\nVeo 3 Content Type:")
        print("1=Product Demo, 2=Lifestyle, 3=Testimonial, 4=Explainer, 5=Entertainment, 6=Other")
        content_choice = input("Content type (1-6): ").strip()
        content_map = {'1': 'Product Demo', '2': 'Lifestyle', '3': 'Testimonial',
                      '4': 'Explainer', '5': 'Entertainment', '6': 'Other'}
        video_data['Creative_Type'] = f"AI Generated - Veo 3 - {content_map.get(content_choice, 'Other')}"
        
        print("Hook Style:")
        print("1=Problem/Solution, 2=Curiosity, 3=Emotional, 4=Educational, 5=Humorous, 6=Direct")
        hook_choice = input("Hook style (1-6): ").strip()
        hook_map = {'1': 'Problem/Solution', '2': 'Curiosity Gap', '3': 'Emotional',
                   '4': 'Educational', '5': 'Humorous', '6': 'Direct'}
        video_data['Hook_Type'] = hook_map.get(hook_choice, 'Other')
        
        # Notes
        notes_parts = [
            "Veo 3 - Quality",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            f"Flow Project Video {index + 1}"
        ]
        
        if prompt:
            notes_parts.append(f"Original Prompt: {prompt}")
            
        video_data['Notes'] = " | ".join(notes_parts)
        
        return video_data
        
    def save_veo3_data(self, filename=None):
        """Save Veo 3 video data to CSV"""
        if not self.veo3_videos:
            logger.warning("No Veo 3 videos to save")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Veo3_Quality_Videos_{timestamp}.csv'
            
        # Define columns matching the user's format
        columns = [
            'Ad_ID', 'Ad_Name', 'Account', 'Campaign', 'Creative_ID', 'Status',
            'Performance_Rating', 'CPA', 'CVR', 'CTR', 'Spend', 'Purchases',
            'Video_Views', 'Hook_Rate', 'Facebook_Preview_Link', 'Meta_Video_URL',
            'Google_Drive_Download_Link', 'Google_Drive_View_Link', 'Creative_Type',
            'Hook_Type', 'Targeting', 'Priority', 'Notes', 'Download_Command'
        ]
        
        # Format data
        formatted_data = []
        for item in self.veo3_videos:
            row = {}
            for col in columns:
                row[col] = item.get(col, 'TBD')
            formatted_data.append(row)
            
        df = pd.DataFrame(formatted_data)
        df.to_csv(filename, index=False)
        logger.info(f"Veo 3 data saved to {filename}")
        
        # Also save raw JSON
        raw_filename = filename.replace('.csv', '_raw.json')
        with open(raw_filename, 'w') as f:
            json.dump(self.veo3_videos, f, indent=2)
            
        return filename
        
    def print_veo3_summary(self):
        """Print summary of Veo 3 videos"""
        if not self.veo3_videos:
            print("No Veo 3 - Quality videos found.")
            return
            
        print(f"\n{'='*80}")
        print(f"VEO 3 - QUALITY VIDEOS SUMMARY")
        print(f"{'='*80}")
        print(f"Total Veo 3 videos found: {len(self.veo3_videos)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🎬 Veo 3 - Quality Videos:")
        for i, item in enumerate(self.veo3_videos, 1):
            name = item.get('Ad_Name', 'N/A')
            if len(name) > 70:
                name = name[:67] + "..."
            print(f"  {i:2d}. {name}")
            
    def close(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main execution function"""
    print("🎬 Veo 3 - Quality Video Extractor")
    print("="*50)
    print("This script extracts ONLY 'Veo 3 - Quality' labeled videos!")
    
    # Option to create template or scan live
    mode = input("Choose mode:\n1. Scan live Flow project for Veo 3 videos\n2. Create manual template for 30 videos\nEnter choice (1 or 2): ").strip()
    
    if mode == "2":
        # Create template mode
        extractor = Veo3QualityExtractor()
        template_data = extractor.create_base_template(30)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'GoogleFlow_Veo3_Template_30_videos_{timestamp}.csv'
        
        df = pd.DataFrame(template_data)
        df.to_csv(filename, index=False)
        
        print(f"\n✅ Template created: {filename}")
        print("📝 This template has 30 video slots ready for Veo 3 - Quality content")
        print("💡 You can now manually fill in the details for each Veo 3 video you find!")
        return
        
    # Live scanning mode
    project_url = input("Enter your Google Flow project URL (or press ENTER for default): ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = Veo3QualityExtractor(headless=False)
    
    try:
        extractor.scan_for_veo3_videos(project_url)
        extractor.print_veo3_summary()
        
        if extractor.veo3_videos:
            filename = extractor.save_veo3_data()
            print(f"\n🎉 Veo 3 - Quality videos exported to: {filename}")
            print("✅ Ready for Airtable import!")
        else:
            print("\n❌ No Veo 3 - Quality videos were found or extracted.")
            print("💡 Try using mode 2 to create a manual template instead.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Extraction cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
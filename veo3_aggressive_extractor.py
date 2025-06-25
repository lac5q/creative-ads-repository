#!/usr/bin/env python3
"""
Aggressive Veo 3 - Quality Video Extractor
Creation Date: June 24, 2025
Version: 2.0

This script uses multiple aggressive strategies to find ALL Veo 3 - Quality videos
in the Google Flow project, including extensive scrolling and multiple search methods.
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AggressiveVeo3Extractor:
    def __init__(self, headless=False):
        """Initialize the aggressive extractor"""
        self.setup_driver(headless)
        self.veo3_videos = []
        self.base_ad_id = 300001000000000
        self.all_found_elements = []
        
    def setup_driver(self, headless=False):
        """Setup Chrome webdriver with enhanced options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        if headless:
            options.add_argument('--headless')
            
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def super_aggressive_scroll(self):
        """Ultra-aggressive scrolling to load ALL content"""
        logger.info("Starting SUPER AGGRESSIVE scrolling...")
        
        # Phase 1: Multiple full-page scrolls
        for phase in range(5):
            logger.info(f"Aggressive scroll phase {phase + 1}/5")
            
            # Scroll to very top first
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Get initial height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 100  # Much higher limit
            
            while scroll_attempts < max_attempts:
                # Multiple scroll strategies
                
                # Strategy 1: Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Strategy 2: Scroll by pixels
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
                
                # Strategy 3: Page down key
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
                except:
                    pass
                
                # Strategy 4: End key
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                    time.sleep(2)
                except:
                    pass
                
                # Check for new content
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    # Try extra scrolls
                    for extra in range(5):
                        self.driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)
                        extra_height = self.driver.execute_script("return document.body.scrollHeight")
                        if extra_height > new_height:
                            new_height = extra_height
                            break
                    
                    if new_height == last_height:
                        logger.info(f"No new content after {scroll_attempts} attempts in phase {phase + 1}")
                        break
                        
                last_height = new_height
                scroll_attempts += 1
                
                if scroll_attempts % 10 == 0:
                    logger.info(f"Phase {phase + 1}: Scroll attempt {scroll_attempts}, height: {new_height}")
        
        # Phase 2: Click and load interactions
        logger.info("Phase 2: Trying click interactions to load more content...")
        self.try_load_more_interactions()
        
        # Phase 3: Final comprehensive scroll
        logger.info("Phase 3: Final comprehensive scroll...")
        for final_scroll in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
        logger.info("Super aggressive scrolling completed!")
        
    def try_load_more_interactions(self):
        """Try to find and click 'Load More' or similar buttons"""
        load_more_selectors = [
            "button:contains('Load')",
            "button:contains('More')",
            "button:contains('Show')",
            "[class*='load']",
            "[class*='more']",
            "[class*='expand']",
            "[data-testid*='load']",
            "[data-testid*='more']",
            ".load-more",
            ".show-more",
            ".expand-more"
        ]
        
        for selector in load_more_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"Clicking potential load more button: {selector}")
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                    except:
                        continue
            except:
                continue
                
    def find_all_possible_veo3_elements(self):
        """Use every possible strategy to find Veo 3 elements"""
        logger.info("Using ALL possible strategies to find Veo 3 elements...")
        
        all_strategies = []
        
        # Strategy 1: Text-based XPath searches
        text_selectors = [
            "//*[contains(text(), 'Veo 3')]",
            "//*[contains(text(), 'veo 3')]", 
            "//*[contains(text(), 'VEO 3')]",
            "//*[contains(text(), 'Veo3')]",
            "//*[contains(text(), 'veo3')]",
            "//*[contains(text(), 'VEO3')]",
            "//*[contains(text(), 'Quality')]",
            "//*[contains(text(), 'quality')]",
            "//*[contains(text(), 'QUALITY')]",
            "//*[contains(text(), 'High quality')]",
            "//*[contains(text(), 'high quality')]",
        ]
        
        for selector in text_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"Text search found {len(elements)} elements: {selector}")
                    all_strategies.extend(elements)
            except Exception as e:
                logger.debug(f"Error with text selector {selector}: {str(e)}")
        
        # Strategy 2: Attribute-based searches
        attr_selectors = [
            "//*[contains(@title, 'Veo')]",
            "//*[contains(@aria-label, 'Veo')]",
            "//*[contains(@data-label, 'Veo')]",
            "//*[contains(@alt, 'Veo')]",
            "//*[contains(@class, 'veo')]",
            "//*[contains(@id, 'veo')]",
        ]
        
        for selector in attr_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"Attribute search found {len(elements)} elements: {selector}")
                    all_strategies.extend(elements)
            except:
                continue
        
        # Strategy 3: CSS-based searches
        css_selectors = [
            '[class*="veo"]',
            '[class*="quality"]',
            '[id*="veo"]',
            '[id*="quality"]',
            '[data-*="veo" i]',
            '[data-*="quality" i]',
        ]
        
        for selector in css_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"CSS search found {len(elements)} elements: {selector}")
                    all_strategies.extend(elements)
            except:
                continue
        
        # Strategy 4: Video-specific searches
        video_selectors = [
            'video',
            '[src*=".mp4"]',
            '[src*=".webm"]', 
            '[src*="video"]',
            'iframe[src*="video"]',
            '.video-card',
            '.video-item',
            '.media-card',
            '.media-item',
            '[data-video]',
            '[data-media]',
        ]
        
        for selector in video_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Video search found {len(elements)} elements: {selector}")
                    all_strategies.extend(elements)
            except:
                continue
        
        # Strategy 5: Generic content containers
        container_selectors = [
            'article',
            '.card',
            '.item',
            '.content',
            '.container',
            '[role="article"]',
            '[data-id]',
            '[data-item]',
            'div[class*="item"]',
            'div[class*="card"]',
        ]
        
        for selector in container_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Container search found {len(elements)} elements: {selector}")
                    all_strategies.extend(elements)
            except:
                continue
                
        # Remove duplicates while preserving order
        unique_elements = []
        seen_elements = set()
        
        for element in all_strategies:
            try:
                element_id = id(element)
                if element_id not in seen_elements:
                    # Check if this element or its content relates to Veo 3
                    element_text = ""
                    element_html = ""
                    
                    try:
                        element_text = element.text.lower()
                        element_html = element.get_attribute('outerHTML').lower()
                    except:
                        pass
                    
                    # Filter for Veo 3 related content
                    veo3_keywords = ['veo 3', 'veo3', 'quality', 'video']
                    if any(keyword in element_text or keyword in element_html for keyword in veo3_keywords):
                        unique_elements.append(element)
                        seen_elements.add(element_id)
                        
            except:
                continue
                
        logger.info(f"Total unique Veo 3 related elements found: {len(unique_elements)}")
        return unique_elements
        
    def extract_comprehensive_veo3_data(self, project_url):
        """Comprehensive extraction with all strategies"""
        try:
            logger.info(f"Starting comprehensive Veo 3 extraction: {project_url}")
            self.driver.get(project_url)
            
            print("\n" + "="*70)
            print("COMPREHENSIVE VEO 3 - QUALITY EXTRACTOR")
            print("="*70)
            print("This will use EVERY possible method to find ALL Veo 3 videos!")
            print("1. Please log in to your Google Flow project")
            print("2. Navigate to your project with all the Veo 3 videos")
            print("3. This will take several minutes of aggressive scrolling")
            print("4. Press ENTER when ready to start the comprehensive scan...")
            print("="*70)
            
            input("Press ENTER when logged in and ready for comprehensive extraction...")
            
            # Wait for initial load
            time.sleep(5)
            
            # Super aggressive scrolling
            self.super_aggressive_scroll()
            
            # Find all possible elements
            all_elements = self.find_all_possible_veo3_elements()
            
            if not all_elements:
                logger.warning("No elements found with comprehensive search. Trying manual mode...")
                self.manual_comprehensive_extraction()
                return
                
            logger.info(f"Processing {len(all_elements)} potential Veo 3 elements...")
            
            # Process each element
            processed_count = 0
            for i, element in enumerate(all_elements):
                try:
                    # Check if this is actually a Veo 3 video
                    if self.is_veo3_video(element):
                        video_data = self.extract_veo3_video_data(element, processed_count)
                        if video_data:
                            self.veo3_videos.append(video_data)
                            processed_count += 1
                            logger.info(f"Successfully processed Veo 3 video {processed_count}")
                except Exception as e:
                    logger.debug(f"Error processing element {i}: {str(e)}")
                    continue
                    
            logger.info(f"Comprehensive extraction completed. Found {len(self.veo3_videos)} Veo 3 videos")
            
            # If we still don't have many, offer manual enhancement
            if len(self.veo3_videos) < 10:  # Assuming you have more than 10
                logger.warning("Found fewer Veo 3 videos than expected. Offering manual enhancement...")
                self.offer_manual_enhancement()
                
        except Exception as e:
            logger.error(f"Error in comprehensive extraction: {str(e)}")
            self.manual_comprehensive_extraction()
            
    def is_veo3_video(self, element):
        """Check if an element represents a Veo 3 video"""
        try:
            element_text = element.text.lower() if element.text else ""
            element_html = element.get_attribute('outerHTML').lower()
            
            # Must contain Veo 3 reference
            veo3_indicators = ['veo 3', 'veo3', 'veo-3']
            has_veo3 = any(indicator in element_text or indicator in element_html for indicator in veo3_indicators)
            
            # Should also have quality or video indicators
            quality_indicators = ['quality', 'video', 'mp4', 'webm', 'play', 'media']
            has_video_content = any(indicator in element_text or indicator in element_html for indicator in quality_indicators)
            
            return has_veo3 and has_video_content
            
        except:
            return False
            
    def extract_veo3_video_data(self, element, index):
        """Extract detailed data from a confirmed Veo 3 video element"""
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
            
            # Extract video name/title
            element_text = element.text.strip() if element.text else ""
            
            # Try to find a meaningful title
            title_elements = element.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6, .title, .name, .caption')
            video_name = f"Veo 3 Quality Video {index + 1}"
            
            for title_elem in title_elements:
                title_text = title_elem.text.strip()
                if title_text and len(title_text) < 100:
                    if not title_text.lower().startswith('veo 3'):
                        video_name = f"Veo 3 - {title_text}"
                    else:
                        video_name = title_text
                    break
            
            # If no title found but element has text, use that
            if video_name == f"Veo 3 Quality Video {index + 1}" and element_text:
                clean_text = element_text.replace('\n', ' ').strip()[:50]
                if clean_text:
                    video_name = f"Veo 3 - {clean_text}"
                    
            video_data['Ad_Name'] = f"video: {video_name}"
            
            # Try to extract video URL with multiple strategies
            video_url_found = False
            
            # Strategy 1: Direct video element
            try:
                video_elem = element.find_element(By.CSS_SELECTOR, 'video')
                video_url = video_elem.get_attribute('src')
                if video_url:
                    video_data['Meta_Video_URL'] = video_url
                    video_url_found = True
            except:
                pass
            
            # Strategy 2: Source elements
            if not video_url_found:
                try:
                    source_elems = element.find_elements(By.CSS_SELECTOR, 'source')
                    for source in source_elems:
                        src = source.get_attribute('src')
                        if src and ('mp4' in src or 'webm' in src):
                            video_data['Meta_Video_URL'] = src
                            video_url_found = True
                            break
                except:
                    pass
            
            # Strategy 3: Data attributes
            if not video_url_found:
                url_attrs = ['data-src', 'data-video-url', 'data-url', 'data-video', 'href']
                for attr in url_attrs:
                    try:
                        url = element.get_attribute(attr)
                        if url and ('video' in url or 'mp4' in url or 'webm' in url):
                            video_data['Meta_Video_URL'] = url
                            video_url_found = True
                            break
                    except:
                        continue
            
            # Strategy 4: Look in parent/child elements
            if not video_url_found:
                try:
                    # Check parent
                    parent = element.find_element(By.XPATH, './..')
                    parent_videos = parent.find_elements(By.CSS_SELECTOR, 'video, [src*="mp4"], [src*="webm"]')
                    for vid in parent_videos:
                        src = vid.get_attribute('src')
                        if src:
                            video_data['Meta_Video_URL'] = src
                            video_url_found = True
                            break
                except:
                    pass
            
            # Generate download command if URL found
            if video_url_found and video_data['Meta_Video_URL'] != 'TBD':
                safe_name = video_name.replace(' ', '_').replace('/', '_').replace(':', '_')
                video_data['Download_Command'] = f'yt-dlp "{video_data["Meta_Video_URL"]}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
            else:
                video_data['Download_Command'] = 'TBD'
            
            # Enhanced notes
            notes_parts = [
                "Veo 3 - Quality",
                f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                f"Flow Project Video {index + 1}",
                "Comprehensive Extraction"
            ]
            
            if element_text and len(element_text) < 200:
                notes_parts.append(f"Content: {element_text[:100]}...")
                
            video_data['Notes'] = " | ".join(notes_parts)
            
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive Veo 3 data for index {index}: {str(e)}")
            return None
            
    def manual_comprehensive_extraction(self):
        """Manual extraction for comprehensive results"""
        print("\n" + "="*70)
        print("MANUAL COMPREHENSIVE VEO 3 EXTRACTION")
        print("="*70)
        print("Let's manually identify ALL your Veo 3 - Quality videos!")
        print("Please look carefully at your Flow project...")
        print("="*70)
        
        total_veo3 = input("How many Veo 3 - Quality videos do you see in TOTAL? ")
        try:
            total_veo3 = int(total_veo3)
        except ValueError:
            total_veo3 = 0
            
        if total_veo3 == 0:
            logger.warning("No Veo 3 videos to extract")
            return
            
        logger.info(f"Manual comprehensive extraction for {total_veo3} Veo 3 videos")
        
        print(f"\nGreat! Let's collect information for all {total_veo3} videos...")
        print("For each video, I'll ask for basic info. You can skip details and add them later.")
        
        for i in range(total_veo3):
            print(f"\n--- VEO 3 VIDEO {i+1} of {total_veo3} ---")
            video_data = self.collect_quick_veo3_data(i)
            self.veo3_videos.append(video_data)
            
    def collect_quick_veo3_data(self, index):
        """Quick collection of Veo 3 video data"""
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
        
        # Quick name collection
        video_name = input(f"Video {index + 1} name/description (or press ENTER to skip): ").strip()
        if not video_name:
            video_name = f"Veo 3 Quality Video {index + 1}"
        elif not video_name.lower().startswith('veo 3'):
            video_name = f"Veo 3 - {video_name}"
            
        video_data['Ad_Name'] = f"video: {video_name}"
        
        # Quick prompt collection
        prompt = input("Original prompt (or press ENTER to skip): ").strip()
        
        # Quick URL collection
        video_url = input("Video URL (or press ENTER to skip): ").strip()
        if video_url:
            video_data['Meta_Video_URL'] = video_url
            safe_name = video_name.replace(' ', '_').replace('/', '_').replace(':', '_')
            video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
        else:
            video_data['Meta_Video_URL'] = 'TBD'
            video_data['Download_Command'] = 'TBD'
        
        # Quick classification
        video_data['Hook_Type'] = 'TBD'
        
        # Notes
        notes_parts = [
            "Veo 3 - Quality",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            f"Flow Project Video {index + 1}",
            "Manual Collection"
        ]
        
        if prompt:
            notes_parts.append(f"Prompt: {prompt}")
            
        video_data['Notes'] = " | ".join(notes_parts)
        
        return video_data
        
    def offer_manual_enhancement(self):
        """Offer to manually add more videos if count seems low"""
        current_count = len(self.veo3_videos)
        print(f"\n⚠️  Currently found {current_count} Veo 3 videos.")
        
        more_videos = input("Do you see more Veo 3 videos that weren't captured? (y/n): ").strip().lower()
        if more_videos == 'y':
            additional_count = input("How many additional Veo 3 videos do you see? ")
            try:
                additional_count = int(additional_count)
                logger.info(f"Adding {additional_count} additional Veo 3 videos manually")
                
                for i in range(additional_count):
                    print(f"\n--- ADDITIONAL VEO 3 VIDEO {i+1} of {additional_count} ---")
                    video_data = self.collect_quick_veo3_data(current_count + i)
                    self.veo3_videos.append(video_data)
                    
            except ValueError:
                logger.warning("Invalid number entered for additional videos")
                
    def save_comprehensive_data(self, filename=None):
        """Save comprehensive Veo 3 data"""
        if not self.veo3_videos:
            logger.warning("No Veo 3 videos to save")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Veo3_Comprehensive_{len(self.veo3_videos)}_videos_{timestamp}.csv'
            
        # Define columns
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
        logger.info(f"Comprehensive Veo 3 data saved to {filename}")
        
        # Save raw JSON
        raw_filename = filename.replace('.csv', '_raw.json')
        with open(raw_filename, 'w') as f:
            json.dump(self.veo3_videos, f, indent=2)
            
        return filename
        
    def print_comprehensive_summary(self):
        """Print comprehensive summary"""
        if not self.veo3_videos:
            print("No Veo 3 videos found.")
            return
            
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE VEO 3 - QUALITY EXTRACTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Veo 3 videos extracted: {len(self.veo3_videos)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze data completeness
        with_urls = sum(1 for v in self.veo3_videos if v.get('Meta_Video_URL', 'TBD') != 'TBD')
        with_prompts = sum(1 for v in self.veo3_videos if 'Prompt:' in v.get('Notes', ''))
        
        print(f"\n📊 Data Completeness:")
        print(f"  ✅ Videos with URLs: {with_urls}/{len(self.veo3_videos)}")
        print(f"  📝 Videos with prompts: {with_prompts}/{len(self.veo3_videos)}")
        
        print(f"\n🎬 All Veo 3 - Quality Videos:")
        for i, item in enumerate(self.veo3_videos, 1):
            name = item.get('Ad_Name', 'N/A')
            if len(name) > 65:
                name = name[:62] + "..."
            url_status = "✅" if item.get('Meta_Video_URL', 'TBD') != 'TBD' else "⚠️"
            print(f"  {i:2d}. {url_status} {name}")
            
    def close(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main execution function"""
    print("🚀 AGGRESSIVE VEO 3 - QUALITY EXTRACTOR")
    print("="*60)
    print("This will find ALL your Veo 3 videos using every possible method!")
    print("⚠️  This process will take several minutes due to comprehensive scanning.")
    
    project_url = input("Enter your Google Flow project URL (or press ENTER for default): ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = AggressiveVeo3Extractor(headless=False)
    
    try:
        extractor.extract_comprehensive_veo3_data(project_url)
        extractor.print_comprehensive_summary()
        
        if extractor.veo3_videos:
            filename = extractor.save_comprehensive_data()
            print(f"\n🎉 ALL Veo 3 - Quality videos exported to: {filename}")
            print("✅ Ready for Airtable import!")
            print(f"📊 Successfully captured {len(extractor.veo3_videos)} Veo 3 videos!")
        else:
            print("\n❌ No Veo 3 videos were found.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Extraction cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
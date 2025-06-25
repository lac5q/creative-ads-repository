#!/usr/bin/env python3
"""
Complete Veo 3 Video Extractor - Maximum Coverage
Creation Date: June 24, 2025
Version: 3.0

This script uses every possible strategy to find ALL Veo 3 videos:
- Infinite scrolling with multiple strategies
- Multiple element detection methods
- Hover extraction for URLs
- Retry mechanisms for dynamic content
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
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteVeo3Extractor:
    def __init__(self, headless=False):
        """Initialize the complete extractor"""
        self.setup_driver(headless)
        self.veo3_videos = []
        self.base_ad_id = 300001000000000
        self.found_urls = set()  # Track unique URLs
        self.processed_elements = set()  # Track processed elements
        
    def setup_driver(self, headless=False):
        """Setup Chrome webdriver with maximum compatibility"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster loading
        
        if headless:
            options.add_argument('--headless')
            
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.set_page_load_timeout(60)
        
    def extreme_scroll_and_load(self):
        """Most aggressive scrolling strategy to load ALL content"""
        logger.info("🚀 Starting EXTREME scroll to load ALL Veo 3 content...")
        
        # Strategy 1: Scroll to bottom multiple times with long waits
        for phase in range(5):  # 5 phases instead of 3
            logger.info(f"📜 Extreme scroll phase {phase + 1}/5")
            
            # Always start from top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)
            
            # Get initial metrics
            initial_height = self.driver.execute_script("return document.body.scrollHeight")
            initial_elements = len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo')]"))
            
            logger.info(f"Phase {phase + 1} - Initial height: {initial_height}, Veo elements: {initial_elements}")
            
            # Aggressive scrolling with multiple strategies
            scroll_methods = [
                # Method 1: Slow scroll to bottom
                lambda: self.slow_scroll_to_bottom(delay=2),
                # Method 2: Fast scroll to bottom
                lambda: self.fast_scroll_to_bottom(),
                # Method 3: Page down scrolling
                lambda: self.page_down_scroll(),
                # Method 4: Mouse wheel scrolling
                lambda: self.mouse_wheel_scroll(),
                # Method 5: JavaScript infinite scroll trigger
                lambda: self.trigger_infinite_scroll()
            ]
            
            for method_idx, scroll_method in enumerate(scroll_methods):
                logger.info(f"  🔄 Using scroll method {method_idx + 1}/5")
                try:
                    scroll_method()
                    time.sleep(5)  # Wait for content to load
                    
                    # Check for new content
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    new_elements = len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo')]"))
                    
                    if new_elements > initial_elements:
                        logger.info(f"    ✅ Found {new_elements - initial_elements} new Veo elements!")
                        initial_elements = new_elements
                        
                except Exception as e:
                    logger.warning(f"    ⚠️ Scroll method {method_idx + 1} failed: {str(e)}")
                    continue
            
            # Final check for this phase
            final_height = self.driver.execute_script("return document.body.scrollHeight")
            final_elements = len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo')]"))
            
            logger.info(f"Phase {phase + 1} complete - Final height: {final_height}, Total Veo elements: {final_elements}")
            
            # If no new content in this phase, try waiting and checking again
            if final_height == initial_height and final_elements == initial_elements:
                logger.info(f"  ⏳ No new content in phase {phase + 1}, waiting 10 seconds...")
                time.sleep(10)
                
                # One more check
                retry_elements = len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo')]"))
                if retry_elements > final_elements:
                    logger.info(f"  🎉 Found {retry_elements - final_elements} more elements after waiting!")
                    
        logger.info("🏁 Extreme scrolling completed!")
        
    def slow_scroll_to_bottom(self, delay=2):
        """Scroll slowly to bottom with delays"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down in small increments
            for i in range(10):
                self.driver.execute_script(f"window.scrollBy(0, {last_height // 10});")
                time.sleep(delay)
                
            # Wait for new content
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            
    def fast_scroll_to_bottom(self):
        """Fast scroll to bottom"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    def page_down_scroll(self):
        """Scroll using Page Down key"""
        body = self.driver.find_element(By.TAG_NAME, "body")
        for _ in range(50):  # Press Page Down 50 times
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            
    def mouse_wheel_scroll(self):
        """Scroll using mouse wheel simulation"""
        actions = ActionChains(self.driver)
        for _ in range(100):
            actions.scroll_by_amount(0, 500).perform()
            time.sleep(0.2)
            
    def trigger_infinite_scroll(self):
        """Trigger infinite scroll with JavaScript"""
        # Common infinite scroll triggers
        scroll_triggers = [
            "window.scrollTo(0, document.body.scrollHeight);",
            "document.body.scrollTop = document.body.scrollHeight;",
            "document.documentElement.scrollTop = document.documentElement.scrollHeight;",
            "window.dispatchEvent(new Event('scroll'));",
            "window.dispatchEvent(new Event('resize'));",
        ]
        
        for trigger in scroll_triggers:
            try:
                self.driver.execute_script(trigger)
                time.sleep(2)
            except:
                continue
                
    def find_all_veo3_comprehensive(self):
        """Most comprehensive Veo 3 element detection"""
        logger.info("🔍 Starting comprehensive Veo 3 element detection...")
        
        all_elements = []
        
        # Strategy 1: Text-based detection with variations
        text_patterns = [
            "Veo 3",
            "Veo3", 
            "veo 3",
            "veo3",
            "VEO 3",
            "VEO3",
            "Quality",
            "quality"
        ]
        
        for pattern in text_patterns:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
            logger.info(f"Found {len(elements)} elements with text '{pattern}'")
            all_elements.extend(elements)
            
        # Strategy 2: Attribute-based detection
        attr_selectors = [
            "[data-label*='veo']",
            "[data-label*='Veo']",
            "[data-label*='quality']",
            "[data-label*='Quality']",
            "[title*='veo']",
            "[title*='Veo']",
            "[alt*='veo']",
            "[alt*='Veo']",
            "[class*='veo']",
            "[class*='Veo']",
            "[id*='veo']",
            "[id*='Veo']"
        ]
        
        for selector in attr_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                    all_elements.extend(elements)
            except:
                continue
                
        # Strategy 3: Video-related elements
        video_selectors = [
            'video',
            'img[src*="video"]',
            'img[src*="mp4"]',
            'img[src*="webm"]',
            '[data-video]',
            '[data-src*="video"]',
            '.video-card',
            '.video-item',
            '.media-card',
            '.media-item',
            'div[class*="video"]',
            'div[class*="media"]',
            'div[class*="content"]',
            'div[class*="item"]',
            'div[class*="card"]'
        ]
        
        for selector in video_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with video selector '{selector}'")
                    all_elements.extend(elements)
            except:
                continue
                
        # Strategy 4: Parent/child relationship detection
        # Find elements near Veo 3 text
        veo_text_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo 3')]")
        for veo_elem in veo_text_elements:
            try:
                # Get parent and siblings
                parent = veo_elem.find_element(By.XPATH, "./..")
                siblings = parent.find_elements(By.XPATH, "./*")
                all_elements.extend(siblings)
                
                # Get children
                children = veo_elem.find_elements(By.XPATH, ".//*")
                all_elements.extend(children)
                
            except:
                continue
                
        # Strategy 5: All images (might be video thumbnails)
        all_images = self.driver.find_elements(By.CSS_SELECTOR, 'img')
        logger.info(f"Found {len(all_images)} total images to analyze")
        all_elements.extend(all_images)
        
        # Remove duplicates and filter
        unique_elements = []
        seen_elements = set()
        
        for elem in all_elements:
            try:
                # Create unique identifier for element
                elem_id = f"{elem.tag_name}_{elem.location}_{elem.size}"
                if elem_id not in seen_elements:
                    seen_elements.add(elem_id)
                    unique_elements.append(elem)
            except:
                continue
                
        logger.info(f"🎯 Total unique elements found: {len(unique_elements)}")
        return unique_elements
        
    def extract_video_with_multiple_strategies(self, element, index):
        """Extract video URL using multiple strategies"""
        logger.info(f"🎬 Extracting video {index + 1} with multiple strategies...")
        
        video_urls = []
        
        try:
            # Strategy 1: Hover and extract
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            time.sleep(3)  # Longer wait for hover
            
            # Look for video elements after hover
            videos = self.driver.find_elements(By.CSS_SELECTOR, 'video')
            for video in videos:
                src = video.get_attribute('src')
                if src and self.is_valid_video_url(src):
                    video_urls.append(src)
                    
            # Strategy 2: Check all URL attributes
            url_attributes = ['src', 'data-src', 'data-video-url', 'data-url', 'href', 'data-href']
            for attr in url_attributes:
                try:
                    url = element.get_attribute(attr)
                    if url and self.is_valid_video_url(url):
                        video_urls.append(url)
                except:
                    continue
                    
            # Strategy 3: Check parent and children
            try:
                parent = element.find_element(By.XPATH, "./..")
                for attr in url_attributes:
                    url = parent.get_attribute(attr)
                    if url and self.is_valid_video_url(url):
                        video_urls.append(url)
                        
                # Check children
                children = element.find_elements(By.XPATH, ".//*")
                for child in children:
                    for attr in url_attributes:
                        try:
                            url = child.get_attribute(attr)
                            if url and self.is_valid_video_url(url):
                                video_urls.append(url)
                        except:
                            continue
            except:
                pass
                
            # Strategy 4: JavaScript execution to find hidden URLs
            try:
                js_urls = self.driver.execute_script("""
                    var urls = [];
                    var element = arguments[0];
                    
                    // Check all attributes
                    for (var i = 0; i < element.attributes.length; i++) {
                        var attr = element.attributes[i];
                        if (attr.value && (attr.value.includes('mp4') || attr.value.includes('webm') || attr.value.includes('googlevideo'))) {
                            urls.push(attr.value);
                        }
                    }
                    
                    // Check data attributes
                    var dataset = element.dataset;
                    for (var key in dataset) {
                        if (dataset[key] && (dataset[key].includes('mp4') || dataset[key].includes('webm') || dataset[key].includes('googlevideo'))) {
                            urls.push(dataset[key]);
                        }
                    }
                    
                    return urls;
                """, element)
                
                for url in js_urls:
                    if self.is_valid_video_url(url):
                        video_urls.append(url)
                        
            except Exception as e:
                logger.debug(f"JavaScript extraction failed: {str(e)}")
                
            # Remove duplicates and return best URL
            unique_urls = list(set(video_urls))
            if unique_urls:
                # Prefer googlevideo URLs
                for url in unique_urls:
                    if 'googlevideo' in url:
                        return url
                return unique_urls[0]
                
        except Exception as e:
            logger.error(f"Error extracting video {index + 1}: {str(e)}")
            
        return None
        
    def is_valid_video_url(self, url):
        """Check if URL is a valid video URL"""
        if not url or not isinstance(url, str):
            return False
            
        video_indicators = ['mp4', 'webm', 'googlevideo', 'videoplayback']
        return any(indicator in url.lower() for indicator in video_indicators)
        
    def extract_video_metadata_enhanced(self, element, index):
        """Enhanced metadata extraction"""
        try:
            # Try to find meaningful name
            video_name = f"Veo 3 Quality Video {index + 1}"
            
            # Look for text content
            text_content = ""
            try:
                text_content = element.text.strip()
                if not text_content:
                    parent = element.find_element(By.XPATH, "./..")
                    text_content = parent.text.strip()
            except:
                pass
                
            # Extract meaningful title from text
            if text_content and len(text_content) < 200:
                # Clean up the text
                clean_text = re.sub(r'[^\w\s-]', '', text_content)
                if clean_text and 'veo' not in clean_text.lower():
                    video_name = f"Veo 3 - {clean_text[:50]}"
                    
            # Try to find prompt or description
            description = ""
            try:
                # Look for nearby text that might be a prompt
                nearby_text = self.driver.execute_script("""
                    var element = arguments[0];
                    var parent = element.parentElement;
                    var allText = '';
                    
                    // Get text from siblings
                    if (parent) {
                        var siblings = parent.children;
                        for (var i = 0; i < siblings.length; i++) {
                            allText += siblings[i].textContent + ' ';
                        }
                    }
                    
                    return allText.trim();
                """, element)
                
                if nearby_text and len(nearby_text) > 10:
                    description = nearby_text[:300]
                    
            except:
                pass
                
            return {
                'name': video_name,
                'description': description,
                'text_content': text_content[:200] if text_content else ""
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata for video {index + 1}: {str(e)}")
            return {
                'name': f"Veo 3 Quality Video {index + 1}",
                'description': "",
                'text_content': ""
            }
            
    def extract_all_veo3_complete(self, project_url):
        """Complete extraction with all strategies"""
        try:
            logger.info(f"🚀 Starting COMPLETE Veo 3 extraction: {project_url}")
            self.driver.get(project_url)
            
            print("\n" + "="*80)
            print("🎯 COMPLETE VEO 3 EXTRACTOR - MAXIMUM COVERAGE")
            print("="*80)
            print("This will find ALL Veo 3 videos using every possible method!")
            print("1. Please log in to your Google Flow project")
            print("2. Navigate to your project and scroll to see some videos")
            print("3. This will then do extreme scrolling to find ALL videos")
            print("4. Press ENTER when ready to start complete extraction...")
            print("="*80)
            
            input("Press ENTER when logged in and ready for COMPLETE extraction...")
            
            # Wait for initial load
            time.sleep(5)
            
            # Extreme scrolling to load all content
            self.extreme_scroll_and_load()
            
            # Comprehensive element detection
            all_elements = self.find_all_veo3_comprehensive()
            
            if not all_elements:
                logger.warning("❌ No elements found!")
                return
                
            logger.info(f"🎯 Found {len(all_elements)} total elements to process")
            
            # Process each element
            successful_extractions = 0
            for i, element in enumerate(all_elements):
                try:
                    if i % 10 == 0:
                        logger.info(f"📊 Processing element {i + 1}/{len(all_elements)}")
                    
                    # Check if element is near Veo 3 text
                    is_veo3_related = self.is_element_veo3_related(element)
                    
                    if not is_veo3_related:
                        continue
                        
                    # Extract metadata
                    metadata = self.extract_video_metadata_enhanced(element, successful_extractions)
                    
                    # Extract video URL
                    video_url = self.extract_video_with_multiple_strategies(element, successful_extractions)
                    
                    # Skip if we already have this URL
                    if video_url and video_url in self.found_urls:
                        logger.debug(f"Skipping duplicate URL: {video_url[:50]}...")
                        continue
                        
                    if video_url:
                        self.found_urls.add(video_url)
                        
                    # Create video data
                    video_data = {
                        'Ad_ID': self.base_ad_id + successful_extractions + 1,
                        'Creative_ID': self.base_ad_id + successful_extractions + 1,
                        'Ad_Name': f"video: {metadata['name']}",
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
                        'Meta_Video_URL': video_url if video_url else 'TBD',
                        'Google_Drive_Download_Link': 'TBD',
                        'Google_Drive_View_Link': 'TBD',
                        'Creative_Type': 'AI Generated - Veo 3',
                        'Hook_Type': 'TBD',
                        'Targeting': 'Broad',
                        'Priority': '🔍 VEO3_REVIEW'
                    }
                    
                    # Generate download command
                    if video_url:
                        safe_name = metadata['name'].replace(' ', '_').replace('/', '_').replace(':', '_')
                        video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
                    else:
                        video_data['Download_Command'] = 'TBD'
                        
                    # Enhanced notes
                    notes_parts = [
                        "Veo 3 - Quality",
                        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                        f"Complete Extraction {successful_extractions + 1}",
                        "URL Status: " + ("✅ Found" if video_url else "⚠️ Missing")
                    ]
                    
                    if metadata['description']:
                        notes_parts.append(f"Content: {metadata['description'][:100]}...")
                        
                    video_data['Notes'] = " | ".join(notes_parts)
                    
                    self.veo3_videos.append(video_data)
                    successful_extractions += 1
                    
                    logger.info(f"✅ Successfully processed Veo 3 video {successful_extractions}" + 
                              (" with URL!" if video_url else " (no URL)"))
                    
                except Exception as e:
                    logger.debug(f"Error processing element {i + 1}: {str(e)}")
                    continue
                    
            logger.info(f"🎉 Complete extraction finished! Found {successful_extractions} Veo 3 videos")
            
        except Exception as e:
            logger.error(f"Error in complete extraction: {str(e)}")
            
    def is_element_veo3_related(self, element):
        """Check if element is related to Veo 3"""
        try:
            # Check element text
            element_text = element.text.lower()
            if 'veo' in element_text and ('3' in element_text or 'quality' in element_text):
                return True
                
            # Check parent text
            try:
                parent = element.find_element(By.XPATH, "./..")
                parent_text = parent.text.lower()
                if 'veo' in parent_text and ('3' in parent_text or 'quality' in parent_text):
                    return True
            except:
                pass
                
            # Check attributes
            for attr in ['class', 'id', 'data-label', 'title', 'alt']:
                try:
                    attr_value = element.get_attribute(attr)
                    if attr_value and 'veo' in attr_value.lower():
                        return True
                except:
                    continue
                    
            # Check if it's a video element
            if element.tag_name == 'video':
                return True
                
            # Check if it has video-related attributes
            video_attrs = ['src', 'data-src', 'data-video', 'data-video-url']
            for attr in video_attrs:
                try:
                    attr_value = element.get_attribute(attr)
                    if attr_value and ('mp4' in attr_value or 'webm' in attr_value or 'googlevideo' in attr_value):
                        return True
                except:
                    continue
                    
            return False
            
        except:
            return False
            
    def save_complete_data(self, filename=None):
        """Save complete extraction data"""
        if not self.veo3_videos:
            logger.warning("No Veo 3 videos to save")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Veo3_COMPLETE_{len(self.veo3_videos)}_videos_{timestamp}.csv'
            
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
        logger.info(f"Complete extraction data saved to {filename}")
        
        # Save raw JSON
        raw_filename = filename.replace('.csv', '_raw.json')
        with open(raw_filename, 'w') as f:
            json.dump(self.veo3_videos, f, indent=2)
            
        return filename
        
    def print_complete_summary(self):
        """Print complete extraction summary"""
        if not self.veo3_videos:
            print("❌ No Veo 3 videos found.")
            return
            
        print(f"\n{'='*90}")
        print(f"🎯 COMPLETE VEO 3 EXTRACTION SUMMARY")
        print(f"{'='*90}")
        print(f"🎬 Total Veo 3 videos extracted: {len(self.veo3_videos)}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze URL extraction success
        with_urls = sum(1 for v in self.veo3_videos if v.get('Meta_Video_URL', 'TBD') != 'TBD')
        success_rate = (with_urls / len(self.veo3_videos)) * 100 if self.veo3_videos else 0
        
        print(f"\n📊 URL Extraction Results:")
        print(f"  ✅ Videos with URLs: {with_urls}/{len(self.veo3_videos)}")
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        print(f"  🔗 Unique URLs found: {len(self.found_urls)}")
        
        print(f"\n🎬 All Veo 3 Videos Found:")
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
    print("🚀 COMPLETE VEO 3 EXTRACTOR - MAXIMUM COVERAGE")
    print("="*70)
    print("This will use EVERY possible method to find ALL Veo 3 videos!")
    print("⚠️  This may take several minutes due to extensive scrolling.")
    
    project_url = input("Enter your Google Flow project URL (or press ENTER for default): ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = CompleteVeo3Extractor(headless=False)
    
    try:
        extractor.extract_all_veo3_complete(project_url)
        extractor.print_complete_summary()
        
        if extractor.veo3_videos:
            filename = extractor.save_complete_data()
            print(f"\n🎉 ALL Veo 3 videos extracted to: {filename}")
            print("✅ Ready for Airtable import!")
            print(f"📊 Successfully captured {len(extractor.veo3_videos)} Veo 3 videos!")
            
            # Show URL extraction success
            with_urls = sum(1 for v in extractor.veo3_videos if v.get('Meta_Video_URL', 'TBD') != 'TBD')
            print(f"🔗 Videos with download URLs: {with_urls}/{len(extractor.veo3_videos)}")
            
            if with_urls > 0:
                print("\n🎬 Sample download commands:")
                for i, video in enumerate(extractor.veo3_videos[:3]):
                    if video.get('Meta_Video_URL', 'TBD') != 'TBD':
                        print(f"  {i+1}. {video.get('Download_Command', 'N/A')}")
        else:
            print("\n❌ No Veo 3 videos were found.")
            print("💡 Try manually scrolling through your Flow project to load more content.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Extraction cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
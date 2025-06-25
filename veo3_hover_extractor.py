#!/usr/bin/env python3
"""
Veo 3 Hover URL Extractor
Creation Date: June 24, 2025
Version: 1.0

This script uses hover actions to extract video URLs from ALL Veo 3 videos
by hovering over each image to reveal the download URL.
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

class Veo3HoverExtractor:
    def __init__(self, headless=False):
        """Initialize the hover extractor"""
        self.setup_driver(headless)
        self.veo3_videos = []
        self.base_ad_id = 300001000000000
        self.hover_delay = 2  # Seconds to wait after hover
        
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
        
    def comprehensive_scroll_and_load(self):
        """Comprehensive scrolling to ensure all content is loaded"""
        logger.info("Starting comprehensive scroll to load all Veo 3 content...")
        
        # Multiple scroll strategies
        for phase in range(3):
            logger.info(f"Scroll phase {phase + 1}/3")
            
            # Scroll to top first
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Get initial height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 50
            
            while scroll_attempts < max_attempts:
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Check for new content
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    # Try extra scrolls
                    for extra in range(3):
                        self.driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(2)
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
        
        logger.info("Comprehensive scrolling completed!")
        
    def find_all_veo3_video_elements(self):
        """Find all Veo 3 video elements using multiple strategies"""
        logger.info("Finding all Veo 3 video elements...")
        
        veo3_elements = []
        
        # Strategy 1: Find elements containing "Veo 3" text
        text_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Veo 3')]")
        logger.info(f"Found {len(text_elements)} elements with 'Veo 3' text")
        
        # Strategy 2: Find video-related elements
        video_selectors = [
            'video',
            'img[src*="video"]',
            '[data-video]',
            '.video-card',
            '.video-item',
            '.media-card',
            '.media-item',
            'div[class*="video"]',
            'div[class*="media"]',
        ]
        
        for selector in video_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    veo3_elements.extend(elements)
            except:
                continue
        
        # Strategy 3: Find images that might be video thumbnails
        image_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img')
        logger.info(f"Found {len(image_elements)} total images to check")
        
        # Filter for images that might be Veo 3 videos
        potential_veo3_images = []
        for img in image_elements:
            try:
                # Check if image is near Veo 3 text
                parent = img.find_element(By.XPATH, './ancestor::*[contains(text(), "Veo 3") or contains(@class, "veo") or contains(@data-label, "veo")]')
                if parent:
                    potential_veo3_images.append(img)
                    continue
            except:
                pass
            
            # Check image attributes
            try:
                src = img.get_attribute('src') or ''
                alt = img.get_attribute('alt') or ''
                title = img.get_attribute('title') or ''
                
                if any(keyword in (src + alt + title).lower() for keyword in ['veo', 'video', 'quality']):
                    potential_veo3_images.append(img)
            except:
                continue
                
        logger.info(f"Found {len(potential_veo3_images)} potential Veo 3 video images")
        veo3_elements.extend(potential_veo3_images)
        
        # Remove duplicates
        unique_elements = list(set(veo3_elements))
        logger.info(f"Total unique Veo 3 elements found: {len(unique_elements)}")
        
        return unique_elements
        
    def extract_video_url_with_hover(self, element, index):
        """Extract video URL by hovering over element and checking for revealed URLs"""
        logger.info(f"Attempting to extract URL for element {index + 1} using hover...")
        
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            
            # Create action chain for hover
            actions = ActionChains(self.driver)
            
            # Hover over the element
            actions.move_to_element(element).perform()
            time.sleep(self.hover_delay)
            
            # Strategy 1: Look for video elements that appeared after hover
            video_urls = []
            
            # Check for video elements
            try:
                videos = self.driver.find_elements(By.CSS_SELECTOR, 'video')
                for video in videos:
                    src = video.get_attribute('src')
                    if src and ('mp4' in src or 'webm' in src or 'googlevideo' in src):
                        video_urls.append(src)
                        logger.info(f"Found video URL via hover: {src[:100]}...")
            except:
                pass
            
            # Strategy 2: Check for source elements
            try:
                sources = self.driver.find_elements(By.CSS_SELECTOR, 'source')
                for source in sources:
                    src = source.get_attribute('src')
                    if src and ('mp4' in src or 'webm' in src or 'googlevideo' in src):
                        video_urls.append(src)
                        logger.info(f"Found source URL via hover: {src[:100]}...")
            except:
                pass
            
            # Strategy 3: Check for data attributes that might have appeared
            url_attrs = ['data-src', 'data-video-url', 'data-url', 'data-video', 'href']
            for attr in url_attrs:
                try:
                    url = element.get_attribute(attr)
                    if url and ('video' in url or 'mp4' in url or 'webm' in url or 'googlevideo' in url):
                        video_urls.append(url)
                        logger.info(f"Found {attr} URL via hover: {url[:100]}...")
                except:
                    continue
            
            # Strategy 4: Check nearby elements that might have been revealed
            try:
                parent = element.find_element(By.XPATH, './..')
                nearby_videos = parent.find_elements(By.CSS_SELECTOR, 'video, [src*="mp4"], [src*="webm"], [src*="googlevideo"]')
                for vid in nearby_videos:
                    src = vid.get_attribute('src')
                    if src and src not in video_urls:
                        video_urls.append(src)
                        logger.info(f"Found nearby URL via hover: {src[:100]}...")
            except:
                pass
            
            # Strategy 5: Check for tooltips or overlays that might contain URLs
            try:
                tooltips = self.driver.find_elements(By.CSS_SELECTOR, '[role="tooltip"], .tooltip, .overlay, .popup')
                for tooltip in tooltips:
                    if tooltip.is_displayed():
                        tooltip_html = tooltip.get_attribute('outerHTML')
                        # Look for URLs in tooltip content
                        import re
                        urls = re.findall(r'https?://[^\s<>"]+(?:mp4|webm|googlevideo)[^\s<>"]*', tooltip_html)
                        for url in urls:
                            if url not in video_urls:
                                video_urls.append(url)
                                logger.info(f"Found tooltip URL via hover: {url[:100]}...")
            except:
                pass
            
            # Strategy 6: Check network requests (if possible)
            try:
                # This would require additional setup to monitor network requests
                # For now, we'll skip this advanced technique
                pass
            except:
                pass
            
            # Return the first valid URL found
            if video_urls:
                return video_urls[0]  # Return the first URL found
            else:
                logger.warning(f"No video URL found for element {index + 1} after hover")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting URL with hover for element {index + 1}: {str(e)}")
            return None
            
    def extract_video_metadata(self, element, index):
        """Extract video metadata including name, description, etc."""
        try:
            # Try to find video title/name
            video_name = f"Veo 3 Quality Video {index + 1}"
            
            # Look for title elements near the video
            title_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.name', '.caption', '.description']
            
            for selector in title_selectors:
                try:
                    # Check element itself
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) < 100 and 'veo' not in title_text.lower():
                        video_name = f"Veo 3 - {title_text}"
                        break
                except:
                    pass
                
                try:
                    # Check parent element
                    parent = element.find_element(By.XPATH, './..')
                    title_elem = parent.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) < 100 and 'veo' not in title_text.lower():
                        video_name = f"Veo 3 - {title_text}"
                        break
                except:
                    continue
            
            # Try to extract any visible text that might be a description
            element_text = ""
            try:
                element_text = element.text.strip()
                if not element_text:
                    parent = element.find_element(By.XPATH, './..')
                    element_text = parent.text.strip()
            except:
                pass
            
            return {
                'name': video_name,
                'description': element_text[:200] if element_text else "",
                'element_html': element.get_attribute('outerHTML')[:500] if element else ""
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata for element {index + 1}: {str(e)}")
            return {
                'name': f"Veo 3 Quality Video {index + 1}",
                'description': "",
                'element_html': ""
            }
            
    def extract_all_veo3_with_hover(self, project_url):
        """Extract all Veo 3 videos using hover technique"""
        try:
            logger.info(f"Starting Veo 3 hover extraction: {project_url}")
            self.driver.get(project_url)
            
            print("\n" + "="*70)
            print("VEO 3 HOVER URL EXTRACTOR")
            print("="*70)
            print("This will hover over each Veo 3 video to extract download URLs!")
            print("1. Please log in to your Google Flow project")
            print("2. Navigate to your project with all the Veo 3 videos")
            print("3. This will hover over each video to reveal URLs")
            print("4. Press ENTER when ready to start the hover extraction...")
            print("="*70)
            
            input("Press ENTER when logged in and ready for hover extraction...")
            
            # Wait for initial load
            time.sleep(5)
            
            # Comprehensive scroll to load all content
            self.comprehensive_scroll_and_load()
            
            # Find all Veo 3 elements
            veo3_elements = self.find_all_veo3_video_elements()
            
            if not veo3_elements:
                logger.warning("No Veo 3 elements found!")
                return
                
            logger.info(f"Found {len(veo3_elements)} potential Veo 3 elements. Starting hover extraction...")
            
            # Process each element with hover
            successful_extractions = 0
            for i, element in enumerate(veo3_elements):
                try:
                    logger.info(f"Processing element {i + 1}/{len(veo3_elements)}")
                    
                    # Extract metadata
                    metadata = self.extract_video_metadata(element, successful_extractions)
                    
                    # Extract URL with hover
                    video_url = self.extract_video_url_with_hover(element, i)
                    
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
                    
                    # Generate download command if URL found
                    if video_url:
                        safe_name = metadata['name'].replace(' ', '_').replace('/', '_').replace(':', '_')
                        video_data['Download_Command'] = f'yt-dlp "{video_url}" -f "best[ext=mp4]" -o "{safe_name}.%(ext)s"'
                    else:
                        video_data['Download_Command'] = 'TBD'
                    
                    # Enhanced notes
                    notes_parts = [
                        "Veo 3 - Quality",
                        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                        f"Hover Extraction {successful_extractions + 1}",
                        "URL Status: " + ("✅ Found" if video_url else "⚠️ Missing")
                    ]
                    
                    if metadata['description']:
                        notes_parts.append(f"Content: {metadata['description'][:100]}...")
                        
                    video_data['Notes'] = " | ".join(notes_parts)
                    
                    self.veo3_videos.append(video_data)
                    successful_extractions += 1
                    
                    logger.info(f"Successfully processed Veo 3 video {successful_extractions}" + 
                              (" with URL!" if video_url else " (no URL found)"))
                    
                    # Small delay between elements
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing element {i + 1}: {str(e)}")
                    continue
                    
            logger.info(f"Hover extraction completed. Successfully extracted {successful_extractions} Veo 3 videos")
            
        except Exception as e:
            logger.error(f"Error in hover extraction: {str(e)}")
            
    def save_hover_data(self, filename=None):
        """Save hover extraction data"""
        if not self.veo3_videos:
            logger.warning("No Veo 3 videos to save")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'GoogleFlow_Veo3_Hover_URLs_{len(self.veo3_videos)}_videos_{timestamp}.csv'
            
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
        logger.info(f"Hover extraction data saved to {filename}")
        
        # Save raw JSON
        raw_filename = filename.replace('.csv', '_raw.json')
        with open(raw_filename, 'w') as f:
            json.dump(self.veo3_videos, f, indent=2)
            
        return filename
        
    def print_hover_summary(self):
        """Print hover extraction summary"""
        if not self.veo3_videos:
            print("No Veo 3 videos found.")
            return
            
        print(f"\n{'='*80}")
        print(f"VEO 3 HOVER EXTRACTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Veo 3 videos extracted: {len(self.veo3_videos)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze URL extraction success
        with_urls = sum(1 for v in self.veo3_videos if v.get('Meta_Video_URL', 'TBD') != 'TBD')
        success_rate = (with_urls / len(self.veo3_videos)) * 100 if self.veo3_videos else 0
        
        print(f"\n📊 URL Extraction Results:")
        print(f"  ✅ Videos with URLs: {with_urls}/{len(self.veo3_videos)}")
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎬 All Veo 3 Videos with Hover URLs:")
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
    print("🎯 VEO 3 HOVER URL EXTRACTOR")
    print("="*60)
    print("This will hover over each Veo 3 video to extract ALL download URLs!")
    print("⚠️  Make sure your Flow project is fully loaded before starting.")
    
    project_url = input("Enter your Google Flow project URL (or press ENTER for default): ").strip()
    if not project_url:
        project_url = "https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275"
        
    extractor = Veo3HoverExtractor(headless=False)
    
    try:
        extractor.extract_all_veo3_with_hover(project_url)
        extractor.print_hover_summary()
        
        if extractor.veo3_videos:
            filename = extractor.save_hover_data()
            print(f"\n🎉 ALL Veo 3 videos with hover URLs exported to: {filename}")
            print("✅ Ready for Airtable import!")
            print(f"📊 Successfully captured {len(extractor.veo3_videos)} Veo 3 videos!")
            
            # Show URL extraction success
            with_urls = sum(1 for v in extractor.veo3_videos if v.get('Meta_Video_URL', 'TBD') != 'TBD')
            print(f"🔗 Videos with download URLs: {with_urls}/{len(extractor.veo3_videos)}")
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
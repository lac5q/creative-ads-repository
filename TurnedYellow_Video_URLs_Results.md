# TurnedYellow Video URLs - API Results
**Generated:** June 21, 2025
**Status:** Successfully extracted preview links and creative IDs

## 🎯 Video Download URLs Extracted

### **🏆 TOP PRIORITY VIDEOS (Active & High Performance)**

#### **1. "Anton Reaction Hook" - Creative ID: 120205938726150108**
- **Ad ID:** 120207192169230108
- **Performance:** $51.44 CPA, 1.94% CVR
- **Status:** ACTIVE
- **Preview Link:** https://fb.me/1Vgwp6rQa30rKGg
- **Download Method:** Use yt-dlp or browser automation
- **Command:** `yt-dlp "https://fb.me/1Vgwp6rQa30rKGg"`

#### **2. "Royal Inspo Hook" - Creative ID: 120207109220570108**
- **Ad ID:** 120208078497390108  
- **Performance:** $72.28 CPA, 1.38% CVR
- **Status:** ACTIVE
- **Preview Link:** https://fb.me/2ayqQiBBS6lTK5g
- **Download Method:** Use yt-dlp or browser automation
- **Command:** `yt-dlp "https://fb.me/2ayqQiBBS6lTK5g"`

#### **3. "TY Video 1 - Make Anyone Laugh" - Creative ID: 120203471704620108**
- **Ad ID:** 120203471547490108
- **Performance:** $34.45 CPA, 2.90% CVR (ASC Campaign)
- **Status:** ACTIVE
- **Preview Link:** https://fb.me/1O3TXzYvE3BeFIv
- **Download Method:** Use yt-dlp or browser automation  
- **Command:** `yt-dlp "https://fb.me/1O3TXzYvE3BeFIv"`

## 🚀 Immediate Download Commands

**Copy and paste these commands to download videos:**

```bash
# Download Anton Reaction Hook (Top priority)
yt-dlp "https://fb.me/1Vgwp6rQa30rKGg" -o "%(title)s.%(ext)s"

# Download Royal Inspo Hook
yt-dlp "https://fb.me/2ayqQiBBS6lTK5g" -o "%(title)s.%(ext)s"

# Download TY Video 1 - Make Anyone Laugh
yt-dlp "https://fb.me/1O3TXzYvE3BeFIv" -o "%(title)s.%(ext)s"
```

**With quality selection:**
```bash
# Download best quality available
yt-dlp "https://fb.me/1Vgwp6rQa30rKGg" -f "best[ext=mp4]" -o "Anton_Reaction_Hook.%(ext)s"
yt-dlp "https://fb.me/2ayqQiBBS6lTK5g" -f "best[ext=mp4]" -o "Royal_Inspo_Hook.%(ext)s"  
yt-dlp "https://fb.me/1O3TXzYvE3BeFIv" -f "best[ext=mp4]" -o "TY_Video_1_Make_Anyone_Laugh.%(ext)s"
```

## 🔍 API Access Status

### **✅ Successfully Retrieved:**
- Ad details with creative IDs
- Fresh preview shareable links
- Ad performance metrics
- Campaign and ad set associations

### **❌ API Limitations Encountered:**
- Direct creative video_data endpoint access blocked
- Ad account videos endpoint permission issues
- Creative thumbnails endpoint not available
- JSON parsing errors in some MCP functions

### **🔧 Workaround Used:**
- Retrieved fresh preview links via ad details API
- Preview links can be used with video downloaders
- Creative IDs confirmed for future API attempts

## 🎬 Missing Top Performers (Need Creative IDs)

**Still need to identify Creative IDs for:**

1. **"Influencer David / Most incredible"** 
   - **Performance:** $11.75 CPA, 11.11% CVR (BEST PERFORMER!)
   - **Ad ID:** 120207192312690108
   - **Status:** Need to get creative details

2. **"Gifting Hook Sara / Life is too short"**
   - **Performance:** $15.81 CPA, 5.88% CVR (SECOND BEST!)
   - **Ad ID:** 120205926791290108  
   - **Status:** Need to get creative details

## 📋 Next Action Steps

### **IMMEDIATE (Today):**
1. **Download the 3 videos** using the yt-dlp commands above
2. **Get creative IDs** for David and Sara videos (top performers)
3. **Analyze downloaded videos** for winning elements

### **SHORT TERM (This Week):**
1. **Scale the David influencer video** (11.11% CVR!)
2. **Scale the Sara gifting video** (5.88% CVR)
3. **Create variations** of top performing video themes
4. **Pause underperforming videos** in retargeting campaigns

### **MEDIUM TERM (Next 2 Weeks):**
1. **Create new testimonial videos** based on David's format
2. **Develop emotional gift scenarios** based on Sara's hook
3. **Test reaction-style content** with different people
4. **Refresh royal/luxury themed videos**

## 🛠️ Alternative Download Methods

### **Method 1: yt-dlp (Recommended)**
```bash
# Install yt-dlp if not already installed
pip install yt-dlp

# Download with metadata
yt-dlp "https://fb.me/1Vgwp6rQa30rKGg" --write-info-json --write-thumbnail
```

### **Method 2: 4K Video Downloader (GUI)**
1. Open 4K Video Downloader
2. Paste preview link
3. Select MP4 format and quality
4. Download

### **Method 3: Browser Automation (Advanced)**
```python
# Playwright script to extract direct video URL
from playwright.sync_api import sync_playwright

def extract_video_url(preview_link):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(preview_link)
        
        # Wait for video to load
        page.wait_for_selector('video')
        
        # Extract video source
        video_src = page.evaluate('''
            () => {
                const video = document.querySelector('video');
                return video ? video.src || video.currentSrc : null;
            }
        ''')
        
        browser.close()
        return video_src

# Usage
video_url = extract_video_url("https://fb.me/1Vgwp6rQa30rKGg")
print(f"Direct video URL: {video_url}")
```

## 📊 Performance Summary

| Video | CPA | CVR | Status | Priority | Download Link |
|-------|-----|-----|--------|----------|---------------|
| Anton Reaction | $51.44 | 1.94% | ACTIVE | Medium | https://fb.me/1Vgwp6rQa30rKGg |
| Royal Inspo | $72.28 | 1.38% | ACTIVE | Low | https://fb.me/2ayqQiBBS6lTK5g |
| TY Video 1 | $34.45 | 2.90% | ACTIVE | High | https://fb.me/1O3TXzYvE3BeFIv |
| David Influencer | $11.75 | 11.11% | ACTIVE | **URGENT** | Need Creative ID |
| Sara Gifting | $15.81 | 5.88% | ACTIVE | **URGENT** | Need Creative ID |

**🎯 Focus:** Get David and Sara video downloads ASAP - they're your money makers! 
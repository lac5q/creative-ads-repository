# TurnedYellow Video Ad Download Methods Guide
**Updated:** June 21, 2025

## 🎯 Better Video Download Methods (Not Preview Links)

### **Method 1: Direct Creative API Access** ⭐ **RECOMMENDED**

**API Endpoint:** `https://graph.facebook.com/v22.0/{creative-id}`

**Required Fields for Video Downloads:**
```
fields=object_story_spec,video_data,asset_feed_spec,thumbnail_url
```

**Your Top Video Creative IDs:**
- **120205938726150108** (Anton Reaction Hook - Best Performer)
- **120207109220570108** (Royal Inspo Hook)
- **120203471704620108** (TY Video 1 - Make Anyone Laugh)

**Example API Call:**
```bash
curl -X GET \
"https://graph.facebook.com/v22.0/120205938726150108?fields=object_story_spec,video_data,asset_feed_spec,thumbnail_url&access_token=YOUR_TOKEN"
```

### **Method 2: Ad Account Videos Endpoint** ⭐ **BEST FOR BULK**

**API Endpoint:** `https://graph.facebook.com/v22.0/act_2391476931086052/advideos`

**Fields for Video Files:**
```
fields=id,name,source,thumbnails,length,updated_time,created_time,permalink_url
```

**Example API Call:**
```bash
curl -X GET \
"https://graph.facebook.com/v22.0/act_2391476931086052/advideos?fields=id,name,source,thumbnails,length,updated_time,created_time,permalink_url&access_token=YOUR_TOKEN"
```

### **Method 3: Browser Automation (Playwright/Selenium)**

**Target URLs for Video Extraction:**
1. **Anton Reaction:** https://fb.me/1Z04LG8B6UfjqHi
2. **Royal Inspo:** https://fb.me/1LBGhkWtpHWDyFL
3. **TY Video 1:** https://fb.me/30yENSgUQFCNruz

**Playwright Script Approach:**
```javascript
// Extract actual video source from preview page
const page = await browser.newPage();
await page.goto('https://fb.me/1Z04LG8B6UfjqHi');
const videoSrc = await page.evaluate(() => {
    const video = document.querySelector('video source, video');
    return video ? video.src || video.currentSrc : null;
});
```

### **Method 4: Facebook Video Downloader Tools**

**Recommended Tools:**
1. **yt-dlp** (Command Line)
   ```bash
   yt-dlp "https://fb.me/1Z04LG8B6UfjqHi"
   ```

2. **4K Video Downloader** (GUI)
   - Paste preview link
   - Select quality
   - Download directly

3. **SaveFrom.net** (Web-based)
   - Supports Facebook video links
   - No software installation needed

## 🔑 Access Tokens & Permissions

**Required Permissions for Video Access:**
- `ads_read`
- `ads_management` 
- `business_management`
- `pages_read_engagement` (for video content)

**Current Token:** Available via Pipeboard API (already configured)

## 📊 Video Quality & Format Information

**Expected Video Formats:**
- **MP4** (Most common)
- **MOV** (iPhone uploads)
- **WebM** (Web optimized)

**Quality Levels Available:**
- **SD (480p)** - Standard definition
- **HD (720p)** - High definition  
- **Source** - Original upload quality

## 🎬 Priority Download List (Based on Performance)

### **🏆 IMMEDIATE DOWNLOAD (Top Performers)**

1. **"Influencer David" Video** 
   - **Performance:** $11.75 CPA, 11.11% CVR
   - **Status:** ACTIVE - Scale immediately
   - **Creative ID:** TBD (need to identify)

2. **"Gifting Hook Sara" Video**
   - **Performance:** $15.81 CPA, 5.88% CVR  
   - **Status:** ACTIVE - Scale with budget
   - **Creative ID:** TBD (need to identify)

3. **"Anton Reaction Hook"**
   - **Creative ID:** 120205938726150108
   - **Performance:** $51.44 CPA, 1.94% CVR
   - **Preview:** https://fb.me/1Z04LG8B6UfjqHi

### **🔄 SECONDARY DOWNLOAD (For Analysis)**

4. **"Royal Inspo Hook"**
   - **Creative ID:** 120207109220570108
   - **Performance:** $72.28 CPA, 1.38% CVR
   - **Preview:** https://fb.me/1LBGhkWtpHWDyFL

5. **"TY Video 1 - Make Anyone Laugh"**
   - **Creative ID:** 120203471704620108
   - **Performance:** Variable ($34.45 - $172.27 CPA)
   - **Preview:** https://fb.me/30yENSgUQFCNruz

## 🚀 Automated Download Script

**Python Script Using Meta Graph API:**
```python
import requests
import json

def download_video_from_creative(creative_id, access_token):
    url = f"https://graph.facebook.com/v22.0/{creative_id}"
    params = {
        'fields': 'object_story_spec,video_data,asset_feed_spec',
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract video URL from response
    if 'object_story_spec' in data:
        video_data = data['object_story_spec'].get('video_data', {})
        video_url = video_data.get('video_id') or video_data.get('source')
        return video_url
    
    return None

# Your creative IDs
creative_ids = [
    "120205938726150108",  # Anton Reaction
    "120207109220570108",  # Royal Inspo  
    "120203471704620108"   # TY Video 1
]

for creative_id in creative_ids:
    video_url = download_video_from_creative(creative_id, YOUR_ACCESS_TOKEN)
    print(f"Creative {creative_id}: {video_url}")
```

## 📝 Next Steps

1. **Try Method 1** (Direct Creative API) first
2. **Use Method 2** (Ad Videos Endpoint) for bulk download
3. **Fallback to Method 3** (Browser automation) if API fails
4. **Use Method 4** (Download tools) for quick manual downloads

**Priority Actions:**
1. Identify Creative IDs for "David" and "Sara" videos (top performers)
2. Download all 5 priority videos using API methods
3. Analyze video content for scaling insights
4. Create new videos based on top performer elements 
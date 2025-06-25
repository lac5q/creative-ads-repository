# Facebook Ad Video Download Solution

## 🎯 Problem Solved
You wanted easier access to your Facebook ad videos instead of the `fb.me` links that redirect to Facebook. 

## 🛠️ Solution Provided

### **Automated Download & Google Drive Upload Script**
I've created a comprehensive solution that:

1. **Extracts real video URLs** from Meta's API (not redirect links)
2. **Downloads videos locally** with proper filenames
3. **Uploads to Google Drive** automatically
4. **Updates your spreadsheet** with direct download links
5. **Cleans up local files** to save space

### **Files Created:**

| File | Purpose |
|------|---------|
| `video_downloader_to_gdrive.py` | Main script that processes all videos |
| `configure_tokens.py` | Helper to set up Meta token & Google Drive folder |
| `requirements.txt` | Python dependencies needed |
| `SETUP_INSTRUCTIONS.md` | Complete setup guide |
| `Enhanced_Video_Metrics_Both_Accounts_Last_3_Months.csv` | Updated spreadsheet with new columns |

### **New Spreadsheet Columns Added:**

- **`Facebook_Link`**: Original fb.me redirect links
- **`Meta_Video_URL`**: Direct video URL from Meta API
- **`GDrive_Download_Link`**: Direct download from Google Drive
- **`GDrive_View_Link`**: Viewable link in Google Drive

## 🚀 How to Use

### **Quick Start:**
1. **Configure:** `python configure_tokens.py`
2. **Install:** `pip install -r requirements.txt`
3. **Setup Google Drive API** (see SETUP_INSTRUCTIONS.md)
4. **Run:** `python video_downloader_to_gdrive.py`

### **What Happens:**
- Script reads your CSV with 22 video ads
- Gets real video URLs from Meta API
- Downloads each video with clean filenames like:
  - `TurnedYellow_120208078493940109_David_Influencer_Video.mp4`
  - `MakeMeJedi_295772075784587301_Jedi_Master_Training.mp4`
- Uploads to your Google Drive folder
- Updates CSV with Google Drive links
- Cleans up local downloads

## 📊 Expected Results

**Before:** 22 ads with fb.me redirect links
**After:** 22 ads with:
- ✅ Direct Meta video URLs  
- ✅ Google Drive download links
- ✅ Google Drive view links
- ✅ Download status for each

## 🎁 Alternative Options

If you prefer manual control, the script also provides:

1. **Direct Meta URLs** you can use with:
   - `yt-dlp "VIDEO_URL"`
   - `wget "VIDEO_URL" -O filename.mp4`
   - Browser downloads

2. **Batch Processing** - run script periodically for new ads

3. **Custom Folders** - organize by campaign, performance, etc.

## 🔒 Security & Privacy

- Uses your existing Meta API token
- Google Drive files are privately shared (you control permissions)
- Local downloads are automatically cleaned up
- All credentials stored securely

## 📈 Benefits

1. **Easy Access**: Direct download links instead of Facebook redirects
2. **Organization**: Videos organized in Google Drive with clear names
3. **Backup**: Your ads are safely stored in your Google Drive
4. **Scalable**: Script can handle new ads as you create them
5. **Professional**: Clean filenames and organized structure

## 🎯 Next Steps

1. Follow the setup instructions
2. Run the script on your current 22 ads
3. Use the Google Drive links for easy access
4. Run periodically to update with new ads

Your video ads will be much more accessible and organized! 🎬 
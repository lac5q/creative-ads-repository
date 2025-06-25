# Google Flow to Airtable Data Extraction Guide
**Creation Date: January 18, 2025**
**Version: 1.0**
**Data Source**: Google Flow Project & Existing TurnedYellow/MakeMeJedi Format

## Overview
This guide provides step-by-step instructions for extracting video content from your Google Flow project and formatting it for Airtable import, matching your existing creative ads database structure.

## Required Data Fields (Based on Your Current Format)

### Core Identification Fields
- **Ad_ID**: Unique identifier (generate sequential numbers)
- **Ad_Name**: Descriptive name from Flow project
- **Account**: "GoogleFlow" or specific account name
- **Campaign**: Campaign category (e.g., "Flow Generated Content")
- **Creative_ID**: Unique creative identifier
- **Status**: "ACTIVE", "PAUSED", or "PENDING_REVIEW"

### Performance Fields (To Be Updated Later)
- **Performance_Rating**: "PENDING_ANALYSIS"
- **CPA**: "TBD"
- **CVR**: "TBD" 
- **CTR**: "TBD"
- **Spend**: "0.00"
- **Purchases**: "0"
- **Video_Views**: "0"
- **Hook_Rate**: "TBD"

### Media Links
- **Facebook_Preview_Link**: "TBD"
- **Meta_Video_URL**: Google Flow video URL
- **Google_Drive_Download_Link**: "TBD"
- **Google_Drive_View_Link**: "TBD"

### Creative Classification
- **Creative_Type**: Based on content analysis
- **Hook_Type**: Based on opening/prompt style
- **Targeting**: "Broad", "Interest", "Lookalike", or "Retargeting"

### Priority & Notes
- **Priority**: "🔍 NEEDS_REVIEW" (for new content)
- **Notes**: Flow prompt + generation details
- **Download_Command**: Generated based on video URL

## Step-by-Step Extraction Process

### Step 1: Access Your Google Flow Project
1. Navigate to: https://labs.google/fx/tools/flow/project/d5f9174f-135c-4f22-a798-a3accef74275
2. Ensure you're logged into your Google account
3. Wait for the project to fully load

### Step 2: Extract Video Information
For each video in your Flow project, collect:

1. **Video Title/Name**
2. **Original Prompt Used**
3. **Video URL** (if available for download)
4. **Generation Settings**
5. **Video Duration**
6. **Creation Date**

### Step 3: Analyze Creative Types
Based on your existing data patterns, classify each video:

#### Creative Types
- **Influencer Testimonial**: Personal recommendations
- **Lifestyle**: Daily life scenarios
- **Product Demo**: Showing product features
- **Reaction Video**: Response/reaction content
- **Process Demo**: How-to content
- **Transformation**: Before/after content
- **Celebrity**: Celebrity comparisons
- **Star Wars**: (for MakeMeJedi content)

#### Hook Types
- **Authority Hook**: Expert/credible source
- **Gifting/Emotional**: Emotional appeal
- **Problem/Solution**: Addressing pain points
- **Reaction Hook**: Surprise/reaction based
- **Royal Theme**: Luxury/premium positioning
- **Custom Hook**: Personalization focus
- **How-To**: Educational approach
- **Family**: Family-focused content
- **Before/After**: Transformation focus
- **Celebrity Comp**: Celebrity comparison

### Step 4: Generate CSV Format
Use this template for each video:

```csv
Ad_ID,Ad_Name,Account,Campaign,Creative_ID,Status,Performance_Rating,CPA,CVR,CTR,Spend,Purchases,Video_Views,Hook_Rate,Facebook_Preview_Link,Meta_Video_URL,Google_Drive_Download_Link,Google_Drive_View_Link,Creative_Type,Hook_Type,Targeting,Priority,Notes,Download_Command
```

### Example Entry:
```csv
300001000000001,"video: Flow Generated / [Your Video Name]",GoogleFlow,Flow Generated Content,300001000000001,ACTIVE,PENDING_ANALYSIS,TBD,TBD,TBD,0.00,0,0,TBD,TBD,[FLOW_VIDEO_URL],TBD,TBD,[CREATIVE_TYPE],[HOOK_TYPE],Broad,🔍 NEEDS_REVIEW,"Original Prompt: [YOUR_PROMPT] | Generated: 2025-01-18 | Settings: [GENERATION_SETTINGS]","[DOWNLOAD_COMMAND_IF_AVAILABLE]"
```

## Data Collection Template

### Video 1:
- **Name**: _____________________
- **Prompt**: _____________________
- **URL**: _____________________
- **Creative Type**: _____________________
- **Hook Type**: _____________________
- **Duration**: _____________________
- **Notes**: _____________________

### Video 2:
- **Name**: _____________________
- **Prompt**: _____________________
- **URL**: _____________________
- **Creative Type**: _____________________
- **Hook Type**: _____________________
- **Duration**: _____________________
- **Notes**: _____________________

[Continue for all videos...]

## Automated Approaches (If Possible)

### Browser Automation Option
If the Flow interface allows, you could use browser automation tools to:
1. Screenshot each video card
2. Extract text from prompts
3. Copy video URLs
4. Export data programmatically

### Google Sheets Import Process
Once you have the data:
1. Create a new Google Sheet
2. Import the CSV format
3. Share with your reviewer
4. Use the existing format validation

## Next Steps After Data Collection

1. **Review & Validate**: Check all extracted data
2. **Performance Tracking Setup**: Prepare for future performance data
3. **Campaign Integration**: Plan how to integrate with existing campaigns
4. **Airtable Upload**: Import to your existing Airtable base

## Integration with Existing Data

### Matching Your Current Structure
Your existing data shows:
- **TurnedYellow**: IDs starting with 120xxx
- **MakeMeJedi**: IDs starting with 295xxx
- **GoogleFlow**: Suggest IDs starting with 300xxx

### Performance Rating System
- 🏆 SCALE NOW: CVR > 6%
- 🥇 SCALE IMMEDIATELY: CVR > 10%
- 🥈 SCALE EXCELLENT: CVR 5-10%
- ✅ GOOD: CVR 3-5%
- 🔄 AVERAGE/OPTIMIZE: CVR 2-3%
- ❌ POOR/PAUSE: CVR < 2%

## Support & Tools

### Manual Data Entry Template
If you need to manually enter the data, I can create a Google Sheets template that matches your existing format exactly.

### CSV Generation Script
I can also create a script to help format your collected data into the proper CSV structure for Airtable import.

---

**Next Action**: Please manually collect the video information from your Flow project using this guide, then I can help you format it properly for Airtable import. 
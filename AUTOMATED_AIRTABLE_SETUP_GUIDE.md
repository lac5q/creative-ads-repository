# 🚀 Automated Airtable Upload Setup Guide
**Created: 2025-06-24**

## Overview
This guide will help you automatically upload your creative ads data to Airtable using the `automated_airtable_uploader.py` script instead of manual CSV import.

## Prerequisites
- Python 3.7+ installed
- `requests` library (`pip install requests`)
- Airtable account with a workspace/base

## Step 1: Get Your Airtable Credentials

### 1.1 Get Personal Access Token (API Key)
1. Go to https://airtable.com/create/tokens
2. Click "Create new token"
3. Give it a name like "Creative Ads Uploader"
4. Add these scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
5. Add access to your specific base
6. Click "Create token"
7. **Copy and save the token** (you won't see it again!)

### 1.2 Get Your Base ID
1. Go to your Airtable base
2. Look at the URL: `https://airtable.com/app1234567890abcde/...`
3. The Base ID is the part that starts with `app` (e.g., `app1234567890abcde`)

## Step 2: Configure the Script

### Option A: Environment Variables (Recommended)
```bash
export AIRTABLE_API_KEY="your_personal_access_token_here"
export AIRTABLE_BASE_ID="your_base_id_here"
export AIRTABLE_TABLE_NAME="Creative Ads Performance"
```

### Option B: Configuration File
1. Run the script once to create a sample config:
   ```bash
   python automated_airtable_uploader.py
   ```
2. This creates `airtable_config_sample.json`
3. Rename it to `airtable_config.json`
4. Fill in your credentials:
   ```json
   {
     "api_key": "your_personal_access_token_here",
     "base_id": "your_base_id_here", 
     "table_name": "Creative Ads Performance"
   }
   ```

## Step 3: Prepare Your Airtable Base

### 3.1 Create the Table
1. In your Airtable base, create a new table called "Creative Ads Performance"
2. The script will show you exactly which fields to create when you run it

### 3.2 Required Fields
The script will display these required fields:
- `Ad_Name`: Single line text
- `Platform`: Single select (TurnedYellow, MakeMeJedi)
- `Campaign_Name`: Single line text
- `CVR_Percent`: Number (2 decimal places)
- `CTR_Percent`: Number (2 decimal places)
- `CPC_USD`: Currency ($)
- `CPA_USD`: Currency ($)
- `Total_Spend_USD`: Currency ($)
- `Total_Conversions`: Number
- `Total_Impressions`: Number
- `Total_Clicks`: Number
- `Hook_Category`: Single select
- `Creative_Type`: Single select
- `Campaign_Season`: Single select
- `Performance_Tier`: Single select
- `Priority_Score`: Number (0 decimal places)
- `Priority_Action`: Single line text
- `Budget_Scaling_Potential`: Single select
- `TikTok_Potential_Score`: Number (0 decimal places)
- `TikTok_Potential_Reason`: Long text
- `Google_Ads_Potential_Score`: Number (0 decimal places)
- `Google_Ads_Potential_Reason`: Long text
- `Cross_Platform_Score`: Number (1 decimal place)
- `Cross_Platform_Notes`: Long text
- `Facebook_Preview_URL`: URL
- `GitHub_Download_URL`: URL
- `Download_Command`: Long text
- `Has_Facebook_Preview`: Checkbox
- `Has_GitHub_URL`: Checkbox

## Step 4: Run the Automated Upload

### 4.1 Basic Upload
```bash
python automated_airtable_uploader.py
```

### 4.2 What the Script Does
1. **Tests Connection**: Verifies your API credentials work
2. **Shows Field Requirements**: Lists all fields you need in Airtable
3. **Asks for Confirmation**: You can review before uploading
4. **Optional Data Clearing**: Can clear existing data first
5. **Batch Upload**: Uploads data in small batches (rate limit friendly)
6. **Progress Tracking**: Shows upload progress in real-time

### 4.3 Sample Output
```
🚀 Automated Airtable Creative Ads Uploader
==================================================
✅ Successfully connected to Airtable

📋 Required Table Structure:
- Ad_Name: singleLineText
- Platform: singleSelect
- Campaign_Name: singleLineText
...

📂 Ready to upload: Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv
📊 Target: app1234567890abcde/Creative Ads Performance

🤔 Do you want to proceed with upload? (y/N): y
🗑️  Clear existing table data first? (y/N): n

✅ Uploaded batch 1: 10 records
✅ Uploaded batch 2: 10 records

🎉 Successfully uploaded 20 records to Airtable!
📊 Check your Airtable base: https://airtable.com/app1234567890abcde
```

## Step 5: Verify Upload

1. Go to your Airtable base
2. Check the "Creative Ads Performance" table
3. Verify all 20 records are there with proper data
4. Check that numeric fields show as numbers (not text)
5. Verify currency fields show with $ symbols
6. Check that URLs are clickable

## Advanced Features

### Clearing Existing Data
- The script can optionally clear existing table data before upload
- Use this if you want to replace all data rather than append
- **Warning**: This permanently deletes existing records

### Error Handling
- The script includes comprehensive error handling
- Failed uploads will show detailed error messages
- Rate limiting prevents API quota issues
- Connection testing ensures credentials work before upload

### Batch Processing
- Data is uploaded in batches of 10 records (Airtable limit)
- Includes delays between batches to respect rate limits
- Progress tracking shows which batches succeed/fail

## Troubleshooting

### Common Issues

**"Connection failed: 401"**
- Your API token is invalid or expired
- Check that you copied the full token
- Verify the token has the right scopes

**"Connection failed: 404"** 
- Your Base ID is incorrect
- Check the URL format: should start with "app"
- Verify you have access to the base

**"Upload failed: 422"**
- Field names don't match between CSV and Airtable
- Create all required fields in Airtable first
- Check field types match (number vs text, etc.)

**"CSV file not found"**
- Make sure `Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv` exists
- Run the script from the correct directory

### Getting Help
1. Check the console output for specific error messages
2. Verify your Airtable table has all required fields
3. Test your API credentials with a simple Airtable API call
4. Check Airtable's API documentation for field type requirements

## Security Notes

- Never commit your API token to version control
- Use environment variables in production
- Your API token has the same permissions as your Airtable account
- Consider creating a dedicated Airtable account for API access

## Why Use Automation vs Manual Import?

### Automation Advantages ✅
- **One-click upload**: Run script and data appears in Airtable
- **Data validation**: Automatic type conversion and error checking  
- **Batch processing**: Handles large datasets efficiently
- **Rate limiting**: Respects API limits automatically
- **Error recovery**: Detailed error messages for troubleshooting
- **Repeatable**: Easy to re-run with updated data
- **Integration ready**: Can be scheduled or triggered automatically

### Manual Import Limitations ❌
- Multi-step process (download CSV, import, map fields)
- Field mapping required every time
- No automatic data validation
- Harder to troubleshoot import issues
- Can't easily automate or schedule
- Risk of human error in field mapping

## Conclusion

The automated uploader provides a much more efficient and reliable way to get your creative ads data into Airtable. Once set up, it's a single command to upload fresh data whenever you need it!

---
**Document Version**: 1.0  
**Created**: 2025-06-24  
**Data Source**: Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv  
**Target**: Airtable Creative Ads Performance Table 
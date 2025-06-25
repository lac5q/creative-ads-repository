# How to Use Meta Ads MCP Server

**Created: June 21, 2025**

## 🚀 Quick Start Guide

Your Meta Ads MCP server is now **installed and configured** in both:
- ✅ `claude_desktop_config.json` (Claude Desktop)
- ✅ `mcp.json` (Global MCP configuration)

## 🔧 Configuration Status

### ✅ What's Already Configured
- **Meta App ID**: `1237417401126987`
- **Meta App Secret**: `014087a6999b22626af83baa2cba4b41`
- **Server Path**: `./meta-ads-mcp-server/src/mcp_server.py`
- **MCP Framework**: FastMCP v2.8.1

### ⚠️ What You Still Need to Do

**1. Get Your Meta Access Token**

You need to get a Meta Access Token to complete the setup:

1. **Go to Meta for Developers**: https://developers.facebook.com/apps/
2. **Select your app** (ID: 1237417401126987)
3. **Navigate to**: Tools → Graph API Explorer
4. **Generate a User Access Token** with these permissions:
   - `ads_management` (manage ads)
   - `ads_read` (read ads data)
   - `business_management` (access business accounts)
   - `pages_read_engagement` (read page data)

**2. Update Your Access Token**

Replace `your_meta_access_token_here` in both files:

```bash
# Update the .env file
cd /Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server
nano .env
# Change: META_ACCESS_TOKEN=your_actual_access_token_here

# Update the mcp.json file  
cd /Users/lcalderon/Documents/GitHub/Marketing
nano mcp.json
# Find the meta-ads-api section and update META_ACCESS_TOKEN
```

## 🎯 How to Use the Server

### Option 1: With Claude Desktop

1. **Restart Claude Desktop** (to load the new MCP server)
2. **Start a new conversation**
3. **Use Meta Ads tools directly in chat**:

```
Can you show me my Meta Ads campaigns?
```

```
Get insights for my top performing Meta ads from last month
```

```
Create a new Meta Ads campaign for my summer promotion
```

### Option 2: With MCP Client Tools

If you're using other MCP clients, the server is available at:
```
./meta-ads-mcp-server/src/mcp_server.py
```

## 🛠️ Available MCP Tools

### 📊 Account & Campaign Management

```bash
# Get your ad accounts
mcp_meta-ads_get_ad_accounts

# Get campaigns
mcp_meta-ads_get_campaigns

# Get campaign details
mcp_meta-ads_get_campaign_details --campaign_id="YOUR_CAMPAIGN_ID"

# Create a new campaign
mcp_meta-ads_create_campaign --account_id="act_XXXXXXXXX" --name="Summer Sale 2025" --objective="CONVERSIONS"
```

### 🎯 Ad Set Management

```bash
# Get ad sets
mcp_meta-ads_get_adsets --account_id="act_XXXXXXXXX"

# Create new ad set
mcp_meta-ads_create_adset --account_id="act_XXXXXXXXX" --campaign_id="CAMPAIGN_ID" --name="Summer Targeting"
```

### 📱 Ad Management

```bash
# Get ads
mcp_meta-ads_get_ads --account_id="act_XXXXXXXXX"

# Get ad creatives
mcp_meta-ads_get_ad_creatives --ad_id="AD_ID"

# Upload ad image
mcp_meta-ads_upload_ad_image --account_id="act_XXXXXXXXX" --image_path="/path/to/image.jpg"
```

### 📈 Analytics & Insights

```bash
# Get performance insights
mcp_meta-ads_get_insights --object_id="CAMPAIGN_ID" --time_range="last_30d"

# Search Facebook Ads Library
mcp_meta-ads_search_ads_archive --search_terms="summer sale" --ad_reached_countries=["US"]
```

## 💬 Example Claude Desktop Conversations

### Get Campaign Performance
```
"Show me the performance of my Meta Ads campaigns from the last 30 days with spend, impressions, and CTR"
```

### Create New Campaign
```
"Help me create a new Meta Ads campaign for promoting my new product launch. I want to target users interested in fitness and healthy living."
```

### Analyze Competitor Ads
```
"Search the Facebook Ads Library for ads from Nike that mention 'running shoes' and show me what creative approaches they're using"
```

### Upload and Create Ad Creative
```
"I have an image at /Users/lcalderon/Desktop/product-image.jpg. Upload it to Meta Ads and create a new ad creative with the headline 'Summer Sale - 50% Off'"
```

## 🔍 Testing Your Setup

### 1. **Test Server Installation**
```bash
cd /Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server
python test_server.py
```

**Expected Output**: ✅ All tests passed (3/3)

### 2. **Test Server Startup**
```bash
python src/mcp_server.py
```

**Expected Output**: Server starts and shows "Starting Meta Ads MCP server..."

### 3. **Test with Claude Desktop**
1. Restart Claude Desktop
2. Start new conversation
3. Ask: "What Meta Ads tools do you have available?"
4. You should see 30+ Meta Ads MCP tools listed

## 🚨 Troubleshooting

### Common Issues

**1. "Access Token Invalid" Error**
- **Solution**: Generate a new access token from Meta for Developers
- **Check**: Token has correct permissions (ads_management, ads_read)

**2. "Server Not Found" Error**
- **Solution**: Restart Claude Desktop to reload MCP configuration
- **Check**: Path in mcp.json is correct: `./meta-ads-mcp-server/src/mcp_server.py`

**3. "Import Error" Error**
- **Solution**: Ensure all dependencies are installed
- **Run**: `pip install -r requirements.txt` in the meta-ads-mcp-server directory

**4. "Permission Denied" Error**
- **Solution**: Check that your Meta App has the necessary permissions
- **Verify**: App is approved for ads management in Meta for Developers

### Debug Commands

```bash
# Check if server can start
cd /Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server
python src/mcp_server.py --help

# Check environment variables
cat .env

# Verify MCP configuration
cd /Users/lcalderon/Documents/GitHub/Marketing
cat mcp.json | grep -A 10 "meta-ads-api"
```

## 📋 Quick Reference

### File Locations
- **Server Code**: `/Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server/src/mcp_server.py`
- **Environment**: `/Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server/.env`
- **Global Config**: `/Users/lcalderon/Documents/GitHub/Marketing/mcp.json`
- **Claude Config**: `/Users/lcalderon/Documents/GitHub/Marketing/claude_desktop_config.json`

### Key Credentials
- **App ID**: `1237417401126987`
- **App Secret**: `014087a6999b22626af83baa2cba4b41`
- **Access Token**: `your_meta_access_token_here` ⚠️ **NEEDS TO BE SET**

### Next Steps
1. ✅ Server installed and configured
2. ⚠️ **Get Meta Access Token** (required)
3. ⚠️ **Update access token in config files**
4. ✅ Restart Claude Desktop
5. ✅ Start using Meta Ads tools!

---

**Need help?** Check the `INSTALLATION_SUMMARY.md` for detailed technical information or `README.md` for complete API documentation. 
# Meta Ads MCP Server - Cursor Installation

**Created: June 21, 2025**  
**Status: ✅ Successfully Installed in Cursor**

## 🎉 Installation Complete!

The Meta Ads API MCP server has been successfully added to **Cursor's global MCP configuration**!

## 📍 **Installation Location**

**File**: `~/.cursor/mcp.json`  
**Server Name**: `meta-ads-api-full`  
**Backup Created**: `~/.cursor/mcp-backup-YYYYMMDD-HHMMSS.json`

## ✅ **Configuration Added**

```json
"meta-ads-api-full": {
    "command": "python",
    "args": [
        "/Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server/src/mcp_server.py"
    ],
    "env": {
        "META_APP_ID": "1237417401126987",
        "META_APP_SECRET": "014087a6999b22626af83baa2cba4b41",
        "META_ACCESS_TOKEN": "your_meta_access_token_here",
        "META_API_VERSION": "v22.0",
        "LOG_LEVEL": "INFO"
    }
}
```

## 🔧 **Your Complete Cursor MCP Setup**

Cursor now has **15 MCP servers** configured, including:

### **Advertising & Marketing**
- ✅ `meta-ads` - Existing Meta Ads server
- ✅ `meta-ads-old` - Legacy Meta Ads server  
- ✅ **`meta-ads-api-full`** - **Your new comprehensive Meta Ads API server**
- ✅ `google-ads-turnedyellow` - Google Analytics (TurnedYellow)
- ✅ `google-ads-makemejedi` - Google Analytics (MakeMeJedi)

### **E-commerce**
- ✅ `shopify-turnedyellow` - Shopify (TurnedYellow)
- ✅ `shopify-makemejedi` - Shopify (MakeMeJedi)

### **Data & Research**
- ✅ `dataforseo` - SEO data
- ✅ `firecrawl` - Web scraping
- ✅ `perplexity` - AI search

### **Productivity & Tools**
- ✅ `slack` - Slack integration
- ✅ `google-drive` - Google Drive
- ✅ `zapier` - Automation
- ✅ `quickchart` - Chart generation
- ✅ `MCP_DOCKER` - Docker integration

## 🚀 **How to Use in Cursor**

### **1. Restart Cursor**
Close and reopen Cursor to load the new MCP server configuration.

### **2. Access MCP Tools**
In Cursor, you can now use Meta Ads tools through:
- **AI Chat**: Ask Cursor to use Meta Ads functions
- **Command Palette**: Access MCP commands
- **Code Generation**: Generate Meta Ads API code

### **3. Example Usage in Cursor**

**AI Chat Examples:**
```
"Use the Meta Ads API to show me my campaign performance"
```

```
"Generate code to create a new Meta Ads campaign"
```

```
"Help me analyze my Meta Ads data using the MCP server"
```

## 🛠️ **Available Tools (30+ MCP Tools)**

Your `meta-ads-api-full` server provides comprehensive Meta Ads functionality:

### **Account Management**
- `mcp_meta-ads_get_ad_accounts`
- `mcp_meta-ads_get_account_info`

### **Campaign Management**
- `mcp_meta-ads_get_campaigns`
- `mcp_meta-ads_create_campaign`
- `mcp_meta-ads_update_campaign`
- `mcp_meta-ads_get_campaign_details`

### **Ad Set Management**
- `mcp_meta-ads_get_adsets`
- `mcp_meta-ads_create_adset`
- `mcp_meta-ads_update_adset`
- `mcp_meta-ads_get_adset_details`

### **Ad Management**
- `mcp_meta-ads_get_ads`
- `mcp_meta-ads_create_ad`
- `mcp_meta-ads_update_ad`
- `mcp_meta-ads_get_ad_details`

### **Creative Management**
- `mcp_meta-ads_upload_ad_image`
- `mcp_meta-ads_create_ad_creative`
- `mcp_meta-ads_get_ad_creatives`
- `mcp_meta-ads_get_ad_image`

### **Analytics & Insights**
- `mcp_meta-ads_get_insights`
- `mcp_meta-ads_search_ads_archive`

## ⚠️ **Next Steps Required**

### **1. Get Meta Access Token**
You need to obtain a Meta Access Token:

1. Go to: https://developers.facebook.com/apps/1237417401126987/
2. Navigate to: Tools → Graph API Explorer
3. Generate a User Access Token with permissions:
   - `ads_management`
   - `ads_read`
   - `business_management`
   - `pages_read_engagement`

### **2. Update Access Token in Cursor Config**
```bash
# Edit Cursor's MCP configuration
nano ~/.cursor/mcp.json

# Find "meta-ads-api-full" section and replace:
"META_ACCESS_TOKEN": "your_actual_access_token_here"
```

### **3. Restart Cursor**
After updating the access token, restart Cursor to apply the changes.

## 🧪 **Testing Your Setup**

### **1. Test Server Installation**
```bash
cd /Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server
python test_server.py
```

### **2. Test in Cursor**
1. Restart Cursor
2. Open AI chat
3. Ask: "What Meta Ads MCP tools are available?"
4. You should see the meta-ads-api-full server tools

### **3. Verify Configuration**
```bash
# Check Cursor MCP config
cat ~/.cursor/mcp.json | grep -A 12 "meta-ads-api-full"
```

## 🔍 **Differences Between Meta Ads Servers**

You now have **3 Meta Ads servers** in Cursor:

| Server | Purpose | Features |
|--------|---------|----------|
| `meta-ads` | NPM package | Basic Meta Ads functionality |
| `meta-ads-old` | Legacy server | Pipeboard-based integration |
| **`meta-ads-api-full`** | **Your new server** | **Complete Meta Ads API access** |

**Recommendation**: Use `meta-ads-api-full` for comprehensive Meta Ads management.

## 🚨 **Troubleshooting**

### **"Server Not Found" Error**
- **Solution**: Restart Cursor to reload MCP configuration
- **Check**: Verify path in config is correct

### **"Access Token Invalid" Error**
- **Solution**: Generate new access token from Meta for Developers
- **Update**: Replace token in `~/.cursor/mcp.json`

### **"Import Error" Error**
- **Solution**: Ensure dependencies are installed
- **Run**: `pip install -r requirements.txt` in meta-ads-mcp-server directory

### **Restore Previous Configuration**
If needed, restore from backup:
```bash
# List available backups
ls ~/.cursor/mcp-backup-*.json

# Restore from backup
cp ~/.cursor/mcp-backup-YYYYMMDD-HHMMSS.json ~/.cursor/mcp.json
```

## 📋 **File Locations**

- **Cursor MCP Config**: `~/.cursor/mcp.json`
- **Server Code**: `/Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server/src/mcp_server.py`
- **Environment File**: `/Users/lcalderon/Documents/GitHub/Marketing/meta-ads-mcp-server/.env`
- **Configuration Backups**: `~/.cursor/mcp-backup-*.json`

## 🎯 **Success Criteria**

- [x] ✅ Added to Cursor's MCP configuration
- [x] ✅ Configuration backup created
- [x] ✅ Server path correctly configured
- [x] ✅ Environment variables set
- [ ] ⚠️ **Meta Access Token needed**
- [ ] ⚠️ **Restart Cursor required**

## 🏆 **What's Next**

1. **Get your Meta Access Token**
2. **Update the token in `~/.cursor/mcp.json`**
3. **Restart Cursor**
4. **Start using Meta Ads tools in Cursor!**

---

**Installation completed successfully on June 21, 2025** 🎉

**Your Meta Ads MCP server is now available in Cursor as `meta-ads-api-full`!** 
# Meta Ads MCP Server - Complete Setup Guide

This guide will walk you through getting all the required login parameters for the Meta Ads MCP Server.

## 📋 Required Parameters Checklist

Before starting, you'll need to obtain these parameters:

- [ ] `META_ACCESS_TOKEN` - Your Meta API Access Token
- [ ] `META_APP_ID` - Your Facebook App ID
- [ ] `META_APP_SECRET` - Your Facebook App Secret
- [ ] `META_DEFAULT_ACCOUNT_ID` - Your Ad Account ID (optional)

## 🚀 Step-by-Step Setup

### Step 1: Create a Facebook App

1. **Go to Facebook Developers**
   - Visit: https://developers.facebook.com/
   - Click "My Apps" → "Create App"

2. **Choose App Type**
   - Select "Business" for advertising use
   - Fill in app details (name, contact email)

3. **Get App ID and App Secret**
   - Go to "App Settings" → "Basic"
   - Copy your **App ID** (`META_APP_ID`)
   - Click "Show" for **App Secret** and copy it (`META_APP_SECRET`)

### Step 2: Configure App Permissions

1. **Add Facebook Login Product**
   - In your app dashboard, click "+ Add Product"
   - Select "Facebook Login" → "Set Up"

2. **Add Marketing API Product**
   - Click "+ Add Product"
   - Select "Marketing API" → "Set Up"

3. **Request Permissions**
   - Go to "App Review" → "Permissions and Features"
   - Request these permissions:
     - `ads_read` - Read ad data
     - `ads_management` - Manage ads
     - `read_insights` - Get performance data
     - `business_management` - Business Manager access (if needed)

### Step 3: Generate Access Token

#### Option A: Using Graph API Explorer (Easiest)

1. **Go to Graph API Explorer**
   - Visit: https://developers.facebook.com/tools/explorer/

2. **Configure Explorer**
   - Select your app from dropdown
   - Click "Generate Access Token"
   - Select required permissions:
     - `ads_read`
     - `ads_management` 
     - `read_insights`

3. **Get Long-lived Token**
   - Copy the short-lived token
   - Use the Access Token Debugger to extend it
   - Visit: https://developers.facebook.com/tools/debug/accesstoken/

#### Option B: Using App Dashboard

1. **Go to Marketing API**
   - In your app, go to "Marketing API" → "Tools"
   - Click "Get Token"

2. **Select Ad Account**
   - Choose the ad account you want to access
   - Grant permissions

### Step 4: Get Ad Account ID

1. **Using Meta Business Manager**
   - Go to: https://business.facebook.com/
   - Click "Business Settings" → "Accounts" → "Ad Accounts"
   - Copy your account ID (format: `123456789`)
   - Add `act_` prefix (final format: `act_123456789`)

2. **Using Graph API Explorer**
   - In Graph API Explorer, use endpoint: `/me/adaccounts`
   - Run query to see all accessible accounts

### Step 5: Configure Environment

1. **Copy Environment Template**
   ```bash
   cd meta-ads-mcp-server
   cp env.template .env
   ```

2. **Fill in Your Values**
   ```env
   META_ACCESS_TOKEN=EAABxxxxxxxxxxxxxxxxx  # Your long-lived token
   META_APP_ID=1234567890123456           # Your app ID
   META_APP_SECRET=abcdef1234567890       # Your app secret
   META_DEFAULT_ACCOUNT_ID=act_1234567890 # Your ad account ID
   ```

3. **Update Claude Desktop Config**
   ```json
   {
     "mcpServers": {
       "meta-ads-api": {
         "command": "python",
         "args": ["./meta-ads-mcp-server/src/mcp_server.py"],
         "env": {
           "META_ACCESS_TOKEN": "your_actual_token_here",
           "META_APP_ID": "your_actual_app_id",
           "META_APP_SECRET": "your_actual_app_secret",
           "META_DEFAULT_ACCOUNT_ID": "act_XXXXXXXXX"
         }
       }
     }
   }
   ```

## 🔧 Testing Your Setup

### Test Connection
```bash
cd meta-ads-mcp-server
python src/mcp_server.py --test
```

### Verify Access
```python
# Test basic connectivity
from src.meta_ads_client import MetaAdsClient

client = MetaAdsClient()
accounts = await client.get_ad_accounts()
print(f"Found {len(accounts)} accounts")
```

## 🔒 Security Best Practices

### Access Token Security
- ✅ Use long-lived tokens (60 days)
- ✅ Store tokens securely (environment variables)
- ✅ Regenerate tokens regularly
- ❌ Never commit tokens to code repositories

### App Configuration
- ✅ Add your domain to "Valid OAuth Redirect URIs"
- ✅ Enable "App Secret Proof" for additional security
- ✅ Use System User tokens for production

### Business Manager Setup
For production applications, consider using Business Manager:
1. Create System User in Business Manager
2. Assign ad account permissions to System User
3. Generate System User Access Token
4. Use `META_SYSTEM_USER_TOKEN` instead of `META_ACCESS_TOKEN`

## ⚠️ Common Issues & Solutions

### Issue: "Invalid App ID or App Secret"
**Solution:** Double-check your App ID and Secret from Facebook App Dashboard

### Issue: "Insufficient Permissions"
**Solution:** 
- Request additional permissions in App Review
- Ensure your access token has the required scopes

### Issue: "Ad Account Access Denied"
**Solution:**
- Verify you have admin access to the ad account
- Add your app to the ad account's authorized apps

### Issue: "Token Expired"
**Solution:**
- Refresh your access token
- Use long-lived tokens (valid for 60 days)

### Issue: "Rate Limit Exceeded"
**Solution:**
- The server has built-in rate limiting handling
- Reduce request frequency if needed

## 📞 Getting Help

### Facebook Developer Resources
- [Marketing API Documentation](https://developers.facebook.com/docs/marketing-api/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

### Test Your Tokens
Use these endpoints to verify your setup:
- Test App: `https://graph.facebook.com/{app-id}?access_token={access-token}`
- Test Account: `https://graph.facebook.com/me/adaccounts?access_token={access-token}`
- Test Permissions: `https://graph.facebook.com/me/permissions?access_token={access-token}`

## 🎯 Quick Start Checklist

After setup, verify these work:

- [ ] Server starts without errors
- [ ] Can fetch ad accounts
- [ ] Can get campaign data
- [ ] Can retrieve insights
- [ ] Claude Desktop recognizes the server

Once all steps are complete, restart Claude Desktop and you should see the Meta Ads tools available! 
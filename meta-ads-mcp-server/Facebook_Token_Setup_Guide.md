# Facebook Access Token Setup for Ad Video Downloads
**Created:** June 21, 2025  
**Issue:** Missing permissions to access ad accounts and download video creatives

## 🚨 Current Problem

Your token test results show:
- ✅ **User Info:** PASS (Basic access works)
- ❌ **Ad Accounts:** FAIL (Missing permissions #200)
- ❌ **Business Accounts:** FAIL (Missing permissions #100)

## 🔧 Solution: Grant Required Permissions

### **Method 1: Facebook Graph API Explorer (Quick Fix)**

**Step 1:** Go to Graph API Explorer
- URL: https://developers.facebook.com/tools/explorer/

**Step 2:** Select Your App
- If you don't have an app, click "Create App" first
- Choose "Consumer" or "Business" type

**Step 3:** Get User Access Token
- Click **"Get Token"** → **"Get User Access Token"**
- Check these permissions:
  ```
  ✅ ads_read               (Read ad account data)
  ✅ ads_management         (Full ad account access)
  ✅ business_management    (Access business assets)
  ✅ read_insights          (Performance metrics)
  ✅ pages_read_engagement  (Page content)
  ```

**Step 4:** Generate and Test
- Click **"Generate Access Token"**
- Copy the new token
- Test it: `python test_token_permissions.py NEW_TOKEN_HERE`

### **Method 2: Meta Business Suite (Recommended for Production)**

**Step 1:** Access Business Settings
- Go to: https://business.facebook.com/settings/system-users
- Must be Business Manager Admin

**Step 2:** Create System User
- Click **"Add"** → **"System User"**
- Name: "API Video Downloads"
- Role: **"Admin"** (required for full access)

**Step 3:** Assign Assets
- **Ad Accounts:** Assign all your ad accounts (TurnedYellow, MakeMeJedi)
- **Pages:** Assign associated Facebook pages
- **Apps:** Assign your Facebook app

**Step 4:** Generate Access Token
- Click **"Generate New Token"**
- Select your app
- Choose permissions:
  ```
  ✅ ads_read
  ✅ ads_management
  ✅ business_management
  ✅ read_insights
  ```
- Set expiration: **"Never"** (for long-lived token)

**Step 5:** Save Token Securely**
- Copy the token immediately (only shown once)
- Update your `.env` file
- Test with permission script

### **Method 3: Facebook App Development Console**

**If you need to create/modify a Facebook App:**

**Step 1:** Create Facebook App
- Go to: https://developers.facebook.com/apps/
- Click **"Create App"**
- Choose **"Consumer"** or **"Business"**
- App Name: "TurnedYellow Video Downloader"

**Step 2:** Add Products
- **Facebook Login:** Required for user authentication
- **Marketing API:** Required for ads access

**Step 3:** Configure App Settings**
- **App Domains:** Add your domain if applicable
- **Privacy Policy URL:** Required for review
- **Terms of Service URL:** Required for review

**Step 4:** Request Advanced Permissions**
- Go to **"App Review"** → **"Permissions and Features"**
- Request these permissions:
  ```
  📝 ads_management
  📝 ads_read  
  📝 business_management
  📝 read_insights
  ```

**Step 5:** Verification Process**
- Facebook may require business verification
- Provide business documents if requested
- Explain use case: "Download own ad creatives for analysis"

## 🛠️ **Testing Your New Token**

After getting a new token, test it:

```bash
# Test the new token
python test_token_permissions.py "YOUR_NEW_TOKEN_HERE"

# If successful, update your environment
export META_ACCESS_TOKEN="YOUR_NEW_TOKEN_HERE"

# Test the ad download script
python get_recent_ads.py
```

## 🎯 **Expected Results After Fix**

When permissions are correctly set, you should see:

```
🔍 Testing Facebook Access Token Permissions...

Testing: User Info (Basic API access)
✅ SUCCESS: User Info
   User: Luis Abraham Calderon

Testing: Ad Accounts (Reading ad account data)  
✅ SUCCESS: Ad Accounts
   Found 8 items
   Example: USD Turned Yellow

Testing: Business Accounts (Business management access)
✅ SUCCESS: Business Accounts
   Found 2 items
   Example: TurnedYellow Business

==================================================
📊 PERMISSION TEST SUMMARY
==================================================
Tests Passed: 3/3
🎉 ALL TESTS PASSED! Your token has the required permissions.

✅ You can now proceed with downloading ad videos!
```

## 🔒 **Security Best Practices**

### **Token Management:**
- **Never commit tokens to git** (use .env files)
- **Use long-lived tokens** for production
- **Rotate tokens** every 90 days
- **Monitor token usage** in Facebook Developer Console

### **Permission Principle:**
- **Request minimum required permissions**
- **Use ads_read for read-only access**
- **Only use ads_management if you need to modify ads**

### **Environment Variables:**
```bash
# Add to .env file (not committed to git)
META_ACCESS_TOKEN=your_new_token_here
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
```

## 🚀 **Next Steps After Permission Fix**

1. **Update token** in your configuration
2. **Test with permission script** 
3. **Run video download script** 
4. **Download your top performers:**
   - David Influencer Video (11.11% CVR)
   - Sara Gifting Hook (5.88% CVR)

## 🆘 **Common Issues & Solutions**

### **Issue: "App Not Approved for ads_management"**
**Solution:** 
- Use Graph API Explorer for testing
- Submit app for review with proper use case documentation
- Alternative: Use Business Manager system user

### **Issue: "Token Expired"**
**Solution:**
- Generate long-lived token (60 days)
- Use system user token (never expires)
- Set up automatic token refresh

### **Issue: "Business Verification Required"**
**Solution:**
- Complete Facebook Business Verification
- Provide business documents
- May take 1-2 weeks for approval

### **Issue: "Cannot Access Specific Ad Account"**
**Solution:**
- Ensure you're admin of the ad account
- Check if account is under business manager
- Verify account permissions in Business Settings

## 📞 **Need Help?**

If you encounter issues:
1. **Check Facebook Developer Documentation:** https://developers.facebook.com/docs/marketing-api/
2. **Facebook Developer Support:** https://developers.facebook.com/support/
3. **Business Manager Help:** https://www.facebook.com/business/help/ 
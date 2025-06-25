#!/bin/bash

# Your OAuth credentials
CLIENT_ID="498217939698-hvpan6eue1ibg7smc6s7gu5ds2dibg2o.apps.googleusercontent.com"
CLIENT_SECRET="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"

echo "🚀 Google Ads API Token Generator (Simple Version)"
echo ""
echo "🔗 STEP 1: Open this URL in your browser:"
echo ""
echo "https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https://www.googleapis.com/auth/adwords&prompt=consent&response_type=code&client_id=${CLIENT_ID}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
echo ""
echo "📋 STEP 2: After authorization, copy the code and paste it here:"
read -p "Enter the authorization code: " AUTH_CODE

echo ""
echo "⏳ Getting tokens..."

# Exchange authorization code for tokens
RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "code=${AUTH_CODE}" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob")

# Check if we got a refresh token
REFRESH_TOKEN=$(echo $RESPONSE | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$REFRESH_TOKEN" ]; then
    echo ""
    echo "✅ SUCCESS! Here are your Google Ads API credentials:"
    echo ""
    echo "============================================================"
    echo "GOOGLE_ADS_CLIENT_ID=\"${CLIENT_ID}\""
    echo "GOOGLE_ADS_CLIENT_SECRET=\"${CLIENT_SECRET}\""
    echo "GOOGLE_ADS_REFRESH_TOKEN=\"${REFRESH_TOKEN}\""
    echo "============================================================"
    echo ""
    echo "💾 Save these credentials - you'll need them for your mcp.json file!"
else
    echo ""
    echo "❌ Error getting tokens. Response:"
    echo $RESPONSE
    echo ""
    echo "🔄 Try running the script again and make sure to:"
    echo "   1. Use the authorization code immediately"
    echo "   2. Copy the entire code (it might be long)"
    echo "   3. Don't use the same code twice"
fi 
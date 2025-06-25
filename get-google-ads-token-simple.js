const { google } = require('googleapis');
const readline = require('readline');

// Your OAuth credentials
const CLIENT_ID = '498217939698-hvpan6eue1ibg7smc6s7gu5ds2dibg2o.apps.googleusercontent.com';
const CLIENT_SECRET = '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';

// Create OAuth2 client
const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  'urn:ietf:wg:oauth:2.0:oob'
);

// Google Ads API scope
const SCOPES = ['https://www.googleapis.com/auth/adwords'];

async function getRefreshToken() {
  // Generate the authorization URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent'
  });

  console.log('\n🔗 STEP 1: Open this URL in your browser:');
  console.log('\n' + authUrl + '\n');
  console.log('📋 STEP 2: After authorization, you\'ll see a code. Copy it and paste here:');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve, reject) => {
    rl.question('Enter the authorization code: ', async (code) => {
      try {
        console.log('\n⏳ Getting tokens...');
        
        const { tokens } = await oauth2Client.getToken(code.trim());
        
        console.log('\n✅ SUCCESS! Here are your Google Ads API credentials:');
        console.log('\n' + '='.repeat(60));
        console.log('GOOGLE_ADS_CLIENT_ID="' + CLIENT_ID + '"');
        console.log('GOOGLE_ADS_CLIENT_SECRET="' + CLIENT_SECRET + '"');
        console.log('GOOGLE_ADS_REFRESH_TOKEN="' + tokens.refresh_token + '"');
        console.log('='.repeat(60));
        console.log('\n💾 Save these credentials - you\'ll need them for your mcp.json file!');
        
        resolve(tokens);
      } catch (error) {
        console.error('\n❌ Error getting tokens:', error.message);
        console.log('\n🔄 Try running the script again and make sure to:');
        console.log('   1. Use the authorization code immediately');
        console.log('   2. Copy the entire code (it might be long)');
        console.log('   3. Don\'t use the same code twice');
        reject(error);
      }
      rl.close();
    });
  });
}

console.log('🚀 Google Ads API Token Generator');
console.log('This will help you get the refresh token for your MCP server.\n');

getRefreshToken().catch(console.error); 
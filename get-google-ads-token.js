const { google } = require('googleapis');
const readline = require('readline');

// Replace these with your actual credentials from Step 1
const CLIENT_ID = '498217939698-hvpan6eue1ibg7smc6s7gu5ds2dibg2o.apps.googleusercontent.com';
const CLIENT_SECRET = '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';
const REDIRECT_URI = 'http://localhost'; // For desktop apps

const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI
);

// Google Ads API scope
const SCOPES = ['https://www.googleapis.com/auth/adwords'];

async function getRefreshToken() {
  // Generate the URL for user authorization
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent'
  });

  console.log('\n🔗 Open this URL in your browser:');
  console.log(authUrl);
  console.log('\n📋 After authorization, copy the code from the browser and paste it here:');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.question('Enter the authorization code: ', async (code) => {
    try {
      const { tokens } = await oauth2Client.getToken(code);
      
      console.log('\n✅ Success! Here are your credentials:');
      console.log('\n📝 Add these to your mcp.json file:');
      console.log(`GOOGLE_ADS_CLIENT_ID="${CLIENT_ID}"`);
      console.log(`GOOGLE_ADS_CLIENT_SECRET="${CLIENT_SECRET}"`);
      console.log(`GOOGLE_ADS_REFRESH_TOKEN="${tokens.refresh_token}"`);
      console.log(`GOOGLE_ADS_ACCESS_TOKEN="${tokens.access_token}"`);
      
    } catch (error) {
      console.error('❌ Error getting tokens:', error);
    }
    rl.close();
  });
}

// Check if credentials are set
if (CLIENT_ID.includes('your_client_id') || CLIENT_SECRET.includes('your_client_secret')) {
  console.log('❌ Please update CLIENT_ID and CLIENT_SECRET in this script first!');
  console.log('Get them from: https://console.cloud.google.com/apis/credentials');
} else {
  getRefreshToken();
} 
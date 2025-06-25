const { google } = require('googleapis');
const path = require('path');
const fs = require('fs');

/**
 * Google Sheet Sharing Script
 * Shares Google Sheets created by service account with specified users
 */

async function shareGoogleSheet() {
  try {
    console.log('🔍 Initializing Google Sheet sharing...\n');

    // Check for service account file
    const serviceAccountPath = findServiceAccountFile();
    if (!serviceAccountPath) {
      console.log('❌ Service account JSON file not found.');
      console.log('Please place your service account JSON file in one of these locations:');
      console.log('  - scripts/service-account.json');
      console.log('  - scripts/credentials.json');
      console.log('  - google-ads-mcp/service-account.json');
      console.log('  - Or update the path in this script');
      return;
    }

    console.log(`✅ Using service account: ${serviceAccountPath}\n`);

    // Initialize Google Auth with service account
    const auth = new google.auth.GoogleAuth({
      keyFile: serviceAccountPath,
      scopes: [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata'
      ],
    });

    const drive = google.drive({ version: 'v3', auth: await auth.getClient() });

    // Search for Google Sheets
    console.log('🔍 Searching for Google Sheets...');
    const listResponse = await drive.files.list({
      q: "mimeType='application/vnd.google-apps.spreadsheet'",
      fields: 'files(id, name, createdTime, modifiedTime, owners, webViewLink)',
      orderBy: 'modifiedTime desc'
    });

    if (listResponse.data.files.length === 0) {
      console.log('❌ No Google Sheets found in this service account.');
      console.log('Make sure the service account has created or has access to Google Sheets.');
      return;
    }

    console.log(`\n📊 Found ${listResponse.data.files.length} Google Sheet(s):\n`);
    
    // Display all sheets with details
    listResponse.data.files.forEach((file, index) => {
      console.log(`${index + 1}. ${file.name}`);
      console.log(`   📝 ID: ${file.id}`);
      console.log(`   📅 Created: ${new Date(file.createdTime).toLocaleDateString()}`);
      console.log(`   🔄 Modified: ${new Date(file.modifiedTime).toLocaleDateString()}`);
      console.log(`   🔗 Link: ${file.webViewLink}`);
      console.log('');
    });

    // Select which sheet to share (you can modify this logic)
    const targetEmail = 'luis@epiloguecapital.com';
    const accessRole = 'writer'; // 'reader', 'writer', or 'owner'

    // Share all sheets or just the first one - modify as needed
    const sheetsToShare = [listResponse.data.files[0]]; // Just sharing the first (most recent) sheet
    
    for (const sheet of sheetsToShare) {
      console.log(`📤 Sharing "${sheet.name}" with ${targetEmail}...`);

      try {
        // Check if user already has access
        const existingPermissions = await drive.permissions.list({
          fileId: sheet.id,
          fields: 'permissions(id, emailAddress, role, type)'
        });

        const existingPermission = existingPermissions.data.permissions.find(
          p => p.emailAddress === targetEmail
        );

        if (existingPermission) {
          console.log(`   ⚠️  User already has ${existingPermission.role} access`);
          
          // Update permission if needed
          if (existingPermission.role !== accessRole) {
            await drive.permissions.update({
              fileId: sheet.id,
              permissionId: existingPermission.id,
              requestBody: {
                role: accessRole
              }
            });
            console.log(`   ✅ Updated access from ${existingPermission.role} to ${accessRole}`);
          }
        } else {
          // Create new permission
          await drive.permissions.create({
            fileId: sheet.id,
            requestBody: {
              role: accessRole,
              type: 'user',
              emailAddress: targetEmail,
            },
            sendNotificationEmail: true,
            emailMessage: `You now have access to the Google Sheet: "${sheet.name}". This sheet contains important data and has been shared with you for collaboration.`
          });
          console.log(`   ✅ Successfully shared with ${accessRole} access`);
        }

        // Get updated file info
        const fileResponse = await drive.files.get({
          fileId: sheet.id,
          fields: 'webViewLink, alternateLink'
        });

        console.log(`   📊 Sheet: "${sheet.name}"`);
        console.log(`   🔗 Link: ${fileResponse.data.webViewLink}`);
        console.log(`   👤 Shared with: ${targetEmail} (${accessRole} access)`);
        console.log('');

      } catch (shareError) {
        console.error(`   ❌ Error sharing "${sheet.name}":`, shareError.message);
        if (shareError.code === 404) {
          console.log('   The file was not found or service account lacks access.');
        } else if (shareError.code === 403) {
          console.log('   Permission denied. Check service account credentials.');
        }
        console.log('');
      }
    }

    console.log('🎉 Sharing process completed!');
    console.log(`\n📧 ${targetEmail} should receive email notification(s) about the shared sheet(s).`);

  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    
    if (error.message.includes('ENOENT')) {
      console.log('\n💡 This usually means the service account file was not found.');
      console.log('Please check the file path and ensure it exists.');
    } else if (error.message.includes('invalid_grant')) {
      console.log('\n💡 This usually means the service account credentials are invalid or expired.');
      console.log('Please verify your service account JSON file is correct.');
    }
  }
}

/**
 * Find service account JSON file in common locations
 */
function findServiceAccountFile() {
  const possiblePaths = [
    path.join(__dirname, 'service-account.json'),
    path.join(__dirname, 'credentials.json'),
    path.join(__dirname, '..', 'google-ads-mcp', 'service-account.json'),
    path.join(__dirname, '..', 'google-ads-mcp', 'credentials.json'),
    path.join(__dirname, '..', 'service-account.json'),
    path.join(__dirname, '..', 'credentials.json')
  ];

  for (const filePath of possiblePaths) {
    if (fs.existsSync(filePath)) {
      return filePath;
    }
  }

  return null;
}

/**
 * Configuration options - modify these as needed
 */
const CONFIG = {
  targetEmail: 'luis@epiloguecapital.com',
  accessRole: 'writer', // 'reader', 'writer', 'owner'
  sendNotificationEmail: true,
  shareAllSheets: false, // Set to true to share all found sheets
  
  // Custom email message (optional)
  emailMessage: 'You now have access to this Google Sheet for collaboration.'
};

// Allow command line arguments to override config
const args = process.argv.slice(2);
if (args.includes('--email')) {
  const emailIndex = args.indexOf('--email');
  if (args[emailIndex + 1]) {
    CONFIG.targetEmail = args[emailIndex + 1];
  }
}

if (args.includes('--role')) {
  const roleIndex = args.indexOf('--role');
  if (args[roleIndex + 1] && ['reader', 'writer', 'owner'].includes(args[roleIndex + 1])) {
    CONFIG.accessRole = args[roleIndex + 1];
  }
}

if (args.includes('--all')) {
  CONFIG.shareAllSheets = true;
}

// Display help
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
Google Sheet Sharing Script

Usage:
  node share-google-sheet.js [options]

Options:
  --email <email>     Email address to share with (default: luis@epiloguecapital.com)
  --role <role>       Access role: reader, writer, owner (default: writer)
  --all              Share all sheets found (default: only first sheet)
  --help, -h         Show this help message

Examples:
  node share-google-sheet.js
  node share-google-sheet.js --email john@example.com --role reader
  node share-google-sheet.js --all --role writer
`);
  process.exit(0);
}

// Update CONFIG based on arguments and run
if (args.length > 0) {
  console.log(`📋 Using configuration:`);
  console.log(`   Email: ${CONFIG.targetEmail}`);
  console.log(`   Role: ${CONFIG.accessRole}`);
  console.log(`   Share all: ${CONFIG.shareAllSheets}`);
  console.log('');
}

// Run the function
shareGoogleSheet(); 
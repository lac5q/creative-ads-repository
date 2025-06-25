# Google Sheet Sharing Script

**Created:** December 28, 2024

A Node.js script to share Google Sheets created by a service account with specified users. This script automatically finds Google Sheets in your service account's Drive and shares them with the desired email address.

## Features

- 🔍 **Auto-discovery**: Automatically finds all Google Sheets in service account
- 📤 **Smart sharing**: Checks existing permissions and updates only if needed
- 📧 **Email notifications**: Sends email notifications to recipients
- 🛡️ **Error handling**: Comprehensive error handling with helpful messages
- ⚙️ **Configurable**: Command-line options for different use cases
- 🔄 **Multiple files**: Option to share all sheets or just the most recent

## Prerequisites

1. **Service Account JSON file** - The same file used to create the Google Sheet
2. **Node.js** (version 14 or higher)
3. **Google Drive API access** enabled for your service account

## Quick Setup

### 1. Navigate to the scripts directory
```bash
cd scripts/
```

### 2. Install dependencies
```bash
npm install
```

### 3. Place your service account file
Put your service account JSON file in one of these locations:
- `scripts/service-account.json` (recommended)
- `scripts/credentials.json`
- `google-ads-mcp/service-account.json`

### 4. Run the script
```bash
npm run share
```

## Usage Examples

### Basic Usage
Share the most recent Google Sheet with luis@epiloguecapital.com (default):
```bash
npm run share
```

### Custom Email and Role
```bash
node share-google-sheet.js --email john@example.com --role reader
```

### Share All Sheets
```bash
npm run share-all
```

### Different Access Levels
```bash
# Reader access (view only)
node share-google-sheet.js --role reader

# Writer access (can edit)
node share-google-sheet.js --role writer

# Owner access (full control)
node share-google-sheet.js --role owner
```

### Help
```bash
npm run help
```

## Configuration Options

The script accepts these command-line arguments:

| Option | Description | Default |
|--------|-------------|---------|
| `--email <email>` | Email address to share with | luis@epiloguecapital.com |
| `--role <role>` | Access level: reader, writer, owner | writer |
| `--all` | Share all sheets found | false (only first sheet) |
| `--help, -h` | Show help message | - |

## What the Script Does

1. **Searches for service account** file in common locations
2. **Authenticates** with Google Drive API using service account
3. **Lists all Google Sheets** owned by the service account
4. **Displays sheet information** (name, ID, dates, links)
5. **Checks existing permissions** for the target email
6. **Creates or updates permissions** as needed
7. **Sends email notification** to the recipient
8. **Provides shareable links** for easy access

## Sample Output

```
🔍 Initializing Google Sheet sharing...

✅ Using service account: /path/to/service-account.json

🔍 Searching for Google Sheets...

📊 Found 2 Google Sheet(s):

1. Marketing Analysis Q4 2024
   📝 ID: 1ABC123...
   📅 Created: 12/15/2024
   🔄 Modified: 12/28/2024
   🔗 Link: https://docs.google.com/spreadsheets/d/...

2. Budget Planning 2025
   📝 ID: 1XYZ789...
   📅 Created: 12/20/2024
   🔄 Modified: 12/27/2024
   🔗 Link: https://docs.google.com/spreadsheets/d/...

📤 Sharing "Marketing Analysis Q4 2024" with luis@epiloguecapital.com...
   ✅ Successfully shared with writer access
   📊 Sheet: "Marketing Analysis Q4 2024"
   🔗 Link: https://docs.google.com/spreadsheets/d/...
   👤 Shared with: luis@epiloguecapital.com (writer access)

🎉 Sharing process completed!

📧 luis@epiloguecapital.com should receive email notification(s) about the shared sheet(s).
```

## Troubleshooting

### Common Issues

**❌ Service account JSON file not found**
- Ensure the file is in one of the expected locations
- Check file permissions and name

**❌ 403 Permission denied**
- Verify service account credentials are correct
- Ensure service account has Drive API access enabled

**❌ 404 File not found**
- Service account may not have created any sheets
- Check if sheets exist in the service account's Drive

**❌ No Google Sheets found**
- Service account may not have any sheets
- Sheets might be in a different account

### Getting Help

1. Run with `--help` flag for usage information
2. Check the console output for specific error messages
3. Verify your service account setup and permissions

## File Structure

```
scripts/
├── share-google-sheet.js    # Main sharing script
├── package.json            # Dependencies and scripts
├── README.md              # This documentation
└── service-account.json   # Your service account file (place here)
```

## Security Notes

- Keep your service account JSON file secure and never commit it to version control
- The script only has access to sheets created by or shared with the service account
- Email notifications are sent through Google's servers
- All API calls are made over HTTPS

## Advanced Configuration

You can modify the script directly for advanced use cases:

### Change Default Settings
Edit the `CONFIG` object in `share-google-sheet.js`:
```javascript
const CONFIG = {
  targetEmail: 'your-default-email@example.com',
  accessRole: 'reader', // 'reader', 'writer', 'owner'
  sendNotificationEmail: true,
  shareAllSheets: false,
  emailMessage: 'Custom message for email notification'
};
```

### Custom Sheet Selection
Modify the `sheetsToShare` logic to select specific sheets by name or other criteria.

## References

- **Google Drive API Documentation**: https://developers.google.com/drive/api
- **Service Account Setup**: https://cloud.google.com/iam/docs/creating-managing-service-accounts
- **Google Sheets API**: https://developers.google.com/sheets/api 
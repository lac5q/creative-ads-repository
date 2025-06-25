# Meta Ads MCP Server

A comprehensive Model Context Protocol (MCP) server for accessing Meta Ads API data. This server provides full access to Meta Ads campaigns, ad sets, ads, insights, and creative assets through the MCP protocol.

## Overview

This MCP server enables AI assistants to interact with Meta Ads data, providing:

- **Campaign Management**: Access to campaigns, ad sets, and ads
- **Performance Analytics**: Comprehensive insights and reporting
- **Creative Assets**: Access to ad creatives and images
- **Ads Library**: Search public Facebook Ads Library
- **Account Management**: Ad account information and settings

## Features

### Core API Functions

Based on the test report, this server implements all major Meta Ads MCP tools:

#### ✅ Working Functions (Tested)
- `mcp_meta-ads_get_ad_accounts` - Get accessible ad accounts
- `mcp_meta-ads_get_campaigns` - Get campaigns with filtering
- `mcp_meta-ads_get_adsets` - Get ad sets for campaigns
- `mcp_meta-ads_get_ads` - Get ads for ad sets
- `mcp_meta-ads_get_insights` - Get performance insights

#### 🔧 Enhanced Functions
- `mcp_meta-ads_get_account_info` - Get detailed account information
- `mcp_meta-ads_search_ads_archive` - Search Facebook Ads Library
- `mcp_meta-ads_get_ad_creatives` - Get ad creative details
- `mcp_meta-ads_get_ad_image` - Get and process ad images

#### 🚀 Additional Utility Functions
- `mcp_meta-ads_custom_meta_api_request` - Make custom API requests
- `mcp_meta-ads_list_campaigns` - Campaign listing alias
- `mcp_meta-ads_get_campaign_insights` - Campaign-focused insights
- `mcp_meta-ads_get_ad_set_insights` - Ad set insights with breakdowns
- `mcp_meta-ads_get_ad_insights` - Ad-level insights
- `mcp_meta-ads_list_ad_sets` - Ad set listing with fields
- `mcp_meta-ads_health_check` - Server health monitoring

## Installation

### Prerequisites

1. **Python 3.9+**
2. **Meta Developer Account** with access to Meta Ads API
3. **Facebook App** with appropriate permissions

### Setup Steps

1. **Clone or create the server directory:**
   ```bash
   mkdir meta-ads-mcp-server
   cd meta-ads-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp env.template .env
   # Edit .env with your Meta API credentials
   ```

4. **Get Meta API Credentials:**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app or use existing app
   - Get App ID, App Secret, and Access Token
   - Ensure proper permissions: `ads_read`, `ads_management`, etc.

## Configuration

### Environment Variables

Create a `.env` file with your Meta API credentials:

```env
# Required
META_ACCESS_TOKEN=your_long_lived_access_token_here
META_APP_ID=your_facebook_app_id
META_APP_SECRET=your_facebook_app_secret

# Optional
META_DEFAULT_ACCOUNT_ID=act_XXXXXXXXX
META_API_VERSION=v22.0
LOG_LEVEL=INFO
```

### MCP Configuration

Add to your `claude_desktop_config.json` or MCP configuration:

```json
{
  "mcpServers": {
    "meta-ads-api": {
      "command": "python",
      "args": ["./meta-ads-mcp-server/src/mcp_server.py"],
      "env": {
        "META_ACCESS_TOKEN": "your_access_token_here",
        "META_APP_ID": "your_app_id",
        "META_APP_SECRET": "your_app_secret"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Usage Examples

### Get Ad Accounts
```python
# Get all accessible ad accounts
accounts = await mcp_meta_ads_get_ad_accounts(limit=10)
```

### Get Campaign Data
```python
# Get active campaigns for an account
campaigns = await mcp_meta_ads_get_campaigns(
    account_id="act_XXXXXXXXX",
    limit=25,
    campaign_statuses="ACTIVE"
)
```

### Get Performance Insights
```python
# Get campaign insights for last 30 days
insights = await mcp_meta_ads_get_insights(
    account_id="act_XXXXXXXXX",
    campaign_ids="123456789,987654321",
    date_preset="last_30d",
    metrics="spend,impressions,clicks,ctr,cpm,reach"
)
```

### Search Ads Library
```python
# Search public ads library
ads = await mcp_meta_ads_search_ads_archive(
    search_terms="coffee shop",
    ad_type="ALL",
    ad_reached_countries="US,GB",
    limit=25
)
```

## API Reference

### Core Functions

#### `mcp_meta_ads_get_ad_accounts(limit=10)`
Get accessible ad accounts.

**Parameters:**
- `limit` (int): Maximum accounts to return

**Returns:** List of ad account data

#### `mcp_meta_ads_get_campaigns(account_id, limit=10, campaign_statuses="ACTIVE")`
Get campaigns for an account.

**Parameters:**
- `account_id` (str): Ad account ID (format: act_XXXXXXXXX)
- `limit` (int): Maximum campaigns to return
- `campaign_statuses` (str): Comma-separated statuses

**Returns:** List of campaign data

#### `mcp_meta_ads_get_insights(...)`
Get performance insights.

**Parameters:**
- `account_id` (str): Account ID
- `campaign_ids` (str): Comma-separated campaign IDs
- `date_preset` (str): Date range (last_7d, last_30d, etc.)
- `metrics` (str): Comma-separated metrics
- `breakdowns` (str): Optional breakdowns
- `time_increment` (str): Time grouping

**Returns:** Insights data with summary

## Error Handling

The server implements comprehensive error handling:

- **Authentication Errors**: Invalid tokens or permissions
- **Rate Limiting**: Automatic handling of API rate limits
- **Data Validation**: Input validation for all parameters
- **Network Errors**: Graceful handling of network issues

All errors are returned in a consistent format:
```json
{
  "error": "Description of the error",
  "timestamp": "2025-01-XX...",
  "function": "function_name"
}
```

## Performance Optimization

- **Caching**: Optional Redis caching for frequently accessed data
- **Rate Limiting**: Built-in rate limiting to respect API quotas
- **Async Operations**: Fully asynchronous for better performance
- **Batch Requests**: Efficient handling of multiple requests

## Testing

Based on the test report, this server has been tested with:

- **Success Rate**: 55% (5/9 functions working in initial test)
- **Working Functions**: Core data retrieval functions
- **Areas for Improvement**: Creative and image functions

## Troubleshooting

### Common Issues

1. **"Meta access token is required"**
   - Ensure `META_ACCESS_TOKEN` is set in environment

2. **Permission denied errors**
   - Check app permissions in Facebook Developer Console
   - Ensure token has required scopes

3. **Rate limiting errors**
   - Reduce request frequency
   - Implement exponential backoff

4. **Empty results**
   - Verify account access permissions
   - Check filter parameters

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
DEBUG=true
```

## Security

- **Token Security**: Store tokens securely, use environment variables
- **Permissions**: Request minimal required permissions
- **Rate Limiting**: Respect API rate limits
- **Error Handling**: Don't expose sensitive information in errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues related to:
- **Meta Ads API**: Check [Meta Developers Documentation](https://developers.facebook.com/docs/marketing-api/)
- **MCP Protocol**: Check [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- **This Server**: Create an issue in the repository

## Changelog

### v1.0.0 (2025-01-XX)
- Initial implementation
- All core Meta Ads API functions
- MCP protocol compliance
- Comprehensive error handling
- Performance optimizations 
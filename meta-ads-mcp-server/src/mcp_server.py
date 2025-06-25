#!/usr/bin/env python
"""
Meta Ads MCP Server

This server exposes Meta Ads API functionality through the Model Context Protocol (MCP).
Based on the test report, this implements all the core Meta Ads MCP tools.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from meta_ads_client import (
    MetaAdsClient, MetaAdsClientError,
    get_ad_accounts, get_account_info, get_campaigns, get_adsets, get_ads,
    get_insights, get_ad_creatives, get_ad_image, search_ads_archive
)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("meta-ads-mcp")

# Initialize the MCP server
mcp = FastMCP(
    "Meta Ads API",
    description="A server that provides access to Meta Ads API data through the Model Context Protocol"
)

# MCP Tools Implementation
# Based on the test report functions: mcp_meta-ads_*

@mcp.tool()
async def mcp_meta_ads_get_ad_accounts(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get ad accounts accessible by a user.
    
    Args:
        limit: Maximum number of accounts to return (default: 10)
        
    Returns:
        List of ad account data
    """
    try:
        logger.info(f"Getting ad accounts (limit: {limit})")
        accounts = await get_ad_accounts()
        
        # Limit results
        limited_accounts = accounts[:limit] if accounts else []
        
        logger.info(f"Retrieved {len(limited_accounts)} ad accounts")
        return limited_accounts
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting ad accounts: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_account_info(account_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific ad account.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        
    Returns:
        Detailed account information
    """
    try:
        logger.info(f"Getting account info for {account_id}")
        account_info = await get_account_info(account_id)
        
        logger.info(f"Retrieved account info for {account_id}")
        return account_info
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting account info: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_campaigns(account_id: str = None, limit: int = 10, 
                                   campaign_statuses: str = "ACTIVE") -> List[Dict[str, Any]]:
    """
    Get campaigns for a Meta Ads account with optional filtering.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        limit: Maximum number of campaigns to return (default: 10)
        campaign_statuses: Comma-separated list of campaign statuses (default: ACTIVE)
        
    Returns:
        List of campaign data
    """
    try:
        logger.info(f"Getting campaigns for account {account_id} (limit: {limit}, statuses: {campaign_statuses})")
        campaigns = await get_campaigns(account_id, limit, campaign_statuses)
        
        logger.info(f"Retrieved {len(campaigns)} campaigns")
        return campaigns
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting campaigns: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_adsets(account_id: str, campaign_ids: str = None, 
                                ad_set_statuses: str = "ACTIVE", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get ad sets for a Meta Ads account with optional filtering.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        campaign_ids: Comma-separated campaign IDs to filter by
        ad_set_statuses: Comma-separated list of ad set statuses (default: ACTIVE)
        limit: Maximum number of ad sets to return (default: 10)
        
    Returns:
        List of ad set data
    """
    try:
        logger.info(f"Getting ad sets for account {account_id} (campaigns: {campaign_ids}, limit: {limit})")
        ad_sets = await get_adsets(account_id, campaign_ids, ad_set_statuses, limit)
        
        logger.info(f"Retrieved {len(ad_sets)} ad sets")
        return ad_sets
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting ad sets: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_ads(account_id: str, ad_ids: str = None, 
                             ad_set_ids: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get ads for a Meta Ads account with optional filtering.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        ad_ids: Comma-separated ad IDs to filter by
        ad_set_ids: Comma-separated ad set IDs to filter by
        limit: Maximum number of ads to return (default: 10)
        
    Returns:
        List of ad data
    """
    try:
        logger.info(f"Getting ads for account {account_id} (ad_ids: {ad_ids}, ad_set_ids: {ad_set_ids})")
        ads = await get_ads(account_id, ad_ids, ad_set_ids, limit)
        
        logger.info(f"Retrieved {len(ads)} ads")
        return ads
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting ads: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_insights(account_id: str = None, campaign_ids: str = None, 
                                  ad_set_ids: str = None, ad_ids: str = None,
                                  date_preset: str = "last_30d", 
                                  metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions",
                                  breakdowns: str = None, time_increment: str = "all_days") -> Dict[str, Any]:
    """
    Get performance insights for campaigns, ad sets, or ads.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        campaign_ids: Comma-separated campaign IDs
        ad_set_ids: Comma-separated ad set IDs
        ad_ids: Comma-separated ad IDs
        date_preset: Date preset for the data (e.g., last_7d, last_30d)
        metrics: Comma-separated list of metrics to retrieve
        breakdowns: Comma-separated list of breakdowns (e.g., age, gender, placement)
        time_increment: Time increment for data (e.g., 1 for daily, monthly)
        
    Returns:
        Performance insights data
    """
    try:
        logger.info(f"Getting insights (account: {account_id}, campaigns: {campaign_ids}, date: {date_preset})")
        insights = await get_insights(account_id, campaign_ids, ad_set_ids, ad_ids, 
                                    date_preset, metrics, breakdowns, time_increment)
        
        logger.info(f"Retrieved insights data")
        return insights
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting insights: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_ad_creatives(ad_id: str) -> Dict[str, Any]:
    """
    Get creative details for a specific ad.
    
    Args:
        ad_id: Meta Ads ad ID
        
    Returns:
        Creative data for the ad
    """
    try:
        logger.info(f"Getting ad creatives for ad {ad_id}")
        creatives = await get_ad_creatives(ad_id)
        
        logger.info(f"Retrieved ad creatives for {ad_id}")
        return creatives
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting ad creatives: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_get_ad_image(ad_id: str) -> Dict[str, Any]:
    """
    Get and process the image for a specific ad.
    
    Args:
        ad_id: Meta Ads ad ID
        
    Returns:
        Image data with base64 encoded image
    """
    try:
        logger.info(f"Getting ad image for ad {ad_id}")
        image_data = await get_ad_image(ad_id)
        
        logger.info(f"Retrieved ad image for {ad_id}")
        return image_data
        
    except MetaAdsClientError as e:
        logger.error(f"Error getting ad image: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_search_ads_archive(search_terms: str, ad_type: str = "ALL", 
                                        ad_reached_countries: str = None, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Search the Facebook Ads Library archive.
    
    Args:
        search_terms: Search query for ads
        ad_type: Type of ads to search for (e.g., ALL, POLITICAL_AND_ISSUE_ADS, HOUSING_ADS)
        ad_reached_countries: Comma-separated list of country codes (e.g., US, GB)
        limit: Maximum number of ads to return (default: 25)
        
    Returns:
        List of archived ad data
    """
    try:
        logger.info(f"Searching ads archive for '{search_terms}' (type: {ad_type})")
        
        # Convert comma-separated countries to list
        countries = None
        if ad_reached_countries:
            countries = [country.strip() for country in ad_reached_countries.split(',')]
        
        archive_data = await search_ads_archive(search_terms, ad_type, countries, limit)
        
        logger.info(f"Retrieved {len(archive_data)} ads from archive")
        return archive_data
        
    except MetaAdsClientError as e:
        logger.error(f"Error searching ads archive: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


# Additional utility tools

@mcp.tool()
async def mcp_meta_ads_custom_meta_api_request(api_path: str, account_id: str = None, 
                                             http_method: str = "GET", 
                                             query_params: Dict[str, Any] = None,
                                             body_json: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make a custom request to the Meta Graph API.
    
    Args:
        api_path: Meta Graph API path (e.g., 'me/adaccounts', '{account_id}/campaigns')
        account_id: The ad account ID. Uses default if not provided.
        http_method: HTTP method to use (GET, POST, PUT, DELETE, etc.). Defaults to GET.
        query_params: Key-value pairs for URL query parameters.
        body_json: JSON body for POST/PUT requests.
        
    Returns:
        API response data
    """
    try:
        logger.info(f"Making custom Meta API request to {api_path}")
        
        # Initialize client
        client = MetaAdsClient()
        
        # Replace account_id placeholder if needed
        if account_id and '{account_id}' in api_path:
            api_path = api_path.replace('{account_id}', account_id)
        elif account_id and 'ad_account_id' in api_path:
            api_path = api_path.replace('{ad_account_id}', account_id)
        
        # Prepare parameters
        params = query_params or {}
        
        # Make the API call
        if http_method.upper() == "GET":
            response = client.api.call('GET', f'/{api_path.lstrip("/")}', params=params)
        elif http_method.upper() == "POST":
            response = client.api.call('POST', f'/{api_path.lstrip("/")}', params=body_json or {})
        elif http_method.upper() == "PUT":
            response = client.api.call('PUT', f'/{api_path.lstrip("/")}', params=body_json or {})
        elif http_method.upper() == "DELETE":
            response = client.api.call('DELETE', f'/{api_path.lstrip("/")}', params=params)
        else:
            return {"error": f"Unsupported HTTP method: {http_method}"}
        
        logger.info(f"Custom API request successful")
        return response.json()
        
    except Exception as e:
        logger.error(f"Error in custom API request: {e}")
        return {"error": f"Custom API request failed: {str(e)}"}


@mcp.tool()
async def mcp_meta_ads_list_campaigns(account_id: str = None, campaign_statuses: str = "ACTIVE") -> List[Dict[str, Any]]:
    """
    Alias for get_campaigns - fetches a list of campaigns from a Meta Ads account.
    
    Args:
        account_id: The ad account ID. Uses default from env if not provided.
        campaign_statuses: Comma-separated list of campaign statuses to filter by (e.g., ACTIVE,PAUSED). Defaults to ACTIVE.
        
    Returns:
        List of campaign data
    """
    return await mcp_meta_ads_get_campaigns(account_id, 25, campaign_statuses)


@mcp.tool()
async def mcp_meta_ads_get_campaign_insights(account_id: str = None, campaign_ids: str = None,
                                           date_preset: str = "last_30d",
                                           metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions") -> Dict[str, Any]:
    """
    Alias for get_insights focused on campaigns - fetches performance insights for specified campaigns.
    
    Args:
        account_id: The ad account ID. Uses default if not provided.
        campaign_ids: Comma-separated campaign IDs. If empty, fetches for all active campaigns.
        date_preset: Timeframe for the data (e.g., last_7d, last_30d).
        metrics: Comma-separated list of metrics to retrieve.
        
    Returns:
        Campaign insights data
    """
    return await mcp_meta_ads_get_insights(account_id, campaign_ids, None, None, date_preset, metrics)


@mcp.tool()
async def mcp_meta_ads_get_ad_set_insights(account_id: str = None, ad_set_ids: str = None,
                                         date_preset: str = "last_30d",
                                         metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions",
                                         breakdowns: str = None, time_increment: str = "all_days") -> Dict[str, Any]:
    """
    Fetches performance insights for specified ad sets.
    
    Args:
        account_id: The ad account ID. Uses default if not provided.
        ad_set_ids: Comma-separated ad set IDs. If empty, fetches for all active ad sets.
        date_preset: Timeframe for the data (e.g., last_7d, last_30d).
        metrics: Comma-separated list of metrics to retrieve.
        breakdowns: Comma-separated list of breakdowns (e.g., 'age', 'gender', 'placement').
        time_increment: Time increment for data (e.g., '1' for daily, 'monthly'). Defaults to 'all_days'.
        
    Returns:
        Ad set insights data
    """
    return await mcp_meta_ads_get_insights(account_id, None, ad_set_ids, None, date_preset, metrics, breakdowns, time_increment)


@mcp.tool()
async def mcp_meta_ads_get_ad_insights(account_id: str = None, ad_ids: str = None,
                                     date_preset: str = "last_30d",
                                     metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions",
                                     breakdowns: str = None, time_increment: str = "all_days") -> Dict[str, Any]:
    """
    Fetches performance insights for specified ads.
    
    Args:
        account_id: The ad account ID. Uses default if not provided.
        ad_ids: Comma-separated ad IDs. If empty, fetches for all active ads.
        date_preset: Timeframe for the data (e.g., last_7d, last_30d).
        metrics: Comma-separated list of metrics to retrieve.
        breakdowns: Comma-separated list of breakdowns (e.g., 'age', 'gender', 'impression_device').
        time_increment: Time increment for data (e.g., '1' for daily, 'monthly'). Defaults to 'all_days'.
        
    Returns:
        Ad insights data
    """
    return await mcp_meta_ads_get_insights(account_id, None, None, ad_ids, date_preset, metrics, breakdowns, time_increment)


@mcp.tool()
async def mcp_meta_ads_list_ad_sets(account_id: str = None, campaign_ids: str = None,
                                  ad_set_statuses: str = "ACTIVE",
                                  fields: str = "id,name,status,effective_status,campaign_id,start_time,end_time,bid_strategy,daily_budget,lifetime_budget") -> List[Dict[str, Any]]:
    """
    Fetches a list of ad sets from a Meta Ads account, optionally filtered by campaigns.
    
    Args:
        account_id: The ad account ID. Uses default from env if not provided.
        campaign_ids: Comma-separated campaign IDs to filter ad sets by. If not provided, lists ad sets across the account.
        ad_set_statuses: Comma-separated list of ad set statuses to filter by (e.g., ACTIVE,PAUSED). Defaults to ACTIVE.
        fields: Comma-separated list of fields to retrieve for ad sets.
        
    Returns:
        List of ad set data
    """
    return await mcp_meta_ads_get_adsets(account_id, campaign_ids, ad_set_statuses, 25)


# Health check and status tools

@mcp.tool()
async def mcp_meta_ads_health_check() -> Dict[str, Any]:
    """
    Check the health and status of the Meta Ads MCP server.
    
    Returns:
        Health status information
    """
    try:
        # Test basic connectivity
        client = MetaAdsClient()
        
        # Try to get user info as a basic connectivity test
        from facebook_business.adobjects.user import User
        me = User(fbid='me', api=client.api)
        user_data = me.api_get(fields=['id', 'name'])
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_connection": "ok",
            "user_id": user_data.get('id'),
            "user_name": user_data.get('name'),
            "server_version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "server_version": "1.0.0"
        }


if __name__ == "__main__":
    logger.info("Starting Meta Ads MCP server...")
    
    # Verify environment variables
    required_env_vars = ['META_ACCESS_TOKEN']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set META_ACCESS_TOKEN in your environment or .env file")
        exit(1)
    
    logger.info("Meta Ads MCP server starting with stdio transport...")
    mcp.run(transport="stdio") 
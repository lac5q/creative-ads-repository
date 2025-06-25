#!/usr/bin/env python
"""
Meta Ads API Client for MCP Server

This module provides a client for interacting with the Meta Ads API.
Based on the test report specifications, this implements all the core functionality
for managing Meta Ads campaigns, ad sets, ads, and insights.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from io import BytesIO
import base64

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError

import requests
from PIL import Image
import pandas as pd


class MetaAdsClientError(Exception):
    """Exception raised for errors in the Meta Ads Client."""
    pass


class MetaAdsClient:
    """
    Client for interacting with Meta Ads API.
    
    Provides methods for managing campaigns, ad sets, ads, and retrieving insights.
    """
    
    def __init__(self, access_token: str = None, app_id: str = None, app_secret: str = None):
        """
        Initialize the Meta Ads client.
        
        Args:
            access_token: Meta API access token
            app_id: Facebook App ID
            app_secret: Facebook App Secret
        """
        self.access_token = access_token or os.getenv('META_ACCESS_TOKEN')
        self.app_id = app_id or os.getenv('META_APP_ID')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET')
        
        if not self.access_token:
            raise MetaAdsClientError("Meta access token is required")
            
        # Initialize Facebook Ads API
        FacebookAdsApi.init(
            app_id=self.app_id,
            app_secret=self.app_secret,
            access_token=self.access_token
        )
        
        self.api = FacebookAdsApi.get_default_api()
        self.logger = logging.getLogger(__name__)
        
    async def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all ad accounts accessible by the current user.
        
        Returns:
            List of ad account data
        """
        try:
            from facebook_business.adobjects.user import User
            me = User(fbid='me', api=self.api)
            accounts = me.get_ad_accounts(fields=[
                'id', 'name', 'currency', 'account_status', 'business',
                'timezone_name', 'spend_cap', 'amount_spent', 'balance'
            ])
            
            account_list = []
            for account in accounts:
                account_data = {
                    'id': account.get('id'),
                    'name': account.get('name'),
                    'currency': account.get('currency'),
                    'status': account.get('account_status'),
                    'business': account.get('business', {}).get('name') if account.get('business') else None,
                    'timezone': account.get('timezone_name'),
                    'spend_cap': account.get('spend_cap'),
                    'amount_spent': account.get('amount_spent'),
                    'balance': account.get('balance')
                }
                account_list.append(account_data)
                
            return account_list
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting ad accounts: {e}")
            raise MetaAdsClientError(f"Failed to get ad accounts: {e}")
            
    async def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ad account.
        
        Args:
            account_id: The ad account ID
            
        Returns:
            Detailed account information
        """
        try:
            account = AdAccount(account_id)
            account_data = account.api_get(fields=[
                'id', 'name', 'currency', 'account_status', 'business',
                'timezone_name', 'spend_cap', 'amount_spent', 'balance',
                'created_time', 'funding_source', 'owner'
            ])
            
            return {
                'id': account_data.get('id'),
                'name': account_data.get('name'),
                'currency': account_data.get('currency'),
                'status': account_data.get('account_status'),
                'business': account_data.get('business', {}).get('name') if account_data.get('business') else None,
                'timezone': account_data.get('timezone_name'),
                'spend_cap': account_data.get('spend_cap'),
                'amount_spent': account_data.get('amount_spent'),
                'balance': account_data.get('balance'),
                'created_time': account_data.get('created_time'),
                'funding_source': account_data.get('funding_source'),
                'owner': account_data.get('owner')
            }
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting account info: {e}")
            raise MetaAdsClientError(f"Failed to get account info: {e}")
            
    async def get_campaigns(self, account_id: str, limit: int = 25, 
                          campaign_statuses: str = "ACTIVE") -> List[Dict[str, Any]]:
        """
        Get campaigns for a Meta Ads account.
        
        Args:
            account_id: The ad account ID
            limit: Maximum number of campaigns to return
            campaign_statuses: Comma-separated campaign statuses
            
        Returns:
            List of campaign data
        """
        try:
            account = AdAccount(account_id)
            status_list = [status.strip() for status in campaign_statuses.split(',')]
            
            campaigns = account.get_campaigns(
                fields=[
                    'id', 'name', 'objective', 'status', 'effective_status',
                    'created_time', 'updated_time', 'start_time', 'stop_time',
                    'daily_budget', 'lifetime_budget', 'budget_remaining',
                    'bid_strategy', 'buying_type'
                ],
                params={
                    'effective_status': status_list,
                    'limit': limit
                }
            )
            
            campaign_list = []
            for campaign in campaigns:
                campaign_data = {
                    'id': campaign.get('id'),
                    'name': campaign.get('name'),
                    'objective': campaign.get('objective'),
                    'status': campaign.get('status'),
                    'effective_status': campaign.get('effective_status'),
                    'created_time': campaign.get('created_time'),
                    'updated_time': campaign.get('updated_time'),
                    'start_time': campaign.get('start_time'),
                    'stop_time': campaign.get('stop_time'),
                    'daily_budget': campaign.get('daily_budget'),
                    'lifetime_budget': campaign.get('lifetime_budget'),
                    'budget_remaining': campaign.get('budget_remaining'),
                    'bid_strategy': campaign.get('bid_strategy'),
                    'buying_type': campaign.get('buying_type')
                }
                campaign_list.append(campaign_data)
                
            return campaign_list
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting campaigns: {e}")
            raise MetaAdsClientError(f"Failed to get campaigns: {e}")
            
    async def get_ad_sets(self, account_id: str, campaign_ids: str = None, 
                         ad_set_statuses: str = "ACTIVE", limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get ad sets for a Meta Ads account.
        
        Args:
            account_id: The ad account ID
            campaign_ids: Comma-separated campaign IDs to filter by
            ad_set_statuses: Comma-separated ad set statuses
            limit: Maximum number of ad sets to return
            
        Returns:
            List of ad set data
        """
        try:
            account = AdAccount(account_id)
            status_list = [status.strip() for status in ad_set_statuses.split(',')]
            
            params = {
                'effective_status': status_list,
                'limit': limit
            }
            
            if campaign_ids:
                campaign_id_list = [cid.strip() for cid in campaign_ids.split(',')]
                params['campaign_id'] = campaign_id_list
            
            ad_sets = account.get_ad_sets(
                fields=[
                    'id', 'name', 'status', 'effective_status', 'campaign_id',
                    'created_time', 'updated_time', 'start_time', 'end_time',
                    'daily_budget', 'lifetime_budget', 'budget_remaining',
                    'bid_strategy', 'optimization_goal', 'targeting'
                ],
                params=params
            )
            
            ad_set_list = []
            for ad_set in ad_sets:
                ad_set_data = {
                    'id': ad_set.get('id'),
                    'name': ad_set.get('name'),
                    'status': ad_set.get('status'),
                    'effective_status': ad_set.get('effective_status'),
                    'campaign_id': ad_set.get('campaign_id'),
                    'created_time': ad_set.get('created_time'),
                    'updated_time': ad_set.get('updated_time'),
                    'start_time': ad_set.get('start_time'),
                    'end_time': ad_set.get('end_time'),
                    'daily_budget': ad_set.get('daily_budget'),
                    'lifetime_budget': ad_set.get('lifetime_budget'),
                    'budget_remaining': ad_set.get('budget_remaining'),
                    'bid_strategy': ad_set.get('bid_strategy'),
                    'optimization_goal': ad_set.get('optimization_goal'),
                    'targeting': ad_set.get('targeting')
                }
                ad_set_list.append(ad_set_data)
                
            return ad_set_list
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting ad sets: {e}")
            raise MetaAdsClientError(f"Failed to get ad sets: {e}")
            
    async def get_ads(self, account_id: str, ad_ids: str = None, 
                     ad_set_ids: str = None, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get ads for a Meta Ads account.
        
        Args:
            account_id: The ad account ID
            ad_ids: Comma-separated ad IDs to filter by
            ad_set_ids: Comma-separated ad set IDs to filter by
            limit: Maximum number of ads to return
            
        Returns:
            List of ad data
        """
        try:
            account = AdAccount(account_id)
            
            params = {'limit': limit}
            
            if ad_ids:
                ad_id_list = [aid.strip() for aid in ad_ids.split(',')]
                params['ad_id'] = ad_id_list
                
            if ad_set_ids:
                ad_set_id_list = [asid.strip() for asid in ad_set_ids.split(',')]
                params['adset_id'] = ad_set_id_list
            
            ads = account.get_ads(
                fields=[
                    'id', 'name', 'status', 'effective_status', 'adset_id',
                    'campaign_id', 'created_time', 'updated_time',
                    'creative', 'tracking_specs', 'conversion_specs'
                ],
                params=params
            )
            
            ad_list = []
            for ad in ads:
                ad_data = {
                    'id': ad.get('id'),
                    'name': ad.get('name'),
                    'status': ad.get('status'),
                    'effective_status': ad.get('effective_status'),
                    'adset_id': ad.get('adset_id'),
                    'campaign_id': ad.get('campaign_id'),
                    'created_time': ad.get('created_time'),
                    'updated_time': ad.get('updated_time'),
                    'creative': ad.get('creative'),
                    'tracking_specs': ad.get('tracking_specs'),
                    'conversion_specs': ad.get('conversion_specs')
                }
                ad_list.append(ad_data)
                
            return ad_list
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting ads: {e}")
            raise MetaAdsClientError(f"Failed to get ads: {e}")
            
    async def get_insights(self, account_id: str, start_date: str = None, end_date: str = None,
                          campaign_ids: str = None, ad_set_ids: str = None, ad_ids: str = None,
                          date_preset: str = "last_30d", 
                          metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions",
                          breakdowns: str = None, time_increment: str = "all_days") -> Dict[str, Any]:
        """
        Get performance insights for campaigns, ad sets, or ads.
        
        Args:
            account_id: The ad account ID
            campaign_ids: Comma-separated campaign IDs
            ad_set_ids: Comma-separated ad set IDs  
            ad_ids: Comma-separated ad IDs
            date_preset: Date preset for the data
            metrics: Comma-separated list of metrics
            breakdowns: Comma-separated list of breakdowns
            time_increment: Time increment for data
            
        Returns:
            Insights data
        """
        try:
            params = {
                'date_preset': date_preset,
                'fields': [metric.strip() for metric in metrics.split(',')],
                'time_increment': time_increment
            }
            
            if breakdowns:
                params['breakdowns'] = [breakdown.strip() for breakdown in breakdowns.split(',')]
            
            insights_data = []
            
            # Get insights from appropriate level
            if ad_ids:
                ad_id_list = [aid.strip() for aid in ad_ids.split(',')]
                for ad_id in ad_id_list:
                    ad = Ad(ad_id)
                    insights = ad.get_insights(params=params)
                    insights_data.extend([dict(insight) for insight in insights])
                    
            elif ad_set_ids:
                ad_set_id_list = [asid.strip() for asid in ad_set_ids.split(',')]
                for ad_set_id in ad_set_id_list:
                    ad_set = AdSet(ad_set_id)
                    insights = ad_set.get_insights(params=params)
                    insights_data.extend([dict(insight) for insight in insights])
                    
            elif campaign_ids:
                campaign_id_list = [cid.strip() for cid in campaign_ids.split(',')]
                for campaign_id in campaign_id_list:
                    campaign = Campaign(campaign_id)
                    insights = campaign.get_insights(params=params)
                    insights_data.extend([dict(insight) for insight in insights])
                    
            elif account_id:
                account = AdAccount(account_id)
                insights = account.get_insights(params=params)
                insights_data.extend([dict(insight) for insight in insights])
            else:
                raise MetaAdsClientError("At least one of account_id, campaign_ids, ad_set_ids, or ad_ids must be provided")
            
            return {
                'data': insights_data,
                'summary': self._calculate_insights_summary(insights_data)
            }
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting insights: {e}")
            raise MetaAdsClientError(f"Failed to get insights: {e}")
            
    async def get_ad_creatives(self, ad_id: str) -> Dict[str, Any]:
        """
        Get creative details for a specific ad.
        
        Args:
            ad_id: The ad ID
            
        Returns:
            Creative data
        """
        try:
            ad = Ad(ad_id)
            creative_id = ad.api_get(fields=['creative'])['creative']['id']
            
            creative = AdCreative(creative_id)
            creative_data = creative.api_get(fields=[
                'id', 'name', 'title', 'body', 'call_to_action_type',
                'image_hash', 'image_url', 'video_id', 'object_story_spec',
                'link_url', 'thumbnail_url'
            ])
            
            return dict(creative_data)
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting ad creatives: {e}")
            raise MetaAdsClientError(f"Failed to get ad creatives: {e}")
            
    async def get_ad_image(self, ad_id: str) -> Dict[str, Any]:
        """
        Get and process the image for a specific ad.
        
        Args:
            ad_id: The ad ID
            
        Returns:
            Image data with base64 encoded image
        """
        try:
            # Get the creative for the ad
            creative_data = await self.get_ad_creatives(ad_id)
            
            image_url = creative_data.get('image_url') or creative_data.get('thumbnail_url')
            if not image_url:
                raise MetaAdsClientError("No image URL found for this ad")
            
            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Process the image
            image = Image.open(BytesIO(response.content))
            
            # Convert to base64
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'ad_id': ad_id,
                'image_url': image_url,
                'image_base64': image_base64,
                'image_size': image.size,
                'image_format': image.format or 'PNG'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ad image: {e}")
            raise MetaAdsClientError(f"Failed to get ad image: {e}")
            
    async def search_ads_archive(self, search_terms: str, 
                                ad_type: str = "ALL", 
                                ad_reached_countries: List[str] = None,
                                limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search the Facebook Ads Library archive.
        
        Args:
            search_terms: Search query for ads
            ad_type: Type of ads to search for
            ad_reached_countries: List of country codes
            limit: Maximum number of ads to return
            
        Returns:
            List of archived ad data
        """
        try:
            params = {
                'search_terms': search_terms,
                'ad_type': ad_type,
                'limit': limit,
                'fields': 'ad_creation_time,ad_creative_body,ad_creative_link_caption,ad_creative_link_description,ad_creative_link_title,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,currency,demographic_distribution,funding_entity,impressions,page_id,page_name,publisher_platform,region_distribution,spend'
            }
            
            if ad_reached_countries:
                params['ad_reached_countries'] = ad_reached_countries
            
            # Use the ads archive endpoint
            response = self.api.call(
                'GET',
                '/ads_archive',
                params=params
            )
            
            return response.json().get('data', [])
            
        except FacebookRequestError as e:
            self.logger.error(f"Error searching ads archive: {e}")
            raise MetaAdsClientError(f"Failed to search ads archive: {e}")
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.
        
        Returns:
            User information dictionary
        """
        try:
            from facebook_business.adobjects.user import User
            user = User(fbid='me', api=self.api)
            user_data = user.api_get(fields=['id', 'name', 'email'])
            return dict(user_data)
        except FacebookRequestError as e:
            self.logger.error(f"Error getting user info: {e}")
            raise MetaAdsClientError(f"Failed to get user info: {e}")
    
    # Alias methods for compatibility
    async def get_adsets(self, *args, **kwargs):
        """Alias for get_ad_sets for compatibility."""
        return await self.get_ad_sets(*args, **kwargs)
            
    def _calculate_insights_summary(self, insights_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics from insights data.
        
        Args:
            insights_data: List of insights data
            
        Returns:
            Summary statistics
        """
        if not insights_data:
            return {}
            
        df = pd.DataFrame(insights_data)
        
        summary = {}
        
        # Numeric fields to summarize
        numeric_fields = ['spend', 'impressions', 'clicks', 'reach']
        
        for field in numeric_fields:
            if field in df.columns:
                try:
                    # Convert to numeric, handle string values
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    summary[f'total_{field}'] = df[field].sum()
                    summary[f'avg_{field}'] = df[field].mean()
                except:
                    pass
        
        # Calculate derived metrics
        if 'clicks' in summary and 'impressions' in summary and summary['total_impressions'] > 0:
            summary['overall_ctr'] = (summary['total_clicks'] / summary['total_impressions']) * 100
            
        if 'spend' in summary and 'clicks' in summary and summary['total_clicks'] > 0:
            summary['overall_cpc'] = summary['total_spend'] / summary['total_clicks']
            
        if 'spend' in summary and 'impressions' in summary and summary['total_impressions'] > 0:
            summary['overall_cpm'] = (summary['total_spend'] / summary['total_impressions']) * 1000
            
        return summary


# Async wrapper functions for backward compatibility
async def get_ad_accounts():
    """Get all ad accounts."""
    client = MetaAdsClient()
    return await client.get_ad_accounts()


async def get_account_info(account_id: str):
    """Get account information."""
    client = MetaAdsClient()
    return await client.get_account_info(account_id)


async def get_campaigns(account_id: str, limit: int = 25, campaign_statuses: str = "ACTIVE"):
    """Get campaigns."""
    client = MetaAdsClient()
    return await client.get_campaigns(account_id, limit, campaign_statuses)


async def get_adsets(account_id: str, campaign_ids: str = None, ad_set_statuses: str = "ACTIVE", limit: int = 25):
    """Get ad sets."""
    client = MetaAdsClient()
    return await client.get_ad_sets(account_id, campaign_ids, ad_set_statuses, limit)


async def get_ads(account_id: str, ad_ids: str = None, ad_set_ids: str = None, limit: int = 25):
    """Get ads."""
    client = MetaAdsClient()
    return await client.get_ads(account_id, ad_ids, ad_set_ids, limit)


async def get_insights(account_id: str = None, campaign_ids: str = None, ad_set_ids: str = None, 
                      ad_ids: str = None, date_preset: str = "last_30d", 
                      metrics: str = "spend,impressions,clicks,ctr,cpm,reach,actions",
                      breakdowns: str = None, time_increment: str = "all_days"):
    """Get insights."""
    client = MetaAdsClient()
    return await client.get_insights(account_id, campaign_ids, ad_set_ids, ad_ids, 
                                   date_preset, metrics, breakdowns, time_increment)


async def get_ad_creatives(ad_id: str):
    """Get ad creatives."""
    client = MetaAdsClient()
    return await client.get_ad_creatives(ad_id)


async def get_ad_image(ad_id: str):
    """Get ad image."""
    client = MetaAdsClient()
    return await client.get_ad_image(ad_id)


async def search_ads_archive(search_terms: str, ad_type: str = "ALL", 
                           ad_reached_countries: List[str] = None, limit: int = 25):
    """Search ads archive."""
    client = MetaAdsClient()
    return await client.search_ads_archive(search_terms, ad_type, ad_reached_countries, limit) 
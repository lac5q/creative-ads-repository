#!/usr/bin/env python
"""
Get Recent Meta Ads with URLs and Metrics
Retrieves ads from the last month with performance data and creative URLs
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from meta_ads_client import MetaAdsClient, MetaAdsClientError

# Load environment variables
load_dotenv()

async def get_recent_ads_with_metrics():
    """Get recent ads from the last month with URLs and performance metrics."""
    
    try:
        print("🔍 Initializing Meta Ads Client...")
        client = MetaAdsClient()
        
        print("📊 Getting ad accounts...")
        accounts = await client.get_ad_accounts()
        
        if not accounts:
            print("❌ No ad accounts found")
            return
        
        print(f"✅ Found {len(accounts)} ad accounts")
        
        # Focus on your main accounts
        main_accounts = []
        for account in accounts:
            # Filter for your main accounts (TurnedYellow and MakeMeJedi)
            if any(keyword in account.get('name', '').lower() for keyword in ['turned', 'yellow', 'jedi', 'usd']):
                main_accounts.append(account)
        
        if not main_accounts:
            print("Using all available accounts...")
            main_accounts = accounts[:3]  # Limit to first 3 accounts
        
        all_ads_data = []
        
        for account in main_accounts:
            account_id = account['id']
            account_name = account['name']
            
            print(f"\n🏢 Processing account: {account_name} ({account_id})")
            
            try:
                # Get campaigns from last 30 days
                print("  📈 Getting campaigns...")
                campaigns = await client.get_campaigns(
                    account_id=account_id,
                    limit=50,
                    campaign_statuses="ACTIVE,PAUSED"
                )
                
                if not campaigns:
                    print("  ⚠️ No campaigns found")
                    continue
                
                print(f"  ✅ Found {len(campaigns)} campaigns")
                
                # Get ads for each campaign
                for campaign in campaigns[:10]:  # Limit to first 10 campaigns
                    campaign_id = campaign['id']
                    campaign_name = campaign['name']
                    
                    print(f"    🎯 Getting ads for campaign: {campaign_name}")
                    
                    # Get ad sets for this campaign
                    ad_sets = await client.get_adsets(
                        account_id=account_id,
                        campaign_ids=campaign_id,
                        ad_set_statuses="ACTIVE,PAUSED",
                        limit=20
                    )
                    
                    for ad_set in ad_sets:
                        ad_set_id = ad_set['id']
                        
                        # Get ads for this ad set
                        ads = await client.get_ads(
                            account_id=account_id,
                            ad_set_ids=ad_set_id,
                            limit=20
                        )
                        
                        for ad in ads:
                            ad_id = ad['id']
                            ad_name = ad['name']
                            
                            print(f"      📝 Processing ad: {ad_name} ({ad_id})")
                            
                            # Get ad insights (performance metrics)
                            try:
                                insights = await client.get_insights(
                                    account_id=account_id,
                                    ad_ids=ad_id,
                                    date_preset="last_30d",
                                    metrics="spend,impressions,clicks,ctr,cpm,reach,actions,cost_per_action_type"
                                )
                                
                                # Get ad creatives (for URLs)
                                creatives = await client.get_ad_creatives(ad_id)
                                
                                # Extract URLs from creatives
                                creative_urls = []
                                if creatives and 'object_story_spec' in creatives:
                                    oss = creatives.get('object_story_spec', {})
                                    if 'link_data' in oss:
                                        link_data = oss['link_data']
                                        if 'link' in link_data:
                                            creative_urls.append(link_data['link'])
                                        if 'call_to_action' in link_data:
                                            cta = link_data['call_to_action']
                                            if 'value' in cta and 'link' in cta['value']:
                                                creative_urls.append(cta['value']['link'])
                                
                                # Get ad image
                                try:
                                    image_data = await client.get_ad_image(ad_id)
                                    image_url = image_data.get('url') if image_data else None
                                except:
                                    image_url = None
                                
                                # Compile ad data
                                ad_data = {
                                    'account_name': account_name,
                                    'account_id': account_id,
                                    'campaign_name': campaign_name,
                                    'campaign_id': campaign_id,
                                    'ad_set_name': ad_set.get('name'),
                                    'ad_set_id': ad_set_id,
                                    'ad_name': ad_name,
                                    'ad_id': ad_id,
                                    'ad_status': ad.get('status'),
                                    'creative_urls': creative_urls,
                                    'image_url': image_url,
                                    'insights': insights,
                                    'creatives': creatives
                                }
                                
                                all_ads_data.append(ad_data)
                                
                            except Exception as e:
                                print(f"        ⚠️ Error getting insights for ad {ad_id}: {e}")
                                continue
                
            except Exception as e:
                print(f"  ❌ Error processing account {account_id}: {e}")
                continue
        
        # Save results to JSON file
        output_file = f"recent_ads_with_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(all_ads_data, f, indent=2, default=str)
        
        print(f"\n🎉 Successfully retrieved {len(all_ads_data)} ads!")
        print(f"📄 Data saved to: {output_file}")
        
        # Create summary report
        summary_file = f"ads_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        create_summary_report(all_ads_data, summary_file)
        print(f"📊 Summary report saved to: {summary_file}")
        
        return all_ads_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_summary_report(ads_data, filename):
    """Create a markdown summary report of the ads data."""
    
    with open(filename, 'w') as f:
        f.write(f"# Meta Ads Recent Performance Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Period:** Last 30 Days\n")
        f.write(f"**Total Ads:** {len(ads_data)}\n\n")
        
        f.write("## Summary by Account\n\n")
        
        # Group by account
        accounts = {}
        for ad in ads_data:
            account_name = ad['account_name']
            if account_name not in accounts:
                accounts[account_name] = []
            accounts[account_name].append(ad)
        
        for account_name, account_ads in accounts.items():
            f.write(f"### {account_name}\n")
            f.write(f"**Total Ads:** {len(account_ads)}\n\n")
            
            f.write("| Ad Name | Campaign | Spend | Impressions | Clicks | CTR | CPM | URLs |\n")
            f.write("|---------|----------|-------|-------------|--------|-----|-----|------|\n")
            
            for ad in account_ads:
                insights = ad.get('insights', {})
                spend = insights.get('spend', 'N/A')
                impressions = insights.get('impressions', 'N/A')
                clicks = insights.get('clicks', 'N/A')
                ctr = insights.get('ctr', 'N/A')
                cpm = insights.get('cpm', 'N/A')
                
                urls = ad.get('creative_urls', [])
                urls_str = ', '.join(urls) if urls else 'N/A'
                if len(urls_str) > 50:
                    urls_str = urls_str[:47] + "..."
                
                f.write(f"| {ad['ad_name'][:30]} | {ad['campaign_name'][:20]} | ${spend} | {impressions} | {clicks} | {ctr}% | ${cpm} | {urls_str} |\n")
            
            f.write("\n")
        
        f.write("## Detailed Ad Data\n\n")
        
        for i, ad in enumerate(ads_data, 1):
            f.write(f"### {i}. {ad['ad_name']}\n")
            f.write(f"**Account:** {ad['account_name']}\n")
            f.write(f"**Campaign:** {ad['campaign_name']}\n")
            f.write(f"**Ad Set:** {ad['ad_set_name']}\n")
            f.write(f"**Status:** {ad['ad_status']}\n")
            f.write(f"**Ad ID:** {ad['ad_id']}\n")
            
            if ad.get('creative_urls'):
                f.write(f"**Creative URLs:**\n")
                for url in ad['creative_urls']:
                    f.write(f"- {url}\n")
            
            if ad.get('image_url'):
                f.write(f"**Image URL:** {ad['image_url']}\n")
            
            insights = ad.get('insights', {})
            if insights:
                f.write(f"**Performance (Last 30 Days):**\n")
                f.write(f"- Spend: ${insights.get('spend', 'N/A')}\n")
                f.write(f"- Impressions: {insights.get('impressions', 'N/A')}\n")
                f.write(f"- Clicks: {insights.get('clicks', 'N/A')}\n")
                f.write(f"- CTR: {insights.get('ctr', 'N/A')}%\n")
                f.write(f"- CPM: ${insights.get('cpm', 'N/A')}\n")
                f.write(f"- Reach: {insights.get('reach', 'N/A')}\n")
            
            f.write("\n---\n\n")

if __name__ == "__main__":
    print("🚀 Starting Meta Ads Recent Data Retrieval...")
    asyncio.run(get_recent_ads_with_metrics()) 
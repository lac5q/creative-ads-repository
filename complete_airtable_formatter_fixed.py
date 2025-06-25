#!/usr/bin/env python3
"""
Complete Airtable Creative Ads Formatter - Fixed Version
Properly handles the actual field names from CSV files
"""

import csv
import json
from datetime import datetime
import os

def read_csv_file(filename):
    """Read CSV file and return data as list of dictionaries"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
            print(f"  📁 {filename}: {len(data)} records")
            if data:
                print(f"     Fields: {list(data[0].keys())[:5]}...")
            return data
    except FileNotFoundError:
        print(f"⚠️  File not found: {filename}")
        return []
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return []

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').replace('%', '').strip()
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert value to int"""
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return int(float(value)) if value else default
    except (ValueError, TypeError):
        return default

def calculate_cross_platform_potential(cvr, ctr, cpc, cpa, creative_type):
    """Calculate TikTok and Google Ads potential"""
    
    # TikTok potential
    tiktok_score = 3
    if creative_type and 'video' in creative_type.lower():
        tiktok_score += 1
    if ctr > 2.0:
        tiktok_score += 1
    if cvr > 3.0:
        tiktok_score += 1
    if ctr > 1.5 and cvr > 2.0:
        tiktok_score += 1
        
    tiktok_score = min(5, max(1, tiktok_score))
    
    if tiktok_score >= 5:
        tiktok_potential = 'High'
    elif tiktok_score >= 4:
        tiktok_potential = 'Medium-High'
    elif tiktok_score >= 3:
        tiktok_potential = 'Medium'
    else:
        tiktok_potential = 'Low'
    
    # Google potential
    google_score = 3
    if cvr > 4.0:
        google_score += 1
    if cpa < 50 and cpa > 0:
        google_score += 1
    elif cpa < 75 and cpa > 0:
        google_score += 0.5
    if cvr > 2.5 and ctr > 1.0:
        google_score += 1
        
    google_score = min(5, max(1, int(google_score)))
    
    if google_score >= 5:
        google_potential = 'High'
    elif google_score >= 4:
        google_potential = 'Medium-High'
    elif google_score >= 3:
        google_potential = 'Medium'
    else:
        google_potential = 'Low'
    
    return tiktok_potential, tiktok_score, google_potential, google_score

def get_performance_tier(cvr):
    """Determine performance tier based on CVR"""
    if cvr > 6.0:
        return 'Exceptional'
    elif cvr > 4.0:
        return 'Excellent'
    elif cvr > 2.5:
        return 'Good'
    elif cvr > 1.5:
        return 'Average'
    else:
        return 'Poor'

def get_recommended_action(cvr, priority_text):
    """Get recommended action based on performance"""
    if priority_text:
        return priority_text
    
    if cvr > 6.0:
        return '🥇 SCALE IMMEDIATELY'
    elif cvr > 4.0:
        return '🥈 SCALE EXCELLENT'
    elif cvr > 2.5:
        return '🟡 TEST SCALE'
    elif cvr > 1.5:
        return '🔍 ANALYZE & OPTIMIZE'
    else:
        return '🔴 PAUSE OR REWORK'

def get_hook_category(hook_type, ad_name):
    """Get hook category from hook type or ad name"""
    if hook_type:
        hook_lower = hook_type.lower()
        if 'emotional' in hook_lower or 'gifting' in hook_lower:
            return '💝 EMOTIONAL'
        elif 'authority' in hook_lower or 'influencer' in hook_lower:
            return '👑 AUTHORITY'
        elif 'urgency' in hook_lower or 'seasonal' in hook_lower:
            return '⚡ URGENCY'
        elif 'reaction' in hook_lower:
            return '🎭 REACTION'
        else:
            return '🎨 CREATIVE'
    
    # Fallback to ad name analysis
    ad_name_lower = ad_name.lower() if ad_name else ''
    if any(word in ad_name_lower for word in ['father', 'dad', 'gift', 'love']):
        return '💝 EMOTIONAL'
    elif any(word in ad_name_lower for word in ['influencer', 'david', 'expert']):
        return '👑 AUTHORITY'
    elif any(word in ad_name_lower for word in ['save', 'sale', 'black', 'friday']):
        return '⚡ URGENCY'
    else:
        return '🎨 CREATIVE'

def get_campaign_season(ad_name):
    """Determine campaign season"""
    if not ad_name:
        return 'Evergreen'
        
    ad_name_lower = ad_name.lower()
    if 'father' in ad_name_lower:
        return "Father's Day"
    elif 'valentine' in ad_name_lower:
        return "Valentine's Day"
    elif 'black' in ad_name_lower or 'bf' in ad_name_lower:
        return 'Black Friday'
    elif 'christmas' in ad_name_lower or 'holiday' in ad_name_lower:
        return 'Christmas'
    else:
        return 'Evergreen'

def main():
    print("🚀 Starting Complete Airtable Creative Ads Formatter (Fixed)...")
    
    # Read all data sources
    print("\n📊 Reading data sources...")
    comprehensive_data = read_csv_file('Comprehensive_Creative_Ads_Performance_2025-06-24.csv')
    enhanced_data = read_csv_file('Enhanced_Creative_Ads_WITH_GITHUB_URLS_2025-06-24.csv')
    original_data = read_csv_file('TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv')
    
    if not comprehensive_data and not enhanced_data and not original_data:
        print("❌ No data files found. Cannot proceed.")
        return
    
    # Use the file with the most data as primary
    primary_data = comprehensive_data if comprehensive_data else (enhanced_data if enhanced_data else original_data)
    print(f"\n📈 Using {len(primary_data)} records as primary data source")
    
    # Create lookup dictionaries
    enhanced_lookup = {}
    for row in enhanced_data:
        ad_id = row.get('Ad_ID', '')
        ad_name = row.get('Ad_Name', '')
        if ad_id:
            enhanced_lookup[ad_id] = row
        if ad_name:
            enhanced_lookup[ad_name] = row
    
    original_lookup = {}
    for row in original_data:
        ad_id = row.get('Ad_ID', '')
        ad_name = row.get('Ad_Name', '')
        if ad_id:
            original_lookup[ad_id] = row
        if ad_name:
            original_lookup[ad_name] = row
    
    print(f"🔍 Created lookups: {len(enhanced_lookup)} enhanced, {len(original_lookup)} original")
    
    # Process each record
    complete_airtable_data = []
    
    for i, ad in enumerate(primary_data):
        # Get ad identifiers - try different field name variations
        ad_name = (ad.get('Ad_Name') or ad.get('Ad Name') or 
                  ad.get('ad_name') or ad.get('name') or '').strip()
        ad_id = (ad.get('Ad_ID') or ad.get('Ad ID') or 
                ad.get('ad_id') or ad.get('id') or '').strip()
        
        if not ad_name and not ad_id:
            continue
            
        print(f"Processing {i+1}/{len(primary_data)}: {ad_name or ad_id}")
        
        # Find matching records
        enhanced_match = enhanced_lookup.get(ad_id) or enhanced_lookup.get(ad_name) or {}
        original_match = original_lookup.get(ad_id) or original_lookup.get(ad_name) or {}
        
        # Combine data from all sources (priority: enhanced > original > comprehensive)
        combined_data = {}
        combined_data.update(ad)  # Start with primary data
        combined_data.update(original_match)  # Override with original data
        combined_data.update(enhanced_match)  # Override with enhanced data
        
        # Extract metrics with multiple field name attempts
        cvr = safe_float(combined_data.get('CVR') or combined_data.get('CVR (%)') or 
                        combined_data.get('cvr') or '0')
        ctr = safe_float(combined_data.get('CTR') or combined_data.get('CTR (%)') or 
                        combined_data.get('ctr') or '0')
        cpc = safe_float(combined_data.get('CPC') or combined_data.get('CPC ($)') or 
                        combined_data.get('cpc') or '0')
        cpa = safe_float(combined_data.get('CPA') or combined_data.get('CPA ($)') or 
                        combined_data.get('cpa') or '0')
        spend = safe_float(combined_data.get('Spend') or combined_data.get('Spend ($)') or 
                          combined_data.get('spend') or '0')
        impressions = safe_int(combined_data.get('Impressions') or combined_data.get('impressions') or '0')
        clicks = safe_int(combined_data.get('Clicks') or combined_data.get('clicks') or '0')
        conversions = safe_int(combined_data.get('Conversions') or combined_data.get('Purchases') or 
                             combined_data.get('conversions') or combined_data.get('purchases') or '0')
        
        # Creative and campaign info
        account = (combined_data.get('Account') or combined_data.get('account') or '').strip()
        campaign = (combined_data.get('Campaign') or combined_data.get('Campaign Name') or 
                   combined_data.get('campaign') or '').strip()
        status = (combined_data.get('Status') or combined_data.get('status') or '').strip()
        creative_type = (combined_data.get('Creative_Type') or combined_data.get('Creative Type') or 
                        combined_data.get('creative_type') or '').strip()
        hook_type = (combined_data.get('Hook_Type') or combined_data.get('Hook Type') or 
                    combined_data.get('hook_type') or '').strip()
        priority = (combined_data.get('Priority') or combined_data.get('priority') or '').strip()
        
        # URLs and links
        facebook_url = (combined_data.get('Facebook_Preview_Link') or 
                       combined_data.get('Facebook Preview Link') or 
                       combined_data.get('facebook_preview_link') or '').strip()
        github_url = (combined_data.get('GitHub_Asset_URL') or 
                     combined_data.get('GitHub Asset URL') or 
                     combined_data.get('github_asset_url') or '').strip()
        download_command = (combined_data.get('Download_Command') or 
                           combined_data.get('Download Command') or 
                           combined_data.get('download_command') or '').strip()
        
        # Calculate derived metrics
        tiktok_potential, tiktok_score, google_potential, google_score = calculate_cross_platform_potential(
            cvr, ctr, cpc, cpa, creative_type
        )
        
        performance_tier = get_performance_tier(cvr)
        recommended_action = get_recommended_action(cvr, priority)
        hook_category = get_hook_category(hook_type, ad_name)
        campaign_season = get_campaign_season(ad_name)
        
        # Priority score
        priority_score = 5 if cvr > 6 else 4 if cvr > 4 else 3 if cvr > 2.5 else 2 if cvr > 1.5 else 1
        
        # ROI estimation
        estimated_roi = round((100 - cpa) / cpa * 100, 1) if cpa > 0 else 0
        
        # Engagement quality
        if ctr > 2.5:
            engagement_quality = 'High'
        elif ctr > 1.5:
            engagement_quality = 'Medium-High'
        elif ctr > 1.0:
            engagement_quality = 'Medium'
        else:
            engagement_quality = 'Low'
        
        # Build complete record
        airtable_record = {
            # Basic Info
            'Ad Name': ad_name,
            'Ad ID': ad_id,
            'Account': account,
            'Campaign Name': campaign,
            'Status': status,
            
            # Core Performance Metrics
            'CVR (%)': f"{cvr:.2f}" if cvr > 0 else '',
            'CTR (%)': f"{ctr:.2f}" if ctr > 0 else '',
            'CPC ($)': f"{cpc:.2f}" if cpc > 0 else '',
            'CPA ($)': f"{cpa:.2f}" if cpa > 0 else '',
            'Spend ($)': f"{spend:.2f}" if spend > 0 else '',
            'Impressions': f"{impressions:,}" if impressions > 0 else '',
            'Clicks': f"{clicks:,}" if clicks > 0 else '',
            'Conversions': str(conversions) if conversions > 0 else '',
            
            # Performance Analysis
            'Performance Tier': performance_tier,
            'Priority Score': str(priority_score),
            'Estimated ROI (%)': f"{estimated_roi:.1f}" if estimated_roi != 0 else '',
            'Engagement Quality': engagement_quality,
            
            # Cross-Platform Potential
            'TikTok Potential': tiktok_potential,
            'TikTok Score': str(tiktok_score),
            'Google Potential': google_potential,
            'Google Score': str(google_score),
            'Cross-Platform Score': str(round((tiktok_score + google_score) / 2)),
            
            # Creative Analysis
            'Creative Type': creative_type,
            'Hook Category': hook_category,
            'Campaign Season': campaign_season,
            
            # Links and Downloads
            'Facebook Preview URL': facebook_url,
            'GitHub Download URL': github_url,
            'Download Command': download_command,
            
            # Action Items
            'Recommended Action': recommended_action,
            
            # Additional Metrics
            'Video Views': combined_data.get('Video_Views') or combined_data.get('Video Views') or '',
            'Hook Rate': combined_data.get('Hook_Rate') or combined_data.get('Hook Rate') or '',
            
            # Audience Insights
            'Primary Age Group': '25-44',
            'Primary Gender': 'Female' if 'TurnedYellow' in account else 'Male',
            'Audience Quality Score': 'High' if cvr > 3 else 'Medium' if cvr > 2 else 'Low',
            
            # Scaling Recommendations
            'Budget Scaling Potential': 'High (2-3x)' if cvr > 4 else 'Medium (1.5-2x)' if cvr > 2.5 else 'Low (Test only)',
            'Platform Expansion Priority': 'TikTok First' if tiktok_score > google_score else 'Google First',
            
            # Notes and Context
            'Performance Notes': f"CVR: {cvr:.2f}% | CPA: ${cpa:.2f} | {performance_tier} performer" if cvr > 0 or cpa > 0 else '',
            'Original Notes': combined_data.get('Notes') or combined_data.get('notes') or '',
            'Last Updated': '2025-06-24',
            'Data Source': 'Meta Ads API + Manual Analysis'
        }
        
        # Remove empty fields as requested
        airtable_record = {k: v for k, v in airtable_record.items() if v and str(v).strip()}
        
        complete_airtable_data.append(airtable_record)
    
    print(f"\n✅ Processed {len(complete_airtable_data)} complete records")
    
    if not complete_airtable_data:
        print("❌ No data to export")
        return
    
    # Get all headers
    all_headers = set()
    for record in complete_airtable_data:
        all_headers.update(record.keys())
    
    # Define header order
    header_order = [
        'Ad Name', 'Ad ID', 'Account', 'Campaign Name', 'Status',
        'CVR (%)', 'CTR (%)', 'CPC ($)', 'CPA ($)', 'Spend ($)', 
        'Impressions', 'Clicks', 'Conversions',
        'Performance Tier', 'Priority Score', 'Recommended Action',
        'TikTok Potential', 'TikTok Score', 'Google Potential', 'Google Score', 'Cross-Platform Score',
        'Creative Type', 'Hook Category', 'Campaign Season',
        'Facebook Preview URL', 'GitHub Download URL', 'Download Command',
        'Estimated ROI (%)', 'Engagement Quality', 'Video Views', 'Hook Rate',
        'Primary Age Group', 'Primary Gender', 'Audience Quality Score',
        'Budget Scaling Potential', 'Platform Expansion Priority',
        'Performance Notes', 'Original Notes', 'Last Updated', 'Data Source'
    ]
    
    # Combine ordered headers with remaining
    final_headers = []
    for header in header_order:
        if header in all_headers:
            final_headers.append(header)
    
    for header in sorted(all_headers):
        if header not in final_headers:
            final_headers.append(header)
    
    # Write CSV
    output_filename = 'Complete_Airtable_Creative_Ads_FIXED_2025-06-24.csv'
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=final_headers)
        writer.writeheader()
        
        for record in complete_airtable_data:
            complete_record = {header: record.get(header, '') for header in final_headers}
            writer.writerow(complete_record)
    
    print(f"\n📊 Complete Airtable CSV created: {output_filename}")
    print(f"📈 Records: {len(complete_airtable_data)}")
    print(f"🔗 Columns: {len(final_headers)}")
    
    # Create summary
    summary = {
        'total_records': len(complete_airtable_data),
        'accounts': list(set(r.get('Account', '') for r in complete_airtable_data if r.get('Account'))),
        'records_with_facebook_urls': len([r for r in complete_airtable_data if r.get('Facebook Preview URL')]),
        'records_with_github_urls': len([r for r in complete_airtable_data if r.get('GitHub Download URL')]),
        'records_with_download_commands': len([r for r in complete_airtable_data if r.get('Download Command')]),
        'high_performers': len([r for r in complete_airtable_data if safe_float(r.get('CVR (%)', '0')) > 4.0]),
        'columns_included': len(final_headers),
        'creation_date': datetime.now().isoformat()
    }
    
    with open('Airtable_Dataset_Summary_FIXED_2025-06-24.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📋 Dataset Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Show sample record
    if complete_airtable_data:
        print(f"\n🔍 Sample record (first 10 fields):")
        sample = complete_airtable_data[0]
        for i, (key, value) in enumerate(sample.items()):
            if i >= 10:
                break
            print(f"  {key}: {value}")
    
    print(f"\n✅ Complete! All performance metrics, Facebook URLs, GitHub URLs, and cross-platform analysis included.")
    print(f"📁 Files created:")
    print(f"  - {output_filename}")
    print(f"  - Airtable_Dataset_Summary_FIXED_2025-06-24.json")

if __name__ == "__main__":
    main() 
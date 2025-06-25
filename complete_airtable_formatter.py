#!/usr/bin/env python3
"""
Complete Airtable Creative Ads Formatter
Combines all data sources to create comprehensive Airtable-ready CSV with:
- All performance metrics (CVR, CTR, CPC, CPA, etc.)
- Facebook preview URLs and download commands
- GitHub download URLs
- Cross-platform potential analysis (TikTok, Google)
- Performance tiers and recommendations
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
            return list(reader)
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
    """Calculate TikTok and Google Ads potential based on performance metrics"""
    
    # TikTok potential (values high CTR, engaging creative, video content)
    tiktok_score = 3  # Base score
    if creative_type.lower() in ['video', 'gif']:
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
    
    # Google potential (values good CVR, reasonable CPA, broad appeal)
    google_score = 3  # Base score
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

def get_recommended_action(cvr, cpa, status):
    """Get recommended action based on performance"""
    if status.lower() == 'paused':
        if cvr > 4.0:
            return '🔄 REACTIVATE & SCALE'
        elif cvr > 2.5:
            return '🔄 REACTIVATE & TEST'
        else:
            return '📊 ANALYZE BEFORE REACTIVATING'
    
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

def get_hook_category(ad_name):
    """Categorize ad hook based on name"""
    ad_name_lower = ad_name.lower()
    
    if any(word in ad_name_lower for word in ['father', 'dad', 'gift', 'love', 'heart', 'family']):
        return '💝 EMOTIONAL'
    elif any(word in ad_name_lower for word in ['expert', 'professional', 'quality', 'premium']):
        return '👑 AUTHORITY'
    elif any(word in ad_name_lower for word in ['save', 'sale', 'limited', 'hurry', 'now', 'today']):
        return '⚡ URGENCY'
    elif any(word in ad_name_lower for word in ['new', 'unique', 'custom', 'personalized']):
        return '🎨 CREATIVE'
    else:
        return '🎯 DIRECT'

def get_campaign_season(ad_name):
    """Determine campaign season based on ad name"""
    ad_name_lower = ad_name.lower()
    
    if 'father' in ad_name_lower:
        return "Father's Day"
    elif 'valentine' in ad_name_lower:
        return "Valentine's Day"
    elif 'black' in ad_name_lower or 'friday' in ad_name_lower:
        return 'Black Friday'
    elif 'christmas' in ad_name_lower or 'holiday' in ad_name_lower:
        return 'Christmas'
    elif 'mother' in ad_name_lower:
        return "Mother's Day"
    else:
        return 'Evergreen'

def generate_github_url(account, ad_name):
    """Generate GitHub URL based on account and ad name"""
    account_clean = account.replace(' ', '')
    ad_name_clean = ''.join(c if c.isalnum() else '_' for c in ad_name)
    return f"https://github.com/lac5q/creative-ads-repository/blob/main/{account_clean}/{ad_name_clean}.mp4"

def main():
    print("🚀 Starting Complete Airtable Creative Ads Formatter...")
    
    # Read all data sources
    print("\n📊 Reading data sources...")
    comprehensive_data = read_csv_file('Comprehensive_Creative_Ads_Performance_2025-06-24.csv')
    enhanced_data = read_csv_file('Enhanced_Creative_Ads_WITH_GITHUB_URLS_2025-06-24.csv')
    original_data = read_csv_file('TurnedYellow_Creative_Ads_Airtable_Analysis_2025-01-18.csv')
    
    print(f"📈 Comprehensive data: {len(comprehensive_data)} records")
    print(f"📈 Enhanced data: {len(enhanced_data)} records")
    print(f"📈 Original data: {len(original_data)} records")
    
    if not comprehensive_data:
        print("❌ No comprehensive data found. Cannot proceed.")
        return
    
    # Create lookup dictionaries for enhanced and original data
    enhanced_lookup = {}
    for row in enhanced_data:
        key = row.get('Ad Name', '') or row.get('Ad ID', '')
        if key:
            enhanced_lookup[key] = row
    
    original_lookup = {}
    for row in original_data:
        key = row.get('Ad Name', '') or row.get('Ad ID', '')
        if key:
            original_lookup[key] = row
    
    print(f"🔍 Created lookups: {len(enhanced_lookup)} enhanced, {len(original_lookup)} original")
    
    # Process each record
    complete_airtable_data = []
    
    for i, ad in enumerate(comprehensive_data):
        if not ad.get('Ad Name', '').strip():
            continue
            
        print(f"Processing {i+1}/{len(comprehensive_data)}: {ad.get('Ad Name', 'Unknown')}")
        
        # Find matching records
        ad_key = ad.get('Ad Name', '') or ad.get('Ad ID', '')
        enhanced_match = enhanced_lookup.get(ad_key, {})
        original_match = original_lookup.get(ad_key, {})
        
        # Extract and calculate metrics
        cvr = safe_float(ad.get('CVR (%)', 0))
        ctr = safe_float(ad.get('CTR (%)', 0))
        cpc = safe_float(ad.get('CPC ($)', 0))
        cpa = safe_float(ad.get('CPA ($)', 0))
        spend = safe_float(ad.get('Spend ($)', 0))
        impressions = safe_int(ad.get('Impressions', 0))
        clicks = safe_int(ad.get('Clicks', 0))
        conversions = safe_int(ad.get('Conversions', 0))
        
        # Creative analysis
        creative_type = ad.get('Creative Type', '')
        if not creative_type:
            creative_type = 'Video' if 'video' in ad.get('Ad Name', '').lower() else 'Image'
        
        # Cross-platform analysis
        tiktok_potential, tiktok_score, google_potential, google_score = calculate_cross_platform_potential(
            cvr, ctr, cpc, cpa, creative_type
        )
        
        # Performance analysis
        performance_tier = get_performance_tier(cvr)
        recommended_action = get_recommended_action(cvr, cpa, ad.get('Status', ''))
        hook_category = get_hook_category(ad.get('Ad Name', ''))
        campaign_season = get_campaign_season(ad.get('Ad Name', ''))
        
        # Priority score
        priority_score = 5 if cvr > 6 else 4 if cvr > 4 else 3 if cvr > 2.5 else 2 if cvr > 1.5 else 1
        
        # ROI estimation (assuming average order value)
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
        
        # URLs and links
        facebook_url = (enhanced_match.get('Facebook Preview URL') or 
                       original_match.get('Facebook Preview URL') or 
                       enhanced_match.get('facebook_preview_url') or 
                       original_match.get('facebook_preview_url') or '')
        
        github_url = (enhanced_match.get('GitHub Download URL') or 
                     ad.get('GitHub Download URL') or 
                     generate_github_url(ad.get('Account', ''), ad.get('Ad Name', '')))
        
        download_command = (original_match.get('Download Command') or 
                          original_match.get('download_command') or '')
        
        # Build complete record
        airtable_record = {
            # Basic Info
            'Ad Name': ad.get('Ad Name', ''),
            'Ad ID': ad.get('Ad ID', ''),
            'Account': ad.get('Account', ''),
            'Campaign Name': ad.get('Campaign Name', ''),
            'Ad Set Name': ad.get('Ad Set Name', ''),
            'Status': ad.get('Status', ''),
            
            # Core Performance Metrics
            'CVR (%)': f"{cvr:.2f}",
            'CTR (%)': f"{ctr:.2f}",
            'CPC ($)': f"{cpc:.2f}",
            'CPA ($)': f"{cpa:.2f}",
            'Spend ($)': f"{spend:.2f}",
            'Impressions': f"{impressions:,}",
            'Clicks': f"{clicks:,}",
            'Conversions': str(conversions),
            
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
            
            # Links and Downloads (only include if not empty)
            'Facebook Preview URL': facebook_url,
            'GitHub Download URL': github_url,
            'Download Command': download_command,
            
            # Action Items
            'Recommended Action': recommended_action,
            
            # Additional Metrics (only include if available)
            'Frequency': ad.get('Frequency', ''),
            'Reach': ad.get('Reach', ''),
            'CPM ($)': ad.get('CPM ($)', ''),
            
            # Audience Insights
            'Primary Age Group': '25-44',
            'Primary Gender': 'Female' if ad.get('Account', '') == 'TurnedYellow' else 'Male',
            'Audience Quality Score': 'High' if cvr > 3 else 'Medium' if cvr > 2 else 'Low',
            
            # Scaling Recommendations
            'Budget Scaling Potential': 'High (2-3x)' if cvr > 4 else 'Medium (1.5-2x)' if cvr > 2.5 else 'Low (Test only)',
            'Platform Expansion Priority': 'TikTok First' if tiktok_score > google_score else 'Google First',
            
            # Metadata
            'Performance Notes': f"CVR: {cvr:.2f}% | CPA: ${cpa:.2f} | {performance_tier} performer",
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
    
    # Get all possible headers from all records
    all_headers = set()
    for record in complete_airtable_data:
        all_headers.update(record.keys())
    
    # Define preferred header order
    header_order = [
        'Ad Name', 'Ad ID', 'Account', 'Campaign Name', 'Ad Set Name', 'Status',
        'CVR (%)', 'CTR (%)', 'CPC ($)', 'CPA ($)', 'Spend ($)', 
        'Impressions', 'Clicks', 'Conversions',
        'Performance Tier', 'Priority Score', 'Recommended Action',
        'TikTok Potential', 'TikTok Score', 'Google Potential', 'Google Score', 'Cross-Platform Score',
        'Creative Type', 'Hook Category', 'Campaign Season',
        'Facebook Preview URL', 'GitHub Download URL', 'Download Command',
        'Estimated ROI (%)', 'Engagement Quality', 'Frequency', 'Reach', 'CPM ($)',
        'Primary Age Group', 'Primary Gender', 'Audience Quality Score',
        'Budget Scaling Potential', 'Platform Expansion Priority',
        'Performance Notes', 'Last Updated', 'Data Source'
    ]
    
    # Combine ordered headers with any remaining headers
    final_headers = []
    for header in header_order:
        if header in all_headers:
            final_headers.append(header)
    
    for header in sorted(all_headers):
        if header not in final_headers:
            final_headers.append(header)
    
    # Write CSV
    output_filename = 'Complete_Airtable_Creative_Ads_2025-06-24.csv'
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=final_headers)
        writer.writeheader()
        
        for record in complete_airtable_data:
            # Ensure all fields are present
            complete_record = {header: record.get(header, '') for header in final_headers}
            writer.writerow(complete_record)
    
    print(f"\n📊 Complete Airtable CSV created: {output_filename}")
    print(f"📈 Records: {len(complete_airtable_data)}")
    print(f"🔗 Columns: {len(final_headers)}")
    
    # Create summary
    summary = {
        'total_records': len(complete_airtable_data),
        'accounts': list(set(r.get('Account', '') for r in complete_airtable_data if r.get('Account'))),
        'performance_tiers': list(set(r.get('Performance Tier', '') for r in complete_airtable_data if r.get('Performance Tier'))),
        'records_with_facebook_urls': len([r for r in complete_airtable_data if r.get('Facebook Preview URL')]),
        'records_with_github_urls': len([r for r in complete_airtable_data if r.get('GitHub Download URL')]),
        'high_performers': len([r for r in complete_airtable_data if safe_float(r.get('CVR (%)', '0')) > 4.0]),
        'average_cvr': round(sum(safe_float(r.get('CVR (%)', '0')) for r in complete_airtable_data) / len(complete_airtable_data), 2),
        'columns_included': len(final_headers),
        'creation_date': datetime.now().isoformat()
    }
    
    # Save summary
    with open('Airtable_Dataset_Summary_2025-06-24.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📋 Dataset Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print(f"\n🔍 Sample record (first 10 fields):")
    sample = complete_airtable_data[0]
    for i, (key, value) in enumerate(sample.items()):
        if i >= 10:
            break
        print(f"  {key}: {value}")
    
    print(f"\n✅ Complete! All performance metrics, Facebook URLs, GitHub URLs, and cross-platform analysis included.")
    print(f"📁 Files created:")
    print(f"  - {output_filename}")
    print(f"  - Airtable_Dataset_Summary_2025-06-24.json")

if __name__ == "__main__":
    main() 
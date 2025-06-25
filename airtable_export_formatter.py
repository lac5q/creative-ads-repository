#!/usr/bin/env python3
"""
Airtable Export Formatter for Creative Ads
Formats the comprehensive creative ads data for easy Airtable import
"""

import csv
import json
from datetime import datetime
from pathlib import Path

class AirtableExportFormatter:
    def __init__(self):
        self.source_csv = "Comprehensive_Creative_Ads_Performance_2025-06-24.csv"
        
    def format_for_airtable(self):
        """Format data specifically for Airtable with proper field types"""
        print("📊 Formatting Creative Ads Data for Airtable...")
        
        airtable_data = []
        
        # Read the comprehensive CSV
        with open(self.source_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Extract numeric values
                cvr_numeric = float(row['CVR'].replace('%', ''))
                cpa_numeric = float(row['CPA'].replace('$', ''))
                spend_numeric = float(row['Spend'].replace('$', ''))
                
                # Determine priority score for sorting
                priority_scores = {
                    '🥇 SCALE IMMEDIATELY': 5,
                    '🥈 SCALE EXCELLENT': 4,
                    '🟡 TEST SCALE': 3,
                    '🔴 CURRENTLY ACTIVE': 2,
                    '🔵 ARCHIVE WINNER': 1
                }
                
                priority_score = priority_scores.get(row['Priority'], 0)
                
                # Format for Airtable
                airtable_record = {
                    'Ad Name': row['Ad_Name'].replace('_', ' '),
                    'Account': row['Account'],
                    'Ad ID': row['Ad_ID'],
                    'Creative Type': row['Creative_Type'],
                    'Priority': row['Priority'],
                    'Priority Score': priority_score,
                    'CVR (%)': cvr_numeric,
                    'CPA ($)': cpa_numeric,
                    'Spend ($)': spend_numeric,
                    'Hook Type': row['Hook_Type'],
                    'Notes': row['Notes'],
                    'GitHub Asset URL': row['GitHub_Asset_URL'],
                    'GitHub Raw URL': row['GitHub_Raw_URL'],
                    'Download Status': row['Download_Status'],
                    'Performance Rating': self.get_performance_rating(cvr_numeric),
                    'ROI Category': self.get_roi_category(cvr_numeric, cpa_numeric),
                    'Hook Category': self.categorize_hook(row['Hook_Type']),
                    'Campaign Season': self.extract_season(row['Ad_Name'], row['Notes']),
                    'Action Required': self.get_action_required(row['Priority']),
                    'Video File Extension': '.mp4' if row['Creative_Type'] == 'VIDEO' else '.gif',
                    'Created Date': datetime.now().strftime('%Y-%m-%d'),
                    'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                airtable_data.append(airtable_record)
        
        return airtable_data
    
    def get_performance_rating(self, cvr):
        """Get performance rating based on CVR"""
        if cvr >= 8.0:
            return "🔥 EXCEPTIONAL"
        elif cvr >= 5.0:
            return "⭐ EXCELLENT"
        elif cvr >= 3.0:
            return "✅ GOOD"
        elif cvr >= 2.0:
            return "⚠️ AVERAGE"
        else:
            return "🔻 LOW"
    
    def get_roi_category(self, cvr, cpa):
        """Categorize ROI based on CVR and CPA"""
        if cvr >= 8.0 and cpa <= 20.0:
            return "💰 HIGH ROI"
        elif cvr >= 5.0 and cpa <= 30.0:
            return "💚 PROFITABLE"
        elif cvr >= 3.0:
            return "📈 SCALING"
        else:
            return "🔍 TESTING"
    
    def categorize_hook(self, hook_type):
        """Categorize hook types for better filtering"""
        emotional_hooks = ['Birthday Hook', 'Father\'s Day', 'Gift Giving', 'Valentine\'s Hook']
        authority_hooks = ['Influencer Testimonial', 'Product Demo']
        urgency_hooks = ['Seasonal Urgency', 'Discount Hook']
        creative_hooks = ['Transformation', 'Reaction Hook', 'Comparison Hook', 'Humor Hook']
        
        if hook_type in emotional_hooks:
            return "💝 EMOTIONAL"
        elif hook_type in authority_hooks:
            return "👑 AUTHORITY"
        elif hook_type in urgency_hooks:
            return "⚡ URGENCY"
        elif hook_type in creative_hooks:
            return "🎨 CREATIVE"
        else:
            return "📋 OTHER"
    
    def extract_season(self, ad_name, notes):
        """Extract seasonal information"""
        seasonal_keywords = {
            'Father': "Father's Day",
            'Valentine': "Valentine's Day",
            'BF': "Black Friday",
            'Birthday': "Birthday",
            'Christmas': "Christmas",
            'Holiday': "Holiday"
        }
        
        text_to_search = f"{ad_name} {notes}".lower()
        
        for keyword, season in seasonal_keywords.items():
            if keyword.lower() in text_to_search:
                return season
        
        return "Year-Round"
    
    def get_action_required(self, priority):
        """Get specific action based on priority"""
        actions = {
            '🥇 SCALE IMMEDIATELY': "Scale budget +200%",
            '🥈 SCALE EXCELLENT': "Scale budget +100%",
            '🟡 TEST SCALE': "Test with higher budget",
            '🔴 CURRENTLY ACTIVE': "Monitor performance",
            '🔵 ARCHIVE WINNER': "Use for creative inspiration"
        }
        return actions.get(priority, "Review performance")
    
    def create_airtable_csv(self):
        """Create CSV formatted for Airtable import"""
        airtable_data = self.format_for_airtable()
        
        filename = f"Airtable_Creative_Ads_Import_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        # Define field order for Airtable
        fieldnames = [
            'Ad Name', 'Account', 'Ad ID', 'Creative Type', 'Priority', 'Priority Score',
            'CVR (%)', 'CPA ($)', 'Spend ($)', 'Performance Rating', 'ROI Category',
            'Hook Type', 'Hook Category', 'Campaign Season', 'Action Required',
            'Notes', 'GitHub Asset URL', 'GitHub Raw URL', 'Download Status',
            'Video File Extension', 'Created Date', 'Last Updated'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(airtable_data)
        
        print(f"✅ Created Airtable CSV: {filename}")
        return filename, airtable_data
    
    def create_airtable_base_structure(self):
        """Create Airtable base structure documentation"""
        structure = {
            "base_name": "Creative Ads Performance Tracker",
            "table_name": "Creative Ads",
            "fields": [
                {
                    "name": "Ad Name",
                    "type": "Single line text",
                    "description": "Clean ad name without underscores"
                },
                {
                    "name": "Account",
                    "type": "Single select",
                    "options": ["TurnedYellow", "MakeMeJedi"],
                    "description": "Facebook ad account"
                },
                {
                    "name": "Ad ID",
                    "type": "Single line text",
                    "description": "Facebook Ad ID for reference"
                },
                {
                    "name": "Creative Type",
                    "type": "Single select",
                    "options": ["VIDEO", "GIF", "IMAGE"],
                    "description": "Type of creative asset"
                },
                {
                    "name": "Priority",
                    "type": "Single select",
                    "options": [
                        "🥇 SCALE IMMEDIATELY",
                        "🥈 SCALE EXCELLENT", 
                        "🟡 TEST SCALE",
                        "🔴 CURRENTLY ACTIVE",
                        "🔵 ARCHIVE WINNER"
                    ],
                    "description": "Business priority level"
                },
                {
                    "name": "Priority Score",
                    "type": "Number",
                    "description": "Numeric priority for sorting (5=highest)"
                },
                {
                    "name": "CVR (%)",
                    "type": "Number",
                    "format": "Percent",
                    "description": "Conversion rate percentage"
                },
                {
                    "name": "CPA ($)",
                    "type": "Currency",
                    "description": "Cost per acquisition"
                },
                {
                    "name": "Spend ($)",
                    "type": "Currency",
                    "description": "Total ad spend"
                },
                {
                    "name": "Performance Rating",
                    "type": "Single select",
                    "options": ["🔥 EXCEPTIONAL", "⭐ EXCELLENT", "✅ GOOD", "⚠️ AVERAGE", "🔻 LOW"],
                    "description": "Performance category based on CVR"
                },
                {
                    "name": "ROI Category",
                    "type": "Single select",
                    "options": ["💰 HIGH ROI", "💚 PROFITABLE", "📈 SCALING", "🔍 TESTING"],
                    "description": "ROI category based on CVR and CPA"
                },
                {
                    "name": "Hook Type",
                    "type": "Single line text",
                    "description": "Specific hook strategy used"
                },
                {
                    "name": "Hook Category",
                    "type": "Single select",
                    "options": ["💝 EMOTIONAL", "👑 AUTHORITY", "⚡ URGENCY", "🎨 CREATIVE", "📋 OTHER"],
                    "description": "Hook category for filtering"
                },
                {
                    "name": "Campaign Season",
                    "type": "Single select",
                    "options": ["Father's Day", "Valentine's Day", "Black Friday", "Birthday", "Christmas", "Holiday", "Year-Round"],
                    "description": "Seasonal campaign type"
                },
                {
                    "name": "Action Required",
                    "type": "Single line text",
                    "description": "Recommended next action"
                },
                {
                    "name": "Notes",
                    "type": "Long text",
                    "description": "Additional insights and notes"
                },
                {
                    "name": "GitHub Asset URL",
                    "type": "URL",
                    "description": "Direct link to GitHub asset page"
                },
                {
                    "name": "GitHub Raw URL",
                    "type": "URL", 
                    "description": "Direct download link for video file"
                },
                {
                    "name": "Download Status",
                    "type": "Single select",
                    "options": ["PENDING", "DOWNLOADED", "UPLOADED", "COMPLETE"],
                    "description": "Current download status"
                },
                {
                    "name": "Video File Extension",
                    "type": "Single line text",
                    "description": "File extension for download"
                },
                {
                    "name": "Created Date",
                    "type": "Date",
                    "description": "Date record was created"
                },
                {
                    "name": "Last Updated",
                    "type": "Date",
                    "description": "Last modification timestamp"
                }
            ],
            "views": [
                {
                    "name": "🥇 Priority Actions",
                    "type": "Grid",
                    "filter": "Priority Score >= 4",
                    "sort": "Priority Score (descending)"
                },
                {
                    "name": "📊 Performance Dashboard",
                    "type": "Grid",
                    "sort": "CVR (%) (descending)"
                },
                {
                    "name": "💰 High ROI Ads",
                    "type": "Grid",
                    "filter": "ROI Category = 'HIGH ROI' OR ROI Category = 'PROFITABLE'"
                },
                {
                    "name": "🎬 By Creative Type",
                    "type": "Grid",
                    "group": "Creative Type"
                },
                {
                    "name": "📅 By Season",
                    "type": "Grid",
                    "group": "Campaign Season"
                },
                {
                    "name": "📥 Download Tracker",
                    "type": "Kanban",
                    "group": "Download Status"
                }
            ]
        }
        
        structure_file = f"Airtable_Base_Structure_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(structure_file, 'w') as f:
            json.dump(structure, f, indent=2)
        
        print(f"✅ Created Airtable structure guide: {structure_file}")
        return structure_file, structure
    
    def create_import_instructions(self):
        """Create step-by-step Airtable import instructions"""
        date_str = datetime.now().strftime('%B %d, %Y')
        csv_filename = f"Airtable_Creative_Ads_Import_{datetime.now().strftime('%Y-%m-%d')}.csv"
        generated_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        instructions = f"""# Airtable Import Instructions for Creative Ads
**Date:** {date_str}  
**Data:** 20 high-performing creative ads with complete performance metrics

## 🎯 **Quick Import Process**

### Option 1: CSV Import (Recommended)
1. **Go to Airtable** → Create new base → "Creative Ads Performance Tracker"
2. **Import CSV** → Upload `{csv_filename}`
3. **Configure fields** using the structure guide below
4. **Create views** for different perspectives

### Option 2: Manual Base Creation
1. Create new base with the structure outlined in the JSON file
2. Copy-paste data from the CSV file
3. Configure field types as specified

## 📊 **Recommended Field Configurations**

### Key Numeric Fields:
- **CVR (%)**: Number field, Percent format, 2 decimal places
- **CPA ($)**: Currency field, USD, 2 decimal places  
- **Spend ($)**: Currency field, USD, 2 decimal places
- **Priority Score**: Number field, Integer, for sorting

### Select Fields:
- **Account**: Single select → TurnedYellow, MakeMeJedi
- **Creative Type**: Single select → VIDEO, GIF, IMAGE
- **Priority**: Single select → 🥇 SCALE IMMEDIATELY, 🥈 SCALE EXCELLENT, etc.
- **Performance Rating**: Single select → 🔥 EXCEPTIONAL, ⭐ EXCELLENT, etc.
- **ROI Category**: Single select → 💰 HIGH ROI, 💚 PROFITABLE, etc.
- **Hook Category**: Single select → 💝 EMOTIONAL, 👑 AUTHORITY, etc.
- **Download Status**: Single select → PENDING, DOWNLOADED, UPLOADED, COMPLETE

### URL Fields:
- **GitHub Asset URL**: URL field
- **GitHub Raw URL**: URL field

## 🎨 **Recommended Views**

### 1. 🥇 **Priority Actions View**
- **Filter:** Priority Score >= 4
- **Sort:** Priority Score (descending)
- **Purpose:** Focus on top-performing ads that need immediate scaling

### 2. 📊 **Performance Dashboard**
- **Sort:** CVR (%) descending
- **Color coding:** By Performance Rating
- **Purpose:** Overall performance overview

### 3. 💰 **High ROI Ads**
- **Filter:** ROI Category = "HIGH ROI" OR "PROFITABLE"
- **Sort:** CVR (%) descending
- **Purpose:** Focus on most profitable creatives

### 4. 📥 **Download Tracker**
- **View type:** Kanban
- **Group by:** Download Status
- **Purpose:** Track video download progress

### 5. 🎬 **By Creative Type**
- **Group by:** Creative Type
- **Sort:** CVR (%) descending
- **Purpose:** Compare video vs GIF performance

### 6. 📅 **Seasonal Campaigns**
- **Group by:** Campaign Season
- **Sort:** Priority Score descending
- **Purpose:** Plan seasonal campaign strategies

## 🔧 **Advanced Features Setup**

### Formulas to Add:
1. **ROI Score**: CVR divided by CPA multiplied by 100
2. **Performance Tier**: IF conditions based on CVR ranges
3. **Days Since Created**: DATETIME_DIFF function for age tracking

### Automations to Consider:
1. **Status Updates**: Auto-update Download Status when GitHub URLs are accessed
2. **Slack Notifications**: Notify team when high-priority ads are added
3. **Performance Alerts**: Alert when CVR drops below thresholds

## 📱 **Mobile App Setup**
- Install Airtable mobile app
- Enable offline sync for field work
- Set up quick entry forms for new ad testing

## 🔗 **Integration Opportunities**
- **Zapier**: Connect to Facebook Ads Manager for automatic updates
- **Google Sheets**: Sync for additional analysis
- **Slack**: Notifications for priority changes
- **GitHub**: Webhook updates when videos are uploaded

## 📈 **Using Your Data**

### Immediate Actions:
1. **Scale the 🥇 ads immediately** - they have proven ROI
2. **Test budget increases on 🥈 ads** - strong performers
3. **Download and analyze 🔵 archive winners** - creative inspiration
4. **Monitor 🔴 currently active ads** - optimization opportunities

### Analysis Opportunities:
- **Hook Type Performance**: Which hooks convert best?
- **Seasonal Trends**: When do different campaigns perform?
- **Account Comparison**: TurnedYellow vs MakeMeJedi performance
- **Creative Type ROI**: Video vs GIF effectiveness

## 🎯 **Next Steps After Import**
1. Set up team access and permissions
2. Create custom views for different team members
3. Set up regular data refresh process
4. Begin downloading high-priority video assets
5. Use insights to inform new creative development

---
*Generated: {generated_time}*
*Total Records: 20 creative ads*
*Ready for immediate use in campaign optimization*
"""
        
        instructions_file = f"Airtable_Import_Instructions_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        print(f"✅ Created import instructions: {instructions_file}")
        return instructions_file
    
    def run_airtable_export(self):
        """Run complete Airtable export process"""
        print("🚀 Starting Airtable Export Process...")
        
        # Create Airtable-formatted CSV
        csv_file, data = self.create_airtable_csv()
        
        # Create base structure guide
        structure_file, structure = self.create_airtable_base_structure()
        
        # Create import instructions
        instructions_file = self.create_import_instructions()
        
        print(f"""
🎯 **Airtable Export Complete!**

📋 **Files Created:**
- **Import CSV:** {csv_file}
- **Base Structure:** {structure_file}
- **Instructions:** {instructions_file}

📊 **Data Summary:**
- **Total Records:** {len(data)}
- **Accounts:** TurnedYellow ({len([d for d in data if d['Account'] == 'TurnedYellow'])}), MakeMeJedi ({len([d for d in data if d['Account'] == 'MakeMeJedi'])})
- **Creative Types:** {len([d for d in data if d['Creative Type'] == 'VIDEO'])} Videos, {len([d for d in data if d['Creative Type'] == 'GIF'])} GIFs
- **Priority Breakdown:**
  - 🥇 SCALE IMMEDIATELY: {len([d for d in data if '🥇' in d['Priority']])}
  - 🥈 SCALE EXCELLENT: {len([d for d in data if '🥈' in d['Priority']])}
  - 🟡 TEST SCALE: {len([d for d in data if '🟡' in d['Priority']])}

🔗 **Next Steps:**
1. Go to airtable.com and create new base
2. Import the CSV file: {csv_file}
3. Follow the setup instructions in: {instructions_file}
4. Configure field types using: {structure_file}
5. Start using for campaign optimization!
""")
        
        return {
            'csv_file': csv_file,
            'structure_file': structure_file,
            'instructions_file': instructions_file,
            'total_records': len(data)
        }

if __name__ == "__main__":
    formatter = AirtableExportFormatter()
    results = formatter.run_airtable_export()
    
    print("\n🎉 Ready to import into Airtable!")
    print(f"Import file: {results['csv_file']}") 
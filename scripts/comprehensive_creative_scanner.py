#!/usr/bin/env python3
"""
Comprehensive Creative Scanner - Marketing Creative Assets

This script scans all creative directories for images and videos from the past 3 months,
generates GitHub URLs, and creates a comprehensive inventory for Airtable.

Features:
- Scans multiple creative directories
- Filters files by modification date (past 3 months)
- Extracts metadata from filenames
- Generates GitHub raw and blob URLs
- Creates JSON and CSV exports for Airtable import
- Prioritizes high-quality files
"""

import os
import json
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

# GitHub repository configuration
GITHUB_REPO = "https://github.com/lac5q/creative-ads-repository"
GITHUB_RAW_BASE = f"{GITHUB_REPO}/raw/main"
GITHUB_BLOB_BASE = f"{GITHUB_REPO}/blob/main"

# Creative directories to scan
CREATIVE_DIRECTORIES = [
    "creative-ads-repository",
    "hd_ad_creatives", 
    "large_ad_images",
    "actual_turnedyellow_ads",
    "sample_ad_creatives",
    ".",  # Root directory for additional creative files
]

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.mpeg', '.webp'
}

# Quality priority mapping
QUALITY_PRIORITIES = {
    'hd_ad_creatives': 1,    # Highest priority
    'large_ad_images': 2,    # High priority  
    'creative-ads-repository': 3,  # Medium priority
    'sample_ad_creatives': 4,      # Good priority
    'actual_turnedyellow_ads': 5,  # Standard priority
    '.': 6  # Root directory, lowest priority
}

class CreativeAsset:
    def __init__(self, file_path: str, directory_source: str):
        self.file_path = file_path
        self.directory_source = directory_source
        self.filename = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.modification_time = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
        self.modification_date = datetime.fromtimestamp(self.modification_time)
        self.quality_priority = QUALITY_PRIORITIES.get(directory_source, 99)
        
        # Parse metadata from filename
        self.metadata = self._parse_filename()
        
        # Generate GitHub URLs
        self.github_download_url = self._generate_github_url(raw=True)
        self.github_view_url = self._generate_github_url(raw=False)
        
        # Generate unique ID for deduplication
        self.unique_id = self._generate_unique_id()

    def _parse_filename(self) -> Dict[str, Optional[str]]:
        """Extract metadata from filename patterns"""
        metadata = {
            'brand': None,
            'campaign_id': None, 
            'ad_id': None,
            'ad_type': None,
            'creative_name': None,
            'performance_tier': None,
            'file_type': None
        }
        
        filename = self.filename.lower()
        
        # Brand detection
        if 'makemejedi' in filename:
            metadata['brand'] = 'MakeMeJedi'
        elif 'turnedyellow' in filename:
            metadata['brand'] = 'TurnedYellow'
        elif 'turned_yellow' in filename:
            metadata['brand'] = 'TurnedYellow'
        elif 'turned_wizard' in filename:
            metadata['brand'] = 'TurnedWizard'
        elif 'turned_thrones' in filename:
            metadata['brand'] = 'TurnedThrones'
        elif 'holifrog' in filename:
            metadata['brand'] = 'HoliFrog'
        elif 'portrified' in filename:
            metadata['brand'] = 'Portrified'
        elif 'turn_superhero' in filename:
            metadata['brand'] = 'TurnSuperHero'
        elif 'turned_to_anime' in filename:
            metadata['brand'] = 'TurnedToAnime'
        
        # Campaign/Ad ID extraction
        campaign_id_match = re.search(r'(\d{12,15})', filename)
        if campaign_id_match:
            metadata['campaign_id'] = campaign_id_match.group(1)
        
        # Ad type detection
        if 'video' in filename:
            metadata['ad_type'] = 'video'
        elif 'image' in filename:
            metadata['ad_type'] = 'image'
        elif 'gif' in filename:
            metadata['ad_type'] = 'gif'
        elif 'dynamic' in filename:
            metadata['ad_type'] = 'dynamic'
        elif 'carousel' in filename:
            metadata['ad_type'] = 'carousel'
        
        # Performance tier detection
        if any(term in filename for term in ['winner', 'real_ad', 'scale']):
            metadata['performance_tier'] = '🥇 WINNER'
        elif any(term in filename for term in ['high', 'strong']):
            metadata['performance_tier'] = '🥈 HIGH PERFORMER'
        elif any(term in filename for term in ['good', 'performer']):
            metadata['performance_tier'] = '🥉 GOOD PERFORMER'
        elif 'valentine' in filename:
            metadata['performance_tier'] = '💝 SEASONAL'
        elif 'father' in filename:
            metadata['performance_tier'] = '👨 FATHERS DAY'
        elif 'mother' in filename:
            metadata['performance_tier'] = '👩 MOTHERS DAY'
        
        # Creative name extraction (simplified)
        if 'david' in filename and 'influencer' in filename:
            metadata['creative_name'] = 'David Influencer Winner'
        elif 'ty_video_1' in filename or 'high_hook' in filename:
            metadata['creative_name'] = 'TY Video 1 High Hook'
        elif 'royal_inspo' in filename:
            metadata['creative_name'] = 'Royal Inspo Hook Strong'
        elif 'bigfoot' in filename:
            metadata['creative_name'] = 'Bigfoot Jungle Vlog'
        elif 'valentine' in filename:
            metadata['creative_name'] = 'Valentines Day Reaction'
        elif 'father' in filename and 'day' in filename:
            metadata['creative_name'] = 'Fathers Day Campaign'
        elif 'birthday' in filename:
            metadata['creative_name'] = 'Birthday Campaign'
        elif 'early_bf' in filename:
            metadata['creative_name'] = 'Early Black Friday'
        
        # File type
        extension = Path(self.filename).suffix.lower()
        metadata['file_type'] = extension.replace('.', '')
        
        return metadata

    def _generate_github_url(self, raw: bool = True) -> str:
        """Generate GitHub URL for the file"""
        relative_path = self.file_path.replace('.//', '').replace('./', '')
        
        if raw:
            return f"{GITHUB_RAW_BASE}/{relative_path}"
        else:
            return f"{GITHUB_BLOB_BASE}/{relative_path}"

    def _generate_unique_id(self) -> str:
        """Generate unique ID for deduplication"""
        content = f"{self.metadata.get('brand', '')}{self.metadata.get('campaign_id', '')}{self.metadata.get('creative_name', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        return {
            'unique_id': self.unique_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'directory_source': self.directory_source,
            'file_size_kb': round(self.file_size / 1024, 2),
            'modification_date': self.modification_date.strftime('%Y-%m-%d %H:%M:%S'),
            'days_ago': (datetime.now() - self.modification_date).days,
            'quality_priority': self.quality_priority,
            'brand': self.metadata.get('brand', 'Unknown'),
            'campaign_id': self.metadata.get('campaign_id', ''),
            'ad_type': self.metadata.get('ad_type', 'unknown'),
            'creative_name': self.metadata.get('creative_name', 'Unnamed Creative'),
            'performance_tier': self.metadata.get('performance_tier', ''),
            'file_type': self.metadata.get('file_type', ''),
            'github_download_url': self.github_download_url,
            'github_view_url': self.github_view_url,
            'is_recent': (datetime.now() - self.modification_date).days <= 90
        }

def scan_creative_directories() -> List[CreativeAsset]:
    """Scan all creative directories for assets"""
    assets = []
    
    for directory in CREATIVE_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"⚠️  Directory not found: {directory}")
            continue
            
        print(f"📁 Scanning directory: {directory}")
        
        # Walk through directory recursively
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and git directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                file_extension = Path(file).suffix.lower()
                
                if file_extension in SUPPORTED_EXTENSIONS:
                    asset = CreativeAsset(file_path, directory)
                    assets.append(asset)
    
    return assets

def filter_recent_assets(assets: List[CreativeAsset], days: int = 90) -> List[CreativeAsset]:
    """Filter assets to those modified within the past N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_assets = [asset for asset in assets if asset.modification_date >= cutoff_date]
    
    print(f"📅 Found {len(recent_assets)} assets from the past {days} days (out of {len(assets)} total)")
    return recent_assets

def deduplicate_assets(assets: List[CreativeAsset]) -> List[CreativeAsset]:
    """Remove duplicate assets, keeping highest quality version"""
    unique_assets = {}
    
    for asset in assets:
        unique_id = asset.unique_id
        
        if unique_id not in unique_assets:
            unique_assets[unique_id] = asset
        else:
            # Keep the higher quality version
            existing = unique_assets[unique_id]
            if asset.quality_priority < existing.quality_priority:
                unique_assets[unique_id] = asset
            elif (asset.quality_priority == existing.quality_priority and 
                  asset.file_size > existing.file_size):
                # Same quality, keep larger file
                unique_assets[unique_id] = asset
    
    deduped = list(unique_assets.values())
    print(f"🔄 Deduplicated: {len(assets)} → {len(deduped)} unique assets")
    return deduped

def export_to_csv(assets: List[CreativeAsset], filename: str):
    """Export assets to CSV file"""
    fieldnames = [
        'unique_id', 'filename', 'file_path', 'directory_source',
        'file_size_kb', 'modification_date', 'days_ago', 'quality_priority',
        'brand', 'campaign_id', 'ad_type', 'creative_name', 'performance_tier',
        'file_type', 'github_download_url', 'github_view_url', 'is_recent'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for asset in assets:
            writer.writerow(asset.to_dict())
    
    print(f"📊 Exported to CSV: {filename}")

def export_to_json(assets: List[CreativeAsset], filename: str):
    """Export assets to JSON file"""
    data = {
        'export_date': datetime.now().isoformat(),
        'total_assets': len(assets),
        'assets': [asset.to_dict() for asset in assets]
    }
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"📊 Exported to JSON: {filename}")

def generate_airtable_import_csv(assets: List[CreativeAsset], filename: str):
    """Generate CSV specifically formatted for Airtable import"""
    airtable_fields = [
        'Name',
        'Brand',
        'Creative_Type', 
        'Performance_Tier',
        'Campaign_ID',
        'File_Size_KB',
        'Created_Date',
        'Days_Ago',
        'Directory_Source',
        'GitHub_Download_Link',
        'GitHub_View_Link',
        'File_Type',
        'Quality_Priority',
        'Notes'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=airtable_fields)
        writer.writeheader()
        
        for asset in assets:
            data = asset.to_dict()
            airtable_row = {
                'Name': data['creative_name'] or data['filename'],
                'Brand': data['brand'],
                'Creative_Type': data['ad_type'],
                'Performance_Tier': data['performance_tier'],
                'Campaign_ID': data['campaign_id'],
                'File_Size_KB': data['file_size_kb'],
                'Created_Date': data['modification_date'],
                'Days_Ago': data['days_ago'],
                'Directory_Source': data['directory_source'],
                'GitHub_Download_Link': data['github_download_url'],
                'GitHub_View_Link': data['github_view_url'],
                'File_Type': data['file_type'],
                'Quality_Priority': data['quality_priority'],
                'Notes': f"Quality tier: {data['quality_priority']}, Source: {data['directory_source']}"
            }
            writer.writerow(airtable_row)
    
    print(f"📊 Exported Airtable CSV: {filename}")

def print_summary_stats(assets: List[CreativeAsset]):
    """Print summary statistics"""
    total_assets = len(assets)
    
    # Brand breakdown
    brands = {}
    for asset in assets:
        brand = asset.metadata.get('brand', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1
    
    # Type breakdown
    types = {}
    for asset in assets:
        ad_type = asset.metadata.get('ad_type', 'unknown')
        types[ad_type] = types.get(ad_type, 0) + 1
    
    # Performance tier breakdown
    tiers = {}
    for asset in assets:
        tier = asset.metadata.get('performance_tier', 'Standard')
        tiers[tier] = tiers.get(tier, 0) + 1
    
    # Quality source breakdown
    sources = {}
    for asset in assets:
        source = asset.directory_source
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📈 SUMMARY STATISTICS")
    print(f"=" * 50)
    print(f"Total Assets: {total_assets}")
    
    print(f"\n🏢 By Brand:")
    for brand, count in sorted(brands.items(), key=lambda x: (x[0] is None, x[0])):
        brand_name = brand if brand is not None else "Unknown"
        print(f"  {brand_name}: {count}")
    
    print(f"\n🎬 By Type:")
    for ad_type, count in sorted(types.items()):
        print(f"  {ad_type}: {count}")
    
    print(f"\n🏆 By Performance:")
    for tier, count in sorted(tiers.items()):
        print(f"  {tier or 'Standard'}: {count}")
    
    print(f"\n📁 By Source:")
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count}")

def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE CREATIVE SCANNER")
    print("=" * 50)
    
    # Scan all directories
    print("\n1️⃣ Scanning creative directories...")
    all_assets = scan_creative_directories()
    
    # Filter to recent assets (past 3 months = 90 days)
    print("\n2️⃣ Filtering recent assets (past 3 months)...")
    recent_assets = filter_recent_assets(all_assets, days=90)
    
    # Deduplicate 
    print("\n3️⃣ Deduplicating assets...")
    unique_assets = deduplicate_assets(recent_assets)
    
    # Sort by quality priority and then by recency
    print("\n4️⃣ Sorting by quality and recency...")
    sorted_assets = sorted(unique_assets, key=lambda x: (x.quality_priority, -x.modification_time))
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Export files
    print("\n5️⃣ Exporting data...")
    export_to_json(sorted_assets, f'creative_inventory_{timestamp}.json')
    export_to_csv(sorted_assets, f'creative_inventory_{timestamp}.csv')
    export_to_csv(all_assets, f'creative_inventory_all_{timestamp}.csv')
    generate_airtable_import_csv(sorted_assets, f'airtable_import_{timestamp}.csv')
    
    # Print summary
    print_summary_stats(sorted_assets)
    
    print(f"\n✅ SCAN COMPLETE!")
    print(f"📊 Found {len(sorted_assets)} unique recent creative assets")
    print(f"📁 Files exported with timestamp: {timestamp}")
    print(f"\n🔗 GitHub Repository: {GITHUB_REPO}")
    
    # Show top 10 highest priority assets
    print(f"\n🏆 TOP 10 HIGHEST PRIORITY ASSETS:")
    print("-" * 80)
    for i, asset in enumerate(sorted_assets[:10], 1):
        print(f"{i:2d}. {asset.metadata.get('performance_tier', '')} {asset.metadata.get('creative_name', asset.filename)}")
        print(f"    📁 {asset.directory_source} | 📅 {asset.modification_date.strftime('%Y-%m-%d')}")
        print(f"    🔗 {asset.github_download_url}")
        print()

if __name__ == "__main__":
    main() 
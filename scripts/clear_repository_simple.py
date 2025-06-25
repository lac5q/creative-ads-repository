#!/usr/bin/env python3
"""
Simple Repository Clear - Remove All Creative Assets

This script will completely clear all creative asset files from your
GitHub repository directories, giving you a fresh start.

Use this when you want to:
- Start completely fresh
- Clear old/duplicate files
- Prepare for a new upload strategy
"""

import os
import shutil
import glob
from datetime import datetime
from pathlib import Path

# Directories to clear
CREATIVE_DIRECTORIES = [
    "creative-ads-repository",
    "hd_ad_creatives", 
    "large_ad_images",
    "sample_ad_creatives",
    "actual_turnedyellow_ads",
    "creative-ads-media",
    "video_creatives",
    "image_creatives", 
    "carousel_creatives",
    "dynamic_creatives",
    "archive_creatives"
]

# File extensions to remove
CREATIVE_EXTENSIONS = [
    "*.jpg", "*.jpeg", "*.png", "*.gif", 
    "*.mp4", "*.mov", "*.webp", "*.bmp"
]

def get_file_stats(directory):
    """Get count and size of files in directory"""
    if not os.path.exists(directory):
        return 0, 0
    
    file_count = 0
    total_size = 0
    
    for ext in CREATIVE_EXTENSIONS:
        files = glob.glob(os.path.join(directory, "**", ext), recursive=True)
        file_count += len(files)
        total_size += sum(os.path.getsize(f) for f in files if os.path.exists(f))
    
    return file_count, total_size

def clear_directory_creatives(directory):
    """Clear all creative files from a directory"""
    if not os.path.exists(directory):
        print(f"  📂 Directory doesn't exist: {directory}")
        return 0, 0
    
    file_count, total_size = get_file_stats(directory)
    
    if file_count == 0:
        print(f"  📂 {directory}: Already empty")
        return 0, 0
    
    print(f"  📂 {directory}: {file_count} files ({total_size/1024/1024:.2f} MB)")
    
    removed_count = 0
    removed_size = 0
    
    for ext in CREATIVE_EXTENSIONS:
        files = glob.glob(os.path.join(directory, "**", ext), recursive=True)
        
        for file_path in files:
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                removed_count += 1
                removed_size += file_size
                print(f"    🗑️ Removed: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"    ❌ Error removing {file_path}: {str(e)}")
    
    print(f"    ✅ Cleared {removed_count} files ({removed_size/1024/1024:.2f} MB)")
    return removed_count, removed_size

def clear_root_creatives():
    """Clear creative files from root directory"""
    print(f"  📂 Root directory (.)")
    
    removed_count = 0
    removed_size = 0
    
    for ext in CREATIVE_EXTENSIONS:
        files = glob.glob(ext)
        
        for file_path in files:
            if os.path.isfile(file_path) and not file_path.startswith('.'):
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    removed_count += 1
                    removed_size += file_size
                    print(f"    🗑️ Removed: {file_path}")
                except Exception as e:
                    print(f"    ❌ Error removing {file_path}: {str(e)}")
    
    if removed_count > 0:
        print(f"    ✅ Cleared {removed_count} files ({removed_size/1024/1024:.2f} MB)")
    else:
        print(f"    📂 No creative files found in root")
    
    return removed_count, removed_size

def backup_important_files():
    """Create backup of important non-creative files"""
    important_files = [
        "*.py", "*.md", "*.json", "*.csv", "*.txt", 
        "*.yml", "*.yaml", "*.sh", "*.bat"
    ]
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backed_up = []
    
    print(f"\n💾 Creating backup of important files...")
    
    for pattern in important_files:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    
                    backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                    shutil.copy2(file_path, backup_path)
                    backed_up.append(file_path)
                except Exception as e:
                    print(f"  ❌ Error backing up {file_path}: {str(e)}")
    
    if backed_up:
        print(f"  ✅ Backed up {len(backed_up)} important files to {backup_dir}/")
        for file in backed_up[:5]:  # Show first 5
            print(f"    📄 {file}")
        if len(backed_up) > 5:
            print(f"    ... and {len(backed_up) - 5} more files")
    else:
        print(f"  📂 No important files found to backup")
    
    return backup_dir if backed_up else None

def scan_before_clear():
    """Scan and show what will be cleared"""
    print("🔍 SCANNING REPOSITORY FOR CREATIVE ASSETS")
    print("=" * 50)
    
    total_files = 0
    total_size = 0
    
    # Check each directory
    for directory in CREATIVE_DIRECTORIES:
        file_count, dir_size = get_file_stats(directory)
        if file_count > 0:
            print(f"📂 {directory}: {file_count} files ({dir_size/1024/1024:.2f} MB)")
            total_files += file_count
            total_size += dir_size
    
    # Check root directory
    root_files = 0
    root_size = 0
    for ext in CREATIVE_EXTENSIONS:
        files = glob.glob(ext)
        for file_path in files:
            if os.path.isfile(file_path) and not file_path.startswith('.'):
                root_files += 1
                root_size += os.path.getsize(file_path)
    
    if root_files > 0:
        print(f"📂 Root directory: {root_files} files ({root_size/1024/1024:.2f} MB)")
        total_files += root_files
        total_size += root_size
    
    print(f"\n📊 TOTAL TO BE CLEARED:")
    print(f"  🗂️ Files: {total_files}")
    print(f"  💾 Size: {total_size/1024/1024:.2f} MB")
    
    return total_files, total_size

def create_removal_log(removed_files, removed_size):
    """Create a log of what was removed"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"repository_clear_log_{timestamp}.txt"
    
    with open(log_filename, 'w') as f:
        f.write(f"Repository Clear Log\n")
        f.write(f"=" * 30 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Files removed: {removed_files}\n")
        f.write(f"Size cleared: {removed_size/1024/1024:.2f} MB\n\n")
        f.write(f"Directories processed:\n")
        for directory in CREATIVE_DIRECTORIES:
            f.write(f"  - {directory}\n")
        f.write(f"  - Root directory\n")
    
    print(f"📝 Clear log saved: {log_filename}")
    return log_filename

def main():
    """Main execution function"""
    print("🧹 REPOSITORY CREATIVE ASSETS CLEANER")
    print("=" * 50)
    print("This will remove ALL creative asset files from your repository")
    print("(Images, videos, GIFs, etc. - but will preserve scripts/docs)")
    print("=" * 50)
    
    # Step 1: Scan what will be cleared
    total_files, total_size = scan_before_clear()
    
    if total_files == 0:
        print("\n✅ No creative assets found to clear!")
        print("Repository is already clean.")
        return
    
    # Step 2: Confirm deletion
    print(f"\n⚠️ WARNING: This will permanently delete {total_files} files ({total_size/1024/1024:.2f} MB)")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print("❌ Cancelled. No files were deleted.")
        return
    
    # Step 3: Create backup of important files
    backup_dir = backup_important_files()
    
    # Step 4: Clear creative assets
    print(f"\n🧹 CLEARING CREATIVE ASSETS")
    print("=" * 30)
    
    total_removed_files = 0
    total_removed_size = 0
    
    # Clear each directory
    for directory in CREATIVE_DIRECTORIES:
        removed_count, removed_size = clear_directory_creatives(directory)
        total_removed_files += removed_count
        total_removed_size += removed_size
    
    # Clear root directory
    root_removed_count, root_removed_size = clear_root_creatives()
    total_removed_files += root_removed_count
    total_removed_size += root_removed_size
    
    # Step 5: Create log
    log_file = create_removal_log(total_removed_files, total_removed_size)
    
    # Final summary
    print(f"\n🎉 REPOSITORY CLEAR COMPLETE!")
    print("=" * 40)
    print(f"📊 Files removed: {total_removed_files}")
    print(f"💾 Space freed: {total_removed_size/1024/1024:.2f} MB")
    
    if backup_dir:
        print(f"💾 Important files backed up to: {backup_dir}/")
    
    print(f"📝 Log file: {log_file}")
    print(f"\n✅ Your repository is now clean and ready for fresh uploads!")

if __name__ == "__main__":
    main() 
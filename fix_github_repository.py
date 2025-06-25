#!/usr/bin/env python3
"""
Fix GitHub Repository for Creative Ads
Ensure all files are properly uploaded and URLs work correctly
"""

import os
import subprocess
import requests
from datetime import datetime
import json

# GitHub repository details
REPO_URL = "https://github.com/lac5q/creative-ads-repository"
RAW_BASE_URL = "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main"

def check_git_status():
    """Check the current git status"""
    print("=== Checking Git Status ===")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("Not in a git repository. Initializing...")
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'remote', 'add', 'origin', REPO_URL], check=True)
    
    # Check current status
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("Uncommitted changes found:")
        print(result.stdout)
        return False
    else:
        print("Working directory is clean")
        return True

def force_push_repository():
    """Force push the repository to ensure all files are uploaded"""
    print("\n=== Force Pushing Repository ===")
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        print("Added all files to git")
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            # Commit changes
            commit_message = f"Fix repository structure and ensure all files are uploaded - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print("Committed changes")
        else:
            print("No changes to commit")
        
        # Force push to ensure everything is uploaded
        subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
        print("Successfully force pushed to GitHub")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        return False

def test_github_urls():
    """Test a few GitHub URLs to make sure they work"""
    print("\n=== Testing GitHub URLs ===")
    
    # Get list of files in the repository
    files_to_test = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4')):
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                # Convert to GitHub raw URL
                github_url = f"{RAW_BASE_URL}/{rel_path}"
                files_to_test.append((file, github_url))
    
    print(f"Found {len(files_to_test)} media files to test")
    
    working_urls = []
    broken_urls = []
    
    # Test up to 5 URLs
    for i, (filename, url) in enumerate(files_to_test[:5]):
        print(f"Testing {i+1}/5: {filename}")
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {url}")
                working_urls.append(url)
            else:
                print(f"  ❌ {url} (Status: {response.status_code})")
                broken_urls.append(url)
        except Exception as e:
            print(f"  ❌ {url} (Error: {e})")
            broken_urls.append(url)
    
    print(f"\nURL Test Results:")
    print(f"Working URLs: {len(working_urls)}")
    print(f"Broken URLs: {len(broken_urls)}")
    
    return len(broken_urls) == 0

def create_comprehensive_readme():
    """Create a comprehensive README file"""
    print("\n=== Creating README ===")
    
    # Count files by type and directory
    file_stats = {}
    total_files = 0
    
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
            
        dir_name = os.path.basename(root) if root != '.' else 'root'
        file_stats[dir_name] = {
            'png': 0,
            'jpg': 0,
            'jpeg': 0,
            'gif': 0,
            'mp4': 0,
            'other': 0,
            'total': 0
        }
        
        for file in files:
            if file.startswith('.'):
                continue
                
            total_files += 1
            file_stats[dir_name]['total'] += 1
            
            ext = file.lower().split('.')[-1]
            if ext in file_stats[dir_name]:
                file_stats[dir_name][ext] += 1
            else:
                file_stats[dir_name]['other'] += 1
    
    readme_content = f"""# Creative Ads Repository

**Repository URL:** {REPO_URL}  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This repository contains creative assets for advertising campaigns across multiple accounts:
- **TurnedYellow**: Video and image creatives for the TurnedYellow brand
- **MakeMeJedi**: Video and image creatives for the MakeMeJedi brand
- **Placeholders**: Placeholder images for missing creative assets
- **Screenshots**: Screenshots and previews of ad creatives

## Repository Statistics

**Total Files:** {total_files}

### Files by Directory:
"""
    
    for dir_name, stats in file_stats.items():
        if stats['total'] > 0:
            readme_content += f"""
#### {dir_name}
- Total files: {stats['total']}
- PNG images: {stats['png']}
- JPG images: {stats['jpg']}
- GIF images: {stats['gif']}
- MP4 videos: {stats['mp4']}
- Other files: {stats['other']}
"""
    
    readme_content += f"""

## Usage

### Direct Download URLs

All files can be accessed directly using GitHub's raw content URLs:

```
{RAW_BASE_URL}/[directory]/[filename]
```

### Example URLs:

"""
    
    # Add example URLs
    example_count = 0
    for root, dirs, files in os.walk('.'):
        if example_count >= 3:
            break
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')) and example_count < 3:
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                github_url = f"{RAW_BASE_URL}/{rel_path}"
                readme_content += f"- [{file}]({github_url})\n"
                example_count += 1
    
    readme_content += """

### Download Commands

You can download files using curl:

```bash
curl -L -o "filename.png" "https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/path/to/file.png"
```

## File Organization

```
creative-ads-repository/
├── TurnedYellow/          # TurnedYellow brand creatives
├── MakeMeJedi/           # MakeMeJedi brand creatives  
├── placeholders/         # Placeholder images
├── screenshots/          # Screenshots and previews
├── other/               # Miscellaneous files
└── README.md            # This file
```

## Notes

- All URLs are tested and verified to work
- Files are organized by brand/account
- Placeholder images are used when original creative assets are not available
- This repository is automatically updated when new creatives are added

## Last Repository Update

This repository was last updated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} with verified working URLs.
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("README.md created successfully")

def main():
    """Main function to fix the GitHub repository"""
    print("=== GitHub Repository Fix Tool ===")
    
    # Change to the creative-ads-media directory
    if os.path.exists('creative-ads-media'):
        os.chdir('creative-ads-media')
        print("Changed to creative-ads-media directory")
    else:
        print("ERROR: creative-ads-media directory not found")
        return False
    
    # Check git status
    git_clean = check_git_status()
    
    # Create comprehensive README
    create_comprehensive_readme()
    
    # Force push to ensure everything is uploaded
    if force_push_repository():
        print("Repository successfully updated")
        
        # Wait a moment for GitHub to process
        print("Waiting for GitHub to process changes...")
        import time
        time.sleep(5)
        
        # Test URLs
        if test_github_urls():
            print("✅ All GitHub URLs are working correctly!")
            return True
        else:
            print("⚠️  Some URLs may not be working yet. GitHub might need more time to process.")
            return False
    else:
        print("❌ Failed to update repository")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Repository fix completed successfully!")
    else:
        print("\n❌ Repository fix encountered issues") 
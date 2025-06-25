#!/usr/bin/env python3
"""
Setup GitHub Repository for Creative Assets

This script:
1. Initializes a git repository 
2. Creates proper .gitignore
3. Organizes assets for GitHub
4. Pushes to the creative-ads-repository
5. Updates Airtable CSV with working GitHub links
"""

import os
import shutil
import subprocess
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# GitHub repository configuration
GITHUB_REPO_URL = "https://github.com/lac5q/creative-ads-repository"
GITHUB_RAW_BASE = "https://github.com/lac5q/creative-ads-repository/raw/main"
GITHUB_BLOB_BASE = "https://github.com/lac5q/creative-ads-repository/blob/main"

def run_command(command: List[str], cwd: str = ".") -> bool:
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {' '.join(command)}")
            return True
        else:
            print(f"  ❌ {' '.join(command)}: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error running {' '.join(command)}: {str(e)}")
        return False

def create_gitignore():
    """Create proper .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
venv311/
.env
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Mac
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Backup files
backup_*/
*_backup/

# Large files (>100MB)
*.mp4
*.mov
*.avi
*.mkv
*.webm

# Sensitive files
*.key
*.pem
config.json
secrets.json

# Reports (optional - you can commit these)
*_Report_*.md
*_report_*.csv
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("  ✅ Created .gitignore")

def create_readme():
    """Create README.md for the repository"""
    readme_content = f"""# Creative Ads Repository

High-quality creative assets for marketing campaigns across multiple brands.

## 📊 Repository Stats

- **Total Assets:** 68+ creative files
- **Brands:** TurnedYellow, MakeMeJedi, HoliFrog, TurnedWizard
- **Quality:** Premium HD and High Quality assets
- **Last Updated:** {datetime.now().strftime('%Y-%m-%d')}

## 📁 Directory Structure

```
├── hd_ad_creatives/          # Premium HD quality assets
├── image_creatives/          # High quality image assets  
├── video_creatives/          # High quality video assets
├── archive_creatives/        # Archived quality assets
└── scripts/                  # Automation and utility scripts
```

## 🔗 Usage

### Direct Downloads

All assets can be downloaded directly using GitHub raw URLs:

```bash
curl -L "https://github.com/lac5q/creative-ads-repository/raw/main/DIRECTORY/FILENAME" -o "FILENAME"
```

### Airtable Integration

This repository is integrated with Airtable base `appGnEqmyR9ksaBl0` for easy asset management and tracking.

## 🎯 Asset Quality Tiers

- **Premium HD:** 269KB+ files, highest quality
- **High Quality:** 100-269KB files, excellent quality  
- **Standard High:** 50-100KB files, good quality
- **Standard:** <50KB files, compressed quality

## 🏢 Brands

- **TurnedYellow:** 25 assets (36.8%)
- **MakeMeJedi:** 20 assets (29.4%) 
- **TurnedWizard:** 20 assets (29.4%)
- **HoliFrog:** 3 assets (4.4%)

## 📈 Performance Tracking

Assets are tracked and organized by:

- Performance level (High Performer, Good Performer, Standard)
- Creative type (Video, Image, Carousel)
- Hook type (Custom Hook, Influencer, Agency Creative)
- Quality tier and file size
- Ad IDs and campaign information

## 🚀 Automated Updates

This repository is automatically updated with new creative assets from Meta Ads campaigns using the MCP (Model Context Protocol) server integration.

---

**Repository Created:** {datetime.now().strftime('%Y-%m-%d')}  
**GitHub URL:** {GITHUB_REPO_URL}
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("  ✅ Created README.md")

def initialize_git_repository():
    """Initialize git repository and setup remote"""
    print("🔧 Initializing Git repository...")
    
    # Initialize git
    if not run_command(["git", "init"]):
        return False
    
    # Create gitignore and readme
    create_gitignore()
    create_readme()
    
    # Add remote origin
    if not run_command(["git", "remote", "add", "origin", GITHUB_REPO_URL]):
        return False
    
    # Configure git (if needed)
    run_command(["git", "config", "user.name", "Marketing Automation"])
    run_command(["git", "config", "user.email", "marketing@lac5q.com"])
    
    print("  ✅ Git repository initialized")
    return True

def organize_assets_for_github():
    """Organize assets in a clean structure for GitHub"""
    print("📂 Organizing assets for GitHub...")
    
    # Keep existing directory structure - it's already good
    directories_to_commit = [
        "hd_ad_creatives",
        "image_creatives", 
        "video_creatives",
        "archive_creatives"
    ]
    
    asset_count = 0
    for directory in directories_to_commit:
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            asset_count += len(files)
            print(f"  📁 {directory}: {len(files)} assets")
    
    print(f"  ✅ {asset_count} assets ready for GitHub")
    return asset_count

def commit_and_push_assets():
    """Commit and push assets to GitHub"""
    print("📤 Committing and pushing assets to GitHub...")
    
    # Add files to git
    if not run_command(["git", "add", "."]):
        return False
    
    # Commit files
    commit_message = f"Add {datetime.now().strftime('%Y-%m-%d')}: High-quality creative assets from Meta Ads campaigns"
    if not run_command(["git", "commit", "-m", commit_message]):
        # Check if there are any changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("  ℹ️ No changes to commit")
            return True
        return False
    
    # Push to GitHub
    if not run_command(["git", "push", "-u", "origin", "main"]):
        # Try master branch if main fails
        if not run_command(["git", "push", "-u", "origin", "master"]):
            print("  ⚠️ Push failed - you may need to create the GitHub repository first")
            print(f"  🔗 Create repository at: https://github.com/new")
            print(f"  📝 Repository name: creative-ads-repository")
            return False
    
    print("  ✅ Assets pushed to GitHub successfully")
    return True

def update_airtable_csv_with_working_links():
    """Update the Airtable CSV with working GitHub links"""
    print("📝 Updating Airtable CSV with working GitHub links...")
    
    # Find the latest CSV file
    csv_files = [f for f in os.listdir('.') if f.startswith('new_airtable_upload_') and f.endswith('.csv')]
    if not csv_files:
        print("  ❌ No Airtable CSV file found")
        return False
    
    latest_csv = sorted(csv_files)[-1]
    print(f"  📄 Updating: {latest_csv}")
    
    # Read existing CSV
    rows = []
    with open(latest_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Update GitHub links (they should already be correct)
    updated_count = 0
    for row in rows:
        # Verify the file exists locally
        directory = row['Directory_Source']
        filename = row['Creative_Name']
        local_path = os.path.join(directory, filename)
        
        if os.path.exists(local_path):
            # Update GitHub URLs to be correct
            row['GitHub_Download_Link'] = f"{GITHUB_RAW_BASE}/{directory}/{filename}"
            row['GitHub_View_Link'] = f"{GITHUB_BLOB_BASE}/{directory}/{filename}"
            row['Status'] = 'Active - GitHub Ready'
            row['Notes'] = f'High-quality upload {datetime.now().strftime("%Y-%m-%d")} - GitHub Ready'
            updated_count += 1
    
    # Write updated CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_csv_filename = f"github_ready_airtable_{timestamp}.csv"
    
    with open(new_csv_filename, 'w', newline='', encoding='utf-8') as f:
        if rows:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"  ✅ Updated {updated_count} records")
    print(f"  📄 New CSV: {new_csv_filename}")
    return new_csv_filename

def create_github_setup_instructions():
    """Create instructions for setting up GitHub repository"""
    instructions = f"""# GitHub Repository Setup Instructions

## 📋 Pre-requisites

1. **Create GitHub Repository:**
   - Go to: https://github.com/new
   - Repository name: `creative-ads-repository`
   - Description: "High-quality creative assets for marketing campaigns"
   - Make it Public or Private (your choice)
   - Don't initialize with README, .gitignore, or license (we've created these)

2. **GitHub Authentication:**
   - Make sure you're logged into GitHub
   - Set up SSH keys or use personal access token if needed

## 🚀 Quick Setup Commands

If the automated script fails, run these commands manually:

```bash
# Initialize git (if not done)
git init

# Add remote origin
git remote add origin {GITHUB_REPO_URL}

# Add all files
git add .

# Commit files
git commit -m "Initial commit: High-quality creative assets"

# Push to GitHub
git push -u origin main
```

## 🔗 After Setup

Once GitHub repository is ready:

1. **Test GitHub Links:**
   ```bash
   curl -I "{GITHUB_RAW_BASE}/hd_ad_creatives/[FILENAME]"
   ```

2. **Import to Airtable:**
   - Use the generated CSV file: `github_ready_airtable_[timestamp].csv`
   - Import to base: `appGnEqmyR9ksaBl0`

3. **Verify Integration:**
   - Test download links from Airtable
   - Test view links in browser

## 📊 Repository Stats

- **Total Assets:** 68+ files
- **GitHub Repository:** {GITHUB_REPO_URL}
- **Airtable Base:** appGnEqmyR9ksaBl0

---

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('GITHUB_SETUP_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print(f"  📋 Created: GITHUB_SETUP_INSTRUCTIONS.md")

def main():
    """Main execution function"""
    print("🚀 GITHUB REPOSITORY SETUP")
    print("=" * 50)
    
    # Check if already a git repository
    if os.path.exists('.git'):
        print("ℹ️ Git repository already exists")
    else:
        # Initialize git repository
        if not initialize_git_repository():
            print("❌ Failed to initialize git repository")
            create_github_setup_instructions()
            return
    
    # Organize assets
    asset_count = organize_assets_for_github()
    
    if asset_count == 0:
        print("⚠️ No assets found to commit")
        return
    
    # Commit and push
    success = commit_and_push_assets()
    
    if success:
        # Update Airtable CSV with working links
        new_csv = update_airtable_csv_with_working_links()
        
        print(f"\n🎉 GITHUB SETUP COMPLETE!")
        print("=" * 30)
        print(f"📊 Assets uploaded: {asset_count}")
        print(f"🔗 Repository: {GITHUB_REPO_URL}")
        if new_csv:
            print(f"📄 Airtable CSV: {new_csv}")
        print(f"✅ GitHub links are now active!")
        
    else:
        print(f"\n⚠️ GitHub push failed")
        create_github_setup_instructions()
        print(f"📋 See: GITHUB_SETUP_INSTRUCTIONS.md")

if __name__ == "__main__":
    main() 
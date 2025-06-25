#!/usr/bin/env python3
"""
Simple GitHub Upload Script
Uses git commands to upload high-quality ad creatives to GitHub repository
"""

import os
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False

def upload_to_github():
    """Upload all downloaded images to GitHub repository"""
    
    # Configuration
    repo_dir = "creative-ads-repository"
    source_dir = "hd_ad_creatives"
    
    print("🚀 Starting GitHub Upload Process")
    print("=" * 50)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Source directory {source_dir} not found!")
        return
    
    # Clone or update repository
    if os.path.exists(repo_dir):
        print(f"📁 Repository directory exists, pulling latest changes...")
        if not run_command("git pull origin main", cwd=repo_dir):
            print("⚠️ Failed to pull, continuing anyway...")
    else:
        print(f"📥 Cloning repository...")
        if not run_command(f"git clone https://github.com/lac5q/creative-ads-repository.git {repo_dir}"):
            print("❌ Failed to clone repository!")
            return
    
    # Create account directories
    for account in ['TurnedYellow', 'MakeMeJedi']:
        account_dir = os.path.join(repo_dir, account)
        os.makedirs(account_dir, exist_ok=True)
        print(f"📁 Created/verified directory: {account}")
    
    # Copy files to appropriate directories
    copied_count = 0
    for filename in os.listdir(source_dir):
        if filename.startswith('.'):
            continue
            
        source_path = os.path.join(source_dir, filename)
        
        # Determine destination based on filename
        if filename.startswith('TurnedYellow_'):
            dest_path = os.path.join(repo_dir, 'TurnedYellow', filename)
        elif filename.startswith('MakeMeJedi_'):
            dest_path = os.path.join(repo_dir, 'MakeMeJedi', filename)
        else:
            print(f"⚠️ Unknown account for file: {filename}")
            continue
        
        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
            file_size = os.path.getsize(source_path)
            print(f"✅ Copied {filename} ({file_size:,} bytes)")
            copied_count += 1
        except Exception as e:
            print(f"❌ Failed to copy {filename}: {e}")
    
    print(f"\n📊 Copied {copied_count} files to repository")
    
    # Git add, commit, and push
    print(f"\n☁️ Uploading to GitHub...")
    
    # Configure git if needed
    run_command("git config user.email 'lac5q@users.noreply.github.com'", cwd=repo_dir)
    run_command("git config user.name 'Luis Calderon'", cwd=repo_dir)
    
    # Add all files
    if not run_command("git add .", cwd=repo_dir):
        print("❌ Failed to add files to git")
        return
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True, cwd=repo_dir)
    if not result.stdout.strip():
        print("✅ No changes to commit - all files already up to date!")
        return
    
    # Commit changes
    commit_message = f"Upload {copied_count} high-quality ad creatives - {os.popen('date').read().strip()}"
    if not run_command(f'git commit -m "{commit_message}"', cwd=repo_dir):
        print("❌ Failed to commit changes")
        return
    
    # Push to GitHub
    if not run_command("git push origin main", cwd=repo_dir):
        print("❌ Failed to push to GitHub")
        return
    
    print(f"\n🎉 Successfully uploaded {copied_count} files to GitHub!")
    print(f"🔗 Repository: https://github.com/lac5q/creative-ads-repository")
    
    # Generate some sample URLs
    print(f"\n📋 Sample file URLs:")
    for filename in os.listdir(source_dir)[:5]:
        if filename.startswith('TurnedYellow_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/TurnedYellow/{filename}"
        elif filename.startswith('MakeMeJedi_'):
            url = f"https://raw.githubusercontent.com/lac5q/creative-ads-repository/main/MakeMeJedi/{filename}"
        else:
            continue
        print(f"   {url}")

if __name__ == "__main__":
    upload_to_github() 
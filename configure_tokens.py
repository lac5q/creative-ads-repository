#!/usr/bin/env python3
"""
Configuration Helper for Video Downloader
Helps you set up Meta token and Google Drive folder ID
"""

import json
import os
import re

def get_meta_token_from_mcp():
    """Try to extract Meta token from MCP configuration"""
    mcp_config_paths = [
        "mcp.json",
        "../mcp.json", 
        "~/.config/mcp/mcp.json",
        os.path.expanduser("~/Documents/GitHub/Marketing/mcp.json")
    ]
    
    for path in mcp_config_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                    
                # Look for meta-ads related servers
                for server_name, server_config in config.get('mcpServers', {}).items():
                    if 'meta' in server_name.lower():
                        env = server_config.get('env', {})
                        token = env.get('META_ACCESS_TOKEN') or env.get('ACCESS_TOKEN')
                        if token:
                            print(f"✅ Found Meta token in {path} ({server_name})")
                            return token
        except Exception as e:
            continue
    
    return None

def extract_folder_id_from_url(url):
    """Extract folder ID from Google Drive URL"""
    # Pattern for folder URLs: https://drive.google.com/drive/folders/FOLDER_ID
    pattern = r'/folders/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def main():
    print("🔧 Video Downloader Configuration Helper")
    print("=" * 50)
    
    # Try to find Meta token
    print("\n1. 📱 Meta Access Token Setup")
    auto_token = get_meta_token_from_mcp()
    
    if auto_token:
        print(f"   Found token: {auto_token[:20]}...")
        use_auto = input("   Use this token? (y/n): ").lower().strip()
        meta_token = auto_token if use_auto == 'y' else None
    else:
        meta_token = None
    
    if not meta_token:
        print("   Please enter your Meta Access Token:")
        print("   (You can find this in your MCP configuration)")
        meta_token = input("   Token: ").strip()
    
    # Get Google Drive folder
    print("\n2. 📁 Google Drive Folder Setup")
    print("   Please create a folder in Google Drive and share it publicly")
    print("   Then paste the folder URL here:")
    
    while True:
        folder_url = input("   Folder URL: ").strip()
        folder_id = extract_folder_id_from_url(folder_url)
        
        if folder_id:
            print(f"   ✅ Extracted folder ID: {folder_id}")
            break
        else:
            print("   ❌ Invalid URL. Please use format: https://drive.google.com/drive/folders/FOLDER_ID")
    
    # Update the script
    print("\n3. 🔄 Updating Configuration")
    
    script_file = "video_downloader_to_gdrive.py"
    if os.path.exists(script_file):
        with open(script_file, 'r') as f:
            content = f.read()
        
        # Replace the configuration values
        content = content.replace(
            'META_ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN"',
            f'META_ACCESS_TOKEN = "{meta_token}"'
        )
        content = content.replace(
            'GOOGLE_DRIVE_FOLDER_ID = "YOUR_FOLDER_ID"',
            f'GOOGLE_DRIVE_FOLDER_ID = "{folder_id}"'
        )
        
        with open(script_file, 'w') as f:
            f.write(content)
        
        print("   ✅ Configuration updated in video_downloader_to_gdrive.py")
    else:
        print("   ❌ Script file not found")
    
    # Save configuration for reference
    config = {
        "meta_access_token": meta_token,
        "google_drive_folder_id": folder_id,
        "folder_url": folder_url,
        "configured_at": "2025-01-18"
    }
    
    with open("downloader_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("   ✅ Configuration saved to downloader_config.json")
    
    print("\n🎉 Configuration Complete!")
    print("\nNext steps:")
    print("1. Install requirements: pip install -r requirements.txt")
    print("2. Set up Google Drive API credentials (see SETUP_INSTRUCTIONS.md)")
    print("3. Run: python video_downloader_to_gdrive.py")

if __name__ == "__main__":
    main() 
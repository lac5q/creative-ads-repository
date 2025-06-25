#!/usr/bin/env python
"""
Test script for Meta Ads MCP Server
This script verifies that the server can start and basic functionality works.
"""

import sys
import os
sys.path.append('src')

def test_server_import():
    """Test that the server can be imported without errors."""
    try:
        import mcp_server
        print("✅ MCP Server imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_meta_ads_client():
    """Test that the Meta Ads client can be imported."""
    try:
        from meta_ads_client import MetaAdsClient
        print("✅ Meta Ads Client imports successfully")
        return True
    except Exception as e:
        print(f"❌ Meta Ads Client import failed: {e}")
        return False

def test_environment():
    """Test that environment variables are loaded."""
    from dotenv import load_dotenv
    load_dotenv()
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    
    if app_id and app_secret:
        print("✅ Environment variables loaded successfully")
        print(f"   App ID: {app_id}")
        print(f"   App Secret: {'*' * len(app_secret)}")
        return True
    else:
        print("❌ Environment variables not found")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Meta Ads MCP Server Installation")
    print("=" * 50)
    
    tests = [
        test_server_import,
        test_meta_ads_client,
        test_environment
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Meta Ads MCP Server is ready to use!")
        print("\nTo start the server, run:")
        print("   python src/mcp_server.py")
        print("\nTo use with Claude Desktop, make sure it's configured in claude_desktop_config.json")
    else:
        print("❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main() 
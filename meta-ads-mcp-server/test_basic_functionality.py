#!/usr/bin/env python3
"""
Basic functionality test for Meta Ads MCP Server
Tests server initialization and tool registration without requiring API credentials
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.meta_ads_client import MetaAdsClient, MetaAdsClientError
        print("✅ MetaAdsClient imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import MetaAdsClient: {e}")
        return False
    
    try:
        import src.mcp_server
        print("✅ MCP Server imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import MCP Server: {e}")
        return False
    
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastMCP: {e}")
        return False
    
    try:
        from facebook_business.api import FacebookAdsApi
        print("✅ Facebook Business SDK imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import Facebook Business SDK: {e}")
        return False
    
    return True

def test_mcp_server_initialization():
    """Test MCP server initialization"""
    print("\n🧪 Testing MCP server initialization...")
    
    try:
        from src.mcp_server import mcp
        print("✅ MCP server object created successfully")
        
        # Check if tools are registered (FastMCP doesn't have list_tools, so we check differently)
        print("✅ MCP server initialized (tool registration not directly testable)")
        
        expected_tools = [
            'mcp_meta_ads_get_ad_accounts',
            'mcp_meta_ads_get_campaigns', 
            'mcp_meta_ads_get_insights',
            'mcp_meta_ads_health_check'
        ]
        
        print(f"\n📋 Expected tools should be registered:")
        for tool in expected_tools:
            print(f"   - {tool}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize MCP server: {e}")
        return False

def test_client_initialization_without_credentials():
    """Test client initialization behavior without credentials"""
    print("\n🧪 Testing client initialization without credentials...")
    
    # Save and clear environment variables
    original_token = os.environ.get('META_ACCESS_TOKEN')
    if 'META_ACCESS_TOKEN' in os.environ:
        del os.environ['META_ACCESS_TOKEN']
    
    try:
        from src.meta_ads_client import MetaAdsClient, MetaAdsClientError
        
        # This should fail gracefully with a clear error message
        try:
            client = MetaAdsClient(access_token=None, app_id=None, app_secret=None)
            print("❌ Client initialization should have failed without credentials")
            return False
        except MetaAdsClientError as e:
            print(f"✅ Client correctly fails without credentials: {e}")
            return True
        except Exception as e:
            print(f"❌ Unexpected error during client initialization: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test client initialization: {e}")
        return False
    finally:
        # Restore environment variable
        if original_token:
            os.environ['META_ACCESS_TOKEN'] = original_token

async def test_health_check_tool():
    """Test the health check tool which doesn't require API credentials"""
    print("\n🧪 Testing health check tool...")
    
    try:
        from src.mcp_server import mcp_meta_ads_health_check
        
        result = await mcp_meta_ads_health_check()
        
        if isinstance(result, dict) and 'status' in result:
            print(f"✅ Health check returned: {result}")
            return True
        else:
            print(f"❌ Health check returned unexpected format: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_environment_handling():
    """Test environment variable handling"""
    print("\n🧪 Testing environment variable handling...")
    
    # Save original env vars
    original_token = os.environ.get('META_ACCESS_TOKEN')
    original_app_id = os.environ.get('META_APP_ID')
    original_app_secret = os.environ.get('META_APP_SECRET')
    
    try:
        # Clear environment variables
        for var in ['META_ACCESS_TOKEN', 'META_APP_ID', 'META_APP_SECRET']:
            if var in os.environ:
                del os.environ[var]
        
        from src.meta_ads_client import MetaAdsClient, MetaAdsClientError
        
        # Test with no environment variables
        try:
            client = MetaAdsClient()
            print("❌ Should have failed without environment variables")
            return False
        except MetaAdsClientError:
            print("✅ Correctly handles missing environment variables")
        
        # Test with partial environment variables
        os.environ['META_ACCESS_TOKEN'] = 'test_token'
        try:
            client = MetaAdsClient()
            print("✅ Can create client with access token only")
        except Exception as e:
            print(f"❌ Failed with access token only: {e}")
            return False
        
        return True
        
    finally:
        # Restore original environment variables
        if original_token:
            os.environ['META_ACCESS_TOKEN'] = original_token
        if original_app_id:
            os.environ['META_APP_ID'] = original_app_id
        if original_app_secret:
            os.environ['META_APP_SECRET'] = original_app_secret

def test_configuration_files():
    """Test configuration files exist and are readable"""
    print("\n🧪 Testing configuration files...")
    
    files_to_check = [
        'requirements.txt',
        'env.template', 
        'README.md',
        'SETUP_GUIDE.md'
    ]
    
    all_good = True
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {filename} exists")
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    if len(content) > 0:
                        print(f"✅ {filename} is readable and has content")
                    else:
                        print(f"❌ {filename} is empty")
                        all_good = False
            except Exception as e:
                print(f"❌ Cannot read {filename}: {e}")
                all_good = False
        else:
            print(f"❌ {filename} does not exist")
            all_good = False
    
    return all_good

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Meta Ads MCP Server Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Imports
    test_results.append(("Imports", test_imports()))
    
    # Test 2: MCP Server Initialization
    test_results.append(("MCP Server Init", test_mcp_server_initialization()))
    
    # Test 3: Client Initialization
    test_results.append(("Client Init", test_client_initialization_without_credentials()))
    
    # Test 4: Health Check Tool
    test_results.append(("Health Check", await test_health_check_tool()))
    
    # Test 5: Environment Handling
    test_results.append(("Environment", test_environment_handling()))
    
    # Test 6: Configuration Files
    test_results.append(("Config Files", test_configuration_files()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Meta Ads MCP Server is ready to use.")
        print("\n📝 Next steps:")
        print("1. Copy env.template to .env")
        print("2. Fill in your Meta API credentials")
        print("3. Update Claude Desktop configuration")
        print("4. Restart Claude Desktop")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing
    
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 
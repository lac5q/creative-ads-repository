#!/usr/bin/env python3
"""
Facebook Ad URL Tester and Video Download Preparation
Tests Facebook preview URLs and prepares for automated downloads
"""

import requests
import json
import csv
from datetime import datetime
import os

def test_facebook_urls():
    """Test Facebook preview URLs from our CSV data"""
    
    print("🔍 Testing Facebook Ad Preview URLs...")
    
    # Top performing ads from our analysis
    top_ads = [
        {
            "ad_id": "120207192312690108",
            "ad_name": "video: influencer David / Most incredible",
            "account": "TurnedYellow",
            "cvr": "11.11%",
            "priority": "🥇 SCALE IMMEDIATELY",
            "facebook_url": "https://fb.me/27UD3eHw89SZ4w1",
            "expected_filename": "01_David_Influencer_WINNER.mp4"
        },
        {
            "ad_id": "120205926791290108", 
            "ad_name": "video: Gifting hook 1 (Sara) / Life is too short",
            "account": "TurnedYellow",
            "cvr": "5.88%",
            "priority": "🥈 SCALE EXCELLENT",
            "facebook_url": "https://fb.me/1NXB1MCtmCtu4jE",
            "expected_filename": "02_Sara_Gifting_Hook_EXCELLENT.mp4"
        }
    ]
    
    results = []
    
    for ad in top_ads:
        print(f"\n📱 Testing: {ad['ad_name']}")
        print(f"🔗 URL: {ad['facebook_url']}")
        
        try:
            # Make a request to see where the URL redirects
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            response = session.get(ad['facebook_url'], allow_redirects=True, timeout=10)
            
            result = {
                **ad,
                "status_code": response.status_code,
                "final_url": response.url,
                "requires_login": "login" in response.url.lower() or "auth" in response.url.lower(),
                "content_length": len(response.content),
                "content_type": response.headers.get('content-type', ''),
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if we're redirected to a login page
            if result["requires_login"]:
                print("❌ Redirected to login page - authentication required")
                result["downloadable"] = False
                result["method"] = "REQUIRES_BROWSER_AUTOMATION"
            else:
                print("✅ Accessible without login")
                result["downloadable"] = True
                result["method"] = "DIRECT_OR_BROWSER"
            
            print(f"📊 Status: {response.status_code}")
            print(f"🎯 Final URL: {response.url}")
            print(f"📦 Content Type: {response.headers.get('content-type', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            result = {
                **ad,
                "status": "ERROR",
                "error": str(e),
                "downloadable": False,
                "method": "REQUIRES_BROWSER_AUTOMATION",
                "timestamp": datetime.now().isoformat()
            }
        
        results.append(result)
    
    # Save results
    with open('facebook_url_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📊 ANALYSIS COMPLETE")
    print("=" * 50)
    
    for result in results:
        print(f"\n{result['ad_name']} ({result['account']}):")
        print(f"  CVR: {result['cvr']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Downloadable: {'✅' if result.get('downloadable', False) else '❌'}")
        print(f"  Method: {result.get('method', 'UNKNOWN')}")
        if result.get('requires_login'):
            print(f"  🔐 Login Required: YES")
    
    print(f"\n💾 Results saved to: facebook_url_test_results.json")
    
    return results

def create_download_strategy(results):
    """Create a strategy for downloading the videos"""
    
    print("\n🎯 Creating Download Strategy...")
    
    strategy = {
        "timestamp": datetime.now().isoformat(),
        "total_ads": len(results),
        "downloadable_count": sum(1 for r in results if r.get('downloadable', False)),
        "requires_browser_count": sum(1 for r in results if r.get('method') == 'REQUIRES_BROWSER_AUTOMATION'),
        "recommended_approach": "PLAYWRIGHT_BROWSER_AUTOMATION",
        "steps": [
            "1. Use Playwright to navigate to Facebook URLs",
            "2. Handle authentication/login redirects",
            "3. Extract video elements and direct URLs",
            "4. Download videos using direct URLs or screen recording",
            "5. Save to creative_ads_downloads/ directory",
            "6. Upload to GitHub repository",
            "7. Update CSV with GitHub URLs"
        ],
        "ads": results
    }
    
    with open('download_strategy.json', 'w') as f:
        json.dump(strategy, f, indent=2)
    
    print("📋 Download Strategy Created")
    print(f"💾 Saved to: download_strategy.json")
    
    if strategy["requires_browser_count"] > 0:
        print(f"\n⚠️  {strategy['requires_browser_count']} ads require browser automation")
        print("🎭 Recommend using Playwright for authentication handling")
    
    if strategy["downloadable_count"] > 0:
        print(f"✅ {strategy['downloadable_count']} ads may be directly downloadable")
    
    return strategy

if __name__ == "__main__":
    print("🚀 Facebook Ad Video Download Preparation")
    print("=" * 50)
    
    # Test the URLs
    results = test_facebook_urls()
    
    # Create download strategy
    strategy = create_download_strategy(results)
    
    print("\n🎬 Ready for video download automation!")
    print("📁 Files created:")
    print("  - facebook_url_test_results.json")
    print("  - download_strategy.json") 
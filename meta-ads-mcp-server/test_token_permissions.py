#!/usr/bin/env python
"""
Test Facebook Access Token Permissions
Tests if your token can access the required endpoints for downloading ad videos
"""

import requests
import json
import sys

def test_token_permissions(access_token):
    """Test various Facebook Graph API endpoints to verify permissions."""
    
    base_url = "https://graph.facebook.com/v23.0"
    
    tests = [
        {
            'name': 'User Info',
            'endpoint': f"{base_url}/me",
            'params': {'access_token': access_token, 'fields': 'id,name'},
            'required_for': 'Basic API access'
        },
        {
            'name': 'Ad Accounts',
            'endpoint': f"{base_url}/me/adaccounts",
            'params': {
                'access_token': access_token,
                'fields': 'id,name,account_status',
                'limit': 5
            },
            'required_for': 'Reading ad account data'
        },
        {
            'name': 'Business Accounts',
            'endpoint': f"{base_url}/me/businesses",
            'params': {
                'access_token': access_token,
                'fields': 'id,name',
                'limit': 5
            },
            'required_for': 'Business management access'
        }
    ]
    
    print("🔍 Testing Facebook Access Token Permissions...\n")
    print(f"Token: {access_token[:20]}...{access_token[-10:]}\n")
    
    results = []
    
    for test in tests:
        print(f"Testing: {test['name']} ({test['required_for']})")
        
        try:
            response = requests.get(test['endpoint'], params=test['params'])
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {test['name']}")
                
                if 'data' in data:
                    print(f"   Found {len(data['data'])} items")
                    if data['data']:
                        print(f"   Example: {data['data'][0].get('name', 'N/A')}")
                elif 'name' in data:
                    print(f"   User: {data['name']}")
                
                results.append({'test': test['name'], 'status': 'PASS', 'data': data})
                
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                error_code = error_data.get('error', {}).get('code', 'N/A')
                
                print(f"❌ FAILED: {test['name']}")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {error_msg} (Code: {error_code})")
                
                results.append({
                    'test': test['name'], 
                    'status': 'FAIL', 
                    'error': error_msg,
                    'code': error_code
                })
                
        except Exception as e:
            print(f"❌ ERROR: {test['name']} - {str(e)}")
            results.append({'test': test['name'], 'status': 'ERROR', 'error': str(e)})
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 PERMISSION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your token has the required permissions.")
        print("\n✅ You can now proceed with downloading ad videos!")
        
        # Test a specific ad account
        print("\n🔍 Testing specific ad account access...")
        test_ad_account_access(access_token, results)
        
    else:
        print("⚠️ SOME TESTS FAILED. You need to update your token permissions.")
        print("\n🛠️ REQUIRED ACTIONS:")
        
        for result in results:
            if result['status'] != 'PASS':
                if 'Missing Permissions' in result.get('error', ''):
                    print(f"   - Add missing permissions for: {result['test']}")
                elif result.get('code') == 190:
                    print(f"   - Token is invalid or expired")
                    break
    
    return results

def test_ad_account_access(access_token, previous_results):
    """Test access to specific ad account and campaigns."""
    
    # Find ad account from previous results
    ad_accounts = []
    for result in previous_results:
        if result['test'] == 'Ad Accounts' and result['status'] == 'PASS':
            ad_accounts = result['data'].get('data', [])
            break
    
    if not ad_accounts:
        print("❌ No ad accounts found to test")
        return
    
    # Test first ad account
    account = ad_accounts[0]
    account_id = account['id']
    account_name = account.get('name', 'Unknown')
    
    print(f"Testing ad account: {account_name} ({account_id})")
    
    # Test campaigns endpoint
    campaigns_url = f"https://graph.facebook.com/v23.0/{account_id}/campaigns"
    campaigns_params = {
        'access_token': access_token,
        'fields': 'id,name,status',
        'limit': 5
    }
    
    try:
        response = requests.get(campaigns_url, params=campaigns_params)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            print(f"✅ Found {len(campaigns)} campaigns")
            
            if campaigns:
                # Test ads endpoint for first campaign
                campaign_id = campaigns[0]['id']
                campaign_name = campaigns[0].get('name', 'Unknown')
                
                print(f"   Testing campaign: {campaign_name}")
                
                # Test ads
                ads_url = f"https://graph.facebook.com/v23.0/{campaign_id}/ads"
                ads_params = {
                    'access_token': access_token,
                    'fields': 'id,name,status',
                    'limit': 3
                }
                
                ads_response = requests.get(ads_url, params=ads_params)
                
                if ads_response.status_code == 200:
                    ads_data = ads_response.json()
                    ads = ads_data.get('data', [])
                    print(f"   ✅ Found {len(ads)} ads")
                    
                    if ads:
                        print("   🎯 Ready to download ad creatives!")
                    
                else:
                    print(f"   ❌ Cannot access ads: {ads_response.status_code}")
                    
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ Cannot access campaigns: {error_msg}")
            
    except Exception as e:
        print(f"❌ Error testing ad account: {str(e)}")

def main():
    """Main function to run permission tests."""
    
    if len(sys.argv) != 2:
        print("Usage: python test_token_permissions.py <ACCESS_TOKEN>")
        print("\nExample:")
        print("python test_token_permissions.py EAARlbLCiEEsBO8nb...")
        return
    
    access_token = sys.argv[1]
    
    if not access_token or len(access_token) < 50:
        print("❌ Invalid access token. Please provide a valid Facebook access token.")
        return
    
    results = test_token_permissions(access_token)
    
    # Save results
    with open('token_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: token_test_results.json")

if __name__ == "__main__":
    main() 
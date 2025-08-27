#!/usr/bin/env python3
"""
Test the actual working endpoints discovered in portfolio_data.py
"""

import json
import urllib.request
import urllib.parse
import urllib.error

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_USER_EMAIL = "demo_individual@sigmasight.com"
DEMO_USER_PASSWORD = "password123"

# Known portfolio IDs from the code
PORTFOLIO_IDS = {
    "a3209353-9ed5-4885-81e8-d4bbc995f96c": "Individual Investor",
    "14e7f420-b096-4e2e-8cc2-531caf434c05": "High Net Worth",
    "cf890da7-7b74-4cb4-acba-2205fdd9dff4": "Hedge Fund Style"
}

def make_request(url, data=None, headers=None, method='GET'):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {}
    
    if data is not None and method == 'POST':
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        content = response.read().decode('utf-8')
        
        return {
            'status': response.status,
            'content': content,
            'headers': dict(response.headers)
        }
        
    except urllib.error.HTTPError as e:
        content = ""
        try:
            content = e.read().decode('utf-8')
        except:
            pass
        return {
            'status': e.code,
            'content': content,
            'error': str(e)
        }
        
    except Exception as e:
        return {
            'status': 0,
            'content': "",
            'error': str(e)
        }

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": DEMO_USER_EMAIL,
        "password": DEMO_USER_PASSWORD
    }
    
    result = make_request(
        f"{BACKEND_URL}/api/v1/auth/login",
        data=login_data,
        method='POST'
    )
    
    if result['status'] != 200:
        return None
    
    try:
        auth_response = json.loads(result['content'])
        return auth_response.get('access_token')
    except:
        return None

def test_portfolio_endpoints():
    """Test the working portfolio endpoints"""
    print("Testing Working Portfolio Endpoints")
    print("=" * 40)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("CRITICAL: Cannot get auth token")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    working_endpoints = []
    broken_endpoints = []
    
    # Test each portfolio with each endpoint
    for portfolio_id, portfolio_name in PORTFOLIO_IDS.items():
        print(f"\n--- Testing {portfolio_name} ({portfolio_id[:8]}...) ---")
        
        endpoints_to_test = [
            f'/api/v1/portfolio/{portfolio_id}/summary',
            f'/api/v1/portfolio/{portfolio_id}/attribution',
            f'/api/v1/portfolio/{portfolio_id}/factors',
            f'/api/v1/portfolio/{portfolio_id}/risk/var',
        ]
        
        for endpoint in endpoints_to_test:
            result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
            
            if result['status'] == 200:
                try:
                    data = json.loads(result['content'])
                    
                    # Check if it's returning real data
                    if 'portfolioId' in data or 'factor' in str(data) or 'varAmount' in data or 'items' in data:
                        print(f"✓ WORKING: {endpoint}")
                        working_endpoints.append(endpoint)
                        
                        # Show sample data
                        if 'portfolioId' in data:
                            print(f"  Portfolio ID: {data['portfolioId']}")
                            print(f"  Equity: ${data.get('equity', 0):,.2f}")
                            print(f"  Return: {data.get('returnPct', 0):.2f}%")
                        elif 'items' in data:
                            print(f"  Attribution items: {len(data['items'])}")
                            if data['items']:
                                print(f"  Top contributor: {data['items'][0]}")
                        elif 'exposures' in data:
                            print(f"  Factor exposures: {len(data['exposures'])}")
                        elif 'varAmount' in data:
                            print(f"  VaR Amount: ${data['varAmount']:,.2f}")
                    else:
                        print(f"✗ TODO: {endpoint} - Returns placeholder data")
                        broken_endpoints.append(endpoint)
                        
                except json.JSONDecodeError:
                    print(f"✗ INVALID JSON: {endpoint}")
                    broken_endpoints.append(endpoint)
                    
            else:
                print(f"✗ ERROR {result['status']}: {endpoint}")
                broken_endpoints.append(endpoint)
                if result.get('error'):
                    print(f"  Error: {result['error']}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"WORKING ENDPOINTS SUMMARY")
    print(f"=" * 60)
    
    print(f"\n✓ WORKING ({len(working_endpoints)}):")
    for endpoint in working_endpoints:
        print(f"  {endpoint}")
    
    print(f"\n✗ BROKEN ({len(broken_endpoints)}):")
    for endpoint in broken_endpoints:
        print(f"  {endpoint}")
    
    # Test with query parameters
    print(f"\n=== TESTING QUERY PARAMETERS ===")
    
    portfolio_id = list(PORTFOLIO_IDS.keys())[0]  # Use first portfolio for testing
    
    # Test summary with different windows
    windows = ['1d', '1w', '1m', '3m', '1y']
    for window in windows:
        endpoint = f'/api/v1/portfolio/{portfolio_id}/summary?window={window}'
        result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if result['status'] == 200:
            try:
                data = json.loads(result['content'])
                print(f"✓ Summary window={window}: Return={data.get('returnPct', 0):.2f}%")
            except:
                print(f"✗ Summary window={window}: Invalid JSON")
        else:
            print(f"✗ Summary window={window}: Status {result['status']}")
    
    # Test attribution with different groupBy
    group_by_options = ['security', 'sector', 'factor']
    for group_by in group_by_options:
        endpoint = f'/api/v1/portfolio/{portfolio_id}/attribution?groupBy={group_by}'
        result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if result['status'] == 200:
            try:
                data = json.loads(result['content'])
                items_count = len(data.get('items', []))
                print(f"✓ Attribution groupBy={group_by}: {items_count} items")
            except:
                print(f"✗ Attribution groupBy={group_by}: Invalid JSON")
        else:
            print(f"✗ Attribution groupBy={group_by}: Status {result['status']}")
    
    print(f"\n=== TESTING DIFFERENT PORTFOLIO TYPES ===")
    
    # Compare data across different portfolio types
    for portfolio_id, portfolio_name in PORTFOLIO_IDS.items():
        endpoint = f'/api/v1/portfolio/{portfolio_id}/summary'
        result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if result['status'] == 200:
            try:
                data = json.loads(result['content'])
                equity = data.get('equity', 0)
                return_pct = data.get('returnPct', 0)
                sharpe = data.get('sharpe', 0)
                
                print(f"{portfolio_name}:")
                print(f"  Equity: ${equity:,.2f}")
                print(f"  Return: {return_pct:.2f}%")
                print(f"  Sharpe: {sharpe:.2f}")
                
            except Exception as e:
                print(f"{portfolio_name}: Error parsing data - {e}")
        else:
            print(f"{portfolio_name}: Status {result['status']}")
    
    return len(working_endpoints), len(broken_endpoints)

if __name__ == "__main__":
    try:
        working_count, broken_count = test_portfolio_endpoints()
        
        print(f"\n" + "=" * 60)
        print(f"FINAL RESULTS:")
        print(f"Working endpoints: {working_count}")
        print(f"Broken endpoints: {broken_count}")
        
        if broken_count == 0:
            print("🎉 ALL PORTFOLIO ENDPOINTS ARE WORKING!")
        else:
            print(f"⚠️  {broken_count} endpoints need attention")
            
    except Exception as e:
        print(f"Testing failed: {e}")
        import traceback
        traceback.print_exc()
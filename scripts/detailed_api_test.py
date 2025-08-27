#!/usr/bin/env python3
"""
SigmaSight Detailed API Testing Script
======================================

Deep dive into API endpoints to find more issues.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_USER_EMAIL = "demo_individual@sigmasight.com"
DEMO_USER_PASSWORD = "password123"

def make_request(url, data=None, headers=None, method='GET'):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {}
    
    if data is not None and method == 'POST':
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        start_time = time.time()
        response = urllib.request.urlopen(req, timeout=30)
        duration = time.time() - start_time
        
        content = response.read().decode('utf-8')
        
        return {
            'status': response.status,
            'content': content,
            'duration': duration,
            'headers': dict(response.headers)
        }
        
    except urllib.error.HTTPError as e:
        duration = time.time() - start_time
        content = ""
        try:
            content = e.read().decode('utf-8')
        except:
            pass
        return {
            'status': e.code,
            'content': content,
            'duration': duration,
            'error': str(e)
        }
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            'status': 0,
            'content': "",
            'duration': duration,
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

def test_detailed_api_endpoints():
    """Test all API endpoints in detail"""
    print("SigmaSight Detailed API Testing")
    print("=" * 40)
    
    # Get auth token first
    print("Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("CRITICAL: Cannot get auth token - stopping tests")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    issues = []
    
    print(f"Testing with token: {token[:20]}...")
    
    # Test all known endpoints
    endpoints_to_test = [
        # Auth endpoints
        ('/api/v1/auth/me', 'GET', 'User profile endpoint'),
        
        # Portfolio endpoints
        ('/api/v1/portfolio/', 'GET', 'Portfolio overview'),
        
        # Risk endpoints - these should work based on test output
        ('/api/v1/risk/greeks', 'GET', 'Greeks risk data'),
        ('/api/v1/risk/factors', 'GET', 'Factor risk data'),
        ('/api/v1/risk/scenarios', 'GET', 'Risk scenarios'),
        
        # Market data endpoints
        ('/api/v1/market-data/quotes', 'GET', 'Market quotes'),
        ('/api/v1/market-data/symbols', 'GET', 'Market symbols'),
        
        # Alerts endpoints
        ('/api/v1/alerts', 'GET', 'Alerts list'),
        ('/api/v1/alerts?priority=critical', 'GET', 'Critical alerts'),
        ('/api/v1/alerts?priority=high', 'GET', 'High priority alerts'),
        
        # Reports endpoints
        ('/api/v1/reports', 'GET', 'Reports list'),
        
        # Position endpoints (will need portfolio ID)
        # ('/api/v1/positions/{portfolio_id}', 'GET', 'Portfolio positions'),
        
        # Admin endpoints
        ('/api/v1/admin/batch/status', 'GET', 'Batch job status'),
        ('/api/v1/admin/batch/run', 'POST', 'Run batch jobs'),
    ]
    
    print(f"\nTesting {len(endpoints_to_test)} endpoints...")
    print("-" * 50)
    
    for endpoint, method, description in endpoints_to_test:
        print(f"\n[{method}] {endpoint} - {description}")
        
        # Make request
        if method == 'GET':
            result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        else:  # POST
            result = make_request(f"{BACKEND_URL}{endpoint}", data={}, headers=headers, method=method)
        
        # Analyze result
        status = result['status']
        duration = result['duration']
        content = result.get('content', '')
        
        print(f"   Status: {status} | Duration: {duration:.3f}s")
        
        # Check for issues
        if status == 404:
            issues.append({
                'severity': 'MEDIUM',
                'endpoint': endpoint,
                'method': method,
                'description': f'{description} not implemented',
                'status': status,
                'issue_type': 'Missing Endpoint'
            })
            print("   ISSUE: Endpoint not implemented (404)")
            
        elif status == 500:
            issues.append({
                'severity': 'HIGH',
                'endpoint': endpoint,
                'method': method,
                'description': f'{description} server error',
                'status': status,
                'error': result.get('error', ''),
                'content': content[:200],
                'issue_type': 'Server Error'
            })
            print("   CRITICAL: Server error (500)")
            
        elif status in [401, 403]:
            print(f"   AUTH: Authentication/Authorization issue ({status})")
            
        elif status == 200:
            # Check response content quality
            try:
                if content:
                    data = json.loads(content)
                    
                    # Check for TODO messages
                    if isinstance(data, dict):
                        if 'message' in data and 'TODO' in str(data['message']):
                            issues.append({
                                'severity': 'MEDIUM',
                                'endpoint': endpoint,
                                'method': method,
                                'description': f'{description} returns TODO placeholder',
                                'status': status,
                                'content': str(data)[:200],
                                'issue_type': 'Incomplete Implementation'
                            })
                            print("   ISSUE: Returns TODO placeholder")
                        
                        # Check for empty or minimal data
                        elif len(str(data)) < 50:
                            issues.append({
                                'severity': 'LOW',
                                'endpoint': endpoint,
                                'method': method,
                                'description': f'{description} returns minimal data',
                                'status': status,
                                'content': str(data),
                                'issue_type': 'Minimal Data'
                            })
                            print("   WARNING: Returns minimal data")
                        else:
                            print("   SUCCESS: Returns structured data")
                    else:
                        print("   SUCCESS: Returns data")
                else:
                    issues.append({
                        'severity': 'LOW',
                        'endpoint': endpoint,
                        'method': method,
                        'description': f'{description} returns empty response',
                        'status': status,
                        'issue_type': 'Empty Response'
                    })
                    print("   WARNING: Empty response body")
                    
            except json.JSONDecodeError:
                if content.strip():
                    print("   WARNING: Non-JSON response")
                else:
                    print("   WARNING: Empty response")
        else:
            issues.append({
                'severity': 'MEDIUM',
                'endpoint': endpoint,
                'method': method,
                'description': f'{description} returns unexpected status {status}',
                'status': status,
                'error': result.get('error', ''),
                'issue_type': 'Unexpected Status'
            })
            print(f"   ISSUE: Unexpected status ({status})")
    
    # Test specific portfolio data
    print(f"\n\n=== TESTING PORTFOLIO-SPECIFIC ENDPOINTS ===")
    
    # First get portfolio data to extract IDs
    portfolio_result = make_request(f"{BACKEND_URL}/api/v1/portfolio/", headers=headers)
    
    if portfolio_result['status'] == 200:
        try:
            portfolio_response = json.loads(portfolio_result['content'])
            print(f"Portfolio response: {portfolio_response}")
            
            # The previous test showed this returns a TODO message, let's analyze the structure
            if 'user_id' in portfolio_response:
                print("   Portfolio endpoint is incomplete - returns user info instead of portfolios")
                
                # Try to get portfolios another way - check if there's a direct portfolios endpoint
                alt_result = make_request(f"{BACKEND_URL}/api/v1/portfolios", headers=headers)
                print(f"   Alternative /api/v1/portfolios status: {alt_result['status']}")
                
                if alt_result['status'] == 200:
                    try:
                        alt_data = json.loads(alt_result['content'])
                        print(f"   Alternative endpoint data: {alt_data}")
                    except:
                        pass
                        
        except json.JSONDecodeError:
            print("   Cannot parse portfolio response as JSON")
    
    # Generate detailed report
    print("\n" + "=" * 80)
    print("DETAILED API TESTING REPORT")
    print("=" * 80)
    
    if not issues:
        print("No additional issues found in detailed API testing.")
        return
    
    # Group issues by type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue.get('issue_type', 'Unknown')
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
    
    print(f"\nFOUND {len(issues)} ADDITIONAL API ISSUES:")
    print("-" * 50)
    
    for issue_type, type_issues in issues_by_type.items():
        print(f"\n{issue_type.upper()} ({len(type_issues)} issues):")
        for issue in type_issues:
            severity_marker = {
                'HIGH': '***',
                'MEDIUM': '**',
                'LOW': '*'
            }.get(issue['severity'], '')
            
            print(f"  {severity_marker} [{issue['method']}] {issue['endpoint']}")
            print(f"      {issue['description']} (Status: {issue['status']})")
            if issue.get('error'):
                print(f"      Error: {issue['error']}")
            if issue.get('content'):
                print(f"      Content: {issue['content'][:100]}...")
    
    # Summary of API health
    print(f"\nAPI HEALTH SUMMARY:")
    print("-" * 30)
    
    total_endpoints = len(endpoints_to_test)
    working_endpoints = len([i for i in issues if i['status'] == 200])
    missing_endpoints = len([i for i in issues if i['status'] == 404])
    error_endpoints = len([i for i in issues if i['status'] >= 500])
    
    print(f"Total endpoints tested: {total_endpoints}")
    print(f"Missing (404): {missing_endpoints}")
    print(f"Server errors (5xx): {error_endpoints}")
    print(f"Authentication issues: {len([i for i in issues if i['status'] in [401, 403]])}")
    print(f"TODO placeholders: {len([i for i in issues if i.get('issue_type') == 'Incomplete Implementation'])}")
    
    coverage_pct = ((total_endpoints - missing_endpoints) / total_endpoints) * 100
    print(f"\nAPI Coverage: {coverage_pct:.1f}%")
    
    if missing_endpoints > total_endpoints * 0.3:
        print("WARNING: More than 30% of expected endpoints are missing")
    
    if error_endpoints > 0:
        print("CRITICAL: Some endpoints are returning server errors")

if __name__ == "__main__":
    try:
        test_detailed_api_endpoints()
    except Exception as e:
        print(f"Detailed API testing failed: {e}")
        import traceback
        traceback.print_exc()
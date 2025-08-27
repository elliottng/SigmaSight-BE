#!/usr/bin/env python3
"""
SigmaSight Quick End-to-End Testing Script
==========================================

Fast testing script to identify critical issues immediately.
This uses only Python standard library to avoid dependency issues.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:3008"
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

def test_frontend():
    """Test frontend availability"""
    print("[TEST] Testing Frontend (http://localhost:3008)...")
    
    issues = []
    
    # Test homepage
    result = make_request(FRONTEND_URL)
    if result['status'] != 200:
        issues.append({
            'severity': 'CRITICAL',
            'description': f"Frontend homepage not accessible - Status: {result['status']}",
            'error': result.get('error', 'HTTP error'),
            'responsible': 'Frontend'
        })
        return issues
    
    # Check load time
    if result['duration'] > 3.0:
        issues.append({
            'severity': 'MEDIUM',
            'description': f"Frontend loads slowly - {result['duration']:.2f} seconds",
            'responsible': 'Performance'
        })
    
    # Check branding
    if "SigmaSight" not in result['content']:
        issues.append({
            'severity': 'MEDIUM',
            'description': "Homepage missing SigmaSight branding",
            'responsible': 'Frontend'
        })
    
    # Test key pages
    pages_to_test = ['/login', '/dashboard', '/positions', '/market', '/reports', '/risk']
    
    for page in pages_to_test:
        page_result = make_request(f"{FRONTEND_URL}{page}")
        if page_result['status'] != 200:
            issues.append({
                'severity': 'HIGH',
                'description': f"Page {page} not accessible - Status: {page_result['status']}",
                'error': page_result.get('error', 'HTTP error'),
                'responsible': 'Frontend'
            })
    
    if not issues:
        print("✅ Frontend tests passed")
    
    return issues

def test_backend_auth():
    """Test backend authentication"""
    print("🔍 Testing Backend Authentication...")
    
    issues = []
    
    # Test API docs
    docs_result = make_request(f"{BACKEND_URL}/docs")
    if docs_result['status'] != 200:
        issues.append({
            'severity': 'HIGH',
            'description': f"API documentation not accessible - Status: {docs_result['status']}",
            'error': docs_result.get('error', 'HTTP error'),
            'responsible': 'Backend'
        })
        return issues
    
    # Test login
    login_data = {
        "email": DEMO_USER_EMAIL,
        "password": DEMO_USER_PASSWORD
    }
    
    login_result = make_request(
        f"{BACKEND_URL}/api/v1/auth/login",
        data=login_data,
        method='POST'
    )
    
    if login_result['status'] != 200:
        issues.append({
            'severity': 'CRITICAL',
            'description': f"Login endpoint fails - Status: {login_result['status']}",
            'error': login_result.get('error', 'Login failed'),
            'details': login_result['content'],
            'responsible': 'Backend'
        })
        return issues
    
    try:
        auth_response = json.loads(login_result['content'])
        if 'access_token' not in auth_response:
            issues.append({
                'severity': 'CRITICAL',
                'description': "Login response missing access token",
                'details': login_result['content'],
                'responsible': 'Backend'
            })
            return issues
        
        token = auth_response['access_token']
        print("✅ Login successful - got access token")
        
        # Test token validation
        me_result = make_request(
            f"{BACKEND_URL}/api/v1/auth/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if me_result['status'] != 200:
            issues.append({
                'severity': 'HIGH',
                'description': f"Token validation fails - Status: {me_result['status']}",
                'error': me_result.get('error', 'Token validation failed'),
                'responsible': 'Backend'
            })
        else:
            print("✅ Token validation successful")
            
        return issues, token
        
    except json.JSONDecodeError:
        issues.append({
            'severity': 'HIGH',
            'description': "Login response is not valid JSON",
            'details': login_result['content'],
            'responsible': 'Backend'
        })
        return issues, None

def test_portfolio_data(token):
    """Test portfolio data endpoints"""
    print("🔍 Testing Portfolio Data...")
    
    issues = []
    
    if not token:
        issues.append({
            'severity': 'CRITICAL',
            'description': "Cannot test portfolio data - no auth token",
            'responsible': 'Backend'
        })
        return issues
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test portfolio overview
    portfolio_result = make_request(
        f"{BACKEND_URL}/api/v1/portfolio/",
        headers=headers
    )
    
    if portfolio_result['status'] != 200:
        issues.append({
            'severity': 'HIGH',
            'description': f"Portfolio overview fails - Status: {portfolio_result['status']}",
            'error': portfolio_result.get('error', 'Portfolio API error'),
            'responsible': 'Backend'
        })
        return issues
    
    try:
        portfolio_data = json.loads(portfolio_result['content'])
        
        if 'portfolios' not in portfolio_data:
            issues.append({
                'severity': 'HIGH',
                'description': "Portfolio response missing 'portfolios' field",
                'details': portfolio_result['content'],
                'responsible': 'Backend'
            })
            return issues
        
        portfolios = portfolio_data['portfolios']
        if not portfolios:
            issues.append({
                'severity': 'HIGH',
                'description': "No portfolios found for demo user - check if demo data is seeded",
                'details': portfolio_result['content'],
                'responsible': 'Backend'
            })
        else:
            print(f"✅ Portfolio data loaded - {len(portfolios)} portfolio(s)")
            
            # Test positions for first portfolio
            first_portfolio = portfolios[0]
            portfolio_id = first_portfolio.get('id')
            
            if portfolio_id:
                positions_result = make_request(
                    f"{BACKEND_URL}/api/v1/positions/{portfolio_id}",
                    headers=headers
                )
                
                if positions_result['status'] != 200:
                    issues.append({
                        'severity': 'MEDIUM',
                        'description': f"Positions endpoint fails for portfolio {portfolio_id} - Status: {positions_result['status']}",
                        'error': positions_result.get('error', 'Positions API error'),
                        'responsible': 'Backend'
                    })
                else:
                    print("✅ Positions data accessible")
        
        return issues
        
    except json.JSONDecodeError:
        issues.append({
            'severity': 'HIGH',
            'description': "Portfolio response is not valid JSON",
            'details': portfolio_result['content'],
            'responsible': 'Backend'
        })
        return issues

def test_missing_endpoints(token):
    """Test for missing/unimplemented endpoints"""
    print("🔍 Testing Missing Endpoints...")
    
    issues = []
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # List of expected endpoints that might be missing
    endpoints_to_check = [
        ('/api/v1/alerts', 'Alerts endpoint'),
        ('/api/v1/alerts?priority=critical', 'Critical alerts filtering'),
        ('/api/v1/risk/greeks', 'Greeks risk data'),
        ('/api/v1/risk/factors', 'Factor risk data'),
        ('/api/v1/risk/scenarios', 'Risk scenarios'),
        ('/api/v1/market-data/quotes', 'Market data quotes'),
    ]
    
    for endpoint, description in endpoints_to_check:
        result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if result['status'] == 404:
            issues.append({
                'severity': 'MEDIUM',
                'description': f"{description} not implemented - {endpoint} returns 404",
                'responsible': 'Backend'
            })
        elif result['status'] not in [200, 401, 403]:  # 401/403 are OK - means endpoint exists but needs auth/permissions
            issues.append({
                'severity': 'LOW',
                'description': f"{description} returns unexpected status {result['status']} - {endpoint}",
                'error': result.get('error', 'Unknown error'),
                'responsible': 'Backend'
            })
    
    return issues

def test_error_handling(token):
    """Test error handling"""
    print("🔍 Testing Error Handling...")
    
    issues = []
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # Test invalid endpoints
    invalid_tests = [
        ('/api/v1/nonexistent', 'Invalid endpoint'),
        ('/api/v1/portfolio/invalid-uuid', 'Invalid UUID'),
        ('/api/v1/positions/not-a-uuid', 'Malformed UUID'),
    ]
    
    for endpoint, description in invalid_tests:
        result = make_request(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if result['status'] == 200:
            issues.append({
                'severity': 'MEDIUM',
                'description': f"{description} inappropriately returns 200 OK - {endpoint}",
                'responsible': 'Backend'
            })
    
    # Test unauthorized access
    unauth_result = make_request(f"{BACKEND_URL}/api/v1/portfolio/")
    if unauth_result['status'] != 401:
        issues.append({
            'severity': 'HIGH',
            'description': f"Unauthorized access not properly rejected - Status: {unauth_result['status']} (should be 401)",
            'responsible': 'Backend'
        })
    
    return issues

def run_all_tests():
    """Run all tests and generate report"""
    print("🔥 SigmaSight Quick E2E Testing Started")
    print("=" * 50)
    
    all_issues = []
    
    # Test frontend
    frontend_issues = test_frontend()
    all_issues.extend(frontend_issues)
    
    # Test backend auth
    auth_result = test_backend_auth()
    if isinstance(auth_result, tuple):
        auth_issues, token = auth_result
        all_issues.extend(auth_issues)
    else:
        auth_issues = auth_result
        all_issues.extend(auth_issues)
        token = None
    
    # Test portfolio data (only if we have a token)
    if token:
        portfolio_issues = test_portfolio_data(token)
        all_issues.extend(portfolio_issues)
        
        missing_endpoint_issues = test_missing_endpoints(token)
        all_issues.extend(missing_endpoint_issues)
        
        error_handling_issues = test_error_handling(token)
        all_issues.extend(error_handling_issues)
    
    # Generate report
    print("\n" + "=" * 80)
    print("🚨 QUICK E2E TEST RESULTS")
    print("=" * 80)
    
    if not all_issues:
        print("✅ NO CRITICAL ISSUES FOUND!")
        print("The core application functionality appears to be working.")
        return 0
    
    # Group by severity
    critical_issues = [i for i in all_issues if i.get('severity') == 'CRITICAL']
    high_issues = [i for i in all_issues if i.get('severity') == 'HIGH']
    medium_issues = [i for i in all_issues if i.get('severity') == 'MEDIUM']
    low_issues = [i for i in all_issues if i.get('severity') == 'LOW']
    
    total_issues = len(all_issues)
    
    print(f"\n📊 SUMMARY: {total_issues} ISSUES FOUND")
    print("-" * 40)
    if critical_issues:
        print(f"🔴 CRITICAL: {len(critical_issues)} issues")
    if high_issues:
        print(f"🟠 HIGH: {len(high_issues)} issues")
    if medium_issues:
        print(f"🟡 MEDIUM: {len(medium_issues)} issues")
    if low_issues:
        print(f"🟢 LOW: {len(low_issues)} issues")
    
    print(f"\n🔥 DETAILED ISSUES:")
    print("=" * 50)
    
    issue_num = 1
    for severity, issues_list in [
        ('CRITICAL', critical_issues),
        ('HIGH', high_issues), 
        ('MEDIUM', medium_issues),
        ('LOW', low_issues)
    ]:
        if not issues_list:
            continue
            
        print(f"\n{severity} SEVERITY:")
        print("-" * 30)
        
        for issue in issues_list:
            print(f"\n#{issue_num}. {issue['description']}")
            print(f"   Responsible: {issue['responsible']}")
            if 'error' in issue:
                print(f"   Error: {issue['error']}")
            if 'details' in issue:
                print(f"   Details: {issue['details'][:200]}...")
            issue_num += 1
    
    print(f"\n🎯 IMMEDIATE ACTIONS NEEDED:")
    print("=" * 40)
    
    if critical_issues:
        print("🚨 CRITICAL - Fix immediately before any releases:")
        for issue in critical_issues:
            print(f"   • {issue['description']}")
    
    if high_issues:
        print("\n🔥 HIGH PRIORITY - Fix this sprint:")
        for issue in high_issues:
            print(f"   • {issue['description']}")
    
    # Return exit code based on severity
    if critical_issues:
        return 1
    elif high_issues:
        return 2
    else:
        return 0

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        print(f"\n{'✅' if exit_code == 0 else '❌'} Testing completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
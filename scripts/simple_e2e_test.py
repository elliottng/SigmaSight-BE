#!/usr/bin/env python3
"""
SigmaSight Simple E2E Testing Script
====================================

ASCII-only version for Windows compatibility.
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

def run_comprehensive_test():
    """Run all tests and return detailed results"""
    print("SigmaSight Comprehensive E2E Testing Started")
    print("=" * 50)
    
    all_issues = []
    
    # Test 1: Frontend availability
    print("\n[TEST 1] Testing Frontend Availability...")
    frontend_result = make_request(FRONTEND_URL)
    
    if frontend_result['status'] != 200:
        all_issues.append({
            'severity': 'CRITICAL',
            'category': 'Frontend',
            'description': f'Frontend not accessible - Status: {frontend_result["status"]}',
            'steps': '1. Navigate to http://localhost:3008',
            'expected': 'Should return 200 OK and load homepage',
            'actual': f'Returned status {frontend_result["status"]}',
            'error': frontend_result.get('error', ''),
            'responsible': 'Frontend Agent'
        })
        print("FAILED: Frontend not accessible")
    else:
        print("PASSED: Frontend accessible")
        
        # Check load time
        if frontend_result['duration'] > 3.0:
            all_issues.append({
                'severity': 'MEDIUM',
                'category': 'Performance',
                'description': f'Frontend loads slowly - {frontend_result["duration"]:.2f} seconds',
                'steps': '1. Navigate to http://localhost:3008\n2. Measure load time',
                'expected': 'Should load in under 3 seconds',
                'actual': f'Took {frontend_result["duration"]:.2f} seconds to load',
                'responsible': 'Performance Agent'
            })
        
        # Check branding
        if "SigmaSight" not in frontend_result['content']:
            all_issues.append({
                'severity': 'MEDIUM',
                'category': 'Frontend',
                'description': 'Homepage missing SigmaSight branding',
                'steps': '1. Navigate to http://localhost:3008\n2. Check page content',
                'expected': 'Should display SigmaSight branding',
                'actual': 'SigmaSight branding not found in page content',
                'responsible': 'Frontend Agent'
            })
    
    # Test 2: Backend API docs
    print("\n[TEST 2] Testing Backend API Documentation...")
    docs_result = make_request(f"{BACKEND_URL}/docs")
    
    if docs_result['status'] != 200:
        all_issues.append({
            'severity': 'HIGH',
            'category': 'Backend',
            'description': f'API documentation not accessible - Status: {docs_result["status"]}',
            'steps': '1. Navigate to http://localhost:8001/docs',
            'expected': 'Should return 200 OK and show API documentation',
            'actual': f'Returned status {docs_result["status"]}',
            'error': docs_result.get('error', ''),
            'responsible': 'Backend Agent'
        })
        print("FAILED: API docs not accessible")
    else:
        print("PASSED: API docs accessible")
    
    # Test 3: Authentication
    print("\n[TEST 3] Testing Authentication Flow...")
    login_data = {
        "email": DEMO_USER_EMAIL,
        "password": DEMO_USER_PASSWORD
    }
    
    login_result = make_request(
        f"{BACKEND_URL}/api/v1/auth/login",
        data=login_data,
        method='POST'
    )
    
    auth_token = None
    
    if login_result['status'] != 200:
        all_issues.append({
            'severity': 'CRITICAL',
            'category': 'Authentication',
            'description': f'Login endpoint fails - Status: {login_result["status"]}',
            'steps': f'1. POST to /api/v1/auth/login with email: {DEMO_USER_EMAIL}, password: {DEMO_USER_PASSWORD}',
            'expected': 'Should return 200 OK with access token',
            'actual': f'Returned status {login_result["status"]}',
            'error': login_result.get('error', ''),
            'details': login_result['content'][:500] if login_result['content'] else '',
            'responsible': 'Backend Agent'
        })
        print("FAILED: Login fails")
    else:
        try:
            auth_response = json.loads(login_result['content'])
            if 'access_token' not in auth_response:
                all_issues.append({
                    'severity': 'CRITICAL',
                    'category': 'Authentication',
                    'description': 'Login response missing access token',
                    'steps': f'1. POST to /api/v1/auth/login with valid credentials',
                    'expected': 'Should return JSON with access_token field',
                    'actual': f'Response: {login_result["content"][:200]}...',
                    'responsible': 'Backend Agent'
                })
                print("FAILED: No access token in response")
            else:
                auth_token = auth_response['access_token']
                print("PASSED: Login successful, token obtained")
                
                # Test token validation
                me_result = make_request(
                    f"{BACKEND_URL}/api/v1/auth/me",
                    headers={'Authorization': f'Bearer {auth_token}'}
                )
                
                if me_result['status'] != 200:
                    all_issues.append({
                        'severity': 'HIGH',
                        'category': 'Authentication',
                        'description': f'Token validation fails - Status: {me_result["status"]}',
                        'steps': '1. Login to get token\n2. GET /api/v1/auth/me with Authorization header',
                        'expected': 'Should return 200 OK with user data',
                        'actual': f'Returned status {me_result["status"]}',
                        'error': me_result.get('error', ''),
                        'responsible': 'Backend Agent'
                    })
                    print("FAILED: Token validation fails")
                else:
                    print("PASSED: Token validation successful")
        
        except json.JSONDecodeError:
            all_issues.append({
                'severity': 'HIGH',
                'category': 'Authentication',
                'description': 'Login response is not valid JSON',
                'steps': f'1. POST to /api/v1/auth/login',
                'expected': 'Should return valid JSON response',
                'actual': f'Response: {login_result["content"][:200]}...',
                'responsible': 'Backend Agent'
            })
            print("FAILED: Invalid JSON response")
    
    # Test 4: Portfolio Data (if we have a token)
    if auth_token:
        print("\n[TEST 4] Testing Portfolio Data...")
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        portfolio_result = make_request(
            f"{BACKEND_URL}/api/v1/portfolio/",
            headers=headers
        )
        
        if portfolio_result['status'] != 200:
            all_issues.append({
                'severity': 'HIGH',
                'category': 'Portfolio Management',
                'description': f'Portfolio overview fails - Status: {portfolio_result["status"]}',
                'steps': '1. Login with demo user\n2. GET /api/v1/portfolio/',
                'expected': 'Should return 200 OK with portfolio overview data',
                'actual': f'Returned status {portfolio_result["status"]}',
                'error': portfolio_result.get('error', ''),
                'responsible': 'Backend Agent'
            })
            print("FAILED: Portfolio data not accessible")
        else:
            try:
                portfolio_data = json.loads(portfolio_result['content'])
                
                if 'portfolios' not in portfolio_data:
                    all_issues.append({
                        'severity': 'HIGH',
                        'category': 'Portfolio Management',
                        'description': 'Portfolio response missing portfolios field',
                        'steps': '1. Login with demo user\n2. GET /api/v1/portfolio/',
                        'expected': 'Should return JSON with portfolios field',
                        'actual': f'Response: {portfolio_result["content"][:200]}...',
                        'responsible': 'Backend Agent'
                    })
                    print("FAILED: Missing portfolios field")
                else:
                    portfolios = portfolio_data['portfolios']
                    if not portfolios:
                        all_issues.append({
                            'severity': 'HIGH',
                            'category': 'Data Seeding',
                            'description': 'No portfolios found for demo user - check if demo data is seeded',
                            'steps': '1. Ensure demo data is seeded\n2. Login with demo_individual@sigmasight.com\n3. Check portfolio data',
                            'expected': 'Should have at least one portfolio for demo user',
                            'actual': 'No portfolios returned in response',
                            'responsible': 'Backend Agent'
                        })
                        print("FAILED: No portfolios found - demo data issue")
                    else:
                        print(f"PASSED: Portfolio data loaded - {len(portfolios)} portfolio(s)")
            
            except json.JSONDecodeError:
                all_issues.append({
                    'severity': 'HIGH',
                    'category': 'Portfolio Management',
                    'description': 'Portfolio response is not valid JSON',
                    'steps': '1. GET /api/v1/portfolio/ with auth',
                    'expected': 'Should return valid JSON response',
                    'actual': f'Response: {portfolio_result["content"][:200]}...',
                    'responsible': 'Backend Agent'
                })
                print("FAILED: Invalid JSON response")
    else:
        print("\n[TEST 4] SKIPPED: Portfolio Data (no auth token)")
    
    # Test 5: Navigation pages
    print("\n[TEST 5] Testing Navigation Pages...")
    pages_to_test = ['/login', '/dashboard', '/positions', '/market', '/reports', '/risk', '/chat']
    
    for page in pages_to_test:
        page_result = make_request(f"{FRONTEND_URL}{page}")
        if page_result['status'] != 200:
            all_issues.append({
                'severity': 'HIGH',
                'category': 'Navigation',
                'description': f'Page {page} not accessible - Status: {page_result["status"]}',
                'steps': f'1. Navigate to {FRONTEND_URL}{page}',
                'expected': 'Should return 200 OK and load page content',
                'actual': f'Returned status {page_result["status"]}',
                'error': page_result.get('error', ''),
                'responsible': 'Frontend Agent'
            })
            print(f"FAILED: Page {page} not accessible")
        else:
            print(f"PASSED: Page {page} accessible")
    
    # Test 6: Missing API endpoints
    print("\n[TEST 6] Testing API Endpoint Coverage...")
    if auth_token:
        headers = {'Authorization': f'Bearer {auth_token}'}
        
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
                all_issues.append({
                    'severity': 'MEDIUM',
                    'category': 'API Coverage',
                    'description': f'{description} not implemented - {endpoint} returns 404',
                    'steps': f'1. Login with demo user\n2. GET {endpoint}',
                    'expected': f'Should return {description} data or appropriate response',
                    'actual': 'Endpoint returns 404 Not Found',
                    'responsible': 'Backend Agent'
                })
                print(f"MISSING: {description}")
            elif result['status'] not in [200, 401, 403]:
                all_issues.append({
                    'severity': 'LOW',
                    'category': 'API Coverage',
                    'description': f'{description} returns unexpected status {result["status"]} - {endpoint}',
                    'steps': f'1. Login with demo user\n2. GET {endpoint}',
                    'expected': 'Should return appropriate status code',
                    'actual': f'Returned status {result["status"]}',
                    'error': result.get('error', ''),
                    'responsible': 'Backend Agent'
                })
                print(f"ISSUE: {description} - Status {result['status']}")
            else:
                print(f"PASSED: {description} - Status {result['status']}")
    
    # Test 7: Error handling
    print("\n[TEST 7] Testing Error Handling...")
    
    # Test unauthorized access
    unauth_result = make_request(f"{BACKEND_URL}/api/v1/portfolio/")
    if unauth_result['status'] != 401:
        all_issues.append({
            'severity': 'HIGH',
            'category': 'Security',
            'description': f'Unauthorized access not properly rejected - Status: {unauth_result["status"]} (should be 401)',
            'steps': '1. GET /api/v1/portfolio/ without auth token',
            'expected': 'Should return 401 Unauthorized',
            'actual': f'Returned status {unauth_result["status"]}',
            'responsible': 'Backend Agent'
        })
        print("FAILED: Unauthorized access not properly rejected")
    else:
        print("PASSED: Unauthorized access properly rejected")
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TESTING REPORT")
    print("=" * 80)
    
    if not all_issues:
        print("*** NO ISSUES FOUND! ***")
        print("The core application functionality is working correctly.")
        return 0
    
    # Group by severity
    critical_issues = [i for i in all_issues if i.get('severity') == 'CRITICAL']
    high_issues = [i for i in all_issues if i.get('severity') == 'HIGH']
    medium_issues = [i for i in all_issues if i.get('severity') == 'MEDIUM']
    low_issues = [i for i in all_issues if i.get('severity') == 'LOW']
    
    total_issues = len(all_issues)
    
    print(f"\nSUMMARY: {total_issues} TOTAL ISSUES FOUND")
    print("-" * 40)
    if critical_issues:
        print(f"CRITICAL: {len(critical_issues)} issues")
    if high_issues:
        print(f"HIGH: {len(high_issues)} issues")
    if medium_issues:
        print(f"MEDIUM: {len(medium_issues)} issues")
    if low_issues:
        print(f"LOW: {len(low_issues)} issues")
    
    # Group by responsible agent
    print(f"\nISSUES BY RESPONSIBLE AGENT:")
    print("-" * 40)
    issues_by_agent = {}
    for issue in all_issues:
        agent = issue.get('responsible', 'Unknown')
        if agent not in issues_by_agent:
            issues_by_agent[agent] = 0
        issues_by_agent[agent] += 1
        
    for agent, count in sorted(issues_by_agent.items()):
        print(f"* {agent}: {count} issues")
    
    # Detailed issue listing
    print(f"\nDETAILED ISSUES:")
    print("=" * 80)
    
    issue_num = 1
    for severity, issues_list in [
        ('CRITICAL', critical_issues),
        ('HIGH', high_issues), 
        ('MEDIUM', medium_issues),
        ('LOW', low_issues)
    ]:
        if not issues_list:
            continue
            
        print(f"\n{severity} SEVERITY ISSUES:")
        print("-" * 50)
        
        for issue in issues_list:
            print(f"\n#{issue_num}. {issue['description']}")
            print(f"   Severity: {issue['severity']}")
            print(f"   Category: {issue['category']}")
            print(f"   Responsible: {issue['responsible']}")
            print(f"   \nSteps to Reproduce:")
            for line in issue.get('steps', '').split('\n'):
                print(f"     {line}")
            print(f"   \nExpected Behavior:")
            print(f"     {issue.get('expected', '')}")
            print(f"   \nActual Behavior:")
            print(f"     {issue.get('actual', '')}")
            
            if issue.get('error'):
                print(f"   \nError Details:")
                print(f"     {issue['error']}")
                
            if issue.get('details'):
                print(f"   \nAdditional Details:")
                print(f"     {issue['details'][:300]}...")
            
            print("-" * 50)
            issue_num += 1
    
    # Action items
    print(f"\nIMMEDIATE ACTION ITEMS:")
    print("=" * 40)
    
    if critical_issues:
        print("*** CRITICAL - Fix Immediately Before Any Releases:")
        for issue in critical_issues:
            print(f"   * {issue['description']} ({issue['responsible']})")
    
    if high_issues:
        print("\n*** HIGH PRIORITY - Fix This Sprint:")
        for issue in high_issues:
            print(f"   * {issue['description']} ({issue['responsible']})")
    
    print(f"\nRECOMMENDATIONS:")
    print("-" * 30)
    print("1. Address all CRITICAL issues before any releases")
    print("2. Create tickets for each HIGH priority issue")
    print("3. Review missing API endpoints and implement as needed")
    print("4. Ensure demo data is properly seeded for testing")
    print("5. Add automated testing for all found issues")
    print("6. Implement proper error handling and user feedback")
    
    # Return exit code based on severity
    if critical_issues:
        print(f"\n*** TESTING FAILED: Critical issues found! ***")
        return 1
    elif high_issues:
        print(f"\n*** TESTING COMPLETED: High priority issues need attention ***")
        return 2
    else:
        print(f"\n*** TESTING COMPLETED: Only minor issues found ***")
        return 0

if __name__ == "__main__":
    try:
        exit_code = run_comprehensive_test()
        print(f"\nTesting completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTesting failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
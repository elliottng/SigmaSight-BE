#!/usr/bin/env python3
"""
SigmaSight Comprehensive End-to-End Testing Script
===================================================

This script performs comprehensive automated testing of the SigmaSight application
to identify ALL issues, bugs, errors, and problems before they reach users.

Usage: 
    python scripts/comprehensive_e2e_testing.py

Requirements:
    - Frontend running on http://localhost:3008  
    - Backend running on http://localhost:8001
    - Database accessible and seeded with demo data
"""

import json
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configuration
FRONTEND_URL = "http://localhost:3008"
BACKEND_URL = "http://localhost:8001"
DEMO_USER_EMAIL = "demo_individual@sigmasight.com"
DEMO_USER_PASSWORD = "password123"

class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ResponsibleAgent(Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    PERFORMANCE = "Performance"
    DOCUMENTATION = "Documentation"

@dataclass
class Issue:
    description: str
    steps_to_reproduce: str
    expected_behavior: str
    actual_behavior: str
    severity: Severity
    responsible_agent: ResponsibleAgent
    test_category: str
    timestamp: datetime
    additional_data: Optional[Dict] = None

class ComprehensiveE2ETester:
    def __init__(self):
        self.issues: List[Issue] = []
        self.session = requests.Session()
        self.session.timeout = 30
        self.session.headers.update({'User-Agent': 'SigmaSight-E2E-Tester/1.0'})
        self.auth_token: Optional[str] = None
        self.user_data: Optional[Dict] = None
        self.portfolios: List[Dict] = []
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            self.session.close()

    def log_issue(self, 
                  description: str,
                  steps: str,
                  expected: str,
                  actual: str,
                  severity: Severity,
                  agent: ResponsibleAgent,
                  category: str,
                  additional_data: Optional[Dict] = None):
        """Log a discovered issue"""
        issue = Issue(
            description=description,
            steps_to_reproduce=steps,
            expected_behavior=expected,
            actual_behavior=actual,
            severity=severity,
            responsible_agent=agent,
            test_category=category,
            timestamp=datetime.now(),
            additional_data=additional_data
        )
        self.issues.append(issue)
        print(f"🚨 [{severity.value}] {description}")

    def test_frontend_availability(self):
        """Test 1: Frontend Availability and Load Time"""
        print("\n=== Testing Frontend Availability ===")
        
        try:
            start_time = time.time()
            response = self.session.get(FRONTEND_URL)
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_issue(
                    "Frontend not accessible",
                    "1. Navigate to http://localhost:3008",
                    "Should return 200 OK and load homepage",
                    f"Returned status {response.status_code}",
                    Severity.CRITICAL,
                    ResponsibleAgent.FRONTEND,
                    "Homepage/Landing"
                )
                return False
                
            if load_time > 3.0:
                self.log_issue(
                    "Frontend loads slowly",
                    "1. Navigate to http://localhost:3008\n2. Measure load time",
                    "Should load in under 3 seconds",
                    f"Took {load_time:.2f} seconds to load",
                    Severity.MEDIUM,
                    ResponsibleAgent.PERFORMANCE,
                    "Homepage/Landing"
                )
            
            content = response.text
            if "SigmaSight" not in content:
                self.log_issue(
                    "Homepage missing SigmaSight branding",
                    "1. Navigate to http://localhost:3008\n2. Check page content",
                    "Should display SigmaSight branding",
                    "SigmaSight branding not found in page content",
                    Severity.MEDIUM,
                    ResponsibleAgent.FRONTEND,
                    "Homepage/Landing"
                )
            
            print("✅ Frontend is accessible and loading")
            return True
                
        except Exception as e:
            self.log_issue(
                "Frontend completely inaccessible",
                "1. Navigate to http://localhost:3008",
                "Should successfully connect and load page",
                f"Connection failed with error: {str(e)}",
                Severity.CRITICAL,
                ResponsibleAgent.FRONTEND,
                "Homepage/Landing",
                {"error": str(e)}
            )
            return False

    async def test_backend_availability(self):
        """Test 2: Backend API Availability"""
        print("\n=== Testing Backend Availability ===")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/docs") as response:
                if response.status != 200:
                    self.log_issue(
                        "Backend API documentation not accessible",
                        "1. Navigate to http://localhost:8001/docs",
                        "Should return 200 OK and show API documentation",
                        f"Returned status {response.status}",
                        Severity.HIGH,
                        ResponsibleAgent.BACKEND,
                        "API Documentation"
                    )
                    return False
                    
            print("✅ Backend API is accessible")
            return True
            
        except Exception as e:
            self.log_issue(
                "Backend API completely inaccessible",
                "1. Navigate to http://localhost:8001/docs",
                "Should successfully connect and show API docs",
                f"Connection failed with error: {str(e)}",
                Severity.CRITICAL,
                ResponsibleAgent.BACKEND,
                "API Documentation",
                {"error": str(e)}
            )
            return False

    async def test_authentication_flow(self):
        """Test 3: Login Process"""
        print("\n=== Testing Authentication Flow ===")
        
        try:
            # Test login endpoint
            login_data = {
                "email": DEMO_USER_EMAIL,
                "password": DEMO_USER_PASSWORD
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/api/v1/auth/login", 
                json=login_data
            ) as response:
                
                if response.status != 200:
                    self.log_issue(
                        "Login endpoint returns non-200 status",
                        f"1. POST to /api/v1/auth/login with email: {DEMO_USER_EMAIL}, password: {DEMO_USER_PASSWORD}",
                        "Should return 200 OK with access token",
                        f"Returned status {response.status}",
                        Severity.CRITICAL,
                        ResponsibleAgent.BACKEND,
                        "Login Process"
                    )
                    return False
                
                auth_response = await response.json()
                
                if "access_token" not in auth_response:
                    self.log_issue(
                        "Login response missing access token",
                        f"1. POST to /api/v1/auth/login with valid credentials",
                        "Should return JSON with 'access_token' field",
                        f"Response: {auth_response}",
                        Severity.CRITICAL,
                        ResponsibleAgent.BACKEND,
                        "Login Process",
                        {"response": auth_response}
                    )
                    return False
                
                self.auth_token = auth_response["access_token"]
                print("✅ Login successful - token obtained")
                
                # Test token validation
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                async with self.session.get(
                    f"{BACKEND_URL}/api/v1/auth/me", 
                    headers=headers
                ) as me_response:
                    
                    if me_response.status != 200:
                        self.log_issue(
                            "Token validation fails",
                            "1. Login to get token\n2. GET /api/v1/auth/me with Authorization header",
                            "Should return 200 OK with user data",
                            f"Returned status {me_response.status}",
                            Severity.HIGH,
                            ResponsibleAgent.BACKEND,
                            "Login Process"
                        )
                        return False
                    
                    self.user_data = await me_response.json()
                    print("✅ Token validation successful")
                    return True
                    
        except Exception as e:
            self.log_issue(
                "Authentication flow completely broken",
                "1. Attempt to login with demo credentials",
                "Should complete authentication flow successfully",
                f"Failed with error: {str(e)}",
                Severity.CRITICAL,
                ResponsibleAgent.BACKEND,
                "Login Process",
                {"error": str(e)}
            )
            return False

    async def test_portfolio_data_loading(self):
        """Test 4: Portfolio Data Loading"""
        print("\n=== Testing Portfolio Data Loading ===")
        
        if not self.auth_token:
            self.log_issue(
                "Cannot test portfolio data - no auth token",
                "1. Login first\n2. Attempt to load portfolio data",
                "Should have valid auth token from login",
                "No auth token available",
                Severity.CRITICAL,
                ResponsibleAgent.BACKEND,
                "Portfolio Management"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test portfolio overview endpoint
            async with self.session.get(
                f"{BACKEND_URL}/api/v1/portfolio/", 
                headers=headers
            ) as response:
                
                if response.status != 200:
                    self.log_issue(
                        "Portfolio overview endpoint not working",
                        "1. Login with demo user\n2. GET /api/v1/portfolio/",
                        "Should return 200 OK with portfolio overview data",
                        f"Returned status {response.status}",
                        Severity.HIGH,
                        ResponsibleAgent.BACKEND,
                        "Portfolio Management"
                    )
                    return False
                
                portfolio_data = await response.json()
                
                # Check for required fields
                required_fields = ["portfolios"]
                missing_fields = [field for field in required_fields if field not in portfolio_data]
                
                if missing_fields:
                    self.log_issue(
                        "Portfolio overview missing required fields",
                        "1. Login with demo user\n2. GET /api/v1/portfolio/",
                        f"Should return JSON with fields: {required_fields}",
                        f"Missing fields: {missing_fields}. Response: {portfolio_data}",
                        Severity.HIGH,
                        ResponsibleAgent.BACKEND,
                        "Portfolio Management",
                        {"response": portfolio_data, "missing_fields": missing_fields}
                    )
                
                self.portfolios = portfolio_data.get("portfolios", [])
                if not self.portfolios:
                    self.log_issue(
                        "No portfolios found for demo user",
                        "1. Ensure demo data is seeded\n2. Login with demo_individual@sigmasight.com\n3. Check portfolio data",
                        "Should have at least one portfolio for demo user",
                        "No portfolios returned in response",
                        Severity.HIGH,
                        ResponsibleAgent.BACKEND,
                        "Portfolio Management",
                        {"response": portfolio_data}
                    )
                    return False
                
                print(f"✅ Portfolio data loaded - {len(self.portfolios)} portfolio(s) found")
                return True
                
        except Exception as e:
            self.log_issue(
                "Portfolio data loading completely broken",
                "1. Attempt to load portfolio data with valid auth",
                "Should successfully load portfolio data",
                f"Failed with error: {str(e)}",
                Severity.CRITICAL,
                ResponsibleAgent.BACKEND,
                "Portfolio Management",
                {"error": str(e)}
            )
            return False

    async def test_dashboard_features(self):
        """Test 5: Dashboard Features"""
        print("\n=== Testing Dashboard Features ===")
        
        if not self.auth_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test alerts endpoint (expecting 404 based on logs)
            async with self.session.get(
                f"{BACKEND_URL}/api/v1/alerts", 
                headers=headers
            ) as response:
                
                if response.status == 404:
                    self.log_issue(
                        "Alerts endpoint not implemented",
                        "1. Login with demo user\n2. GET /api/v1/alerts",
                        "Should return alerts data or empty array",
                        "Endpoint returns 404 Not Found",
                        Severity.MEDIUM,
                        ResponsibleAgent.BACKEND,
                        "Dashboard"
                    )
                elif response.status != 200:
                    self.log_issue(
                        "Alerts endpoint returns error",
                        "1. Login with demo user\n2. GET /api/v1/alerts",
                        "Should return 200 OK with alerts data",
                        f"Returned status {response.status}",
                        Severity.MEDIUM,
                        ResponsibleAgent.BACKEND,
                        "Dashboard"
                    )
                
                # Test critical alerts endpoint
                async with self.session.get(
                    f"{BACKEND_URL}/api/v1/alerts?priority=critical", 
                    headers=headers
                ) as crit_response:
                    
                    if crit_response.status == 404:
                        self.log_issue(
                            "Critical alerts filtering not implemented",
                            "1. Login with demo user\n2. GET /api/v1/alerts?priority=critical",
                            "Should return filtered alerts data",
                            "Endpoint returns 404 Not Found",
                            Severity.MEDIUM,
                            ResponsibleAgent.BACKEND,
                            "Dashboard"
                        )
            
            print("✅ Dashboard features tested (some endpoints missing)")
            return True
            
        except Exception as e:
            self.log_issue(
                "Dashboard features testing failed",
                "1. Attempt to test dashboard API endpoints",
                "Should successfully test dashboard features",
                f"Failed with error: {str(e)}",
                Severity.HIGH,
                ResponsibleAgent.BACKEND,
                "Dashboard",
                {"error": str(e)}
            )
            return False

    async def test_navigation_endpoints(self):
        """Test 6: Navigation and Page Endpoints"""
        print("\n=== Testing Navigation Endpoints ===")
        
        test_pages = [
            "/login",
            "/dashboard", 
            "/positions",
            "/market",
            "/reports",
            "/risk",
            "/chat"
        ]
        
        for page in test_pages:
            try:
                async with self.session.get(f"{FRONTEND_URL}{page}") as response:
                    if response.status != 200:
                        self.log_issue(
                            f"Page {page} not accessible",
                            f"1. Navigate to {FRONTEND_URL}{page}",
                            "Should return 200 OK and load page content",
                            f"Returned status {response.status}",
                            Severity.HIGH,
                            ResponsibleAgent.FRONTEND,
                            "Navigation"
                        )
                    else:
                        print(f"✅ Page {page} accessible")
                        
            except Exception as e:
                self.log_issue(
                    f"Page {page} completely inaccessible",
                    f"1. Navigate to {FRONTEND_URL}{page}",
                    "Should successfully load page",
                    f"Failed with error: {str(e)}",
                    Severity.HIGH,
                    ResponsibleAgent.FRONTEND,
                    "Navigation",
                    {"error": str(e)}
                )
        
        return True

    async def test_positions_management(self):
        """Test 7: Positions Management"""
        print("\n=== Testing Positions Management ===")
        
        if not self.auth_token or not self.portfolios:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for portfolio in self.portfolios[:1]:  # Test first portfolio only
                portfolio_id = portfolio.get("id")
                if not portfolio_id:
                    continue
                    
                # Test positions endpoint
                async with self.session.get(
                    f"{BACKEND_URL}/api/v1/positions/{portfolio_id}", 
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        self.log_issue(
                            "Positions endpoint not working",
                            f"1. Login with demo user\n2. GET /api/v1/positions/{portfolio_id}",
                            "Should return 200 OK with positions data",
                            f"Returned status {response.status}",
                            Severity.HIGH,
                            ResponsibleAgent.BACKEND,
                            "Portfolio Management"
                        )
                        continue
                    
                    positions_data = await response.json()
                    positions = positions_data.get("positions", [])
                    
                    if not positions:
                        self.log_issue(
                            "No positions found for demo portfolio",
                            f"1. Ensure demo data is seeded\n2. GET positions for portfolio {portfolio_id}",
                            "Should return positions for demo portfolio",
                            "No positions found",
                            Severity.MEDIUM,
                            ResponsibleAgent.BACKEND,
                            "Portfolio Management",
                            {"response": positions_data}
                        )
                    else:
                        print(f"✅ Positions loaded - {len(positions)} position(s) found")
            
            return True
            
        except Exception as e:
            self.log_issue(
                "Positions management completely broken",
                "1. Attempt to load positions data",
                "Should successfully load positions",
                f"Failed with error: {str(e)}",
                Severity.CRITICAL,
                ResponsibleAgent.BACKEND,
                "Portfolio Management",
                {"error": str(e)}
            )
            return False

    async def test_risk_analytics(self):
        """Test 8: Risk Analytics Features"""
        print("\n=== Testing Risk Analytics ===")
        
        if not self.auth_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test risk endpoints
            risk_endpoints = [
                "/api/v1/risk/greeks",
                "/api/v1/risk/factors", 
                "/api/v1/risk/scenarios"
            ]
            
            for endpoint in risk_endpoints:
                try:
                    async with self.session.get(
                        f"{BACKEND_URL}{endpoint}", 
                        headers=headers
                    ) as response:
                        
                        if response.status == 404:
                            self.log_issue(
                                f"Risk endpoint {endpoint} not implemented",
                                f"1. Login with demo user\n2. GET {endpoint}",
                                "Should return risk analytics data",
                                "Endpoint returns 404 Not Found",
                                Severity.MEDIUM,
                                ResponsibleAgent.BACKEND,
                                "Risk Analytics"
                            )
                        elif response.status != 200:
                            self.log_issue(
                                f"Risk endpoint {endpoint} returns error",
                                f"1. Login with demo user\n2. GET {endpoint}",
                                "Should return 200 OK with risk data",
                                f"Returned status {response.status}",
                                Severity.MEDIUM,
                                ResponsibleAgent.BACKEND,
                                "Risk Analytics"
                            )
                        else:
                            print(f"✅ Risk endpoint {endpoint} working")
                            
                except Exception as e:
                    self.log_issue(
                        f"Risk endpoint {endpoint} completely inaccessible",
                        f"1. GET {endpoint}",
                        "Should be accessible",
                        f"Failed with error: {str(e)}",
                        Severity.MEDIUM,
                        ResponsibleAgent.BACKEND,
                        "Risk Analytics",
                        {"error": str(e)}
                    )
            
            return True
            
        except Exception as e:
            self.log_issue(
                "Risk analytics testing failed",
                "1. Attempt to test risk analytics endpoints",
                "Should successfully test risk features",
                f"Failed with error: {str(e)}",
                Severity.HIGH,
                ResponsibleAgent.BACKEND,
                "Risk Analytics",
                {"error": str(e)}
            )
            return False

    async def test_market_data(self):
        """Test 9: Market Data Features"""
        print("\n=== Testing Market Data Features ===")
        
        if not self.auth_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test market data endpoint
            async with self.session.get(
                f"{BACKEND_URL}/api/v1/market-data/quotes", 
                headers=headers
            ) as response:
                
                if response.status == 404:
                    self.log_issue(
                        "Market data quotes endpoint not implemented",
                        "1. Login with demo user\n2. GET /api/v1/market-data/quotes",
                        "Should return market quotes data",
                        "Endpoint returns 404 Not Found",
                        Severity.MEDIUM,
                        ResponsibleAgent.BACKEND,
                        "Market Data"
                    )
                elif response.status != 200:
                    self.log_issue(
                        "Market data endpoint returns error",
                        "1. Login with demo user\n2. GET /api/v1/market-data/quotes",
                        "Should return 200 OK with market data",
                        f"Returned status {response.status}",
                        Severity.MEDIUM,
                        ResponsibleAgent.BACKEND,
                        "Market Data"
                    )
                else:
                    print("✅ Market data endpoint working")
            
            return True
            
        except Exception as e:
            self.log_issue(
                "Market data testing failed",
                "1. Attempt to test market data endpoints",
                "Should successfully test market data features",
                f"Failed with error: {str(e)}",
                Severity.HIGH,
                ResponsibleAgent.BACKEND,
                "Market Data",
                {"error": str(e)}
            )
            return False

    async def test_reports_generation(self):
        """Test 10: Reports Generation"""
        print("\n=== Testing Reports Generation ===")
        
        if not self.auth_token or not self.portfolios:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for portfolio in self.portfolios[:1]:  # Test first portfolio only
                portfolio_id = portfolio.get("id")
                if not portfolio_id:
                    continue
                    
                # Test reports endpoint
                async with self.session.get(
                    f"{BACKEND_URL}/api/v1/reports/{portfolio_id}", 
                    headers=headers
                ) as response:
                    
                    if response.status == 404:
                        self.log_issue(
                            "Reports endpoint not implemented",
                            f"1. Login with demo user\n2. GET /api/v1/reports/{portfolio_id}",
                            "Should return portfolio report or generation status",
                            "Endpoint returns 404 Not Found",
                            Severity.MEDIUM,
                            ResponsibleAgent.BACKEND,
                            "Reports"
                        )
                    elif response.status != 200:
                        self.log_issue(
                            "Reports endpoint returns error",
                            f"1. Login with demo user\n2. GET /api/v1/reports/{portfolio_id}",
                            "Should return 200 OK with report data",
                            f"Returned status {response.status}",
                            Severity.MEDIUM,
                            ResponsibleAgent.BACKEND,
                            "Reports"
                        )
                    else:
                        print("✅ Reports endpoint working")
            
            return True
            
        except Exception as e:
            self.log_issue(
                "Reports testing failed",
                "1. Attempt to test reports generation",
                "Should successfully test reports features",
                f"Failed with error: {str(e)}",
                Severity.HIGH,
                ResponsibleAgent.BACKEND,
                "Reports",
                {"error": str(e)}
            )
            return False

    async def test_error_handling(self):
        """Test 11: Error Handling"""
        print("\n=== Testing Error Handling ===")
        
        try:
            # Test invalid endpoints
            invalid_endpoints = [
                "/api/v1/nonexistent",
                "/api/v1/portfolio/invalid-uuid",
                "/api/v1/positions/not-a-uuid"
            ]
            
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            for endpoint in invalid_endpoints:
                async with self.session.get(
                    f"{BACKEND_URL}{endpoint}", 
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        self.log_issue(
                            f"Invalid endpoint {endpoint} returns 200",
                            f"1. GET {endpoint}",
                            "Should return appropriate error status (400, 404, etc.)",
                            "Returns 200 OK inappropriately",
                            Severity.MEDIUM,
                            ResponsibleAgent.BACKEND,
                            "Error Handling"
                        )
                    
                    # Check if error response has proper structure
                    try:
                        error_data = await response.json()
                        if not isinstance(error_data, dict) or "detail" not in error_data:
                            self.log_issue(
                                f"Poor error response format for {endpoint}",
                                f"1. GET {endpoint}",
                                "Should return structured error with 'detail' field",
                                f"Response: {error_data}",
                                Severity.LOW,
                                ResponsibleAgent.BACKEND,
                                "Error Handling",
                                {"response": error_data}
                            )
                    except:
                        pass  # Non-JSON response is acceptable for some errors
            
            # Test unauthorized access
            async with self.session.get(f"{BACKEND_URL}/api/v1/portfolio/") as response:
                if response.status != 401:
                    self.log_issue(
                        "Unauthorized access not properly rejected",
                        "1. GET /api/v1/portfolio/ without auth token",
                        "Should return 401 Unauthorized",
                        f"Returned status {response.status}",
                        Severity.HIGH,
                        ResponsibleAgent.BACKEND,
                        "Error Handling"
                    )
            
            print("✅ Error handling tests completed")
            return True
            
        except Exception as e:
            self.log_issue(
                "Error handling testing failed",
                "1. Attempt to test error handling scenarios",
                "Should successfully test error responses",
                f"Failed with error: {str(e)}",
                Severity.MEDIUM,
                ResponsibleAgent.BACKEND,
                "Error Handling",
                {"error": str(e)}
            )
            return False

    async def test_performance_metrics(self):
        """Test 12: Performance and Response Times"""
        print("\n=== Testing Performance Metrics ===")
        
        if not self.auth_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test response times for key endpoints
            performance_tests = [
                ("/api/v1/portfolio/", 2.0),  # Should respond in under 2s
                ("/api/v1/auth/me", 1.0),     # Should respond in under 1s
            ]
            
            for endpoint, max_time in performance_tests:
                start_time = time.time()
                async with self.session.get(
                    f"{BACKEND_URL}{endpoint}", 
                    headers=headers
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response_time > max_time:
                        self.log_issue(
                            f"Slow response time for {endpoint}",
                            f"1. Login with demo user\n2. GET {endpoint}\n3. Measure response time",
                            f"Should respond in under {max_time} seconds",
                            f"Took {response_time:.2f} seconds to respond",
                            Severity.MEDIUM,
                            ResponsibleAgent.PERFORMANCE,
                            "Performance",
                            {"response_time": response_time, "max_allowed": max_time}
                        )
                    else:
                        print(f"✅ {endpoint} response time: {response_time:.2f}s")
            
            return True
            
        except Exception as e:
            self.log_issue(
                "Performance testing failed",
                "1. Attempt to measure API response times",
                "Should successfully measure performance metrics",
                f"Failed with error: {str(e)}",
                Severity.MEDIUM,
                ResponsibleAgent.PERFORMANCE,
                "Performance",
                {"error": str(e)}
            )
            return False

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🔥 Starting Comprehensive End-to-End Testing for SigmaSight")
        print("=" * 60)
        
        # Run all test categories
        test_results = []
        
        test_functions = [
            ("Frontend Availability", self.test_frontend_availability),
            ("Backend Availability", self.test_backend_availability),
            ("Authentication Flow", self.test_authentication_flow),
            ("Portfolio Data Loading", self.test_portfolio_data_loading),
            ("Dashboard Features", self.test_dashboard_features),
            ("Navigation Endpoints", self.test_navigation_endpoints),
            ("Positions Management", self.test_positions_management),
            ("Risk Analytics", self.test_risk_analytics),
            ("Market Data", self.test_market_data),
            ("Reports Generation", self.test_reports_generation),
            ("Error Handling", self.test_error_handling),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        for test_name, test_func in test_functions:
            try:
                result = await test_func()
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                test_results.append((test_name, False))
                self.log_issue(
                    f"{test_name} test suite failed",
                    f"1. Run {test_name} test",
                    "Test should complete successfully", 
                    f"Failed with exception: {str(e)}",
                    Severity.HIGH,
                    ResponsibleAgent.BACKEND,
                    "Testing Framework",
                    {"error": str(e)}
                )

    def generate_report(self):
        """Generate comprehensive issue report"""
        print("\n" + "=" * 80)
        print("🚨 COMPREHENSIVE TESTING REPORT")
        print("=" * 80)
        
        if not self.issues:
            print("✅ NO ISSUES FOUND! The application appears to be working correctly.")
            return
            
        # Group issues by severity
        issues_by_severity = {}
        for issue in self.issues:
            severity = issue.severity.value
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        # Print summary
        total_issues = len(self.issues)
        print(f"\n📊 SUMMARY: {total_issues} TOTAL ISSUES FOUND")
        print("-" * 40)
        
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            count = len(issues_by_severity.get(severity.value, []))
            if count > 0:
                print(f"🔴 {severity.value}: {count} issues")
        
        # Group by responsible agent
        print(f"\n👥 ISSUES BY RESPONSIBLE AGENT:")
        print("-" * 40)
        issues_by_agent = {}
        for issue in self.issues:
            agent = issue.responsible_agent.value
            if agent not in issues_by_agent:
                issues_by_agent[agent] = 0
            issues_by_agent[agent] += 1
            
        for agent, count in sorted(issues_by_agent.items()):
            print(f"• {agent}: {count} issues")
        
        # Detailed issue listing
        print(f"\n📋 DETAILED ISSUES:")
        print("=" * 80)
        
        issue_num = 1
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            severity_issues = issues_by_severity.get(severity.value, [])
            if not severity_issues:
                continue
                
            print(f"\n🔴 {severity.value} SEVERITY ISSUES:")
            print("-" * 50)
            
            for issue in severity_issues:
                print(f"\n#{issue_num}. {issue.description}")
                print(f"   Severity: {issue.severity.value}")
                print(f"   Responsible: {issue.responsible_agent.value}")
                print(f"   Category: {issue.test_category}")
                print(f"   Timestamp: {issue.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   \nSteps to Reproduce:")
                for line in issue.steps_to_reproduce.split('\n'):
                    print(f"     {line}")
                print(f"   \nExpected Behavior:")
                print(f"     {issue.expected_behavior}")
                print(f"   \nActual Behavior:")
                print(f"     {issue.actual_behavior}")
                
                if issue.additional_data:
                    print(f"   \nAdditional Data:")
                    print(f"     {issue.additional_data}")
                
                print("-" * 50)
                issue_num += 1
        
        # Action items
        print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
        print("=" * 40)
        
        critical_issues = issues_by_severity.get(Severity.CRITICAL.value, [])
        high_issues = issues_by_severity.get(Severity.HIGH.value, [])
        
        if critical_issues:
            print("🚨 CRITICAL - Fix Immediately:")
            for issue in critical_issues:
                print(f"   • {issue.description} ({issue.responsible_agent.value})")
        
        if high_issues:
            print("\n🔥 HIGH PRIORITY - Fix This Sprint:")
            for issue in high_issues:
                print(f"   • {issue.description} ({issue.responsible_agent.value})")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 30)
        print("1. Address all CRITICAL issues before any releases")
        print("2. Create tickets for each HIGH priority issue")
        print("3. Review error handling and user experience")
        print("4. Implement comprehensive monitoring")
        print("5. Add automated testing for all found issues")
        
        return self.issues

async def main():
    """Main entry point"""
    print("SigmaSight Comprehensive E2E Testing Starting...")
    
    async with ComprehensiveE2ETester() as tester:
        await tester.run_comprehensive_tests()
        issues = tester.generate_report()
        
        # Return exit code based on severity of issues found
        if any(issue.severity == Severity.CRITICAL for issue in issues):
            print(f"\n❌ TESTING FAILED: Critical issues found!")
            return 1
        elif any(issue.severity == Severity.HIGH for issue in issues):
            print(f"\n⚠️  TESTING COMPLETED: High priority issues need attention")
            return 2
        else:
            print(f"\n✅ TESTING COMPLETED: Only minor issues found")
            return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {e}")
        sys.exit(1)
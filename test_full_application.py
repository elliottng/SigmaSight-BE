#!/usr/bin/env python3
"""
Comprehensive SigmaSight Application Testing Script

This script tests the complete application flow:
1. Backend API functionality  
2. Frontend page loading
3. Authentication flow
4. Main application features
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8001/api/v1"
FRONTEND_URL = "http://localhost:3008"

def test_backend_health() -> bool:
    """Test if backend is responding"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"✅ Backend Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend Health: {e}")
        return False

def test_frontend_health() -> bool:
    """Test if frontend is responding"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        print(f"✅ Frontend Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Frontend Health: {e}")
        return False

def test_login_flow() -> str:
    """Test login and return JWT token"""
    try:
        login_data = {
            "email": "demo_individual@sigmasight.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            print(f"✅ Login Success: {user.get('email')} ({user.get('full_name')})")
            return token
        else:
            print(f"❌ Login Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return None

def test_portfolio_api(token: str) -> bool:
    """Test portfolio API with authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/portfolio/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            portfolios = data.get("portfolios", [])
            print(f"✅ Portfolio API: {len(portfolios)} portfolios found")
            
            # Print portfolio details
            for portfolio in portfolios:
                print(f"   Portfolio: {portfolio['name']} (${portfolio['total_market_value']:,.0f})")
                print(f"   Positions: {portfolio['position_count']} positions")
                
            return True
        else:
            print(f"❌ Portfolio API Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Portfolio API Error: {e}")
        return False

def test_market_data_api(token: str) -> bool:
    """Test market data API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/market-data/prices/AAPL", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market Data API: {len(data)} AAPL price records")
            
            # Show latest price
            if data:
                latest = data[0]
                print(f"   AAPL Latest: ${latest['close']} on {latest['date']}")
                
            return True
        else:
            print(f"❌ Market Data API Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Market Data API Error: {e}")
        return False

def test_reports_api(token: str) -> bool:
    """Test reports API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/reports/portfolios", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reports API: {len(data)} reports available")
            
            for report in data:
                print(f"   Report: {report['name']} ({', '.join(report['formats_available'])})")
                
            return True
        else:
            print(f"❌ Reports API Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Reports API Error: {e}")
        return False

def test_frontend_pages() -> Dict[str, bool]:
    """Test frontend page loading"""
    pages = {
        "login": f"{FRONTEND_URL}/login",
        "register": f"{FRONTEND_URL}/register", 
        "dashboard": f"{FRONTEND_URL}/dashboard",
        "positions": f"{FRONTEND_URL}/positions",
        "risk": f"{FRONTEND_URL}/risk",
        "market": f"{FRONTEND_URL}/market",
        "reports": f"{FRONTEND_URL}/reports"
    }
    
    results = {}
    
    for name, url in pages.items():
        try:
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            results[name] = success
            
            status = "✅" if success else "❌"
            print(f"{status} Frontend {name.capitalize()}: {response.status_code}")
            
        except Exception as e:
            results[name] = False
            print(f"❌ Frontend {name.capitalize()}: {e}")
    
    return results

def main():
    """Run comprehensive application testing"""
    print("🔍 SigmaSight Application Testing")
    print("=" * 50)
    
    # Test backend health
    print("\n📡 Backend Testing:")
    if not test_backend_health():
        print("❌ Backend is not responding. Please check if backend server is running.")
        return
    
    # Test frontend health  
    print("\n🌐 Frontend Testing:")
    if not test_frontend_health():
        print("❌ Frontend is not responding. Please check if frontend server is running.")
        return
        
    # Test authentication
    print("\n🔐 Authentication Testing:")
    token = test_login_flow()
    if not token:
        print("❌ Cannot proceed without valid authentication token.")
        return
    
    # Test API endpoints
    print("\n📊 API Endpoints Testing:")
    test_portfolio_api(token)
    test_market_data_api(token)
    test_reports_api(token)
    
    # Test frontend pages
    print("\n📱 Frontend Pages Testing:")
    page_results = test_frontend_pages()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 50)
    
    backend_working = token is not None
    frontend_working = all(page_results.values())
    
    print(f"Backend API: {'✅ Working' if backend_working else '❌ Issues Found'}")
    print(f"Frontend Pages: {'✅ Working' if frontend_working else '❌ Issues Found'}")
    
    if backend_working and frontend_working:
        print("\n🎉 All tests passed! SigmaSight application is ready to use.")
        print(f"\n🌐 Access the application at: {FRONTEND_URL}")
        print("📧 Demo credentials:")
        print("   Email: demo_individual@sigmasight.com")
        print("   Password: password123")
    else:
        print("\n⚠️  Some issues were found. Please review the test results above.")

if __name__ == "__main__":
    main()
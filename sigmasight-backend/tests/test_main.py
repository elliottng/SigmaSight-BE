"""
Tests for main FastAPI application
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SigmaSight Backend API"
    assert data["version"] == "1.0.0"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_api_v1_auth_endpoints():
    """Test API v1 auth endpoints are accessible"""
    # Test login endpoint
    response = client.post("/api/v1/auth/login")
    assert response.status_code == 200
    
    # Test register endpoint
    response = client.post("/api/v1/auth/register")
    assert response.status_code == 200
    
    # Test refresh endpoint
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200

def test_api_v1_portfolio_endpoints():
    """Test API v1 portfolio endpoints are accessible"""
    # Test portfolio overview
    response = client.get("/api/v1/portfolio/")
    assert response.status_code == 200
    
    # Test portfolio upload
    response = client.post("/api/v1/portfolio/upload")
    assert response.status_code == 200
    
    # Test portfolio summary
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200

def test_api_v1_risk_endpoints():
    """Test API v1 risk endpoints are accessible"""
    # Test risk metrics
    response = client.get("/api/v1/risk/metrics")
    assert response.status_code == 200
    
    # Test factor exposures
    response = client.get("/api/v1/risk/factors")
    assert response.status_code == 200
    
    # Test Greeks
    response = client.get("/api/v1/risk/greeks")
    assert response.status_code == 200

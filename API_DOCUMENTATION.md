# SigmaSight API Documentation

**Version**: 1.4  
**Last Updated**: August 26, 2025  
**Base URL**: http://localhost:8001/api/v1  
**OpenAPI Spec**: http://localhost:8001/docs  

## Overview

This document provides comprehensive API documentation for the SigmaSight portfolio risk management platform backend services. The API follows RESTful principles with JSON request/response formats and JWT authentication.

## Architecture

### Backend Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  API Routes (app/api/v1/)                                  │
│  ├── auth.py           - Authentication & user management   │
│  ├── portfolio.py      - Portfolio operations & analytics  │
│  ├── positions.py      - Position CRUD operations         │
│  ├── risk.py           - Risk analytics & stress testing   │
│  ├── market_data.py    - Market data integration          │
│  ├── reports.py        - Report generation & retrieval     │
│  └── chat.py           - GPT integration endpoints        │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                      │
│  ├── Calculation Engines (app/calculations/)              │
│  │   ├── Portfolio Aggregation                            │
│  │   ├── Position Greeks                                  │
│  │   ├── Factor Analysis                                  │
│  │   ├── Market Risk (VaR/ES)                            │
│  │   ├── Stress Testing                                   │
│  │   ├── Portfolio Snapshots                             │
│  │   ├── Position Correlations                           │
│  │   └── Factor Correlations                             │
│  └── Services (app/services/)                             │
│      ├── Market Data Service                              │
│      ├── Correlation Service                              │
│      └── Rate Limiter                                     │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── Models (app/models/) - SQLAlchemy ORM                │
│  ├── Schemas (app/schemas/) - Pydantic validation         │
│  └── Database (PostgreSQL) - Data persistence             │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Core Entities
User (1) ──→ (N) Portfolio ──→ (N) Position
                │                  │
                │                  ├──→ (1) PositionGreeks
                │                  ├──→ (N) PositionFactorExposure
                │                  └──→ (N) Tag (M:N)
                │
                ├──→ (N) PortfolioSnapshot
                ├──→ (N) CorrelationCalculation
                ├──→ (N) StressTestResult
                └──→ (N) PortfolioReport
```

### Calculation Engine Status

| Engine | Status | Description |
|--------|--------|-------------|
| Portfolio Aggregation | ✅ Working | Portfolio-level metrics calculation |
| Position Greeks | ✅ Working | Options pricing using mibian library |
| Factor Analysis | ⚠️ Partial | 7-factor model (missing factor ETF data) |
| Market Risk | ⚠️ Partial | VaR/ES calculations (async/sync issues) |
| Stress Testing | ❌ Failed | Missing stress_test_results table |
| Portfolio Snapshots | ✅ Working | Daily portfolio state capture |
| Position Correlations | ✅ Working | Cross-position correlation analysis |
| Factor Correlations | ✅ Working | Factor relationship modeling |

---

## Authentication

### JWT Token Authentication

All API endpoints require JWT authentication via the Authorization header:

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "created_at": "2025-08-26T10:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

#### Get Current User
```http
GET /auth/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-08-26T10:00:00Z"
  }
}
```

---

## Portfolio Management API

### Get Portfolio Overview

```http
GET /portfolio/{portfolio_id}
```

**Path Parameters:**
- `portfolio_id` (string, UUID): Portfolio identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "name": "Demo Individual Investor Portfolio",
    "total_value": 298845.30,
    "total_pl": 15240.75,
    "total_pl_percent": 5.35,
    "created_at": "2025-08-23T10:00:00Z",
    "updated_at": "2025-08-26T09:30:00Z",
    "exposures": {
      "long": {
        "value": 325000.50,
        "percentage": 108.7,
        "visual": {
          "status": "success",
          "color": "#4CAF50"
        }
      },
      "short": {
        "value": -26155.20,
        "percentage": -8.7,
        "visual": {
          "status": "warning",
          "color": "#FF9800"
        }
      },
      "gross": {
        "value": 351155.70,
        "percentage": 117.5,
        "visual": {
          "status": "success",
          "limit": 150.0
        }
      },
      "net": {
        "value": 298845.30,
        "percentage": 100.0,
        "visual": {
          "status": "success",
          "target_range": [90.0, 110.0]
        }
      }
    },
    "risk_metrics": {
      "var_1d_99": -8450.25,
      "es_1d_99": -12675.50,
      "volatility_annual": 0.185,
      "beta": 1.15,
      "sharpe_ratio": 0.85,
      "max_drawdown": -0.125
    }
  },
  "meta": {
    "timestamp": "2025-08-26T10:30:15Z",
    "calculation_date": "2025-08-25",
    "cache_status": "hit"
  }
}
```

### Get Portfolio Summary

```http
GET /portfolio/{portfolio_id}/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "name": "Demo Individual Investor Portfolio",
    "total_value": 298845.30,
    "daily_pnl": 2150.75,
    "daily_return": 0.0072,
    "position_count": 16,
    "last_updated": "2025-08-26T09:30:00Z",
    "top_positions": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "market_value": 45250.00,
        "percentage": 15.1,
        "pnl": 2340.50,
        "pnl_percent": 5.45
      },
      {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "market_value": 38750.25,
        "percentage": 13.0,
        "pnl": 1875.75,
        "pnl_percent": 5.09
      }
    ],
    "sector_breakdown": {
      "Technology": 35.5,
      "Healthcare": 18.2,
      "Financial Services": 15.8,
      "Consumer Discretionary": 12.1,
      "Industrials": 8.9,
      "Other": 9.5
    },
    "active_alerts": 2
  }
}
```

### Upload Portfolio CSV

```http
POST /portfolio/upload
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `file` (file): CSV file with portfolio positions
- `portfolio_name` (string, optional): Name for the new portfolio

**CSV Format:**
```csv
Symbol,Name,Type,Quantity,Price,Sector
AAPL,Apple Inc.,LONG,250,180.50,Technology
MSFT,Microsoft Corporation,LONG,200,375.25,Technology
SPY_240119C450,SPY Call Option,LC,10,12.50,Options
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "new-uuid-here",
    "positions_created": 25,
    "positions_updated": 0,
    "validation_errors": [],
    "message": "Portfolio uploaded successfully."
  }
}
```

---

## Position Management API

### List Positions

```http
GET /positions
```

**Query Parameters:**
- `portfolio_id` (string, UUID, optional): Filter by portfolio
- `position_type` (string, optional): Filter by type (LONG, SHORT, LC, LP, SC, SP)
- `sector` (string, optional): Filter by sector
- `skip` (integer, default: 0): Pagination offset
- `limit` (integer, default: 100): Pagination limit

**Response:**
```json
{
  "success": true,
  "data": {
    "positions": [
      {
        "id": "pos_123",
        "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "type": "LONG",
        "quantity": 250,
        "price": 180.50,
        "market_value": 45125.00,
        "cost_basis": 42750.00,
        "unrealized_pnl": 2375.00,
        "unrealized_pnl_percent": 5.56,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "beta": 1.25,
        "volatility": 0.28,
        "risk_contribution": 0.045,
        "created_at": "2025-08-20T14:30:00Z",
        "updated_at": "2025-08-26T09:30:00Z"
      }
    ],
    "summary": {
      "total_positions": 16,
      "total_market_value": 298845.30,
      "gross_exposure": 351155.70,
      "net_exposure": 298845.30,
      "average_beta": 1.08
    }
  },
  "meta": {
    "total": 16,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

### Get Position Details

```http
GET /positions/{position_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "pos_123",
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "type": "LONG",
    "quantity": 250,
    "price": 180.50,
    "market_value": 45125.00,
    "cost_basis": 42750.00,
    "unrealized_pnl": 2375.00,
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "country": "United States",
    "currency": "USD",
    "beta": 1.25,
    "volatility": 0.28,
    "correlation_avg": 0.65,
    "risk_contribution": 0.045,
    "factor_exposures": {
      "Market_Beta": 1.15,
      "Value": -0.25,
      "Growth": 0.45,
      "Momentum": 0.10,
      "Quality": 0.30,
      "Size": -0.15,
      "Low_Volatility": -0.20
    },
    "greeks": null,
    "tags": ["#tech", "#large-cap", "#dividend"],
    "created_at": "2025-08-20T14:30:00Z",
    "updated_at": "2025-08-26T09:30:00Z"
  }
}
```

### Create Position

```http
POST /positions
```

**Request Body:**
```json
{
  "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
  "symbol": "GOOGL",
  "name": "Alphabet Inc. Class A",
  "type": "LONG",
  "quantity": 50,
  "price": 142.50,
  "sector": "Technology",
  "industry": "Internet Content & Information",
  "tags": ["#tech", "#growth"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "pos_new_uuid",
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "symbol": "GOOGL",
    "name": "Alphabet Inc. Class A",
    "type": "LONG",
    "quantity": 50,
    "price": 142.50,
    "market_value": 7125.00,
    "cost_basis": 7125.00,
    "unrealized_pnl": 0.00,
    "sector": "Technology",
    "industry": "Internet Content & Information",
    "tags": ["#tech", "#growth"],
    "created_at": "2025-08-26T10:30:00Z",
    "updated_at": "2025-08-26T10:30:00Z"
  }
}
```

### Update Position

```http
PUT /positions/{position_id}
```

**Request Body:**
```json
{
  "quantity": 300,
  "price": 182.75,
  "tags": ["#tech", "#large-cap", "#dividend", "#core-holding"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "pos_123",
    "quantity": 300,
    "price": 182.75,
    "market_value": 54825.00,
    "tags": ["#tech", "#large-cap", "#dividend", "#core-holding"],
    "updated_at": "2025-08-26T10:35:00Z"
  }
}
```

### Delete Position

```http
DELETE /positions/{position_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Position deleted successfully",
    "deleted_position_id": "pos_123"
  }
}
```

---

## Risk Analytics API

### Get Risk Overview

```http
GET /risk/overview
```

**Query Parameters:**
- `portfolio_id` (string, UUID, optional): Specific portfolio
- `view` (string, optional): portfolio|longs|shorts
- `period` (string, optional): daily|weekly|monthly

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "view": "portfolio",
    "period": "daily",
    "calculation_date": "2025-08-25",
    "metrics": {
      "var_1d_99": {
        "value": -8450.25,
        "percentage": -2.83,
        "confidence": 0.99,
        "description": "1-day Value at Risk (99% confidence)",
        "visual": {
          "status": "warning",
          "color": "#FF9800"
        }
      },
      "es_1d_99": {
        "value": -12675.50,
        "percentage": -4.24,
        "confidence": 0.99,
        "description": "Expected Shortfall (99% confidence)",
        "visual": {
          "status": "danger",
          "color": "#F44336"
        }
      },
      "volatility_annual": {
        "value": 0.185,
        "percentage": 18.5,
        "description": "Annualized portfolio volatility",
        "visual": {
          "status": "success",
          "target_range": [0.15, 0.25]
        }
      },
      "beta": {
        "value": 1.15,
        "description": "Portfolio beta vs S&P 500",
        "visual": {
          "status": "success",
          "benchmark": "SPY"
        }
      },
      "sharpe_ratio": {
        "value": 0.85,
        "description": "Risk-adjusted returns",
        "visual": {
          "status": "success"
        }
      },
      "max_drawdown": {
        "value": -0.125,
        "percentage": -12.5,
        "description": "Maximum peak-to-trough decline",
        "visual": {
          "status": "warning"
        }
      }
    },
    "concentration_risk": {
      "largest_position": {
        "symbol": "AAPL",
        "percentage": 15.1,
        "limit": 10.0,
        "status": "warning"
      },
      "top_5_concentration": 58.3,
      "sector_concentration": {
        "Technology": 35.5,
        "limit": 25.0,
        "status": "warning"
      }
    },
    "factor_exposures": {
      "Market_Beta": 1.15,
      "Value": -0.08,
      "Growth": 0.32,
      "Momentum": 0.15,
      "Quality": 0.22,
      "Size": -0.12,
      "Low_Volatility": -0.18
    }
  }
}
```

### Get Portfolio Greeks

```http
GET /risk/greeks
```

**Query Parameters:**
- `portfolio_id` (string, UUID, optional): Specific portfolio
- `include_expired` (boolean, default: false): Include expired options
- `view` (string, optional): portfolio|longs|shorts

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "cf890da7-7b74-4cb4-acba-2205fdd9dff4",
    "calculation_date": "2025-08-25",
    "current": {
      "delta": 3250.75,
      "gamma": -450.25,
      "theta": -185.50,
      "vega": 820.25,
      "rho": 125.75
    },
    "after_expiry": {
      "delta": 2800.50,
      "gamma": -35.75,
      "theta": -45.25,
      "vega": 420.50,
      "changes": {
        "delta": -450.25,
        "gamma": 414.50,
        "gamma_percent": 92.1,
        "theta": 140.25,
        "vega": -399.75
      }
    },
    "expiring_positions": [
      {
        "symbol": "SPY_240830C450",
        "expiration": "2025-08-30",
        "days_to_expiry": 4,
        "quantity": 10,
        "delta": 850.25,
        "gamma": 125.50,
        "theta": -45.75,
        "vega": 185.25
      }
    ],
    "visual": {
      "delta_status": "neutral",
      "gamma_status": "danger",
      "gamma_message": "High negative gamma concentration",
      "theta_status": "warning",
      "theta_message": "Significant time decay exposure",
      "vega_status": "success"
    }
  }
}
```

### Calculate Greeks for Scenarios

```http
POST /risk/greeks/calculate
```

**Request Body:**
```json
{
  "positions": [
    {
      "symbol": "SPY",
      "type": "LC",
      "quantity": 20,
      "strike": 450.00,
      "expiration": "2025-12-19",
      "underlying_price": 445.50
    },
    {
      "symbol": "QQQ",
      "type": "LP",
      "quantity": 15,
      "strike": 380.00,
      "expiration": "2025-11-15",
      "underlying_price": 385.25
    }
  ],
  "market_conditions": {
    "risk_free_rate": 0.05,
    "implied_volatility": 0.22
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "calculation_date": "2025-08-26T10:30:00Z",
    "positions": [
      {
        "symbol": "SPY_251219C450",
        "type": "LC",
        "quantity": 20,
        "greeks": {
          "delta": 0.58,
          "gamma": 0.012,
          "theta": -0.045,
          "vega": 0.125,
          "rho": 0.035
        },
        "portfolio_greeks": {
          "delta": 1160.00,
          "gamma": 240.00,
          "theta": -90.00,
          "vega": 2500.00,
          "rho": 700.00
        }
      }
    ],
    "total_greeks": {
      "delta": 1835.50,
      "gamma": 105.25,
      "theta": -125.75,
      "vega": 3150.25,
      "rho": 875.50
    },
    "warnings": []
  }
}
```

### Get Factor Exposures

```http
GET /risk/factors
```

**Query Parameters:**
- `portfolio_id` (string, UUID, optional): Specific portfolio
- `view` (string, optional): portfolio|longs|shorts

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "calculation_date": "2025-08-25",
    "model": "7-Factor Model",
    "factors": [
      {
        "factor_name": "Market Beta",
        "exposure": 1.15,
        "description": "Portfolio sensitivity to market movements",
        "etf_proxy": "SPY",
        "visual": {
          "percentage": 115,
          "status": "warning",
          "target": 1.0
        }
      },
      {
        "factor_name": "Value",
        "exposure": -0.08,
        "description": "Exposure to value vs growth stocks",
        "etf_proxy": "VTV",
        "visual": {
          "percentage": -8,
          "status": "neutral"
        }
      },
      {
        "factor_name": "Growth",
        "exposure": 0.32,
        "description": "Exposure to growth companies",
        "etf_proxy": "VUG",
        "visual": {
          "percentage": 32,
          "status": "success"
        }
      },
      {
        "factor_name": "Momentum",
        "exposure": 0.15,
        "description": "Exposure to momentum stocks",
        "etf_proxy": "MTUM",
        "visual": {
          "percentage": 15,
          "status": "success"
        }
      },
      {
        "factor_name": "Quality",
        "exposure": 0.22,
        "description": "Exposure to quality companies",
        "etf_proxy": "QUAL",
        "visual": {
          "percentage": 22,
          "status": "success"
        }
      },
      {
        "factor_name": "Size",
        "exposure": -0.12,
        "description": "Large cap vs small cap bias",
        "etf_proxy": "IJR",
        "visual": {
          "percentage": -12,
          "status": "neutral"
        }
      },
      {
        "factor_name": "Low Volatility",
        "exposure": -0.18,
        "description": "Low volatility vs high volatility",
        "etf_proxy": "SPLV",
        "visual": {
          "percentage": -18,
          "status": "neutral"
        }
      }
    ],
    "regression_stats": {
      "r_squared": 0.67,
      "tracking_error": 0.045,
      "data_points": 252,
      "last_updated": "2025-08-25T16:00:00Z"
    }
  }
}
```

### Run Stress Tests

```http
POST /risk/scenarios
```

**Request Body:**
```json
{
  "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
  "scenario_ids": ["market_down_10", "rate_up_200bp", "vix_spike_40"],
  "custom_scenarios": [
    {
      "name": "Tech Sector Crisis",
      "description": "Technology sector drops 25%",
      "parameters": {
        "sector_shocks": {
          "Technology": -0.25
        }
      }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "calculation_date": "2025-08-26T10:30:00Z",
    "base_value": 298845.30,
    "scenarios": [
      {
        "id": "market_down_10",
        "name": "Market Down 10%",
        "description": "S&P 500 declines 10%",
        "probability": 0.15,
        "portfolio_value": 264250.75,
        "pnl": -34594.55,
        "pnl_percent": -11.58,
        "visual": {
          "status": "danger",
          "severity": "high"
        }
      },
      {
        "id": "rate_up_200bp",
        "name": "Interest Rates +200bp",
        "description": "Fed funds rate increases 2%",
        "probability": 0.25,
        "portfolio_value": 285340.85,
        "pnl": -13504.45,
        "pnl_percent": -4.52,
        "visual": {
          "status": "warning",
          "severity": "medium"
        }
      },
      {
        "id": "tech_sector_crisis",
        "name": "Tech Sector Crisis",
        "description": "Technology sector drops 25%",
        "probability": 0.08,
        "portfolio_value": 248725.15,
        "pnl": -50120.15,
        "pnl_percent": -16.77,
        "visual": {
          "status": "danger",
          "severity": "critical"
        }
      }
    ],
    "summary": {
      "worst_case": {
        "scenario": "tech_sector_crisis",
        "pnl": -50120.15,
        "pnl_percent": -16.77
      },
      "best_case": {
        "scenario": "rate_up_200bp",
        "pnl": -13504.45,
        "pnl_percent": -4.52
      },
      "probability_weighted": {
        "expected_pnl": -28735.50,
        "expected_pnl_percent": -9.62
      }
    }
  }
}
```

---

## Market Data API

### Get Real-Time Quotes

```http
GET /market/quotes
```

**Query Parameters:**
- `symbols` (string): Comma-separated list of symbols (e.g., "AAPL,MSFT,SPY")
- `fields` (string, optional): Comma-separated fields to return

**Response:**
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "symbol": "AAPL",
        "price": 180.50,
        "change": 2.25,
        "change_percent": 1.26,
        "volume": 45250000,
        "bid": 180.48,
        "ask": 180.52,
        "bid_size": 100,
        "ask_size": 200,
        "last_trade": "2025-08-26T15:59:45Z",
        "market_cap": 2750000000000,
        "pe_ratio": 28.5,
        "52_week_high": 195.75,
        "52_week_low": 150.25
      },
      {
        "symbol": "MSFT",
        "price": 375.25,
        "change": -1.75,
        "change_percent": -0.46,
        "volume": 22150000,
        "bid": 375.20,
        "ask": 375.30,
        "last_trade": "2025-08-26T15:59:50Z"
      }
    ],
    "market_status": "open",
    "last_updated": "2025-08-26T15:59:55Z"
  }
}
```

### Get Options Chain

```http
GET /market/options/{symbol}
```

**Query Parameters:**
- `expiration` (string, optional): Specific expiration date (YYYY-MM-DD)
- `strike_count` (integer, default: 20): Number of strikes around current price
- `include_greeks` (boolean, default: true): Include calculated Greeks

**Response:**
```json
{
  "success": true,
  "data": {
    "underlying": {
      "symbol": "SPY",
      "price": 445.50,
      "change": 1.25,
      "change_percent": 0.28,
      "implied_volatility": 0.22
    },
    "expirations": [
      {
        "expiration": "2025-08-30",
        "days_to_expiry": 4,
        "total_volume": 125000,
        "total_open_interest": 450000,
        "calls": [
          {
            "strike": 440.0,
            "bid": 6.25,
            "ask": 6.45,
            "last": 6.35,
            "volume": 2500,
            "open_interest": 8500,
            "implied_volatility": 0.25,
            "greeks": {
              "delta": 0.65,
              "gamma": 0.015,
              "theta": -0.125,
              "vega": 0.085
            }
          }
        ],
        "puts": [
          {
            "strike": 450.0,
            "bid": 5.15,
            "ask": 5.35,
            "last": 5.25,
            "volume": 1800,
            "open_interest": 6200,
            "implied_volatility": 0.23,
            "greeks": {
              "delta": -0.45,
              "gamma": 0.018,
              "theta": -0.095,
              "vega": 0.092
            }
          }
        ]
      }
    ]
  }
}
```

### Get Historical Data

```http
GET /market/historical/{symbol}
```

**Query Parameters:**
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `interval` (string, default: "1d"): Data interval (1d, 1h, 5m)
- `adjusted` (boolean, default: true): Adjust for splits/dividends

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "interval": "1d",
    "adjusted": true,
    "currency": "USD",
    "data_points": 252,
    "prices": [
      {
        "date": "2025-08-26",
        "open": 179.25,
        "high": 181.75,
        "low": 178.50,
        "close": 180.50,
        "volume": 45250000,
        "adjusted_close": 180.50
      },
      {
        "date": "2025-08-25",
        "open": 177.50,
        "high": 179.85,
        "low": 176.75,
        "close": 178.25,
        "volume": 38750000,
        "adjusted_close": 178.25
      }
    ]
  }
}
```

---

## Reports API

### List Available Portfolios

```http
GET /reports/portfolios
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
      "name": "Demo Individual Investor Portfolio",
      "report_folder": "demo-individual-investor-portfolio",
      "generated_date": "2025-08-25",
      "formats_available": ["json", "csv", "md"],
      "position_count": 16,
      "total_value": "298845.30",
      "last_updated": "2025-08-25T16:00:00Z"
    },
    {
      "id": "14e7f420-b096-4e2e-8cc2-531caf434c05",
      "name": "Demo High Net Worth Portfolio",
      "report_folder": "demo-high-net-worth-portfolio",
      "generated_date": "2025-08-25",
      "formats_available": ["json", "csv"],
      "position_count": 17,
      "total_value": "1250750.85",
      "last_updated": "2025-08-25T16:00:00Z"
    },
    {
      "id": "cf890da7-7b74-4cb4-acba-2205fdd9dff4",
      "name": "Demo Hedge Fund Style Portfolio",
      "report_folder": "demo-hedge-fund-style-investor-portfolio",
      "generated_date": "2025-08-25",
      "formats_available": ["json", "csv", "md"],
      "position_count": 30,
      "total_value": "2750250.50",
      "last_updated": "2025-08-25T16:00:00Z"
    }
  ],
  "meta": {
    "total_portfolios": 3,
    "last_generation_run": "2025-08-25T16:00:00Z"
  }
}
```

### Get Portfolio Report Content

```http
GET /reports/portfolio/{portfolio_id}/content/{format}
```

**Path Parameters:**
- `portfolio_id` (string, UUID): Portfolio identifier
- `format` (string): Report format (json|csv|md)

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "format": "json",
    "content": {
      "metadata": {
        "portfolio_name": "Demo Individual Investor Portfolio",
        "generated_date": "2025-08-25",
        "total_value": 298845.30,
        "position_count": 16
      },
      "calculation_engines": {
        "portfolio_snapshot": {
          "status": "success",
          "data": {
            "total_value": "298845.30",
            "daily_pnl": "2150.75",
            "daily_return": "0.0072"
          }
        },
        "position_exposures": {
          "status": "success",
          "data": {
            "gross_exposure": "351155.70",
            "net_exposure": "298845.30",
            "long_exposure": "325000.50",
            "short_exposure": "-26155.20"
          }
        },
        "factor_analysis": {
          "status": "partial",
          "data": {
            "Market_Beta": 1.15,
            "Value": -0.08,
            "Growth": 0.32,
            "Quality": 0.22
          },
          "warnings": ["Insufficient data for Size factor"]
        },
        "risk_metrics": {
          "status": "success",
          "data": {
            "var_1d_99": -8450.25,
            "es_1d_99": -12675.50,
            "volatility": 0.185,
            "beta": 1.15
          }
        }
      },
      "positions": [
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "type": "LONG",
          "quantity": 250,
          "market_value": 45125.00,
          "sector": "Technology",
          "beta": 1.25
        }
      ]
    },
    "filename": "demo-individual-investor-portfolio_2025-08-25.json",
    "file_size": 15420,
    "generated_at": "2025-08-25T16:00:00Z"
  }
}
```

### Generate New Report

```http
POST /reports/portfolio/{portfolio_id}/generate
```

**Request Body:**
```json
{
  "formats": ["json", "csv", "md"],
  "include_sections": [
    "portfolio_snapshot",
    "position_exposures", 
    "factor_analysis",
    "risk_metrics",
    "position_performance"
  ],
  "options": {
    "include_expired_options": false,
    "calculation_date": "2025-08-26"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_report_abc123",
    "status": "queued",
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "formats_requested": ["json", "csv", "md"],
    "estimated_duration": 45,
    "poll_url": "/api/v1/reports/jobs/job_report_abc123",
    "created_at": "2025-08-26T10:30:00Z"
  }
}
```

### Get Report Generation Job Status

```http
GET /reports/jobs/{job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_report_abc123",
    "status": "completed",
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "progress_percentage": 100,
    "current_step": "Finalizing reports",
    "started_at": "2025-08-26T10:30:00Z",
    "completed_at": "2025-08-26T10:31:15Z",
    "duration_seconds": 75,
    "result": {
      "formats_generated": ["json", "csv", "md"],
      "report_urls": {
        "json": "/api/v1/reports/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/content/json",
        "csv": "/api/v1/reports/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/content/csv",
        "md": "/api/v1/reports/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/content/md"
      }
    }
  }
}
```

---

## Chat Integration API

### Analyze Portfolio with AI

```http
POST /chat/analyze
```

**Request Body:**
```json
{
  "message": "What are my biggest risks today?",
  "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
  "context": {
    "current_view": "risk_dashboard",
    "selected_positions": ["AAPL", "MSFT"],
    "date_range": "1M"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary_markdown": "# Portfolio Risk Analysis\n\nBased on your portfolio analysis, I've identified three primary risks:\n\n## 1. Concentration Risk\n- **Technology Sector**: 35.5% allocation exceeds recommended 25% limit\n- **Single Position**: AAPL at 15.1% approaches position limit\n- **Impact**: Vulnerable to sector-specific events\n\n## 2. Options Gamma Risk\n- **Expiring Positions**: 4 options expire Friday (8/30)\n- **Gamma Exposure**: -450 net gamma creates acceleration risk\n- **Impact**: Position values may change rapidly near expiration\n\n## 3. Market Beta Exposure\n- **Portfolio Beta**: 1.15 vs market benchmark\n- **Amplification**: 15% greater volatility than S&P 500\n- **Impact**: Magnifies both gains and losses\n\n## Recommendations\n1. **Reduce tech allocation** to 25-30% through gradual trimming\n2. **Manage expiring options** - consider rolling or closing\n3. **Add defensive positions** to lower overall beta\n4. **Diversify sectors** - consider healthcare, utilities\n\n*Analysis based on portfolio snapshot as of 2025-08-25*",
    "machine_readable": {
      "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
      "analysis_type": "risk_assessment",
      "key_risks": [
        {
          "type": "concentration",
          "severity": "high",
          "metric": "sector_allocation",
          "value": 35.5,
          "limit": 25.0,
          "description": "Technology sector overweight"
        },
        {
          "type": "options_risk",
          "severity": "medium",
          "metric": "gamma_exposure",
          "value": -450.25,
          "description": "Negative gamma from expiring options"
        },
        {
          "type": "market_risk",
          "severity": "medium",
          "metric": "beta",
          "value": 1.15,
          "description": "Above-market volatility"
        }
      ],
      "recommendations": [
        {
          "action": "reduce_allocation",
          "target": "Technology",
          "current": 35.5,
          "recommended": 25.0,
          "priority": "high"
        },
        {
          "action": "manage_options",
          "target": "expiring_positions",
          "count": 4,
          "days_to_expiry": 4,
          "priority": "high"
        },
        {
          "action": "add_defensive",
          "target": "portfolio_beta",
          "current": 1.15,
          "recommended": 1.0,
          "priority": "medium"
        }
      ],
      "data_quality": {
        "calculation_date": "2025-08-25",
        "coverage": "complete",
        "gaps": [],
        "warnings": []
      }
    }
  }
}
```

### Get Chat History

```http
GET /chat/history
```

**Query Parameters:**
- `portfolio_id` (string, UUID, optional): Filter by portfolio
- `limit` (integer, default: 50): Number of messages to return
- `offset` (integer, default: 0): Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_123",
        "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
        "created_at": "2025-08-26T10:30:00Z",
        "messages": [
          {
            "role": "user",
            "content": "What are my biggest risks today?",
            "timestamp": "2025-08-26T10:30:00Z"
          },
          {
            "role": "assistant", 
            "content": "Based on your portfolio analysis, I've identified three primary risks...",
            "timestamp": "2025-08-26T10:30:05Z"
          }
        ]
      }
    ],
    "total": 15,
    "limit": 50,
    "offset": 0
  }
}
```

---

## Error Handling

### Standard Error Response Format

All API endpoints return errors in a consistent format:

```json
{
  "success": false,
  "errors": [
    {
      "code": "PORTFOLIO_NOT_FOUND",
      "message": "Portfolio with ID 'invalid-uuid' not found",
      "field": "portfolio_id",
      "details": {
        "provided_id": "invalid-uuid",
        "valid_format": "UUID v4"
      }
    }
  ],
  "meta": {
    "timestamp": "2025-08-26T10:30:15Z",
    "request_id": "req_abc123",
    "path": "/api/v1/portfolio/invalid-uuid"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid JWT token |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `PORTFOLIO_NOT_FOUND` | 404 | Portfolio ID does not exist |
| `POSITION_NOT_FOUND` | 404 | Position ID does not exist |
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `CALCULATION_ERROR` | 500 | Backend calculation engine failed |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `EXTERNAL_API_ERROR` | 502 | Market data provider error |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |

### Rate Limiting

The API implements token bucket rate limiting:

**Limits:**
- **General API**: 100 requests per minute per user
- **Market Data**: 50 requests per minute per user
- **Report Generation**: 10 requests per minute per user
- **Chat Analysis**: 20 requests per minute per user

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1724668215
X-RateLimit-Window: 60
```

**Rate Limit Exceeded Response:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
```

```json
{
  "success": false,
  "errors": [
    {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "Rate limit exceeded. Try again in 45 seconds.",
      "details": {
        "limit": 100,
        "window": 60,
        "reset_at": "2025-08-26T10:31:00Z"
      }
    }
  ]
}
```

---

## Pagination

APIs that return lists support pagination using `skip` and `limit` parameters:

**Request:**
```http
GET /positions?skip=20&limit=10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "positions": [...],
    "meta": {
      "total": 150,
      "skip": 20,
      "limit": 10,
      "has_more": true,
      "next_url": "/api/v1/positions?skip=30&limit=10",
      "prev_url": "/api/v1/positions?skip=10&limit=10"
    }
  }
}
```

---

## WebSocket API (Future)

*Note: WebSocket endpoints are planned for future implementation*

### Real-Time Portfolio Updates

```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8001/ws/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'portfolio_value_update':
            // Handle real-time value changes
            break;
        case 'position_update':
            // Handle position changes
            break;
        case 'risk_alert':
            // Handle risk threshold breaches
            break;
    }
};
```

---

## SDK and Integration Examples

### Python SDK Example

```python
import requests
from typing import Dict, List, Optional

class SigmaSightAPI:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_portfolio(self, portfolio_id: str) -> Dict:
        """Get portfolio overview"""
        response = requests.get(
            f'{self.base_url}/portfolio/{portfolio_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_positions(self, portfolio_id: str = None, 
                     skip: int = 0, limit: int = 100) -> Dict:
        """List positions with optional filtering"""
        params = {'skip': skip, 'limit': limit}
        if portfolio_id:
            params['portfolio_id'] = portfolio_id
            
        response = requests.get(
            f'{self.base_url}/positions',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_risk_metrics(self, portfolio_id: str) -> Dict:
        """Get risk analytics for portfolio"""
        response = requests.get(
            f'{self.base_url}/risk/overview?portfolio_id={portfolio_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
api = SigmaSightAPI('http://localhost:8001/api/v1', 'your-jwt-token')
portfolio = api.get_portfolio('a3209353-9ed5-4885-81e8-d4bbc995f96c')
positions = api.get_positions(portfolio_id='a3209353-9ed5-4885-81e8-d4bbc995f96c')
risk = api.get_risk_metrics('a3209353-9ed5-4885-81e8-d4bbc995f96c')
```

### JavaScript SDK Example

```javascript
class SigmaSightAPI {
    constructor(baseURL, apiToken) {
        this.baseURL = baseURL;
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }

    async apiRequest(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers: { ...this.headers, ...options.headers }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    }

    async getPortfolio(portfolioId) {
        return this.apiRequest(`/portfolio/${portfolioId}`);
    }

    async getPositions(portfolioId = null, skip = 0, limit = 100) {
        const params = new URLSearchParams({ skip, limit });
        if (portfolioId) params.append('portfolio_id', portfolioId);
        
        return this.apiRequest(`/positions?${params}`);
    }

    async getRiskMetrics(portfolioId) {
        return this.apiRequest(`/risk/overview?portfolio_id=${portfolioId}`);
    }

    async analyzeWithAI(message, portfolioId, context = {}) {
        return this.apiRequest('/chat/analyze', {
            method: 'POST',
            body: JSON.stringify({
                message,
                portfolio_id: portfolioId,
                context
            })
        });
    }
}

// Usage
const api = new SigmaSightAPI('http://localhost:8001/api/v1', 'your-jwt-token');

(async () => {
    const portfolio = await api.getPortfolio('a3209353-9ed5-4885-81e8-d4bbc995f96c');
    const positions = await api.getPositions('a3209353-9ed5-4885-81e8-d4bbc995f96c');
    const riskMetrics = await api.getRiskMetrics('a3209353-9ed5-4885-81e8-d4bbc995f96c');
    
    const aiAnalysis = await api.analyzeWithAI(
        'What are my biggest risks?',
        'a3209353-9ed5-4885-81e8-d4bbc995f96c'
    );
    
    console.log('Portfolio:', portfolio);
    console.log('AI Analysis:', aiAnalysis.data.summary_markdown);
})();
```

---

## Changelog

### Version 1.4 (Current)

**Completed Features:**
- ✅ Authentication system with JWT tokens
- ✅ Portfolio management endpoints
- ✅ Position CRUD operations
- ✅ Risk analytics (VaR, stress testing)
- ✅ Market data integration (multi-provider)
- ✅ Report generation system
- ✅ Chat/AI integration endpoints
- ✅ Rate limiting implementation
- ✅ 8 calculation engines (partial functionality)

**Known Issues:**
- Factor analysis missing some ETF proxy data
- Stress testing table missing from database
- Async/sync mixing in batch processes
- Market data gaps for some instruments

**API Changes:**
- Added chat analysis endpoints
- Enhanced error response format
- Improved rate limiting headers
- Extended portfolio metrics

### Planned Version 1.5

**Upcoming Features:**
- WebSocket real-time updates
- Enhanced factor analysis with complete data
- Advanced stress testing scenarios  
- Performance attribution analysis
- Mobile-optimized endpoints
- Batch API operations
- Webhook notifications

---

**Documentation Status**: Complete for Version 1.4  
**Last Updated**: August 26, 2025  
**Next Review**: After Version 1.5 implementation  

For the latest API documentation and interactive testing, visit: http://localhost:8001/docs
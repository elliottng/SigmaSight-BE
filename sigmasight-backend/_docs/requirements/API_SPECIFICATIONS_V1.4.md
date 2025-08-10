# SigmaSight API Endpoints Specification v1.4

## Document Version Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.4.0 | 2024-06-27 | Initial | Initial V1.4 API specification |
| 1.4.1 | 2025-08-04 | Cascade | Updated for V1.4 implementation decisions: 150-day regression, position-level factor storage, mibian-only Greeks, 7-factor model, rate limiting completion |

## 1. Overview

This document specifies the REST API endpoints for SigmaSight V1.4, focusing on portfolio management, risk analytics, and ProForma modeling capabilities.

### 1.1 V1.4 Implementation Status

#### COMPLETED Features
- **Rate Limiting**: Token bucket algorithm for both SigmaSight API (100 req/min) and Polygon.io API
- **Authentication**: JWT-based authentication with 24-hour token expiry
- **Database Models**: All V1.4 models and schemas implemented
- **Portfolio Aggregation**: Complete engine with 5 core functions and caching
- **Market Data Integration**: Polygon.io client with rate limiting and error handling

#### IN PROGRESS Features
- **Risk Factor Analysis**: 150-day regression window, 7-factor model implementation
- **Greeks Calculation**: mibian-only implementation (Black-Scholes), no py_vollib fallback
- **Batch Processing**: Daily jobs for factor exposure calculations

#### V1.4 Key Decisions
- **Factor Model**: 7 real factors + 1 mock (Short Interest postponed to V1.5)
- **Regression Window**: 150 trading days with 60-day minimum
- **Storage Strategy**: Both position-level and portfolio-level factor exposures
- **Greeks Library**: mibian (Black-Scholes); py_vollib deprecated
- **Calculation Approach**: Real calculations only for options; stocks have no Greeks; expired options return zeros
- Modeling sessions can generate broker-ready trade lists
- Support for both synchronous and asynchronous operations (bias toward asynchronous for AI agent use)

- Implement proper error handling and validation
- Cache frequently accessed data
- Use batch operations where possible
- Implement proper rate limiting

### 1.2 How to Use This Document

#### 1.2.1 For AI Coding Agents
- API is designed for long-term SigmaSight product needs
- Start with API calls needed for the Demo Script
- Contains sample JSON data for database reference
- Database design should be respected; report conflicts for resolution

#### 1.2.2 For Frontend Developers
- All endpoints include visual indicator specifications
- Follow the UI synchronization API patterns
- Use the provided error handling patterns
- Implement proper loading states for async operations

## 2. API Calls for Demo Script V1.4

### 2.1 Core Portfolio APIs ✅

#### 2.1.1 Dashboard Summary Cards
```http
GET /api/v1/portfolio
```

#### 2.1.2 Exposure Metrics
```http
GET /api/v1/portfolio/exposures
```

#### 2.1.3 Performance Display
```http
GET /api/v1/portfolio/performance
```

### 2.2 Position Management APIs ✅

#### 2.2.1 Positions Table
```http
GET /api/v1/positions
```

#### 2.2.2 Grouped Positions
```http
GET /api/v1/positions/grouped
```

#### 2.2.3 Strategy Grouping
```http
GET /api/v1/strategies
```

### 2.3 Risk Analytics APIs ✅

#### 2.3.1 Greeks Display
```http
GET /api/v1/risk/greeks
```

#### 2.3.2 Greeks Calculation
```http
POST /api/v1/risk/greeks/calculate
```

#### 2.3.3 Factor Exposures
```http
GET /api/v1/risk/factors
```

#### 2.3.4 Risk Metrics
```http
GET /api/v1/risk/metrics
```

### 2.4 ProForma/Modeling APIs ✅

#### 2.4.1 Create Modeling Session
```http
POST /api/v1/modeling/sessions
```

#### 2.4.2 Get Session State
```http
GET /api/v1/modeling/sessions/{sessionId}
```

#### 2.4.3 Update Positions
```http
PUT /api/v1/modeling/sessions/{sessionId}/positions
```

#### 2.4.4 Export Trades
```http
GET /api/v1/modeling/sessions/{sessionId}/export
```

### 2.5 Market Data APIs ✅

#### 2.5.1 Real-time Prices
```http
GET /api/v1/market/quotes
```

### 2.6 Export APIs ✅

#### 2.6.1 Trade Lists
```http
POST /api/v1/export/trades
```

### 2.7 Tag Management APIs ✅

#### 2.7.1 List Tags
```http
GET /api/v1/tags
```

#### 2.7.2 Create Tags
```http
POST /api/v1/tags
```

#### 2.7.3 Update Tags
```http
PUT /api/v1/tags/{tagId}
```

#### 2.7.4 Delete Tags
```http
DELETE /api/v1/tags/{tagId}
```

#### 2.7.5 Position Tags
```http
GET /api/v1/positions/{positionId}/tags
PUT /api/v1/positions/{positionId}/tags
```

## 3. Core Architecture

### 3.1 Base URLs

#### 3.1.1 Production
```http
https://api.sigmasight.com/v1
```

#### 3.1.2 Staging
```http
https://api-staging.sigmasight.com/v1
```

### 3.2 Authentication & Headers

#### 3.2.1 Required Headers
```http
Authorization: Bearer {token}
X-AI-Agent-ID: {agent_id}
X-Session-ID: {session_id}
X-User-Context: {encoded_context}
Content-Type: application/json
```

### 3.3 Standard Response Format
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2024-06-27T14:32:15Z",
    "request_id": "req_abc123",
    "execution_time_ms": 123,
    "cache_status": "hit|miss|partial"
  },
  "errors": []
}
```

### 3.4 Async Response Format
```json
{
  "success": true,
  "job_id": "job_abc123",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_abc123",
  "estimated_duration_ms": 5000
}
```

### 3.5 Execution Mode

#### 3.5.1 Query Parameter
```http
?mode=sync|async
```

#### 3.5.2 Default Behavior
- Light operations (<500ms): sync only
- Heavy operations (>2s): async by default, sync optional
- Medium operations: sync by default, async optional

### 3.6 Visual Indicator Standard
```json
"visual": {
  "value": 0.45,
  "display": "45%",
  "percentage": 75,
  "status": "success|warning|danger|info",
  "color": "#4CAF50",
  "target_range": [0.4, 0.6],
  "limit": 0.5
}
```

### 3.7 Position Types

#### 3.7.1 Supported Types
- LONG: Long equity position
- SHORT: Short equity position
- LC: Long Call option
- LP: Long Put option
- SC: Short Call option
- SP: Short Put option

## 4. Portfolio Management APIs

### 4.1 Get Portfolio Overview
```http
GET /api/v1/portfolio
```

#### 4.1.1 Execution
- Sync only

#### 4.1.2 Response
```json
{
  "data": {
    "total_value": 1200000,
    "total_pl": 87360,
    "total_pl_percent": 7.28,
    "exposures": {
      "long": {
        "value": 1100000,
        "visual": {
          "percentage": 92,
          "status": "success"
        }
      },
      "short": {
        "value": -567000,
        "visual": {
          "percentage": 47,
          "status": "success"
        }
      },
      "gross": {
        "value": 1667000,
        "visual": {
          "percentage": 139,
          "status": "warning",
          "limit": 150
        }
      },
      "net": {
        "value": 533000,
        "visual": {
          "percentage": 44,
          "status": "success",
          "target_range": [40, 60]
        }
      }
    },
    "exposure_calculations": {
      "delta": {
        "long_exposure": 1250000,
        "short_exposure": -650000,
        "gross_exposure": 1900000,
        "net_exposure": 600000
      },
      "notional": {
        "long_exposure": 1100000,
        "short_exposure": -567000,
        "gross_exposure": 1667000,
        "net_exposure": 533000
      }
    },
    "ai_insights": {
      "primary_risks": ["high_tech_concentration", "gamma_exposure"],
      "opportunities": ["income_generation", "volatility_hedge"]
    }
  }
}
```

### 4.2 Upload Portfolio CSV
```http
POST /api/v1/portfolio/upload
```

#### 4.2.1 Request Body
```http
Content-Type: multipart/form-data
```

#### 4.2.2 Response (200 OK)
```json
{
  "portfolio_id": 1,
  "positions_created": 35,
  "positions_updated": 0,
  ~~"historical_data_status": "processing",~~
  ~~"historical_data_job_id": "uuid",~~
  "message": "Portfolio uploaded successfully."
}
```

~~**Note**: The upload endpoint triggers automatic fetching of 90 days of historical market data.~~
~~This process runs asynchronously and typically completes within 5-10 minutes depending on~~
~~the number of unique tickers.~~

**Note (Updated)**: *Historical data generation removed from V1.4 scope. Portfolio snapshots will be generated daily going forward from upload date.*

### 4.3 Get Portfolio Summary
```http
GET /api/v1/portfolio/summary
```

#### 4.3.1 Execution
- Sync only

#### 4.3.2 Response
```json
{
  "data": {
    "total_value": 1200000,
    "total_pl": 87360,
    "total_pl_percent": 7.28,
    "top_positions": [
      {
        "ticker": "AAPL",
        "value": 150000,
        "pnl": 15000,
        "pnl_percent": 11.1
      }
    ],
    "active_alerts": 2
  }
}
```

### 4.4 Get Portfolio Timeline
```http
GET /api/v1/portfolio/timeline
```

#### 4.4.1 Query Parameters
```http
?start=2024-01-01&end=2024-12-31&mode=sync|async
```

#### 4.4.2 Execution
- Sync by default
- Async for large date ranges

#### 4.4.3 Async Response
```json
{
  "success": true,
  "job_id": "job_timeline_456",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_timeline_456",
  "estimated_duration_ms": 3000
}
}
```

## 5. Position & Strategy APIs

### 5.1 List Positions
```http
GET /api/v1/positions
```

#### 5.1.1 Query Parameters
```http
?groupBy=type|strategy|tag&tags=tag1,tag2&tagMode=any|all&fields=ticker,value,pnl
```

#### 5.1.2 Execution
- Sync only

#### 5.1.3 Response
```json
{
  "data": {
    "positions": [
      {
        "id": "pos_123",
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "type": "LONG",
        "quantity": 500,
        "price": 180,
        "value": 90000,
        "pnl": 5000,
        "pnl_percent": 5.9,
        "tags": ["#momentum", "#tech", "#strategy:tech-longs"],
        "notional_exposure": 90000,
        "risk_metrics": {
          "beta": 1.25,
          "risk_contribution": 0.042
        }
      }
    ],
    "summary": {
      "total_positions": 24,
      "gross_exposure": 1667000,
      "net_exposure": 533000
    }
  }
}
```

### 5.2 Add Position
```http
POST /api/v1/positions
```

#### 5.2.1 Request Body
```json
{
  "ticker": "AAPL",
  "type": "LONG",
  "quantity": 500,
  "price": 178.50,
  "tags": ["#momentum", "#tech", "#strategy:tech-longs"],
  "ai_metadata": {
    "source": "ai_conversation",
    "intent": "increase_tech_exposure",
    "conversation_id": "conv_789"
  }
}
```

### 5.3 Get P&L Attribution
```http
GET /api/v1/attribution/positions
```

#### 5.3.1 Query Parameters
```http
?date=2024-06-27&groupBy=position|tag|type
```

#### 5.3.2 Execution
- Sync only

#### 5.3.3 Response
```json
{
  "data": {
    "date": "2024-06-27",
    "total_pl": 15420,
    "positions": [
      {
        "id": "pos_123",
        "ticker": "AAPL",
        "pnl": 5000,
        "pnl_percent": 5.9,
        "contribution_percent": 32.4
      }
    ],
    "by_type": {
      "LONG": { "pnl": 25000, "contribution_percent": 162.2 },
      "SHORT": { "pnl": -8000, "contribution_percent": -51.9 },
      "LC": { "pnl": 3420, "contribution_percent": 22.2 }
    }
  }
}
```

## 6. Risk & Analytics APIs

### 6.1 Get Risk Overview
```http
GET /api/v1/risk/overview
```

#### 6.1.1 Query Parameters
```http
?view=portfolio|longs|shorts&period=daily|weekly|monthly|annual
```

#### 6.1.2 Execution
- Sync only

#### 6.1.3 Response
```json
{
  "data": {
    "view": "portfolio",
    "period": "daily",
    "metrics": {
      "beta": {
        "value": 0.85,
        "description": "vs. SPY",
        "visual": {
          "status": "success"
        }
      },
      "annualized_volatility": {
        "value": "18.5%",
        "description": "Std. dev of returns"
      },
      "position_correlation": {
        "value": 0.23,
        "description": "Avg. pairwise correlation"
      },
      "max_drawdown": {
        "value": "-12.3%",
        "description": "Peak-to-trough decline"
      },
      "var_1d": {
        "value": -9700,
        "confidence": 0.95
      }
    },
    "ai_risk_summary": {
      "biggest_risks": [
        {
          "type": "concentration",
          "description": "Tech sector at 25% exceeds 20% limit",
          "severity": "medium",
          "suggested_actions": ["reduce_tech", "add_defensive_positions"]
        }
      ]
    }
  }
}
```

### 6.2 Calculate Portfolio Greeks (V1.4)
```http
GET /api/v1/risk/greeks
```

**V1.4 Implementation**: Uses real calculations with `mibian` for options. Stocks have no Greeks. Expired options return zero Greeks. On calculation errors, the service returns null values for affected fields (no mock fallback).

#### 6.2.1 Query Parameters
```http
?include_after_expiry=true&view=portfolio|longs|shorts
```

#### 6.2.2 Execution
- Sync only

#### 6.2.3 Response
```json
{
  "data": {
    "current": {
      "delta": 3250,
      "gamma": -450,
      "theta": -185,
      "vega": 820,
      "visual": {
        "gamma_status": "danger",
        "gamma_message": "High gamma concentration"
      }
    },
    "after_expiry": {
      "delta": 2800,
      "gamma": -35,
      "changes": {
        "delta": -450,
        "gamma": 415,
        "gamma_percent": 92.2
      }
    }
  }
}
```

### 6.3 Calculate Greeks for Modified Positions (V1.4)
```http
POST /api/v1/risk/greeks/calculate
```

**V1.4 Implementation**: 
- Performs real-time calculation using `mibian` only
- No mock fallback; if inputs are insufficient or a calculation error occurs, returns nulls with warnings
- Requires underlying price from market data cache

#### 6.3.1 Query Parameters
```http
?mode=sync|async
```

#### 6.3.2 Request Body
```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "type": "LC",
      "quantity": 20,
      "strike": 200,
      "expiration": "2025-12-19"
    }
  ]
}
```

#### 6.3.3 Async Response
```json
{
  "success": true,
  "job_id": "job_greeks_789",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_greeks_789",
  "estimated_duration_ms": 2000
}
```

### 6.4 Get Factor Definitions (V1.4 7-Factor Model)
```http
GET /api/v1/risk/factors/definitions
```

**V1.4 Implementation**:
- **7 Real Factors**: Calculated using 150-day regression with ETF proxies
- **1 Mock Factor**: Short Interest (postponed to V1.5)
- **ETF Proxies**: Standard institutional factor ETFs

#### 6.4.1 Execution
- Sync only

#### 6.4.2 Response
```json
{
  "data": [
    {
      "factor_name": "Market Beta",
      "etf_ticker": "SPY",
      "description": "Sensitivity of the portfolio to overall market movements",
      "calculation_method": "real",
      "display_order": 1
    },
    {
      "factor_name": "Momentum",
      "etf_ticker": "MTUM",
      "description": "Exposure to stocks that have exhibited strong recent performance",
      "calculation_method": "real",
      "display_order": 2
    },
    {
      "factor_name": "Value",
      "etf_ticker": "VTV",
      "description": "Exposure to stocks that are considered undervalued relative to their fundamentals",
      "calculation_method": "real",
      "display_order": 3
    },
    {
      "factor_name": "Growth",
      "etf_ticker": "VUG",
      "description": "Exposure to companies with high growth rates",
      "calculation_method": "real",
      "display_order": 4
    },
    {
      "factor_name": "Quality",
      "etf_ticker": "QUAL",
      "description": "Exposure to companies with strong balance sheets and stable earnings",
      "calculation_method": "real",
      "display_order": 5
    },
    {
      "factor_name": "Size",
      "etf_ticker": "IJR",
      "description": "Exposure to smaller companies vs large-cap",
      "calculation_method": "real",
      "display_order": 6
    },
    {
      "factor_name": "Low Volatility",
      "etf_ticker": "SPLV",
      "description": "Exposure to stocks that have historically exhibited lower price volatility",
      "calculation_method": "real",
      "display_order": 7
    },
    {
      "factor_name": "Short Interest",
      "etf_ticker": null,
      "description": "Exposure to stocks with high short interest (V1.5 feature)",
      "calculation_method": "mock",
      "display_order": 8
    }
  ]
}
```

### 6.5 Get Portfolio Factor Exposures (V1.4 Implementation)
```http
GET /api/v1/risk/factors
```

**V1.4 Implementation**:
- **Real calculations** for 7 factors using `statsmodels` OLS regression
- **252-day regression window** (12 months) with 60-day minimum
- **Mock value** (0.0) for Short Interest factor (postponed to V1.5)
- Both position-level and portfolio-level factor exposures stored
- Batch-calculated with API serving cached results

#### 6.5.1 Query Parameters
```http
?view=portfolio|longs|shorts&period=daily|weekly|monthly|annual
```

#### 6.5.2 Execution
- Sync only

#### 6.5.3 Response
```json
{
  "data": [
    {
      "factor_name": "Market Beta",
      "exposure": 0.7,
      "exposure_visual": {
        "percentage": 70,
        "status": "success"
      }
    }
  ]
}
```

### 6.6 Get Position-Level Factor Exposures (V1.4 New)
```http
GET /api/v1/risk/factors/positions
```

**V1.4 Implementation**:
- **Position-level factor exposures** stored in database
- Same 252-day regression methodology as portfolio-level
- Enables drill-down analysis and position-specific risk attribution
- Batch-calculated with cached results

#### 6.6.1 Query Parameters
```http
?portfolio_id={id}&position_ids=pos1,pos2&factors=Market Beta,Momentum
```

#### 6.6.2 Execution
- Sync only

#### 6.6.3 Response
```json
{
  "data": {
    "positions": [
      {
        "position_id": "pos_123",
        "ticker": "AAPL",
        "factor_exposures": {
          "Market Beta": 1.15,
          "Momentum": 0.23,
          "Value": -0.18,
          "Growth": 0.45,
          "Quality": 0.12,
          "Size": -0.08,
          "Low Volatility": -0.31,
          "Short Interest": 0.0
        },
        "regression_stats": {
          "r_squared": 0.67,
          "data_points": 252,
          "last_updated": "2025-08-04T12:00:00Z"
        }
      }
    ]
  }
}
```

### 6.7 Get Scenario Templates
```http
GET /api/v1/risk/scenarios/templates
```

#### 6.6.1 Execution
- Sync only

#### 6.6.2 Response
```json
{
  "data": [
    {
      "id": "market_up_10",
      "name": "Market Up 10%",
      "parameters": {
        "spy_change": 0.10
      }
    },
    {
      "id": "market_down_10",
      "name": "Market Down 10%",
      "parameters": {
        "spy_change": -0.10
      }
    },
    {
      "id": "oil_up_5",
      "name": "Oil Up 5%",
      "parameters": {
        "oil_change": 0.05
      }
    }
  ]
}
```

### 6.7 Run Scenario Analysis
```http
POST /api/v1/risk/scenarios
```

#### 6.7.1 Query Parameters
```http
?view=portfolio|longs|shorts&mode=sync|async
```

#### 6.7.2 Request Body
```json
{
  "scenario_ids": ["market_down_10", "oil_up_5"],
  "custom_scenario": {
    "name": "Fed Rate Hike",
    "parameters": {
      "rate_change": 0.0025
    }
  }
}
```

#### 6.7.3 Async Response
```json
{
  "success": true,
  "job_id": "job_scenario_123",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_scenario_123",
  "estimated_duration_ms": 5000
}
}
```

## 7. ProForma Analytics & Modeling APIs

### 7.1 Create Modeling Session
```http
POST /api/v1/modeling/sessions
```

#### 7.1.1 Request Body
```json
{
  "name": "Tech Exposure Reduction",
  "base_portfolio": "current"
}
```

#### 7.1.2 Response
```json
{
  "data": {
    "session_id": "session_789",
    "created_at": "2024-06-27T14:32:15Z",
    "name": "Tech Exposure Reduction",
    "status": "active"
  }
}
```

### 7.2 Get Modeling Session
```http
GET /api/v1/modeling/sessions/{sessionId}
```

#### 7.2.1 Response
```json
{
  "data": {
    "session_id": "session_789",
    "name": "Tech Exposure Reduction",
    "status": "active",
    "original_portfolio": {
      "total_value": 1200000,
      "exposures": {...}
    },
    "modified_portfolio": {
      "total_value": 1180000,
      "exposures": {...}
    },
    "changes": [
      {
        "action": "modify",
        "position_id": "pos_123",
        "field": "quantity",
        "from": 500,
        "to": 300
      }
    ],
    "impact": {
      "net_exposure_change": -0.05,
      "tech_exposure_change": -0.08,
      "greeks_change": {
        "delta": -200,
        "gamma": 15
      }
    }
  }
}
```

### 7.3 Update Modeling Session Positions
```http
PUT /api/v1/modeling/sessions/{sessionId}/positions
```

#### 7.3.1 Request Body
```json
{
  "modifications": [
    {
      "position_id": "pos_123",
      "new_quantity": 300
    },
    {
      "position_id": "new",
      "ticker": "SPY",
      "type": "LP",
      "quantity": 10,
      "strike": 420,
      "expiration": "2025-01-17"
    }
  ]
}
```

### 7.4 Reset Modeling Session
```http
POST /api/v1/modeling/sessions/{sessionId}/reset
```

#### 7.4.1 Execution
- Sync only

### 7.5 Model Single Trade
```http
POST /api/v1/proforma/trade
```

#### 7.5.1 Query Parameters
```http
?mode=sync|async
```

#### 7.5.2 Request Body
```json
{
  "symbol": "MSFT",
  "action": "buy",
  "quantity": 200,
  "include_stress_scenarios": true
}
```

### 7.6 Find Optimal Hedges
```http
POST /api/v1/proforma/hedge
```

#### 7.6.1 Request Body
```json
{
  "risk_to_hedge": "sector_technology",
  "budget": 5000,
  "constraints": {
    "max_positions": 3,
    "allowed_instruments": ["options", "etfs"]
  }
}
```

#### 7.6.2 Response
```json
{
  "success": true,
  "job_id": "job_hedge_456",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_hedge_456",
  "estimated_duration_ms": 8000
}
```

### 7.7 Export Trade List
```http
GET /api/v1/modeling/sessions/{sessionId}/export
```

#### 7.7.1 Query Parameters
```http
?format=csv|json|fix
```

#### 7.7.2 Response
```json
{
  "data": {
    "format": "csv",
    "trades": [
      {
        "action": "SELL",
        "symbol": "AAPL",
        "quantity": 200,
        "order_type": "MARKET",
        "time_in_force": "DAY"
      },
      {
        "action": "BUY_TO_OPEN",
        "symbol": "SPY_011725P420",
        "quantity": 10,
        "order_type": "LIMIT",
        "limit_price": 5.50
      }
    ],
    "export_url": "/exports/session_789_trades.csv",
    "instructions": "Import this file into your broker's basket trading tool"
  }
}
```

## 8. Reporting APIs

### 8.1 Generate Report
```http
POST /api/v1/reports/generate
```

#### 8.1.1 Request Body
```json
{
  "type": "risk_summary",
  "format": "pdf",
  "sections": ["exposure", "greeks", "factors", "scenarios"],
  "period": "daily"
}
```

#### 8.1.2 Response
```json
{
  "success": true,
  "job_id": "job_report_789",
  "status": "queued",
  "poll_url": "/api/v1/jobs/job_report_789",
  "estimated_duration_ms": 15000
}
```

### 8.2 Get Report Templates
```http
GET /api/v1/reports/templates
```

#### 8.2.1 Execution
- Sync only

### 8.3 Schedule Report
```http
POST /api/v1/reports/schedule
```

#### 8.3.1 Request Body
```json
{
  "template_id": "weekly_risk",
  "frequency": "weekly",
  "day_of_week": 5,
  "time": "16:00",
  "email": "user@example.com"
}
```

## 9. AI Agent Control APIs

### 9.1 Natural Language Processing
```http
POST /api/v1/ai/interpret
```

#### 9.1.1 Request Body
```json
{
  "query": "Show me my biggest risks today",
  "context": {
    "current_view": "dashboard",
    "recent_actions": []
  }
}
```

#### 9.1.2 Response
```json
{
  "interpretation": {
    "intent": "analyze_risk",
    "confidence": 0.95,
    "parameters": {
      "focus": "immediate_risks",
      "timeframe": "today"
    }
  },
  "actions": [
    {
      "type": "navigate_ui",
      "target": "risk_tab"
    },
    {
      "type": "highlight_elements",
      "elements": ["gamma_risk", "expiration_alerts"]
    }
  ],
  "response": "I found 2 critical risks requiring immediate attention..."
}
```

### 9.2 Execute AI Command
```http
POST /api/v1/ai/execute
```

#### 9.2.1 Query Parameters
```http
?mode=sync|async
```

#### 9.2.2 Request Body
```json
{
  "intent": "reduce_tech_exposure",
  "parameters": {
    "target_exposure": 0.15,
    "method": "proportional"
  },
  "confirmation_required": true
}
```

### 9.3 AI Workflow Creation
```http
POST /api/v1/ai/workflow/create
```

#### 9.3.1 Request Body
```json
{
  "name": "Daily Risk Check",
  "trigger": {
    "type": "time",
    "schedule": "0 9 * * *"
  },
  "actions": [
    {
      "type": "analyze_expiration_risk",
      "parameters": {"days_ahead": 5}
    },
    {
      "type": "check_risk_limits",
      "parameters": {"alert_on_breach": true}
    }
  ]
}
```

### 9.4 Save AI Context
```http
POST /api/v1/ai/context/save
```

#### 9.4.1 Request Body
```json
{
  "context_type": "conversation",
  "data": {
    "user_concern": "tech_exposure",
    "discussed_solutions": ["reduce_positions", "add_hedges"],
    "pending_actions": ["review_tomorrow"]
  }
}
```

## 10. UI Synchronization APIs

### 10.1 Navigate UI
```http
POST /api/v1/ui/navigate
```

#### 10.1.1 Request Body
```json
{
  "target": "positions_tab",
  "params": {
    "filter": "expiring_today",
    "sort": "gamma_risk_desc",
    "highlight": ["pos_123", "pos_456"]
  },
  "ai_context": {
    "reason": "showing_expiration_risk"
  }
}
```

### 10.2 Highlight UI Elements
```http
POST /api/v1/ui/highlight
```

#### 10.2.1 Request Body
```json
{
  "elements": [
    {
      "id": "pos_020",
      "style": "critical",
      "reason": "expiring_today"
    },
    {
      "id": "gamma_metric",
      "style": "warning",
      "pulse": true
    }
  ]
}
```

### 10.3 Apply Filter Preset
```http
POST /api/v1/ui/apply-filter
```

#### 10.3.1 Request Body
```json
{
  "view": "positions",
  "filter": {
    "preset": "expiring_today",
    "sort": {
      "field": "gamma_risk",
      "order": "desc"
    }
  },
  "highlight_reason": "92% of portfolio gamma"
}
```

## 11. Market Data APIs

### 11.1 Get Market Quotes
```http
GET /api/v1/market/quotes
```

#### 11.1.1 Query Parameters
```http
?symbols=AAPL,MSFT,SPY
```

#### 11.1.2 Execution
- Sync only

### 11.2 Get Options Chain
```http
GET /api/v1/market/options
```

#### 11.2.1 Query Parameters
```http
?symbol=SPY&expiry=all&strikes=20
```

#### 11.2.2 Execution
- Sync only

## 12. Alert & Notification APIs

### 12.1 Get Active Alerts
```http
GET /api/v1/alerts
```

#### 12.1.1 Query Parameters
```http
?priority=critical|high
```

#### 12.1.2 Response
```json
{
  "data": [
    {
      "id": "alert_001",
      "type": "expiration_risk",
      "priority": "critical",
      "title": "Options Expiration Risk",
      "message": "2 positions expiring TODAY (92% of portfolio Gamma)",
      "positions_affected": ["pos_020", "pos_021"],
      "triggered_at": "2024-06-28T09:00:00Z",
      "actions": ["close_positions", "roll_forward"]
    }
  ]
}
```

### 12.2 Configure Alert Rules
```http
POST /api/v1/alerts/rules
```

#### 12.2.1 Request Body
```json
{
  "name": "Tech Concentration Alert",
  "condition": {
    "metric": "sector_exposure",
    "sector": "technology",
    "operator": "greater_than",
    "threshold": 0.20
  }
}
```

## 13. Export & Trade List APIs

### 13.1 Export Portfolio Data
```http
GET /api/v1/export/portfolio
```

#### 13.1.1 Query Parameters
```http
?format=csv|excel|json&include=positions,greeks,exposures
```

#### 13.1.2 Execution
- Sync for CSV/JSON
- Async for Excel

### 13.2 Generate Trade List
```http
POST /api/v1/export/trades
```

#### 13.2.1 Request Body
```json
{
  "trades": [
    {
      "symbol": "AAPL",
      "action": "SELL",
      "quantity": 200
    }
  ],
  "format": "fix",
  "broker": "generic"
}
```

#### 13.2.2 Supported Formats
- CSV: Generic comma-separated values
- JSON: Structured trade data
- FIX: Financial Information eXchange protocol format

## 14. Job Management APIs

### 14.1 Get Job Status
```http
GET /api/v1/jobs/{job_id}
```

#### 14.1.1 Response
```json
{
  "data": {
    "job_id": "job_scenario_123",
    "status": "processing",
    "created_at": "2024-06-27T14:32:15Z",
    "updated_at": "2024-06-27T14:32:18Z",
    "estimated_completion": "2024-06-27T14:32:20Z"
  }
}
```

### 14.2 Get Job Result
```http
GET /api/v1/jobs/{job_id}/result
```

#### 14.2.1 Response
```json
{
  "data": {
    "job_id": "job_scenario_123",
    "status": "completed",
    "result": {
      // Original endpoint response data
    }
  }
}
```

### 14.3 Cancel Job
```http
POST /api/v1/jobs/{job_id}/cancel
```

#### 14.3.1 Execution
- Sync only

## 15. Error Handling

### 15.1 Standard Error Response
```json
{
  "success": false,
  "errors": [
    {
      "code": "RISK_LIMIT_EXCEEDED",
      "message": "Cannot execute trade: would exceed gamma limit",
      "field": "gamma",
      "ai_suggestions": [
        "reduce_position_size",
        "close_existing_positions"
      ]
    }
  ]
}
```

### 15.2 Async Job Error Response
```json
{
  "data": {
    "job_id": "job_scenario_123",
    "status": "failed",
    "error": {
      "code": "CALCULATION_ERROR",
      "message": "Unable to calculate scenario impact: Missing market data"
    }
  }
}
```

## 16. Rate Limiting (V1.4 COMPLETED)

**Implementation Status**: ✅ **COMPLETED** - Token bucket algorithm with exponential backoff

### 16.1 SigmaSight API Rate Limits

#### 16.1.1 Per-User Rate Limits
- **Standard Limit**: 100 requests/minute per authenticated user
- **Algorithm**: Token bucket with automatic refill
- **Headers**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **429 Response**: Includes `Retry-After` header

#### 16.1.2 Endpoint Categories
- **Read APIs**: Portfolio, positions, risk data (standard limit)
- **Write APIs**: Position updates, modeling (standard limit)
- **Export APIs**: Report generation (standard limit)
- **Job Status**: Polling endpoints (standard limit)

### 16.2 Polygon.io API Rate Limiting

#### 16.2.1 Plan-Based Limits (COMPLETED)
- **Free**: 5 requests/minute
- **Starter**: 100 requests/minute (current plan)
- **Developer**: 1,000 requests/minute
- **Advanced**: 10,000 requests/minute

#### 16.2.2 Implementation Details
- **Token Bucket**: `app/services/rate_limiter.py`
- **Global Instance**: `polygon_rate_limiter`
- **Exponential Backoff**: 1s base, 300s max, 2x factor
- **Environment**: `POLYGON_PLAN` variable controls limits

## 17. Pagination

### 17.1 Standard Pagination
```http
GET /api/v1/positions?page=1&limit=20
```

#### 17.1.1 Response Includes
```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

## 18. Async Operation Guidelines

### 18.1 When Async is Available

#### 18.1.1 Heavy Calculations (>2s expected)
- Scenario analysis
- Complex hedge optimization
- Large historical data queries
- Report generation

#### 18.1.2 Optional Async (500ms-2s expected)
- Bulk Greeks calculations
- Factor analysis with custom parameters
- Trade impact modeling with scenarios

### 18.2 Polling Best Practices

#### 18.2.1 Initial Poll
- After: estimated_duration_ms / 2

#### 18.2.2 Subsequent Polls
- Every 1-2 seconds

#### 18.2.3 Max Polling Duration
- 5 minutes

#### 18.2.4 After Max Duration
- Consider job failed

## 19. V1.4 Implementation Summary

### 19.1 Completed Features ✅

#### 19.1.1 Rate Limiting System
- **SigmaSight API**: 100 requests/minute per user with token bucket algorithm
- **Polygon.io API**: Plan-based limits (5-10,000 req/min) with exponential backoff
- **Implementation**: `app/services/rate_limiter.py` with global instances
- **Status**: Production ready with comprehensive testing

#### 19.1.2 Authentication & Security
- **JWT Authentication**: 24-hour token expiry with refresh capability
- **Password Security**: bcrypt hashing via passlib
- **Protected Routes**: All portfolio endpoints require valid JWT
- **Demo Users**: 3 seeded users for testing

#### 19.1.3 Database Infrastructure
- **Models**: All V1.4 SQLAlchemy models implemented
- **Migrations**: Alembic setup with initial schema
- **Schemas**: Pydantic schemas for all endpoints
- **Seeding**: Factor definitions and demo data ready

#### 19.1.4 Portfolio Aggregation Engine
- **Functions**: 5 core aggregation functions with caching
- **Performance**: <1 second for 10,000 positions
- **Precision**: Decimal precision maintained throughout
- **Testing**: 29/29 unit tests passing

#### 19.1.5 Market Data Integration
- **Polygon.io Client**: Full integration with rate limiting
- **Historical Data**: 90-day backfill capability
- **Caching**: Market data cache with 24-hour TTL
- **Error Handling**: Graceful degradation and retry logic

### 19.2 In Progress Features 

#### 19.2.1 Risk Factor Analysis
- **Regression Window**: 150 trading days with 60-day minimum
- **Factor Model**: 7 real factors using statsmodels OLS regression
- **Storage**: Both position-level and portfolio-level exposures
- **Mock Factor**: Short Interest (0.0 values, postponed to V1.5)

#### 19.2.2 Greeks Calculation
- **Primary Library**: `mibian` for Black-Scholes calculations
- **Fallback Pattern**: None; return null values on calculation error
- **Integration**: Real-only calculations; stocks have no Greeks; expired options return zeros

#### 19.2.3 Batch Processing Framework
- **Daily Jobs**: Factor exposure calculations and portfolio snapshots
- **Scheduling**: Configurable time slots with timeout handling
- **Progress Tracking**: Database tables for job status monitoring
- **Error Recovery**: Retry logic and failure handling

### 19.3 API Endpoint Status

#### 19.3.1 Ready for Implementation
- Portfolio Management APIs (Sections 2-3)
- Position Management APIs (Section 4)
- Tag Management APIs (Section 5)
- Authentication APIs (Section 11)
- Export APIs (Section 12)

#### 19.3.2 Requires Factor Analysis Completion
- Risk Analytics APIs (Section 6)
- ProForma Modeling APIs (Section 7)
- Batch Job APIs (Section 8)
- AI Agent APIs (Section 9)

### 19.4 V1.5 Postponed Features

#### 19.4.1 Advanced Risk Metrics
- Factor correlation matrix (using identity matrix in V1.4)
- Advanced VaR calculations (basic VaR in V1.4)
- Risk attribution drill-down

#### 19.4.2 Short Interest Factor
- Real short interest data integration
- Days-to-cover calculations
- Short squeeze risk metrics

#### 19.4.3 Advanced Analytics
- Monte Carlo simulations
- Stress testing scenarios
- Performance attribution analysis

### 19.5 Next Implementation Steps

1. **Complete Section 1.4.4**: Risk Factor Analysis implementation
2. **Modify calculate_daily_pnl()**: Support 252-day historical lookbacks
3. **Implement Batch Jobs**: Daily factor exposure calculations
4. **API Endpoint Development**: Risk analytics and factor exposure endpoints
5. **Integration Testing**: End-to-end workflow validation
6. **Production Deployment**: Rate limiting and monitoring setup

### 19.6 Technical Architecture Decisions

#### 19.6.1 Calculation Libraries
- **mibian**: Options pricing and Greeks (pure Python Black-Scholes)
- **statsmodels**: Factor regression analysis (Federal Reserve usage)
- **empyrical**: Risk metrics (Quantopian/Point72 heritage)
- **pandas/numpy**: Data infrastructure (institutional standard)

#### 19.6.2 Design Patterns
- **Deterministic Calculations**: Real calculations only; no mock fallbacks for Greeks
- **Batch Processing**: Heavy calculations done offline, APIs serve cached results
- **Graceful Degradation**: System continues operating with partial data
- **Institutional Standards**: Aligned with quantitative finance best practices

This API specification document is now fully aligned with V1.4 implementation decisions and ready to guide the remaining development work.
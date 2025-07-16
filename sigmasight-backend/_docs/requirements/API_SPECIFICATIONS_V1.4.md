# SigmaSight API Endpoints Specification v1.4

## 1. Overview
This document provides the API specification for SigmaSight, a portfolio risk management platform with comprehensive AI agent control capabilities.

### 1.1 Key Design Principles

#### 1.1.1 AI-First Architecture
- Every API endpoint is designed to be controllable by the AI agent in addition to being used by the Web frontend
- Visual indicators included for UI rendering
- Modeling sessions can generate broker-ready trade lists
- Support for both synchronous and asynchronous operations (bias toward asynchronous for AI agent use)

#### 1.1.2 Implementation Guidelines
- Use TypeScript interfaces for request/response types
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
  "historical_data_status": "processing",
  "historical_data_job_id": "uuid",
  "message": "Portfolio uploaded successfully. Historical data backfill in progress."
}
```

**Note**: The upload endpoint triggers automatic fetching of 90 days of historical market data.
This process runs asynchronously and typically completes within 5-10 minutes depending on 
the number of unique tickers.

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

### 6.2 Calculate Portfolio Greeks (V1.4 Hybrid)
```http
GET /api/v1/risk/greeks
```

**V1.4 Implementation**: Uses real calculations with `py_vollib` for options, falls back to mock values if calculation fails.

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

### 6.3 Calculate Greeks for Modified Positions (V1.4 Hybrid)
```http
POST /api/v1/risk/greeks/calculate
```

**V1.4 Implementation**: 
- Attempts real-time calculation using `py_vollib` or `mibian`
- Falls back to mock values if missing data or calculation error
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

### 6.4 Get Factor Definitions
```http
GET /api/v1/risk/factors/definitions
```

#### 6.4.1 Execution
- Sync only

#### 6.4.2 Response
```json
{
  "data": [
    {
      "factor_name": "Market Beta",
      "etf_ticker": "SPY",
      "description": "Sensitivity of the portfolio to overall market movements"
    },
    {
      "factor_name": "Momentum",
      "etf_ticker": "MTUM",
      "description": "Exposure to stocks that have exhibited strong recent performance"
    },
    {
      "factor_name": "Value",
      "etf_ticker": "VTV",
      "description": "Exposure to stocks that are considered undervalued relative to their fundamentals"
    },
    {
      "factor_name": "Growth",
      "etf_ticker": "VUG",
      "description": "Exposure to companies with high growth rates"
    },
    {
      "factor_name": "Quality",
      "etf_ticker": "QUAL",
      "description": "Exposure to companies with strong balance sheets and stable earnings"
    },
    {
      "factor_name": "Size (Small-Cap)",
      "etf_ticker": "IJR",
      "description": "Exposure to smaller companies"
    },
    {
      "factor_name": "Low Volatility",
      "etf_ticker": "SPLV",
      "description": "Exposure to stocks that have historically exhibited lower price volatility"
    }
  ]
}
```

### 6.5 Get Factor Exposures (V1.4 Hybrid)
```http
GET /api/v1/risk/factors
```

**V1.4 Implementation**:
- **Real calculations** for 7 factors using `statsmodels` OLS regression
- 60-day rolling window with position returns vs factor ETF returns
- **Mock value** (0.0) for Short Interest factor
- Leverages legacy `factors_utils.py` logic

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

### 6.6 Get Scenario Templates
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

## 16. Rate Limiting

### 16.1 Endpoint Types

#### 16.1.1 Read APIs
- Requests/min: 300
- Notes: Portfolio, positions, risk data

#### 16.1.2 Write APIs
- Requests/min: 60
- Notes: Position updates, modeling

#### 16.1.3 AI APIs
- Requests/min: 100
- Notes: Natural language processing

#### 16.1.4 Export APIs
- Requests/min: 10
- Notes: Report generation, trade lists

#### 16.1.5 Job Status
- Requests/min: 600
- Notes: Higher limit for polling

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
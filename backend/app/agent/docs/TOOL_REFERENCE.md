# Tool Handler Quick Reference

## Overview

This reference provides quick access to all tool functions available to the SigmaSight Agent for portfolio analysis.

## Tool Functions

### 1. get_portfolio_complete

**Purpose:** Comprehensive portfolio snapshot with positions, values, and optional data.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| portfolio_id | string | Yes | - | Portfolio UUID |
| include_holdings | boolean | No | true | Include position details |
| include_timeseries | boolean | No | false | Include historical data |
| include_attrib | boolean | No | false | Include attribution analysis |

**Limits:**
- Max 200 positions returned
- Max 180 days historical data

**Example Call:**
```python
result = await get_portfolio_complete(
    portfolio_id="550e8400-e29b-41d4-a716-446655440000",
    include_holdings=True,
    include_timeseries=False,
    include_attrib=False
)
```

**Response Structure:**
```json
{
  "meta": {
    "as_of": "2025-08-28T14:30:00Z",
    "truncated": false,
    "positions_count": 45
  },
  "portfolio": {
    "total_value": 125430.00,
    "cash_balance": 5430.00,
    "positions_value": 120000.00
  },
  "holdings": [...],
  "data_quality": {
    "score": 0.92,
    "has_prices": true,
    "has_factors": false
  }
}
```

---

### 2. get_portfolio_data_quality

**Purpose:** Assess data completeness and analysis feasibility.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| portfolio_id | string | Yes | - | Portfolio UUID |
| check_factors | boolean | No | true | Check factor data availability |
| check_correlations | boolean | No | true | Check correlation data |

**Example Call:**
```python
result = await get_portfolio_data_quality(
    portfolio_id="550e8400-e29b-41d4-a716-446655440000",
    check_factors=True,
    check_correlations=True
)
```

**Response Structure:**
```json
{
  "data_quality_score": 0.85,
  "feasible_analyses": {
    "basic_performance": true,
    "factor_analysis": false,
    "correlation_matrix": true,
    "attribution": false
  },
  "missing_data": {
    "factor_exposures": ["Size", "Value"],
    "price_history": []
  },
  "_tool_recommendation": "Data quality is good. Most analyses should be feasible."
}
```

---

### 3. get_positions_details

**Purpose:** Detailed position information with P&L and metadata.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| portfolio_id | string | Conditional* | - | Portfolio UUID |
| position_ids | string | Conditional* | - | Comma-separated position IDs |
| include_closed | boolean | No | false | Include closed positions |

*Either portfolio_id OR position_ids required

**Limits:**
- Max 200 positions returned

**Example Call:**
```python
# By portfolio
result = await get_positions_details(
    portfolio_id="550e8400-e29b-41d4-a716-446655440000",
    include_closed=False
)

# By specific positions
result = await get_positions_details(
    position_ids="id1,id2,id3",
    include_closed=True
)
```

**Response Structure:**
```json
{
  "meta": {
    "truncated": false,
    "total_positions": 45,
    "positions_returned": 45
  },
  "positions": [
    {
      "position_id": "uuid",
      "symbol": "AAPL",
      "quantity": 250,
      "entry_price": 171.56,
      "current_price": 180.92,
      "market_value": 45230.00,
      "cost_basis": 42890.00,
      "pnl_dollar": 2340.00,
      "pnl_percent": 5.45
    }
  ]
}
```

---

### 4. get_prices_historical

**Purpose:** Historical prices for top portfolio positions.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| portfolio_id | string | Yes | - | Portfolio UUID |
| lookback_days | integer | No | 90 | Days of history (max 180) |
| max_symbols | integer | No | 5 | Max symbols to return (max 5) |
| include_factor_etfs | boolean | No | true | Include factor ETF prices |
| date_format | string | No | "iso" | Date format: "iso" or "unix" |

**Business Logic:**
- Automatically selects top N symbols by market value
- Includes factor ETFs for comparison

**Example Call:**
```python
result = await get_prices_historical(
    portfolio_id="550e8400-e29b-41d4-a716-446655440000",
    lookback_days=30,
    max_symbols=3,
    include_factor_etfs=True,
    date_format="iso"
)
```

**Response Structure:**
```json
{
  "meta": {
    "symbols_selected": ["AAPL", "MSFT", "NVDA"],
    "selection_method": "top_by_market_value",
    "lookback_days": 30,
    "truncated": true
  },
  "prices": {
    "AAPL": [
      {"date": "2025-08-28T00:00:00Z", "close": 180.92},
      {"date": "2025-08-27T00:00:00Z", "close": 179.45}
    ]
  },
  "factor_etfs": {
    "SPY": [...],
    "IWM": [...]
  }
}
```

---

### 5. get_current_quotes

**Purpose:** Real-time market quotes for specified symbols.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| symbols | string | Yes | - | Comma-separated symbols |
| include_options | boolean | No | false | Include options data |

**Limits:**
- Max 5 symbols per request

**Example Call:**
```python
result = await get_current_quotes(
    symbols="AAPL,MSFT,GOOGL",
    include_options=False
)
```

**Response Structure:**
```json
{
  "meta": {
    "requested_symbols": "AAPL,MSFT,GOOGL",
    "applied_symbols": ["AAPL", "MSFT", "GOOGL"],
    "truncated": false
  },
  "quotes": {
    "AAPL": {
      "symbol": "AAPL",
      "price": 180.92,
      "change": 1.47,
      "change_percent": 0.82,
      "volume": 52384920,
      "bid": 180.90,
      "ask": 180.94,
      "day_high": 181.45,
      "day_low": 179.23
    }
  }
}
```

---

### 6. get_factor_etf_prices

**Purpose:** Historical prices for factor ETFs used in analysis.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lookback_days | integer | No | 90 | Days of history (max 180) |
| factors | string | No | All | Comma-separated factor names |

**Available Factors:**
- Market (SPY)
- Size (IWM)
- Value (IWD)
- Growth (IWF)
- Momentum (MTUM)
- Quality (QUAL)
- Low Volatility (USMV)

**Example Call:**
```python
result = await get_factor_etf_prices(
    lookback_days=30,
    factors="Market,Size,Value"
)
```

**Response Structure:**
```json
{
  "meta": {
    "lookback_days": 30,
    "requested_factors": "Market,Size,Value",
    "factor_mapping": {
      "Market": "SPY",
      "Size": "IWM",
      "Value": "IWD"
    }
  },
  "prices": {
    "SPY": [...],
    "IWM": [...],
    "IWD": [...]
  }
}
```

---

## Error Handling

All tools return errors in a consistent format:

```json
{
  "error": "Error message",
  "retryable": true,
  "details": {
    "code": "TOOL_ERROR",
    "context": "Additional context"
  }
}
```

### Common Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| `VALIDATION_ERROR` | Invalid parameters | No |
| `NOT_FOUND` | Portfolio/position not found | No |
| `TIMEOUT` | Request timeout | Yes |
| `RATE_LIMIT` | API rate limit | Yes |
| `DATA_UNAVAILABLE` | Market data not available | Sometimes |
| `INTERNAL_ERROR` | Server error | Yes |

---

## Best Practices

### 1. Check Data Quality First
```python
# Always check data quality before complex analyses
quality = await get_portfolio_data_quality(portfolio_id)
if quality["data_quality_score"] < 0.7:
    # Warn user about limited analysis capabilities
```

### 2. Handle Truncation
```python
result = await get_positions_details(portfolio_id)
if result["meta"]["truncated"]:
    # Inform user that showing top positions only
    coverage = result["meta"].get("coverage_percent", 0)
```

### 3. Use Appropriate Lookback Periods
```python
# For recent performance: 30 days
# For quarterly analysis: 90 days
# For annual analysis: 180 days (max)
```

### 4. Batch Related Queries
```python
# Good: Get all data in one call
complete = await get_portfolio_complete(
    portfolio_id,
    include_holdings=True,
    include_timeseries=True
)

# Avoid: Multiple separate calls
portfolio = await get_portfolio_complete(portfolio_id)
positions = await get_positions_details(portfolio_id)
prices = await get_prices_historical(portfolio_id)
```

### 5. Cache Responses
- Portfolio structure: Cache for 5 minutes
- Historical prices: Cache for 1 hour
- Real-time quotes: Cache for 30 seconds
- Data quality: Cache for 10 minutes

---

## Tool Selection Guide

### User Query → Tool Mapping

| User Query | Primary Tool | Secondary Tools |
|------------|--------------|-----------------|
| "What's my portfolio value?" | `get_portfolio_complete` | - |
| "Show my top holdings" | `get_positions_details` | `get_current_quotes` |
| "How did I perform this month?" | `get_prices_historical` | `get_portfolio_complete` |
| "What's AAPL trading at?" | `get_current_quotes` | - |
| "Calculate my portfolio beta" | `get_prices_historical` | `get_factor_etf_prices` |
| "Can I run factor analysis?" | `get_portfolio_data_quality` | - |
| "Show my P&L" | `get_positions_details` | - |
| "Compare to market" | `get_factor_etf_prices` | `get_prices_historical` |

---

## Performance Tips

### Optimize Tool Usage

1. **Minimize calls**: Batch related data needs
2. **Use caps**: Request only needed data
3. **Cache aggressively**: Reuse recent responses
4. **Check quality early**: Avoid impossible analyses
5. **Handle errors gracefully**: Retry with backoff

### Response Time Targets

| Tool | Target p50 | Target p95 | Max Timeout |
|------|------------|------------|-------------|
| get_portfolio_complete | 500ms | 1000ms | 3000ms |
| get_portfolio_data_quality | 200ms | 500ms | 2000ms |
| get_positions_details | 400ms | 800ms | 3000ms |
| get_prices_historical | 600ms | 1200ms | 5000ms |
| get_current_quotes | 300ms | 600ms | 2000ms |
| get_factor_etf_prices | 500ms | 1000ms | 3000ms |
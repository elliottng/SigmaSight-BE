# Agent-Specific Endpoint Enhancements

This document details the enhancements made to existing Raw Data APIs to support the SigmaSight Agent's requirements.

## Overview

The agent requires specific enhancements to Raw Data endpoints to ensure:
1. **Token-efficient responses** through data caps and truncation
2. **Transparent data handling** via comprehensive meta objects
3. **Smart data selection** based on portfolio characteristics
4. **Consistent error handling** with retry guidance

## Enhanced Endpoints

### 1. GET /api/v1/data/portfolio/{portfolio_id}/complete

**Enhancements:**
- Changed `include_positions` → `include_holdings` for clarity
- Added `include_timeseries` flag for historical data
- Added `include_attrib` flag for attribution analysis
- Consistent `as_of` timestamps across all data sections

**Meta Object Structure:**
```json
{
  "meta": {
    "as_of": "2025-08-28T14:30:00Z",
    "requested": {
      "include_holdings": true,
      "include_timeseries": false,
      "include_attrib": false
    },
    "applied": {
      "include_holdings": true,
      "include_timeseries": false,
      "include_attrib": false
    },
    "truncated": false,
    "limits": {
      "max_positions": 200,
      "max_history_days": 180
    },
    "data_quality": {
      "completeness": 0.92,
      "has_prices": true,
      "has_factors": false
    }
  }
}
```

### 2. GET /api/v1/data/positions/top/{portfolio_id} (NEW)

**Purpose:** Returns top N positions by market value or weight for efficient analysis.

**Parameters:**
- `limit` (integer, default: 20, max: 50): Number of positions to return
- `sort_by` (string): `market_value` or `weight`
- `as_of_date` (string, optional): ISO date for historical view (max 180 days back)

**Response:**
```json
{
  "meta": {
    "as_of": "2025-08-28T14:30:00Z",
    "requested": {
      "limit": 20,
      "sort_by": "market_value"
    },
    "applied": {
      "limit": 20,
      "sort_by": "market_value"
    },
    "total_positions": 45,
    "positions_returned": 20,
    "coverage_percent": 92.5
  },
  "data": [
    {
      "position_id": "uuid",
      "symbol": "AAPL",
      "quantity": 250,
      "market_value": 45230.00,
      "weight": 0.361,
      "cost_basis": 42890.00,
      "pnl_dollar": 2340.00,
      "pnl_percent": 5.5
    }
  ]
}
```

### 3. GET /api/v1/data/prices/historical/{portfolio_id}

**Enhancements:**
- Added automatic symbol selection based on portfolio composition
- Added `max_symbols` parameter (default: 5, max: 5)
- Added `selection_method` parameter: `top_by_value`, `top_by_weight`, `all`
- Smart truncation with explanation

**New Parameters:**
```typescript
{
  lookback_days?: number;      // Max 180
  max_symbols?: number;         // Max 5
  selection_method?: string;    // top_by_value (default), top_by_weight
  include_factor_etfs?: boolean;
  date_format?: string;         // iso, unix
}
```

**Enhanced Meta Object:**
```json
{
  "meta": {
    "as_of": "2025-08-28T14:30:00Z",
    "requested": {
      "lookback_days": 90,
      "max_symbols": 5,
      "selection_method": "top_by_value"
    },
    "applied": {
      "lookback_days": 90,
      "symbols_selected": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"],
      "selection_method": "top_by_value"
    },
    "truncated": true,
    "truncation_reason": "Portfolio has 15 symbols, showing top 5 by market value",
    "coverage_percent": 87.3
  }
}
```

### 4. GET /api/v1/data/positions/details

**Enhancements:**
- Added comprehensive position metadata
- Enforced 200 position cap with truncation
- Added summary statistics when truncated

**Response Enhancements:**
```json
{
  "meta": {
    "as_of": "2025-08-28T14:30:00Z",
    "requested": {
      "portfolio_id": "uuid",
      "include_closed": false
    },
    "applied": {
      "portfolio_id": "uuid",
      "include_closed": false
    },
    "total_positions": 250,
    "positions_returned": 200,
    "truncated": true,
    "truncation_method": "by_market_value_desc",
    "summary": {
      "total_market_value": 125430.00,
      "returned_market_value": 123200.00,
      "coverage_percent": 98.2
    }
  },
  "positions": [...]
}
```

### 5. GET /api/v1/data/prices/quotes

**Enhancements:**
- Enforced 5 symbol maximum with clear truncation
- Added suggested symbol prioritization
- Enhanced error messages for invalid symbols

**Truncation Behavior:**
```json
{
  "meta": {
    "requested_symbols": "AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA",
    "applied_symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    "truncated": true,
    "truncated_symbols": ["NVDA", "TSLA"],
    "suggested_params": {
      "symbols": "AAPL,MSFT,GOOGL,AMZN,META"
    }
  }
}
```

## Common Enhancement Patterns

### 1. Meta Object Standards

All enhanced endpoints include:
```typescript
interface MetaObject {
  as_of: string;              // UTC ISO 8601 with Z suffix
  requested: object;           // Original request parameters
  applied: object;             // Actually applied parameters
  truncated: boolean;          // Data was capped/filtered
  limits: object;              // Applicable limits
  retryable?: boolean;         // For errors
  suggested_params?: object;   // Better parameters to use
}
```

### 2. Truncation Rules

When data exceeds limits:
1. Apply intelligent selection (by value, weight, or recency)
2. Set `meta.truncated = true`
3. Include `truncation_reason` or `truncation_method`
4. Calculate `coverage_percent` to show data completeness
5. Suggest optimal parameters in `meta.suggested_params`

### 3. Error Enhancement

Enhanced error responses for agent understanding:
```json
{
  "error": {
    "code": "LIMIT_EXCEEDED",
    "message": "Requested 50 symbols, maximum is 5",
    "details": {
      "requested": 50,
      "maximum": 5,
      "suggestion": "Use top 5 symbols by portfolio weight"
    }
  },
  "meta": {
    "retryable": false,
    "suggested_params": {
      "symbols": "AAPL,MSFT,NVDA,GOOGL,AMZN"
    }
  }
}
```

## Implementation Guidelines

### For New Endpoints

1. **Always include meta object** with request/applied params
2. **Implement caps early** in request processing
3. **Calculate coverage** when truncating
4. **Provide suggestions** for better queries
5. **Use consistent timestamps** (UTC ISO 8601 with Z)

### For Existing Endpoints

1. **Preserve backward compatibility** - new params optional
2. **Add meta progressively** - start with basic, enhance over time
3. **Document caps clearly** in response and docs
4. **Test with large datasets** to verify truncation logic

## Testing Checklist

For each enhanced endpoint:

- [ ] Meta object present and complete
- [ ] Truncation works correctly at limits
- [ ] Coverage percentage accurate
- [ ] Suggested params helpful
- [ ] Error messages clear for agent
- [ ] Timestamps consistent (UTC with Z)
- [ ] Backward compatibility maintained
- [ ] Performance acceptable with max data

## Migration Notes

### From Original to Enhanced

1. **Position endpoints**: Add P&L calculations
2. **Price endpoints**: Add symbol selection logic
3. **Portfolio endpoints**: Add data quality metrics
4. **All endpoints**: Add comprehensive meta objects

### Breaking Changes

None - all enhancements are additive:
- New optional parameters
- Additional response fields
- Backward-compatible defaults

## Performance Considerations

### Caching Strategy

- Cache computed metrics (coverage, quality scores)
- Cache symbol selections for repeated queries
- TTL: 60 seconds for market data, 300 seconds for portfolio structure

### Query Optimization

- Use materialized views for top positions
- Pre-calculate portfolio weights
- Batch symbol lookups

## Future Enhancements

### Planned for v1.1

1. **Streaming updates** via WebSocket for real-time data
2. **Batch endpoints** for multiple portfolio queries
3. **Explanation fields** for why data was selected/truncated
4. **Alternative data sources** when primary unavailable

### Under Consideration

1. **GraphQL interface** for flexible data selection
2. **Aggregation endpoints** for portfolio groups
3. **Time-series compression** for efficient historical data
4. **Predictive truncation** based on usage patterns
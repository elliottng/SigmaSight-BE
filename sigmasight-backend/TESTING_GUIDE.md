# Testing Guide - Core Calculation Engine

## 🎯 Test-Driven Development for Section 1.4.2: Options Greeks Calculations

### Overview
This section implements the **V1.4 Hybrid Greeks Calculation** approach:
- **Real calculations** using `py_vollib` and `mibian` libraries
- **Mock fallback values** when real calculations fail
- **Database integration** for market data and position updates

### 📋 Test Requirements (Write Tests First)

#### 1. Unit Tests to Write

**File:** `tests/test_greeks_calculations.py`

```python
# Test cases to implement BEFORE writing the actual functions
# Import fixtures from tests/fixtures/greeks_fixtures.py
from app.calculations.greeks import MOCK_GREEKS  # Import existing dict

class TestGreeksCalculations:
    
    def test_calculate_greeks_hybrid_long_call_real():
        """Test real Greeks calculation for long call with valid market data"""
        # Expected: Real py_vollib calculation results
        # Input: LC position (SQLAlchemy model or dict) with all fields
        # Market data: Dict keyed by symbol {'AAPL': {...}}
        # Output: Dict with all 5 Greeks as floats, scaled appropriately
        
    def test_calculate_greeks_hybrid_short_put_real():
        """Test real Greeks calculation for short put with valid market data"""
        # Expected: Real calculation with negative scaling for short position
        
    def test_calculate_greeks_hybrid_fallback_missing_data():
        """Test fallback to mock values when market data missing"""
        # Expected: Mock values from imported MOCK_GREEKS dict
        # IV fallback: 0.25 (25%) if missing
        
    def test_calculate_greeks_hybrid_fallback_calculation_error():
        """Test fallback when py_vollib throws exception"""
        # Expected: Mock values with appropriate logging (no error raise)
        
    def test_calculate_greeks_hybrid_stock_positions():
        """Test that stock positions always use simple delta"""
        # Expected: LONG=1.0, SHORT=-1.0, other Greeks=0.0
        
    def test_calculate_greeks_hybrid_expired_options():
        """Test expired options return zero Greeks"""
        # Expected: All Greeks = 0.0 for expired positions
        
    def test_get_mock_greeks_all_position_types():
        """Test mock Greeks for all position types (LC, SC, LP, SP, LONG, SHORT)"""
        # Expected: Predefined values scaled by quantity
        
    def test_options_symbol_parsing_edge_cases():
        """Test parsing of complex option symbols"""
        # Test cases:
        # - Special chars: BRK.A → BRK/A240119C00150000
        # - Weekly options with 'W' suffix
        # - Non-standard strikes with extra digits
        # - Mini options (10 vs 100 multiplier)
        
    def test_update_position_greeks_database():
        """Test database update to position_greeks table"""
        # Expected: Insert/update in position_greeks table with:
        # - position_id, calculation_date
        # - All 5 Greeks + dollar_delta, dollar_gamma
        # Use PostgreSQL test schema with test_ prefix
        
    def test_bulk_update_portfolio_greeks():
        """Test bulk Greeks calculation for entire portfolio"""
        # Process in chunks of 100 positions
        # Use bulk_update_mappings for efficiency
        # Return summary with failed calculations
```

#### 2. Integration Tests to Write

**File:** `tests/test_greeks_integration.py`

```python
class TestGreeksIntegration:
    
    def test_greeks_with_real_market_data():
        """Test Greeks calculation with live market data from cache"""
        # Expected: Real calculations using cached prices and volatility
        # Database: Use test_ prefixed PostgreSQL schema
        
    def test_greeks_batch_processing():
        """Test Greeks calculation in daily batch job"""
        # Expected: All portfolio positions updated after market close
        # Missing market data: Log warning, use last known values
        # Create batch_jobs record to track success/failure
        # Create positions via SQLAlchemy ORM
        
    def test_greeks_api_endpoint():
        """Test Greeks retrieval via API endpoint"""
        # Expected JSON response:
        # {
        #   "position_id": 123,
        #   "symbol": "AAPL240119C00150000",
        #   "greeks": {
        #     "delta": 2.6,
        #     "gamma": 0.09,
        #     "theta": -0.225,
        #     "vega": 0.75,
        #     "rho": 0.4
        #   },
        #   "calculated_at": "2024-01-15T10:30:00Z"
        # }
```

#### 3. Performance Tests to Write

```python
import pytest

@pytest.mark.performance
def test_greeks_calculation_performance():
    """Test Greeks calculation speed for large portfolios"""
    # Expected: <100ms per position, <5s for 100-position portfolio
    # Skip with: pytest -m "not performance"
    
@pytest.mark.performance
def test_greeks_memory_usage():
    """Test memory efficiency of bulk calculations"""
    # Expected: Reasonable memory usage for large portfolios
```

### 🔧 Implementation Checklist (After Writing Tests)

#### Core Functions to Implement:

**File:** `app/calculations/greeks.py`

- [ ] `calculate_greeks_hybrid(position, market_data) -> Dict[str, float]`
  - Real calculation using py_vollib/mibian
  - Fallback to mock values on error (with logger.warning)
  - Position: SQLAlchemy model or dict with required fields
  - Market data: Dict keyed by symbol
  - Returns all 5 Greeks as floats (never Decimal)
  
- [ ] `get_mock_greeks(position_type, quantity) -> Dict[str, float]`
  - Predefined mock values by position type
  - Scaled by quantity
  
- [ ] `update_position_greeks(db, position_id, greeks) -> None`
  - Insert/update position_greeks table
  - Include dollar_delta and dollar_gamma
  
- [ ] `bulk_update_portfolio_greeks(db, portfolio_id) -> Dict`
  - Process in chunks of 100 positions
  - Use SQLAlchemy bulk_update_mappings
  - Track and return failed calculations
  - Returns summary: {updated: int, failed: int, errors: list}

#### Helper Functions:

- [ ] `extract_option_parameters(position) -> Dict`
  - Parse strike, expiry, option type from position
  
- [ ] `get_implied_volatility(symbol, market_data) -> float`
  - Retrieve or estimate implied volatility
  
- [ ] `calculate_time_to_expiry(expiry_date) -> float`
  - Convert expiry date to years fraction using calendar days / 365 convention

### 🧪 Test Data Setup

#### Test Fixtures File:
**File:** `tests/fixtures/greeks_fixtures.py`

```python
# Create explicit fixtures for all position types
from datetime import date, timedelta

# Market data includes dividend yield
TEST_MARKET_DATA = {
    'AAPL': {
        'current_price': 150.00,
        'implied_volatility': 0.25,  # 25% - fallback if missing
        'risk_free_rate': 0.05,       # 5%
        'dividend_yield': 0.0         # 0% default
    }
}

# All position types fixtures
# Position structure matches SQLAlchemy model fields
TEST_POSITIONS = {
    'LC': {  # Long Call
        'id': 1,
        'portfolio_id': 1,
        'symbol': 'AAPL240119C00150000',
        'position_type': 'LC',
        'quantity': 5,
        'entry_price': 3.50,
        'entry_date': '2024-01-01',
        'last_price': 4.00,
        'market_value': 2000.00,
        'unrealized_pnl': 250.00,
        # Option-specific fields
        'underlying_symbol': 'AAPL',
        'strike_price': 150.00,
        'expiration_date': '2024-01-19'
    },
    'SC': {  # Short Call
        'symbol': 'AAPL240119C00155000',
        'position_type': 'SC',
        'quantity': -3,
        'strike_price': 155.00,
        'expiry_date': '2024-01-19',
        'underlying_symbol': 'AAPL'
    },
    'LP': {  # Long Put
        'symbol': 'AAPL240119P00145000',
        'position_type': 'LP',
        'quantity': 2,
        'strike_price': 145.00,
        'expiry_date': '2024-01-19',
        'underlying_symbol': 'AAPL'
    },
    'SP': {  # Short Put
        'symbol': 'AAPL240119P00140000',
        'position_type': 'SP',
        'quantity': -4,
        'strike_price': 140.00,
        'expiry_date': '2024-01-19',
        'underlying_symbol': 'AAPL'
    },
    'LONG': {  # Long Stock
        'symbol': 'AAPL',
        'position_type': 'LONG',
        'quantity': 100,
        'underlying_symbol': 'AAPL'
    },
    'SHORT': {  # Short Stock
        'symbol': 'MSFT',
        'position_type': 'SHORT',
        'quantity': -50,
        'underlying_symbol': 'MSFT'
    }
}
```

### 📊 Expected Test Results

#### Real Calculation Results:
```python
# Long Call (AAPL, strike=150, 30 days, vol=25%)
# Values shown are AFTER scaling:
expected_greeks = {
    'delta': 0.52 * 5,           # 5 contracts
    'gamma': 0.018 * 5,
    'theta': -0.045 * 5,         # Already daily (÷365)
    'vega': 0.12 * 5,            # Already per 1% (÷100)
    'rho': 0.06 * 5
}
```

#### Mock Fallback Results:
```python
# From MOCK_GREEKS['LC'] scaled by quantity=5
fallback_greeks = {
    'delta': 0.6 * 5,
    'gamma': 0.02 * 5,
    'theta': -0.05 * 5,
    'vega': 0.15 * 5,
    'rho': 0.08 * 5
}
```

### 🚨 Error Scenarios to Test

1. **Missing Market Data**: Position has no underlying price
   - Action: Log warning, use last known values or mock fallback
2. **Invalid Option Parameters**: Malformed option symbol
   - Action: Log error, return mock Greeks
3. **Expired Options**: Expiry date in the past
   - Action: Return all Greeks as 0.0
4. **py_vollib Errors**: Library calculation failures
   - Action: `logger.warning(f"Greeks calculation failed: {e}")`
   - Return mock values
5. **Database Errors**: Failed position updates
   - Action: Track in failed list, continue processing

### 🔄 Batch Processing Behavior

- **Schedule**: Runs after market close (configurable time)
- **Tracking**: Creates batch_jobs record with status
- **Failure Handling**: Continues processing on individual failures
- **Market Data**: Uses cached prices from market_data_cache

### 🎯 TDD Workflow

1. **Red**: Write failing tests first
   ```bash
   pytest tests/test_greeks_calculations.py -v
   # Should fail - functions don't exist yet
   ```

2. **Green**: Implement minimal code to pass tests
   ```bash
   # Create app/calculations/greeks.py with basic implementations
   pytest tests/test_greeks_calculations.py -v
   # Should pass
   ```

3. **Refactor**: Improve code quality while keeping tests green
   ```bash
   # Optimize performance, add error handling
   pytest tests/test_greeks_calculations.py -v
   # Should still pass
   ```

### 📝 Manual Testing Script

**File:** `scripts/test_greeks.py`

```bash
# After implementation, run manual tests
python scripts/test_greeks.py

# Expected output:
# ✅ Real Greeks calculation: AAPL LC delta=2.6
# ✅ Mock fallback: Invalid position uses mock values
# ✅ Database update: Position Greeks saved
# ✅ Portfolio bulk update: 25 positions updated
```

### ✅ Definition of Done

- [ ] All unit tests pass (100% coverage)
- [ ] Integration tests pass with real database
- [ ] Performance tests meet requirements (<100ms per position)
- [ ] Manual testing script runs successfully
- [ ] Error scenarios handled gracefully
- [ ] Database updates work correctly
- [ ] Batch processing integration complete

---

## 📋 Section 1.4.1: Market Data Calculations

This guide covers integration and manual testing for the **Market Data Calculations** implementation (Section 1.4.1).

## ✅ Unit Testing Status

**Completed:** Full unit test suite with 100% coverage
- File: `tests/test_market_data_calculations.py`
- Run: `pytest tests/test_market_data_calculations.py -v`

## 🧪 Integration Testing

### 1. Test Calculation Functions

```bash
# Run the comprehensive calculation test script
python scripts/test_calculations.py
```

This validates:
- ✅ Position market value calculations (stocks & options)
- ✅ Daily P&L with database price lookups
- ✅ Bulk price fetching and caching
- ✅ Portfolio aggregations

### 2. Test Batch Processing Integration

```python
# Test the daily calculations batch job
from app.batch.daily_calculations import (
    update_portfolio_market_values,
    calculate_portfolio_aggregations
)
import asyncio

# Run for a specific portfolio
async def test_batch():
    async with get_db() as db:
        portfolio_id = 1  # Your test portfolio
        await update_portfolio_market_values(db, portfolio_id)
        aggregations = await calculate_portfolio_aggregations(db, portfolio_id)
        print(f"Portfolio aggregations: {aggregations}")

asyncio.run(test_batch())
```

### 3. Verify Database Updates

```sql
-- Check position updates
SELECT symbol, quantity, last_price, market_value, 
       unrealized_pnl, daily_pnl, updated_at
FROM positions
WHERE portfolio_id = 1
ORDER BY market_value DESC;

-- Check market data cache
SELECT symbol, date, close, volume
FROM market_data_cache
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY symbol, date DESC;
```

## 📊 Expected Results

### Position Calculations:
```
Stock Long (AAPL, 100 shares @ $150):
  Market Value: $15,500
  Exposure: $15,500
  Unrealized P&L: $500

Options Long Call (AAPL240119C00150, 5 contracts @ $3.75):
  Market Value: $1,875 (5 × $3.75 × 100)
  Exposure: $1,875
  Daily P&L: $125
```

### Portfolio Aggregations:
```json
{
  "total_market_value": 125000.00,
  "total_exposure": 115000.00,
  "long_exposure": 120000.00,
  "short_exposure": -5000.00,
  "gross_exposure": 125000.00,
  "net_exposure": 115000.00,
  "cash_percentage": 8.0
}
```

## 🐛 Common Issues

**Missing Previous Price:**
- Function returns zero P&L with warning
- Check market_data_cache has historical data

**API Rate Limits:**
- Bulk operations respect Polygon rate limits
- Check logs for rate limit warnings

## ✅ Validation Checklist

- [ ] Unit tests pass: `pytest tests/test_market_data_calculations.py`
- [ ] Integration script runs: `python scripts/test_calculations.py`
- [ ] Database shows updated position values
- [ ] Market data cache populated
- [ ] Batch processing completes without errors
- [ ] Portfolio aggregations match expected values

---

**Section 1.4.1 Complete** ✅ Ready for Section 1.4.2: Options Greeks Calculations
# Testing Guide - Core Calculation Engine

## 🎯 Test-Driven Development for Section 1.4.2: Options Greeks Calculations

### Overview
This section implements the **V1.4 Deterministic Greeks Calculation** approach:
- **Real calculations** using `mibian` (pure Python Black-Scholes) only
- **No mock fallbacks**; on error or missing inputs, store/return null and log
- **Database integration** for market data and position updates

### 📋 Test Requirements (Write Tests First)

#### 1. Unit Tests to Write

**File:** `tests/test_greeks_calculations.py`

```python
# Test cases to implement BEFORE writing the actual functions
# Import fixtures from tests/fixtures/greeks_fixtures.py
from app.calculations.greeks import calculate_position_greeks

class TestGreeksCalculations:
    
    def test_calculate_position_greeks_long_call():
        """Test real Greeks calculation for long call with valid market data"""
        # Expected: Real mibian calculation results
        # Input: LC position (SQLAlchemy model or dict) with all fields
        # Market data: Dict keyed by symbol {'AAPL': {...}}
        # Output: Dict with all 5 Greeks as floats, scaled appropriately
        
    def test_calculate_position_greeks_short_put():
        """Test real Greeks calculation for short put with valid market data"""
        # Expected: Real calculation with negative scaling for short position
        
    def test_returns_none_when_market_data_missing():
        """Test null-on-error behavior when market data missing"""
        # Expected: Function returns None and logs a warning
        
    def test_returns_none_on_calculation_error():
        """Test null-on-error behavior when calculation raises"""
        # Expected: Returns None with appropriate logging (no error raise)
        
    def test_calculate_position_greeks_stock_positions():
        """Test that stock positions always use simple delta"""
        # Expected: LONG=1.0, SHORT=-1.0, other Greeks=0.0
        
    def test_calculate_position_greeks_expired_options():
        """Test expired options return zero Greeks"""
        # Expected: All Greeks = 0.0 for expired positions
        
    def test_no_mock_fallback_used():
        """Ensure no mock Greeks are used; None is returned instead"""
        # Expected: No code path returns predefined mock Greek values
        
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

- [ ] `calculate_position_greeks(position, market_data) -> Optional[Dict[str, float]]`
  - Real calculation using `mibian` only
  - Null-on-error: return None and log a warning
  - Position: SQLAlchemy model or dict with required fields
  - Market data: Dict keyed by symbol
  - Returns dict of 5 Greeks as floats, or None on failure
  
- [ ] Remove any legacy mock Greeks references from tests and scripts
  
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

#### Null-on-error behavior
```python
# When inputs are missing or calculation fails
result = calculate_position_greeks(position_missing_data, market_data)
assert result is None  # No mock values should be returned
```

### 🚨 Error Scenarios to Test

1. **Missing Market Data**: Position has no underlying price
   - Action: Log warning and return None (skip in aggregation)
2. **Invalid Option Parameters**: Malformed option symbol
   - Action: Log error and return None
3. **Expired Options**: Expiry date in the past
   - Action: Return all Greeks as 0.0
4. **mibian Calculation Errors**: Library/input calculation failures
   - Action: `logger.warning(f"Greeks calculation failed: {e}")`
   - Return None
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
# ✅ Null-on-error: Invalid position yields None and is skipped
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

## 🎯 Test-Driven Development for Section 1.4.3: Portfolio Aggregation

### Overview
These tests ensure that aggregation functions correctly process pre-calculated position data without recalculation, handle edge cases gracefully, and meet performance targets.

### 📋 Test Requirements (Write Tests First)

#### 1. Unit Tests to Write

**File:** `tests/test_portfolio_aggregation.py`

```python
import pytest
from decimal import Decimal
from app.services.portfolio_aggregation import (
    calculate_portfolio_exposures,
    aggregate_portfolio_greeks,
    calculate_delta_adjusted_exposure,
    aggregate_by_tags,
    aggregate_by_underlying
)
from tests.fixtures.portfolio_aggregation_fixtures import TEST_PORTFOLIOS

class TestCalculatePortfolioExposures:
    """Test exposure calculations with pre-calculated values"""
    
    def test_mixed_portfolio_exposures(self):
        """Verify all 8 exposure fields calculated correctly"""
        result = calculate_portfolio_exposures(TEST_PORTFOLIOS['mixed_portfolio'])
        
        assert result['gross_exposure'] == Decimal('30000.00')
        assert result['net_exposure'] == Decimal('10000.00')
        assert result['long_exposure'] == Decimal('20000.00')
        assert result['short_exposure'] == Decimal('-10000.00')
        assert result['long_count'] == 2
        assert result['short_count'] == 1
        assert result['options_exposure'] == Decimal('5000.00')
        assert result['stock_exposure'] == Decimal('25000.00')
    
    def test_empty_portfolio_returns_zeros(self):
        """Empty portfolio returns all zeros with metadata"""
        result = calculate_portfolio_exposures([])
        
        assert result['gross_exposure'] == Decimal('0.00')
        assert result['metadata']['warnings'] == []
        assert result['metadata']['excluded_positions'] == 0
    
    def test_no_recalculation_of_values(self):
        """Verify function uses pre-calculated values only"""
        # Mock position with market_value/exposure
        # Should NOT call any price lookup functions
        pass

class TestAggregatePortfolioGreeks:
    """Test Greeks aggregation with signed values"""
    
    def test_sum_greeks_skip_none(self):
        """Sum only positions with Greeks, skip stocks (None)"""
        result = aggregate_portfolio_greeks(TEST_PORTFOLIOS['mixed_portfolio'])
        
        assert result['delta'] == Decimal('6.5')
        assert result['gamma'] == Decimal('0.2')
        assert result['theta'] == Decimal('-0.5')
        assert result['vega'] == Decimal('1.5')
        assert result['rho'] == Decimal('0.8')
    
    def test_missing_greeks_excluded(self):
        """Options with None Greeks are excluded with warning"""
        result = aggregate_portfolio_greeks(TEST_PORTFOLIOS['positions_missing_greeks'])
        
        assert result['delta'] == Decimal('0.0')
        assert 'excluded_positions' in result['metadata']
        assert result['metadata']['excluded_positions'] == 1

class TestDeltaAdjustedExposure:
    """Test delta-adjusted exposure calculations"""
    
    def test_returns_both_raw_and_adjusted(self):
        """Must return both raw_exposure and delta_adjusted_exposure"""
        result = calculate_delta_adjusted_exposure(TEST_PORTFOLIOS['mixed_portfolio'])
        
        assert 'raw_exposure' in result
        assert 'delta_adjusted_exposure' in result
        assert result['raw_exposure'] == Decimal('30000.00')
        # 15k*1 + 10k*1 + 5k*0.65 = 28250
        assert result['delta_adjusted_exposure'] == Decimal('28250.00')
    
    def test_stock_delta_assumptions(self):
        """Stocks use delta=1.0 (long) or -1.0 (short)"""
        # Test with all-stock portfolio
        pass

class TestAggregateByTags:
    """Test flexible tag-based aggregation"""
    
    def test_tag_filter_any_mode(self):
        """'any' mode returns positions with ANY matching tag"""
        result = aggregate_by_tags(
            TEST_PORTFOLIOS['complex_tags_portfolio'],
            tag_filter=['tech', 'growth'],
            tag_mode='any'
        )
        # Should include all positions with 'tech' OR 'growth'
    
    def test_tag_filter_all_mode(self):
        """'all' mode returns positions with ALL matching tags"""
        result = aggregate_by_tags(
            TEST_PORTFOLIOS['complex_tags_portfolio'],
            tag_filter=['tech', 'growth'],
            tag_mode='all'
        )
        # Should include only positions with 'tech' AND 'growth'
    
    def test_no_filter_returns_all(self):
        """No tag_filter returns aggregation by each unique tag"""
        result = aggregate_by_tags(TEST_PORTFOLIOS['mixed_portfolio'])
        assert 'tech' in result
        assert 'growth' in result

class TestAggregateByUnderlying:
    """Test underlying symbol aggregation for options"""
    
    def test_groups_stock_and_options(self):
        """Groups stock + options for same underlying"""
        # Add test data with SPY stock + SPY options
        pass
    
    def test_critical_for_options_analysis(self):
        """Verify all SPY positions grouped together"""
        result = aggregate_by_underlying(TEST_PORTFOLIOS['mixed_portfolio'])
        
        assert 'SPY' in result
        assert result['SPY']['positions'] == 1
        assert result['SPY']['exposure'] == Decimal('5000.00')
        assert result['SPY']['greeks']['delta'] == Decimal('6.5')

class TestDecimalPrecision:
    """Test Decimal type consistency"""
    
    def test_all_monetary_values_decimal(self):
        """All monetary values must be Decimal type"""
        result = calculate_portfolio_exposures(TEST_PORTFOLIOS['mixed_portfolio'])
        
        assert isinstance(result['gross_exposure'], Decimal)
        assert isinstance(result['net_exposure'], Decimal)
        # No float conversions in aggregation layer

@pytest.mark.performance
class TestPerformance:
    """Performance benchmarks for large portfolios"""
    
    def test_10k_positions_under_1_second(self):
        """Process 10,000 positions in <1 second"""
        import time
        large_portfolio = generate_test_positions(10000)
        
        start = time.time()
        result = calculate_portfolio_exposures(large_portfolio)
        elapsed = time.time() - start
        
        assert elapsed < 1.0
        assert result['position_counts']['total'] == 10000
```

#### 2. Integration Tests to Write

**File:** `tests/test_portfolio_aggregation_integration.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Portfolio, Position
from app.services.portfolio_aggregation import aggregate_portfolio_complete

class TestPortfolioAggregationIntegration:
    """Integration tests with database and API"""
    
    @pytest.mark.asyncio
    async def test_aggregation_with_real_positions(self, db: AsyncSession):
        """Test aggregation with positions from database"""
        # Load positions with pre-calculated values
        positions = await db.execute(
            select(Position).where(Position.portfolio_id == 1)
        )
        position_dicts = [pos.to_dict() for pos in positions.scalars()]
        
        # Run aggregation
        result = calculate_portfolio_exposures(position_dicts)
        
        # Verify results match expected
        assert result['gross_exposure'] > 0
        assert 'metadata' in result
    
    @pytest.mark.asyncio
    async def test_batch_job_stores_snapshots(self, db: AsyncSession):
        """Verify batch job stores aggregations in portfolio_snapshots"""
        from app.batch.portfolio_aggregation_job import run_portfolio_aggregation
        
        # Run batch job
        await run_portfolio_aggregation(db, portfolio_id=1)
        
        # Check snapshot was created
        snapshot = await db.execute(
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.portfolio_id == 1)
            .order_by(PortfolioSnapshot.created_at.desc())
        )
        latest = snapshot.scalar_one()
        
        assert latest.gross_exposure is not None
        assert latest.aggregated_greeks is not None
    
    @pytest.mark.asyncio
    async def test_api_endpoint_with_filters(self, client: AsyncClient):
        """Test API endpoint with tag and underlying filters"""
        # Test tag filter
        response = await client.get(
            "/api/v1/portfolio/aggregations?tag=tech"
        )
        assert response.status_code == 200
        data = response.json()
        assert 'by_tags' in data
        assert 'tech' in data['by_tags']
        
        # Test underlying filter
        response = await client.get(
            "/api/v1/portfolio/aggregations?underlying=SPY"
        )
        assert response.status_code == 200
        data = response.json()
        assert 'by_underlying' in data
        assert 'SPY' in data['by_underlying']
```

#### 3. Error Handling Tests

**File:** `tests/test_portfolio_aggregation_errors.py`

```python
class TestErrorHandling:
    """Test error scenarios and edge cases"""
    
    def test_malformed_position_data(self):
        """Handle positions missing required fields gracefully"""
        malformed = [{
            'symbol': 'AAPL',
            # Missing market_value and exposure
        }]
        
        result = calculate_portfolio_exposures(malformed)
        assert result['metadata']['warnings']
        assert result['metadata']['excluded_positions'] == 1
    
    def test_invalid_greek_values(self):
        """Handle non-numeric Greek values"""
        positions = [{
            'symbol': 'SPY240119C00450000',
            'greeks': {
                'delta': 'invalid',  # Non-numeric
                'gamma': None
            }
        }]
        
        result = aggregate_portfolio_greeks(positions)
        assert result['metadata']['excluded_positions'] == 1
    
    def test_extreme_values(self):
        """Handle extremely large position values"""
        positions = [{
            'market_value': Decimal('999999999999.99'),
            'exposure': Decimal('999999999999.99')
        }]
        
        # Should not overflow or raise exceptions
        result = calculate_portfolio_exposures(positions)
        assert result['gross_exposure'] == Decimal('999999999999.99')
```

### 🧪 Test Data Setup

**File:** `tests/fixtures/portfolio_aggregation_fixtures.py`

```python
from decimal import Decimal
from app.constants.portfolio import OPTIONS_MULTIPLIER, STOCK_MULTIPLIER

def generate_test_positions(count: int):
    """Generate large dataset for performance testing"""
    positions = []
    for i in range(count):
        if i % 2 == 0:  # Stock
            positions.append({
                'position_id': i,
                'symbol': f'STOCK{i}',
                'position_type': 'LONG' if i % 4 == 0 else 'SHORT',
                'quantity': Decimal(str(100 * (i % 10 + 1))),
                'market_value': Decimal(str(1000 * (i % 50 + 1))),
                'exposure': Decimal(str(abs(1000 * (i % 50 + 1)))),
                'current_price': Decimal('100.00'),
                'multiplier': STOCK_MULTIPLIER,
                'tags': ['tech'] if i % 3 == 0 else ['financials'],
                'greeks': None
            })
        else:  # Option
            positions.append({
                'position_id': i,
                'symbol': f'SPY{i}C00450000',
                'position_type': 'LC' if i % 4 == 1 else 'SC',
                'quantity': Decimal(str(10 * (i % 5 + 1))),
                'market_value': Decimal(str(500 * (i % 20 + 1))),
                'exposure': Decimal(str(abs(500 * (i % 20 + 1)))),
                'current_price': Decimal('5.00'),
                'multiplier': OPTIONS_MULTIPLIER,
                'underlying_symbol': 'SPY',
                'tags': ['#strategy:hedging'],
                'greeks': {
                    'delta': Decimal(str(0.5 * (i % 3 + 1))),
                    'gamma': Decimal('0.02'),
                    'theta': Decimal('-0.05'),
                    'vega': Decimal('0.15'),
                    'rho': Decimal('0.08')
                }
            })
    return positions

# Test Data Requirements - All values pre-calculated from Section 1.4.1/1.4.2
TEST_PORTFOLIOS = {
    'mixed_portfolio': [
        # Stocks (Greeks = None)
        {
            'position_id': 1,
            'symbol': 'AAPL', 
            'position_type': 'LONG', 
            'quantity': Decimal('100'),
            'market_value': Decimal('15000.00'),  # Pre-calculated
            'exposure': Decimal('15000.00'),       # Pre-calculated
            'current_price': Decimal('150.00'),    # For notional calc
            'multiplier': STOCK_MULTIPLIER,
            'tags': ['tech', 'growth'],
            'greeks': None  # Stocks have no Greeks
        },
        {
            'position_id': 2,
            'symbol': 'TSLA',
            'position_type': 'SHORT',
            'quantity': Decimal('-50'),
            'market_value': Decimal('-10000.00'),
            'exposure': Decimal('10000.00'),  # abs(market_value)
            'current_price': Decimal('200.00'),
            'multiplier': STOCK_MULTIPLIER,
            'tags': ['tech', 'momentum'],
            'greeks': None
        },
        # Options (Greeks from Section 1.4.2)
        {
            'position_id': 3,
            'symbol': 'SPY240119C00450000',
            'position_type': 'LC',
            'quantity': Decimal('10'),
            'market_value': Decimal('5000.00'),
            'exposure': Decimal('5000.00'),
            'current_price': Decimal('5.00'),  # Option price
            'multiplier': OPTIONS_MULTIPLIER,  # 100
            'underlying_symbol': 'SPY',
            'tags': ['#strategy:hedging'],
            'greeks': {  # Already signed by quantity
                'delta': Decimal('6.5'),
                'gamma': Decimal('0.2'),
                'theta': Decimal('-0.5'),
                'vega': Decimal('1.5'),
                'rho': Decimal('0.8')
            }
        }
    ],
    
    'empty_portfolio': [],
    
    'single_position': [
        {
            'position_id': 100,
            'symbol': 'MSFT',
            'position_type': 'LONG',
            'quantity': Decimal('200'),
            'market_value': Decimal('60000.00'),
            'exposure': Decimal('60000.00'),
            'tags': ['tech'],
            'greeks': None
        }
    ],
    
    'all_long_portfolio': [...],   # 20 long positions only
    'all_short_portfolio': [...],  # 20 short positions only
    
    'positions_missing_greeks': [  # Options that failed Greeks calc
        {
            'position_id': 200,
            'symbol': 'AAPL240119C00150000',
            'position_type': 'LC',
            'quantity': Decimal('5'),
            'market_value': Decimal('2500.00'),
            'exposure': Decimal('2500.00'),
            'underlying_symbol': 'AAPL',
            'tags': [],
            'greeks': None  # Failed calculation
        }
    ],
    
    'complex_tags_portfolio': [  # For tag aggregation testing
        {
            'position_id': 301,
            'symbol': 'MSFT',
            'position_type': 'LONG',
            'quantity': Decimal('100'),
            'market_value': Decimal('35000.00'),
            'exposure': Decimal('35000.00'),
            'tags': ['tech', 'growth', '#strategy:momentum'],
            'greeks': None
        },
        {
            'position_id': 302,
            'symbol': 'JPM',
            'position_type': 'LONG',
            'quantity': Decimal('200'),
            'market_value': Decimal('30000.00'),
            'exposure': Decimal('30000.00'),
            'tags': ['financials', '#strategy:value'],
            'greeks': None
        },
        {
            'position_id': 303,
            'symbol': 'GOOGL',
            'position_type': 'SHORT',
            'quantity': Decimal('-50'),
            'market_value': Decimal('-7500.00'),
            'exposure': Decimal('7500.00'),
            'tags': ['tech', '#strategy:pairs-trade'],
            'greeks': None
        },
        {
            'position_id': 304,
            'symbol': 'NVDA',
            'position_type': 'LONG',
            'quantity': Decimal('50'),
            'market_value': Decimal('25000.00'),
            'exposure': Decimal('25000.00'),
            'tags': ['tech', 'growth'],  # Has both tech AND growth
            'greeks': None
        }
    ],
    
    'spy_options_portfolio': [  # For underlying aggregation testing
        {
            'position_id': 401,
            'symbol': 'SPY',
            'position_type': 'LONG',
            'quantity': Decimal('100'),
            'market_value': Decimal('45000.00'),
            'exposure': Decimal('45000.00'),
            'current_price': Decimal('450.00'),
            'multiplier': STOCK_MULTIPLIER,
            'tags': ['etf', 'index'],
            'greeks': None  # Stock has no Greeks
        },
        {
            'position_id': 402,
            'symbol': 'SPY240119C00450000',
            'position_type': 'LC',
            'quantity': Decimal('10'),
            'market_value': Decimal('5000.00'),
            'exposure': Decimal('5000.00'),
            'current_price': Decimal('5.00'),
            'multiplier': OPTIONS_MULTIPLIER,
            'underlying_symbol': 'SPY',
            'tags': ['#strategy:hedging'],
            'greeks': {
                'delta': Decimal('6.5'),
                'gamma': Decimal('0.2'),
                'theta': Decimal('-0.5'),
                'vega': Decimal('1.5'),
                'rho': Decimal('0.8')
            }
        },
        {
            'position_id': 403,
            'symbol': 'SPY240119P00440000',
            'position_type': 'LP',
            'quantity': Decimal('5'),
            'market_value': Decimal('2500.00'),
            'exposure': Decimal('2500.00'),
            'current_price': Decimal('5.00'),
            'multiplier': OPTIONS_MULTIPLIER,
            'underlying_symbol': 'SPY',
            'tags': ['#strategy:hedging'],
            'greeks': {
                'delta': Decimal('-2.5'),
                'gamma': Decimal('0.1'),
                'theta': Decimal('-0.25'),
                'vega': Decimal('0.75'),
                'rho': Decimal('-0.4')
            }
        }
    ],
    
    'large_portfolio': generate_test_positions(10000)  # Performance test
}
```

### 📊 Expected Results

```python
# Test calculate_portfolio_exposures() - includes notional
expected_exposures = {
    'gross_exposure': Decimal('30000.00'),  # 15k + 10k + 5k
    'net_exposure': Decimal('10000.00'),    # 15k - 10k + 5k
    'long_exposure': Decimal('20000.00'),   # 15k + 5k
    'short_exposure': Decimal('-10000.00'), # -10k (negative)
    'long_count': 2,                        # AAPL, SPY option
    'short_count': 1,                       # TSLA
    'options_exposure': Decimal('5000.00'), # SPY option only
    'stock_exposure': Decimal('25000.00'),  # AAPL + TSLA
    'notional_exposure': Decimal('30000.00') # Notional calculation:
    # AAPL: abs(100 * 150 * 1) = 15,000
    # TSLA: abs(-50 * 200 * 1) = 10,000  
    # SPY:  abs(10 * 5 * 100) = 5,000
    # Total: 15k + 10k + 5k = 30,000
}

# Test aggregate_portfolio_greeks()
expected_greeks = {
    'delta': Decimal('6.5'),   # Only from SPY option
    'gamma': Decimal('0.2'),
    'theta': Decimal('-0.5'),
    'vega': Decimal('1.5'),
    'rho': Decimal('0.8')
}

# Test calculate_delta_adjusted_exposure()
expected_delta_adjusted = {
    'raw_exposure': Decimal('30000.00'),
    'delta_adjusted_exposure': Decimal('8250.00')  # 15k*1 + 10k*1 + 5k*0.65
}

# Test aggregate_by_underlying()
expected_by_underlying = {
    'AAPL': {
        'positions': 1,
        'exposure': Decimal('15000.00'),
        'greeks': None  # No options for AAPL
    },
    'TSLA': {
        'positions': 1,
        'exposure': Decimal('10000.00'),
        'greeks': None
    },
    'SPY': {
        'positions': 1,
        'exposure': Decimal('5000.00'),
        'greeks': {'delta': Decimal('6.5'), ...}
    }
}

# Empty portfolio returns zeros with metadata
expected_empty = {
    'data': {
        'gross_exposure': Decimal('0.00'),
        'net_exposure': Decimal('0.00'),
        # ... all zeros
    },
    'metadata': {
        'calculated_at': '2024-01-15T10:30:00Z',
        'excluded_positions': 0,
        'warnings': []
    }
}
```

### 🎯 Performance Testing

```python
@pytest.mark.performance
def test_aggregation_performance():
    """Test aggregation speed for large portfolios"""
    # Generate 10,000 positions
    large_portfolio = generate_test_positions(10000)
    
    start_time = time.time()
    result = calculate_portfolio_exposures(large_portfolio)
    elapsed = time.time() - start_time
    
    assert elapsed < 1.0  # Target: <1 second for 10k positions
    assert result['position_counts']['total'] == 10000
```

### 🔄 Cache Behavior Tests

```python
import time
from unittest.mock import patch
from app.services.portfolio_aggregation import (
    calculate_portfolio_exposures,
    clear_portfolio_cache
)

class TestCacheBehavior:
    """Test caching with 60-second TTL"""
    
    def test_cache_returns_same_result(self):
        """Cached result returned for same input"""
        positions = TEST_PORTFOLIOS['mixed_portfolio']
        
        # First call - computes result
        result1 = calculate_portfolio_exposures(positions)
        
        # Second call - should return cached
        with patch('app.services.portfolio_aggregation.logger') as mock_logger:
            result2 = calculate_portfolio_exposures(positions)
            # Should not log computation, using cache
            assert result1 == result2
    
    def test_cache_ttl_60_seconds(self):
        """Verify cache expires after 60 seconds"""
        positions = TEST_PORTFOLIOS['mixed_portfolio']
        
        # First call
        result1 = calculate_portfolio_exposures(positions)
        
        # Mock time to advance 61 seconds
        with patch('time.time', return_value=time.time() + 61):
            result2 = calculate_portfolio_exposures(positions)
            # Should recompute after TTL
            assert result1 == result2  # Same result but recomputed
    
    def test_cache_invalidation_on_position_change(self):
        """Cache cleared when positions change"""
        # Clear cache explicitly
        clear_portfolio_cache()
        
        # Verify cache is empty
        assert calculate_portfolio_exposures.cache_info().currsize == 0

class TestNotionalExposure:
    """Test notional exposure calculations"""
    
    def test_notional_with_multipliers(self):
        """Notional = abs(quantity * price * multiplier)"""
        positions = [{
            'symbol': 'SPY240119C00450000',
            'quantity': Decimal('10'),
            'current_price': Decimal('5.00'),
            'multiplier': 100,  # Options multiplier
            'market_value': Decimal('5000.00'),
            'exposure': Decimal('5000.00')
        }]
        
        result = calculate_portfolio_exposures(positions)
        # 10 * 5 * 100 = 5000
        assert result['notional_exposure'] == Decimal('5000.00')
    
    def test_notional_aggregates_all_positions(self):
        """Sum notional across all positions"""
        result = calculate_portfolio_exposures(TEST_PORTFOLIOS['mixed_portfolio'])
        assert result['notional_exposure'] == Decimal('30000.00')
```

### ✅ Definition of Done
- [ ] Unit tests pass (≥95% coverage)
- [ ] Integration tests pass against test DB
- [ ] Performance target met (<200 ms for 200 positions, <1s for 10k positions)
- [ ] API response matches schema with proper decimal precision
- [ ] All edge cases (empty portfolio, missing data) handled gracefully
- [ ] Cache behavior verified (60s TTL, consistent results)
- [ ] Underlying-based aggregations work for options portfolios
- [ ] Tag-based filtering returns correct subsets

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
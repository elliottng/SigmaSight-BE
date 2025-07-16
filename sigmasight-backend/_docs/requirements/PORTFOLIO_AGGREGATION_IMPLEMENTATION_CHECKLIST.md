# Portfolio Aggregation Implementation Checklist

## Pre-Implementation Verification ✅

### Documentation Review
- [x] PORTFOLIO_AGGREGATION_V1.4.md - All 25 design decisions documented
- [x] TODO.md Section 1.4.3 - Tasks aligned with design decisions
- [x] TESTING_GUIDE.md Section 1.4.3 - Comprehensive test coverage defined
- [x] PRD_V1.4.md - Requirements clear and consistent

### Design Decisions Confirmed
- [x] Use pre-calculated values from Section 1.4.1 (no recalculation)
- [x] Greeks embedded in position dictionaries from Section 1.4.2
- [x] Return 8 exposure fields + notional exposure
- [x] NO sector/industry aggregation (use tags instead)
- [x] Hybrid storage: summaries in snapshots, details on-demand
- [x] 60-second cache TTL with functools.lru_cache
- [x] Decimal precision: monetary 2 places, Greeks 4 places
- [x] Performance target: <1 second for 10,000 positions

## Implementation Order

### 1. Constants File
- [ ] Create `app/constants/portfolio.py` with:
  - OPTIONS_MULTIPLIER = 100
  - STOCK_MULTIPLIER = 1
  - GREEKS_DECIMAL_PLACES = 4
  - MONETARY_DECIMAL_PLACES = 2
  - AGGREGATION_CACHE_TTL = 60

### 2. Core Aggregation Functions
- [ ] `calculate_portfolio_exposures(positions: List[Dict]) -> Dict`
  - Returns: gross, net, long, short exposures + counts + notional
- [ ] `aggregate_portfolio_greeks(positions: List[Dict]) -> Dict`
  - Skip positions with None Greeks
  - Sum signed Greeks values
- [ ] `calculate_delta_adjusted_exposure(positions: List[Dict]) -> Dict`
  - Returns both raw and delta-adjusted exposures
- [ ] `aggregate_by_tags(positions: List[Dict], tag_filter=None, tag_mode='any') -> Dict`
  - Support 'any' (OR) and 'all' (AND) filtering
- [ ] `aggregate_by_underlying(positions: List[Dict]) -> Dict`
  - Group stocks and options by underlying symbol

### 3. Cache Implementation
- [ ] Add @lru_cache decorator with TTL wrapper
- [ ] Implement `clear_portfolio_cache()` function
- [ ] Test cache behavior with time mocking

### 4. Batch Job Integration
- [ ] Create `app/batch/portfolio_aggregation_job.py`
- [ ] Store summaries in portfolio_snapshots table
- [ ] Schedule for 5:30 PM daily execution

### 5. API Endpoints
- [ ] Update portfolio aggregations endpoint
- [ ] Add query parameter support (?tag=tech, ?underlying=SPY)
- [ ] Convert Decimal to float in response

### 6. Testing
- [ ] Write all unit tests first (TDD approach)
- [ ] Create test fixtures with pre-calculated values
- [ ] Performance benchmarks with 10,000 positions
- [ ] Cache behavior tests
- [ ] Integration tests with database

## Success Criteria
- [ ] All tests pass with >95% coverage
- [ ] Performance meets targets (<1s for 10k positions)
- [ ] API responses match schema with proper precision
- [ ] Cache works correctly with 60s TTL
- [ ] Batch job stores snapshots successfully
- [ ] No recalculation of market values or exposures

## Notes
- Start with test implementation (TDD)
- Use pandas for vectorized operations
- Handle edge cases gracefully (empty portfolios, missing data)
- Maintain Decimal precision throughout calculations
- Convert to float only at API response layer

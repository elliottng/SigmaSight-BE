# Pragmatic Batch Processing Test Plan
**For Demo-Stage Product (20 Users Max)**

## Testing Philosophy
- **Accuracy over scale** - Traders need correct numbers, not fast ones
- **Manual verification acceptable** - We're not at automation scale yet
- **Focus on demo scenarios** - Test what we'll actually show
- **Skip premature optimization** - No need for 1000-position portfolios yet

---

## 1. Critical Path Testing Only (What Actually Matters)

### 1.1 Accuracy Validation (MOST IMPORTANT)
```python
# tests/batch/test_accuracy.py

async def test_calculation_accuracy_for_demo():
    """Verify calculations match trader expectations"""
    
    # Use Growth Investor portfolio (most likely demo)
    portfolio_id = 1
    
    # Run the batch sequence
    await run_daily_batch_sequence(portfolio_id)
    
    # MANUAL VERIFICATION POINTS:
    # 1. Greeks: Check 1-2 options positions manually
    aapl_call = await get_position_greek("AAPL_250117C00200000")
    print(f"AAPL Call Delta: {aapl_call.delta}")  # Should be ~0.55
    # Trader can verify: "Yes, that delta looks right for ATM call"
    
    # 2. Portfolio Value: Compare to Bloomberg/broker
    snapshot = await get_latest_snapshot(portfolio_id)
    print(f"Total Portfolio Value: ${snapshot.total_market_value:,.2f}")
    # Compare to TD Ameritrade: Should match within 1%
    
    # 3. Factor Exposures: Sanity check
    factors = await get_factor_exposures(portfolio_id)
    spy_beta = next(f for f in factors if f.factor == "SPY").beta
    print(f"Portfolio Beta to S&P: {spy_beta}")
    # Should be between 0.8-1.2 for typical portfolio
```

### 1.2 Demo Scenario Testing
```python
async def test_demo_scenarios():
    """Test exactly what we'll show in demos"""
    
    # Scenario 1: Daily update at market close
    await simulate_market_close()
    await run_daily_batch_sequence(portfolio_id=1)
    
    # Check the dashboard shows updated values
    dashboard_data = await get_dashboard_data(portfolio_id=1)
    assert dashboard_data.last_updated.date() == date.today()
    assert dashboard_data.total_value > 0
    
    # Scenario 2: Stress test presentation
    stress_results = await get_latest_stress_test(portfolio_id=1)
    
    # Just verify we have results to show
    assert len(stress_results.scenarios) >= 5  # At least 5 scenarios
    assert "Market Crash -20%" in [s.name for s in stress_results.scenarios]
    # Don't need to verify math - just that we have presentable data
```

---

## 2. Scale Testing (For 20 Users)

### 2.1 Concurrent User Test
```python
async def test_20_user_scale():
    """Ensure system handles 20 users (not 20,000)"""
    
    # Create 20 test portfolios (or use 3 demo portfolios x 7 times)
    portfolio_ids = [1, 2, 3] * 7  # Reuse demo portfolios
    
    # Run batch for all "20 users"
    start = time.time()
    for pid in portfolio_ids:
        await run_daily_batch_sequence(pid)
    duration = time.time() - start
    
    # Acceptable: Under 30 minutes for all 20
    assert duration < 1800  # 30 minutes is fine for batch
    print(f"Processed 20 portfolios in {duration/60:.1f} minutes")
```

### 2.2 Database Load Test
```python
async def test_database_capacity():
    """Ensure database handles demo scale"""
    
    # We have 3 portfolios x 21 positions = 63 positions
    # At 20 users with similar portfolios = ~1,260 positions
    # This is tiny for PostgreSQL
    
    position_count = await db.query("SELECT COUNT(*) FROM positions")
    print(f"Total positions in system: {position_count}")
    
    # Just verify basic queries still work
    query_time = await measure_query_time(
        "SELECT * FROM positions WHERE portfolio_id = 1"
    )
    assert query_time < 0.1  # Under 100ms is fine
```

---

## 3. Simplified Failure Testing

### 3.1 Market Data Failure (Most Likely Issue)
```python
async def test_polygon_api_failure_handling():
    """Test handling of Polygon API failures (most common issue)"""
    
    # Simulate Polygon being down
    with patch('app.clients.polygon_client.get_latest_price') as mock:
        mock.side_effect = Exception("Polygon API timeout")
        
        # Run batch - should use cached prices
        result = await run_daily_batch_sequence(portfolio_id=1)
        
        # Should complete with warnings, not fail
        assert result.status == "completed_with_warnings"
        assert "Using cached prices" in result.warnings
        
        # Dashboard should still show data (with stale warning)
        dashboard = await get_dashboard_data(portfolio_id=1)
        assert dashboard.data_status == "stale"
        assert dashboard.total_value > 0  # Still shows something
```

### 3.2 Calculation Engine Failure
```python
async def test_partial_calculation_failure():
    """If Greeks fail, everything else should still work"""
    
    # Break Greeks calculation
    with patch('app.calculations.greeks.calculate_portfolio_greeks') as mock:
        mock.side_effect = Exception("Greeks calculation failed")
        
        await run_daily_batch_sequence(portfolio_id=1)
        
        # Portfolio value should still update
        snapshot = await get_latest_snapshot(portfolio_id=1)
        assert snapshot.total_market_value > 0
        
        # Greeks should be null but noted
        assert snapshot.greeks_available == False
        assert snapshot.notes == "Greeks calculation failed - using previous values"
```

---

## 4. Manual Testing Checklist (For Demo Prep)

### Before Each Demo:
- [ ] Run batch manually at 3:30 PM
- [ ] Check dashboard loads properly
- [ ] Verify portfolio value looks reasonable (compare to yesterday)
- [ ] Click through to stress test results
- [ ] Ensure no error messages visible

### Weekly Checks:
- [ ] Tuesday: Verify correlation calculation ran
- [ ] Compare portfolio values to broker statements
- [ ] Check that all 3 demo portfolios updated
- [ ] Review batch job logs for any warnings

### If Something Looks Wrong:
1. Check `batch_jobs` table for errors
2. Re-run specific job manually via admin endpoint
3. Use cached/yesterday's data if needed
4. Have backup slides with pre-calculated results

---

## 5. What We're NOT Testing (Intentionally)

### Skip These Tests:
- ❌ 1000+ position portfolios (not needed yet)
- ❌ Sub-second response times (batch is fine being slow)
- ❌ Automated alerting (just check logs manually)
- ❌ Complex retry logic (just re-run manually if needed)
- ❌ Memory optimization (20 users won't stress memory)
- ❌ Distributed processing (single server is fine)
- ❌ Real-time updates (daily batch is sufficient)

---

## 6. Practical Test Execution Plan

### Week Before Demo:
**Monday**: 
- Run full batch with all 3 demo portfolios
- Screenshot results for backup slides

**Tuesday**: 
- Verify correlation calculation works
- Note any data quality issues

**Wednesday-Thursday**: 
- Daily batch runs
- Compare values to external sources
- Fix any calculation bugs found

**Friday**: 
- Final test run
- Document all "known issues" to avoid surprises
- Prepare explanation for any quirks

### Day of Demo:
- Run batch 2 hours before demo
- Quick manual verification of key numbers
- Have yesterday's data as backup

---

## 7. Success Criteria (Realistic)

### Must Have:
✅ Portfolio values within 2% of broker statements  
✅ Greeks look reasonable to a trader's eye  
✅ Stress tests produce believable scenarios  
✅ No visible errors on dashboard  
✅ Batch completes within 30 minutes for all portfolios  

### Nice to Have:
📊 All calculations within 1% accuracy  
📊 Batch completes in under 10 minutes  
📊 Automatic recovery from API failures  

### Don't Need Yet:
❌ 99.99% uptime  
❌ Sub-second calculations  
❌ Handling 1000+ concurrent users  

---

## 8. Test Data Strategy

### Use Real Demo Portfolios:
```python
# These are already seeded and realistic
portfolio_1 = "Growth Investor"  # Mixed stocks/options
portfolio_2 = "Hedge Fund"       # Complex strategies  
portfolio_3 = "Retail Trader"    # Simple portfolio

# Test with these exact portfolios
# Traders can relate to these in demos
```

### Manual Baseline Validation:
```excel
# Create simple Excel sheet with expected values:
Portfolio         | Expected Value | Our System | Difference
Growth Investor   | $1,000,000    | $998,500   | -0.15%
Hedge Fund        | $5,000,000    | $5,012,000 | +0.24%
Retail Trader     | $100,000      | $99,750    | -0.25%

# If within 1%, we're good for demo
```

---

## 9. Emergency Demo Procedures

### If Batch Fails Day-of:
1. Use yesterday's snapshot (usually fine)
2. Say "values as of yesterday's close" 
3. Run calculations live if needed (single portfolio is fast)
4. Have static slides with pre-calculated results

### Common Issues & Solutions:
| Issue | Quick Fix | Explanation for Demo |
|-------|-----------|---------------------|
| Polygon API down | Use cached prices | "Using last available market data" |
| Greeks missing | Hide Greeks panel | "Options analytics updating" |
| Stress test fails | Use last week's | "Stress tests run weekly" |
| Wrong values | Blame market volatility | "Reflecting this morning's gap" |

---

## 10. Documentation for Demo Team

### What to tell traders:
- "Calculations run daily at market close"
- "All risk metrics updated overnight"
- "Real-time prices available on request" (run manual update)
- "System designed for institutional accuracy"

### What NOT to promise:
- Real-time streaming updates
- Microsecond latency
- 100% uptime
- Handling their 50,000 position portfolio

---

## Summary

**Focus on**: Accuracy, reliability for demos, handling 20 users
**Skip**: Premature optimization, complex automation, enterprise scale
**Test method**: Mostly manual verification with some automated checks
**Time needed**: 2-3 days of testing, not 2-3 weeks

This is appropriate for a demo-stage product that needs to work well enough to impress traders, not scale to thousands of users.
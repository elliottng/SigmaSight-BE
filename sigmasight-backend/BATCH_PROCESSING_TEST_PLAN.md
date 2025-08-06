# Batch Processing Framework - Comprehensive Testing Plan
**⚠️ STATUS: DEFERRED FOR FUTURE PRODUCTION SCALING**

> **IMPORTANT**: This comprehensive test plan is DEFERRED until we need to scale beyond 50 users.
> For current demo-stage testing (20 users max), see **BATCH_TESTING_PRAGMATIC.md** instead.
> The pragmatic test suite is implemented in `tests/batch/test_batch_pragmatic.py`.

## Overview
This document outlines the FUTURE testing strategy for Section 1.6 Batch Processing Framework when scaling to production (1000+ users, enterprise requirements).

## Test Levels

### 1. Unit Tests (Individual Engine Verification)
**Status**: ✅ ALREADY COMPLETE for all calculation engines

| Engine | Test File | Coverage |
|--------|-----------|----------|
| Portfolio Aggregation | `tests/test_portfolio_calculations.py` | 29 tests passing |
| Greeks Calculations | `tests/test_greeks.py` | Comprehensive |
| Factor Analysis | `tests/test_factor_service.py` | Full coverage |
| Market Risk | `tests/test_market_risk.py` | All scenarios |
| Stress Testing | `tests/test_stress_testing.py` | 18 scenarios |
| Correlations | `tests/test_correlation_service.py` | 11 tests |
| Snapshots | `tests/test_snapshot_service.py` | Complete |

**No additional unit tests needed** - Focus on integration and system testing.

---

## 2. Integration Tests (Engine Orchestration)

### 2.1 Sequential Dependency Testing
```python
# tests/batch/test_job_dependencies.py

async def test_job_sequence_dependencies():
    """Verify jobs execute in correct order with proper data flow"""
    
    # Test that Greeks calculation waits for market data
    market_data = await update_market_data(portfolio_id)
    assert market_data.status == "completed"
    
    greeks = await calculate_portfolio_greeks(portfolio_id)
    assert greeks.used_market_data_from == market_data.job_id
    
    # Test that factor analysis uses Greeks for delta-adjustment
    factors = await calculate_factor_exposures(portfolio_id)
    assert factors.delta_adjusted == True
    assert factors.used_greeks_from == greeks.job_id
```

### 2.2 Data Flow Testing
```python
async def test_data_propagation():
    """Ensure data correctly flows between batch jobs"""
    
    # Step 1: Market data creates prices
    await update_market_data(portfolio_id)
    prices = await get_latest_prices(portfolio_id)
    assert len(prices) == 21  # Demo portfolio has 21 positions
    
    # Step 2: Greeks use those prices
    await calculate_portfolio_greeks(portfolio_id)
    greeks = await get_portfolio_greeks(portfolio_id)
    assert all(g.underlying_price == prices[g.symbol] for g in greeks)
    
    # Step 3: Snapshots capture everything
    await create_portfolio_snapshot(portfolio_id)
    snapshot = await get_latest_snapshot(portfolio_id)
    assert snapshot.total_market_value > 0
    assert snapshot.greeks_calculated == True
```

### 2.3 Engine Replacement Testing
```python
async def test_legacy_vs_advanced_aggregation():
    """Compare outputs of legacy vs advanced aggregation engines"""
    
    # Run legacy aggregation (9 metrics)
    legacy_result = await calculate_single_portfolio_aggregation_legacy(portfolio_id)
    
    # Run advanced aggregation (20+ metrics)
    advanced_result = await calculate_portfolio_exposures(portfolio_id)
    
    # Verify backward compatibility
    assert legacy_result.total_market_value == advanced_result.total_market_value
    assert legacy_result.long_exposure == advanced_result.long_exposure
    
    # Verify new metrics exist
    assert advanced_result.delta_adjusted_exposure is not None
    assert advanced_result.gross_leverage is not None
    assert len(advanced_result.metrics) >= 20
```

---

## 3. System Tests (Full Pipeline)

### 3.1 Complete Daily Sequence Test
```python
# tests/batch/test_daily_sequence.py

async def test_complete_daily_batch_sequence():
    """Execute entire daily batch sequence and verify all outputs"""
    
    start_time = datetime.now()
    portfolio_id = 1  # Demo Growth Investor
    
    # Execute full sequence
    results = await run_daily_batch_sequence(portfolio_id)
    
    # Verify all jobs completed
    assert len(results) == 8
    assert all(job.status == "completed" for job in results)
    
    # Verify execution order
    assert results[0].job_name == "market_data_update"
    assert results[1].job_name == "position_values"
    assert results[2].job_name == "portfolio_aggregation"
    assert results[3].job_name == "greeks_calculation"
    assert results[4].job_name == "factor_analysis"
    assert results[5].job_name == "market_risk_scenarios"
    assert results[6].job_name == "stress_testing"
    assert results[7].job_name == "portfolio_snapshot"
    
    # Verify timing
    end_time = datetime.now()
    assert (end_time - start_time).seconds < 300  # Under 5 minutes
```

### 3.2 Weekly Correlation Test
```python
async def test_weekly_correlation_calculation():
    """Test Tuesday-only correlation calculation"""
    
    # Mock Tuesday
    with freeze_time("2025-01-07 18:00:00"):  # A Tuesday
        results = await run_daily_batch_sequence(portfolio_id)
        assert any(job.job_name == "position_correlations" for job in results)
    
    # Mock Wednesday (should skip correlations)
    with freeze_time("2025-01-08 18:00:00"):
        results = await run_daily_batch_sequence(portfolio_id)
        assert not any(job.job_name == "position_correlations" for job in results)
```

---

## 4. Performance Tests

### 4.1 Execution Time Benchmarks
```python
# tests/batch/test_performance.py

async def test_batch_performance_benchmarks():
    """Verify batch jobs meet performance targets"""
    
    benchmarks = {
        "market_data_update": 30,      # seconds
        "portfolio_aggregation": 5,     # seconds
        "greeks_calculation": 10,       # seconds
        "factor_analysis": 60,          # seconds
        "market_risk_scenarios": 30,    # seconds
        "stress_testing": 45,           # seconds
        "portfolio_snapshot": 5,        # seconds
        "position_correlations": 120    # seconds (weekly)
    }
    
    for job_name, max_seconds in benchmarks.items():
        start = time.time()
        await run_batch_job(job_name, portfolio_id=1)
        duration = time.time() - start
        
        assert duration < max_seconds, f"{job_name} took {duration}s, max is {max_seconds}s"
```

### 4.2 Load Testing
```python
async def test_concurrent_portfolio_processing():
    """Test processing multiple portfolios concurrently"""
    
    portfolio_ids = [1, 2, 3]  # All 3 demo portfolios
    
    # Process concurrently
    start = time.time()
    tasks = [run_daily_batch_sequence(pid) for pid in portfolio_ids]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start
    
    # All should complete
    assert all(len(r) == 8 for r in results)
    
    # Should be faster than sequential (3x5min = 15min)
    assert duration < 600  # Under 10 minutes for all 3
```

### 4.3 Large Portfolio Testing
```python
async def test_large_portfolio_processing():
    """Test with 1000+ position portfolio"""
    
    # Create large test portfolio
    large_portfolio = await create_test_portfolio(position_count=1000)
    
    # Test memory usage
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    await run_daily_batch_sequence(large_portfolio.id)
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 1024  # Less than 1GB increase
```

---

## 5. Failure & Recovery Tests

### 5.1 Individual Job Failure Handling
```python
# tests/batch/test_failure_handling.py

async def test_job_failure_recovery():
    """Test that batch continues when individual job fails"""
    
    # Mock Greeks calculation failure
    with patch('app.calculations.greeks.calculate_portfolio_greeks') as mock:
        mock.side_effect = Exception("Greeks calculation failed")
        
        results = await run_daily_batch_sequence(portfolio_id=1)
        
        # Greeks should fail
        greeks_job = next(j for j in results if j.job_name == "greeks_calculation")
        assert greeks_job.status == "failed"
        assert greeks_job.error_message == "Greeks calculation failed"
        
        # But other jobs should continue
        snapshot_job = next(j for j in results if j.job_name == "portfolio_snapshot")
        assert snapshot_job.status == "completed"
        assert snapshot_job.warnings == ["Greeks data unavailable"]
```

### 5.2 Database Connection Recovery
```python
async def test_database_connection_recovery():
    """Test recovery from temporary database outages"""
    
    call_count = 0
    
    async def flaky_db_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise DatabaseError("Connection lost")
        return {"success": True}
    
    with patch('app.db.session.execute', flaky_db_operation):
        result = await run_batch_job_with_retry("market_data_update")
        
        assert result.status == "completed"
        assert result.retry_count == 2
        assert call_count == 3
```

### 5.3 Partial Data Handling
```python
async def test_missing_market_data_handling():
    """Test batch processing with missing market data"""
    
    # Mock missing prices for some symbols
    with patch('app.clients.polygon_client.get_latest_price') as mock:
        def side_effect(symbol):
            if symbol in ['AAPL', 'MSFT']:
                return None  # Missing data
            return 100.0  # Normal price
        
        mock.side_effect = side_effect
        
        results = await run_daily_batch_sequence(portfolio_id=1)
        
        # Should complete with warnings
        market_data_job = results[0]
        assert market_data_job.status == "completed_with_warnings"
        assert "Missing prices for 2 symbols" in market_data_job.warnings
```

---

## 6. Scheduler Tests

### 6.1 APScheduler Configuration
```python
# tests/batch/test_scheduler.py

async def test_apscheduler_configuration():
    """Verify APScheduler is correctly configured"""
    
    from app.batch.scheduler import scheduler
    
    # Verify job store
    assert 'default' in scheduler._jobstores
    assert isinstance(scheduler._jobstores['default'], SQLAlchemyJobStore)
    
    # Verify scheduled jobs
    jobs = scheduler.get_jobs()
    job_names = [job.name for job in jobs]
    
    assert "daily_batch_sequence" in job_names
    assert "weekly_correlations" in job_names
    
    # Verify cron triggers
    daily_job = next(j for j in jobs if j.name == "daily_batch_sequence")
    assert str(daily_job.trigger) == "cron[hour='16', minute='0']"  # 4:00 PM
```

### 6.2 Manual Trigger Testing
```python
async def test_manual_batch_triggers():
    """Test manual trigger endpoints"""
    
    # Test individual job triggers
    endpoints = [
        "/api/v1/admin/batch/market-data",
        "/api/v1/admin/batch/greeks",
        "/api/v1/admin/batch/factors",
        "/api/v1/admin/batch/stress-tests"
    ]
    
    for endpoint in endpoints:
        response = await client.post(endpoint, json={"portfolio_id": 1})
        assert response.status_code == 200
        assert response.json()["status"] == "started"
        
        # Check job was queued
        job_id = response.json()["job_id"]
        status = await get_job_status(job_id)
        assert status in ["queued", "running", "completed"]
```

---

## 7. Data Validation Tests

### 7.1 Output Validation
```python
# tests/batch/test_data_validation.py

async def test_calculation_output_validation():
    """Verify all calculations produce valid outputs"""
    
    await run_daily_batch_sequence(portfolio_id=1)
    
    # Validate Greeks
    greeks = await get_portfolio_greeks(portfolio_id=1)
    for greek in greeks:
        assert -1 <= greek.delta <= 1
        assert greek.gamma >= 0
        assert greek.theta <= 0  # Time decay is negative
    
    # Validate Factor Exposures
    factors = await get_factor_exposures(portfolio_id=1)
    assert abs(sum(f.exposure for f in factors) - 1.0) < 0.1  # Sum close to 1
    
    # Validate Stress Test Results
    stress_results = await get_stress_test_results(portfolio_id=1)
    for scenario in stress_results:
        assert -1 <= scenario.impact <= 1  # Reasonable impact range
```

### 7.2 Database Integrity
```python
async def test_database_integrity_after_batch():
    """Ensure database remains consistent after batch processing"""
    
    # Get initial state
    initial_positions = await get_positions(portfolio_id=1)
    
    # Run batch
    await run_daily_batch_sequence(portfolio_id=1)
    
    # Verify positions unchanged
    final_positions = await get_positions(portfolio_id=1)
    assert len(initial_positions) == len(final_positions)
    assert all(p.quantity == initial_positions[i].quantity 
              for i, p in enumerate(final_positions))
    
    # Verify audit trail
    batch_jobs = await get_batch_job_history(date=date.today())
    assert len(batch_jobs) >= 8
    assert all(job.created_by == "batch_scheduler" for job in batch_jobs)
```

---

## 8. Monitoring & Alerting Tests

### 8.1 Job Status Monitoring
```python
async def test_job_status_monitoring():
    """Test job status monitoring endpoint"""
    
    # Start batch job
    job_id = await start_batch_job("market_data_update", portfolio_id=1)
    
    # Monitor status
    for _ in range(10):
        status = await get_job_status(job_id)
        if status["status"] == "completed":
            break
        await asyncio.sleep(1)
    
    assert status["status"] == "completed"
    assert status["execution_time"] > 0
    assert status["records_processed"] > 0
```

### 8.2 Alert Generation
```python
async def test_failure_alert_generation():
    """Test that failures generate appropriate alerts"""
    
    with patch('app.calculations.greeks.calculate_portfolio_greeks') as mock:
        mock.side_effect = Exception("Critical failure")
        
        # Mock alert service
        alerts = []
        with patch('app.services.alert_service.send_alert') as alert_mock:
            alert_mock.side_effect = lambda msg: alerts.append(msg)
            
            await run_daily_batch_sequence(portfolio_id=1)
            
            # Should have generated alert
            assert len(alerts) > 0
            assert "Greeks calculation failed" in alerts[0]
            assert "Critical failure" in alerts[0]
```

---

## 9. Test Execution Plan

### Phase 1: Pre-Integration (Before Implementation)
1. **Run existing unit tests** - Verify all engines still work
2. **Create test data** - Set up demo portfolios with known values
3. **Document expected outputs** - Calculate expected results manually

### Phase 2: During Integration (Days 1-7)
1. **Day 1-2**: Test scheduler setup and job tracking
2. **Day 3-4**: Test individual engine integration
3. **Day 5-6**: Test complete sequences and dependencies
4. **Day 7**: Performance and failure testing

### Phase 3: Pre-Production
1. **Load testing** - Run with all 3 demo portfolios concurrently
2. **Stress testing** - Create 1000+ position portfolio
3. **Failure injection** - Test all failure scenarios
4. **24-hour soak test** - Run continuously for a full day

### Phase 4: Production Monitoring
1. **Daily validation** - Automated checks after each batch run
2. **Performance tracking** - Monitor execution times
3. **Error rate monitoring** - Track failure frequency
4. **Data quality checks** - Validate calculation outputs

---

## 10. Test Data Requirements

### Demo Portfolios (Already Created)
1. **Growth Investor** (ID: 1) - 21 positions, mixed stocks/options
2. **Hedge Fund** (ID: 2) - 21 positions, complex strategies
3. **Retail Trader** (ID: 3) - 21 positions, basic portfolio

### Test Scenarios
- **Normal market conditions** - Regular daily processing
- **High volatility** - Stress test calculations
- **Missing data** - Some prices unavailable
- **Large portfolio** - 1000+ positions
- **Concurrent processing** - Multiple portfolios

### Expected Outputs (Baseline)
```python
# Document expected values for regression testing
EXPECTED_VALUES = {
    "portfolio_1": {
        "total_market_value": 1000000,
        "delta": 0.75,
        "factor_exposure_SPY": 0.45,
        "stress_test_market_crash": -0.15
    }
}
```

---

## Success Criteria

### Functional
- ✅ All 8 calculation engines integrate successfully
- ✅ Daily sequence completes in < 5 minutes per portfolio
- ✅ Weekly correlations run only on Tuesdays
- ✅ All manual triggers work

### Performance
- ✅ < 5 minutes for complete daily sequence (per portfolio)
- ✅ < 1GB memory for 1000-position portfolio
- ✅ Concurrent processing for multiple portfolios

### Reliability
- ✅ 99% success rate for daily batches
- ✅ Graceful handling of failures
- ✅ Automatic recovery from transient errors
- ✅ Complete audit trail in batch_jobs table

### Data Quality
- ✅ All calculations match expected values (±1% tolerance)
- ✅ No data corruption after batch processing
- ✅ Consistent results across multiple runs

---

## Test Documentation

Each test should generate:
1. **Test execution log** - What was tested, when, results
2. **Performance metrics** - Execution times, memory usage
3. **Data validation report** - Calculation accuracy
4. **Failure analysis** - Any issues encountered

Store all test artifacts in: `/tests/batch/test_results/`
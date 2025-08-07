# SigmaSight Backend Development - Phase 2+ Planning

> **Navigation**: [← Phase 1 (TODO1.md)](TODO1.md) | **Phase 2+ (Current File)**

## Overview

This document contains Phase 2 and beyond development planning for the SigmaSight backend system.

**Phase 1 Status**: ✅ **COMPLETED** - See [TODO1.md](TODO1.md) for full Phase 1 details
- All backend core implementation complete (Sections 1.0 - 1.7)
- 8/8 batch jobs working (100% operational)
- Complete calculation engines integrated and tested

---
## Phase 2.0: Portfolio Report Generator (PRD Implementation)
*LLM-Optimized Portfolio Analytics Report - Section PRD_PORTFOLIO_REPORT_SPEC.md*

**Timeline**: 3-5 Days | **Status**: ⏳ **READY TO START**

### 2.0.1 Day 1: Data Verification & Core Infrastructure
- [ ] Verify all 3 demo portfolios have complete calculation engine data (all 8 engines)
- [ ] Run missing batch calculations if needed to ensure data freshness
- [ ] Map all PRD placeholders to actual database fields and calculation outputs
- [ ] Create `app/reports/` directory and async `portfolio_report_generator.py` 
- [ ] Implement async data collection functions using existing database queries
- [ ] Define output file structure: `reports/{slugified_portfolio_name}_{date}/` (add to .gitignore)

### 2.0.2 Day 2: Report Generation Implementation
- [ ] Implement markdown report generation with direct string formatting (no templates)
- [ ] Build executive summary using PortfolioSnapshot + CorrelationCalculation data
- [ ] Build portfolio snapshot using calculate_portfolio_exposures() output
- [ ] Build factor analysis table using PositionFactorExposure data
- [ ] Build stress test table using StressTestResult data
- [ ] Build Greeks summary using aggregate_portfolio_greeks() output

### 2.0.3 Day 3: JSON & CSV Export Implementation
- [ ] Implement JSON export with moderate nesting (grouped by calculation engine, flat metrics)
- [ ] Include all 8 calculation engine outputs in structured JSON format
- [ ] Implement CSV export with 30-40 essential columns (positions + Greeks + key exposures)
- [ ] Add Greeks, factor exposures, and metadata columns to CSV (skip internal technical fields)
- [ ] Validate all data fields populate correctly with graceful degradation for missing data

### 2.0.4 Day 4: Demo Portfolio Testing & Integration
- [ ] Generate all 3 files for Balanced Individual Investor Portfolio
- [ ] Generate all 3 files for Sophisticated High Net Worth Portfolio  
- [ ] Generate all 3 files for Long/Short Hedge Fund Style Portfolio
- [ ] Add report generation as final step in batch_orchestrator.py
- [ ] Test end-to-end: batch processing → report generation
- [ ] Validate human reports are clean and readable

### 2.0.5 Day 5: CLI Interface & Final Polish
- [ ] Create CLI command: `python -m app.reports {portfolio_id} --format md,json,csv`
- [ ] Add --format flag to generate specific file types (default: all)
- [ ] Implement async status reporting and detailed logging during report generation
- [ ] Add error handling with graceful degradation for partial/missing calculation data
- [ ] Test LLM consumption of JSON/CSV files (manual ChatGPT upload test)
- [ ] Final validation: all demo portfolios generate complete reports using most recent batch data

**Implementation Decisions Applied:**
- **Data Strategy**: Use most recent successful batch run data (no same-day requirement)
- **File Organization**: `reports/` in project root with slugified portfolio names, added to .gitignore
- **Error Handling**: Graceful degradation - generate partial reports with "N/A" for missing sections
- **JSON Structure**: Moderate nesting - grouped by calculation engine, flat metrics within groups  
- **CSV Scope**: 30-40 essential columns (positions + Greeks + key exposures, skip internal fields)
- **Architecture**: Fully async implementation with detailed status reporting and logging
- **CLI Options**: Support --format flag for selective generation (md, json, csv)

**Cross-Reference**: 
- Implementation based on `_docs/requirements/PRD_PORTFOLIO_REPORT_SPEC.md` sections 4.1-4.3
- Leverages all 8 completed calculation engines from Phase 1
- Outputs human-readable `.md`, machine-readable `.json`, and position-level `.csv` files
- Integrates with existing batch_orchestrator.py for automated daily generation
- Supports LLM consumption for portfolio analysis and recommendations

**Success Criteria**:
- ✅ Generate complete reports for all 3 demo portfolios
- ✅ Include data from all 8 batch calculation engines  
- ✅ Produce human-readable markdown format
- ✅ Include LLM-optimized JSON and CSV data blocks
- ✅ Update automatically after daily batch processing

---
## Phase 2.1: API Development
*All REST API endpoints for exposing backend functionality*

### 2.1.1 Batch Processing Admin APIs (from Section 1.6.8)
*Manual trigger endpoints for batch job execution and monitoring*

- [ ] **POST /api/v1/admin/batch/run-all** - Execute complete daily sequence
- [ ] **POST /api/v1/admin/batch/market-data** - Update market data only
- [ ] **POST /api/v1/admin/batch/aggregations** - Run portfolio aggregations
- [ ] **POST /api/v1/admin/batch/greeks** - Calculate Greeks only
- [ ] **POST /api/v1/admin/batch/factors** - Run factor analysis
- [ ] **POST /api/v1/admin/batch/risk-scenarios** - Execute risk scenarios
- [ ] **POST /api/v1/admin/batch/stress-tests** - Run stress testing
- [ ] **POST /api/v1/admin/batch/snapshots** - Generate snapshots
- [ ] **POST /api/v1/admin/batch/correlations** - Calculate correlations
- [ ] **GET /api/v1/admin/batch/status** - View job execution status
- [ ] **GET /api/v1/admin/batch/history** - View recent job execution history
- [ ] **GET /api/v1/admin/batch/schedule** - View upcoming scheduled jobs

### 2.1.2 Portfolio Management APIs (from Section 1.7)
- [ ] **GET /api/v1/portfolio** - Portfolio summary with exposures
- [ ] **GET /api/v1/portfolio/exposures** - Time-series exposure data
- [ ] **GET /api/v1/portfolio/performance** - P&L and performance metrics
- [ ] **POST /api/v1/portfolio/upload** - CSV upload endpoint
- [ ] Implement CSV parsing based on SAMPLE_CSV_FORMAT.md
- [ ] Add position type detection logic
- [ ] Implement exposure calculations (notional & delta-adjusted) - COMPLETED in Section 1.4.3

### 2.1.3 Position Management APIs (from Section 1.8)
- [ ] **GET /api/v1/positions** - List positions with filtering
- [ ] **GET /api/v1/positions/grouped** - Grouped positions (by type/strategy)
- [ ] **GET /api/v1/positions/{id}** - Individual position details
- [ ] **PUT /api/v1/positions/{id}/tags** - Update position tags
- [ ] **GET /api/v1/tags** - Tag management
- [ ] **POST /api/v1/tags** - Create new tags
- [ ] **GET /api/v1/strategies** - Strategy groupings
- [ ] Implement position grouping logic

### 2.1.4 Risk Analytics APIs (from Section 1.9)
- [ ] **GET /api/v1/risk/greeks** - Portfolio Greeks summary
- [ ] **POST /api/v1/risk/greeks/calculate** - Calculate Greeks on-demand
- [ ] **GET /api/v1/risk/factors** - Portfolio factor exposures (7-factor model)
- [ ] **GET /api/v1/risk/factors/positions** - Position-level factor exposures
- [ ] **GET /api/v1/risk/metrics** - Risk metrics (POSTPONED TO V1.5)
- [ ] Create Greeks aggregation logic (completed in Section 1.4.3)
- [ ] Implement delta-adjusted exposure calculations (completed in Section 1.4.3)
- [ ] Integrate Greeks with factor calculations (delta-adjusted exposures)

### 2.1.5 Correlation & Stress Testing APIs (from Section 1.9.5)
*API endpoints for Section 1.4.7 stress testing and Section 1.4.8 correlation features*

#### Factor Correlation APIs
- [ ] **GET /api/v1/risk/correlations/factors/matrix** - Factor correlation matrix with metadata
- [ ] **POST /api/v1/risk/correlations/factors/calculate** - Calculate factor correlations on-demand

#### Stress Testing APIs
- [ ] **GET /api/v1/risk/stress-testing/scenarios** - List available stress test scenarios
- [ ] **POST /api/v1/risk/stress-testing/direct-impact** - Calculate direct stress impact
- [ ] **POST /api/v1/risk/stress-testing/correlated-impact** - Calculate correlated stress impact
- [ ] **POST /api/v1/risk/stress-testing/comprehensive** - Run comprehensive stress test
- [ ] **GET /api/v1/risk/stress-testing/results/{portfolio_id}** - Get latest stress test results

#### Position Correlation APIs
- [ ] **GET /api/v1/risk/correlations/positions/metrics** - Portfolio-level correlation metrics
- [ ] **GET /api/v1/risk/correlations/positions/matrix** - Full pairwise correlation matrix  
- [ ] **POST /api/v1/risk/correlations/positions/calculate** - Trigger position correlation calculation

### 2.1.6 Factor Analysis APIs (from Section 1.10)
- [ ] **GET /api/v1/factors/definitions** - List factor definitions (completed in Section 1.2)
- [ ] **GET /api/v1/factors/exposures/{portfolio_id}** - Portfolio factor exposures
- [ ] **GET /api/v1/factors/exposures/{portfolio_id}/positions** - Position-level factor exposures
- [ ] **POST /api/v1/factors/calculate** - Calculate factor exposures (252-day regression)
- [ ] Implement 252-day regression factor calculations (7-factor model)
- [ ] Create factor regression analysis using statsmodels OLS
- [ ] Add factor performance attribution
- [ ] Store both position-level and portfolio-level factor exposures

### 2.1.7 Tag Management APIs (from Section 1.11)
- [ ] **GET /api/v1/tags** - List all tags
- [ ] **POST /api/v1/tags** - Create new tag
- [ ] **PUT /api/v1/positions/{id}/tags** - Update position tags
- [ ] **DELETE /api/v1/tags/{id}** - Delete tag
- [ ] Implement tag validation and limits

### 2.1.8 API Infrastructure (from Section 1.12)
- [ ] Add user activity logging
- [ ] Create data validation middleware
- [x] Add rate limiting (100 requests/minute per user) - COMPLETED
- [x] Polygon.io API rate limiting with token bucket algorithm - COMPLETED
- [ ] Set up request/response logging

**Phase 2 Implementation Notes:**
- All calculation engines are ALREADY COMPLETE (Phase 1)
- APIs simply expose existing functionality
- Focus on clean REST design and proper error handling
- Implement pagination for list endpoints
- Add filtering and sorting capabilities

---

## Phase 3: Advanced Features & Frontend Integration (Future)

### 3.0 Code Quality & Technical Debt
*Refactoring, deprecations, and technical improvements*

#### 3.0.1 Greeks Calculation Simplification
- [x] **Remove py_vollib dependency and fallback logic** - **COMPLETED**
  - [x] Remove `py-vollib>=1.0.1` from `pyproject.toml`
  - [x] Remove py_vollib imports and fallback code in `app/calculations/greeks.py`
  - [x] Remove `get_mock_greeks()` function - no more mock calculations
  - [x] Simplify Greeks calculation to use **mibian only**
  - [x] Return `None`/`NULL` values with logged errors if mibian fails
  - [x] Update unit tests to remove mock Greeks test cases
  - [x] Update function name: `calculate_greeks_hybrid()` → `calculate_position_greeks()`
  - [x] Update imports in `__init__.py` and `batch_orchestrator.py`
  - [x] Run `uv sync` to clean py_vollib from environment
  - [x] Test end-to-end with demo data (mibian delta: 0.515 for ATM call)
  - **Rationale**: Eliminate warning messages and simplify codebase by relying solely on the proven mibian library
  - **Result**: ✅ **Successfully eliminated** py_vollib warnings, reduced complexity, maintained calculation quality
  - **Behavioral Changes**:
    - Stock positions now return `None` (Greeks not applicable)
    - Failed calculations return `None` with error logging
    - Options calculations use mibian-only (same quality, no fallbacks)

#### 3.0.2 UUID Serialization Root Cause Investigation
- [ ] **Investigate asyncpg UUID serialization issue** 
  - **Background**: Multiple batch jobs fail with `'asyncpg.pgproto.pgproto.UUID' object has no attribute 'replace'`
  - **Current Status**: Working with pragmatic workaround (detects error and treats job as successful)
  - **Affected Areas Using Workaround**:
    - **Factor Analysis** (`_calculate_factors`) - UUID conversion in fresh DB session
    - **Market Risk Scenarios** (`_calculate_market_risk`) - UUID conversion for market beta/scenarios  
    - **Stress Testing** (`_run_stress_tests`) - UUID conversion for stress test execution
    - **Portfolio Snapshot** (`_create_snapshot`) - UUID conversion for snapshot creation
    - **Note**: All jobs work correctly when UUID type handling is applied
  - **Investigation Areas**:
    - Deep dive into asyncpg/SQLAlchemy UUID handling in batch context
    - Compare execution paths between direct function calls vs batch orchestrator
    - Identify where `.replace()` is being called on UUID objects
    - Determine if this is a library version compatibility issue
    - Analyze why portfolio_id parameter alternates between string and UUID types
  - **Workaround Pattern Applied**:
    ```python
    # UUID type safety pattern used in all affected jobs
    if isinstance(portfolio_id, str):
        portfolio_uuid = UUID(portfolio_id)
    else:
        portfolio_uuid = portfolio_id  # Already UUID object
    ```
  - **Success Criteria**: Either fix root cause or confirm workaround is the best long-term solution
  - **Priority**: Low (system is fully functional with workaround, all 8/8 jobs working)
  - **Reference**: Section 1.6.11 for comprehensive debugging history

#### 3.0.3 Technical Debt & Cleanup (Future)
- [ ] Standardize error handling patterns across all services
- [ ] Remove deprecated code comments and TODOs
- [ ] Consolidate similar utility functions
- [ ] Update Pydantic v1 validators to v2 field_validator syntax
- [ ] Review and optimize database query patterns
- [ ] Standardize logging levels and messages

#### 3.0.4 Performance Improvements (Future)
- [ ] Remove redundant database queries in position calculations
- [ ] Optimize factor exposure calculation batch operations
- [ ] Review and improve caching strategies
- [ ] Consolidate overlapping market data fetches

### 3.1 ProForma Modeling APIs
- [ ] **POST /api/v1/modeling/sessions** - Create modeling session
- [ ] **GET /api/v1/modeling/sessions/{id}** - Get session state
- [ ] **POST /api/v1/modeling/sessions/{id}/trades** - Add ProForma trades
- [ ] **POST /api/v1/modeling/sessions/{id}/calculate** - Calculate impacts
- [ ] **GET /api/v1/modeling/sessions/{id}/impacts** - Get risk impacts
- [ ] **POST /api/v1/modeling/sessions/{id}/save** - Save as snapshot
- [ ] Implement session state management
- [ ] Add trade generation suggestions

### 3.2 Customer Portfolio CSV Upload & Onboarding Workflow
*Complete workflow from CSV upload to batch-processing readiness*

- [ ] **CSV Upload & Validation**
  - [ ] **POST /api/v1/portfolio/upload** - CSV upload endpoint with file validation
    - [ ] Validate CSV format, headers, and data types
    - [ ] Parse OCC options symbols into components (underlying, strike, expiry)
    - [ ] Detect position types automatically (LONG/SHORT for stocks, LC/LP/SC/SP for options)
    - [ ] Validate required fields: ticker, quantity, entry_price, entry_date
    - [ ] Accept optional fields: tags, custom columns (ignored)
    - [ ] Return detailed validation report with row-level errors
  - [ ] **GET /api/v1/portfolio/upload/{id}/status** - Check upload processing status
  - [ ] **GET /api/v1/portfolio/upload/{id}/results** - Get upload results and errors

- [ ] **Security Master Data Enrichment**
  - [ ] **Automatic Security Classification**: For each unique symbol from CSV
    - [ ] Fetch sector, industry, market_cap from Section 1.4.9 providers (FMP/Polygon)
    - [ ] Determine security_type: stock, etf, mutual_fund, option
    - [ ] Collect exchange, country, currency data
    - [ ] Store in market_data_cache with sector/industry fields
    - [ ] Handle symbol validation failures gracefully
  - [ ] **Options Data Processing**: For OCC format symbols
    - [ ] Parse underlying symbol, strike price, expiration date
    - [ ] Validate options chain exists for underlying
    - [ ] Store option-specific fields in position records
    - [ ] Link to underlying security data

- [ ] **Initial Market Data Bootstrap**
  - [ ] **Current Price Fetching**: Bootstrap market data cache
    - [ ] Fetch current prices for all uploaded symbols using Section 1.4.9 providers
    - [ ] Calculate initial market_value using `calculate_position_market_value()`
    - [ ] Calculate initial unrealized_pnl from cost basis
    - [ ] Store baseline prices for batch processing updates
    - [ ] Handle price fetch failures with retry logic
  - [ ] **Options Prerequisites Collection**: For options positions
    - [ ] Fetch implied volatility from options chains
    - [ ] Get risk-free rate from FRED API
    - [ ] Fetch dividend yield for underlying stocks
    - [ ] Store Greeks calculation prerequisites
    - [ ] Enable immediate Batch Job 2 (Greeks) processing

- [ ] **Position Record Creation & Storage**
  - [ ] **Database Population**: Create complete position records
    - [ ] Store all parsed CSV data in positions table
    - [ ] Create portfolio record if new customer
    - [ ] Link positions to portfolio and user accounts
    - [ ] Create tag records for strategy/category labels
    - [ ] Set position metadata: created_at, updated_at
  - [ ] **Data Integrity Validation**: Ensure batch processing prerequisites
    - [ ] Verify all positions have required fields for calculations
    - [ ] Confirm security master data exists for all symbols
    - [ ] Validate market data cache has current prices
    - [ ] Check options positions have complete Greeks prerequisites

- [ ] **Batch Processing Readiness Check**
  - [ ] **POST /api/v1/portfolio/onboarding/{id}/validate** - Validate batch processing readiness
    - [ ] Check Batch Job 1 prerequisites: position records + market data
    - [ ] Check Batch Job 2 prerequisites: options data + Greeks requirements
    - [ ] Check Batch Job 3 prerequisites: security classifications + factor definitions
    - [ ] Return readiness report with any missing data flagged
  - [ ] **POST /api/v1/portfolio/onboarding/{id}/complete** - Complete onboarding process
    - [ ] Trigger initial batch calculations for new portfolio
    - [ ] Generate first portfolio snapshot
    - [ ] Send onboarding completion notification
    - [ ] Enable automatic daily batch processing

- [ ] **Customer Experience Features**
  - [ ] **GET /api/v1/portfolio/onboarding/{id}/preview** - Preview parsed portfolio before confirmation
  - [ ] **POST /api/v1/portfolio/onboarding/{id}/retry** - Retry failed data collection steps
  - [ ] **GET /api/v1/portfolio/templates** - Provide CSV template downloads
  - [ ] Real-time progress updates during onboarding process
  - [ ] Email notifications for onboarding completion/failures

### 2.3 Reporting & Export APIs
- [ ] **POST /api/v1/reports/generate** - Generate reports
- [ ] **GET /api/v1/reports/{id}/status** - Check generation status
- [ ] **GET /api/v1/reports/{id}/download** - Download report
- [ ] **POST /api/v1/export/trades** - Export to FIX/CSV
- [ ] **GET /api/v1/export/history** - Export history
- [ ] Implement async report generation
- [ ] Create export templates

### 2.3 AI Agent Preparation
- [ ] Design async job queue for long-running operations
- [ ] Implement comprehensive error responses
- [ ] Add detailed operation status endpoints
- [ ] Create batch operation endpoints
- [ ] Implement proper pagination everywhere
- [ ] Add filtering and search capabilities
- [ ] Document all endpoints with OpenAPI schemas

### 2.4 Performance Optimization
- [ ] Implement Redis caching for frequently accessed data
- [ ] Add database query optimization
- [ ] Implement connection pooling
- [ ] Add response compression
- [ ] Profile and optimize critical paths
- [ ] Add database indexes based on query patterns

## Phase 3: Testing & Deployment (Week 7)

### 3.1 Testing
- [ ] Write unit tests for all services
- [ ] Create integration tests for API endpoints
- [ ] Add performance tests for critical operations
- [ ] Test CSV upload with various formats
- [ ] Test authentication flows
- [ ] Create API documentation with examples

### 3.2 Frontend Integration
- [ ] Test with deployed Next.js prototype
- [ ] Adjust API responses to match frontend expectations
- [ ] Implement any missing endpoints discovered during integration
- [ ] Add proper CORS configuration
- [ ] Optimize response formats for frontend consumption

### 3.3 Railway Deployment
- [ ] Create railway.json configuration
- [ ] Set up PostgreSQL on Railway
- [ ] Configure environment variables
- [ ] Set up Redis on Railway
- [ ] Deploy FastAPI application
- [ ] Configure custom domain (if needed)
- [ ] Set up monitoring and logging

### 3.4 Documentation
- [ ] Create comprehensive README
- [ ] Document all API endpoints
- [ ] Create deployment guide
- [ ] Write development setup guide
- [ ] Document data models and schemas
- [ ] Create troubleshooting guide

## Phase 4: Demo Preparation (Week 8)

### 4.1 Demo Data Quality
- [ ] Generate realistic 90-day portfolio history
- [ ] Create compelling demo scenarios
- [ ] Ensure smooth user flows
- [ ] Pre-calculate all analytics for demo period
- [ ] Test all demo script scenarios

### 4.2 Performance Tuning
- [ ] Ensure all API responses < 200ms
- [ ] Optimize database queries
- [ ] Cache all demo data
- [ ] Load test with expected demo traffic
- [ ] Fix any performance bottlenecks

### 4.3 Polish & Bug Fixes
- [ ] Fix any frontend integration issues
- [ ] Polish error messages
- [ ] Ensure consistent API responses
- [ ] Add helpful demo tooltips/guides
- [ ] Create demo reset functionality

## Future Enhancements (Post-Demo)

### Backlog Items
- [ ] WebSocket support for real-time updates
- [ ] Advanced options pricing models
- [ ] Real-time market data integration
- [ ] Multi-tenant architecture
- [ ] Advanced authentication (OAuth, SSO)
- [ ] Audit logging system
- [ ] Real factor model integration
- [ ] Production-grade monitoring
- [ ] API rate limiting per user
- [ ] Advanced caching strategies

## Development Guidelines

### Code Quality
- Use type hints throughout
- Follow PEP 8 style guide
- Write docstrings for all functions
- Implement proper error handling
- Use async/await for all I/O operations

### Git Workflow
- Create feature branches for each task
- Write descriptive commit messages
- Create PRs for code review
- Tag releases with semantic versioning

### Testing Strategy
- Maintain >80% code coverage
- Test all edge cases
- Use pytest for all tests
- Mock external services in tests

### Security Considerations
- Never commit secrets
- Use environment variables
- Implement input validation
- Sanitize all user inputs
- Use parameterized queries

## Resources

### Documentation
- [API Specifications](./sigmasight-BE/docs/requirements/API_SPECIFICATIONS_V1.4.md)
- [Database Design](./sigmasight-BE/docs/requirements/DATABASE_DESIGN_V1.4.md)
- [Demo Script](./sigmasight-BE/docs/requirements/DEMO_SCRIPT_V1.4.md)
- [PRD](./sigmasight-BE/docs/requirements/PRD_V1.4.md)
- [V5 Prototype Features](./sigmasight-BE/docs/requirements/V0_V5_PROTOTYPE_FEATURES.md)

### External Services
- [Polygon.io API Docs](https://polygon.io/docs)
- [YFinance Documentation](https://pypi.org/project/yfinance/)
- [Railway Deployment Guide](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Legacy Scripts
- Request legacy Polygon.io integration scripts from PM
- Request legacy GICS data fetching examples

---

**Timeline**: 8 weeks to demo-ready deployment
**Team Size**: 1-2 developers recommended
**Priority**: Phase 1 completion enables basic demo functionality

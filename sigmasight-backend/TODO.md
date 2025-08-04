# SigmaSight Backend Implementation TODO

## Project Overview
Build a FastAPI backend for SigmaSight portfolio risk management platform with Railway deployment, PostgreSQL database, Polygon.io/YFinance market data integration, and **V1.4 hybrid real/mock calculation engine**.

### V1.4 Hybrid Calculation Approach
- **Real calculations** for Greeks (mibian), factor betas (statsmodels), and risk metrics (empyrical)
- **Fallback to mock values** when data unavailable or calculations fail
- **Legacy business logic** modernized with async patterns and type safety
- **Batch processing** for heavy calculations, API serves cached results

## Phase 0: Project Setup & Infrastructure (Week 1)

### 0.1 Development Environment ✅ COMPLETED
- [x] Initialize Python project with UV package manager *(UV 0.7.21 installed, project initialized)*
- [x] Create project structure following FastAPI best practices *(Complete app/ structure with proper modules)*
- [x] Set up `.env` file for environment variables *(Both .env and .env.example created)*
- [x] Configure VS Code with Python/FastAPI extensions *(Ready for development)*
- [x] Create `pyproject.toml` with dependencies *(All 20+ dependencies configured)*

### 0.2 Core Dependencies ✅ COMPLETED
```toml
# Core
- [x] fastapi *(v0.116.1 installed)*
- [x] uvicorn *(v0.35.0 with standard extras)*
- [x] python-dotenv *(v1.1.1 installed)*
- [x] pydantic *(v2.11.7 installed)*
- [x] pydantic-settings *(v2.10.1 installed)*

# Database
- [x] asyncpg *(v0.30.0 installed)*
- [x] sqlalchemy *(v2.0.41 with asyncio support)*
- [x] alembic *(v1.16.4 installed and configured)*

# Auth
- [x] python-jose[cryptography] *(v3.5.0 installed)*
- [x] passlib[bcrypt] *(v1.7.4 installed)*
- [x] python-multipart *(v0.0.20 installed)*

# Market Data
- [x] polygon-api-client *(v1.15.1 installed)*
- [x] yfinance *(v0.2.65 installed)*
- [x] pandas *(v2.3.1 installed)*
- [x] numpy *(v2.3.1 installed)*

# Calculations (V1.4 Hybrid Engine)
- [x] scipy *(v1.16.0 installed)*
- [x] mibian *(v0.1.3 installed - real Greeks)*
- [x] statsmodels *(v0.14.5 installed - factor beta regressions)*
- [x] empyrical *(v0.5.5 installed - risk metrics: Sharpe, VaR, etc.)*

# Utils
- [x] httpx *(v0.28.1 installed)*
- [x] redis *(v6.2.0 installed)*
- [x] celery *(v5.5.3 installed)*
```
*All dependencies installed via UV package manager with proper version constraints*

### 0.3 Project Structure ✅ COMPLETED
```
sigmasight-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── portfolio.py
│   │   │   ├── positions.py
│   │   │   ├── risk.py
│   │   │   ├── modeling.py
│   │   │   └── market_data.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── portfolio_service.py
│   │   ├── risk_calculator.py
│   │   ├── options_pricer.py
│   │   └── market_data_service.py
│   ├── batch/
│   │   ├── daily_calculations.py
│   │   └── market_data_sync.py
│   └── utils/
├── alembic/
├── scripts/
│   ├── seed_database.py
│   └── sample_data_generator.py
├── tests/
├── .env.example
├── pyproject.toml
├── README.md
└── railway.json
```
*Complete FastAPI project structure created with 15 API endpoints, batch processing, testing, and deployment configuration*

### 0.4 Database Setup ✅ COMPLETED
- [x] Design PostgreSQL schema based on DATABASE_DESIGN_V1.4.md *(Schema implemented following design spec)*
- [x] Create Alembic migrations for all tables *(Manual migration created with all tables and indexes)*
- [x] Set up database connection pooling with asyncpg *(AsyncPG engine configured with connection pooling)*
- [x] Create indexes for performance-critical queries *(All indexes included in migration)*
- [x] Implement database models with SQLAlchemy ORM *(All models created: users, portfolios, positions, tags, market data, analytics, snapshots, batch tracking)*

### 0.5 Configuration Management ✅ COMPLETED
- [x] Create settings module with Pydantic BaseSettings *(app/config.py with comprehensive settings)*
- [x] Configure environment-specific settings (dev/staging/prod) *(Environment variables and .env support)*
- [x] Set up logging configuration *(Structured logging with JSON format for production, file rotation, module-specific loggers)*
- [x] Configure CORS for frontend integration *(CORS middleware configured for multiple origins)*
- [x] Set up API versioning structure *(API v1 router structure implemented)*

---

## 🎉 Phase 0 Summary - COMPLETED (2025-07-15)

**✅ Fully Completed:** 0.1, 0.2, 0.3, 0.4, 0.5  

**Key Achievements:**
- FastAPI backend running on http://localhost:8000
- 15 API endpoints implemented across 6 modules
- Complete project structure with batch processing, testing, deployment
- All dependencies installed and configured
- SQLAlchemy ORM models for all tables implemented
- Alembic migrations created with full schema and indexes
- Docker Compose setup for PostgreSQL development
- Sample data generation and basic test suite
- Ready for Phase 1 implementation

**Next Priority:** Database models and authentication system

---

## Phase 1: Core Backend Implementation (Weeks 2-4)

### 1.0 Logging Infrastructure ✅ COMPLETED (2025-07-15)
- [x] Create centralized logging configuration *(app/core/logging.py with setup_logging())*
- [x] Set up structured logging with JSON formatter for production *(JSON logs in production, human-readable in dev)*
- [x] Configure environment-specific log levels *(LOG_LEVEL setting in config)*
- [x] Set up log rotation and file handlers *(10MB files, 5 backups)*
- [x] Create logger instances for each module *(api, db, auth, batch, market_data loggers)*
- [x] Add logging to existing endpoints *(Root endpoint logging added)*

### 1.1 Authentication System ✅ COMPLETED (2025-07-15)
- [x] Implement JWT token generation and validation *(app/core/auth.py with passlib + jose)*
- [x] Create user registration endpoint (admin-only initially) *(POST /auth/register with auto portfolio creation)*
- [x] Create login endpoint with email/password *(POST /auth/login returning JWT token)*
- [x] Implement token refresh mechanism *(POST /auth/refresh, V1 simple token renewal)*
- [x] Create demo user seeding script *(scripts/seed_demo_users.py with 3 demo users)*
- [x] Add authentication dependencies to protected routes *(app/core/dependencies.py, portfolio endpoints protected)*
- [x] Complete authentication testing: ✅ ALL TESTS PASSING (2025-07-15)
  - [x] Test user registration flow (email validation, password hashing, portfolio creation)
  - [x] Test login flow (valid/invalid credentials, JWT token generation)
  - [x] Test token refresh (expired token handling, new token generation)
  - [x] Test protected route access (with/without token, expired token)
  - [x] Test demo user seeding script execution
  - [x] Verify JWT token expiration and validation
  - [x] Test authentication error handling and logging

### 1.2 Database Models & Seeding ✅ COMPLETED (2025-07-15)
- [x] Implement core SQLAlchemy models *(users, portfolios, positions, tags, market_data, greeks, snapshots, batch_jobs)*
- [x] Implement missing models from DATABASE_DESIGN_ADDENDUM_V1.4.1:
  - [x] modeling_session_snapshots table (for what-if scenarios) *(app/models/modeling.py with JSONB fields)*
  - [x] export_history table (track exports) *(app/models/history.py with type/format constraints)*
  - [x] Update FactorDefinition model to match addendum (add etf_proxy, display_order fields) *(Migration applied)*
  - [x] Update market_data_cache to include sector/industry fields *(Already implemented)*
- [x] Create database seeding scripts:
  - [x] Demo users (demo_growth, demo_value, demo_balanced) *(scripts/seed_demo_users.py ready)*
  - [ ] Sample portfolios with strategy characteristics *(Deferred to section 1.5)*
  - [ ] Historical positions (90 days) *(Deferred to section 1.5)*
  - [ ] Pre-calculated risk metrics *(Deferred to section 1.5)*
  - [ ] Sample tags and strategies *(Deferred to section 1.5)*
  - [x] Load 8 fixed factors into factors table *(app/db/seed_factors.py - all 8 factors seeded with ETF proxies)*
- [x] Create Pydantic schemas for all models *(app/schemas/ with CRUD pattern for all new models)*
- [ ] Generate historical snapshots (90 days with realistic variations) *(Deferred to section 1.5)*
  - [ ] Use real historical market data from Polygon.io *(Deferred to section 1.5)*
  - [ ] Calculate actual P&L from real price movements *(Deferred to section 1.5)*
  - [ ] Only generate snapshots for actual trading days *(Deferred to section 1.5)*

**Completion Notes:**
- Created ModelingSessionSnapshot, ExportHistory, and HistoricalBackfillProgress models
- Added relationships: User.modeling_sessions
- Implemented full Pydantic schema hierarchy with base classes and CRUD patterns
- Successfully seeded all 8 factors with ETF proxies and display order
- Applied migrations for new tables and FactorDefinition updates
- Created verification script (app/db/verify_schema.py)
- Git commit: 45f1840

### 1.3 Market Data Integration ✅ COMPLETED (2025-07-15)
- [x] Set up Polygon.io client with API key management *(app/services/market_data_service.py with environment-based API key)*
- [x] Implement market data service:
  - [x] Stock price fetching *(fetch_stock_prices() with historical data support)*
  - [x] Options chain data *(fetch_options_chain() with full contract details)*
  - [x] Historical price data (90 days of real market data) *(bulk_fetch_and_cache() with configurable date ranges)*
  - [x] Bulk fetch capability for initial historical backfill *(fetch_missing_historical_data() with intelligent caching)*
  - [x] Rate limiting handling for Polygon.io API *(Built-in delays: 0.1s between requests, 0.2s for YFinance)*
- [x] Set up YFinance integration for GICS data *(fetch_gics_data() for sector/industry classification)*
- [ ] Implement data caching strategy with Redis *(Deferred - using PostgreSQL caching for V1.4)*
- [x] Create batch job for daily market data updates *(app/batch/market_data_sync.py with automated portfolio symbol detection)*

**Completion Notes:**
- **Core Service**: Complete MarketDataService class with Polygon.io RESTClient integration
- **API Endpoints**: Full REST API with authentication (GET prices, current prices, sectors, options; POST refresh)
- **Database Integration**: PostgreSQL caching with upsert operations using market_data_cache table
- **Batch Processing**: Daily sync job for portfolio symbols + factor ETFs (SPY, VTV, VUG, etc.)
- **Testing Framework**: Comprehensive pytest suite, manual testing scripts, API endpoint tests
- **Documentation**: Complete TESTING_GUIDE.md with multiple testing approaches
- **Validation**: Successfully tested with user's Polygon API key - historical data working
- **Dependencies Added**: mibian, statsmodels, empyrical for upcoming calculation engine
- **Production Considerations**: Code review identified areas for improvement (async I/O, rate limiting)
- **Git Commit**: 34372dd - "feat: Complete Section 1.3 - Market Data Integration"

**Known Limitations (V1.4 Scope):**
- Redis caching deferred to Phase 2 (PostgreSQL caching sufficient for V1.4)
- Free-tier Polygon API limits real-time data access (historical data works perfectly)
- Rate limiting optimized for current load (may need adjustment for high-concurrency usage)
- Options chain returns full data (filtering can be added in Phase 2)

**Critical Improvements Completed:**
- [x] Implement proper rate limiting with token bucket pattern ✅ COMPLETED (2025-07-15)
  - Token bucket algorithm with configurable capacity and refill rate
  - Support for multiple Polygon plan tiers (free/starter/developer/advanced)
  - Exponential backoff for 429 errors
  - Integrated into all MarketDataService API calls
- [x] Add pagination handling for Polygon aggregation API ✅ COMPLETED (2025-07-15)
  - Follows next_url in API responses to fetch all pages
  - Successfully tested with 8,748+ options contracts
  - Handles large date ranges properly
- [ ] Create and apply Alembic migration for market_data_cache table (existing DBs lack schema updates)

### 1.4 Core Calculation Engine
*Individual calculation functions designed for both batch processing and future real-time APIs*

**📚 LIBRARY STACK**: 
- **mibian**: Options Greeks (Black-Scholes standard)
- **empyrical**: Risk metrics (Sharpe, VaR, max drawdown) - *Postponed to V1.5*
- **statsmodels**: Factor regression analysis
- **pandas/numpy**: Data manipulation and matrix operations

**🎯 V1.4 APPROACH**: Hybrid real/mock calculations
- Real: Greeks, factor betas (7 factors, 12-month window), portfolio aggregations
- Mock: Fallback values when calculations fail
- Postponed to V1.5: Risk metrics (VaR, Sharpe), Short Interest factor
- Forward-looking: 252-day regression window for better predictive power
- See ANALYTICAL_ARCHITECTURE_V1.4.md and RISK_FACTOR_AND_METRICS_V1.4.md for details

**⚠️ IMPORTANT**: Before implementing any calculation function, review the legacy analytics code in:
- `_docs/requirements/legacy_scripts_for_reference_only/legacy_analytics_for_reference/`
- Key files: `factors_utils.py`, `var_utils.py`, `reporting_plotting_analytics.py`
- Extract business logic and mathematical formulas, but modernize for FastAPI/PostgreSQL
- See `README_legacy.md` for migration guidelines

#### 1.4.1 Market Data Calculations (Database Integrated) ✅ COMPLETED (2025-07-16)
- [x] **`calculate_position_market_value(position, current_price)`**
  - Input: Position object, current market price (Decimal)
  - Output: Dict with market_value, exposure, unrealized_pnl
  - Business Logic: market_value = abs(quantity) × price × multiplier; exposure = quantity × price × multiplier
  - Options: 1 contract = 100 shares multiplier
  - File: `app/calculations/market_data.py`

- [x] **`calculate_daily_pnl(db, position, current_price)`**
  - **Updated Function Signature**: Now takes (db, position, current_price) instead of (position, previous_price, current_price)
  - Input: Database session, Position object, current price (Decimal)
  - Output: Dict with daily_pnl, daily_return, price_change
  - **Database Integration**: Automatically queries market_data_cache for previous trading day price
  - **Fallback Behavior**: Uses position.last_price if no market data found in cache
  - **Robust Price Lookup**: Handles missing historical data gracefully
  - Database: Queries market_data_cache for previous close price with date filtering
  - File: `app/calculations/market_data.py`

- [x] **`fetch_and_cache_prices(db, symbols_list)`**
  - Input: Database session, List of unique symbols from positions
  - Output: Dict mapping symbol to current price (Decimal)
  - Integration: Uses existing MarketDataService.fetch_current_prices()
  - Caching: Updates market_data_cache table for valid prices
  - Fallback: Retrieves cached prices for symbols with fetch failures
  - Dependencies: Polygon.io API via MarketDataService
  - File: `app/calculations/market_data.py`

**Implementation Notes:**
- **Database Integration**: All functions now include database integration for robust price lookups
- **Automated Previous Price Retrieval**: calculate_daily_pnl automatically queries market_data_cache instead of requiring previous_price parameter
- **Fallback Strategy**: Uses position.last_price field when market_data_cache lacks historical data
- **Maintains Legacy Business Logic**: market value always positive, exposure signed
- **Options handling**: 100x multiplier for contract-to-share conversion
- **Error handling**: Graceful fallbacks to cached data when API fails
- **Database Performance**: Uses efficient SQL queries with proper indexing on market_data_cache(symbol, date)

#### 1.4.2 Options Greeks Calculations - V1.4 Hybrid (Depends on 1.4.1) ✅ COMPLETED (2025-07-16)
- [x] **`calculate_greeks_hybrid(position, market_data)`**
  - Input: Position object, current market data
  - Output: Position-level Greeks (delta, gamma, theta, vega, rho)
  - **Implementation**: Uses `mibian` library for real calculations, fallback to mock values
  - File: `app/calculations/greeks.py`

- [x] **`calculate_real_greeks(option_params)`**
  - Input: Strike, expiry, underlying_price, volatility, risk_free_rate
  - Output: Real Greeks using `mibian` Black-Scholes model
  - **Implementation**: Switched from `py_vollib` to `mibian` due to compatibility issues
  - File: `app/calculations/greeks.py`

- [x] **`get_mock_greeks_fallback(position_type, quantity)`**
  - Input: Position type (LC, LP, SC, SP, LONG, SHORT), quantity
  - Output: Scaled mock Greeks values (fallback)
  - **Implementation**: Uses predefined mock values from PRD specification
  - File: `app/calculations/greeks.py`

**📝 Implementation Notes - Section 1.4.2:**

**✅ Successfully Implemented:**
- **Core Functions**: All planned functions implemented and tested
- **Database Integration**: `update_position_greeks()` and `bulk_update_portfolio_greeks()` functions
- **Helper Functions**: Option parameter extraction, time-to-expiry calculations, volatility retrieval
- **Testing**: Comprehensive unit tests (20 passing, 1 skipped) and manual testing script
- **Portfolio Aggregation**: `aggregate_portfolio_greeks()` for portfolio-level summaries

**🔧 Technical Implementation Details:**
- **Primary Library**: `mibian` v0.1.3 for Black-Scholes calculations
- **Fallback Strategy**: Mock values from PRD specification when real calculations fail
- **Stock Positions**: Simple delta (1.0 for long, -1.0 for short), zero other Greeks
- **Expired Options**: All Greeks return 0.0 for expired positions
- **Database Schema**: Uses existing `position_greeks` table with proper relationships
- **Error Handling**: Graceful fallback with comprehensive logging

**⚠️ Library Change Decision:**
- **Original Plan**: Use `py_vollib` as primary library
- **Issue Encountered**: `py_vollib` dependency `py_lets_be_rational` imports `_testcapi` - a private CPython testing module not available in standard Python installations
- **Root Cause**: `from _testcapi import DBL_MIN, DBL_MAX` in `py_lets_be_rational/constants.py`
- **Solution Chosen**: Switch to `mibian` library which provides equivalent Black-Scholes calculations
- **Result**: `mibian` works perfectly with Python 3.11+ and provides same mathematical results

**📊 Test Results:**
- **Unit Tests**: 20/21 tests passing (1 skipped for py_vollib unavailability)
- **Manual Tests**: All scenarios working (real calculations, mock fallbacks, expired options)
- **Performance**: <100ms per position, <5s for 100-position portfolio
- **Coverage**: All position types (LC, SC, LP, SP, LONG, SHORT), edge cases, error scenarios

**🔄 Integration Status:**
- **Market Data**: Integrated with existing `market_data_service` for underlying prices
- **Database**: Uses `position_greeks` table with upsert operations
- **Batch Processing**: Ready for integration into daily batch jobs
- **API Endpoints**: Ready for exposure via REST API

#### 1.4.3 Portfolio Aggregation (Depends on 1.4.1, 1.4.2) ✅ COMPLETED (2025-07-17)
- [x] **`calculate_portfolio_exposures(positions: List[Dict]) -> Dict[str, Any]`**  
  • Input: List of position dicts with pre-calculated `market_value`, `exposure`, `position_type`  
  • Output: Dict with `gross_exposure`, `net_exposure`, `long_exposure`, `short_exposure`, `long_count`, `short_count`, `options_exposure`, `stock_exposure`, `notional`  
  • NO recalculation of market_value or exposure - uses values from Section 1.4.1  
  • Returns zeros with metadata for empty portfolios  
  • File: `app/calculations/portfolio.py`

- [x] **`aggregate_portfolio_greeks(positions: List[Dict]) -> Dict[str, Decimal]`**  
  • Input: List of position dicts with embedded `greeks` dict (None for stocks)  
  • Output: Portfolio-level Greeks dict (`delta`, `gamma`, `theta`, `vega`, `rho`) with metadata  
  • Skips positions with None Greeks (doesn't use mock values)  
  • Sums Greeks with proper sign handling from Section 1.4.2  
  • File: `app/calculations/portfolio.py`

- [x] **`calculate_delta_adjusted_exposure(positions: List[Dict]) -> Dict[str, Decimal]`**  
  • Input: Positions with `exposure` and `greeks` (or None for stocks)  
  • Stocks: delta = 1.0 (long) or -1.0 (short)  
  • Output: Dict with both `raw_exposure` and `delta_adjusted_exposure`  
  • Skips positions with None Greeks for options  
  • File: `app/calculations/portfolio.py`

- [x] **`aggregate_by_tags(positions: List[Dict], tag_filter: Optional[Union[str, List[str]]] = None, tag_mode: str = "any") -> Dict[str, Dict]`**  
  • Single flexible function for tag-based aggregation  
  • tag_mode: "any" (OR logic) or "all" (AND logic)  
  • Positions with multiple tags count fully in each tag  
  • Used for sector-like grouping (e.g., "tech", "financials" tags)  
  • File: `app/calculations/portfolio.py`

- [x] **`aggregate_by_underlying(positions: List[Dict]) -> Dict[str, Dict]`** *(critical for options)*  
  • Groups all positions (stocks + options) by underlying symbol  
  • Essential for options risk analysis (e.g., all SPY exposure)  
  • Uses `underlying_symbol` field for options, `symbol` for stocks  
  • File: `app/calculations/portfolio.py`

**📝 Implementation Notes - Section 1.4.3:**

**✅ Successfully Implemented:**
- **Core Functions**: All 5 planned functions implemented and fully tested
- **Constants Module**: `app/constants/portfolio.py` with precision, cache, and performance settings
- **Advanced Caching**: Custom `timed_lru_cache` decorator with 60-second TTL (functools.lru_cache doesn't support TTL natively)
- **Comprehensive Testing**: 29 unit tests covering all scenarios, edge cases, and performance requirements
- **Manual Testing**: `scripts/test_portfolio_aggregation.py` with realistic portfolio demonstrations

**🔧 Technical Implementation Details:**
- **Performance**: Pandas-optimized vectorized operations, <1 second for 10,000 positions ✅
- **Precision**: Decimal throughout calculations, 2 decimal places for monetary, 4 for Greeks ✅
- **Error Handling**: Graceful handling of missing data, None values, malformed inputs ✅
- **Metadata**: Rich metadata with timestamps, warnings, position counts, exclusions ✅
- **Robustness**: Automatic market_value derivation, string-to-Decimal conversion ✅

**⚠️ Implementation Enhancements vs Requirements:**
- **Enhanced Error Handling**: Missing `market_value` fields auto-derived from `exposure`
- **Custom Cache Implementation**: `timed_lru_cache` decorator for TTL support
- **Comprehensive Metadata**: Detailed calculation tracking and debugging information
- **String Conversion**: Automatic string-to-Decimal conversion for API robustness
- **Underlying Symbol Logic**: Robust fallback handling for missing symbols

**📊 Test Results:**
- **Unit Tests**: 29/29 passing ✅
- **Performance**: <1 second for 10,000 positions ✅
- **Edge Cases**: Empty portfolios, missing data, malformed inputs ✅
- **Cache Behavior**: TTL expiration, cache clearing utilities ✅
- **Manual Testing**: Realistic portfolio scenarios with 8 mixed positions ✅

**🔄 Integration Status:**
- **Constants**: Ready for use across application
- **Database**: Functions accept pre-loaded data (no database queries)
- **API Layer**: Ready for REST endpoint integration (converts Decimal to float)
- **Batch Processing**: Ready for nightly aggregation jobs
- **Caching**: 60-second TTL with manual cache clearing utilities

**🚀 Ready for Next Steps:**
- Section 1.4.4: Risk Factor Analysis (depends on 1.4.3) ✅
- Section 1.6: Batch Processing Framework (can use 1.4.3 functions) ✅
- Section 1.7: Portfolio Management APIs (can expose 1.4.3 functions) ✅

**Git Commit**: Portfolio Aggregation implementation complete with 29 passing tests

**Future Enhancements (Documented in Code):**
- Historical analysis with `as_of_date` parameter
- Sector/industry aggregation (currently use tags)
- Real-time aggregation updates (currently batch-first approach)

#### 1.4.4 Risk Factor Analysis - V1.4 Implementation (Depends on 1.4.2)

**Prerequisites - Database Schema & Historical Data:**
- [ ] **Create `position_factor_exposures` table**
  - Add new table: position_id, factor_id, calculation_date, exposure_value, created_at, updated_at
  - Add foreign keys: position_id → positions.id, factor_id → factor_definitions.id
  - Add indexes: (position_id, factor_id), (calculation_date), unique constraint on (position_id, factor_id, calculation_date)
  - Create Alembic migration

- [ ] **Fix Pydantic schema mismatch**
  - Keep existing `FactorExposureCreate` with portfolio_id for portfolio-level storage
  - Create new `PositionFactorExposureCreate` with position_id for position-level storage
  - Update schemas in `app/schemas/factors.py`
  - Update imports in `app/schemas/__init__.py`

- [ ] **Create database models**
  - Add `PositionFactorExposure` model in `app/models/market_data.py`
  - Add relationships: Position.factor_exposures, FactorDefinition.position_exposures
  - Update `app/models/__init__.py` exports

- [ ] **Update `calculate_daily_pnl()` in Section 1.4.1** 
  - **MODIFY EXISTING FUNCTION** to support 252-day historical price lookups for factor analysis
  - Add new parameter `lookback_days` with default 252 for factor calculations
  - Maintain backward compatibility for existing daily P&L calculations
  - Ensure market_data_cache has sufficient historical data (12+ months)
  - Run data backfill using existing `fetch_missing_historical_data()` if needed

- [ ] **Verify market_data_cache historical depth**
  - Check if existing portfolios have 252 trading days of price history
  - Check if factor ETFs (SPY, VTV, VUG, MTUM, QUAL, SIZE, USMV) have 12+ months of data
  - Run backfill job if needed to populate missing historical data
  - Update market data sync job to maintain 12+ month rolling window
  - Create database query to validate minimum data requirements before factor calculations

**Core Factor Analysis Functions:**
- [ ] **`calculate_factor_betas_hybrid(portfolio_id, calculation_date, use_delta_adjusted=False)`**
  - Input: Portfolio ID, calculation date, and exposure type option
  - Output: 7-factor betas via statsmodels OLS regression
  - Process: Internally calls position/factor return functions, performs regression
  - Implementation: 252-day (12-month) window, 60-day minimum, beta cap at ±3
  - Exposure options: Dollar exposure (default) or delta-adjusted exposure
  - Note: Short Interest factor postponed to V1.5
  - File: `app/calculations/factors.py`

- [ ] **`fetch_factor_returns(symbols, start_date, end_date)`**
  - Input: Factor ETF symbols (SPY, VTV, VUG, MTUM, QUAL, SIZE, USMV), date range
  - Output: DataFrame with daily factor returns calculated from ETF prices
  - Implementation: On-demand calculation from Polygon adjusted close prices
  - File: `app/calculations/factors.py`

- [ ] **`calculate_position_returns(portfolio_id, start_date, end_date, use_delta_adjusted=False)`**
  - Input: Portfolio ID, date range, and exposure type option
  - Output: DataFrame with exposure-based daily returns for each position
  - Implementation: Configurable exposure type for options:
    - Dollar exposure (default): quantity × price × multiplier
    - Delta-adjusted exposure: dollar_exposure × delta
  - Process: Accounts for position size changes and corporate actions
  - Dependencies: Greeks calculation (if delta-adjusted)
  - File: `app/calculations/factors.py`

- [ ] **`store_position_factor_exposures(position_betas, calculation_date)`**
  - Input: Position-level betas dictionary, calculation date
  - Output: Store individual position factor exposures in database
  - Implementation: Store results in `position_factor_exposures` table
  - Process: One record per position per factor per date
  - File: `app/calculations/factors.py`

- [ ] **`aggregate_portfolio_factor_exposures(position_betas, portfolio_exposures)`**
  - Input: Position-level betas and current portfolio exposures
  - Output: Portfolio-level factor exposures (exposure-weighted average)
  - Implementation: Store results in `factor_exposures` table (portfolio-level)
  - Process: Aggregate from position-level betas, weighted by exposure
  - File: `app/calculations/factors.py`

- [ ] **Create factor configuration constants**
  - Create: `app/constants/factors.py`
  - Constants: REGRESSION_WINDOW_DAYS=252, MIN_REGRESSION_DAYS=60, BETA_CAP_LIMIT=3.0, POSITION_CHUNK_SIZE=1000
  - Environment variables: FACTOR_CACHE_TTL, FACTOR_CALCULATION_TIMEOUT, FACTOR_USE_DELTA_ADJUSTED
  - Integration: Use in all factor calculation functions

#### 1.4.5 Market Risk Scenarios (Depends on 1.4.4)
*Calculate portfolio responses to market and interest rate movements*

**Prerequisites:**
- Portfolio-level factor exposures from Section 1.4.4
- Portfolio beta calculations (market factor exposure)
- Historical market data for beta calculations

**Core Market Risk Functions:**
- [ ] **`calculate_portfolio_market_beta(portfolio_id, calculation_date)`**
  - Input: Portfolio ID, calculation date
  - Output: Portfolio market beta (from factor exposure to SPY)
  - Process: Extract market factor beta from factor exposures
  - Implementation: Use existing factor calculation results
  - File: `app/calculations/market_risk.py`

- [ ] **`calculate_market_scenarios(portfolio_id, market_moves=[0.01, -0.01])`**
  - Input: Portfolio ID, market moves (default: +1%, -1%)
  - Output: Portfolio P&L response to market scenarios
  - Process: Apply portfolio_beta × market_move to current portfolio value
  - Implementation: scenario_pnl = portfolio_value × portfolio_beta × market_move
  - Dependencies: Portfolio beta, current portfolio value
  - File: `app/calculations/market_risk.py`

- [ ] **`calculate_position_interest_rate_betas(portfolio_id, start_date, end_date)`**
  - Input: Portfolio ID, historical date range (252 days)
  - Output: Interest rate beta per position using 10-year Treasury yield
  - Process: Regress position returns vs 10-year Treasury yield changes
  - Implementation: Use statsmodels OLS, fetch Treasury data from FRED API
  - Dependencies: Position returns, Treasury yield historical data
  - File: `app/calculations/market_risk.py`

- [ ] **`calculate_interest_rate_scenarios(portfolio_id, rate_moves=[0.005, -0.005])`**
  - Input: Portfolio ID, rate moves (default: +50bp, -50bp)
  - Output: Portfolio P&L response to interest rate scenarios
  - Process: Apply position_ir_beta × rate_move for each position, aggregate
  - Implementation: scenario_pnl = sum(position_value × ir_beta × rate_move)
  - Dependencies: Position-level interest rate betas, current position values
  - File: `app/calculations/market_risk.py`

- [ ] **`backtest_scenario_accuracy(portfolio_id, days_back=90)`**
  - Input: Portfolio ID, historical period for testing
  - Output: Accuracy metrics for scenario predictions vs actual performance
  - Process: Compare predicted vs actual portfolio responses to market moves
  - Implementation: Calculate RMSE, correlation between predicted and actual returns
  - Purpose: Backend optimization to test and adjust scenario accuracy
  - File: `app/calculations/market_risk.py`

**Database Storage:**
- [ ] **Create `market_risk_scenarios` table**
  - Fields: portfolio_id, scenario_type, scenario_value, predicted_pnl, calculation_date
  - Scenarios: 'market_up_1pct', 'market_down_1pct', 'rates_up_50bp', 'rates_down_50bp'
  
- [ ] **Create `position_interest_rate_betas` table**
  - Fields: position_id, ir_beta, calculation_date, r_squared, created_at
  - Store position-level interest rate sensitivities

**API Integration:**
- [ ] **GET /api/v1/risk/scenarios/market** - Market scenario results
- [ ] **GET /api/v1/risk/scenarios/rates** - Interest rate scenario results
- [ ] **POST /api/v1/risk/scenarios/calculate** - Trigger scenario calculations
- [ ] **GET /api/v1/risk/scenarios/accuracy** - Backtest accuracy metrics

**Batch Job Integration:**
- [ ] **Add to Batch Job 3: Market Risk Scenarios (5:20 PM weekdays)**
  - Call `calculate_market_scenarios()` for each portfolio
  - Call `calculate_interest_rate_scenarios()` for each portfolio
  - Store results in `market_risk_scenarios` table
  - Run weekly: `backtest_scenario_accuracy()` for accuracy monitoring
  - 5-minute timeout

#### 1.4.6 Snapshot Generation (Depends on 1.4.1-1.4.4)
- [ ] **`create_portfolio_snapshot(portfolio_id, calculation_date)`**
  - Input: Portfolio ID, date
  - Output: Complete portfolio snapshot record
  - Dependencies: Market data, Greeks, portfolio aggregations, factor exposures
  - Note: Risk metrics (VaR, Sharpe, etc.) postponed to V1.5
  - File: `app/calculations/snapshots.py`

- [ ] **`generate_historical_snapshots(portfolio_id, days_back=90)`**
  - Input: Portfolio ID, number of historical days
  - Output: Historical snapshot records with realistic variations
  - File: `app/calculations/snapshots.py`

#### 1.4.7 Comprehensive Stress Testing Framework (Optional - Can be Postponed)
*Advanced stress testing with 10+ predefined scenarios and factor correlation modeling*

**Prerequisites:**
- Section 1.4.4 (Factor Analysis) completed
- Factor correlation matrix calculations
- Historical crisis event data

**Core Stress Testing Infrastructure:**
- [ ] **Create `stress_scenarios.json` configuration system**
  - External scenario definitions (not hardcoded)
  - Support for single-factor and multi-factor shocks
  - Scenario metadata: name, shock_amount, shocked_variable, factor_mapping
  - Historical crisis replay configurations
  - File: `app/config/stress_scenarios.json`

- [ ] **`calculate_factor_correlation_matrix(lookback_days=252)`**
  - Input: Historical factor returns, lookback period
  - Output: Factor cross-correlation matrix with exponential decay weighting
  - Implementation: 94% decay factor for historical data weighting
  - Dependencies: Factor return history from Section 1.4.4
  - File: `app/calculations/stress_testing.py`

- [ ] **`load_stress_scenarios(config_path="stress_scenarios.json")`**
  - Input: JSON configuration file path
  - Output: Parsed stress scenario definitions
  - Validation: Ensure all referenced factors exist in factor model
  - File: `app/calculations/stress_testing.py`

**Two-Tier Stress Testing Engine:**
- [ ] **`calculate_direct_stress_impact(portfolio_id, scenario_config)`**
  - Input: Portfolio ID, single scenario configuration
  - Output: Direct impact without factor correlations
  - Formula: `direct_pnl = 100 × shock_amount × factor_exposure`
  - Implementation: Apply shock directly to specific factor exposure
  - File: `app/calculations/stress_testing.py`

- [ ] **`calculate_correlated_stress_impact(portfolio_id, scenario_config, correlation_matrix)`**
  - Input: Portfolio ID, scenario, factor correlation matrix
  - Output: Total impact including cross-factor correlations
  - Formula: `correlated_pnl = factor_exposure × shock_amount × factor_betas × 100`
  - Implementation: Account for factor correlations and cascading effects
  - File: `app/calculations/stress_testing.py`

- [ ] **`run_comprehensive_stress_test(portfolio_id, scenario_list=None)`**
  - Input: Portfolio ID, optional scenario filter
  - Output: Complete stress test results for all scenarios
  - Process: Run both direct and correlated calculations for each scenario
  - Implementation: Aggregate results by scenario type and severity
  - File: `app/calculations/stress_testing.py`

**Predefined Stress Scenarios (Legacy-Compatible):**

**Market Risk Scenarios:**
- [ ] **Market Up/Down 10%** - SPY factor shock (±0.10)
- [ ] **Market Crash 35%** - Severe market decline (-0.35, COVID-like)
- [ ] **Market Rally 25%** - Strong bull market scenario (+0.25)

**Interest Rate Scenarios:**
- [ ] **Rates Up/Down 25bp** - Treasury yield shock (±0.0025)
- [ ] **Rates Up/Down 100bp** - Aggressive Fed policy shock (±0.01)
- [ ] **Rate Spike 300bp** - Volcker-style shock (+0.03)

**Commodity & Sector Scenarios:**
- [ ] **Oil Up/Down 5%** - WTI crude price shock, energy sector impact (±0.05)
- [ ] **Oil Crash 65%** - Supply disruption scenario (-0.65, COVID-like)
- [ ] **Gold Rally 20%** - Safe haven flight scenario (+0.20)

**International Market Scenarios:**
- [ ] **Europe (DAX) Up/Down 10%** - European market shock (±0.10)
- [ ] **Emerging Markets Crash 25%** - EM currency/equity crisis (-0.25)
- [ ] **China Slowdown 15%** - Chinese growth concerns (-0.15)

**Factor-Specific Scenarios:**
- [ ] **Value Rotation 20%** - Value vs Growth factor shock (+0.20 value, -0.10 growth)
- [ ] **Growth Rally 15%** - Tech/growth momentum (+0.15 growth factor)
- [ ] **Small Cap Outperformance 10%** - Size factor shock (+0.10)
- [ ] **Quality Flight 12%** - Flight to quality scenario (+0.12 quality factor)

**Volatility & Risk-Off Scenarios:**
- [ ] **VIX Spike 150%** - Fear index explosion (+1.5 VIX factor)
- [ ] **Credit Spread Widening 600bp** - Credit crunch scenario (+0.06)
- [ ] **Liquidity Crisis** - Multi-factor risk-off scenario

**Historical Crisis Replay Scenarios:**
- [ ] **2008 Financial Crisis Replay**
  - Multi-factor simultaneous shocks:
  - Market: -45%, Credit: +600bp, Volatility: +150%, Value: -30%
  
- [ ] **COVID-19 Crash Replay (March 2020)**
  - Multi-factor simultaneous shocks:
  - Market: -35%, Oil: -65%, Travel: -70%, Tech: +15%

- [ ] **Dot-Com Crash Replay (2000-2002)**
  - Multi-factor simultaneous shocks:
  - Growth: -60%, Tech: -80%, Market: -45%, Value: +20%

**Database Storage:**
- [ ] **Create `stress_test_scenarios` table**
  - Fields: scenario_id, name, description, shock_config (JSONB), active, created_at
  - Store scenario definitions and configurations

- [ ] **Create `stress_test_results` table**
  - Fields: portfolio_id, scenario_id, direct_pnl, correlated_pnl, total_pnl, calculation_date
  - Store historical stress test results for tracking

- [ ] **Create `factor_correlations` table**
  - Fields: factor_1, factor_2, correlation, calculation_date, lookback_days
  - Store factor correlation matrix results

**API Integration:**
- [ ] **GET /api/v1/stress/scenarios** - List available stress scenarios
- [ ] **POST /api/v1/stress/test/{portfolio_id}** - Run stress test for portfolio
- [ ] **GET /api/v1/stress/results/{portfolio_id}** - Get historical stress test results
- [ ] **GET /api/v1/stress/correlations** - Get factor correlation matrix
- [ ] **POST /api/v1/stress/scenarios** - Create custom stress scenario
- [ ] **GET /api/v1/stress/historical/{crisis_type}** - Get historical crisis scenarios

**Batch Job Integration:**
- [ ] **Add to Batch Job 4: Stress Testing (5:35 PM weekdays)**
  - Calculate factor correlation matrix (weekly)
  - Run comprehensive stress tests for all portfolios (daily)
  - Store results in stress_test_results table
  - Generate stress test reports and alerts
  - 10-minute timeout

**Advanced Features:**
- [ ] **Monte Carlo Stress Testing** - Random scenario generation
- [ ] **Custom Scenario Builder** - User-defined stress scenarios
- [ ] **Stress Test Alerts** - Threshold-based risk alerts
- [ ] **Historical Backtesting** - Validate stress predictions against actual events
- [ ] **Stress Test Reports** - PDF/Excel export of comprehensive results

**Note:** This entire section can be postponed to V1.5+ if needed to reduce scope. The basic market risk scenarios in Section 1.4.5 provide essential functionality, while this section adds enterprise-grade stress testing capabilities.

### 1.5 Demo Data Seeding
*Create comprehensive demo data for testing and demonstration*

- [ ] Create sample portfolio data:
  - [ ] Sample portfolios with strategy characteristics (from Ben Mock Portfolios.md)
  - [ ] Historical positions (90 days) with realistic variations
  - [ ] Pre-calculated factor exposures for demo purposes
  - [ ] Sample tags and strategies for each portfolio

- [ ] Generate historical snapshots:
  - [ ] Use real historical market data from Polygon.io
  - [ ] Calculate actual P&L from real price movements
  - [ ] Only generate snapshots for actual trading days
  - [ ] 90 days of portfolio history with realistic variations

- [ ] Implement demo data seeding scripts:
  - [ ] `app/db/seed_demo_portfolios.py` - Create 3 demo portfolios
  - [ ] `app/db/seed_historical_data.py` - Fetch and store 90 days of market data
  - [ ] `app/db/seed_portfolio_snapshots.py` - Generate historical snapshots
  - [ ] `app/db/seed_factor_exposures.py` - Pre-calculate factor exposures for demos

### 1.6 Batch Processing Framework
*Orchestrates calculation functions for automated daily processing*

- [ ] Create batch job framework:
  - [x] Implement `batch_jobs` table for job tracking *(Table created in initial migration)*
  - [x] Create `batch_job_schedules` table for cron management *(Table created in initial migration)*
  - [ ] Build job runner service using APScheduler (runs within FastAPI app)
  - [ ] Configure APScheduler with PostgreSQL job store for persistence

- [ ] **Batch Job 1: `update_market_data()` (4:00 PM weekdays)**
  - [ ] Call `fetch_and_cache_prices()` for all portfolio symbols + factor ETFs
  - [ ] Call `calculate_position_market_value()` for all positions
  - [ ] Call `calculate_daily_pnl()` for all positions
  - [ ] Update market_data_cache and positions tables
  - [ ] Maintain 12+ month rolling window for factor calculations
  - [ ] 5-minute timeout

- [ ] **Batch Job 2: `calculate_portfolio_greeks()` (5:00 PM weekdays)**
  - [ ] Call `calculate_greeks_hybrid()` for all positions
  - [ ] Call `aggregate_portfolio_greeks()` for each portfolio
  - [ ] Store results in position_greeks table
  - [ ] 10-minute timeout

- [ ] **Batch Job 3: `calculate_factor_exposures()` (5:15 PM weekdays)**
  - [ ] Call `calculate_factor_betas_hybrid()` for each portfolio
  - [ ] Call `store_position_factor_exposures()` to store position-level data
  - [ ] Call `aggregate_portfolio_factor_exposures()` to store portfolio-level data
  - [ ] Store results in both `position_factor_exposures` and `factor_exposures` tables
  - [ ] 15-minute timeout
  - [ ] Process large portfolios in 1000-position chunks

- [ ] **Batch Job 4: `create_portfolio_snapshots()` (5:30 PM weekdays)**
  - [ ] Call `create_portfolio_snapshot()` for each portfolio
  - [ ] Aggregate all calculated metrics (no VaR/risk metrics in V1.4)
  - [ ] Store in portfolio_snapshots table
  - [ ] Implement 365-day retention policy

- [ ] Add manual trigger endpoints:
  - [ ] POST /api/v1/admin/batch/market-data
  - [ ] POST /api/v1/admin/batch/risk-metrics
  - [ ] POST /api/v1/admin/batch/snapshots

- [ ] Add job monitoring and error handling

### 1.7 Portfolio Management APIs
- [ ] **GET /api/v1/portfolio** - Portfolio summary with exposures
- [ ] **GET /api/v1/portfolio/exposures** - Time-series exposure data
- [ ] **GET /api/v1/portfolio/performance** - P&L and performance metrics
- [ ] **POST /api/v1/portfolio/upload** - CSV upload endpoint
- [ ] Implement CSV parsing based on SAMPLE_CSV_FORMAT.md
- [ ] Add position type detection logic
- [ ] Implement exposure calculations (notional & delta-adjusted)

### 1.8 Position Management APIs
- [ ] **GET /api/v1/positions** - List positions with filtering
- [ ] **GET /api/v1/positions/grouped** - Grouped positions (by type/strategy)
- [ ] **GET /api/v1/positions/{id}** - Individual position details
- [ ] **PUT /api/v1/positions/{id}/tags** - Update position tags
- [ ] **GET /api/v1/tags** - Tag management
- [ ] **POST /api/v1/tags** - Create new tags
- [ ] **GET /api/v1/strategies** - Strategy groupings
- [ ] Implement position grouping logic

### 1.9 Risk Analytics APIs
- [ ] Implement simplified Black-Scholes calculator
- [ ] **GET /api/v1/risk/greeks** - Portfolio Greeks summary
- [ ] **POST /api/v1/risk/greeks/calculate** - Calculate Greeks on-demand
- [ ] **GET /api/v1/risk/factors** - Factor exposures (mock initially)
- [ ] **GET /api/v1/risk/metrics** - Risk metrics (POSTPONED TO V1.5)
- [ ] Create Greeks aggregation logic
- [ ] Implement delta-adjusted exposure calculations

### 1.10 Factor Analysis APIs
- [ ] **GET /api/v1/factors/definitions** - List factor definitions
- [ ] **GET /api/v1/factors/exposures** - Portfolio factor exposures
- [ ] **GET /api/v1/factors/correlation** - Factor correlation matrix
- [ ] Implement factor exposure calculations

### 1.11 Tag Management APIs
- [ ] **GET /api/v1/tags** - List all tags
- [ ] **POST /api/v1/tags** - Create new tag
- [ ] **PUT /api/v1/positions/{id}/tags** - Update position tags
- [ ] **DELETE /api/v1/tags/{id}** - Delete tag
- [ ] Implement tag validation and limits

### 1.12 API Infrastructure  
- [ ] Add user activity logging
- [ ] Create data validation middleware
- [ ] Add rate limiting (100 requests/minute per user)
- [ ] Set up request/response logging

### 1.13 Implementation Priority (from DATABASE_DESIGN_ADDENDUM_V1.4.1)
**Week 1 Priority - Core Tables:**
- Users & Authentication
- Portfolios & Positions (with options parsing)
- Market Data Cache (with sector/industry)
- Tags

**Week 2 Priority - Analytics:**
- Portfolio Snapshots
- Position Greeks
- Factor Definitions (8 fixed factors)
- Risk Metrics

**Week 3 Priority - Operations:**
- Batch Jobs
- Demo Data Generation (3 demo users)
- Historical Snapshots (90 days)

---

## 🎯 Phase 1 Summary

**✅ Completed:** 1.0, 1.1, 1.2, 1.3, 1.4.1, 1.4.2, 1.4.3  
**🔄 In Progress:** None  
**📋 Remaining:** 1.4.4, 1.4.6, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13  
**🚫 Postponed to V1.5:** 1.4.5 (Risk Metrics)

**Key Achievements:**
- **Authentication system** with JWT tokens fully tested ✅
- **All database models** and Pydantic schemas implemented ✅
- **Factor definitions** seeded with ETF proxies ✅
- **New tables** for modeling sessions, export history, and backfill progress ✅
- **Complete market data integration** with Polygon.io and YFinance ✅
- **Database-integrated market data calculations** (section 1.4.1) with improved function signatures ✅
- **Options Greeks calculations** (section 1.4.2) with mibian library and comprehensive testing ✅
- **Portfolio aggregation functions** (section 1.4.3) with 29 passing tests and <1s performance ✅
- **Comprehensive constants module** with precision, cache, and performance settings ✅
- **Advanced caching implementation** with time-based TTL support ✅

**Latest Completion (2025-07-17):**
- **Section 1.4.3 Portfolio Aggregation**: 5 core functions, 29 unit tests, performance optimized
- **Functions implemented**: `calculate_portfolio_exposures`, `aggregate_portfolio_greeks`, `calculate_delta_adjusted_exposure`, `aggregate_by_tags`, `aggregate_by_underlying`
- **Advanced features**: Time-based LRU cache, pandas optimization, comprehensive error handling
- **Test coverage**: Empty portfolios, large datasets (10k positions), edge cases, cache behavior
- **Ready for**: Batch processing integration, API endpoints, real-time calculations

**Next Priority:**
- Section 1.4.4: Risk Factor Analysis - 7-factor model implementation
- Section 1.4.6: Snapshot Generation (without risk metrics)
- Section 1.5: Demo Data Seeding (sample portfolios)
- Section 1.6: Batch Processing Framework with APScheduler

---

## Phase 2: Advanced Features & Frontend Integration (Weeks 5-6)

### 2.1 ProForma Modeling APIs
- [ ] **POST /api/v1/modeling/sessions** - Create modeling session
- [ ] **GET /api/v1/modeling/sessions/{id}** - Get session state
- [ ] **POST /api/v1/modeling/sessions/{id}/trades** - Add ProForma trades
- [ ] **POST /api/v1/modeling/sessions/{id}/calculate** - Calculate impacts
- [ ] **GET /api/v1/modeling/sessions/{id}/impacts** - Get risk impacts
- [ ] **POST /api/v1/modeling/sessions/{id}/save** - Save as snapshot
- [ ] Implement session state management
- [ ] Add trade generation suggestions

### 2.2 Reporting & Export APIs
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

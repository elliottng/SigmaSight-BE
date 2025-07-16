# SigmaSight Backend Implementation TODO

## Project Overview
Build a FastAPI backend for SigmaSight portfolio risk management platform with Railway deployment, PostgreSQL database, Polygon.io/YFinance market data integration, and **V1.4 hybrid real/mock calculation engine**.

### V1.4 Hybrid Calculation Approach
- **Real calculations** for Greeks (py_vollib), factor betas (statsmodels), and risk metrics (empyrical)
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
- [x] py_vollib *(v1.0.1 installed - real Greeks)*
- [ ] mibian *(fallback Greeks calculations)*
- [ ] statsmodels *(factor beta regressions)*
- [ ] empyrical *(risk metrics: Sharpe, VaR, etc.)*

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

### 1.2 Database Models & Seeding
- [x] Implement core SQLAlchemy models *(users, portfolios, positions, tags, market_data, greeks, snapshots, batch_jobs)*
- [ ] Implement missing models from DATABASE_DESIGN_ADDENDUM_V1.4.1:
  - [ ] modeling_session_snapshots table (for what-if scenarios)
  - [ ] export_history table (track exports)
  - [ ] Update FactorDefinition model to match addendum (add etf_proxy, display_order fields)
  - [x] Update market_data_cache to include sector/industry fields *(Already implemented)*
- [ ] Create database seeding scripts:
  - [x] Demo users (demo_growth, demo_value, demo_balanced) *(scripts/seed_demo_users.py ready)*
  - [ ] Sample portfolios with strategy characteristics
  - [ ] Historical positions (90 days)
  - [ ] Pre-calculated risk metrics
  - [ ] Sample tags and strategies
  - [ ] Load 8 fixed factors into factors table
- [ ] Create Pydantic schemas for all models
- [ ] Generate historical snapshots (90 days with realistic variations)

### 1.3 Market Data Integration
- [ ] Set up Polygon.io client with API key management
- [ ] Implement market data service:
  - [ ] Stock price fetching
  - [ ] Options chain data
  - [ ] Historical price data (90 days)
- [ ] Set up YFinance integration for GICS data
- [ ] Implement data caching strategy with Redis
- [ ] Create batch job for daily market data updates

### 1.4 Core Calculation Engine
*Granular calculation functions designed for both batch processing and future real-time APIs*

**📚 LIBRARY STACK**: 
- **py_vollib**: Options Greeks (Black-Scholes standard)
- **empyrical**: Risk metrics (Sharpe, VaR, max drawdown)  
- **statsmodels**: Factor regression analysis
- **pandas/numpy**: Data manipulation and matrix operations

**🎯 V1.4 APPROACH**: Hybrid real/mock calculations
- Real: Greeks, risk metrics, factor betas (7/8), portfolio aggregations
- Mock: Short interest factor, fallback values
- See ANALYTICAL_ARCHITECTURE_V1.4.md for detailed rationale

**⚠️ IMPORTANT**: Before implementing any calculation function, review the legacy analytics code in:
- `_docs/requirements/legacy_scripts_for_reference_only/legacy_analytics_for_reference/`
- Key files: `factors_utils.py`, `var_utils.py`, `reporting_plotting_analytics.py`
- Extract business logic and mathematical formulas, but modernize for FastAPI/PostgreSQL
- See `README_legacy.md` for migration guidelines

#### 1.4.1 Market Data Calculations (No Dependencies)
- [ ] **`calculate_position_market_value(position, current_price)`**
  - Input: Position object, current market price
  - Output: Current market value, unrealized P&L
  - File: `app/calculations/market_data.py`

- [ ] **`calculate_daily_pnl(position, previous_price, current_price)`**
  - Input: Position, previous close, current price
  - Output: Daily P&L (realized + unrealized)
  - File: `app/calculations/market_data.py`

- [ ] **`fetch_and_cache_prices(symbols_list)`**
  - Input: List of unique symbols from positions
  - Output: Updated market_data_cache table
  - Dependencies: Polygon.io API, YFinance for GICS
  - File: `app/calculations/market_data.py`

#### 1.4.2 Options Greeks Calculations - V1.4 Hybrid (Depends on 1.4.1)
- [ ] **`calculate_greeks_hybrid(position, market_data)`**
  - Input: Position object, current market data
  - Output: Position-level Greeks (delta, gamma, theta, vega, rho)
  - Implementation: Try py_vollib first, fallback to mock values
  - File: `app/calculations/greeks.py`

- [ ] **`calculate_real_greeks(option_params)`**
  - Input: Strike, expiry, underlying_price, volatility, risk_free_rate
  - Output: Real Greeks using py_vollib BSM model
  - File: `app/calculations/greeks.py`

- [ ] **`get_mock_greeks_fallback(position_type, quantity)`**
  - Input: Position type (LC, LP, SC, SP, LONG, SHORT), quantity
  - Output: Scaled mock Greeks values (fallback)
  - File: `app/calculations/greeks.py`

#### 1.4.3 Portfolio Aggregation (Depends on 1.4.1, 1.4.2)
- [ ] **`aggregate_portfolio_greeks(positions_greeks)`**
  - Input: List of position Greeks
  - Output: Portfolio-level Greeks summary
  - File: `app/calculations/portfolio.py`

- [ ] **`calculate_portfolio_exposures(positions)`**
  - Input: List of positions with market values
  - Output: Gross exposure, net exposure, long/short breakdown
  - File: `app/calculations/portfolio.py`

- [ ] **`calculate_delta_adjusted_exposure(positions_with_greeks)`**
  - Input: Positions with calculated Greeks
  - Output: Delta-adjusted notional exposure
  - Dependencies: Greeks calculations
  - File: `app/calculations/portfolio.py`

#### 1.4.4 Risk Factor Analysis - V1.4 Hybrid (Depends on 1.4.2)
- [ ] **`calculate_factor_betas_hybrid(position_returns, factor_returns)`**
  - Input: 60-day position returns, factor ETF returns
  - Output: 8-factor betas (7 real via statsmodels, 1 mock for Short Interest)
  - Implementation: Uses legacy `factors_utils.py` logic with statsmodels OLS
  - File: `app/calculations/factors.py`

- [ ] **`calculate_position_betas(factor_returns_df, position_returns_df)`**
  - Input: Factor returns DataFrame, position returns DataFrame
  - Output: Adjusted position-level betas using legacy logic
  - File: `app/calculations/factors.py`

- [ ] **`get_factor_covariance_matrix()`**
  - Input: None (uses static identity matrix for V1.4)
  - Output: 8x8 covariance matrix (np.eye(8) * 0.01)
  - Note: Real correlations deferred to Phase 2
  - File: `app/calculations/factors.py`

#### 1.4.5 Risk Metrics - V1.4 Real Calculations (Depends on 1.4.3, 1.4.4)
- [ ] **`calculate_portfolio_var_hybrid(portfolio_exposures, covariance_matrix)`**
  - Input: Portfolio exposures, factor covariance matrix
  - Output: 1-day VaR (95%, 99% confidence)
  - Implementation: Uses legacy `var_utils.py` matrix multiplication
  - File: `app/calculations/risk_metrics.py`

- [ ] **`calculate_risk_metrics_empyrical(returns_series)`**
  - Input: Historical portfolio returns (pandas Series)
  - Output: Dict with Sharpe ratio, max drawdown, volatility, VaR
  - Implementation: Uses `empyrical` library for all metrics
  - File: `app/calculations/risk_metrics.py`

- [ ] **`multiply_matrices(cov_matrix, exposures, factor_betas)`**
  - Input: Covariance matrix, exposures, factor betas
  - Output: Position exposure for VaR calculation
  - Implementation: Legacy `var_utils.py` logic
  - File: `app/calculations/risk_metrics.py`

#### 1.4.6 Snapshot Generation (Depends on All Above)
- [ ] **`create_portfolio_snapshot(portfolio_id, calculation_date)`**
  - Input: Portfolio ID, date
  - Output: Complete portfolio snapshot record
  - Dependencies: All calculation functions
  - File: `app/calculations/snapshots.py`

- [ ] **`generate_historical_snapshots(portfolio_id, days_back=90)`**
  - Input: Portfolio ID, number of historical days
  - Output: Historical snapshot records with realistic variations
  - File: `app/calculations/snapshots.py`

### 1.5 Batch Processing Framework
*Orchestrates calculation functions for automated daily processing*

- [ ] Create batch job framework:
  - [x] Implement `batch_jobs` table for job tracking *(Table created in initial migration)*
  - [x] Create `batch_job_schedules` table for cron management *(Table created in initial migration)*
  - [ ] Build job runner service (using APScheduler, not Celery for V1.4)

- [ ] **Batch Job 1: `update_market_data()` (4 PM weekdays)**
  - [ ] Call `fetch_and_cache_prices()` for all portfolio symbols
  - [ ] Call `calculate_position_market_value()` for all positions
  - [ ] Call `calculate_daily_pnl()` for all positions
  - [ ] Update market_data_cache and positions tables
  - [ ] 5-minute timeout

- [ ] **Batch Job 2: `calculate_all_risk_metrics()` (5 PM weekdays)**
  - [ ] Call `calculate_position_greeks()` for all positions
  - [ ] Call `calculate_factor_exposures()` for all positions
  - [ ] Call `aggregate_portfolio_greeks()` for each portfolio
  - [ ] Call `calculate_portfolio_exposures()` for each portfolio
  - [ ] Store results in position_greeks and factor_exposures tables
  - [ ] 10-minute timeout

- [ ] **Batch Job 3: `create_portfolio_snapshots()` (5:30 PM weekdays)**
  - [ ] Call `create_portfolio_snapshot()` for each portfolio
  - [ ] Call `calculate_portfolio_var()` and risk metrics
  - [ ] Store in portfolio_snapshots table
  - [ ] Implement 365-day retention policy

- [ ] Add manual trigger endpoints:
  - [ ] POST /api/v1/admin/batch/market-data
  - [ ] POST /api/v1/admin/batch/risk-metrics
  - [ ] POST /api/v1/admin/batch/snapshots

- [ ] Add job monitoring and error handling

### 1.6 Portfolio Management APIs
- [ ] **GET /api/v1/portfolio** - Portfolio summary with exposures
- [ ] **GET /api/v1/portfolio/exposures** - Time-series exposure data
- [ ] **GET /api/v1/portfolio/performance** - P&L and performance metrics
- [ ] **POST /api/v1/portfolio/upload** - CSV upload endpoint
- [ ] Implement CSV parsing based on SAMPLE_CSV_FORMAT.md
- [ ] Add position type detection logic
- [ ] Implement exposure calculations (notional & delta-adjusted)

### 1.7 Position Management APIs
- [ ] **GET /api/v1/positions** - List positions with filtering
- [ ] **GET /api/v1/positions/grouped** - Grouped positions (by type/strategy)
- [ ] **GET /api/v1/positions/{id}** - Individual position details
- [ ] **PUT /api/v1/positions/{id}/tags** - Update position tags
- [ ] **GET /api/v1/tags** - Tag management
- [ ] **POST /api/v1/tags** - Create new tags
- [ ] **GET /api/v1/strategies** - Strategy groupings
- [ ] Implement position grouping logic

### 1.8 Risk Analytics APIs
- [ ] Implement simplified Black-Scholes calculator
- [ ] **GET /api/v1/risk/greeks** - Portfolio Greeks summary
- [ ] **POST /api/v1/risk/greeks/calculate** - Calculate Greeks on-demand
- [ ] **GET /api/v1/risk/factors** - Factor exposures (mock initially)
- [ ] **GET /api/v1/risk/metrics** - Risk metrics (VaR, Sharpe, etc.)
- [ ] Create Greeks aggregation logic
- [ ] Implement delta-adjusted exposure calculations

### 1.9 API Infrastructure  
- [ ] Add user activity logging
- [ ] Create data validation middleware
- [ ] Add rate limiting (100 requests/minute per user)
- [ ] Set up request/response logging

### 1.10 Implementation Priority (from DATABASE_DESIGN_ADDENDUM_V1.4.1)
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

# SigmaSight Backend - Project Requirements Document (PRD) & Engineering Design Document (EDD)

## 1. Executive Summary
SigmaSight is a portfolio risk management platform designed to provide institutional-quality analytics for long/short equity portfolios. This document outlines the backend requirements and technical design for a demonstration system that showcases core functionality through pre-computed analytics and batch processing.

**Key Principles**

- **Batch Processing First**: All computations run before demo to ensure snappy performance
- **PostgreSQL Only**: No distributed storage needed for 90-day demo dataset
- **Railway Deployment**: Zero-config deployment using UV package manager
- **API-First Design**: RESTful API matching the V5 frontend prototype requirements

## 2. Project Scope
### In Scope – Phase 1 (Demo)
- Portfolio data ingestion via CSV upload
- Pre-calculated risk metrics and factor exposures
- Position management with tagging system
- JWT-based authentication for multiple demo accounts
- Daily batch processing of market data
- Mock options Greeks display
- API endpoints for frontend V5 prototype

### In Scope – Phase 2 (Post-Demo)
- Real-time ProForma modeling with session management
- Dynamic Greeks calculation
- Real export functionality (FIX, CSV formats)
- WebSocket support for live updates

### Out of Scope
- Real-time market data feeds
- Actual options pricing models
- Complex authentication/authorization
- Multi-tenant architecture
- Audit logging

## 3. Functional Requirements
### 3.1 Portfolio Management
#### CSV Upload Endpoint
```
POST /api/v1/portfolio/upload
Content-Type: multipart/form-data
```
CSV Format:
```
csvticker,quantity,entry_price,entry_date,tags
AAPL,1000,150.00,2024-01-15,"momentum,tech"
MSFT,-500,380.00,2024-01-20,"hedge,tech"
AAPL240119C00150000,10,5.50,2024-01-10,"hedge,options"
```
Requirements:
- Support stocks (positive quantity = long, negative = short)
- Support options (OCC symbology)
- Multiple tags per position (comma-separated)
- Calculate current market value using latest prices
- Generate 90 days of historical snapshots

#### Portfolio Overview
```
GET /api/v1/portfolio
```
Returns:
- Total portfolio value
- Long/short/gross/net exposures
- Total P&L (daily, MTD, YTD)
- Number of positions by type

### 3.2 Position Management
#### List Positions
```
GET /api/v1/positions?groupBy=type|tag&tags=momentum,hedge&tagMode=any|all
```
Features:
- Filter by position type (LONG, SHORT, LC, LP, SC, SP)
- Filter by tags with AND/OR logic
- Group by type or tag
- Include current market values and P&L

#### Position Greeks (Mock Data)
```
GET /api/v1/risk/greeks?view=portfolio|longs|shorts
```
Mock Greeks by Position Type:

| Type | Delta | Gamma | Theta | Vega |
|------|------|------|------|------|
| Long Call (LC) | 0.6 | 0.02 | -0.5 | 0.3 |
| Short Call (SC) | -0.4 | -0.02 | 0.5 | -0.3 |
| Long Put (LP) | -0.4 | 0.02 | -0.5 | 0.3 |
| Short Put (SP) | 0.3 | -0.02 | 0.5 | -0.3 |

### 3.3 Risk Analytics
#### Factor Exposures
```
GET /api/v1/risk/factors
```
Eight Factors (with ETF proxies):
1. Market Beta (SPY)
2. Momentum (MTUM)
3. Value (VTV)
4. Growth (VUG)
5. Quality (QUAL)
6. Size (IWM)
7. Low Volatility (SPLV)
8. Short Interest (custom calculation)

Calculation Method:
- 60-day rolling window
- Daily returns regression
- Position-level betas aggregated by portfolio weights

#### Risk Metrics
```
GET /api/v1/risk/metrics
```
Pre-calculated Metrics:
- Portfolio Beta (weighted average vs SPY)
- Annualized Volatility (60-day rolling)
- Sharpe Ratio
- Maximum Drawdown (90-day period)
- Value at Risk (95% confidence, 1-day)

### 3.4 Tag Management
CRUD Operations
```
GET    /api/v1/tags
POST   /api/v1/tags          {"name": "momentum", "color": "#FF5733"}
PUT    /api/v1/tags/{id}     {"name": "momentum_v2"}
DELETE /api/v1/tags/{id}

GET    /api/v1/positions/{id}/tags
PUT    /api/v1/positions/{id}/tags   {"tag_ids": [1, 2, 3]}
```

### 3.5 Authentication
#### Login
```
POST /api/v1/auth/login
{
  "username": "demo_user_1",
  "password": "demo123"
}
```
Response:
```
{
  "token": "eyJ...",
  "expires_in": 86400,
  "portfolio_id": 1
}
```
Demo Users (pre-seeded):
- demo_user_1 / demo123 – Main portfolio
- demo_user_2 / demo123 – Secondary portfolio
- demo_admin  / admin123 – Admin access

### 3.6 Batch Processing
#### Daily Update Process
```
POST /api/v1/admin/daily-update
```
Steps:
1. Fetch latest prices from Polygon.io
2. Calculate new market values
3. Generate P&L for the day
4. Recalculate all risk metrics
5. Update factor exposures
6. Create new portfolio snapshot

Scheduling:
- **Automatic**: Daily batch runs at specific times
- **Manual**: Admin endpoint trigger

#### Batch Job Implementation Details

##### 1. Market Data Update Job (4 PM EST)
```python
def update_market_data():
    """
    Fetch and store latest market data for all active securities
    """
    # Steps:
    # 1. Get list of unique symbols from positions
    # 2. Fetch EOD prices from Polygon.io
    # 3. Fetch sector/industry from YFinance for new symbols
    # 4. Update market_data_cache table
    # 5. Update last_price in positions table
    # 6. Calculate market values and P&L
```

##### 2. Risk Metrics Calculation Job (5 PM EST)
```python
def calculate_all_risk_metrics():
    """
    Calculate portfolio-level risk metrics and factor exposures
    """
    # Steps:
    # 1. Calculate position-level Greeks (using mock values)
    # 2. Aggregate portfolio Greeks
    # 3. Calculate factor exposures (using mock values):
    #    - Use MOCK_FACTOR_EXPOSURES dictionary
    #    - Apply to each position based on characteristics
    # 4. Update position_greeks table
    # 5. Update factor_exposures table
    # 6. Calculate portfolio beta and volatility
```

##### 3. Portfolio Snapshot Job (5:30 PM EST)
```python
def create_portfolio_snapshots():
    """
    Create daily snapshots for historical tracking
    """
    # Steps:
    # 1. Calculate daily P&L for each portfolio
    # 2. Calculate portfolio metrics:
    #    - Total value, gross/net exposure
    #    - Aggregated Greeks
    #    - Risk metrics
    # 3. Create portfolio_snapshots record
    # 4. Update portfolio performance metrics
    # 5. Clean up old snapshots (>365 days)
```

##### Batch Job Configuration
```python
BATCH_SCHEDULE = {
    'market_data': {
        'function': update_market_data,
        'schedule': '0 16 * * 1-5',  # 4 PM weekdays
        'timeout': 300,
        'retry_count': 3
    },
    'risk_metrics': {
        'function': calculate_all_risk_metrics,
        'schedule': '0 17 * * 1-5',  # 5 PM weekdays
        'timeout': 600,
        'retry_count': 2
    },
    'snapshots': {
        'function': create_portfolio_snapshots,
        'schedule': '30 17 * * 1-5',  # 5:30 PM weekdays
        'timeout': 300,
        'retry_count': 2
    }
}
```

## 4. Technical Architecture
### 4.1 Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Package Manager**: UV
- **Deployment**: Railway
- **External APIs**: Polygon.io for market data

### 4.2 Project Structure
```
sigmasight-backend/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── portfolio.py
│   │       ├── positions.py
│   │       ├── risk.py
│   │       ├── tags.py
│   │       └── admin.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── portfolio.py
│   │   ├── position.py
│   │   ├── market_data.py
│   │   └── user.py
│   ├── services/
│   │   ├── market_data.py
│   │   ├── risk_calc.py
│   │   ├── factor_calc.py
│   │   └── batch.py
│   ├── schemas/
│   └── main.py
├── scripts/
│   ├── seed_data.py
│   └── daily_batch.py
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

### 4.3 Database Schema
*(See SQL definitions in original document)*

### 4.4 Development Environment Setup
Prerequisites: Python 3.11+, PostgreSQL 15, UV, Git

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
git clone https://github.com/your-org/sigmasight-backend.git
cd sigmasight-backend

# Create env
uv venv && source .venv/bin/activate

# Install deps
uv sync

# Setup DB
createdb sigmasight_dev
cp .env.example .env
# Edit .env

# Migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Run server
uvicorn app.main:app --reload
```

### 4.5 Configuration Management
Environment variables (.env) and UV `pyproject.toml` settings are defined for database, security, external APIs, and batch processing.

## 5. Implementation Phases
1. **Phase 1 – Core Infrastructure (Week 1)**: project setup, auth, CSV upload.
2. **Phase 2 – Data Pipeline (Week 2)**: Polygon integration, batch, risk metrics.
3. **Phase 3 – API Development (Week 3)**: endpoints, mock Greeks, tag CRUD.
4. **Phase 4 – Testing & Deployment (Week 4)**: tests, Railway deploy, performance.
5. **Phase 5 – ProForma Modeling (Post-Demo)**: session management, real-time calcs.

## 6. API Endpoint Summary
*(Detailed list provided earlier; see section 3)*

## 7. Sample Data Specifications
Portfolio: $3M total with 20 longs, 15 shorts, 15 options; 90-day historical return +7.3%.

## 8. Development Guidelines
- **Git workflow**: feature branches, conventional commits.
- **Code standards**: type hints, docstrings, Black, Ruff, 90% test coverage.
- **Migrations**: Alembic revision management.

## 9. Deployment to Railway
CLI steps for initial setup, environment variables, and continuous deployment on `main` branch.

## 10. Testing Strategy
Unit, integration, and end-to-end tests covering services, calculations, and workflows.

## 11. Performance Considerations
Caching, database indexing, response-time targets, and pagination guidelines.

## 12. Security Considerations
JWT auth, bcrypt hashing, HTTPS, rate limiting, and environment-based secrets.

## 13. Future Enhancements
Features planned for Phases 2-4, including websocket updates, ML predictions, and webhooks.

## 14. Success Criteria
Demo requirements, performance metrics, and availability targets.

## 15. AI Agent Implementation Notes
Error handling, validation, logging, and consistent implementation order for building the backend.

## Appendix A: Legacy Script Migration Strategy

### Overview of Migration Approach
The SigmaSight backend will adapt three categories of scripts from the legacy Dockyard system. Rather than using these scripts as-is, we will extract their core calculation logic and data processing patterns while modernizing the architecture for our demo needs. The key principle is to preserve the mathematical and business logic while replacing the infrastructure components (S3, Parquet) with our simpler PostgreSQL-based approach.

### A.1 Data Architecture Scripts Migration Strategy

#### Portfolio Data Ingestion (investment_portfolio_holdings_collection.py)
**Legacy Functionality:**

- Reads daily Excel files from Paragon system
- Processes multiple years of historical holdings
- Standardizes column names and data types
- Uploads to S3 in Parquet format
- Handles various Excel format variations

**Migration Strategy:**
The AI agent should extract the core data transformation logic while replacing the Excel/S3 infrastructure:

- Replace Excel parsing with CSV ingestion - The column standardization logic (exposure(v) → exposure, pl(v) → pnl) should be preserved but applied to CSV inputs
- Preserve position type determination - The logic for determining long/short based on quantity sign should be maintained
- Adapt the exposure percentage calculations - The fund-level calculations for exposure% should be reimplemented
- Replace S3 uploads with direct database writes - Instead of creating Parquet files, write directly to PostgreSQL tables
- Generate historical snapshots programmatically - Rather than processing years of files, create 90 days of synthetic historical data based on the uploaded positions

**Key Business Logic to Preserve:**

- Position exposure as percentage of total portfolio
- Long/short classification based on quantity
- P&L field mappings and standardization
- Portfolio aggregation calculations

#### Market Data Collection (polygon_collection.py)
**Legacy Functionality:**

- Fetches daily OHLCV data from Polygon.io
- Handles multiple timeframes (minute/daily)
- Manages API rate limits and retries
- Stores data in S3/Parquet format

**Migration Strategy:**
The AI agent should maintain the Polygon API integration while simplifying the storage:

- Keep the same API endpoints and parameters - The Polygon API calls should remain identical
- Remove minute-level data handling - Focus only on daily data for the demo
- Replace S3 storage with PostgreSQL - Write market data directly to the database
- Enhance error handling - Add better logging and retry logic
- Add batch update capabilities - Support both historical backfill and daily updates

**Key Integration Points:**

- Preserve the exact Polygon API request format
- Maintain the data field mappings (o→open, h→high, etc.)
- Keep the same date handling logic
- Add support for both stocks and ETFs (for factor calculations)

#### Security Enrichment (yfinance_gics_industry_sector.py)
**Legacy Functionality:**

- Fetches GICS sector/industry classification
- Enriches securities with metadata
- Runs as a separate batch process

**Migration Strategy:**
The AI agent should integrate this into the security creation workflow:

- Make enrichment synchronous - Call during security creation rather than as a batch
- Add option parsing logic - Extend to handle OCC option symbols
- Cache enrichment data - Avoid repeated API calls for the same security
- Handle failures gracefully - Don't block position creation if enrichment fails

### A.2 Calculation Engine Migration Strategy

#### Risk and Analytics Engine (reporting_plotting_analytics.py)
This is the most complex script with multiple calculation types. The AI agent should break it into focused services:

##### Factor Exposure Calculations
**Legacy Functionality:**

- Calculates position-level betas to factor ETFs
- Uses 60-day rolling regression
- Aggregates to portfolio level using position weights
- Creates factor covariance matrix

**Migration Strategy:**

- Extract the beta calculation methodology - The covariance/variance approach should be preserved exactly
- Maintain the same factor definitions - Use the same ETF proxies (SPY, VTV, VUG, etc.)
- Preserve the regression window - Keep the 60-day lookback period
- Store results in database - Pre-calculate and store rather than computing on-demand
- Add the 8th factor - Implement custom logic for "Short Interest" factor

**Mathematical Preservations:**

- Beta = Covariance(asset, factor) / Variance(factor)
- Portfolio exposure = Σ(position_weight × position_beta)
- Minimum 20 observations for valid regression
- Handle missing data appropriately

##### Portfolio Risk Metrics
**Legacy Functionality:**

- Calculates portfolio volatility
- Computes Sharpe ratios
- Tracks maximum drawdown
- Generates VaR estimates

**Migration Strategy:**

- Extract return calculation logic - Preserve the exact method for calculating daily returns
- Maintain volatility calculations - Use the same annualization factor (√252)
- Preserve drawdown methodology - Keep the peak-to-trough calculation
- Simplify VaR calculation - Use parametric approach for demo

##### Performance Attribution
**Legacy Functionality:**

- Calculates position-level P&L
- Aggregates by various groupings
- Handles currency and basis adjustments

**Migration Strategy:**

- Simplify to price-based P&L - Remove complex currency handling
- Preserve aggregation logic - Keep grouping by sector/strategy
- Store daily snapshots - Pre-calculate for performance

### A.3 Implementation Guidelines for AI Agent

#### Code Organization Principles

- Service Layer Architecture - Each calculation type should be its own service class
- Preserve Core Logic - Mathematical calculations must match exactly
- Modernize Infrastructure - Replace S3/Parquet with PostgreSQL, replace synchronous with async
- Add Type Safety - Use type hints and Pydantic models throughout
- Improve Error Handling - Add comprehensive logging and error recovery

#### Data Flow Architecture

**Batch Processing Pipeline:**

- CSV Upload → Security Enrichment → Position Creation → Historical Generation
- Market Data Fetch → Price Storage → Return Calculation → Risk Metrics
- Factor Data → Beta Calculation → Exposure Aggregation → Storage

**Calculation Dependencies:**

- Returns depend on prices
- Betas depend on returns
- Exposures depend on betas and weights
- Risk metrics depend on returns and exposures

#### Testing Strategy

- Unit Tests for Calculations - Verify mathematical accuracy against known results
- Integration Tests for Data Flow - Ensure pipeline processes correctly
- Regression Tests - Compare results with legacy system outputs where possible

#### Performance Optimizations

- Vectorized Calculations - Use pandas/numpy operations rather than loops
- Bulk Database Operations - Insert many records at once
- Parallel Processing - Calculate betas for multiple securities concurrently
- Caching Strategy - Store immutable calculations permanently

#### Key Differences from Legacy

- No S3/Parquet - All data in PostgreSQL
- No Real-time Updates - Batch processing only
- Simplified Portfolio Structure - Single portfolio per user
- Mock Greeks - No complex option pricing
- Pre-calculated Metrics - Compute during batch, serve from database

The AI agent should focus on extracting the business logic and calculations while building a modern, maintainable architecture suitable for the demo requirements.

---

*This PRD/EDD provides a comprehensive blueprint for building the SigmaSight backend demonstration system.*

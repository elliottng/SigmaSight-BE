# DATABASE_DESIGN_ADDENDUM.md

## Overview
This addendum resolves all 15 unresolved questions identified by the coding agent and provides complete database schemas, implementation details, and deployment configuration for SigmaSight V1.

## 1. Complete Database Schema

### 1.1 Users & Authentication Tables

```sql
-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_demo BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL  -- Soft delete
);

-- Single portfolio per user (enforced by unique constraint)
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL DEFAULT 'My Portfolio',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,  -- Soft delete
    UNIQUE(user_id)  -- Enforces single portfolio per user
);

-- No session table needed - JWTs are stateless
-- No refresh tokens for V1 - users login daily
```

### 1.2 Market Data Cache (Enhanced)

```sql
-- Enhanced market data cache with sector/industry
CREATE TABLE market_data_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    -- NEW FIELDS
    sector VARCHAR(100),        -- From YFinance
    industry VARCHAR(100),      -- From YFinance  
    data_source VARCHAR(20) NOT NULL DEFAULT 'polygon',  -- 'polygon' or 'yfinance'
    -- END NEW FIELDS
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);
```

### 1.3 Factor Definitions Table

```sql
-- Fixed factor definitions (8 factors)
CREATE TABLE factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    etf_proxy VARCHAR(10) NOT NULL,  -- ETF ticker used as proxy
    factor_type VARCHAR(20) NOT NULL, -- 'style', 'sector', 'macro'
    calculation_method TEXT,          -- Description of calculation
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert the 8 fixed factors
INSERT INTO factors (name, description, etf_proxy, factor_type, display_order) VALUES
('Market Beta', 'Exposure to overall market movements', 'SPY', 'macro', 1),
('Momentum', 'Exposure to recent price momentum', 'MTUM', 'style', 2),
('Value', 'Exposure to value characteristics', 'VTV', 'style', 3),
('Growth', 'Exposure to growth characteristics', 'VUG', 'style', 4),
('Quality', 'Exposure to quality metrics', 'QUAL', 'style', 5),
('Size', 'Exposure to small-cap stocks', 'IWM', 'style', 6),
('Low Volatility', 'Exposure to low volatility stocks', 'SPLV', 'style', 7),
('Short Interest', 'Custom calculation based on short interest', 'CUSTOM', 'macro', 8);
```

### 1.4 Tags Tables (Complete)

```sql
-- Tags with support for regular and strategy types
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    tag_type VARCHAR(20) NOT NULL CHECK (tag_type IN ('REGULAR', 'STRATEGY')),
    color VARCHAR(7) DEFAULT '#6B7280',  -- Hex color
    usage_count INTEGER DEFAULT 0,       -- Track popularity
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,  -- Soft delete
    UNIQUE(user_id, name)
);

-- Many-to-many relationship
CREATE TABLE position_tags (
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (position_id, tag_id)
);
```

### 1.5 Enhanced Positions Table

```sql
-- Positions with parsed options data
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(30) NOT NULL,
    position_type position_type_enum NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    
    -- Options-specific parsed fields
    underlying_symbol VARCHAR(10),     -- e.g., 'AAPL' from 'AAPL240119C00150000'
    expiration_date DATE,             -- e.g., '2024-01-19'
    strike_price DECIMAL(10,2),       -- e.g., 150.00
    option_type VARCHAR(4),           -- 'CALL' or 'PUT'
    
    -- Entry tracking
    entry_price DECIMAL(12,4) NOT NULL,
    entry_date DATE NOT NULL,
    
    -- Current values (updated by batch)
    last_price DECIMAL(12,4),
    market_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(15,2),
    unrealized_pnl_pct DECIMAL(8,4),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL  -- Soft delete
);
```

### 1.6 Portfolio Snapshots

```sql
-- Daily portfolio snapshots for historical tracking
CREATE TABLE portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    
    -- Portfolio metrics
    total_value DECIMAL(15,2) NOT NULL,
    cash_value DECIMAL(15,2) DEFAULT 0,
    long_value DECIMAL(15,2) NOT NULL,
    short_value DECIMAL(15,2) NOT NULL,
    
    -- Exposures
    gross_exposure DECIMAL(15,2) NOT NULL,
    net_exposure DECIMAL(15,2) NOT NULL,
    
    -- P&L
    daily_pnl DECIMAL(15,2),
    daily_pnl_pct DECIMAL(8,4),
    cumulative_pnl DECIMAL(15,2),
    
    -- Risk metrics
    portfolio_beta DECIMAL(6,3),
    portfolio_volatility DECIMAL(6,4),
    sharpe_ratio DECIMAL(6,3),
    max_drawdown DECIMAL(6,4),
    
    -- Greeks aggregates
    total_delta DECIMAL(10,4),
    total_gamma DECIMAL(10,4),
    total_theta DECIMAL(10,4),
    total_vega DECIMAL(10,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, snapshot_date)
);
```

### 1.7 Batch Processing Tables

```sql
-- Simple batch job tracking
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL,  -- 'market_data', 'risk_calc', 'snapshot'
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,  -- Job-specific data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Track last successful run for each job type
CREATE TABLE batch_job_schedules (
    job_type VARCHAR(50) PRIMARY KEY,
    cron_expression VARCHAR(100) NOT NULL,  -- e.g., '0 16 * * *' for 4 PM daily
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    is_enabled BOOLEAN DEFAULT true
);
```

## 2. Data Transformation Specifications

### 2.1 CSV Import Transformation

```python
def parse_csv_row(row: dict, user_id: str, portfolio_id: str) -> dict:
    """Transform CSV row to position record"""
    
    symbol = row['ticker'].strip().upper()
    quantity = float(row['quantity'])
    
    # Parse position type
    position_type = determine_position_type(symbol, quantity)
    
    # Parse options data if applicable
    options_data = parse_options_symbol(symbol) if is_options_symbol(symbol) else {}
    
    # Parse tags
    tags = [tag.strip() for tag in row.get('tags', '').split(',') if tag.strip()]
    
    return {
        'portfolio_id': portfolio_id,
        'symbol': symbol,
        'position_type': position_type,
        'quantity': abs(quantity),  # Always store positive
        'entry_price': float(row['entry_price']),
        'entry_date': row['entry_date'],  # Expected format: YYYY-MM-DD
        'tags': tags,
        **options_data  # Includes underlying_symbol, expiration_date, etc.
    }

def determine_position_type(symbol: str, quantity: float) -> str:
    """Determine position type from symbol and quantity"""
    
    if is_options_symbol(symbol):
        # OCC format check
        option_type = 'C' if 'C' in symbol[-9] else 'P'
        
        if quantity > 0:
            return 'LC' if option_type == 'C' else 'LP'
        else:
            return 'SC' if option_type == 'C' else 'SP'
    else:
        # Stock position
        return 'LONG' if quantity > 0 else 'SHORT'

def is_options_symbol(symbol: str) -> bool:
    """Check if symbol is OCC format option"""
    # OCC format: AAPL240119C00150000 (min 15 chars)
    return len(symbol) >= 15 and symbol[-9:-7].isdigit()

def parse_options_symbol(symbol: str) -> dict:
    """Parse OCC format option symbol"""
    if not is_options_symbol(symbol):
        return {}
    
    # Example: AAPL240119C00150000
    # Find where the date starts (first digit after letters)
    date_start = next(i for i, c in enumerate(symbol) if c.isdigit())
    
    underlying = symbol[:date_start]
    date_str = symbol[date_start:date_start+6]  # YYMMDD
    option_type = 'CALL' if 'C' in symbol[date_start+6] else 'PUT'
    strike_str = symbol[-8:]  # 00150000 = $150.00
    
    return {
        'underlying_symbol': underlying,
        'expiration_date': f'20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}',
        'strike_price': float(strike_str) / 1000,
        'option_type': option_type
    }
```

### 2.2 Mock Greeks Values

```python
# Mock Greeks by position type (Phase 1)
MOCK_GREEKS = {
    'LC': {'delta': 0.65, 'gamma': 0.02, 'theta': -0.05, 'vega': 0.15, 'rho': 0.08},
    'LP': {'delta': -0.35, 'gamma': 0.02, 'theta': -0.05, 'vega': 0.15, 'rho': -0.06},
    'SC': {'delta': -0.65, 'gamma': -0.02, 'theta': 0.05, 'vega': -0.15, 'rho': -0.08},
    'SP': {'delta': 0.35, 'gamma': -0.02, 'theta': 0.05, 'vega': -0.15, 'rho': 0.06},
    'LONG': {'delta': 1.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0},
    'SHORT': {'delta': -1.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0}
}

def get_mock_greeks(position_type: str, quantity: float) -> dict:
    """Return scaled mock Greeks for a position"""
    base_greeks = MOCK_GREEKS[position_type].copy()
    
    # Scale by quantity (contracts for options, shares/100 for stocks)
    multiplier = quantity if position_type in ['LC', 'LP', 'SC', 'SP'] else quantity / 100
    
    return {k: v * multiplier for k, v in base_greeks.items()}
```

## 3. Database Indexes

```sql
-- Primary key indexes are automatic

-- Foreign key indexes (some automatic, explicitly ensure)
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_positions_portfolio_id ON positions(portfolio_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_position_tags_position_id ON position_tags(position_id);
CREATE INDEX idx_position_tags_tag_id ON position_tags(tag_id);

-- Common query patterns
CREATE INDEX idx_positions_symbol ON positions(symbol) WHERE deleted_at IS NULL;
CREATE INDEX idx_positions_type ON positions(position_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_market_data_symbol_date ON market_data_cache(symbol, date DESC);
CREATE INDEX idx_snapshots_portfolio_date ON portfolio_snapshots(portfolio_id, snapshot_date DESC);

-- Tag queries
CREATE INDEX idx_tags_user_type ON tags(user_id, tag_type) WHERE deleted_at IS NULL;

-- Options queries
CREATE INDEX idx_positions_expiration ON positions(expiration_date) 
    WHERE expiration_date IS NOT NULL AND deleted_at IS NULL;

-- Batch job monitoring
CREATE INDEX idx_batch_jobs_status_created ON batch_jobs(status, created_at DESC);
```

## 4. Environment Configuration

### 4.1 Local Development (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sigmasight_dev

# Authentication
JWT_SECRET=local-development-secret-do-not-use-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# External APIs
POLYGON_API_KEY=your_polygon_api_key_here
YFINANCE_CACHE_DIR=./cache/yfinance

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Batch Processing
BATCH_MARKET_DATA_HOUR=16  # 4 PM
BATCH_RISK_CALC_HOUR=17    # 5 PM
```

### 4.2 Railway Production Environment

```bash
# Set these in Railway dashboard:

# DATABASE_URL - Automatically provided by Railway Postgres
JWT_SECRET=<generate with: openssl rand -hex 32>
POLYGON_API_KEY=<your production API key>
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4.3 Configuration Management

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # APIs
    polygon_api_key: str
    
    # App
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

## 5. Demo Data Specifications

### 5.1 Demo Users

```sql
-- Create 3 demo users with different portfolio strategies
INSERT INTO users (username, email, password_hash, is_demo) VALUES
('demo_growth', 'demo_growth@sigmasight.com', '<bcrypt hash of "demo123">', true),
('demo_value', 'demo_value@sigmasight.com', '<bcrypt hash of "demo123">', true),
('demo_balanced', 'demo_balanced@sigmasight.com', '<bcrypt hash of "demo123">', true);
```

### 5.2 Demo Portfolio Characteristics

1. **demo_growth**: Tech-heavy, momentum plays, some options
   - 25 positions: 18 long stocks, 3 short stocks, 4 options
   - Heavy NASDAQ exposure
   
2. **demo_value**: Traditional value investing
   - 20 positions: 15 long stocks, 5 short stocks
   - Focus on financials, energy
   
3. **demo_balanced**: Mixed strategies
   - 30 positions: 20 stocks, 10 options
   - Includes pairs trades and hedges

### 5.3 Historical Data Generation

```python
def generate_historical_snapshots(portfolio_id: str, days: int = 90):
    """Generate 90 days of historical snapshots with realistic variations"""
    
    base_value = 1_000_000  # $1M starting value
    volatility = 0.02       # 2% daily volatility
    
    for day in range(days):
        date = datetime.now().date() - timedelta(days=days-day)
        
        # Random walk with slight upward bias
        daily_return = np.random.normal(0.0003, volatility)
        base_value *= (1 + daily_return)
        
        snapshot = {
            'portfolio_id': portfolio_id,
            'snapshot_date': date,
            'total_value': base_value,
            'daily_pnl_pct': daily_return,
            # ... other metrics
        }
        
        create_snapshot(snapshot)
```

## 6. Batch Processing Schedule

```python
# Batch job configuration
BATCH_JOBS = {
    'market_data_update': {
        'cron': '0 16 * * 1-5',  # 4 PM weekdays
        'function': 'update_market_data',
        'timeout': 300  # 5 minutes
    },
    'calculate_risk_metrics': {
        'cron': '0 17 * * 1-5',  # 5 PM weekdays
        'function': 'calculate_all_risk_metrics',
        'timeout': 600  # 10 minutes
    },
    'create_daily_snapshot': {
        'cron': '30 17 * * 1-5',  # 5:30 PM weekdays
        'function': 'create_portfolio_snapshots',
        'timeout': 300
    }
}
```

## 7. Implementation Priority

### Phase 1 - Core Tables (Week 1)
1. Users & Authentication
2. Portfolios
3. Positions (with options parsing)
4. Market Data Cache
5. Tags

### Phase 2 - Analytics (Week 2)
1. Portfolio Snapshots
2. Position Greeks
3. Factor Definitions
4. Risk Metrics

### Phase 3 - Operations (Week 3)
1. Batch Jobs
2. Demo Data Generation
3. Historical Snapshots

## 8. Key Decisions Summary

1. **Single Portfolio**: Enforced by unique constraint
2. **Mock Greeks**: Use provided values, no pricing library
3. **Sync API**: No async job management
4. **Batch Processing**: All calculations run on schedule
5. **Soft Deletes**: Track deleted_at, never hard delete
6. **JWT Auth**: Stateless, 24-hour expiry
7. **Tag System**: Supports both regular and strategy tags

## 9. Migration Commands

```bash
# Create database
createdb sigmasight_dev

# Run migrations (using Alembic)
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head

# Load demo data
python scripts/load_demo_data.py
```

This addendum provides complete resolution to all identified issues and clear implementation guidance for the SigmaSight V1 database.
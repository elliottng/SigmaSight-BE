# SigmaSight Backend - AI Agent Reference Guide

**Purpose**: Comprehensive reference for AI coding agents to quickly understand codebase structure, avoid discovery overhead, and implement features efficiently.

**Target Audience**: AI agents (Claude, ChatGPT, etc.) working on SigmaSight backend development

**Last Updated**: 2025-01-16

---

## 🏗️ Codebase Architecture Quick Reference

### **Directory Structure & Purpose**
```
app/
├── models/           - Database models (SQLAlchemy ORM)
│   ├── users.py      - User, Portfolio models
│   ├── positions.py  - Position, Tag, PositionType enums
│   ├── market_data.py - PositionGreeks, PositionFactorExposure, StressTestResult
│   ├── correlations.py - CorrelationCalculation
│   ├── snapshots.py  - PortfolioSnapshot
│   └── history.py    - Historical data models
├── batch/            - Batch processing framework (8 calculation engines)
│   ├── batch_orchestrator_v2.py - Main orchestration (run_daily_batch_sequence)
│   └── scheduler_config.py   - APScheduler configuration  
├── calculations/     - Core calculation engines
│   ├── greeks.py     - Options Greeks (mibian library)
│   ├── factors.py    - Factor exposure analysis
│   ├── correlations.py - Position correlations
│   └── market_risk.py - Market risk scenarios
├── api/v1/endpoints/ - FastAPI REST endpoints
├── core/             - Core utilities (config, logging, auth)
├── db/               - Database utilities and seeding
│   └── seed_demo_portfolios.py - Demo data creation
└── database.py       - Database connection utilities

scripts/              - Utility scripts
├── reset_and_seed.py - Main seeding script (AUTHORITATIVE)
└── test_*.py         - Testing scripts

_docs/requirements/   - Product requirements and specifications
├── PRD_PORTFOLIO_REPORT_SPEC.md - Portfolio report generator PRD
└── BATCH_TESTING_PRAGMATIC.md  - Batch testing procedures
```

### **Key Configuration Files**
```
docker-compose.yml    - PostgreSQL database (Redis removed)
pyproject.toml       - Dependencies (mibian, not py_vollib)
.env                 - Environment variables (no REDIS_URL)
alembic/             - Database migrations
TODO1.md             - Phase 1 implementation status
TODO2.md             - Phase 2+ planning
```

---

## 🔗 Critical Import Patterns

### **Database Models**
```python
# User and Portfolio models
from app.models.users import User, Portfolio

# Position models  
from app.models.positions import Position, PositionType, Tag, TagType

# Calculation result models
from app.models.market_data import PositionGreeks, PositionFactorExposure, StressTestResult
from app.models.correlations import CorrelationCalculation
from app.models.snapshots import PortfolioSnapshot

# Database utilities
from app.database import get_async_session, AsyncSessionLocal
```

### **Batch Processing**
```python
# Main batch orchestrator
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2

# Individual calculation engines
from app.calculations.greeks import calculate_position_greeks
from app.calculations.factors import calculate_factor_exposures
from app.calculations.portfolio_aggregation import calculate_portfolio_exposures
```

### **Core Utilities**
```python
# Configuration
from app.config import settings

# Logging
from app.core.logging import get_logger

# Authentication  
from app.core.auth import get_password_hash
```

---

## 🗄️ Database Schema Quick Reference

### **Core Relationships**
```
User (1) ─→ (N) Portfolio ─→ (N) Position
                │                │
                │                ├─→ (1) PositionGreeks
                │                ├─→ (N) PositionFactorExposure  
                │                └─→ (N) Tag (M:N relationship)
                │
                ├─→ (N) PortfolioSnapshot
                ├─→ (N) CorrelationCalculation
                └─→ (N) StressTestResult (⚠️ TABLE MISSING - see TODO1.md 1.6.14)
```

### **Common Query Patterns**
```python
# Get portfolios for user
portfolios = await db.execute(
    select(Portfolio).where(Portfolio.user_id == user_id)
)

# Get positions for portfolio
positions = await db.execute(
    select(Position).where(Position.portfolio_id == portfolio_id)
)

# Get latest portfolio snapshot
snapshot = await db.execute(
    select(PortfolioSnapshot)
    .where(PortfolioSnapshot.portfolio_id == portfolio_id)
    .order_by(PortfolioSnapshot.calculation_date.desc())
    .limit(1)
)

# Count records for data verification
count = await db.execute(select(func.count(PositionGreeks.id)))
```

### **UUID Handling Pattern**
```python
# Always convert string UUIDs to UUID objects when needed
from uuid import UUID

if isinstance(portfolio_id, str):
    portfolio_uuid = UUID(portfolio_id)
else:
    portfolio_uuid = portfolio_id  # Already UUID object
```

---

## ⚙️ Batch Processing System

### **8 Calculation Engines Status**
1. **Portfolio Aggregation** ✅ Working
2. **Position Greeks** ✅ Working (mibian library)  
3. **Factor Analysis** ⚠️ Partial (missing factor ETF data)
4. **Market Risk Scenarios** ⚠️ Partial (async/sync issues)
5. **Stress Testing** ❌ Failed (missing stress_test_results table)
6. **Portfolio Snapshots** ✅ Working
7. **Position Correlations** ✅ Working  
8. **Factor Correlations** ✅ Working

### **Batch Execution**
```python
# Main entry point
await batch_orchestrator_v2.run_daily_batch_sequence()  # Runs all 8 engines

# Individual portfolio  
await batch_orchestrator_v2.run_daily_batch_sequence(portfolio_id="uuid-string")

# Check if batch orchestrator imports correctly
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2
print("Batch orchestrator ready!")
```

### **Known Batch Issues (see TODO1.md 1.6.14)**
- **CRITICAL**: Async/sync mixing causes greenlet errors
- **CRITICAL**: Missing stress_test_results table in database
- **HIGH**: Market data gaps (SPY/QQQ options, factor ETFs, BRK.B)
- **HIGH**: Treasury rate data insufficient for IR beta calculations

---

## 📊 Demo Data Reference

### **Demo Portfolios (3 Main)**
```python
# Email addresses for demo users
DEMO_USERS = [
    "demo_individual@sigmasight.com",     # Balanced Individual Investor
    "demo_hnw@sigmasight.com",           # High Net Worth Investor  
    "demo_hedgefundstyle@sigmasight.com" # Hedge Fund Style Investor
]

# Portfolio names
"Balanced Individual Investor Portfolio"      # 16 positions
"Sophisticated High Net Worth Portfolio"      # 17 positions  
"Long/Short Equity Hedge Fund Style Portfolio" # 30 positions (includes options)

# Total expected positions: 63 across all 3 portfolios
```

### **Demo Data Commands**
```bash
# Seed all demo data (AUTHORITATIVE script)
python scripts/reset_and_seed.py seed

# Test specific seeding
uv run python app/db/seed_demo_portfolios.py

# Check demo data status
uv run python -c "
from app.models.users import Portfolio
from app.database import get_async_session
import asyncio

async def check():
    async with get_async_session() as db:
        result = await db.execute(select(Portfolio))
        portfolios = result.scalars().all()
        print(f'Found {len(portfolios)} portfolios')
        
asyncio.run(check())
"
```

---

## 🔧 Environment & Dependencies

### **Database Setup**
```bash
# Start PostgreSQL (Docker)
docker-compose up -d

# Apply migrations
uv run alembic upgrade head

# Check database connection
uv run python -c "from app.database import get_async_session; print('DB connection ready')"
```

### **Key Environment Variables (.env)**
```bash
# Database (required)
DATABASE_URL=postgresql+asyncpg://sigmasight:sigmasight_dev@localhost:5432/sigmasight_db

# Market Data APIs (required for batch processing)
POLYGON_API_KEY=your_polygon_key
FMP_API_KEY=your_fmp_key
TRADEFEEDS_API_KEY=your_tradefeeds_key
FRED_API_KEY=your_fred_key

# JWT (required)
SECRET_KEY=your_secret_key

# Note: REDIS_URL removed - not used in application
```

### **Dependencies Note**
- ✅ **mibian**: Used for Greeks calculations
- ❌ **py_vollib**: Removed due to `_testcapi` import issues
- ❌ **redis**: Removed - unused dependency
- ❌ **celery**: Removed - unused dependency

---

## 🚨 Known Issues & Workarounds

### **Current System Limitations**

**1. Batch Processing Issues** (TODO1.md Section 1.6.14)
- Async/sync architecture mixing → Use pure async patterns
- Missing database tables → Check `alembic upgrade head`
- Market data provider gaps → Implement graceful degradation

**2. Tag Relationships**
- Async relationship access has limitations for existing positions
- Workaround: Create tags during position creation, not after

**3. UUID Serialization**
- Batch jobs have UUID type handling workarounds
- Pattern: Always convert string to UUID when needed

### **Common Error Patterns & Solutions**

```python
# Error: "cannot import name X from Y"
# Solution: Check actual model locations in app/models/

# Error: "greenlet_spawn has not been called"  
# Solution: Ensure using async session properly
async with get_async_session() as db:
    # All database operations here

# Error: "relation does not exist"
# Solution: Apply migrations
# uv run alembic upgrade head

# Error: "Extra inputs are not permitted" (REDIS_URL)
# Solution: Remove REDIS_URL from .env file
```

### **Working Patterns**
```python
# Graceful degradation for missing data
try:
    result = await db.execute(select(SomeTable))
    data = result.scalars().all()
except Exception as e:
    logger.warning(f"Missing data: {e}")
    data = []  # Proceed with empty data

# Check table existence before querying
from sqlalchemy import inspect
inspector = inspect(db.bind)
if 'table_name' in inspector.get_table_names():
    # Query the table
else:
    # Handle missing table
```

---

## 🔍 Quick Diagnostic Commands

### **Test Critical Imports**
```bash
# Test all key imports work
uv run python -c "
from app.models.users import Portfolio
from app.models.market_data import PositionGreeks
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2
from app.database import get_async_session
print('✅ All critical imports working')
"
```

### **Check Data Status**
```bash
# Quick data verification
uv run python -c "
import asyncio
from sqlalchemy import select, func
from app.database import get_async_session
from app.models.users import Portfolio
from app.models.market_data import PositionGreeks

async def check():
    async with get_async_session() as db:
        portfolios = await db.execute(select(func.count(Portfolio.id)))
        greeks = await db.execute(select(func.count(PositionGreeks.id)))
        print(f'Portfolios: {portfolios.scalar()}, Greeks: {greeks.scalar()}')

asyncio.run(check())
"
```

### **Environment Validation**
```bash
# Check environment setup
uv run python -c "
from app.config import settings
print(f'Database: {settings.DATABASE_URL[:50]}...')
print(f'Polygon API: {'SET' if settings.POLYGON_API_KEY else 'MISSING'}')
print('✅ Environment configured')
"
```

---

## 📋 Common Development Tasks

### **Adding New Models**
1. Create model in appropriate `app/models/` file
2. Add to `alembic/env.py` if needed
3. Generate migration: `uv run alembic revision --autogenerate -m "description"`
4. Apply migration: `uv run alembic upgrade head`

### **Testing Batch Jobs**
1. Ensure demo data seeded: `python scripts/reset_and_seed.py seed`
2. Test individual functions before running full batch
3. Check TODO1.md Section 1.6.14 for known issues
4. Use graceful degradation for missing data

### **Working with Portfolio Reports** (Phase 2.0)
1. Reference `_docs/requirements/PRD_PORTFOLIO_REPORT_SPEC.md`
2. Use existing calculation data (even if incomplete)
3. Implement graceful degradation for missing calculation engines
4. Target 3 demo portfolios initially

---

## 🎯 Phase-Specific Context

### **Phase 1: COMPLETED** ✅
- All 8 batch calculation engines implemented
- Demo data seeding production-ready
- Database schema complete (except stress_test_results)
- Basic infrastructure solid

### **Phase 2.0: Portfolio Report Generator** ⏳ **CURRENT**
- Generate LLM-optimized reports (MD, JSON, CSV formats)
- Use existing calculation data with graceful degradation
- Target: 3 demo portfolios
- Known issues documented in TODO1.md 1.6.14

### **Phase 3.0: Developer Experience** 📋 **PLANNED**
- Streamlined onboarding (enhanced from Redis removal)
- Automated setup scripts
- Better documentation

---

## 💡 AI Agent Efficiency Tips

1. **Always check TODO1.md and TODO2.md first** for current status and known issues
2. **Use existing demo data** rather than creating new test data
3. **Implement graceful degradation** for missing calculation data
4. **Reference this guide** instead of exploring file structure
5. **Check completion status** in TODO files before implementing features
6. **Use the diagnostic commands** to verify environment quickly

---

**Remember**: This codebase has 8 working calculation engines with some data gaps. Use graceful degradation patterns and reference the systematic issue resolution plan in TODO1.md Section 1.6.14 for any batch processing problems.
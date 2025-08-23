# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SigmaSight Backend - A FastAPI-based portfolio risk analytics platform with 8 calculation engines, automated batch processing, and comprehensive financial analytics. The project is structured with the main application code in the `sigmasight-backend/` subdirectory.

## Common Development Commands

### Server & Development
```bash
# Start development server
cd sigmasight-backend
uv run python run.py              # Main development server
uvicorn app.main:app --reload     # Alternative with auto-reload

# Database setup
docker-compose up -d               # Start PostgreSQL
uv run alembic upgrade head        # Run migrations
uv run python scripts/seed_database.py  # Seed demo data (3 portfolios, 63 positions)
```

### Testing
```bash
# Run test suite
uv run pytest                      # All tests
uv run pytest tests/test_market_data_service.py  # Single test file
uv run pytest -k "test_function_name"  # Single test function

# Verification scripts
uv run python scripts/verify_setup.py    # Verify installation
./scripts/test_api_endpoints.sh          # Test API endpoints
```

### Code Quality
```bash
# Format and lint
uv run black .                     # Format code
uv run isort .                     # Sort imports
uv run flake8 app/                 # Lint
uv run mypy app/                   # Type checking
```

### Batch Processing & Reports
```bash
# Manual batch runs
uv run python scripts/run_batch_calculations.py      # Run all calculations
uv run python scripts/generate_all_reports.py        # Generate portfolio reports

# Database reset
uv run python scripts/reset_and_seed.py              # Full reset and reseed
```

## High-Level Architecture

### Core Structure
The application follows a multi-layered architecture within `sigmasight-backend/`:

```
app/
├── api/v1/endpoints/     # FastAPI REST endpoints
├── models/               # SQLAlchemy ORM models
├── services/             # Business logic layer
├── batch/                # Batch processing orchestration
├── calculations/         # Financial calculation engines
├── core/                 # Shared utilities (auth, db, logging)
└── database.py           # Database connection management
```

### Key Architectural Patterns

1. **Async-First Design**: All database operations use async/await with SQLAlchemy 2.0
2. **Batch Processing Framework**: 8 sequential calculation engines with graceful degradation
3. **Multi-Provider Market Data**: FMP (primary), Polygon (options), FRED (economic)
4. **Hybrid Calculation Engine**: Real calculations with mock fallbacks when data unavailable

### Database Architecture
- PostgreSQL with UUID primary keys
- Alembic for schema migrations
- Full audit trails with created_at/updated_at
- Relationships: User → Portfolio → Position → Calculations

### Critical Import Paths
```python
# Database models
from app.models.users import User, Portfolio
from app.models.positions import Position, PositionType
from app.models.market_data import PositionGreeks, PositionFactorExposure

# Database utilities
from app.database import get_async_session, AsyncSessionLocal

# Batch processing
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2

# Core utilities
from app.config import settings
from app.core.logging import get_logger
```

## Important Context

### Current Status
- **Phase**: 2.0 - Portfolio Report Generator implementation
- **Calculation Engines**: 5/6 operational (83.3% functional)
- **Demo Data**: 3 portfolios with 63 positions ready for testing
- **Known Issues**: See `sigmasight-backend/TODO1.md` Section 1.6.14 for batch processing issues

### Key Documentation
- **`sigmasight-backend/AI_AGENT_REFERENCE.md`**: Comprehensive codebase reference (READ FIRST)
- **`sigmasight-backend/TODO1.md`**: Phase 1 status and known issues
- **`sigmasight-backend/TODO2.md`**: Current phase planning and tasks
- **`sigmasight-backend/_docs/requirements/`**: Product requirements and specifications

### Environment Variables
Required in `.env` file:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/sigmasight
POLYGON_API_KEY=your_key_here
SECRET_KEY=your_jwt_secret
FMP_API_KEY=your_fmp_key  # Optional but recommended
FRED_API_KEY=your_fred_key  # Optional
```

### Common Gotchas
1. **Async/Sync Mixing**: Always use async patterns - mixing causes greenlet errors
2. **UUID Handling**: Convert string UUIDs to UUID objects when needed
3. **Missing Tables**: stress_test_results table doesn't exist (known issue)
4. **Import Errors**: Use diagnostic commands from AI_AGENT_REFERENCE.md
5. **Demo Data**: Always test with existing demo portfolios first

### Testing Approach
- Use existing demo data (don't create new test data)
- Run diagnostic commands to verify imports
- Test with graceful degradation for missing data
- Update TODO files with completion status

## Development Workflow

1. **Before Starting**: Read `sigmasight-backend/AI_AGENT_REFERENCE.md`
2. **Check Status**: Review TODO1.md and TODO2.md for context
3. **Test Imports**: Use diagnostic commands to verify setup
4. **Implement**: Follow async patterns, handle errors gracefully
5. **Update Docs**: Document new patterns in AI_AGENT_REFERENCE.md
6. **Mark Complete**: Update TODO status with detailed results

## Key Commands for Debugging

```bash
# Verify critical imports
PYTHONPATH=/Users/elliottng/CascadeProjects/SigmaSight-BE/sigmasight-backend uv run python -c "from app.models.users import User; print('✅ Models import successfully')"

# Check database content
uv run python scripts/check_database_content.py

# Test batch processing
uv run python scripts/test_batch_with_reports.py

# Verify demo portfolios
uv run python scripts/verify_demo_portfolios.py
```

## Notes
- Main application code is in `sigmasight-backend/` subdirectory
- Always work from the `sigmasight-backend/` directory when running commands
- Update `sigmasight-backend/AI_AGENT_REFERENCE.md` when discovering new patterns
- Prefer simple, correct implementations over complex feature flags
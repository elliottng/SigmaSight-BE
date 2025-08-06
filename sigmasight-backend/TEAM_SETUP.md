# Team Development Setup Guide

## For Multiple Developers Working on SigmaSight

This guide ensures all team members have consistent development environments.

## Quick Setup for New Team Members

### 1. Clone and Environment Setup
```bash
git clone https://github.com/elliottng/SigmaSight-BE.git
cd SigmaSight-BE/sigmasight-backend

# Copy environment template
cp .env.example .env

# Install dependencies
uv sync
```

### 2. Database Setup
```bash
# Start PostgreSQL (with Docker)
docker-compose up -d

# Set up development database (consistent across all team members)
uv run python scripts/setup_dev_database.py

# Add demo users for testing
uv run python scripts/seed_demo_users.py
```

### 3. Verify Setup
```bash
# Run integration tests to verify everything works
uv run python scripts/test_api_providers/integration_test.py

# Start development server
uv run python run.py
```

## Development Workflow

### Daily Development
- Use `scripts/setup_dev_database.py` to reset your local database
- This ensures everyone starts with the same clean schema
- Safe to run multiple times during development

### When Someone Adds New Models
1. **Model Author**: Add the new model to imports in `scripts/setup_dev_database.py`
2. **Team Members**: Run `uv run python scripts/setup_dev_database.py` to get the new tables
3. **Everyone**: Continues development with consistent schema

### Database Changes Process
1. **Add new models** to appropriate files in `app/models/`
2. **Update** `scripts/setup_dev_database.py` imports if needed
3. **Test locally** with `uv run python scripts/setup_dev_database.py`
4. **Commit** both model and setup script changes
5. **Team notification**: "New models added, run setup_dev_database.py"

## Why This Approach?

### ✅ Benefits for Team Development:
- **Consistent environments**: Everyone has identical database schema
- **No migration conflicts**: No risk of conflicting Alembic migrations during development
- **Fast iteration**: Add model → run script → start coding
- **Easy onboarding**: New team members get working environment quickly
- **Reset capability**: Can always start fresh if something gets corrupted
- **Model-driven**: Schema is always in sync with code

### ⚠️ Important Notes:
- **Development only**: This approach is for local development environments
- **Data loss expected**: Running the setup script drops all existing data
- **Production ready**: We have proper Alembic migrations for production deployment

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart if needed
docker-compose down
docker-compose up -d
```

### Schema Issues
```bash
# Reset everything
uv run python scripts/setup_dev_database.py

# This will:
# 1. Drop all tables
# 2. Recreate from current models
# 3. Verify setup
```

### Import Errors
```bash
# Reinstall dependencies
uv sync

# Check Python path
uv run python -c "import app; print('OK')"
```

## Production Deployment

When ready for production, we'll use proper Alembic migrations:

```bash
# Generate migration from current models
alembic revision --autogenerate -m "production deployment"

# Deploy to production
alembic upgrade head
```

## File Structure

```
scripts/
├── setup_dev_database.py     # Team development setup
├── init_database.py          # Legacy script (kept for compatibility)
├── seed_demo_users.py        # Demo data creation
└── test_api_providers/       # Section 1.4.9 testing scripts

app/models/                    # All database models (source of truth)
├── users.py
├── positions.py  
├── market_data.py            # Includes new FundHoldings model
└── ...

alembic/                       # For production deployments
├── versions/
│   └── bb4d41ad753e_baseline_all_models_v1_4_9.py
└── ...
```

## Team Communication

### When Making Schema Changes:
1. **Announce in team chat**: "Adding new model: XYZ"
2. **Include in PR description**: "Requires running setup_dev_database.py"
3. **After merge**: "New schema changes merged, please run setup script"

### Before Major Features:
- Consider if new models will be needed
- Plan schema changes as a team
- Coordinate who adds what models

This approach keeps development fast and consistent while maintaining production safety through proper migrations.
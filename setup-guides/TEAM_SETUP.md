# Professional Team Development Setup Guide

## For Multiple Developers Working on SigmaSight

This guide ensures all team members use professional database migration workflows.

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

### 2. Professional Database Setup
```bash
# Start PostgreSQL (with Docker)
docker-compose up -d

# Set up database using proper Alembic migrations
uv run python scripts/setup_dev_database_alembic.py

# Seed demo data (users, portfolios, factors, security master, prices)
uv run python scripts/seed_database.py
```

### 3. Verify Setup
```bash
# Run integration tests to verify everything works
uv run python scripts/test_api_providers/integration_test.py

# Start development server
uv run python run.py
```

## Development Workflow

### Daily Development with Alembic
- Professional database versioning with proper migrations
- Rollback capability if changes need to be undone
- Full change history and team coordination

### When Someone Adds New Models (Professional Workflow)
1. **Model Author**: 
   - Add new model to appropriate files in `app/models/`
   - Generate migration: `alembic revision --autogenerate -m "add new model"`
   - Test migration: `alembic upgrade head`
   - Commit both model files and migration file

2. **Team Members**: 
   - Pull latest changes: `git pull`
   - Apply new migrations: `alembic upgrade head`
   - Continue development with updated schema

### Database Changes Process (Professional)
1. **Modify models** in `app/models/`
2. **Generate migration**: `alembic revision --autogenerate -m "descriptive message"`
3. **Review migration** file for correctness
4. **Test migration** locally: `alembic upgrade head`
5. **Test rollback** if needed: `alembic downgrade -1` then `alembic upgrade head`
6. **Commit** both model changes and migration file
7. **Team coordination**: Include migration info in PR/commit message

## Why This Approach?

### Benefits for Professional Development:
- **Database versioning**: Full history of all schema changes
- **Rollback capability**: Can undo problematic migrations safely
- **Team coordination**: Clear migration files show what changed and when
- **Production safety**: Same tools used in development and production
- **Change tracking**: Alembic tracks exactly what was applied when
- **Industry standard**: Professional teams expect Alembic workflows

### Migration Advantages:
- **Incremental updates**: Only apply changes since last migration
- **Data preservation**: Migrations can transform data during schema changes
- **Conflict resolution**: Team members can coordinate schema changes through git
- **Audit trail**: Complete history of database evolution

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
# Reset everything with proper Alembic (WARNING: loses data)
uv run python scripts/setup_dev_database_alembic.py --reset

# This will:
# 1. Drop all tables
# 2. Apply proper Alembic baseline migration
# 3. Verify setup with professional workflow
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
├── setup_dev_database_alembic.py  # Professional Alembic-based setup
├── seed_database.py          # Orchestrated demo data creation
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
2. **Include in PR description**: "Requires running: alembic upgrade head"
3. **After merge**: "New schema changes merged, please run setup script"

### Before Major Features:
- Consider if new models will be needed
- Plan schema changes as a team
- Coordinate who adds what models

This approach keeps development fast and consistent while maintaining production safety through proper migrations.
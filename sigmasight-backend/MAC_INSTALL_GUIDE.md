# SigmaSight Backend - Mac Installation Guide for AI Agents

This guide provides complete step-by-step instructions for setting up the SigmaSight Backend on macOS for development and testing. Each step includes verification commands to ensure successful execution.

## 📋 System Requirements

- macOS 10.15 (Catalina) or later
- At least 4GB of free disk space
- Internet connection for downloading packages
- Administrator access for installing software

## 🎯 Overview

We'll install and configure these components:
1. **Homebrew** - Package manager for macOS
2. **Python 3.11+** - Programming language runtime
3. **Docker Desktop** - Container platform for database
4. **UV** - Fast Python package manager
5. **PostgreSQL** - Database (via Docker)
6. **SigmaSight Backend** - The application itself

## Prerequisites Check

Before starting, verify these tools are available:

```bash
# Check if Homebrew is installed
which brew || echo "❌ Homebrew not installed"

# Check if Docker is installed and running
docker --version || echo "❌ Docker not installed"
docker ps || echo "❌ Docker not running"

# Check Python version (need 3.11+)
python3 --version || echo "❌ Python3 not installed"

# Check if UV is installed
uv --version || echo "❌ UV not installed"
```

## Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd /Users/elliottng/CascadeProjects/SigmaSight-BE/sigmasight-backend
```

**Verification**:
```bash
pwd  # Should show: /Users/elliottng/CascadeProjects/SigmaSight-BE/sigmasight-backend
ls pyproject.toml  # Should exist
```

### Step 2: Install System Prerequisites (if needed)

```bash
# Install Homebrew (skip if already installed)
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Install Python 3.11+ (skip if already installed)
if ! python3 --version | grep -E "3\.(1[1-9]|[2-9][0-9])" &> /dev/null; then
    brew install python@3.11
fi

# Install Docker Desktop (skip if already installed)
if ! command -v docker &> /dev/null; then
    brew install --cask docker
    echo "⚠️ Please open Docker Desktop manually from Applications and wait for it to start"
    echo "Then run: docker ps"
fi

# Install UV package manager (skip if already installed)
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.cargo/env  # Add UV to PATH
fi
```

**Verification**:
```bash
python3 --version  # Should show Python 3.11 or higher
docker --version   # Should show Docker version
docker ps          # Should not error (Docker daemon must be running)
uv --version       # Should show UV version
```

### Step 3: Create and Configure Environment File

```bash
# Create .env from example
cp .env.example .env

# Update database credentials to match docker-compose.yml
cat > .env << 'EOF'
# Database Configuration (matches docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://sigmasight:sigmasight_dev@localhost:5432/sigmasight_db

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379

# Market Data API Keys (optional for basic testing)
POLYGON_API_KEY=your_polygon_api_key_here

# JWT Configuration (generate a secure key)
SECRET_KEY=$(openssl rand -hex 32)

# Application Settings
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF

echo "✅ Environment file created with development settings"
```

**Verification**:
```bash
test -f .env && echo "✅ .env file exists" || echo "❌ .env file missing"
grep DATABASE_URL .env  # Should show the PostgreSQL connection string
```

### Step 4: Install Python Dependencies

```bash
# Install all project dependencies using UV
uv sync

# Activate the virtual environment for manual testing
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate
```

**Verification**:
```bash
uv pip list | grep fastapi  # Should show fastapi installed
uv pip list | grep sqlalchemy  # Should show sqlalchemy installed
python -c "import app; print('✅ App module imports successfully')" 2>/dev/null || echo "❌ App module import failed"
```

### Step 5: Start Database Container

```bash
# Start PostgreSQL container in detached mode
docker-compose up -d postgres

# Wait for database to be ready (max 30 seconds)
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec $(docker ps -qf "name=postgres") pg_isready -U sigmasight &>/dev/null; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    echo -n "."
    sleep 1
done
```

**Verification**:
```bash
# Check container is running
docker ps --filter name=postgres --format "table {{.Names}}\t{{.Status}}"

# Test database connection
docker exec $(docker ps -qf "name=postgres") psql -U sigmasight -d sigmasight_db -c "SELECT version();" || echo "❌ Database connection failed"
```

### Step 6: Initialize Database Schema

```bash
# Run Alembic migrations to create tables
uv run alembic upgrade head

# Seed initial data (if script exists)
if [ -f scripts/seed_database.py ]; then
    uv run python scripts/seed_database.py
    echo "✅ Database seeded with initial data"
fi

# Create demo users for testing (optional but recommended)
if [ -f scripts/seed_demo_users.py ]; then
    uv run python scripts/seed_demo_users.py
    echo "✅ Demo users created:"
    echo "  - Email: demo_growth@sigmasight.com | Password: demo12345"
    echo "  - Email: demo_value@sigmasight.com | Password: demo12345"
    echo "  - Email: demo_balanced@sigmasight.com | Password: demo12345"
    echo ""
    echo "Note: These demo accounts represent different investment strategies:"
    echo "  • Growth: Tech-heavy, momentum plays, some options"
    echo "  • Value: Traditional value investing"
    echo "  • Balanced: Mixed strategies with pairs trades and hedges"
fi
```

**Verification**:
```bash
# Check if tables were created
uv run python -c "
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL').replace('+asyncpg', ''))
with engine.connect() as conn:
    result = conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\"))
    tables = [row[0] for row in result]
    if tables:
        print(f'✅ Database has {len(tables)} tables: {tables[:5]}...')
    else:
        print('❌ No tables found in database')
" 2>/dev/null || echo "❌ Database verification failed"
```

### Step 7: Start the Application Server

```bash
# Start FastAPI with auto-reload for development
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for server to start
sleep 5
```

**Verification**:
```bash
# Test health endpoint
curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Server not responding"

# Check API documentation is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200" && echo "✅ API docs available at http://localhost:8000/docs" || echo "❌ API docs not accessible"
```

### Step 8: Run Tests (Recommended)

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/test_main.py -v  # Basic API tests
uv run pytest tests/test_market_data_service.py -v  # Market data tests
uv run pytest tests/test_portfolio_aggregation.py -v  # Portfolio tests

# Test authentication system (if demo users were created)
if [ -f scripts/test_auth.py ]; then
    uv run python scripts/test_auth.py
    echo "Authentication tests complete - should show 'Success Rate: 100%'"
fi

# Check code quality
uv run black app/ --check
uv run flake8 app/
```

**Verification**:
```bash
# Check test results
if uv run pytest tests/test_main.py -q 2>/dev/null; then
    echo "✅ Basic tests passing"
else
    echo "⚠️ Some tests failing (may be expected without full configuration)"
fi
```

## 🧪 Complete System Validation

### 1. Database Health Check
```bash
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

async def check_db():
    load_dotenv()
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text('SELECT version()'))
            version = result.scalar()
            print(f'✅ PostgreSQL connected: {version[:30]}...')
            
            # Check tables
            result = await conn.execute(text(
                \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'\"
            ))
            table_count = result.scalar()
            print(f'✅ Database has {table_count} tables')
    except Exception as e:
        print(f'❌ Database error: {e}')
    finally:
        await engine.dispose()

asyncio.run(check_db())
" 2>/dev/null || echo "❌ Database check failed"
```

### 2. API Endpoints Test
```bash
# Test key endpoints
echo "Testing API endpoints..."

# Health check
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Health endpoint OK" || echo "❌ Health endpoint failed"

# API docs
curl -s http://localhost:8000/docs | grep -q "swagger" && echo "✅ API docs accessible" || echo "❌ API docs not accessible"

# OpenAPI schema
curl -s http://localhost:8000/openapi.json | grep -q "openapi" && echo "✅ OpenAPI schema available" || echo "❌ OpenAPI schema not available"
```

### 3. Full System Test Script
```bash
# Create and run a comprehensive test script
cat > /tmp/test_sigmasight.py << 'EOF'
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def run_tests():
    results = []
    
    # Test 1: Import checks
    try:
        import app.main
        from app.core.database import get_db
        from app.models import users, positions
        results.append("✅ All imports successful")
    except ImportError as e:
        results.append(f"❌ Import error: {e}")
    
    # Test 2: Configuration
    try:
        from app.config import settings
        if settings.DATABASE_URL:
            results.append("✅ Configuration loaded")
        else:
            results.append("❌ Configuration missing DATABASE_URL")
    except Exception as e:
        results.append(f"❌ Configuration error: {e}")
    
    # Test 3: Database models
    try:
        from app.models.users import User
        from app.models.positions import Position
        results.append("✅ Database models loaded")
    except Exception as e:
        results.append(f"❌ Model loading error: {e}")
    
    # Print results
    print("\n=== System Test Results ===")
    for result in results:
        print(result)
    
    # Return exit code
    return 0 if all("✅" in r for r in results) else 1

sys.exit(asyncio.run(run_tests()))
EOF

uv run python /tmp/test_sigmasight.py
```

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Docker Not Running
```bash
# Error: Cannot connect to Docker daemon
# Solution:
open -a Docker  # Opens Docker Desktop on Mac
sleep 10  # Wait for Docker to start
docker ps  # Verify it's running
```

#### 2. Port Already in Use
```bash
# Error: [Errno 48] Address already in use
# Find what's using port 8000:
lsof -i :8000

# Kill the process (replace PID with actual process ID):
kill -9 PID

# Or use a different port:
uv run uvicorn app.main:app --reload --port 8001
```

#### 3. Database Connection Failed
```bash
# Check if container is running
docker ps | grep postgres

# If not running, restart it:
docker-compose down
docker-compose up -d postgres

# Check logs:
docker logs $(docker ps -qf "name=postgres")

# Reset database if needed:
docker-compose down -v  # Warning: This deletes all data
docker-compose up -d postgres
uv run alembic upgrade head
```

#### 4. UV Command Not Found
```bash
# Reinstall UV:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH:
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### 5. Python Import Errors
```bash
# Clear and reinstall dependencies:
rm -rf .venv
uv venv
uv sync
source .venv/bin/activate
```

#### 6. Alembic Migration Errors
```bash
# Check current migration status:
uv run alembic current

# If corrupted, reset (WARNING: loses data):
docker exec $(docker ps -qf "name=postgres") psql -U sigmasight -d sigmasight_db -c "DROP TABLE IF EXISTS alembic_version;"
uv run alembic upgrade head
```

## 📝 Daily Usage

After initial setup, here's how to start SigmaSight each time:

### Starting the System
```bash
# 1. Ensure Docker Desktop is running (check menu bar for Docker icon)
open -a Docker  # Opens Docker Desktop if not running

# 2. Navigate to project directory
cd /Users/elliottng/CascadeProjects/SigmaSight-BE/sigmasight-backend

# 3. Start the database
docker-compose up -d

# 4. Start the application
uv run uvicorn app.main:app --reload

# OR use the simpler run script if available:
uv run python run.py
```

### Stopping the System
```bash
# 1. Stop the application (in the terminal running uvicorn)
# Press Ctrl+C

# 2. Stop the database
docker-compose down

# 3. Optionally quit Docker Desktop to save resources
```

### Updating the Code
```bash
# Pull latest changes from GitHub
git pull origin main

# Update dependencies if needed
uv sync

# Run any new database migrations
uv run alembic upgrade head
```

## 📋 Quick Commands Reference

```bash
# Navigate to project
cd /Users/elliottng/CascadeProjects/SigmaSight-BE/sigmasight-backend

# Start everything
docker-compose up -d postgres
uv run uvicorn app.main:app --reload

# Stop everything
pkill -f uvicorn
docker-compose down

# View logs
docker logs -f $(docker ps -qf "name=postgres")  # Database logs
tail -f logs/app.log  # Application logs (if configured)

# Database access
docker exec -it $(docker ps -qf "name=postgres") psql -U sigmasight -d sigmasight_db

# Update from GitHub
git pull
uv sync
uv run alembic upgrade head

# Seed demo users
uv run python scripts/seed_demo_users.py

# Run authentication tests
uv run python scripts/test_auth.py

# Reset everything (WARNING: Deletes all data)
docker-compose down -v
rm -rf .venv
rm .env
```

## ✅ Installation Complete Checklist

Run this final verification:
```bash
echo "=== SigmaSight Installation Status ==="
echo -n "✓ Python 3.11+: "; python3 --version
echo -n "✓ UV installed: "; uv --version
echo -n "✓ Docker running: "; docker ps > /dev/null 2>&1 && echo "Yes" || echo "No"
echo -n "✓ PostgreSQL running: "; docker ps | grep -q postgres && echo "Yes" || echo "No"
echo -n "✓ .env configured: "; [ -f .env ] && echo "Yes" || echo "No"
echo -n "✓ Dependencies installed: "; [ -d .venv ] && echo "Yes" || echo "No"
echo -n "✓ API accessible: "; curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "Yes" || echo "No"
echo "===================================="
```

If all checks show "Yes", the installation is complete and ready for development testing.

## 💡 Tips for AI Agents

- Always verify Docker is running before database operations
- Use absolute paths when navigating directories
- Check for existing processes on ports before starting services
- Save state between sessions by documenting completed steps
- Run verification commands after each major step
- When errors occur, check logs before attempting fixes

## 📚 Additional Resources

- API Documentation: http://localhost:8000/docs (when server is running)
- Interactive API Testing: http://localhost:8000/redoc
- Project README: [README.md](README.md)
- Testing Guide: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Windows Setup: [WINDOWS_SETUP_GUIDE.md](WINDOWS_SETUP_GUIDE.md)

## 📞 Notes for Human Supervision

If the AI agent encounters issues it cannot resolve:
1. Check Docker Desktop is running (whale icon in menu bar)
2. Verify network connectivity for package downloads
3. Ensure sufficient disk space (at least 4GB free)
4. Check that no security software is blocking installations
5. Review error messages in both terminal and Docker logs

## ⚠️ Implementation Notes

### Demo User Credentials
The current implementation uses:
- Password: `demo12345` (as implemented in seed_demo_users.py)
- Note: Design docs originally specified `demo123`, but implementation uses `demo12345`

### User Model
- The User model uses `email` and `full_name` fields (no separate username field)
- Each user has exactly one portfolio (enforced by unique constraint)
- Authentication is handled via JWT tokens (stateless)

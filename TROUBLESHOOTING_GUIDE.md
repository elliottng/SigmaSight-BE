# SigmaSight Troubleshooting Guide

**Version**: 1.0  
**Last Updated**: August 26, 2025  
**Support Level**: Production Ready  

## Quick Reference

### Service Health Check Commands

```bash
# Backend API health
curl http://localhost:8001/docs

# GPT Agent health  
curl http://localhost:8888/health

# Frontend application
curl http://localhost:3008

# Database connectivity
cd backend && python -c "from app.database import get_async_session; print('DB OK')"
```

### Emergency Service Restart

```bash
# Stop all services
pkill -f "python run.py"
pkill -f "next"
pkill -f "node.*8888"

# Restart in order
cd backend && uv run python run.py &
cd ../gptagent && npm run dev &
cd ../frontend && npm run dev &
```

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Service-Specific Troubleshooting](#service-specific-troubleshooting)
3. [Database Issues](#database-issues)
4. [Performance Problems](#performance-problems)
5. [API Integration Issues](#api-integration-issues)
6. [Deployment Problems](#deployment-problems)
7. [Data Quality Issues](#data-quality-issues)
8. [Security and Authentication](#security-and-authentication)
9. [Recovery Procedures](#recovery-procedures)
10. [Diagnostic Tools](#diagnostic-tools)

---

## Common Issues

### 1. Application Won't Load

**Symptoms:**
- Browser shows "This site can't be reached"
- Blank page with loading spinner
- Connection refused errors

**Diagnosis:**
```bash
# Check all service ports
netstat -tulpn | grep -E ":(3008|8001|8888|5432)"

# Expected output:
# tcp6  0  0  :::3008  :::*  LISTEN  12345/node (Frontend)
# tcp6  0  0  :::8001  :::*  LISTEN  12346/python (Backend)  
# tcp6  0  0  :::8888  :::*  LISTEN  12347/node (GPT Agent)
# tcp   0  0  127.0.0.1:5432  :::*  LISTEN  12348/postgres
```

**Solutions:**

**Step 1: Verify Service Status**
```bash
# Check process status
ps aux | grep -E "(run.py|next|node.*8888|postgres)"

# If services missing, start them:
cd backend && uv run python run.py &
cd ../gptagent && npm run dev &
cd ../frontend && npm run dev &
```

**Step 2: Check Port Conflicts**
```bash
# Find what's using ports
lsof -i :3008  # Frontend port
lsof -i :8001  # Backend port  
lsof -i :8888  # GPT Agent port

# Kill conflicting processes if needed
kill -9 <PID>
```

**Step 3: Verify Firewall Settings**
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 3008
sudo ufw allow 8001
sudo ufw allow 8888

# Windows
# Check Windows Firewall in Control Panel
# Add inbound rules for ports 3008, 8001, 8888
```

### 2. Services Start But No Data

**Symptoms:**
- Dashboard shows "No data available"
- Empty portfolio lists
- API returns empty results

**Diagnosis:**
```bash
# Check database connectivity
cd backend
python -c "
import asyncio
from sqlalchemy import select, func
from app.database import get_async_session
from app.models.users import Portfolio

async def check():
    try:
        async with get_async_session() as db:
            count = await db.execute(select(func.count(Portfolio.id)))
            print(f'Found {count.scalar()} portfolios in database')
    except Exception as e:
        print(f'Database error: {e}')

asyncio.run(check())
"
```

**Solutions:**

**Step 1: Verify Database Connection**
```bash
# Test direct database connection
psql -h localhost -p 5432 -U sigmasight -d sigmasight_db -c "SELECT COUNT(*) FROM portfolios;"

# If connection fails:
# - Check PostgreSQL is running
# - Verify connection string in .env
# - Check database credentials
```

**Step 2: Seed Demo Data**
```bash
cd backend

# Reset and seed database
python scripts/reset_and_seed.py seed

# Verify seeding worked
python -c "
import asyncio
from sqlalchemy import select
from app.database import get_async_session  
from app.models.users import Portfolio

async def verify():
    async with get_async_session() as db:
        result = await db.execute(select(Portfolio))
        portfolios = result.scalars().all()
        for p in portfolios:
            print(f'Portfolio: {p.name}')

asyncio.run(verify())
"
```

**Step 3: Check API Endpoints**
```bash
# Test backend API directly
curl http://localhost:8001/api/v1/reports/portfolios

# Expected: JSON response with portfolio list
# If empty or error, check backend logs
```

### 3. AI Chat Not Responding

**Symptoms:**
- Chat messages sent but no response
- "Thinking..." indicator never completes
- Error messages in chat interface

**Diagnosis:**
```bash
# Check GPT Agent service
curl http://localhost:8888/health
# Expected: {"status": "ok"}

# Check GPT Agent logs
# Look for Node.js console output with errors

# Check OpenAI API key
cd gptagent
echo $OPENAI_API_KEY
# Should show your API key
```

**Solutions:**

**Step 1: Verify GPT Agent Service**
```bash
# Restart GPT Agent service
pkill -f "node.*8888"
cd gptagent
npm run dev

# Should see:
# Server ready at http://localhost:8888
```

**Step 2: Check OpenAI API Key**
```bash
# Test API key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# If this fails, check/update your OpenAI API key
nano gptagent/apps/api/.env
```

**Step 3: Verify Backend Integration**
```bash
# Test GPT Agent -> Backend communication
curl -X POST http://localhost:8888/analyze \
     -H "Content-Type: application/json" \
     -d '{"message": "test", "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"}'
```

### 4. Slow Performance

**Symptoms:**
- Pages load slowly (>5 seconds)
- API responses are delayed
- Database queries timeout

**Diagnosis:**
```bash
# Check system resources
htop  # or top on systems without htop
df -h  # Check disk space
free -h  # Check memory usage

# Check database performance
cd backend
psql -U sigmasight -d sigmasight_db -c "
SELECT query, mean_exec_time, calls, total_exec_time 
FROM pg_stat_statements 
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC 
LIMIT 10;
"
```

**Solutions:**

**Step 1: Database Optimization**
```bash
# Update database statistics
psql -U sigmasight -d sigmasight_db -c "ANALYZE;"

# Check for missing indexes
cd backend
python -c "
from app.database import get_async_session
from sqlalchemy import text
import asyncio

async def check_indexes():
    async with get_async_session() as db:
        # Check if critical indexes exist
        result = await db.execute(text('''
            SELECT schemaname, tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
        '''))
        indexes = result.fetchall()
        print(f'Found {len(indexes)} custom indexes')
        for idx in indexes:
            print(f'  {idx.tablename}.{idx.indexname}')

asyncio.run(check_indexes())
"
```

**Step 2: Application-Level Caching**
```bash
# Check if calculation results are cached
cd backend
grep -r "cache" app/calculations/

# Restart services to clear any memory leaks
pkill -f "python run.py"
pkill -f "node.*8888"
pkill -f "next"

# Start services again
cd backend && uv run python run.py &
cd ../gptagent && npm run dev &
cd ../frontend && npm run dev &
```

---

## Service-Specific Troubleshooting

### Backend Service (FastAPI)

#### Startup Issues

**Problem: ModuleNotFoundError**
```bash
# Error: ModuleNotFoundError: No module named 'uvicorn'
# Solution: Always use uv to run Python

# WRONG:
python run.py

# CORRECT:
uv run python run.py
```

**Problem: Database Connection Failed**
```bash
# Check environment variables
cd backend
cat .env | grep DATABASE_URL

# Test connection string manually
psql "postgresql+asyncpg://sigmasight:sigmasight_dev@localhost:5432/sigmasight_db"

# Common fixes:
# 1. Start PostgreSQL: docker-compose up -d
# 2. Check credentials in .env
# 3. Verify database exists: createdb sigmasight_db
```

**Problem: Port Already in Use**
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or change port in run.py:
# uvicorn.run(app, host="0.0.0.0", port=8002)  # Use different port
```

#### Runtime Issues

**Problem: Calculation Errors**
```bash
# Check calculation engine status
cd backend
python -c "
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2
print('Batch orchestrator imported successfully')
"

# Test individual calculations
python scripts/test_calculations.py

# Check for missing data
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def check_data():
    async with get_async_session() as db:
        # Check position data
        result = await db.execute(text('SELECT COUNT(*) FROM positions'))
        print(f'Positions: {result.scalar()}')
        
        # Check market data
        result = await db.execute(text('SELECT COUNT(*) FROM market_data_cache'))
        print(f'Market data points: {result.scalar()}')

asyncio.run(check_data())
"
```

**Problem: API Rate Limiting**
```bash
# Check rate limit configuration
cd backend
grep -r "rate" app/config.py

# Check API key quotas
curl -H "Authorization: Bearer $POLYGON_API_KEY" \
     "https://api.polygon.io/v3/reference/tickers?limit=1"

# Look for rate limit headers in response
```

### Frontend Service (Next.js)

#### Build Issues

**Problem: TypeScript Errors**
```bash
cd frontend

# Check TypeScript configuration
npx tsc --noEmit

# Common fixes:
# 1. Update dependencies
npm update @types/node @types/react @types/react-dom

# 2. Fix type errors in components
npm run type-check

# 3. Skip type checking temporarily (not recommended)
npm run build -- --no-type-check
```

**Problem: Environment Variables Not Found**
```bash
# Check environment file exists
ls -la .env.local

# Verify variables are set
cat .env.local | grep NEXT_PUBLIC

# Environment variables must start with NEXT_PUBLIC_ for client access
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1" >> .env.local
```

#### Runtime Issues

**Problem: API Connection Failures**
```bash
# Test API endpoint directly
curl http://localhost:8001/api/v1/reports/portfolios

# Check browser console for CORS errors
# F12 -> Console tab -> Look for CORS or network errors

# Check Next.js API routes
curl http://localhost:3008/api/chat \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
```

**Problem: Styling Issues**
```bash
cd frontend

# Clear Next.js cache
rm -rf .next

# Rebuild Tailwind CSS
npm run dev

# Check Tailwind configuration
npx tailwindcss --init --check
```

### GPT Agent Service (Node.js)

#### Startup Issues

**Problem: Node.js Version Compatibility**
```bash
# Check Node.js version
node --version
# Should be 18.0 or higher

# Update Node.js if needed
# Using nvm:
nvm install 18
nvm use 18

# Using package manager:
# Ubuntu: sudo apt install nodejs
# macOS: brew upgrade node
```

**Problem: Package Installation Failures**
```bash
cd gptagent

# Clear package cache
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install

# Check for peer dependency warnings
npm ls
```

#### Runtime Issues

**Problem: OpenAI API Failures**
```bash
# Test OpenAI API key directly
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'

# Check API key in environment
cd gptagent/apps/api
echo $OPENAI_API_KEY

# Common issues:
# 1. API key missing or invalid
# 2. Rate limits exceeded
# 3. Insufficient API credits
```

**Problem: Backend Integration Failures**
```bash
# Test backend connectivity from GPT Agent
cd gptagent
curl http://localhost:8001/api/v1/health

# Check authentication
# GPT Agent should use service account or bypass auth for internal calls

# Test full integration
curl -X POST http://localhost:8888/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are my biggest risks?",
       "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
     }'
```

---

## Database Issues

### Connection Problems

**Problem: Connection Refused**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Start PostgreSQL if stopped
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Docker PostgreSQL
docker-compose up -d postgres
```

**Problem: Authentication Failed**
```bash
# Reset PostgreSQL user password
sudo -u postgres psql -c "ALTER USER sigmasight PASSWORD 'new_password';"

# Update .env file with new password
cd backend
nano .env
# DATABASE_URL=postgresql+asyncpg://sigmasight:new_password@localhost:5432/sigmasight_db
```

**Problem: Database Does Not Exist**
```bash
# Create database
sudo -u postgres createdb sigmasight_db

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sigmasight_db TO sigmasight;"

# Apply migrations
cd backend
uv run alembic upgrade head
```

### Data Integrity Issues

**Problem: Missing Tables**
```bash
# Check table existence
psql -U sigmasight -d sigmasight_db -c "\dt"

# Apply missing migrations
cd backend
uv run alembic upgrade head

# If migrations fail, check alembic status
uv run alembic current
uv run alembic history
```

**Problem: Corrupted Data**
```bash
# Check data integrity
psql -U sigmasight -d sigmasight_db -c "
SELECT tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables 
ORDER BY n_tup_ins DESC;
"

# Restore from backup if needed
cd backend
./scripts/restore_database.sh /path/to/backup.sql.gz
```

### Performance Issues

**Problem: Slow Queries**
```bash
# Enable query logging
psql -U postgres -c "ALTER SYSTEM SET log_statement = 'all';"
psql -U postgres -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"  # Log queries >1s
psql -U postgres -c "SELECT pg_reload_conf();"

# Check slow queries
tail -f /var/log/postgresql/postgresql-14-main.log | grep "duration:"

# Analyze query performance
psql -U sigmasight -d sigmasight_db -c "
EXPLAIN ANALYZE SELECT * FROM positions 
WHERE portfolio_id = 'a3209353-9ed5-4885-81e8-d4bbc995f96c';
"
```

**Problem: Index Missing**
```bash
# Check existing indexes
psql -U sigmasight -d sigmasight_db -c "
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"

# Create missing indexes
psql -U sigmasight -d sigmasight_db -c "
CREATE INDEX CONCURRENTLY idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX CONCURRENTLY idx_positions_symbol ON positions(symbol);
CREATE INDEX CONCURRENTLY idx_portfolio_snapshots_date ON portfolio_snapshots(calculation_date DESC);
"
```

---

## Performance Problems

### System Resource Issues

**Problem: High CPU Usage**
```bash
# Check CPU usage by service
htop
# Look for processes: python run.py, node, postgres

# Check specific service CPU usage
ps aux | grep -E "(run.py|node|postgres)" | awk '{print $3, $11}'

# Solutions:
# 1. Restart memory-intensive services
# 2. Optimize database queries
# 3. Implement caching
# 4. Scale horizontally if needed
```

**Problem: Memory Leaks**
```bash
# Monitor memory usage over time
watch -n 5 'free -h && ps aux | grep -E "(python|node)" | head -10'

# Check for memory leaks in Node.js
cd gptagent
node --inspect apps/api/src/index.js
# Use Chrome DevTools to inspect memory usage

# Restart services to clear memory
pkill -f "python run.py" && cd backend && uv run python run.py &
pkill -f "node.*8888" && cd gptagent && npm run dev &
```

**Problem: Disk Space Full**
```bash
# Check disk usage
df -h

# Find large files
du -ah /opt/sigmasight | sort -hr | head -20

# Clean up logs
cd backend
find logs/ -name "*.log" -mtime +7 -delete

# Clean up old reports (if not needed)
find reports/ -name "*" -mtime +30 -delete
```

### Application Performance

**Problem: Slow API Responses**
```bash
# Test API response times
time curl http://localhost:8001/api/v1/reports/portfolios

# Should complete in <1 second for cached data
# If >3 seconds, investigate:

# 1. Database performance
cd backend
psql -U sigmasight -d sigmasight_db -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 5;
"

# 2. Application profiling
python -m cProfile -s tottime run.py > performance_profile.txt
```

**Problem: Frontend Loading Slowly**
```bash
cd frontend

# Check bundle size
npm run analyze

# Optimize images and assets
# Check for unused dependencies
npx depcheck

# Enable Next.js speed insights
npm install @next/bundle-analyzer
```

---

## API Integration Issues

### Market Data Provider Issues

**Problem: Polygon API Failures**
```bash
# Test API key
curl -H "Authorization: Bearer $POLYGON_API_KEY" \
     "https://api.polygon.io/v3/reference/tickers/AAPL"

# Check rate limits
curl -I -H "Authorization: Bearer $POLYGON_API_KEY" \
     "https://api.polygon.io/v3/reference/tickers/AAPL"
# Look for X-RateLimit-* headers

# Common solutions:
# 1. Check API key is valid and not expired
# 2. Upgrade to higher tier if rate limited
# 3. Implement request queuing/throttling
```

**Problem: Missing Market Data**
```bash
# Check market data cache
cd backend
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def check_market_data():
    async with get_async_session() as db:
        # Check data coverage
        result = await db.execute(text('''
            SELECT symbol, COUNT(*) as data_points,
                   MIN(date) as earliest,
                   MAX(date) as latest
            FROM market_data_cache 
            GROUP BY symbol
            ORDER BY data_points DESC
            LIMIT 10
        '''))
        
        for row in result:
            print(f'{row.symbol}: {row.data_points} points ({row.earliest} to {row.latest})')

asyncio.run(check_market_data())
"

# Backfill missing data
python scripts/backfill_market_data.py
```

### Authentication Issues

**Problem: JWT Token Expired**
```bash
# Check token expiration
cd backend
python -c "
import jwt
from datetime import datetime

# Replace with actual token
token = 'your-jwt-token-here'
try:
    decoded = jwt.decode(token, options={'verify_signature': False})
    exp = datetime.fromtimestamp(decoded['exp'])
    print(f'Token expires: {exp}')
    print(f'Current time: {datetime.now()}')
    print(f'Expired: {exp < datetime.now()}')
except Exception as e:
    print(f'Token error: {e}')
"

# Generate new token
curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@sigmasight.com", "password": "demo123"}'
```

---

## Deployment Problems

### Docker Issues

**Problem: Container Won't Start**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs gpt-agent

# Check container status
docker-compose ps

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

**Problem: Volume Mount Issues**
```bash
# Check volume mounts
docker-compose exec backend ls -la /app
docker-compose exec backend ls -la /app/logs

# Fix permission issues
sudo chown -R $(id -u):$(id -g) logs/
sudo chown -R $(id -u):$(id -g) reports/
```

### Environment Configuration

**Problem: Environment Variables Not Set**
```bash
# Check environment files exist
ls -la .env*

# Verify variables in containers
docker-compose exec backend env | grep -E "(DATABASE|API_KEY)"
docker-compose exec gpt-agent env | grep -E "(OPENAI|PORT)"
docker-compose exec frontend env | grep "NEXT_PUBLIC"

# Common issues:
# 1. .env file missing
# 2. Variables not prefixed correctly (NEXT_PUBLIC_ for frontend)
# 3. Docker not loading .env file
```

---

## Data Quality Issues

### Calculation Problems

**Problem: Missing Greeks**
```bash
# Check options positions
cd backend
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def check_options():
    async with get_async_session() as db:
        result = await db.execute(text('''
            SELECT p.symbol, p.position_type, pg.delta, pg.gamma, pg.theta, pg.vega
            FROM positions p
            LEFT JOIN position_greeks pg ON p.id = pg.position_id
            WHERE p.position_type IN ('LC', 'LP', 'SC', 'SP')
            LIMIT 10
        '''))
        
        for row in result:
            greeks_status = 'Present' if row.delta is not None else 'Missing'
            print(f'{row.symbol} ({row.position_type}): Greeks {greeks_status}')

asyncio.run(check_options())
"

# Recalculate Greeks
python scripts/calculate_greeks.py
```

**Problem: Factor Analysis Failing**
```bash
# Check factor data availability
cd backend
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def check_factors():
    async with get_async_session() as db:
        result = await db.execute(text('''
            SELECT factor_name, COUNT(*) as exposures
            FROM position_factor_exposures
            GROUP BY factor_name
            ORDER BY exposures DESC
        '''))
        
        for row in result:
            print(f'{row.factor_name}: {row.exposures} exposures')

asyncio.run(check_factors())
"

# Run factor analysis
python scripts/run_factor_analysis.py
```

### Data Validation

**Problem: Invalid Position Data**
```bash
# Check for data anomalies
cd backend
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def validate_positions():
    async with get_async_session() as db:
        # Check for negative quantities in LONG positions
        result = await db.execute(text('''
            SELECT symbol, quantity, position_type
            FROM positions
            WHERE position_type = 'LONG' AND quantity < 0
            LIMIT 5
        '''))
        
        anomalies = result.fetchall()
        if anomalies:
            print('Data anomalies found:')
            for row in anomalies:
                print(f'  {row.symbol}: {row.quantity} shares ({row.position_type})')
        else:
            print('No data anomalies found')

asyncio.run(validate_positions())
"
```

---

## Security and Authentication

### Authentication Problems

**Problem: Login Failures**
```bash
# Test user authentication
curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@sigmasight.com", "password": "demo123"}'

# Check user exists
cd backend
python -c "
import asyncio
from app.database import get_async_session
from sqlalchemy import text

async def check_users():
    async with get_async_session() as db:
        result = await db.execute(text('SELECT email FROM users LIMIT 5'))
        users = result.fetchall()
        for user in users:
            print(f'User: {user.email}')

asyncio.run(check_users())
"

# Reset demo user password if needed
python scripts/reset_demo_users.py
```

### API Security

**Problem: Rate Limiting Issues**
```bash
# Check rate limit configuration
cd backend
grep -r "rate" app/config.py

# Test rate limits
for i in {1..10}; do
    curl -w "Status: %{http_code}, Time: %{time_total}s\n" \
         http://localhost:8001/api/v1/health
done

# Should see 429 status codes if rate limiting works
```

---

## Recovery Procedures

### Service Recovery

**Full System Recovery:**
```bash
#!/bin/bash
# Emergency recovery script

echo "Starting SigmaSight emergency recovery..."

# Stop all services
pkill -f "python run.py"
pkill -f "next"
pkill -f "node.*8888"
echo "Services stopped"

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%"
    # Clean up logs
    find . -name "*.log" -mtime +7 -delete
fi

# Check database
if ! pg_isready -h localhost -p 5432; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql || docker-compose up -d postgres
    sleep 10
fi

# Restart services in order
echo "Starting Backend..."
cd backend && uv run python run.py > ../recovery.log 2>&1 &
sleep 15

echo "Starting GPT Agent..."
cd ../gptagent && npm run dev >> ../recovery.log 2>&1 &
sleep 10

echo "Starting Frontend..."  
cd ../frontend && npm run dev >> ../recovery.log 2>&1 &
sleep 10

# Verify services
echo "Verifying service health..."
sleep 5

curl -s http://localhost:8001/health && echo "✅ Backend OK" || echo "❌ Backend Failed"
curl -s http://localhost:8888/health && echo "✅ GPT Agent OK" || echo "❌ GPT Agent Failed"  
curl -s http://localhost:3008 > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend Failed"

echo "Recovery procedure completed. Check recovery.log for details."
```

### Database Recovery

**Database Restore from Backup:**
```bash
#!/bin/bash
# Database recovery script

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo "Available backups:"
    ls -la backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

echo "Starting database recovery from $BACKUP_FILE"

# Stop dependent services
pkill -f "python run.py"
pkill -f "node.*8888"

# Backup current database
pg_dump -U sigmasight -h localhost sigmasight_db > "backup_before_recovery_$(date +%Y%m%d_%H%M%S).sql"

# Drop and recreate database
dropdb -U postgres sigmasight_db
createdb -U postgres sigmasight_db
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sigmasight_db TO sigmasight;"

# Restore from backup
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql -U sigmasight -d sigmasight_db
else
    psql -U sigmasight -d sigmasight_db -f "$BACKUP_FILE"
fi

# Verify restoration
PORTFOLIO_COUNT=$(psql -U sigmasight -d sigmasight_db -t -c "SELECT COUNT(*) FROM portfolios;")
echo "Restored $PORTFOLIO_COUNT portfolios"

# Restart services
cd backend && uv run python run.py &
sleep 10
cd ../gptagent && npm run dev &

echo "Database recovery completed"
```

---

## Diagnostic Tools

### Health Check Script

**Comprehensive System Check:**
```bash
#!/bin/bash
# System health check script

echo "SigmaSight System Health Check"
echo "=============================="
date
echo

# Check system resources
echo "System Resources:"
echo "-----------------"
echo "💾 Disk usage: $(df -h / | awk 'NR==2{print $5}')"
echo "🧠 Memory usage: $(free -h | awk 'NR==2{print $3"/"$2}')"
echo "⚡ Load average: $(uptime | awk -F'load average:' '{print $2}')"
echo

# Check service ports
echo "Service Ports:"
echo "--------------"
echo "🔌 PostgreSQL (5432): $(nc -z localhost 5432 && echo 'Open' || echo 'Closed')"
echo "🔌 Backend (8001): $(nc -z localhost 8001 && echo 'Open' || echo 'Closed')"
echo "🔌 GPT Agent (8888): $(nc -z localhost 8888 && echo 'Open' || echo 'Closed')"
echo "🔌 Frontend (3008): $(nc -z localhost 3008 && echo 'Open' || echo 'Closed')"
echo

# Check service health
echo "Service Health:"
echo "---------------"
curl -s http://localhost:8001/health >/dev/null && echo "✅ Backend API: Healthy" || echo "❌ Backend API: Unhealthy"
curl -s http://localhost:8888/health >/dev/null && echo "✅ GPT Agent: Healthy" || echo "❌ GPT Agent: Unhealthy"
curl -s http://localhost:3008 >/dev/null && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Unhealthy"
echo

# Check database
echo "Database Status:"
echo "----------------"
if pg_isready -h localhost -p 5432; then
    echo "✅ PostgreSQL: Running"
    PORTFOLIO_COUNT=$(psql -U sigmasight -d sigmasight_db -t -c "SELECT COUNT(*) FROM portfolios;" 2>/dev/null)
    if [ ! -z "$PORTFOLIO_COUNT" ]; then
        echo "📊 Portfolios: $PORTFOLIO_COUNT"
        POSITION_COUNT=$(psql -U sigmasight -d sigmasight_db -t -c "SELECT COUNT(*) FROM positions;" 2>/dev/null)
        echo "📈 Positions: $POSITION_COUNT"
    else
        echo "❌ Database: Connection failed"
    fi
else
    echo "❌ PostgreSQL: Not running"
fi
echo

# Check log files
echo "Recent Errors:"
echo "--------------"
if [ -f "backend/logs/sigmasight.log" ]; then
    ERROR_COUNT=$(grep -i "error" backend/logs/sigmasight.log | tail -5 | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "⚠️  Found $ERROR_COUNT recent errors in backend log:"
        grep -i "error" backend/logs/sigmasight.log | tail -3
    else
        echo "✅ No recent errors in backend log"
    fi
else
    echo "ℹ️  Backend log file not found"
fi
echo

echo "Health check completed."
echo "For detailed logs, check:"
echo "- Backend: backend/logs/sigmasight.log"
echo "- System: journalctl -f (Linux) or Console.app (macOS)"
```

### Performance Monitor

**Performance Monitoring Script:**
```bash
#!/bin/bash
# Performance monitoring script

echo "SigmaSight Performance Monitor"
echo "=============================="

while true; do
    clear
    date
    echo
    
    # CPU and Memory
    echo "System Resources:"
    echo "-----------------"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo
    
    # Service-specific resource usage
    echo "Service Resource Usage:"
    echo "-----------------------"
    ps aux | grep -E "(python run.py|node.*8888|next)" | grep -v grep | while read line; do
        USER=$(echo $line | awk '{print $1}')
        PID=$(echo $line | awk '{print $2}')
        CPU=$(echo $line | awk '{print $3}')
        MEM=$(echo $line | awk '{print $4}')
        CMD=$(echo $line | awk '{print $11}' | cut -d'/' -f1)
        echo "$CMD (PID $PID): CPU $CPU%, Memory $MEM%"
    done
    echo
    
    # Database connections
    echo "Database Connections:"
    echo "---------------------"
    DB_CONNECTIONS=$(psql -U sigmasight -d sigmasight_db -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null)
    echo "Active connections: ${DB_CONNECTIONS:-'Unable to connect'}"
    echo
    
    # API response times
    echo "API Response Times:"
    echo "-------------------"
    BACKEND_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8001/health)
    GPT_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8888/health)
    FRONTEND_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:3008)
    
    echo "Backend: ${BACKEND_TIME}s"
    echo "GPT Agent: ${GPT_TIME}s" 
    echo "Frontend: ${FRONTEND_TIME}s"
    
    sleep 5
done
```

### Log Analyzer

**Log Analysis Script:**
```bash
#!/bin/bash
# Log analysis script

LOG_FILE="backend/logs/sigmasight.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "Log file not found: $LOG_FILE"
    exit 1
fi

echo "SigmaSight Log Analysis"
echo "======================"
echo "Analyzing: $LOG_FILE"
echo "File size: $(du -h "$LOG_FILE" | cut -f1)"
echo

# Error summary
echo "Error Summary (Last 24 Hours):"
echo "--------------------------------"
grep -i "error" "$LOG_FILE" | grep "$(date '+%Y-%m-%d')" | head -10

echo
echo "Warning Summary (Last 24 Hours):"
echo "----------------------------------"
grep -i "warning" "$LOG_FILE" | grep "$(date '+%Y-%m-%d')" | head -10

echo
echo "Request Summary (Last Hour):"
echo "-----------------------------"
LAST_HOUR=$(date -d '1 hour ago' '+%H')
grep "$LAST_HOUR:" "$LOG_FILE" | grep -E "(GET|POST)" | wc -l | xargs echo "Total requests:"

# Most frequent errors
echo
echo "Most Frequent Error Types:"
echo "---------------------------"
grep -i "error" "$LOG_FILE" | sed 's/.*ERROR/ERROR/' | sort | uniq -c | sort -nr | head -5

# Response time analysis
echo
echo "Slow Requests (>2 seconds):"
echo "-----------------------------"
grep -E "took [2-9][0-9]*\.[0-9]+s" "$LOG_FILE" | tail -5
```

---

## Getting Help

### Information to Collect

When reporting issues, collect the following information:

**System Information:**
```bash
# System details
uname -a
python --version
node --version
psql --version

# Service status
curl -I http://localhost:8001/health
curl -I http://localhost:8888/health
curl -I http://localhost:3008

# Recent logs
tail -50 backend/logs/sigmasight.log
```

**Error Details:**
- Exact error message
- Steps to reproduce
- Time of occurrence
- Browser console errors (F12 → Console)
- Screenshots if applicable

### Contact Information

**Internal Support:**
- Development Team: Contact via internal channels
- System Administrator: For infrastructure issues
- Database Administrator: For data-related problems

**Documentation Resources:**
- Complete Implementation Guide
- API Documentation  
- User Guide
- Deployment Guide

### Emergency Contacts

**Critical System Failures:**
1. Run emergency recovery script
2. Contact system administrator immediately
3. Document incident details
4. Follow disaster recovery procedures

**Data Loss Scenarios:**
1. Stop all services immediately
2. Do not write to database
3. Contact database administrator
4. Initiate backup recovery procedures

---

**Troubleshooting Guide Status**: Production Ready  
**Last Updated**: August 26, 2025  
**Next Review**: Quarterly or after major incidents  
**Maintenance**: Update after system changes or new issue patterns discovered
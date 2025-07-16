# Testing Guide - Market Data Implementation

This guide covers how to test the Market Data Service implementations we just created.

## 🚀 Quick Start Testing

### 1. Prerequisites

Make sure you have:
- ✅ PostgreSQL running
- ✅ Database migrated (`alembic upgrade head`)
- ✅ Dependencies installed (`uv sync`)
- ✅ Polygon.io API key in `.env` file

### 2. Set Up Your API Key

Add your Polygon.io API key to the `.env` file:
```bash
# In .env file
POLYGON_API_KEY=your_actual_api_key_here
```

### 3. Quick API Connection Test

```bash
# Quick test of API connections
python scripts/test_market_data.py quick
```

## 🧪 Testing Methods

### Method 1: Unit Tests (Pytest)

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_market_data_service.py -v

# Run specific test categories
pytest tests/test_market_data_service.py::TestMarketDataService -v
pytest tests/test_market_data_service.py::TestMarketDataEndpoints -v

# Run integration tests (requires API key)
pytest tests/test_market_data_service.py -m integration -v
```

### Method 2: Manual Service Testing

Test the service directly:

```bash
# Comprehensive test of all components
python scripts/test_market_data.py

# This will test:
# - Polygon.io connection and data fetching
# - YFinance GICS data
# - Historical data retrieval
# - Options chain data
# - Database integration
```

### Method 3: API Endpoint Testing

Test the HTTP endpoints:

```bash
# Start the server first
uvicorn app.main:app --reload

# In another terminal, test the API endpoints
./scripts/test_api_endpoints.sh

# Or specify a different URL
./scripts/test_api_endpoints.sh http://localhost:8000
```

### Method 4: Manual API Testing with curl

```bash
# 1. Start the server
uvicorn app.main:app --reload

# 2. Create a demo user (if not exists)
python scripts/seed_demo_users.py

# 3. Get auth token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo_growth@sigmasight.com", "password": "demopassword123"}'

# 4. Use the token from response for authenticated requests
TOKEN="your_token_here"

# 5. Test market data endpoints
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/market-data/prices/AAPL"

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/market-data/current-prices?symbols=AAPL&symbols=MSFT"
```

## 📊 Expected Test Results

### ✅ Successful Test Outputs

**API Connection Test:**
```
✅ Polygon.io connection successful
   AAPL current price: $175.43

✅ YFinance connection successful
   AAPL sector: Technology
   AAPL industry: Consumer Electronics
```

**Database Integration:**
```
✅ Database connection successful
   Cached price check completed for ['AAPL']
   Found cached price for AAPL: $175.43
```

**API Endpoint Response:**
```json
{
  "symbol": "AAPL",
  "date": "2024-01-15",
  "open": 174.50,
  "high": 176.20,
  "low": 174.10,
  "close": 175.43,
  "volume": 52469400,
  "sector": "Technology",
  "industry": "Consumer Electronics"
}
```

### ⚠️ Common Issues and Solutions

**No API Key:**
```
❌ No Polygon API key configured in .env file
```
**Solution:** Add `POLYGON_API_KEY=your_key_here` to `.env`

**Database Connection Error:**
```
❌ Database integration failed: connection to server failed
```
**Solution:** Start PostgreSQL and run `alembic upgrade head`

**Authentication Required:**
```
🔒 Status: 401 (Authentication required)
```
**Solution:** Run `python scripts/seed_demo_users.py` first

## 🔍 Testing Specific Features

### Test Price Data Fetching
```python
# Direct service test
from app.services.market_data_service import market_data_service
import asyncio

async def test_prices():
    prices = await market_data_service.fetch_current_prices(['AAPL', 'MSFT'])
    print(f"Current prices: {prices}")

asyncio.run(test_prices())
```

### Test Historical Data
```bash
# Via API endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/market-data/prices/AAPL?days_back=30"
```

### Test Batch Processing
```python
# Test the daily sync job
from app.batch.market_data_sync import sync_market_data
import asyncio

asyncio.run(sync_market_data())
```

### Test Options Chain
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/market-data/options/AAPL"
```

## 🎯 Performance Testing

### Load Testing with Multiple Symbols
```python
# Test bulk fetching
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
prices = await market_data_service.fetch_current_prices(symbols)
```

### Database Caching Performance
```python
# Test cache vs API performance
import time

# First call (should hit API)
start = time.time()
await service.update_market_data_cache(db, ['AAPL'])
api_time = time.time() - start

# Second call (should use cache)
start = time.time()
cached = await service.get_cached_prices(db, ['AAPL'])
cache_time = time.time() - start

print(f"API call: {api_time:.2f}s, Cache lookup: {cache_time:.2f}s")
```

## 🐛 Debugging Tips

### Enable Debug Logging
```python
# In your test script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Rate Limits
```python
# The service includes rate limiting delays
# Check logs for rate limit warnings
```

### Verify Database State
```sql
-- Check cached data
SELECT symbol, date, close, sector 
FROM market_data_cache 
ORDER BY symbol, date DESC 
LIMIT 10;
```

## 📈 Next Steps

After successful testing:

1. **Ready for Production:**
   - All tests pass ✅
   - API key configured ✅
   - Database integration working ✅

2. **Ready for Section 1.4:**
   - Market data available ✅
   - Can proceed with calculation engine ✅

3. **Optional Improvements:**
   - Implement Redis caching
   - Add WebSocket real-time updates
   - Set up monitoring/alerting

## 🆘 Getting Help

If tests fail:

1. Check the logs: `tail -f logs/sigmasight.log`
2. Verify environment: `python -c "from app.config import settings; print(settings.POLYGON_API_KEY[:10] + '...')"`
3. Test database: `python -c "from app.core.database import engine; print('DB configured')"`
4. Check dependencies: `uv sync`

---

**Ready to test?** Start with: `python scripts/test_market_data.py quick`
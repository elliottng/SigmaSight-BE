# MARKET DATA API MIGRATION PLAN

## Goal
Choose a cost-effective solution that adds mutual fund holdings data while keeping the existing system mostly intact.

## Quick Test Plan (2-3 days)

### Test Portfolio
```python
# ALL tickers from Ben's Mock Portfolios - comprehensive test
TEST_ITEMS = {
    # Portfolio 1: Balanced Individual Investor
    "portfolio_1_stocks": [
        "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", 
        "NVDA", "JNJ", "JPM", "V"
    ],
    "portfolio_1_mutual_funds": [
        "FXNAX",  # Fidelity US Large Cap Growth
        "FCNTX",  # Fidelity Contrafund
        "FMAGX",  # Fidelity Magellan
        "VTIAX",  # Vanguard Total International
    ],
    "portfolio_1_etfs": ["VTI", "BND", "VNQ"],
    
    # Portfolio 2: Sophisticated High Net Worth
    "portfolio_2_stocks": [
        "SPY", "QQQ", "AAPL", "MSFT", "AMZN", 
        "GOOGL", "BRK.B", "JPM", "JNJ", "NVDA", 
        "META", "UNH", "V", "HD", "PG"
    ],
    "portfolio_2_etfs": ["GLD", "DJP"],  # Alternative investments
    
    # Portfolio 3: Long/Short Equity Hedge Fund Style
    "portfolio_3_longs": [
        "NVDA", "MSFT", "AAPL", "GOOGL", "META", 
        "AMZN", "TSLA", "AMD", "BRK.B", "JPM", 
        "JNJ", "UNH", "V"
    ],
    "portfolio_3_shorts": [
        "NFLX", "SHOP", "ZOOM", "PELOTON", "ROKU",
        "XOM", "F", "GE", "C"
    ],
    "portfolio_3_options": [
        # Long Options
        "SPY 2025-09-19 460C",
        "QQQ 2025-08-15 420C", 
        "VIX 2025-07-16 25C",
        "NVDA 2025-10-17 800C",
        # Short Options
        "AAPL 2025-08-15 200P",
        "MSFT 2025-09-19 380P",
        "TSLA 2025-08-15 300C",
        "META 2025-09-19 450P"
    ]
}

# Consolidated unique list for testing
ALL_STOCKS = list(set(
    TEST_ITEMS["portfolio_1_stocks"] + 
    TEST_ITEMS["portfolio_2_stocks"] + 
    TEST_ITEMS["portfolio_3_longs"] + 
    TEST_ITEMS["portfolio_3_shorts"]
))

ALL_MUTUAL_FUNDS = TEST_ITEMS["portfolio_1_mutual_funds"]

ALL_ETFS = list(set(
    TEST_ITEMS["portfolio_1_etfs"] + 
    TEST_ITEMS["portfolio_2_etfs"]
))

ALL_OPTIONS = TEST_ITEMS["portfolio_3_options"]
```

### Three Options to Test

1. **EODHD + Keep Polygon** (~$130/month)
2. **FMP + Keep Polygon** (~$180/month)  
3. **TwelveData Only** (~$99/month)

### Test Scripts
Create directory: `scripts/test_api_providers/`

#### 1. Main Test Script: `test_new_apis.py`
```python
import asyncio
import json
import csv
from datetime import datetime
from decimal import Decimal
import pandas as pd

async def test_provider(provider_name, api_key, output_dir="./api_test_results"):
    """Comprehensive test of all required features"""
    
    print(f"\n{'='*50}")
    print(f"Testing {provider_name}")
    print(f"{'='*50}")
    
    results = {
        "provider": provider_name,
        "test_date": datetime.now().isoformat(),
        "stocks": {},
        "mutual_funds": {},
        "options": {},
        "summary": {}
    }
    
    # Test 1: Stock Prices (test all unique stocks)
    print("\n1. Testing Stock Prices...")
    print(f"   Testing {len(ALL_STOCKS)} unique stocks from all portfolios")
    
    stocks_to_test = ALL_STOCKS[:5]  # Test first 5 for detail
    for symbol in stocks_to_test:
        try:
            prices = await fetch_stock_prices(provider_name, symbol)
            print(f"  ✓ {symbol}: {len(prices)} days of history")
            results["stocks"][symbol] = {"success": True, "days": len(prices)}
        except Exception as e:
            print(f"  ✗ {symbol}: {str(e)}")
            results["stocks"][symbol] = {"success": False, "error": str(e)}
    
    # Quick test remaining stocks
    remaining_stocks = ALL_STOCKS[5:]
    success_count = 0
    for symbol in remaining_stocks:
        try:
            prices = await fetch_stock_prices(provider_name, symbol)
            success_count += 1
            results["stocks"][symbol] = {"success": True, "days": len(prices)}
        except:
            results["stocks"][symbol] = {"success": False}
    
    print(f"  → Tested {len(ALL_STOCKS)} total stocks: {success_count + len(stocks_to_test)} successful")
    
    # Test 2: Mutual Fund Holdings (CRITICAL - export all)
    print("\n2. Testing Mutual Fund Holdings...")
    for symbol in ALL_MUTUAL_FUNDS:
        try:
            holdings = await fetch_fund_holdings(provider_name, symbol)
            print(f"  ✓ {symbol}: {len(holdings)} holdings found")
            
            # Export to CSV for manual review
            export_holdings_to_csv(symbol, holdings, provider_name, output_dir)
            
            # Analyze holdings quality
            total_weight = sum(h.get('weight', 0) for h in holdings)
            has_names = all(h.get('name') for h in holdings[:10])
            
            results["mutual_funds"][symbol] = {
                "success": True,
                "count": len(holdings),
                "total_weight": total_weight,
                "has_security_names": has_names,
                "sample": holdings[:3] if holdings else []
            }
        except Exception as e:
            print(f"  ✗ {symbol}: {str(e)}")
            results["mutual_funds"][symbol] = {"success": False, "error": str(e)}
    
    # Test 2b: ETF Holdings (also important)
    print("\n2b. Testing ETF Holdings...")
    for symbol in ALL_ETFS:
        try:
            holdings = await fetch_fund_holdings(provider_name, symbol)
            print(f"  ✓ {symbol}: {len(holdings)} holdings found")
            export_holdings_to_csv(symbol, holdings, provider_name, output_dir)
            results["etfs"][symbol] = {"success": True, "count": len(holdings)}
        except Exception as e:
            print(f"  ✗ {symbol}: {str(e)}")
            results["etfs"][symbol] = {"success": False, "error": str(e)}
    
    # Test 3: Options Chains (test sample from Portfolio 3)
    print("\n3. Testing Options Chains...")
    for option_str in ALL_OPTIONS[:4]:  # Test first 4 in detail
        parts = option_str.split()
        symbol = parts[0]
        expiry = parts[1]
        strike_type = parts[2]  # e.g., "460C" or "200P"
        
        try:
            chain = await fetch_options_chain(provider_name, symbol, expiry)
            print(f"  ✓ {symbol} {expiry}: {len(chain)} contracts found")
            
            # Check data quality
            has_greeks = any(c.get('delta') for c in chain[:10])
            has_iv = any(c.get('implied_volatility') for c in chain[:10])
            
            results["options"][f"{symbol}_{expiry}"] = {
                "success": True,
                "contracts": len(chain),
                "has_greeks": has_greeks,
                "has_iv": has_iv,
                "specific_strike": strike_type
            }
        except Exception as e:
            print(f"  ✗ {symbol}: {str(e)}")
            results["options"][f"{symbol}_{expiry}"] = {"success": False, "error": str(e)}
    
    # Save full results
    with open(f"{output_dir}/{provider_name}_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_dir}/{provider_name}_test_results.json")
    return results

def export_holdings_to_csv(fund_symbol, holdings, provider_name, output_dir):
    """Export holdings to CSV for manual inspection"""
    filename = f"{output_dir}/{provider_name}_{fund_symbol}_holdings.csv"
    
    with open(filename, 'w', newline='') as f:
        if holdings:
            writer = csv.DictWriter(f, fieldnames=holdings[0].keys())
            writer.writeheader()
            writer.writerows(holdings)
    
    print(f"    → Exported to {filename}")

# Run all tests
async def main():
    import os
    os.makedirs("./api_test_results", exist_ok=True)
    
    # Test each provider
    results = []
    results.append(await test_provider("EODHD", "your-trial-key"))
    results.append(await test_provider("FMP", "your-trial-key"))
    results.append(await test_provider("TwelveData", "your-trial-key"))
    
    # Generate comparison report
    generate_comparison_report(results)
```

#### 2. Comparison Report Generator: `generate_report.py`
```python
def generate_comparison_report(results):
    """Create a summary comparison of all providers"""
    
    report = []
    report.append("# API Provider Comparison Report")
    report.append(f"\nGenerated: {datetime.now()}")
    
    # Mutual Funds Coverage (Most Important)
    report.append("\n## Mutual Fund Holdings Coverage")
    report.append("| Provider | FXNAX | FCNTX | FMAGX | VTIAX | Avg Holdings | Data Quality |")
    report.append("|----------|-------|-------|-------|-------|--------------|--------------|")
    
    for r in results:
        provider = r['provider']
        mf_data = r['mutual_funds']
        
        counts = []
        quality = "Good" if all(mf.get('has_security_names') for mf in mf_data.values() if mf.get('success')) else "Limited"
        
        row = f"| {provider} "
        for symbol in ['FXNAX', 'FCNTX', 'FMAGX', 'VTIAX']:
            if symbol in mf_data and mf_data[symbol].get('success'):
                count = mf_data[symbol]['count']
                counts.append(count)
                row += f"| {count} "
            else:
                row += "| ❌ "
        
        avg = sum(counts) / len(counts) if counts else 0
        row += f"| {avg:.0f} | {quality} |"
        report.append(row)
    
    # Stock Data Coverage
    report.append("\n## Stock Price Data")
    report.append("| Provider | AAPL | MSFT | AMZN | Historical Days |")
    report.append("|----------|------|------|------|-----------------|")
    
    # Options Data Coverage  
    report.append("\n## Options Chain Data")
    report.append("| Provider | Contracts | Greeks | IV | Overall |")
    report.append("|----------|-----------|--------|----|---------| ")
    
    # Save report
    with open("./api_test_results/COMPARISON_REPORT.md", 'w') as f:
        f.write('\n'.join(report))
    
    print("\n✓ Comparison report saved to ./api_test_results/COMPARISON_REPORT.md")
```

### Decision Criteria
1. **Mutual Fund Holdings Quality** (40% - Critical)
   - Coverage: Do all 4 test funds have holdings data?
   - Completeness: 40+ holdings per fund expected
   - Data fields: Symbol, name, weight/percentage, shares
   - Total weights: Should sum to ~90-100%

2. **Stock Price Data** (20% - Must Have)
   - Historical data: 1+ years available
   - All test symbols supported
   - Accurate OHLCV data

3. **Options Chain Data** (20% - Must Have)  
   - Full chain with multiple expiries
   - Greeks available (delta, gamma, theta, vega)
   - Implied volatility data

4. **Cost & Simplicity** (20%)
   - Under $200/month
   - Simple API to integrate
   - Good documentation

### Expected Output Files
After running tests, you'll have:
```
api_test_results/
├── EODHD_test_results.json          # Full test results
├── EODHD_FXNAX_holdings.csv        # Fidelity Growth holdings
├── EODHD_FCNTX_holdings.csv        # Contrafund holdings  
├── EODHD_FMAGX_holdings.csv        # Magellan holdings
├── EODHD_VTIAX_holdings.csv        # Vanguard Intl holdings
├── FMP_test_results.json
├── FMP_FXNAX_holdings.csv
├── ... (same for each provider)
└── COMPARISON_REPORT.md             # Summary comparison
```

### What to Look for in Holdings CSVs
1. **Number of holdings**: Should see 50-200+ per fund
2. **Data completeness**: 
   - Security identifiers (ticker/CUSIP)
   - Security names (not just tickers)
   - Weights/percentages
   - Share counts (nice to have)
3. **Weight totals**: Should sum to 90-100%
4. **Recognizable names**: Top holdings should match fund's strategy

## Implementation Plan (3-5 days)

### Option 1: If Choosing Hybrid (EODHD/FMP + Polygon)

Just modify the existing `MarketDataService`:

```python
# app/services/market_data_service.py

class MarketDataService:
    def __init__(self):
        self.polygon_client = RESTClient(POLYGON_API_KEY)
        self.eodhd_client = EODHDClient(EODHD_API_KEY)  # NEW
    
    async def fetch_stock_prices(self, symbols):
        # CHANGE: Route to EODHD instead of Polygon
        return await self.eodhd_client.get_prices(symbols)
    
    async def fetch_mutual_fund_holdings(self, symbol):
        # NEW: Add this method
        return await self.eodhd_client.get_fund_holdings(symbol)
    
    async def fetch_options_chain(self, symbol):
        # NO CHANGE: Keep using Polygon
        return await self.polygon_client.get_options(symbol)
```

### Option 2: If Choosing TwelveData Only

Replace everything in one go:

```python
# app/services/market_data_service.py

class MarketDataService:
    def __init__(self):
        self.client = TwelveDataClient(TWELVEDATA_API_KEY)
    
    async def fetch_stock_prices(self, symbols):
        return await self.client.time_series(symbols)
    
    async def fetch_mutual_fund_holdings(self, symbol):
        return await self.client.get_fund_holdings(symbol)
    
    async def fetch_options_chain(self, symbol):
        return await self.client.get_options(symbol)
```

## Minimal TODO List

### Week 1: Test & Decide
- [ ] Day 1: Get trial API keys
- [ ] Day 2: Run test script, check mutual fund holdings quality
- [ ] Day 3: Pick winner, document decision

### Week 2: Implement
- [ ] Day 1: Add new API client to requirements.txt
- [ ] Day 2: Update MarketDataService (add new client, modify 1-3 methods)
- [ ] Day 3: Test with real portfolio data
- [ ] Day 4: Update .env.example and deployment configs
- [ ] Day 5: Deploy and monitor

### That's It!

## Future-Proofing (Do Later)

When you have 100+ users and need more flexibility:
1. Add a simple provider config in .env:
   ```
   STOCK_DATA_PROVIDER=eodhd
   OPTIONS_DATA_PROVIDER=polygon
   ```

2. Add a factory pattern:
   ```python
   def get_stock_data_client():
       if settings.STOCK_DATA_PROVIDER == "eodhd":
           return EODHDClient()
       elif settings.STOCK_DATA_PROVIDER == "polygon":
           return PolygonClient()
   ```

But don't build this now - you don't need it yet.

## Migration Checklist

- [ ] Test new API with actual mutual fund tickers
- [ ] Update MarketDataService (change ~50 lines of code)
- [ ] Add new API key to environment variables
- [ ] Test all existing features still work
- [ ] Update any batch jobs that call the service
- [ ] Deploy

## What We're NOT Doing (Yet)
- Complex routing engines
- Multiple fallback providers  
- Sophisticated caching layers
- Provider health monitoring
- Cost tracking systems

These can all wait until you have real users and real problems to solve.

## Implementation Questions for AI Coding Agent

### 1. Provider-Specific API Details
- What are the actual API endpoints for each provider (EODHD, FMP, TwelveData) for:
  - Fetching mutual fund holdings
  - Getting stock prices
  - Retrieving options chains
- What authentication method does each use (API key in header vs query parameter)?

### 2. Response Format Normalization
- Each provider likely returns data in different formats. Should the test script include normalization logic to convert all responses to a common format? For example:
```python
# EODHD might return: {"symbol": "AAPL", "weight": 5.2}
# FMP might return: {"ticker": "AAPL", "percentage": 5.2}
# Should we normalize to: {"symbol": "AAPL", "weight": 5.2, "name": "Apple Inc."}
```

### 3. Missing Implementation Functions
- The test script references `fetch_stock_prices()`, `fetch_fund_holdings()`, and `fetch_options_chain()` but doesn't show their implementations
- Should these be provider-specific adapters?

### 4. Rate Limiting
- Should the test script include rate limiting logic to avoid hitting API limits during testing?
- What are the rate limits for each provider's trial/free tier?

### 5. Error Handling Specifics
- What specific errors should we catch and how should we handle them?
- Examples: symbol not found, API limit exceeded, network timeout

### 6. Data Quality Metrics
- For the "Data Quality" assessment in the comparison report, what specific criteria determine "Good" vs "Limited"?
- Is it just the presence of security names, or should we check for other fields?

### 7. Options Contract Format
- The test portfolio shows options as strings like "SPY 2025-09-19 460C"
- Do the APIs expect this format, or do they need separate parameters (underlying, expiry, strike, type)?

### 8. Provider Adapter Pattern
- Should we create a common interface like this?
```python
class MarketDataProvider(ABC):
    @abstractmethod
    async def get_stock_price(self, symbol: str) -> Optional[StockPrice]:
        pass
    
    @abstractmethod
    async def get_mutual_fund_holdings(self, symbol: str) -> Optional[List[Holding]]:
        pass
    
    @abstractmethod
    async def get_options_chain(self, underlying: str, expiry: date) -> Optional[List[OptionContract]]:
        pass

# Then implement:
# EODHDProvider(MarketDataProvider)
# FMPProvider(MarketDataProvider)
# TwelveDataProvider(MarketDataProvider)
```

### 9. Test Execution Strategy
- Should we run tests against all providers in parallel or sequentially?
- How do we handle API keys for testing (environment variables)?
- Should failed API calls be retried during testing?

### 10. Holdings Update Frequency
- How often do mutual fund holdings typically update (quarterly?)?
- Should we cache holdings data differently than price data?
- What's the staleness tolerance for holdings data in production?

### 11. Development Testing Approach
- Should we create mock responses for each provider first?
- Example mock data structure for consistent testing?
- How to verify data quality without manual inspection of 192 test cases?
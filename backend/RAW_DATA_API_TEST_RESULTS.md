# Raw Data API Test Results - /data/ Namespace Only

Generated: 2025-08-26T17:48:51.026295

Server: http://localhost:8000

Testing ONLY /api/v1/data/ endpoints per API_SPECIFICATIONS_V1.4.4.md

---


## Account: Individual Investor
Email: demo_individual@sigmasight.com
Expected Positions: 16

✅ **Login Successful**


### Portfolio ID: 51134ffd-2f13-49bd-b1f5-0c327e801b69


#### Endpoint: /api/v1/data/portfolio/51134ffd-2f13-49bd-b1f5-0c327e801b69/complete
- ✅ Status: 200
- Response Time: 50.4ms
- Data Size: 3,508 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/portfolio/51134ffd-2f13-49bd-b1f5-0c327e801b69/data-quality
- ✅ Status: 200
- Response Time: 76.6ms
- Data Size: 992 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/positions/details
- ✅ Status: 200
- Response Time: 23.8ms
- Data Size: 6,059 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/historical/51134ffd-2f13-49bd-b1f5-0c327e801b69
- ✅ Status: 200
- Response Time: 47.0ms
- Data Size: 297,402 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/quotes
- ✅ Status: 200
- Response Time: 11.0ms
- Data Size: 944 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/factors/etf-prices
- ✅ Status: 200
- Response Time: 17.1ms
- Data Size: 9,168 bytes
- 🟢 **No issues detected**

---


## Account: High Net Worth
Email: demo_hnw@sigmasight.com
Expected Positions: 17

✅ **Login Successful**


### Portfolio ID: c0510ab8-c6b5-433c-adbc-3f74e1dbdb5e


#### Endpoint: /api/v1/data/portfolio/c0510ab8-c6b5-433c-adbc-3f74e1dbdb5e/complete
- ✅ Status: 200
- Response Time: 44.4ms
- Data Size: 3,705 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/portfolio/c0510ab8-c6b5-433c-adbc-3f74e1dbdb5e/data-quality
- ✅ Status: 200
- Response Time: 82.7ms
- Data Size: 991 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/positions/details
- ✅ Status: 200
- Response Time: 45.8ms
- Data Size: 6,432 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/historical/c0510ab8-c6b5-433c-adbc-3f74e1dbdb5e
- ✅ Status: 200
- Response Time: 71.3ms
- Data Size: 297,332 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/quotes
- ✅ Status: 200
- Response Time: 11.5ms
- Data Size: 944 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/factors/etf-prices
- ✅ Status: 200
- Response Time: 17.3ms
- Data Size: 9,165 bytes
- 🟢 **No issues detected**

---


## Account: Hedge Fund Style
Email: demo_hedgefundstyle@sigmasight.com
Expected Positions: 30

✅ **Login Successful**


### Portfolio ID: 2ee7435f-379f-4606-bdb7-dadce587a182


#### Endpoint: /api/v1/data/portfolio/2ee7435f-379f-4606-bdb7-dadce587a182/complete
- ✅ Status: 200
- Response Time: 54.7ms
- Data Size: 6,199 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/portfolio/2ee7435f-379f-4606-bdb7-dadce587a182/data-quality
- ✅ Status: 200
- Response Time: 87.1ms
- Data Size: 1,210 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/positions/details
- ✅ Status: 200
- Response Time: 54.2ms
- Data Size: 11,015 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/historical/2ee7435f-379f-4606-bdb7-dadce587a182
- ✅ Status: 200
- Response Time: 98.7ms
- Data Size: 477,535 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/prices/quotes
- ✅ Status: 200
- Response Time: 11.9ms
- Data Size: 944 bytes
- 🟢 **No issues detected**

#### Endpoint: /api/v1/data/factors/etf-prices
- ✅ Status: 200
- Response Time: 38.7ms
- Data Size: 9,161 bytes
- 🟢 **No issues detected**

---


## Summary of /data/ Namespace Endpoints

### Endpoints Tested: 6
- /api/v1/data/portfolio/{id}/complete
- /api/v1/data/portfolio/{id}/data-quality
- /api/v1/data/positions/details
- /api/v1/data/prices/historical/{id}
- /api/v1/data/prices/quotes
- /api/v1/data/factors/etf-prices

### Known Issues to Verify:
1. **cash_balance** - Check if hardcoded to 0
2. **Historical prices** - Verify if using real vs mock data
3. **Market quotes** - Check if real-time or simulated
4. **Greeks calculations** - Verify options positions have Greeks

### Data Quality Issues:
1. Factor ETF prices are mock data
2. Some risk metrics may be placeholder values
3. Correlation matrices might be simplified

### Recommendations:
1. **Priority 1**: Implement real market data connection
2. **Priority 2**: Fix cash_balance implementation
3. **Priority 3**: Calculate real Greeks for options
4. **Priority 4**: Implement proper factor analysis
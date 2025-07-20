# Risk Factor Analysis & Risk Metrics Implementation Planning
## Sections 1.4.4 & 1.4.5 Design Document

**Created:** 2025-07-17  
**Purpose:** Planning document for Risk Factor Analysis and Risk Metrics implementation  
**Dependencies:** Sections 1.4.1, 1.4.2, 1.4.3 (all completed)

---

## Document Scope

This document covers the planning and design decisions for two interconnected sections:

### **Section 1.4.4: Risk Factor Analysis**
- 8-factor model implementation with ETF proxies
- Factor beta calculations using regression analysis
- Portfolio-level factor exposure aggregation
- Integration with existing portfolio aggregation functions

### **Section 1.4.5: Risk Metrics**
- Portfolio VaR calculations using factor model
- Risk metrics using empyrical library (Sharpe, max drawdown, volatility)
- Historical return-based risk analysis
- Integration with factor exposures from Section 1.4.4

---

## Overview

This document identifies clarifying questions and design decisions needed for implementing both Risk Factor Analysis (1.4.4) and Risk Metrics (1.4.5). These sections work together to provide comprehensive portfolio risk assessment - factor analysis provides the risk attribution framework, while risk metrics provide quantitative risk measures.

---

# SECTION 1.4.4: RISK FACTOR ANALYSIS

## 1. Factor Model Architecture Questions

### Q1.1: Factor Return Data Source & Calculation Method
**Question:** How should we calculate factor returns for the 8-factor model?

**Current State:**
- 8 factors defined in database with ETF proxies (SPY, VTV, VUG, MTUM, QUAL, SIZE, USMV)
- Short Interest factor has no ETF proxy
- MarketDataService can fetch ETF historical prices

**Design Decision Needed:**
- **Option A:** Calculate factor returns from ETF price changes (SPY return = market factor return)
- **Option B:** Use regression against broader factor definitions
- **Option C:** Hybrid approach with ETF proxies for 7 factors, mock for Short Interest

**Recommendation:** **Option C - Hybrid Approach**
- Use daily ETF returns for 7 factors with ETF proxies
- Mock Short Interest factor with small random returns (±0.5% daily)
- Aligns with V1.4 hybrid real/mock approach
- Simple to implement and understand

**Elliott comments:**
- Option C.  Basically Option A for the 7 factors with ETF proxies. That's what the legacy scripts did. Legacy Scripts did not do Short Interest. Ben mocked it in the V0.dev Front End prototype. What data source is needed and what calcuations are needed? Should we drop it for now or figure it out?

**Ben comments:**
- 

### Q1.2: Factor Beta Calculation Window
**Question:** What time window should we use for factor beta calculations?

**Current State:**
- Legacy code uses unspecified window
- Need to balance statistical significance vs. responsiveness

**Options:**
- **Option A:** 60 trading days (3 months) - follows legacy approach
- **Option B:** 252 trading days (1 year) - more stable betas
- **Option C:** Configurable window with 60-day default

**Recommendation:** **Option A - 60 Trading Days**
- Matches legacy `factors_utils.py` approach
- Good balance of stability vs. responsiveness
- Sufficient sample size for regression analysis
- Can be made configurable later

**Elliott comments:**
- Let's do Option C, but not expose this ability to the user right now. Just plan for the future. Adds some testing complexity but future proofing.

**Ben comments:**
- 

### Q1.3: Position vs Portfolio Level Betas
**Question:** Should we calculate factor betas at position level or portfolio level?

**Current State:**
- Legacy code calculates position-level betas then aggregates
- Database has `factor_exposures` table at portfolio level
- Need to decide calculation approach

**Legacy Approach For Reference:**
- `factors_utils.py` calculates position-level betas using covariance method
- Formula: `beta = cov(position_rf, factor_rf) / var(factor_rf)`
- Reshapes results into DataFrame with positions as index, factors as columns
- Aggregation to portfolio level done separately

**Options:**
- **Option A:** Position-level betas aggregated to portfolio (legacy approach)
- **Option B:** Direct portfolio-level beta calculation
- **Option C:** Both approaches for validation

**Recommendation:** **Option A - Position-Level with Aggregation**
- Follows proven legacy methodology
- Allows for position-level risk attribution
- More flexible for future enhancements
- Database schema supports this approach

**Elliott comments:**
- Option A. Need position-level granularity.

**Ben comments:**
- 

---

## 2. Data Requirements & Sources

### Q2.1: Historical Return Data Calculation
**Question:** How should we calculate position returns for factor regression?

**Current State:**
- Have daily P&L calculations from Section 1.4.1
- Need return series for regression analysis
- Position quantities and prices available

**Legacy Approach For Reference:**
- `get_data.py` uses simple price-based returns: `ret = close / prev_close - 1`
- Uses NYSE trading calendar to find previous trading day
- Handles missing data with `np.nan` values
- No exposure weighting or position size adjustments

**Design Decision Needed:**
- **Method 1:** Daily return = (today_exposure - yesterday_exposure) / yesterday_exposure
- **Method 2:** Daily return = daily_pnl / position_market_value
- **Method 3:** Daily return = (today_price - yesterday_price) / yesterday_price

**Recommendation:** **Method 1 - Exposure-Based Returns**
- Accounts for position size changes
- Consistent with portfolio management practices
- Handles both stocks and options uniformly
- Uses existing exposure calculations

**Elliott comments:**
- Method 1: this makes sense to me for stocks, but what about options? Claude is recommending delta-adjusted exposure. Also what if you make trades and increase/decrease your exposure? That muddies the meaning of the position returns for factor regression.  Does this mean that for us factor regression is specific to a portfolio? so each portfolio would have a different factor beta regression analysis.

**Ben comments:**
- 

### Q2.2: Missing Data Handling
**Question:** How should we handle missing historical data?

**Current State:**
- Market data fetching may have gaps
- Some positions may lack sufficient history
- Need robust fallback strategy

**Legacy Approach For Reference:**
- `get_data.py` uses `np.nan` for missing previous close prices
- Continues calculations with available data points
- No minimum data requirements enforced
- Graceful degradation without blocking entire calculation

**Scenarios & Recommendations:**
- **New positions (<60 days history):** Skip factor calculation, use zeros
- **Missing market data:** Use last available price, log warning
- **ETF proxy data gaps:** Skip that day from regression, require minimum 30 days
- **Complete data failure:** Fall back to mock factor exposures (small random values)

**Elliott comments:**
- need to ask about general philosophy of this.
- scenario 1: new positions with <90 day history.  Skip factor calculation, use zeros
- scenario 2: missing market data.  Use last available price, log warning
- scenario 3: ETF proxy data gaps.  Skip that day from regression, require minimum 30 days
- scenario 4: complete data failure.  Fall back to mock factor exposures (small random values)
- scenario 5: market holidays/weekend gaps
- scenario 6: corporate actions/stock splits
- scenario 7: position size changes.

### Q2.3: Factor Return Data Storage
**Question:** Should we cache factor returns or calculate on-demand?

**Legacy Approach For Reference:**
- `get_data.py` shows no evidence of cached factor returns
- Calculations performed fresh each time from market data
- Uses direct database queries to fetch price data on-demand
- No intermediate storage of computed factor returns

**Options:**
- **Option A:** Cache factor returns in database table
- **Option B:** Calculate from ETF prices on-demand
- **Option C:** Hybrid with smart caching

**Recommendation:** **Option B - Calculate On-Demand**
- Simpler implementation for V1.4
- Leverages existing market data infrastructure
- Less database complexity
- Can add caching in Phase 2 if needed

**Elliott comments:**
- 

**Ben comments:**
- 

### Q2.4: Missing Data Handling Strategy
**Question:** How to handle positions with insufficient price history for factor regression?

**Context:**
- New positions may not have 60 days of history
- ETF proxies might have missing data for holidays/halts

**Options:**
- **Option A:** Skip positions with <30 days of data
- **Option B:** Use available data with minimum 20 observations
- **Option C:** Assign neutral (zero) betas to new positions

**Recommendation:** **Option B - Flexible Minimum**
- Require minimum 20 trading days for regression
- Log warning for positions with limited history
- Include data quality flag in response
- Graceful degradation rather than exclusion

**Elliott comments:**
- 

**Ben comments:**
- 

---

## 3. Calculation Implementation Questions

### Q3.1: Regression Library Choice
**Question:** Which library should we use for factor regression calculations?

**Current State:**
- Legacy uses `statsmodels.api` for OLS regression
- Already included in dependencies

**Legacy Approach For Reference:**
- `get_data.py` imports `statsmodels.api as sm`
- Uses `model = sm.OLS(dependent_variable, X).fit()` for regression
- Adds constant term with `X = sm.add_constant(X)`
- Extracts beta coefficients with `model.params[1:].values`

**Analysis:**
- **statsmodels:** Mature, statistical significance testing, matches legacy
- **sklearn:** Machine learning focused, might be overkill
- **numpy:** Basic linear algebra, would need custom implementation

**Recommendation:** **statsmodels (OLS)**
- Matches legacy implementation exactly
- Provides statistical significance metrics
- Industry standard for financial factor models
- Already a project dependency

**Elliott comments:**
- 

**Ben comments:**
- 

### Q3.2: Portfolio Beta Aggregation Method
**Question:** How should we aggregate position-level betas to portfolio level?

**Current State:**
- Legacy code has aggregation logic
- Need to weight by position exposure

**Options:**
- **Option A:** Exposure-weighted average (standard approach)
- **Option B:** Equal-weighted average
- **Option C:** Market-value weighted average

**Recommendation:** **Option A - Exposure-Weighted Average**
- Standard practice in portfolio management
- Reflects true portfolio risk exposure
- Matches legacy implementation approach
- Consistent with Section 1.4.3 aggregation methods

**Elliott comments:**
- 

**Ben comments:**
- 

### Q3.3: Factor Covariance Matrix
**Question:** How should we handle the factor covariance matrix for V1.4?

**Current State:**
- Legacy mentions identity matrix for simplicity
- Real correlations would require significant historical analysis

**Legacy Approach For Reference:**
- `var_utils.py` has both simple and sophisticated covariance methods
- `covariance_matrix()`: Simple `factor_returns.cov()` calculation
- `decay_covariance_matrix()`: Uses 0.94 exponential decay weighting
- `correlation_matrix()`: Calculates real factor correlations from returns
- Legacy used actual correlations, not identity matrix

**Options:**
- **Option A:** Identity matrix (no correlations, σ = 0.01)
- **Option B:** Simple correlation estimates
- **Option C:** Historical correlation calculation

**Recommendation:** **Option A - Identity Matrix (V1.4 Scope)**
- Follows V1.4 hybrid approach philosophy
- Simpler implementation and testing
- Real correlations can be Phase 2 enhancement
- Provides baseline risk attribution functionality

**Elliott comments:**
- 

**Ben comments:**
- 

### Q3.4: Outlier Handling for Factor Betas
**Question:** How should we handle extreme factor beta values from regression?

**Context:**
- Regression can produce extreme betas for positions with limited history
- Outliers can distort portfolio-level risk assessments

**Options:**
- **Option A:** No capping, use raw regression outputs
- **Option B:** Cap betas at ±3 (99.7% of normal distribution)
- **Option C:** Winsorize at 5th/95th percentiles

**Recommendation:** **Option B - Cap at ±3**
- Prevents extreme outliers from dominating portfolio risk
- Maintains mathematical interpretability
- Simple to implement and explain
- Can be made configurable later

**Elliott comments:**
- 

**Ben comments:**
- 

### Q3.5: Greeks Integration with Factor Models
**Question:** How should option Greeks interact with factor risk calculations?

**Context:**
- Options have non-linear risk profiles via Greeks
- Delta-adjusted exposure already calculated in Section 1.4.3

**Options:**
- **Option A:** Use market value exposure for all positions
- **Option B:** Use delta-adjusted exposure for options
- **Option C:** Hybrid based on calculation type

**Recommendation:** **Option B - Delta-Adjusted for Options**
- More accurate risk representation for options
- Consistent with industry practices
- Already calculated in portfolio aggregation
- Use `calculate_delta_adjusted_exposure()` output

**Elliott comments:**
- 

**Ben comments:**
- 

### Q3.6: Correlation Stability Monitoring
**Question:** How to handle time-varying correlations between factors?

**Context:**
- Factor correlations change during market regimes
- Identity matrix assumption may be too simple

**Options:**
- **Option A:** Static identity matrix (current plan)
- **Option B:** Rolling correlation calculation
- **Option C:** Regime-based correlation matrices

**Recommendation:** **Option A for V1.4, with Monitoring**
- Implement identity matrix as planned
- Add correlation calculation function (not used)
- Log actual correlations for future analysis
- Upgrade path clear for V1.5

**Elliott comments:**
- 

**Ben comments:**
- 

---

## 4. Database & Storage Questions

### Q4.1: Factor Exposure Storage Strategy
**Question:** How frequently should we store factor exposures?

**Current State:**
- Database supports daily storage
- Batch jobs run at 5:30 PM daily

**Options:**
- **Option A:** Daily storage (matches snapshots)
- **Option B:** Weekly storage (reduces database size)
- **Option C:** On-demand calculation only

**Recommendation:** **Option A - Daily Storage**
- Consistent with portfolio snapshot approach
- Enables historical factor analysis
- Required for time-series risk attribution
- Database schema already supports this

### Q4.2: Position-Level Factor Storage
**Question:** Should we store position-level factor exposures?

**Current State:**
- Current schema only has portfolio-level `factor_exposures`
- Position-level would require new table

**Analysis:**
- **Pros of Position-Level:** Detailed attribution, debugging capability
- **Cons:** Database size, complexity
- **V1.4 Scope:** Portfolio-level analysis focus

**Recommendation:** **Portfolio-Level Only (V1.4)**
- Matches current database schema
- Sufficient for portfolio risk management
- Position-level can be Phase 2 enhancement
- Reduces implementation complexity

---

## 5. Performance & Caching Questions

### Q5.1: Calculation Performance Targets
**Question:** What performance targets should we set for factor calculations?

**Current State:**
- Portfolio aggregation: <1 second for 10,000 positions
- Market data: <5 seconds for portfolio symbols
- Factor calculations will be more intensive

**Analysis:**
- Factor regression for 60 days × N positions
- Matrix operations for portfolio aggregation
- Should integrate with existing batch job timing

**Recommendation:** **Performance Targets**
- **Individual portfolio:** <30 seconds for factor calculation
- **Batch processing:** <10 minutes for all portfolios
- **API response:** <5 seconds for cached results
- **Timeout:** 60 seconds max per portfolio

### Q5.2: Caching Strategy
**Question:** What should be our caching approach for factor calculations?

**Options:**
- **Option A:** No caching, calculate on-demand
- **Option B:** Same 60-second TTL as portfolio aggregations
- **Option C:** Longer TTL (24 hours) since factors change slowly

**Recommendation:** **Option C - 24-Hour TTL**
- Factor exposures change slowly
- Expensive calculations justify longer cache
- Daily batch job refreshes cache anyway
- Reduces computational load

### Q5.3: Real-time vs Batch Calculation Trade-offs
**Question:** Which calculations must be real-time vs batch only?

**Context:**
- Some metrics needed for trading decisions
- Others only for reporting

**Real-time Requirements:**
- Portfolio Greeks (already real-time)
- Current exposures (already real-time)

**Batch Sufficient:**
- Factor betas (change slowly)
- VaR calculations (daily sufficient)
- Historical risk metrics

**Recommendation:** **Batch-First Approach**
- All Section 1.4.4/1.4.5 calculations in batch
- API serves cached results
- Add real-time triggers later if needed
- Optimize for reliability over latency

---

## 6. Integration & API Questions

### Q6.1: API Endpoint Design
**Question:** How should factor analysis endpoints be structured?

**Current State:**
- Portfolio aggregation uses `/api/v1/portfolio/...` pattern
- Risk endpoints planned in `/api/v1/risk/...`

**Proposed Endpoints:**
- `GET /api/v1/risk/factors/exposures` - Portfolio factor exposures
- `GET /api/v1/risk/factors/definitions` - Available factors
- `POST /api/v1/risk/factors/calculate` - Trigger calculation
- `GET /api/v1/risk/factors/history` - Historical factor exposures

**Recommendation:** **Adopt Proposed Structure**
- Consistent with existing API patterns
- Clear separation of factor vs. other risk metrics
- Supports both real-time and historical analysis

### Q6.2: Batch Job Integration
**Question:** How should factor calculations integrate with existing batch jobs?

**Current State:**
- 4 PM: Market data update
- 5:30 PM: Portfolio snapshots
- Need to fit factor calculations in sequence

**Recommendation:** **5:15 PM Factor Calculation Job**
- After market data update (needs price data)
- Before portfolio snapshots (snapshots can include factor data)
- 15-minute window allows for reasonable portfolio count
- Separate job for better error isolation

---

## 7. Testing & Validation Questions

### Q7.1: Regression Testing Strategy
**Question:** How should we validate factor regression calculations?

**Approaches:**
- **Unit Tests:** Mock data with known expected outputs
- **Integration Tests:** Real historical data validation
- **Comparison Tests:** Legacy code output comparison

**Recommendation:** **Multi-Layer Testing**
- Unit tests with synthetic data (known factor relationships)
- Integration tests with historical ETF data
- Comparison with legacy output where possible
- Performance tests with large portfolios

### Q7.2: Data Quality Monitoring
**Question:** How to detect and handle data quality issues?

**Context:**
- Bad prices can corrupt risk calculations
- Missing data can skew regression results

**Quality Checks Needed:**
- Price continuity (>20% daily moves)
- Data completeness (missing observations)
- Regression diagnostics (R-squared, p-values)

**Recommendation:** **Basic Quality Flags**
- Add quality_score to calculation results
- Log warnings for suspicious data
- Include diagnostic stats in metadata
- Don't block calculations, just flag issues

### Q7.3: Mock Factor Implementation
**Question:** How should we implement the Short Interest mock factor?

**Current State:**
- 7 factors have ETF proxies
- Short Interest needs mock implementation

**Options:**
- **Option A:** Random returns within ±0.5% daily
- **Option B:** Sector-based proxy calculation
- **Option C:** Zero returns (no exposure)

**Recommendation:** **Option A - Random Returns**
- Provides realistic mock behavior
- Enables testing of factor attribution
- Simple to implement and maintain
- Can be enhanced to sector-based in Phase 2

---

## 8. Implementation Functions Specification

### 8.1: Core Functions Needed

Based on the analysis above, here are the required functions:

#### `calculate_factor_betas_hybrid(portfolio_id: UUID, calculation_date: date) -> Dict[str, Decimal]`
- **Input:** Portfolio ID and calculation date
- **Process:** Fetch 60-day returns, calculate regression betas for 8 factors
- **Output:** Dictionary mapping factor names to beta values
- **Dependencies:** Market data service, factor definitions
- **File:** `app/calculations/factors.py`

#### `fetch_factor_returns(symbols: List[str], start_date: date, end_date: date) -> pd.DataFrame`
- **Input:** Factor ETF symbols and date range
- **Process:** Fetch ETF historical prices, calculate daily returns
- **Output:** DataFrame with factor returns
- **Dependencies:** MarketDataService
- **File:** `app/calculations/factors.py`

#### `calculate_position_returns(portfolio_id: UUID, start_date: date, end_date: date) -> pd.DataFrame`
- **Input:** Portfolio ID and date range
- **Process:** Calculate daily position returns from exposure changes
- **Output:** DataFrame with position returns
- **Dependencies:** Position data, market data
- **File:** `app/calculations/factors.py`

#### `aggregate_portfolio_factor_exposures(position_betas: Dict, portfolio_exposures: Dict) -> Dict[str, Decimal]`
- **Input:** Position-level betas and current portfolio exposures
- **Process:** Exposure-weighted aggregation to portfolio level
- **Output:** Portfolio factor exposures
- **Dependencies:** Portfolio aggregation from Section 1.4.3
- **File:** `app/calculations/factors.py`

#### `get_factor_covariance_matrix() -> np.ndarray`
- **Input:** None
- **Process:** Return 8x8 identity matrix scaled by variance
- **Output:** NumPy array representing factor covariance
- **Note:** Static implementation for V1.4
- **File:** `app/calculations/factors.py`

---

## 9. Implementation Timeline

### Phase 1: Core Implementation (3-4 days)
1. **Day 1:** Factor return calculation and data fetching
2. **Day 2:** Position return calculation and regression functions
3. **Day 3:** Portfolio aggregation and database integration
4. **Day 4:** Testing and validation

### Phase 2: Integration (1-2 days)
1. **Day 5:** Batch job integration and API endpoints
2. **Day 6:** Performance optimization and error handling

### Total Estimate: 5-6 days for Section 1.4.4 completion

---

# SECTION 1.4.5: RISK METRICS

## 11. Risk Metrics Architecture Questions

### Q11.1: VaR Calculation Method
**Question:** How should we implement Value-at-Risk (VaR) calculations?

**Current State:**
- Legacy `var_utils.py` uses factor model approach with matrix multiplication
- Need 95% and 99% confidence levels
- Integration with factor exposures from Section 1.4.4

**Legacy Approach For Reference:**
- `var_utils.py` implements `multiply_matrices()` function
- Formula: `exposure_t.dot(factor_betas).dot(matrix_cov).dot(factor_betas_t).T`
- Returns `(position_exposure ** 0.5)` - square root for standard deviation
- Uses actual covariance matrix, not simplified version

**Options:**
- **Option A:** Factor model VaR using matrix multiplication (legacy approach)
- **Option B:** Historical simulation VaR from return series
- **Option C:** Monte Carlo VaR simulation
- **Option D:** Hybrid approach with factor model primary, historical fallback

**Recommendation:** **Option A - Factor Model VaR (Primary)**
- Matches legacy `var_utils.py` implementation
- Uses factor exposures and covariance matrix
- More stable than historical methods
- Industry standard for portfolio risk management

**Elliott comments:**
- 

**Ben comments:**
- 

### Q11.2: Portfolio Return Calculation for Risk Metrics
**Question:** How should we calculate portfolio returns for empyrical library metrics?

**Current State:**
- Have position-level P&L from Section 1.4.1
- Need portfolio-level return series
- empyrical requires pandas Series of returns

**Legacy Approach For Reference:**
- `get_data.py` shows portfolio return calculations in various functions
- `calculate_contribution_to_return()` uses position weights × returns
- `calculate_adjusted_cumulative_returns()` aggregates position returns
- No single standard method - varies by use case

**Options:**
- **Option A:** Aggregate daily P&L / total portfolio value
- **Option B:** Weight-adjusted position returns
- **Option C:** Use existing exposure calculations from Section 1.4.3

**Recommendation:** **Option A - P&L Based Returns**
- Simple and intuitive calculation
- Uses existing P&L infrastructure
- Formula: `portfolio_return = total_daily_pnl / portfolio_market_value`
- Handles position changes automatically

**Elliott comments:**
- 

**Ben comments:**
- 

### Q11.3: Risk Metrics Selection
**Question:** Which risk metrics should we implement using empyrical?

**Available in empyrical:**
- Sharpe ratio, Calmar ratio, Sortino ratio
- Maximum drawdown, volatility
- VaR (historical), CVaR (conditional VaR)
- Alpha, beta (vs benchmark)

**Recommendation:** **Core Risk Metrics Set**
- **Sharpe Ratio:** Risk-adjusted return measure
- **Maximum Drawdown:** Peak-to-trough loss
- **Volatility:** Annualized standard deviation
- **VaR (95%, 99%):** Historical VaR for comparison
- **Calmar Ratio:** Return/max drawdown ratio

**Elliott comments:**
- 

**Ben comments:**
- 

---

## 12. VaR Implementation Questions

### Q12.1: Factor Model VaR Formula
**Question:** How should we implement the factor model VaR calculation?

**Legacy Formula (from var_utils.py):**
```python
position_exposure = exposure.T.dot(factor_betas).dot(covariance_matrix).dot(factor_betas.T).T
var_estimate = (position_exposure ** 0.5)
```

**Design Decisions:**
- **Matrix Operations:** Use numpy/pandas for matrix multiplication
- **Confidence Levels:** Apply 95% (1.645) and 99% (2.326) multipliers
- **Input Validation:** Ensure matrix dimensions match

**Recommendation:** **Direct Legacy Implementation**
- Use exact formula from `var_utils.py`
- Portfolio exposure vector × factor betas × covariance × factor betas transpose
- Apply confidence multipliers for final VaR estimates

**Elliott comments:**
- 

**Ben comments:**
- 

### Q12.2: Time Horizon for VaR
**Question:** What time horizon should VaR calculations use?

**Options:**
- **Option A:** 1-day VaR (standard for daily risk management)
- **Option B:** 10-day VaR (regulatory requirement for some firms)
- **Option C:** Both with scaling relationship

**Recommendation:** **Option A - 1-Day VaR**
- Matches daily batch job frequency
- Standard for portfolio management
- Can scale to longer horizons using √t scaling
- Legacy approach uses 1-day horizon

**Elliott comments:**
- 

**Ben comments:**
- 

### Q12.3: Risk-Free Rate Source
**Question:** How should we obtain risk-free rate for Sharpe ratio calculations?

**Current State:**
- Greeks calculations use 5% default risk-free rate
- Need current Treasury rate for accurate Sharpe ratios

**Options:**
- **Option A:** Use same 5% default as Greeks calculations
- **Option B:** Fetch current 3-month Treasury rate
- **Option C:** Configurable rate with 5% default

**Recommendation:** **Option A - Use 5% Default (V1.4)**
- Consistency with existing Greeks calculations
- Simpler implementation
- Real Treasury integration can be Phase 2 enhancement

**Elliott comments:**
- 

**Ben comments:**
- 

---

## 13. Data & Storage Questions (Section 1.4.5)

### Q13.1: Historical Returns Storage
**Question:** Should we store calculated portfolio returns or compute on-demand?

**Current State:**
- Have daily P&L from positions
- Portfolio snapshots store total values
- Need return series for risk metrics

**Options:**
- **Option A:** Calculate returns on-demand from P&L data
- **Option B:** Pre-calculate and store daily returns
- **Option C:** Hybrid with smart caching

**Recommendation:** **Option A - Calculate On-Demand**
- Leverages existing P&L infrastructure
- Reduces database storage requirements
- More flexible for different calculation periods
- Can add caching if performance requires

### Q13.2: Risk Metrics Storage Strategy
**Question:** How should we store calculated risk metrics?

**Current State:**
- Portfolio snapshots table exists for daily summaries
- Risk metrics calculated daily in batch job

**Options:**
- **Option A:** Add risk metrics columns to portfolio_snapshots
- **Option B:** Create separate risk_metrics table
- **Option C:** Store in portfolio_snapshots with JSON field

**Recommendation:** **Option A - Add to Portfolio Snapshots**
- Consistent with existing snapshot approach
- Keeps all daily portfolio data together
- Easier querying for historical analysis
- Schema change is minor addition

---

## 14. Performance Questions (Section 1.4.5)

### Q14.1: Risk Calculation Performance Targets
**Question:** What performance targets for risk metrics calculations?

**Analysis:**
- VaR calculation involves matrix operations
- empyrical metrics need return series (252 days)
- Should complement factor calculation timing

**Recommendation:** **Performance Targets (Section 1.4.5)**
- **VaR calculation:** <5 seconds per portfolio
- **Risk metrics:** <10 seconds per portfolio
- **Combined (1.4.4 + 1.4.5):** <45 seconds total per portfolio
- **Batch processing:** <15 minutes for all portfolios

### Q14.2: Historical Data Requirements
**Question:** How much historical data do we need for risk metrics?

**Current State:**
- empyrical typically uses 252 days (1 year) for metrics
- Factor betas use 60 days
- Need balance between accuracy and data requirements

**Recommendation:** **252 Trading Days for Risk Metrics**
- Industry standard for risk metric calculations
- Provides stable volatility and drawdown estimates
- Different from 60-day factor window (appropriate for different purposes)
- Fallback to shorter periods for new portfolios

---

## 15. Implementation Functions (Section 1.4.5)

### 15.1: Core Risk Metrics Functions

#### `calculate_portfolio_var_hybrid(portfolio_exposures: Dict, factor_betas: Dict, covariance_matrix: np.ndarray) -> Dict[str, Decimal]`
- **Input:** Portfolio exposures, factor betas, covariance matrix
- **Process:** Matrix multiplication following legacy var_utils.py formula
- **Output:** VaR estimates at 95% and 99% confidence levels
- **Dependencies:** Factor exposures from Section 1.4.4
- **File:** `app/calculations/risk_metrics.py`

#### `calculate_risk_metrics_empyrical(portfolio_returns: pd.Series, risk_free_rate: float = 0.05) -> Dict[str, float]`
- **Input:** Historical portfolio returns series
- **Process:** Use empyrical library for standard risk metrics
- **Output:** Sharpe ratio, max drawdown, volatility, historical VaR
- **Dependencies:** Portfolio return history
- **File:** `app/calculations/risk_metrics.py`

#### `calculate_portfolio_returns(portfolio_id: UUID, start_date: date, end_date: date) -> pd.Series`
- **Input:** Portfolio ID and date range
- **Process:** Aggregate daily P&L / portfolio value for return series
- **Output:** pandas Series of daily returns
- **Dependencies:** P&L calculations from Section 1.4.1, portfolio values
- **File:** `app/calculations/risk_metrics.py`

#### `multiply_matrices(exposure: pd.DataFrame, factor_betas: pd.DataFrame, matrix_cov: pd.DataFrame) -> pd.DataFrame`
- **Input:** Portfolio exposure, factor betas, covariance matrix
- **Process:** Legacy matrix multiplication formula
- **Output:** Position exposure for VaR calculation
- **Note:** Direct implementation of legacy var_utils.py logic
- **File:** `app/calculations/risk_metrics.py`

#### `get_risk_free_rate() -> float`
- **Input:** None
- **Process:** Return configured risk-free rate (5% for V1.4)
- **Output:** Risk-free rate as decimal
- **Note:** Static implementation, can be enhanced later
- **File:** `app/calculations/risk_metrics.py`

---

## 16. Integration Between Sections 1.4.4 & 1.4.5

### 16.1: Data Flow Integration
**Section 1.4.4 Outputs → Section 1.4.5 Inputs:**
- Factor exposures → VaR calculation inputs
- Factor covariance matrix → VaR matrix operations
- Portfolio aggregations → Risk metrics base data

### 16.2: Batch Job Sequencing
**Recommended Job Order:**
1. **5:00 PM:** Market data updates (Section 1.4.1)
2. **5:15 PM:** Factor calculations (Section 1.4.4) 
3. **5:25 PM:** Risk metrics calculations (Section 1.4.5)
4. **5:30 PM:** Portfolio snapshots (include all metrics)

### 16.3: API Integration
**Proposed Combined Endpoints:**
- `GET /api/v1/risk/summary` - Combined factor + risk metrics
- `GET /api/v1/risk/factors/exposures` - Factor analysis only
- `GET /api/v1/risk/metrics` - Risk metrics only
- `POST /api/v1/risk/calculate` - Trigger both calculations

---

## 17. Combined Implementation Timeline

### Phase 1: Section 1.4.4 Implementation (3-4 days)
1. **Day 1:** Factor return calculation and data fetching
2. **Day 2:** Position return calculation and regression functions  
3. **Day 3:** Portfolio factor aggregation and database integration
4. **Day 4:** Factor calculation testing and validation

### Phase 2: Section 1.4.5 Implementation (2-3 days)
1. **Day 5:** VaR calculation with matrix operations
2. **Day 6:** Risk metrics implementation with empyrical
3. **Day 7:** Portfolio return calculation and integration testing

### Phase 3: Integration & Optimization (1-2 days)
1. **Day 8:** Combined batch job integration and API endpoints
2. **Day 9:** Performance optimization and comprehensive testing

### **Total Estimate: 7-9 days for both Sections 1.4.4 & 1.4.5**

---

## 18. Summary of Key Recommendations

### Critical Design Recommendations:
1. **60-day regression window** with 20-day minimum for factor betas
2. **Position-level betas** aggregated to portfolio using exposure weights  
3. **Delta-adjusted exposures** for options in factor calculations
4. **Identity matrix** for factor covariance with future upgrade path
5. **Batch-first architecture** with 24-hour cache TTL
6. **Quality flags** without blocking calculations
7. **Cap factor betas at ±3** to prevent outliers

### Deferred to V1.5:
1. Factor attribution and performance decomposition
2. Stress testing scenarios
3. Benchmark-relative risk metrics  
4. Real-time correlation monitoring
5. Multi-currency support

### Testing Strategy Additions:
1. Regression quality metrics (R-squared, residuals)
2. Edge cases for limited price history
3. Greeks integration validation
4. Cache invalidation scenarios
5. Data quality flag accuracy

### **Section 1.4.4: Risk Factor Analysis**
**Data Sources:**
- ETF proxy returns for 7 factors (SPY, VTV, VUG, MTUM, QUAL, SIZE, USMV)
- Mock random returns for Short Interest factor
- 60-day rolling window for regression analysis

**Calculation Method:**
- Position-level factor betas using statsmodels OLS regression
- Exposure-weighted aggregation to portfolio level
- Identity matrix for factor covariance (V1.4 scope)

**Performance Targets:**
- <30 seconds per portfolio factor calculation
- 24-hour cache TTL for factor calculations

### **Section 1.4.5: Risk Metrics**
**VaR Implementation:**
- Factor model VaR using legacy matrix multiplication formula
- 95% and 99% confidence levels with standard multipliers
- 1-day time horizon for daily risk management

**Risk Metrics:**
- empyrical library for Sharpe ratio, max drawdown, volatility
- Portfolio returns calculated from daily P&L aggregation
- 252-day historical window for risk metrics

**Performance Targets:**
- <15 seconds per portfolio risk metrics calculation
- Combined <45 seconds total per portfolio

### **Combined Integration**
**Storage Strategy:**
- Portfolio-level factor exposures stored daily
- Risk metrics added to portfolio_snapshots table
- Integrated batch job sequence (5:15 PM factors, 5:25 PM risk metrics)

**API Design:**
- Unified risk endpoints combining both factor and risk metrics
- Separate endpoints for detailed factor or risk analysis
- Real-time calculation triggers for both sections

**Testing Approach:**
- Multi-layer testing with unit, integration, and performance tests
- Legacy comparison for both factor betas and VaR calculations
- Combined workflow testing for data flow between sections

---

## 19. Additional Design Considerations

### 19.1: Factor Attribution Reporting
**Question:** Should we calculate and store factor contributions to portfolio returns?

**Context:**
- Factor attribution shows which factors drove performance
- Useful for performance analysis and reporting

**Analysis:**
- **Formula:** Factor contribution = beta × factor_return × position_weight
- **Storage:** Could add to portfolio_snapshots or separate table
- **Complexity:** Moderate - requires return decomposition

**Recommendation:** **Defer to V1.5**
- Focus on risk (forward-looking) for V1.4
- Attribution is backward-looking performance analysis
- Add TODO comment in code for future enhancement
- Keep data structures compatible for future addition

### 19.2: Stress Testing Scenarios
**Question:** Should we implement pre-defined stress scenarios beyond VaR?

**Context:**
- VaR doesn't capture tail risk well
- Stress tests show portfolio behavior in extreme events

**Potential Scenarios:**
- Market crash (-20% equity)
- Interest rate shock (+200bps)
- Volatility spike (VIX to 40)

**Recommendation:** **Defer to V1.5**
- VaR sufficient for V1.4 risk metrics
- Stress testing requires scenario definitions
- Add infrastructure comments for future
- Focus on core risk metrics first

### 19.3: Benchmark-Relative Risk Metrics
**Question:** Should risk metrics be calculated relative to a benchmark?

**Context:**
- Tracking error and information ratio need benchmark
- Active managers often report benchmark-relative metrics

**Analysis:**
- Would need benchmark selection (S&P 500?)
- Additional return series calculations
- More complex risk decomposition

**Recommendation:** **Defer to V1.5**
- Absolute risk metrics sufficient for V1.4
- Add benchmark_id field to portfolios table
- Structure code to allow easy addition
- Comment future enhancement points

### 19.4: Multi-Currency Future Considerations
**Question:** How to structure code for future multi-currency support?

**Context:**
- V1.4 is USD-only
- International portfolios need FX risk

**Preparation Steps:**
- Add currency field to return calculations
- Structure factor models to allow FX factor
- Comment FX integration points

**Recommendation:** **Minimal Preparation**
- Add TODO comments at FX integration points
- Ensure return calculations use consistent currency
- Don't add complexity, just awareness
- Keep data structures extensible

### 19.5: Batch Job Runtime Environment
**Question:** Where should the 5:00 PM factor job and 5:25 PM risk-metrics job run (e.g., Kubernetes CronJob, Celery beat, other)?

### 19.6: Database Schema for New Outputs
**Question:** What exact schema and indexing strategy will store factor exposures and risk metrics (JSONB columns in `portfolio_snapshots` vs dedicated tables)?

### 19.7: API Error-Handling & Auth Conventions
**Question:** What standard error codes and payload shapes should the new `/risk/*` endpoints follow, and how should they integrate with existing JWT/role checks?

### 19.8: Monitoring & Alerting
**Question:** Which runtime metrics and alert thresholds should be emitted for the factor and risk-metrics batch jobs?

### 19.9: Configuration Surface
**Question:** Which parameters (e.g., regression window, beta cap, cache TTL) must be environment-configurable versus hard-coded?

### 19.10: Test Dataset Size Limits
**Question:** How should the system handle portfolios exceeding 10 k positions with respect to performance targets and chunking?

---

**Next Steps:** Review these questions and recommendations with the team, then proceed with implementation of Sections 1.4.4 and 1.4.5 in sequence.
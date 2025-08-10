# SigmaSight Calculation Engine White Paper

## Executive Summary

The SigmaSight Calculation Engine provides institutional-grade portfolio analytics through a modular, scalable architecture. This document explains the mathematical foundations and business logic implemented in our calculation modules, designed for transparency and accuracy in portfolio risk management.

## Table of Contents

1. [Overview](#overview)
2. [Section 1.4.1: Market Data Calculations](#section-141-market-data-calculations)
   - [Position Valuation Engine](#position-valuation-engine)
   - [Daily P&L Calculations](#daily-pl-calculations)
   - [Market Data Integration](#market-data-integration)
3. [Section 1.4.2: Options Greeks Calculations](#section-142-options-greeks-calculations)
   - [Hybrid Calculation Architecture](#hybrid-calculation-architecture)
   - [The Five Greeks Explained](#the-five-greeks-explained)
   - [Real Calculation Implementation](#real-calculation-implementation)
   - [Mock Greeks Fallback System](#mock-greeks-fallback-system)
4. [Section 1.4.3: Portfolio Aggregation Engine](#section-143-portfolio-aggregation-engine)
   - [Core Aggregation Functions](#core-aggregation-functions)
   - [Performance Optimization](#performance-optimization)
   - [Caching Strategy](#caching-strategy)
   - [Integration with Batch Processing](#integration-with-batch-processing)
5. [Future Sections](#future-sections)

---

## Overview

The SigmaSight Calculation Engine transforms raw position and market data into actionable portfolio insights. Our approach prioritizes:

- **Accuracy**: Calculations match institutional standards
- **Transparency**: All formulas are documented and auditable
- **Performance**: Pre-computed metrics ensure rapid response times
- **Reliability**: Fallback mechanisms handle data gaps gracefully

## Section 1.4.1: Market Data Calculations

This section implements the fundamental building blocks for portfolio valuation and P&L tracking. All calculations follow standard market conventions used by prime brokers and fund administrators.

### Position Valuation Engine

**Purpose**: Calculate the current market value and exposure for each position in the portfolio.

#### Core Concepts

**Market Value vs. Exposure**
- **Market Value**: Always positive, represents the absolute dollar amount at risk
- **Exposure**: Signed value, positive for long positions, negative for short positions

**The Multiplier Effect**
- Stocks: 1 share = 1 unit (multiplier = 1)
- Options: 1 contract = 100 shares (multiplier = 100)

#### Calculation Formulas

**Market Value Calculation**
```
Market Value = |Quantity| × Current Price × Multiplier
```

**Exposure Calculation**
```
Exposure = Quantity × Current Price × Multiplier
```

**Unrealized P&L**
```
Unrealized P&L = Current Exposure - Cost Basis
Cost Basis = Quantity × Entry Price × Multiplier
```

#### Real-World Examples

**Example 1: Long Stock Position**
- Position: Long 1,000 shares of AAPL
- Entry Price: $150.00
- Current Price: $155.00
- Calculations:
  - Market Value = 1,000 × $155.00 × 1 = $155,000
  - Exposure = 1,000 × $155.00 × 1 = $155,000 (positive)
  - Cost Basis = 1,000 × $150.00 × 1 = $150,000
  - Unrealized P&L = $155,000 - $150,000 = $5,000 profit

**Example 2: Short Stock Position**
- Position: Short 500 shares of TSLA
- Entry Price: $200.00
- Current Price: $180.00
- Calculations:
  - Market Value = |−500| × $180.00 × 1 = $90,000
  - Exposure = −500 × $180.00 × 1 = −$90,000 (negative)
  - Cost Basis = −500 × $200.00 × 1 = −$100,000
  - Unrealized P&L = −$90,000 - (−$100,000) = $10,000 profit

**Example 3: Long Call Option**
- Position: Long 10 AAPL Jan 2024 $150 Call contracts
- Entry Price: $2.50 per contract
- Current Price: $3.75 per contract
- Calculations:
  - Market Value = 10 × $3.75 × 100 = $3,750
  - Exposure = 10 × $3.75 × 100 = $3,750 (positive)
  - Cost Basis = 10 × $2.50 × 100 = $2,500
  - Unrealized P&L = $3,750 - $2,500 = $1,250 profit

### Daily P&L Calculations

**Purpose**: Track day-over-day changes in position value for performance measurement and risk monitoring.

#### Methodology

Our daily P&L calculation uses a hierarchical approach to ensure accuracy:

1. **Primary Source**: Previous trading day closing price from market data cache
2. **Fallback Source**: Last recorded price on the position record
3. **Error Handling**: Zero P&L with error flag if no previous price available

#### Calculation Formulas

**Daily P&L**
```
Daily P&L = Current Position Value - Previous Position Value

Where:
Current Position Value = Quantity × Current Price × Multiplier
Previous Position Value = Quantity × Previous Price × Multiplier
```

**Daily Return**
```
Daily Return = (Current Price - Previous Price) / Previous Price
```

#### Data Integrity Features

- **Weekend/Holiday Handling**: Automatically uses last trading day price
- **Corporate Actions**: Manual adjustment capability for splits/dividends
- **New Positions**: P&L begins accumulating from T+1

### Market Data Integration

**Purpose**: Efficiently fetch, validate, and cache market prices for accurate valuations.

#### Architecture

Our market data integration follows a robust pattern:

1. **Batch Collection**: Aggregate all unique symbols across portfolios
2. **API Integration**: Fetch current prices from Polygon.io
3. **Intelligent Caching**: Store validated prices in database
4. **Fallback Logic**: Use cached prices when API fails

#### Price Hierarchy

When determining current price, the system follows this precedence:

1. Real-time price from Polygon.io (if available)
2. Most recent cached price from database
3. Last price stored on position record
4. Error state with clear messaging

#### Performance Optimization

- **Batch Processing**: Update all positions in a portfolio simultaneously
- **Symbol Deduplication**: Fetch each unique symbol only once
- **Asynchronous Operations**: Parallel processing for large portfolios
- **Database Transactions**: Atomic updates ensure consistency

### Error Handling and Edge Cases

Our calculation engine handles various edge cases gracefully:

**Missing Market Data**
- Scenario: Polygon.io API is unavailable
- Solution: Use cached prices with timestamp indication

**New Listings**
- Scenario: IPO or new option series with no history
- Solution: P&L calculations begin from first available price

**Delisted Securities**
- Scenario: Position in delisted/halted security
- Solution: Maintain last known price with warning flag

**Data Validation**
- All prices must be positive
- Quantities can be positive (long) or negative (short)
- Multipliers are predetermined by asset type
- Calculations preserve decimal precision

### Integration with Portfolio Analytics

The Section 1.4.1 calculations serve as the foundation for higher-level analytics:

**Portfolio Aggregations**
- Total Market Value = Sum of all position market values
- Gross Exposure = Sum of all position market values
- Net Exposure = Sum of all position exposures (signed)
- Long Exposure = Sum of positive exposures
- Short Exposure = |Sum of negative exposures|

**Risk Metrics (Future)**
- Position-level market values feed into VaR calculations
- Daily P&L history enables volatility measurements
- Exposure calculations support leverage monitoring

---

## Future Sections

### Section 1.4.2: Options Greeks Calculations

**Purpose**: Calculate the five primary Greeks (Delta, Gamma, Theta, Vega, Rho) for options positions using a mibian-only Black-Scholes implementation with clear error handling (no mock fallbacks).

#### Implementation Overview

Our Greeks calculation engine uses a single, deterministic path:

- **Library**: `mibian` Black-Scholes (pure Python)
- **No mock fallbacks**: Calculation errors or missing inputs return null values with warnings

#### The Five Greeks Explained

**Delta (Δ)**: Price sensitivity to underlying movement
```
Delta = ∂Option_Price / ∂Underlying_Price
```
- **Range**: -1.0 to +1.0 for options, exactly ±1.0 for stocks
- **Interpretation**: A delta of 0.6 means option price moves $0.60 for every $1 underlying move
- **Portfolio Use**: Delta-adjusted exposure calculations

**Gamma (Γ)**: Rate of change of delta
```
Gamma = ∂Delta / ∂Underlying_Price
```
- **Range**: Always positive, highest at-the-money
- **Interpretation**: Measures delta acceleration as underlying moves
- **Risk Implication**: High gamma = high convexity risk

**Theta (Θ)**: Time decay
```
Theta = ∂Option_Price / ∂Time
```
- **Units**: Daily P&L impact from time passage
- **Sign**: Negative for long options (time decay hurts), positive for short
- **Acceleration**: Increases as expiration approaches

**Vega (ν)**: Volatility sensitivity
```
Vega = ∂Option_Price / ∂Implied_Volatility
```
- **Units**: Dollar change per 1% volatility change
- **Sign**: Positive for long options, negative for short
- **Peak**: Highest at-the-money with ~45 days to expiry

**Rho (ρ)**: Interest rate sensitivity
```
Rho = ∂Option_Price / ∂Risk_Free_Rate
```
- **Units**: Dollar change per 1% interest rate change
- **Relevance**: Usually minimal for short-term options
- **Sign**: Positive for calls, negative for puts

#### Real Calculation Implementation

**Black-Scholes Model Parameters**:
- **Underlying Price**: Current market price from Polygon.io
- **Strike Price**: From position data
- **Time to Expiry**: Calculated from expiration date
- **Volatility**: Implied volatility (default: 25% if unavailable)
- **Risk-Free Rate**: Treasury rate (default: 5% if unavailable)

**Calculation Process**:
```python
# 1. Extract option parameters
option_params = {
    "strike": position.strike_price,
    "time_to_expiry": days_to_expiry / 365,
    "option_type": "c" for calls, "p" for puts,
    "underlying_symbol": position.underlying_symbol
}

# 2. Get market data
underlying_price = market_data[symbol]["current_price"]
volatility = market_data[symbol].get("implied_volatility", 0.25)
risk_free_rate = market_data.get("risk_free_rate", 0.05)

# 3. Calculate using mibian Black-Scholes
bs_model = mibian.BS([underlying_price, strike, risk_free_rate, days_to_expiry], 
                     volatility=volatility * 100)

# 4. Extract Greeks with proper unit conversions
greeks = {
    "delta": bs_model.callDelta,  # Already in correct units
    "gamma": bs_model.gamma,      # Already in correct units
    "theta": bs_model.callTheta,  # Already daily
    "vega": bs_model.vega / 100,  # Convert from per 100% to per 1%
    "rho": bs_model.callRho / 100 # Convert from per 100% to per 1%
}
```

#### No Mock Fallbacks

When real calculations fail or inputs are insufficient, Greeks are returned as null with a warning logged. This preserves data integrity and avoids introducing artificial values.

#### Quantity Scaling and Sign Conventions

**All Greeks are scaled by position quantity**:
```
Position Greeks = Per-Contract Greeks × Quantity
```

**Sign Conventions**:
- **Long positions**: Positive quantity, Greeks as calculated
- **Short positions**: Negative quantity, Greeks automatically inverted
- **Mathematical consistency**: Maintains proper portfolio aggregation

#### Special Cases Handling

**Expired Options**:
```python
if expiration_date <= current_date:
    return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
```

**Stock Positions**:
- **Delta**: ±1.0 (exact, no calculation needed)
- **Other Greeks**: 0.0 (stocks have no time decay or volatility sensitivity)

**Missing Market Data**:
- Returns null values with warning logged
- Ensures system behavior is explicit and auditable when data is unavailable

#### Error Handling and Logging

**Behavior**:
- **Debug**: Successful calculations with values
- **Warning**: Missing inputs or calculation errors; Greeks set to null
- **Error**: Unexpected exceptions during calculation

#### Integration with Portfolio System

**Batch Processing**:
- Greeks calculated during 5:30 PM daily batch job
- Stored in `position_greeks` table for API consumption
- Cached for 24 hours to avoid recalculation

**Real-Time Updates**:
- API endpoints can trigger fresh calculations
- Uses the same mibian-only engine for consistency
- Market data fetched on-demand from Polygon.io

**Portfolio Aggregation**:
- Individual position Greeks feed into Section 1.4.3
- Portfolio-level Greeks = Sum of all position Greeks
- Delta-adjusted exposure calculations for risk management

#### Performance Characteristics

**Calculation Speed**:
- **Real Greeks**: ~2-5ms per option position
- **Mock Greeks**: ~0.1ms per position
- **Batch Processing**: 1,000 positions in <10 seconds

**Memory Usage**:
- Minimal - no caching of intermediate calculations
- Market data shared across all position calculations
- Stateless functions enable parallel processing

#### Validation and Testing

**Unit Test Coverage**:
- All calculation functions with edge cases
- Mock value consistency checks
- Fallback behavior verification
- Quantity scaling accuracy

**Integration Testing**:
- End-to-end Greeks calculation pipeline
- Market data integration scenarios
- Error handling under various failure modes

**Production Monitoring**:
- Fallback usage rates tracked
- Calculation performance metrics
- Error rate monitoring with alerting

### Section 1.4.3: Portfolio Aggregation Engine

**Purpose**: Transform individual position data into portfolio-level metrics for risk management, performance analysis, and strategic decision-making. This section implements the core aggregation functions that power SigmaSight's portfolio analytics dashboard.

#### Design Philosophy

Our portfolio aggregation engine follows a **batch-first architecture** that prioritizes accuracy and performance:

- **Pre-computed Values**: Uses market values and exposures from Section 1.4.1 (no recalculation)
- **Greeks Integration**: Incorporates position-level Greeks from Section 1.4.2
- **Pandas Optimization**: Vectorized operations for sub-second performance on large portfolios
- **Comprehensive Metadata**: Rich calculation tracking for debugging and monitoring
- **Decimal Precision**: Maintains accuracy throughout all calculations

#### Core Aggregation Functions

The portfolio aggregation engine implements five fundamental functions that serve as building blocks for all portfolio analytics:

##### 1. Portfolio Exposure Calculation

**Function**: `calculate_portfolio_exposures(positions: List[Dict]) -> Dict[str, Any]`

**Purpose**: Calculate comprehensive exposure metrics across all positions in a portfolio.

**Input Requirements**:
- Pre-calculated `market_value` and `exposure` from Section 1.4.1
- Position type classification (LONG, SHORT, LC, LP, SC, SP)
- Quantity information for notional calculations

**Output Metrics**:
```python
{
    "gross_exposure": Decimal,      # Sum of absolute exposures
    "net_exposure": Decimal,        # Sum of signed exposures  
    "long_exposure": Decimal,       # Sum of positive exposures
    "short_exposure": Decimal,      # Sum of negative exposures
    "long_count": int,             # Number of long positions
    "short_count": int,            # Number of short positions
    "options_exposure": Decimal,    # Exposure from options only
    "stock_exposure": Decimal,      # Exposure from stocks only
    "notional": Decimal,           # Sum of absolute market values
    "metadata": Dict               # Calculation tracking
}
```

**Business Logic**:
- **Gross Exposure**: Measures total portfolio leverage (sum of absolute values)
- **Net Exposure**: Indicates directional bias (positive = net long, negative = net short)
- **Long/Short Breakdown**: Enables hedge ratio analysis
- **Asset Type Separation**: Distinguishes between stock and options exposure
- **Notional Exposure**: Alternative measure of portfolio size

**Example Calculation**:
```python
# Portfolio positions
positions = [
    {"exposure": Decimal("100000"), "position_type": "LONG"},      # Long stock
    {"exposure": Decimal("-50000"), "position_type": "SHORT"},     # Short stock  
    {"exposure": Decimal("25000"), "position_type": "LC"},         # Long call
    {"exposure": Decimal("-10000"), "position_type": "SP"}         # Short put
]

# Result
{
    "gross_exposure": Decimal("185000.00"),    # 100k + 50k + 25k + 10k
    "net_exposure": Decimal("65000.00"),       # 100k - 50k + 25k - 10k
    "long_exposure": Decimal("125000.00"),     # 100k + 25k
    "short_exposure": Decimal("-60000.00"),    # -50k - 10k
    "long_count": 2,
    "short_count": 2,
    "options_exposure": Decimal("35000.00"),   # 25k + 10k
    "stock_exposure": Decimal("150000.00")     # 100k + 50k
}
```

##### 2. Portfolio Greeks Aggregation

**Function**: `aggregate_portfolio_greeks(positions: List[Dict]) -> Dict[str, Decimal]`

**Purpose**: Sum position-level Greeks to calculate portfolio-level risk sensitivities.

**Input Requirements**:
- Position dictionaries with embedded `greeks` data from Section 1.4.2
- Stocks have `greeks: None` (automatically skipped)
- Options have calculated or mock Greeks values

**Aggregation Logic**:
```python
# Portfolio Greeks = Sum of Position Greeks
portfolio_delta = sum(position.greeks.delta for position in options_positions)
portfolio_gamma = sum(position.greeks.gamma for position in options_positions)
# ... etc for theta, vega, rho
```

**Sign Convention Handling**:
- **Long positions**: Greeks as calculated (positive delta for long calls)
- **Short positions**: Greeks already scaled by negative quantity
- **Mathematical consistency**: Enables accurate portfolio-level risk assessment

**Output Structure**:
```python
{
    "delta": Decimal("0.8500"),        # Portfolio delta exposure
    "gamma": Decimal("0.0320"),        # Portfolio gamma exposure  
    "theta": Decimal("-45.2500"),      # Daily time decay
    "vega": Decimal("23.7500"),        # Volatility sensitivity
    "rho": Decimal("12.5000"),         # Interest rate sensitivity
    "metadata": {
        "positions_with_greeks": 15,    # Options positions included
        "positions_without_greeks": 8,   # Stocks excluded
        "warnings": []                   # Any calculation issues
    }
}
```

**Business Applications**:
- **Delta**: Equivalent stock exposure for hedging calculations
- **Gamma**: Risk of delta changes during market moves
- **Theta**: Expected daily P&L from time decay
- **Vega**: Risk from volatility changes
- **Rho**: Risk from interest rate changes

##### 3. Delta-Adjusted Exposure Calculation

**Function**: `calculate_delta_adjusted_exposure(positions: List[Dict]) -> Dict[str, Decimal]`

**Purpose**: Calculate risk-adjusted exposure that accounts for options' actual market sensitivity.

**Methodology**:
- **Options**: `exposure × delta` (uses actual Greeks)
- **Stocks**: `exposure × 1.0` (long) or `exposure × -1.0` (short)
- **Missing Greeks**: Position excluded from calculation

**Formula**:
```python
# For each position:
if position.greeks:
    delta_adjusted = position.exposure * position.greeks.delta
else:
    # Stock position
    delta_adjusted = position.exposure * (1.0 if long else -1.0)
```

**Output Comparison**:
```python
{
    "raw_exposure": Decimal("500000.00"),           # Sum of absolute exposures
    "delta_adjusted_exposure": Decimal("325000.00"), # Delta-weighted exposure
    "metadata": {
        "positions_included": 45,      # Positions with delta info
        "positions_excluded": 3,       # Positions without delta info
        "warnings": []
    }
}
```

**Risk Management Usage**:
- **Hedging**: Tells you how much stock to buy/sell to hedge options
- **Leverage Assessment**: True market exposure vs. notional exposure
- **Risk Budgeting**: Allocate risk based on actual sensitivity, not notional

##### 4. Tag-Based Aggregation

**Function**: `aggregate_by_tags(positions: List[Dict], tag_filter: Optional[Union[str, List[str]]] = None, tag_mode: str = "any") -> Dict[str, Dict]`

**Purpose**: Group positions by strategy tags for thematic analysis and risk attribution.

**Tag System Design**:
- **Flexible Tagging**: Positions can have multiple tags
- **Strategy Tags**: e.g., "momentum", "value", "pairs-trade"
- **Sector Tags**: e.g., "tech", "healthcare", "financials"
- **Custom Tags**: User-defined for specific strategies

**Filtering Modes**:
- **"any" (OR logic)**: Position must have at least one specified tag
- **"all" (AND logic)**: Position must have all specified tags

**Aggregation Logic**:
```python
# Each position contributes to ALL its tags
position_tags = ["tech", "momentum", "large-cap"]
for tag in position_tags:
    tag_aggregations[tag].add_position(position)
```

**Output Structure**:
```python
{
    "tech": {
        "gross_exposure": Decimal("250000.00"),
        "net_exposure": Decimal("180000.00"),
        "position_count": 12,
        "long_count": 8,
        "short_count": 4
    },
    "momentum": {
        "gross_exposure": Decimal("125000.00"),
        "net_exposure": Decimal("95000.00"),
        "position_count": 6,
        "long_count": 5,
        "short_count": 1
    },
    "metadata": {
        "tag_filter": ["tech", "momentum"],
        "tag_mode": "any",
        "total_positions": 25,
        "tags_found": 2
    }
}
```

**Business Applications**:
- **Strategy Attribution**: Which strategies are driving performance?
- **Risk Concentration**: Are we overexposed to specific themes?
- **Allocation Analysis**: How much capital is in each strategy?

##### 5. Underlying Symbol Aggregation

**Function**: `aggregate_by_underlying(positions: List[Dict]) -> Dict[str, Dict]`

**Purpose**: Group all positions (stocks + options) by underlying symbol for comprehensive risk analysis.

**Critical for Options Risk**:
- **Concentration Risk**: Total exposure to single underlying
- **Complex Strategies**: Covered calls, protective puts, straddles
- **Hedge Analysis**: How well are stock positions hedged by options?

**Symbol Resolution Logic**:
```python
# Determine underlying symbol
if position_type in ["LC", "LP", "SC", "SP"]:
    underlying = position.underlying_symbol
else:
    underlying = position.symbol
```

**Output Structure**:
```python
{
    "AAPL": {
        "gross_exposure": Decimal("150000.00"),
        "net_exposure": Decimal("125000.00"),
        "position_count": 4,
        "stock_count": 1,           # Stock positions
        "option_count": 3,          # Options positions
        "call_count": 2,            # Call options
        "put_count": 1,             # Put options
        "greeks": {                 # Aggregated Greeks for this underlying
            "delta": Decimal("0.75"),
            "gamma": Decimal("0.023"),
            "theta": Decimal("-12.50"),
            "vega": Decimal("8.75"),
            "rho": Decimal("3.25")
        }
    },
    "metadata": {
        "underlyings_found": 15,
        "total_positions": 48
    }
}
```

**Risk Analysis Applications**:
- **Concentration Limits**: Ensure no single underlying exceeds risk limits
- **Hedge Effectiveness**: Compare stock delta vs. options delta
- **Strategy Complexity**: Identify multi-leg options strategies

#### Performance Optimization

**Pandas Vectorization**:
```python
# Convert to DataFrame for efficient operations
df = pd.DataFrame(positions)
df['exposure'] = df['exposure'].apply(lambda x: Decimal(str(x)))

# Vectorized calculations
gross_exposure = df['exposure'].apply(abs).sum()
net_exposure = df['exposure'].sum()
```

**Performance Benchmarks**:
- **1,000 positions**: ~50ms per aggregation function
- **10,000 positions**: ~500ms per aggregation function
- **Target met**: <1 second for 10,000 positions across all functions

#### Caching Strategy

**Time-Based LRU Cache**:
```python
@timed_lru_cache(seconds=60, maxsize=128)
def calculate_portfolio_exposures(positions_tuple):
    # Function implementation
```

**Cache Implementation**:
- **TTL**: 60 seconds (configurable)
- **Custom Decorator**: functools.lru_cache doesn't support TTL natively
- **Cache Clearing**: Manual cache clearing for real-time updates

#### Error Handling and Edge Cases

**Missing Data Handling**:
- **Missing market_value**: Auto-derived from exposure field
- **Missing Greeks**: Options positions excluded from Greeks aggregation
- **Empty portfolio**: Returns zero values with appropriate metadata

**Data Type Conversion**:
- **String to Decimal**: Automatic conversion for API compatibility
- **None values**: Converted to Decimal("0") for calculations
- **Malformed data**: Graceful handling with warning logs

**Metadata Tracking**:
```python
"metadata": {
    "calculated_at": "2025-07-17T14:38:57.426128Z",
    "position_count": 45,
    "positions_excluded": 3,
    "warnings": ["3 positions excluded from Greeks aggregation"]
}
```

#### Integration with Batch Processing

**Nightly Batch Jobs**:
1. **5:30 PM EST**: Calculate portfolio aggregations for all users
2. **Storage**: Summary metrics stored in `portfolio_snapshots` table
3. **Caching**: Results cached for fast API response times

**Batch Job Integration**:
```python
# Daily batch job pseudocode
for portfolio in active_portfolios:
    positions = load_positions_with_greeks(portfolio.id)
    
    # Calculate all aggregations
    exposures = calculate_portfolio_exposures(positions)
    greeks = aggregate_portfolio_greeks(positions)
    delta_adjusted = calculate_delta_adjusted_exposure(positions)
    
    # Store in database
    create_portfolio_snapshot(portfolio.id, exposures, greeks, delta_adjusted)
```

#### API Integration

**Real-Time Calculations**:
- **On-Demand**: API endpoints can trigger fresh calculations
- **Filtering**: Support for query parameters (?tag=tech, ?underlying=AAPL)
- **Response Format**: JSON with Decimal-to-float conversion

**API Response Structure**:
```python
{
    "summary": {
        "gross_exposure": 185000.00,
        "net_exposure": 65000.00,
        "position_count": 45
    },
    "greeks": {
        "delta": 0.8500,
        "gamma": 0.0320,
        "theta": -45.2500
    },
    "by_tag": {
        "tech": {"gross_exposure": 125000.00, ...},
        "momentum": {"gross_exposure": 87500.00, ...}
    },
    "by_underlying": {
        "AAPL": {"gross_exposure": 75000.00, ...},
        "MSFT": {"gross_exposure": 62500.00, ...}
    },
    "metadata": {
        "calculated_at": "2025-07-17T14:38:57Z",
        "cache_ttl": 60,
        "warnings": []
    }
}
```

#### Testing and Validation

**Comprehensive Test Suite**:
- **29 Unit Tests**: Cover all functions and edge cases
- **Performance Tests**: Validate <1s target for 10,000 positions
- **Edge Cases**: Empty portfolios, missing data, malformed inputs
- **Cache Behavior**: TTL expiration, cache clearing

**Test Scenarios**:
1. **Mixed Portfolio**: 50 stocks + 50 options across sectors
2. **Edge Cases**: Empty portfolio, single position, all long/short
3. **Missing Data**: Positions without Greeks, malformed data
4. **Large Portfolio**: 10,000 positions for performance validation
5. **Complex Tags**: Multiple overlapping tags, filtering modes

#### Future Enhancements

**Documented in Code**:
- **Historical Analysis**: Add `as_of_date` parameter for historical aggregations
- **Sector/Industry**: Implement sector aggregation (currently use tags)
- **Real-Time Updates**: Stream-based updates for live portfolios
- **Currency Exposure**: Multi-currency portfolio support
- **Concentration Metrics**: Automated concentration risk analysis

#### Business Value

**Risk Management**:
- **Exposure Monitoring**: Real-time portfolio leverage tracking
- **Concentration Risk**: Identify overexposure to single names/sectors
- **Hedge Effectiveness**: Measure how well positions offset each other

**Performance Attribution**:
- **Strategy Analysis**: Which strategies are driving returns?
- **Greeks Impact**: How much P&L comes from time decay vs. market moves?
- **Allocation Efficiency**: Optimize capital allocation across strategies

**Regulatory Compliance**:
- **Risk Limits**: Automated monitoring of exposure limits
- **Reporting**: Generate regulatory reports from aggregated data
- **Audit Trail**: Complete calculation history with metadata

### Section 1.4.4: Risk Factor Analysis
*Coming Soon*
- Multi-factor model implementation
- Factor attribution analysis
- Correlation analysis

### Section 1.4.5: Advanced Risk Metrics
*Coming Soon*
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Stress testing scenarios

---

## Appendix: Technical Implementation

For technical readers interested in the implementation details:

- **Language**: Python 3.11 with type hints
- **Precision**: Decimal type for all monetary calculations
- **Database**: PostgreSQL with ACID compliance
- **Testing**: Comprehensive unit and integration tests
- **Performance**: Sub-second calculations for 1,000+ positions

---

*Last Updated: July 2025*
*Version: 1.4.3 - Portfolio Aggregation Engine Complete*
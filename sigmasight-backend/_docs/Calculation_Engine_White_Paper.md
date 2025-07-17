# SigmaSight Calculation Engine White Paper

## Executive Summary

The SigmaSight Calculation Engine provides institutional-grade portfolio analytics through a modular, scalable architecture. This document explains the mathematical foundations and business logic implemented in our calculation modules, designed for transparency and accuracy in portfolio risk management.

## Table of Contents

1. [Overview](#overview)
2. [Section 1.4.1: Market Data Calculations](#section-141-market-data-calculations)
   - [Position Valuation Engine](#position-valuation-engine)
   - [Daily P&L Calculations](#daily-pl-calculations)
   - [Market Data Integration](#market-data-integration)
3. [Future Sections](#future-sections)

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
*Coming Soon*
- Delta, Gamma, Theta, Vega calculations
- Portfolio-level Greeks aggregation
- Greeks-based risk limits

### Section 1.4.3: Enhanced Portfolio Aggregation
*Coming Soon*
- Sector/Industry breakdowns
- Currency exposure analysis
- Concentration metrics

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
*Version: 1.4 - Section 1.4.1 Implementation*
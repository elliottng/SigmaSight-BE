# Analytical Architecture and Library Decisions V1.4

## Overview
This document details the technical rationale behind our quantitative library choices and their alignment with institutional practices in quantitative finance.

## Quantitative Library Stack

### Tier 1: Core Calculations

#### py_vollib
- **Purpose**: Options pricing and Greeks calculations
- **Implementation**: Black-Scholes model with analytical Greeks
- **Institutional Heritage**: Created by Gammon Capital Management
- **Why Not QuantLib**: QuantLib is better suited for fixed income and exotic derivatives; overkill for listed equity options

#### empyrical  
- **Purpose**: Portfolio risk and performance metrics
- **Implementation**: Sharpe ratio, max drawdown, VaR, Calmar ratio
- **Institutional Heritage**: Developed by Quantopian (Point72/Bessemer backed)
- **Production Use**: Core to Quantopian's platform serving thousands of quants

#### statsmodels
- **Purpose**: Factor exposure calculations via regression
- **Implementation**: OLS regression for factor betas
- **Institutional Heritage**: Used by Federal Reserve, academic finance
- **Why This Matters**: Regulatory acceptance of methodology

### Tier 2: Data Infrastructure

#### pandas/numpy
- **Purpose**: Time series data manipulation and matrix operations
- **Evidence of Use**: 
  - Two Sigma contributions to pandas
  - AQR public discussions of pandas usage
  - Man Group's ArcticDB built on pandas

### Tier 3: Market Data

#### polygon-api-client
- **Purpose**: Real-time and historical market data
- **Why**: Institutional-grade data quality, reasonable pricing

#### yfinance
- **Purpose**: GICS sector/industry classification only
- **Limitation**: Not for pricing data (use Polygon)

## Calculation Methodology Alignment

### Factor Model (Industry Standard)
```python
# Our approach matches institutional factor models
- Market Beta (SPY) - Standard CAPM
- Value (VTV) - Fama-French value factor  
- Growth (VUG) - Growth factor
- Momentum (MTUM) - Carhart momentum
- Quality (QUAL) - Quality factor (profitability/earnings)
- Size (SLY) - Fama-French size factor
- Low Volatility (USMV) - Low vol anomaly
- Short Interest - Custom factor
```

### Greeks Calculation (Black-Scholes Standard)
- Using same model as CBOE for listed options
- Historical volatility proxy common when IV unavailable
- Matches Bloomberg/Reuters Greeks for verification

### Risk Metrics (Industry Conventions)
- 252 trading days annualization
- 95% and 99% VaR (regulatory standard)
- Sharpe ratio with risk-free rate parameter
- Maximum drawdown (peak-to-trough)

## Implementation Patterns from Hedge Funds

### 1. Calculation Layer Separation
```
Market Data → Core Calculations → Risk Aggregation → Reporting
     ↓              ↓                    ↓              ↓
  Polygon      py_vollib           empyrical      Database
              statsmodels            numpy
```

### 2. Fallback Pattern (Production Best Practice)
```python
try:
    return real_calculation()
except:
    log_warning()
    return mock_calculation()
```

### 3. Batch vs Real-time Separation
- **Batch**: Factor exposures, risk metrics (like most funds)
- **Real-time**: Positions, market values (for trading)

## Validation Against Industry Standards

### Greeks Validation
- Compare py_vollib output with:
  - Bloomberg Terminal OVDV function
  - Interactive Brokers option analytics
  - CBOE published theoretical values

### Factor Model Validation
- Regression methodology matches:
  - Barra risk models
  - Axioma factor models
  - Academic literature (Fama-French)

### Risk Metrics Validation
- Empyrical calculations align with:
  - CFA Institute standards
  - GIPS performance reporting
  - Basel III risk requirements

## Future Architecture Evolution

### Phase 2 Enhancements
1. **Implied Volatility Surface**
   - Add volatility smile modeling
   - Term structure of volatility

2. **Advanced Factor Models**
   - Dynamic factor loading
   - Sector-neutral factors
   - Custom factor construction

3. **Real-time Greeks**
   - Streaming calculations
   - Scenario analysis engine

### Phase 3 Institutional Features
1. **Multi-Asset Support**
   - Fixed income analytics
   - FX hedging calculations

2. **Advanced Risk Models**
   - Monte Carlo VaR
   - Stress testing framework
   - Correlation breakdowns

## Appendix: Library Version Requirements

```toml
[tool.poetry.dependencies]
# Core Calculations
py_vollib = "^1.0.1"
empyrical = "^0.5.5"
statsmodels = "^0.14.0"
mibian = "^0.1.3"  # Fallback for Greeks

# Data Infrastructure  
pandas = "^2.0.0"
numpy = "^1.24.0"
scipy = "^1.10.0"

# Market Data
polygon-api-client = "^1.12.0"
yfinance = "^0.2.18"
```

## References

1. **Black-Scholes Model**: Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
2. **Factor Models**: Fama, E. F., & French, K. R. (1993). "Common risk factors in the returns on stocks and bonds"
3. **Performance Metrics**: Bacon, C. (2008). "Practical Portfolio Performance Measurement and Attribution"
4. **Risk Management**: Jorion, P. (2007). "Value at Risk: The New Benchmark for Managing Financial Risk"

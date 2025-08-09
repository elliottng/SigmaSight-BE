# Factor Exposure Model Redesign Document

**Created**: 2025-08-09  
**Status**: PROPOSAL  
**Author**: SigmaSight Engineering Team  
**Decision Required**: Architectural change to factor exposure calculation

---

## Executive Summary

The current factor exposure model has a fundamental mathematical flaw where each factor claims 100% of the portfolio value, leading to factor exposures that sum to 500-700% of actual portfolio value. This document analyzes the legacy approach, current implementation, explains the flaw, and proposes three alternative approaches for consideration.

---

## Legacy Approach (Original Reference Implementation)

### Location
- **Files**: `legacy_analytics_for_reference/factors_utils.py`, `reporting_plotting_analytics.py`, `var_utils.py`
- **Method**: Position-level beta calculation with proper aggregation

### Key Components

#### 1. Position Beta Calculation (`factors_utils.py`)
```python
def calculate_position_betas(
    factor_returns: pd.DataFrame,
    position_returns: pd.DataFrame,
) -> pd.DataFrame:
    # Calculate beta for each position against each factor
    # Uses covariance method: β = Cov(position, factor) / Var(factor)
    numerator = calculate_beta_factor_numerator(merged_returns)  # Cov
    denominator = calculate_beta_factors_denominator(merged_returns)  # Var
    beta_factors = numerator / denominator
```

#### 2. Portfolio Factor Exposure (`reporting_plotting_analytics.py`)
```python
def calculate_portfolio_exposure(
    positions_df: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    factors_df: pd.DataFrame,
):
    # Calculate portfolio exposure to each factor
    for factor in factor_names:
        factor_beta = filtered_factor_betas[factor]
        # Key: Uses exposure percentage weights, not dollar amounts
        factor_exposure = np.dot(positions_df["exposure%"], factor_beta)
        portfolio_exposure.append({"Factor": factor, "Exposure": factor_exposure})
```

#### 3. Risk Contribution Calculation
```python
# Calculate portfolio's forward looking volatility
factor_covariance = matrix_cov[factor_names].loc[factor_names]
factor_exposures = portfolio_exposure["exposure"].values
# Calculate contributions to volatility
risk_contributions = factor_exposures * np.dot(
    factor_covariance, factor_exposures.T
)
```

### Legacy Model Characteristics

1. **Position-Level Foundation**: Calculated betas for each position individually
2. **Weighted Aggregation**: Used position exposure percentages (weights) for aggregation
3. **Risk-Based Attribution**: Factor exposures represented risk contributions, not dollar amounts
4. **Covariance Integration**: Used factor covariance matrix for risk contribution calculations
5. **Percentage-Based**: Exposures were percentages, not dollar amounts

### Legacy Formula Summary
```
Position Beta[i,f] = Cov(Position[i] returns, Factor[f] returns) / Var(Factor[f] returns)
Portfolio Factor Exposure[f] = Σ(Position Weight[i] × Position Beta[i,f])
Risk Contribution[f] = Factor Exposure[f] × Cov Matrix × Factor Exposures
```

---

## Evolution from Legacy to Current

### What Changed
The transition from the legacy system to the current implementation introduced several changes:

1. **From Percentage to Dollars**: Legacy used percentage weights; current attempts dollar exposures
2. **Lost Position Attribution**: Legacy maintained position-level detail; current aggregates too early
3. **Misinterpreted "Exposure"**: Legacy treated exposure as risk weight; current treats it as notional value
4. **Simplified Risk Model**: Legacy used covariance matrix; current uses direct beta multiplication

### Where It Went Wrong
The critical error occurred when trying to show dollar exposure values:
- **Intent**: Show how many dollars are exposed to each factor risk
- **Implementation Error**: Multiplied each factor beta by the ENTIRE portfolio value
- **Result**: Each factor claims 100% of portfolio, leading to 500-700% total exposure

### The Conceptual Confusion
The fundamental confusion is between:
- **Risk Exposure** (what percentage of portfolio risk comes from each factor)
- **Dollar Exposure** (how many dollars are "attributed" to each factor)

Since factors are overlapping (a stock can have exposure to multiple factors), the notion of "dollar exposure" to a factor is inherently problematic without a proper attribution model.

---

## Current Implementation (Flawed)

### Location
- **File**: `app/calculations/factors.py`
- **Function**: `aggregate_portfolio_factor_exposures()`
- **Lines**: 674-675

### Current Formula
```python
# Each factor gets the entire portfolio value
portfolio_value = portfolio_exposures.get("gross_exposure", Decimal('0'))
exposure_dollar = float(beta_value) * float(portfolio_value)
```

### Data Flow
1. Calculate portfolio beta for each factor (Market, Value, Size, etc.)
2. Multiply each beta by the ENTIRE gross exposure
3. Store as `exposure_dollar` in FactorExposure table
4. Display in reports

### Example with Demo Individual Portfolio
- **Gross Exposure**: $485,000
- **Factor Betas**:
  - Market Beta: 0.77
  - Value: 0.91
  - Size: 0.77
  - Momentum: 0.67
  - Growth: 0.66
  - Quality: 0.85
  - Low Volatility: 0.93

**Current Calculation**:
- Market: 0.77 × $485,000 = $373,450
- Value: 0.91 × $485,000 = $441,350
- Size: 0.77 × $485,000 = $373,450
- ... (each factor gets 100% of portfolio)
- **Total**: ~$2,700,000 (557% of actual portfolio!)

---

## Why This Is Wrong

### Mathematical Issues

1. **Non-Additive**: Factor exposures should represent decomposition of risk, not multiply it
2. **Overlapping Claims**: Each factor claims 100% of portfolio, ignoring others
3. **Stress Test Amplification**: When multiple factors are shocked, losses compound unrealistically
4. **Meaningless Aggregation**: Summing factor dollars has no financial interpretation

### Business Impact

1. **Risk Overstatement**: Reports show 5-7x more exposure than exists
2. **Stress Test Distortion**: All scenarios hit 99% loss cap, no differentiation
3. **Client Confusion**: "How can my $500K portfolio have $2.7M in factor exposure?"
4. **Regulatory Concerns**: Incorrect risk reporting could have compliance implications

---

## Proposed Solutions

### Option A: Weighted Allocation (Simple)

**Concept**: Allocate portfolio proportionally based on relative beta magnitudes

**Formula**:
```python
# Calculate total absolute beta
total_beta = sum(abs(beta) for beta in all_factor_betas)

# Allocate proportionally
for factor in factors:
    exposure_dollar = gross_exposure * abs(beta[factor]) / total_beta
```

**Example**:
- Total Beta: |0.77| + |0.91| + ... = 5.56
- Market: $485,000 × 0.77 / 5.56 = $67,190
- Value: $485,000 × 0.91 / 5.56 = $79,410
- **Total**: $485,000 (exactly 100%)

**Pros**:
- Simple to implement
- Factor exposures sum to gross exposure
- Easy to explain

**Cons**:
- Loses sign information (all positive)
- Not based on actual position contributions
- Arbitrary weighting scheme

---

### Option B: Position-Level Attribution (Recommended)

**Concept**: Calculate each position's contribution to each factor exposure

**Formula**:
```python
# For each factor f and position p:
position_factor_contribution[f][p] = position_exposure[p] * position_beta[p][f]

# Aggregate to portfolio level
factor_dollar_exposure[f] = sum(position_factor_contribution[f])

# Portfolio beta (for reporting)
portfolio_beta[f] = factor_dollar_exposure[f] / gross_exposure
```

**Implementation Steps**:
1. Calculate position-level betas for each factor
2. Multiply position exposure (signed) by position beta
3. Sum contributions across positions for each factor
4. Store both dollar exposure and portfolio beta

**Example with 3 Positions**:
```
Position 1 (AAPL): $100K exposure
  - Market beta: 1.2 → Market contribution: $120K
  - Value beta: 0.3 → Value contribution: $30K

Position 2 (XOM): $50K exposure  
  - Market beta: 0.8 → Market contribution: $40K
  - Value beta: 1.5 → Value contribution: $75K

Position 3 (TLT): -$30K exposure (short)
  - Market beta: -0.5 → Market contribution: $15K
  - Value beta: 0.2 → Value contribution: -$6K

Portfolio Factor Exposures:
  - Market: $120K + $40K + $15K = $175K
  - Value: $30K + $75K - $6K = $99K
```

**Pros**:
- Mathematically correct attribution
- Preserves sign information
- Based on actual position characteristics
- Can trace exposure to specific holdings

**Cons**:
- More complex implementation
- Requires position-level factor betas
- Factor exposures won't sum to gross (but shouldn't)

---

### Option C: Document as "Notional Exposure" (Minimal Change)

**Concept**: Keep current calculation but rebrand as "notional" or "beta-adjusted" exposure

**Changes**:
- Rename `exposure_dollar` to `notional_exposure`
- Update reports to clarify these are not additive
- Add explanation: "Represents portfolio value scaled by factor sensitivity"
- Remove summation across factors

**Pros**:
- No calculation changes needed
- Preserves existing data
- Quick to implement

**Cons**:
- Doesn't fix underlying issue
- Still causes stress test problems
- May not satisfy regulatory requirements
- Confusing to users

---

## Current Database State Assessment

### What We Already Have
Based on database analysis, we already store most of the data needed:

1. **Position-Level Factor Betas** ✅
   - Table: `PositionFactorExposure`
   - Field: `exposure_value` (beta coefficient for each position-factor pair)
   - Coverage: 1,348 records across all positions and factors
   - Quality tracking: `quality_flag` field indicates data reliability

2. **Portfolio-Level Factor Exposures** ✅
   - Table: `FactorExposure` 
   - Fields: `exposure_value` (portfolio beta), `exposure_dollar` (currently flawed)
   - Coverage: 83 records across portfolios and dates

3. **Position Market Values** ✅
   - Table: `Position`
   - Field: `market_value` (quantity × price × multiplier)
   - Always positive, even for short positions

### What We DON'T Have
- **Position signed exposures**: Market values don't reflect short position signs
- **Delta-adjusted exposures**: Would require Greeks integration
- **Position factor dollar contributions**: Not stored (position_exposure × beta)

### Implementation Without Schema Changes
**Option B can be implemented with NO schema changes:**
1. Calculate signed exposure: `market_value × (-1 if SHORT/SC/SP else 1)`
2. Calculate contribution: `signed_exposure × position_beta`
3. Sum contributions by factor for portfolio dollar exposure
4. Update `FactorExposure.exposure_dollar` calculation logic

---

## Recommendation

**We recommend Option B: Position-Level Attribution** for the following reasons:

1. **Correctness**: Only mathematically sound approach
2. **Traceability**: Can explain which positions drive each factor
3. **Flexibility**: Supports more sophisticated risk analytics
4. **Industry Standard**: Aligns with professional risk systems
5. **Legacy Alignment**: Returns to the conceptually correct approach from the original implementation
6. **Proven Model**: The legacy system had the right conceptual framework, just needed enhancement

### Why Option B Over Legacy Approach
While the legacy approach was conceptually correct, Option B improves upon it by:
- Maintaining both percentage and dollar representations
- Storing position-level contributions for full attribution
- Supporting more granular analysis and reporting
- Integrating better with modern database architecture

---

## Implementation Plan

### Phase 1: Fix Calculation Logic (NO SCHEMA CHANGES)
1. Update `aggregate_portfolio_factor_exposures()` in `factors.py`:
   - Calculate signed position exposures
   - Multiply by position betas from `PositionFactorExposure`
   - Sum contributions for portfolio dollar exposure
2. Fix sign handling in position exposure calculations
3. Update stress test to use corrected logic

### Phase 2: Report Updates
1. Update report generator to handle signed exposures correctly
2. Add position-level factor attribution section
3. Update documentation and tooltips

### Phase 3: Optional Schema Enhancements (Future)
1. Add `PositionFactorExposure.dollar_contribution` field (optional)
2. Add `Position.signed_exposure` field for clarity (optional)
3. Migration scripts if schema changes are approved

### Phase 4: Validation & Migration
1. Recalculate historical data with new logic
2. Provide comparison reports (old vs new)
3. Verify stress test scenarios show differentiation

---

## Breaking Changes

### API Changes
- `factor_exposures.exposure_dollar` semantics change
- New field: `factor_exposures.position_contributions`
- Stress test results will change significantly

### Report Changes
- Factor exposures will no longer sum to multiples of portfolio
- Stress test scenarios will show realistic differentiation
- New attribution reports available

### Database Changes
- New tables for position-level attribution
- Updated indices for performance
- Migration required for historical data

---

## Questions for Stakeholders

1. **Reporting Preference**: Should factor exposures be shown as dollars, percentages, or both?
2. **Historical Data**: Should we recalculate all historical factor exposures?
3. **Transition Period**: How long should we maintain both calculations?
4. **Client Communication**: How do we explain the change to existing users?
5. **Regulatory Impact**: Are there compliance implications for the change?

---

## Appendix: Technical Details

### Current Database Schema
```sql
-- Current (flawed)
CREATE TABLE factor_exposures (
    portfolio_id UUID,
    factor_id UUID,
    calculation_date DATE,
    exposure_value DECIMAL(16,6),  -- Beta
    exposure_dollar DECIMAL(20,2)   -- Beta × Gross (wrong)
);
```

### Proposed Schema
```sql
-- Position-level contributions
CREATE TABLE position_factor_contributions (
    position_id UUID,
    factor_id UUID,
    calculation_date DATE,
    position_beta DECIMAL(16,6),
    dollar_contribution DECIMAL(20,2)
);

-- Portfolio-level aggregation
CREATE TABLE factor_exposures_v2 (
    portfolio_id UUID,
    factor_id UUID,
    calculation_date DATE,
    portfolio_beta DECIMAL(16,6),
    dollar_exposure DECIMAL(20,2),      -- Sum of position contributions
    contributing_positions INTEGER,      -- Count of positions
    largest_contributor_id UUID         -- For attribution
);
```

### Sample Queries

**Current (Flawed)**:
```sql
SELECT 
    f.name,
    fe.exposure_value as beta,
    fe.exposure_dollar  -- This is beta × entire portfolio!
FROM factor_exposures fe
JOIN factor_definitions f ON fe.factor_id = f.id
WHERE portfolio_id = ? AND calculation_date = ?;
```

**Proposed**:
```sql
-- Portfolio-level summary
SELECT 
    f.name,
    fe.portfolio_beta,
    fe.dollar_exposure,  -- Sum of position contributions
    fe.contributing_positions
FROM factor_exposures_v2 fe
JOIN factor_definitions f ON fe.factor_id = f.id
WHERE portfolio_id = ? AND calculation_date = ?;

-- Position-level attribution
SELECT 
    p.symbol,
    f.name as factor,
    pfc.position_beta,
    pfc.dollar_contribution
FROM position_factor_contributions pfc
JOIN positions p ON pfc.position_id = p.id
JOIN factor_definitions f ON pfc.factor_id = f.id
WHERE p.portfolio_id = ? 
ORDER BY ABS(pfc.dollar_contribution) DESC;
```

---

## Decision Required

Please review the three options and provide feedback on:
1. Which approach to implement
2. Timeline constraints
3. Migration strategy for existing data
4. Client communication plan

**Target Decision Date**: [To be determined]  
**Implementation Timeline**: 3-5 days after approval
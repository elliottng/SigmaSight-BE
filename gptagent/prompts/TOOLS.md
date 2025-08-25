# Tool Specifications (Backend-Aligned)

All tools **fetch data from backend**. GPT never recomputes.

## get_portfolio_snapshot
Inputs: `{ portfolio_id, as_of?: date }`
Outputs: net/gross exposures, totals, diversification score

## get_positions
Inputs: `{ portfolio_id }`
Outputs: positions, greeks, tags

## get_factor_exposures
Inputs: `{ portfolio_id, calc_date?: date }`
Outputs: factor loadings (from backend)

## get_factor_risk_contrib
Inputs: `{ portfolio_id, calc_date?: date }`
Outputs: risk contribution per factor

## get_var
Inputs: `{ portfolio_id, method, horizon_days, cl }`
Outputs: `{ var, es, method }`

## get_stress_results
Inputs: `{ portfolio_id, scenarios: [] }`
Outputs: scenario P&L impacts (backend-calculated)

## get_short_metrics
Inputs: `{ portfolio_id }`
Outputs: short interest %, borrow rate, days-to-cover

## get_modeling_session
Inputs: `{ portfolio_id | session_id }`
Outputs: current modeling session snapshot + impacts

## get_exports
Inputs: `{ portfolio_id }`
Outputs: available export history

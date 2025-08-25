# Data Mapping — DB v1.4 → GPT Inputs (Backend-Aligned)

## Rule
All metrics come from **backend DB + scripts**. GPT never queries DB directly.

## Example Mappings
- Exposures → `portfolio_snapshots`
- Greeks → `position_greeks`
- Factor Exposures → `portfolio_factor_exposures`
- Factor Risk Contribution → `factor_covariance_matrix`
- Stress Results → `stress_scenarios`, `stress_scenario_shocks`
- Short Metrics → `short_selling_metrics`
- Modeling Sessions → `modeling_session_snapshots`
- Exports → `export_history`

## Usage
GPT receives JSON payloads already computed by backend. Its job:
1. Validate against schema
2. Narrate insights
3. Flag missing or stale data

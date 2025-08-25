# Risk Page — Factor & Forward-Looking Analytics

Route: `/risk/[id]`

## Sections
1. **Factor Exposures**
   - Bar list of betas; highlight top +/– tilts
   - Toggle: `exposures` vs `riskContribution`
   - Source: `GET /portfolio/:id/factors`

2. **Forward-Looking Risk**
   - VaR / ES cards
   - Controls: method (historical/parametric/mc), horizon, conf
   - Source: `GET /portfolio/:id/risk/var?horizon=1d&conf=0.99&method=historical`

3. **Stress Tests (Optional)**
   - Scenarios dropdown: `COVID-2020`, `Rates +75bps`, `Oil Shock`
   - Source: `POST /whatif/model` with `scenarioId` or dedicated endpoint

4. **Aggregate Greeks (if options)**
   - Delta / Gamma / Vega / Theta totals
   - Source: either extended `summary` or a new `/risk/greeks`

## UX Rules
- Always show **as-of** timestamps.
- If VaR method changes, annotate notes (lookback, assumptions).
- Provide quick actions: “Model hedge” -> prefill What-If on Chat page.


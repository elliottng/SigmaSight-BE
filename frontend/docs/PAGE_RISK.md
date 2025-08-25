# /risk — Factor Risks & Scenarios

## Sections
1. **Factor Exposures** — bar chart of exposures (top 6), table with units/date
2. **Risk Contribution** — stacked bar of variance share (top 5 + residual)
3. **Scenarios** — tiles with name, pnl_pct, rank; link to drivers
4. **Short Metrics** — table: symbol, short_interest_pct, days_to_cover, borrow_rate

## API
- `GET /api/portfolio/:id/factors`
- `GET /api/portfolio/:id/factor-risk`
- `GET /api/portfolio/:id/stress`
- `GET /api/portfolio/:id/short`

## Acceptance
- Charts powered by Recharts; accessible tables below charts
- Dates and units shown; "as of" visible
- No recomputation; display backend numbers as-is

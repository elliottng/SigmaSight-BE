# State, API Clients, and Caching

## State
- `usePortfolioStore`: { portfolioId, asOf, filters (view, period, index) }
- `useRiskStore`: { selectedFactors, scenarioSet, lookback }
- `useTaggingStore`: { edits: Record<positionId, { targetPrice?, tags[] }> }

## API Clients (Backend-Aligned)
- `GET /api/portfolio/:id/snapshot` → proxy to backend `get_portfolio_snapshot`
- `GET /api/portfolio/:id/positions` → `get_positions`
- `GET /api/portfolio/:id/factors` → `get_factor_exposures`
- `GET /api/portfolio/:id/factor-risk` → `get_factor_risk_contrib`
- `GET /api/portfolio/:id/stress` → `get_stress_results`
- `GET /api/portfolio/:id/short` → `get_short_metrics`
- `GET /api/portfolio/:id/targets` → read/write targets & tags (via backend)
- `POST /api/gpt/analyze` → calls GPT with portfolio_id and prompt

Use SWR/React Query for caching with keys `["snapshot", id]`, etc.

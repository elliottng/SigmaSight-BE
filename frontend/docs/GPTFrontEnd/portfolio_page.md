# Portfolio Page — Wiring & Behavior

Route: `/portfolio/[id]`

## Purpose
Display performance summary, attribution, and benchmark comparison. Integrate with your existing dashboard component.

## Data Sources
- `GET /v1/portfolio/:id/summary?window=1m`
- `GET /v1/portfolio/:id/attribution?window=1m&groupBy=security`
- Optional: `GET /v1/benchmarks` (static or config)

## Component Tree
- Header: title + selectors (View: portfolio/longs/shorts; Period)
- **MetricGrid**: Return, Ann. Vol, Sharpe, Sortino
- **AttributionGrid**: contributors / detractors (cards)
- **ContributionGrid**: factors & industries (from `factors` endpoint if available)

## Notes on Your Provided Code
- Replace mock generators (`genPerfMetrics`, etc.) with hooks that fetch from the API.
- Use Suspense + SWR/React Query; cache keyed by `[portfolioId, window, view]`.
- If `groupBy=security`, map `items` to your `AttributionTickerCard` values.

## Error & Loading
- Skeleton cards for metrics & lists.
- On error, show retry and emit `tool_error` telemetry.


# /portfolio — Portfolio Analytics

## Goal
Display performance, attribution, and contributions. Use provided component.

## Component Contract
`<PerformanceAnalyticsDashboard />` expects props or internal hooks. Adjust to fetch from backend.

### Expected Data (from backend)
- Performance vs index (return, vol, sharpe, sortino) for chosen `period`
- Attribution: contributors/detractors by book (longs/shorts)
- Contributions: factor & industry contributions

## Agent Tasks
- Replace mock generators with API calls:
  - `GET /api/portfolio/:id/snapshot?period=daily`
  - `GET /api/portfolio/:id/attribution?view=portfolio&period=daily`
  - `GET /api/portfolio/:id/contributions?period=daily`
- Wire selects to refetch on change (view, period, index)
- Keep `MetricCard`, `AttributionTickerCard`, `ContributionCard` as-is for styling

## Acceptance
- Loading skeletons, error toasts
- No derived math beyond basic formatting
- Works with empty states (no shorts, limited attribution)

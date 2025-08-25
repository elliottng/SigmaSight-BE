# DB Mapping — Aligning to `DATABASE_DESIGN_V1.4.md`

> **Note**: Adjust table/column names to exactly match your schema. Below is a canonical mapping the frontend expects via the API layer.

## Core Entities
- **users**: id, email, role
- **portfolios**: id, user_id, name, base_ccy
- **positions**: id, portfolio_id, ticker, side, qty, avg_cost, market_price, sector, industry, as_of
- **trades**: id, portfolio_id, position_id, ticker, side, qty, price, executed_at
- **factors**: id, name, type (`style|macro`)
- **position_factors**: position_id, factor_id, beta, as_of
- **portfolio_factor_snapshots**: portfolio_id, as_of, factor_name, beta, pct_of_total_variance
- **benchmarks**: id, symbol, name
- **portfolio_returns**: portfolio_id, as_of, twr, mwr, ann_vol, sharpe, drawdown
- **tags**: id, label, color, description
- **position_tags**: position_id, tag_id
- **targets**: position_id, target_price, stop_price, note, updated_at

## API Adapters
The backend should **not** expose tables directly. Instead, map DB rows to the contracts in `api_contracts.md` via view models:

- `GET /portfolio/:id/summary` pulls from `portfolio_returns` (latest by `as_of`) + aggregates from `positions` for exposures.
- `GET /portfolio/:id/attribution` joins `positions` + returns window; aggregate by `groupBy` param.
- `GET /portfolio/:id/factors` reads from `portfolio_factor_snapshots` (latest `as_of`), fallback: aggregate `position_factors`.
- `GET /portfolio/:id/risk/var` reads from your risk engine outputs table or computes on demand.
- `POST /whatif/model` runs your modeling tool; do not mutate DB.
- `GET/POST /tags` maps to `tags`, `position_tags`.
- `GET/POST /targets` maps to `targets` by `position_id`.


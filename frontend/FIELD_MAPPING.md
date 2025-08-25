# FIELD MAPPING — UI ↔ Backend ↔ DB v1.4

> Fill the RIGHT column with your exact field names from `DATABASE_DESIGN_V1.4.md`.

## Snapshot (GET /get_portfolio_snapshot)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| as_of | snapshot.as_of | portfolio_snapshots.as_of |
| total_value | snapshot.total_value | portfolio_snapshots.total_value |
| long_exposure | snapshot.long_exposure | portfolio_snapshots.long_exposure |
| short_exposure | snapshot.short_exposure | portfolio_snapshots.short_exposure |
| gross_exposure | snapshot.gross_exposure | portfolio_snapshots.gross_exposure |
| net_exposure | snapshot.net_exposure | portfolio_snapshots.net_exposure |
| diversification_score | snapshot.diversification_score | position_correlation_matrix or precompute |

## Positions (GET /get_positions)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| position_id | position_id | positions.id |
| symbol | symbol | positions.symbol |
| side | side | positions.side |
| quantity | quantity | positions.quantity |
| price | price | positions.price |
| market_value | market_value | positions.market_value |
| sector | sector | positions.sector |
| greeks.delta | greeks.delta | position_greeks.delta |

## Factors (GET /get_factor_exposures)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| factors[].name | factors[].name | portfolio_factor_exposures.factor |
| factors[].exposure | factors[].exposure | portfolio_factor_exposures.exposure |
| as_of | as_of | portfolio_factor_exposures.as_of |

## Factor Risk Contribution (GET /get_factor_risk_contrib)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| contributions[].factor | contributions[].factor | factor_covariance_matrix.factor |
| contributions[].variance_share | contributions[].variance_share | derived server-side |

## Scenarios (GET /get_stress_results)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| results[].name | results[].name | stress_scenarios.name |
| results[].pnl_pct | results[].pnl_pct | computed server-side against snapshot |

## Shorts (GET /get_short_metrics)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| symbol | symbol | positions.symbol |
| short_interest_pct | short_interest_pct | short_selling_metrics.short_interest_pct |
| days_to_cover | days_to_cover | short_selling_metrics.days_to_cover |
| borrow_rate | borrow_rate | short_selling_metrics.borrow_rate |

## Targets (GET/POST)
| UI Field | Backend JSON Field | DB v1.4 Source |
|---|---|---|
| position_id | position_id | positions.id |
| target_price | target_price | position_targets.target_price |
| tags[] | tags | position_tags.tag (join) |

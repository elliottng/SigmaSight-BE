# API Contracts (v1)

Base URL: `{API_BASE}/v1`

Authentication: `Authorization: Bearer <token>` (JWT or session token)

---

## Portfolio Summary
`GET /portfolio/:portfolioId/summary`

**Query**: `asOf` (ISO date), `window` (e.g., `1d|1w|1m|1y`)

**Response**
```json
{
  "portfolioId": "string",
  "asOf": "2025-08-22",
  "window": "1m",
  "equity": 1250000.25,
  "cash": 150000.00,
  "grossExposurePct": 125.4,
  "netExposurePct": 42.7,
  "longExposurePct": 84.0,
  "shortExposurePct": 41.3,
  "returnPct": 2.15,
  "annVolPct": 18.2,
  "sharpe": 1.42,
  "drawdownPct": -6.3,
  "benchmark": { "name": "SPX", "returnPct": 1.1, "annVolPct": 15.0 }
}
```

---

## Attribution by Name / Sector
`GET /portfolio/:portfolioId/attribution`

**Query**: `window`, `groupBy=security|sector|industry`

**Response**
```json
{
  "groupBy": "security",
  "items": [
    { "key": "NVDA", "contributionPct": 0.85 },
    { "key": "AAPL", "contributionPct": -0.21 }
  ],
  "topContributors": ["NVDA","META","MSFT"],
  "topDetractors": ["AAPL","TSLA","AMZN"]
}
```

---

## Factor Exposures & Contribution
`GET /portfolio/:portfolioId/factors`

**Response**
```json
{
  "asOf": "2025-08-22",
  "model": "Barra-lite",
  "exposures": [
    { "factor": "Value", "beta": -0.12 },
    { "factor": "Growth", "beta": 0.35 },
    { "factor": "Momentum", "beta": 0.28 },
    { "factor": "Size", "beta": -0.10 }
  ],
  "riskContribution": [
    { "factor": "Growth", "pctOfTotalVariance": 34.1 },
    { "factor": "Momentum", "pctOfTotalVariance": 22.8 }
  ]
}
```

---

## VaR / ES
`GET /portfolio/:portfolioId/risk/var`

**Query**: `horizon=1d|10d`, `conf=0.95|0.99`, `method=historical|parametric|mc`

**Response**
```json
{
  "method": "historical",
  "conf": 0.99,
  "horizon": "1d",
  "varAmount": -45000.0,
  "esAmount": -68000.0,
  "notes": "Lookback 252d; includes options via delta-gamma."
}
```

---

## What-If Modeler
`POST /whatif/model`

**Body**
```json
{
  "portfolioId": "string",
  "proposedTrades": [
    { "ticker": "AAPL", "side": "SELL", "qty": 250 },
    { "ticker": "XLE", "side": "BUY", "notional": 50000 }
  ]
}
```

**Response**
```json
{
  "before": { "netExposurePct": 42.7, "grossExposurePct": 125.4, "factors": [{ "factor": "Growth", "beta": 0.35 }] },
  "after":  { "netExposurePct": 30.2, "grossExposurePct": 112.1, "factors": [{ "factor": "Growth", "beta": 0.05 }] },
  "deltas": { "netExposurePct": -12.5, "grossExposurePct": -13.3, "factors": [{ "factor": "Growth", "delta": -0.30 }] }
}
```

---

## Tags
`GET /tags?portfolioId=...`
`POST /tags` -> create/update

**Tag Object**
```json
{ "id": "uuid", "label": "AI", "color": "#8B5CF6", "description": "AI thematics" }
```

**Assignment**
`POST /tags/assign`
```json
{ "portfolioId": "string", "assignments": [{ "positionId": "uuid", "tagId": "uuid" }] }
```

---

## Targets
`GET /targets?portfolioId=...`
`POST /targets` (upsert array)

**Target Object**
```json
{ "positionId": "uuid", "ticker": "AAPL", "targetPrice": 245.0, "stopPrice": 190.0, "note": "Earnings next qtr" }
```


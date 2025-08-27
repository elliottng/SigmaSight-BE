# Technical Design Doc — SigmaSight Agent + Chat (Phase 1)

**Date:** 2025-08-26\
**Owners:** Engineering (Agent, Backend, Frontend)\
**Audience:** AI coding agent + engineers\
**Status:** Draft for sign‑off

---

## 1. Overview & Scope

**Goal (Phase 1):** Ship a chat interface where an Agent answers portfolio questions using **function calling to Raw Data APIs** and **Code Interpreter** for calculations. No writes. Two prompt modes: **Analyst Blue** and **Analyst Green**.

**Out of scope (Phase 1):** Calculation‑engine tools, file uploads, conversation sharing, dashboard integration, long‑term memory beyond session, pagination (we use hard caps + truncation metadata).

**Phase 2 preview:** Add calculation‑engine tools (risk/exposures/attribution/stress), optional async job wrappers, eval harness + tracing.

---

## 2. Architecture & Sequence

```
Frontend (Next.js) ──POST /chat/conversations────────▶ Backend (FastAPI)
Frontend (Next.js) ──SSE POST /chat/send─────────────▶  ├─ Auth (verify JWT cookie)
                                                        ├─ Compose prompt (mode)
                                                        ├─ OpenAI Responses (GPT‑5; Agents SDK wrapper)
                                                        │    ├─ Tool call → server‑side handler → Raw Data service
                                                        │    └─ Code Interpreter (JSON only)
                                                        └─ Stream SSE events back to FE
```

**Key decisions:** Backend‑only OpenAI calls; SSE streaming; Conversations for session memory; JSON‑only to Code Interpreter; sync tools with caps (no pagination).

---

## 3. Modules & Repo Layout

```
/backend/
  src/sigmasight_api/
    auth/                     # JWT login route
    chat/
      conversations.py        # POST /chat/conversations
      send.py                 # POST /chat/send (SSE)
    tools/                    # server-side tool handlers calling Raw Data services
    services/raw_data/        # thin service layer over FastAPI or in-proc calls
    prompts/                  # prompt files Blue/Green (copied from agent_pkg)
    telemetry/
/agent/
  agent_pkg/
    prompts/                  # versioned Markdown with YAML frontmatter
    tools/                    # tool schema registry (names, JSON schemas)
    orchestration/            # Agents SDK integration & dispatcher
    memory/                   # session helpers (Conversations) & primer glue
/shared/
  clients/                    # typed clients (if agent splits later)
  models/                     # Pydantic types for tool IO
/frontend/
  src/app/agent/              # chat page
  src/components/chat/        # ChatContainer, MessageList, MessageInput, AgentMessage
```

---

## 4. Runtime & Dependencies

**Backend:** Python 3.11, FastAPI/Starlette, httpx, pydantic, uvicorn, cachetools (or Redis client), OpenAI SDK, Agents SDK.\
**Frontend:** Next.js 15, React 18, TypeScript, Tailwind, react‑markdown, Recharts.\
**Model default:** `gpt-5` (admin toggle to `gpt-4o-mini`).\
**Transport:** SSE (`text/event-stream`).

**Env vars (backend)**

- `OPENAI_API_KEY`
- `SIGMASIGHT_ENV` (dev|staging|prod)
- `JWT_PUBLIC_KEY` (or secret)
- `RAW_DATA_BASE_URL` (if calling over HTTP)
- `SSE_HEARTBEAT_INTERVAL_MS` (default 15\_000)
- `MODEL_DEFAULT` (gpt-5)
- `CACHE_TTL_SECONDS` (default 600)

**Nginx/SSE:** `proxy_buffering off;` add `X-Accel-Buffering: no`; increase `proxy_read_timeout` (e.g., 120s).

---

## 5. Chat Endpoints (Backend)

### 5.1 `POST /chat/conversations`

**Request:** `{}`\
**Response 200:** `{ "conversation_id": "conv_..." }`\
**Behavior:** Creates OpenAI Conversation; persist `{conversation_id, user_id, mode}`.

### 5.2 `POST /chat/send`  (SSE)

**Request:** `{ "conversation_id": "conv_...", "text": "What's my 30‑day P&L?" }`\
**Response:** `text/event-stream` (see §8 for event schema)\
**Behavior:** Verify JWT → load mode → call Responses with tools + Code Interpreter → stream events.

---

## 6. Orchestration (Responses + Agents SDK)

- **Agents SDK** provides a thin wrapper: registers **prompt modes** (Blue/Green), **tool registry**, and the run loop with retries.
- **We still call Responses API** under the hood; Conversations supply session memory.
- **Server‑side tool handlers** are plain Python functions (see §7) that call Raw Data services (in‑proc or HTTP).

---

## 7. Function Tools — Raw Data (Phase 1)

### 7.A Common response/ error shapes & parameter inventory

Each tool returns a common envelope and error shape:

```json
{
  "meta": {
    "as_of": "2025-08-26T20:00:00Z",
    "requested": {},
    "applied": {},
    "limits": {},
    "rows_returned": 0,
    "truncated": false,
    "suggested_params": null
  },
  "data": {}
}
```

Error (non‑200):

```json
{ "error": { "message": "...", "retryable": true, "suggested_params": { }, "request_id": "req_..." } }
```

**Parameter inventory from spec (expose exactly these):**

- Portfolio complete: `include_positions`, `include_cash`, `as_of_date` (ISO date)
- Portfolio data-quality: `check_factors`, `check_correlations`
- Positions details: `portfolio_id` *or* `position_ids`, `include_closed`
- Prices historical: `lookback_days`, `include_factor_etfs`, `date_format` (`iso|unix`)
- Quotes: `symbols` (comma list), `include_options`
- Factor ETF prices: `lookback_days`, `factors` (comma list)

**Time standardization (P1 change):** All tool outputs must use **UTC ISO‑8601** timestamps with `Z`. Handlers will normalize until backend emits UTC natively. All tools **mirror** the spec in `API_SPECIFICATIONS_V1.4.4.md` and enforce **caps** (no pagination). Each returns:

```json
{
  "meta": {
    "as_of": "2025-08-26T20:00:00Z",
    "requested": { /* input as received */ },
    "applied":   { /* adjusted for caps/defaults */ },
    "limits":    { /* per-endpoint caps */ },
    "rows_returned": 0,
    "truncated": false,
    "suggested_params": null
  },
  "data": { /* typed rows or objects per endpoint */ }
}
```

**Error shape (non‑200)**

```json
{
  "error": {
    "message": "window exceeds cap",
    "retryable": true,
    "suggested_params": { "window": "90d" },
    "request_id": "req_abc123"
  }
}
```

### 7.1 `get_portfolio_complete`

**Maps to:** `GET /api/v1/data/portfolio/{portfolio_id}/complete`\
**Input schema**

```json
{
  "type":"object",
  "properties":{
    "portfolio_id":{"type":"string", "description":"UUID"},
    "include_positions":{"type":"boolean", "default":true},
    "include_cash":{"type":"boolean", "default":true},
    "as_of_date":{"type":"string", "format":"date"}
  },
  "required":["portfolio_id"]
}
```

**Limits:** `max_rows_positions=200`.\
**Output:** `data` contains raw positions/cash; **no derived metrics**.

### 7.2 `get_portfolio_data_quality`

**Maps to:** `GET /api/v1/data/portfolio/{portfolio_id}/data-quality`\
**Input**

```json
{
  "type":"object",
  "properties":{
    "portfolio_id":{"type":"string"},
    "check_factors":{"type":"boolean", "default":true},
    "check_correlations":{"type":"boolean", "default":true}
  },
  "required":["portfolio_id"]
}
```

**Output:** Feasibility flags and any missing inputs for downstream analytics.

### 7.3 `get_positions_details`

**Maps to:** `GET /api/v1/data/positions/details`\
**Input**

```json
{
  "type":"object",
  "properties":{
    "portfolio_id":{"type":"string"},
    "position_ids":{"type":"string", "description":"comma-separated"},
    "include_closed":{"type":"boolean", "default":false}
  },
  "oneOf":[{"required":["portfolio_id"]},{"required":["position_ids"]}]
}
```

**Limits:** `max_rows=200` (truncate + report in meta).\
**Output:** Row list + summary block.

### 7.4 `get_prices_historical`

**Maps to:** `GET /api/v1/data/prices/historical/{portfolio_id}`\
**Input**

```json
{
  "type":"object",
  "properties":{
    "portfolio_id":{"type":"string"},
    "lookback_days":{"type":"integer", "default":150, "minimum":1},
    "include_factor_etfs":{"type":"boolean", "default":true},
    "date_format":{"type":"string", "enum":["iso","unix"], "default":"iso"}
  },
  "required":["portfolio_id"]
}
```

**Limits:** `max_window_days=180`; intraday alternative `5d@5m` (downsample to meet token budget).\
**Output:** Per‑symbol series (dates, open/high/low/close/volume/adjusted\_close).

**Note (per product decision, no API change):** this endpoint **does not** accept a `symbols` filter. The tool handler will:

1. fetch **positions** to identify **top 5 symbols by market value** (configurable policy),
2. call this historical endpoint with the requested (or capped) window,
3. **post‑process** the response to **retain only the selected symbols** before sending to the model,
4. set `meta.truncated=true` and include `meta.applied.symbols` and `suggested_params` when trimming occurs. If payload still exceeds token thresholds, the handler will further **reduce **`` (down to the cap) and reflect that in `meta.applied`.

### 7.5 `get_current_quotes`

**Maps to:** `GET /api/v1/data/prices/quotes`\
**Input**

```json
{
  "type":"object",
  "properties":{
    "symbols":{"type":"string", "description":"comma-separated tickers"},
    "include_options":{"type":"boolean", "default":false}
  },
  "required":["symbols"]
}
```

**Limits:** `max_symbols=5`.\
**Output:** Latest quotes; optional options chain when requested.

### 7.6 `get_factor_etf_prices`

**Canonical factor ETF universe (CONFIRMED)**\
Source of truth: `backend/app/constants/factors.py` → `FACTOR_ETFS` dict\
Data provider: **FMP (Financial Modeling Prep)** via backend services (the Agent/tools do **not** call FMP directly).

| Factor         | ETF Symbol         | Notes                                                                                                     |
| -------------- | ------------------ | --------------------------------------------------------------------------------------------------------- |
| Market Beta    | **SPY**            | SPDR S&P 500 ETF Trust                                                                                    |
| Value          | **VTV**            | Vanguard Value ETF                                                                                        |
| Growth         | **VUG**            | Vanguard Growth ETF                                                                                       |
| Momentum       | **MTUM**           | iShares MSCI USA Momentum Factor ETF                                                                      |
| Quality        | **QUAL**           | iShares MSCI USA Quality Factor ETF                                                                       |
| Size           | **SIZE** / **SLY** | Size factor; docs show **SIZE** as canonical, **SLY** appears as alternative—handler should accept either |
| Low Volatility | **USMV**           | iShares MSCI USA Min Vol Factor ETF                                                                       |

If the backend exposes a different/extended mapping at runtime, tool handlers must **prefer the backend-sourced **``; otherwise fall back to the table above.

**Maps to:** `GET /api/v1/data/factors/etf-prices`\
**Input**

```json
{
  "type":"object",
  "properties":{
    "lookback_days":{"type":"integer", "default":150},
    "factors":{"type":"string", "description":"comma-separated factor names (e.g., 'market,value,momentum')"}
  }
}
```

**Output:** Series for the factor ETF basket defined above. Handlers should normalize factor aliases (e.g., `market`→`SPY`, `size`→`SIZE`) and include the resolved `etf_symbol` in `meta.applied`.

---

## 8. SSE Event Protocol (chat/send)

**Headers:** `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`\
**Heartbeat:** comment lines `:\n` every 15s to keep proxies alive.

**Events**

- `start` → `{}`
- (default `message`) → `{ "delta": "partial token(s)" }`
- `tool_call` → `{ "name": "get_prices_historical", "args": { ... } }`
- `tool_result` → `{ "name": "get_prices_historical", "meta": { ... }, "preview": { /* optional small table */ } }`
- `error` → `{ "message": "..." }`
- `done` → `{}` (client closes stream)

**Client handling:** Append `delta` to current assistant message; on `tool_call`/`tool_result`, render lightweight breadcrumbs and any small preview tables.

---

## 9. Prompt Library & Modes

**Location:** `agent/agent_pkg/prompts/`

- Files: `analyst_blue_v001.md`, `analyst_green_v001.md`
- **YAML frontmatter** requirements:

```yaml
id: analyst_blue
version: v001
mode: Analyst Blue
owner: agent-team
change_notes: "Initial"
token_budget: 1800
```

- **Templating variables:** `{user_profile}`, `{as_of}`, `{caps}`.
- **Guardrails (both modes):** Use tools for facts; use CI for math; include as‑of; never fabricate; propose narrower params when truncated.
- **Telemetry:** Log `prompt_id`, `version`, `hash` per run.

---

## 10. Code Interpreter (CI)

- **Enabled by default.**
- **Input:** JSON from tools (or small embedded JSON).
- **No external network.**
- **Typical tasks:** compute 30‑day P&L from prices + positions; aggregate exposures; generate compact tables for FE charts.
- **Output:** Tabular JSON (preferred) or (later) small PNG images; P1 prefers FE charts from tables.

---

## 11. Auth & Security

### Authentication Strategy (Dual Support)
Given the existing backend uses Bearer tokens but SSE works better with cookies, we implement **dual authentication**:

- **Login:** `POST /api/v1/auth/login` returns JWT in response body (existing) AND sets HTTP‑only cookie (new)
- **Regular endpoints:** Accept BOTH Bearer token (existing) OR cookie (new)
- **SSE endpoints:** Prefer cookie (automatic attachment) but accept Bearer via query param if needed
- **Implementation:** Modify `get_current_user` dependency to check both sources:
  ```python
  # Try Bearer token first (existing clients)
  # Fallback to cookie (SSE, new clients)
  # Return 401 if neither present
  ```

### Security Notes
- **Backend‑only OpenAI calls:** API keys never exposed to frontend
- **Tool handlers** receive `user_id` from verified request context; no user JWT forwarded to OpenAI/tools
- **CSRF:** Not needed in Phase 1 (read-only endpoints)
- **PII:** Consider masking in Phase 2
- **Rate limits:** Basic per‑user (e.g., 60 req/min burst 10)

---

## 12. Performance & Limits

- Latency: stream start ≤ 3s p50; complete ≤ 8–10s p95.
- Tool caps (no pagination): Prices `max_symbols=5`, `max_window_days=180` (daily); optional intraday policy `5d@5m` if added later. Positions `max_rows=200`; Transactions `max_rows=500` (if used).
- Timeouts: \~5–6s p95 per tool.
- Truncation metadata: Always populate `meta.applied`, `truncated`, and `suggested_params`.

### Caps explained (plain English)

- **“5 symbols”**: when symbol lists are accepted (e.g., quotes), cap to **5 tickers** per call.
- **“180d”**: for daily historical prices, cap **lookback\_days at 180**. If the request exceeds this, enforce 180, mark `truncated=true`, and suggest a narrower window.
- **Historical by portfolio**: if a portfolio holds >5 symbols, return **top 5 by market value** (or configured policy), mark truncation, and suggest specifying a subset.
- **Why**: keeps payloads <\~2k tokens so the agent can make 1–3 tool calls within latency budgets.

---

## 13. Telemetry & Logging

---

## 13. Telemetry & Logging

- **Per run:** `run_id, user_id, conversation_id, mode, prompt_version, tool_calls[], latency_ms, prompt_tokens, completion_tokens, cost_est, rating`.
- **Storage:** DB table or log sink; no raw payloads (store hashes/sizes only).
- **Cache:** 5–10 min TTL per‑conversation for common slices.

---

## 14. Testing & Golden Set

- **Smoke tests:** One per tool (happy path + cap exceeded).
- **Golden tasks (15):** e.g., “What’s my 30‑day P&L?”, “Biggest positions?”, “Delta exposure?”, “Positions expiring this week?”.
- **Assertions:** presence of tables, correct units/as‑of, no hallucinated tickers, numeric sanity checks.

---

## 15. Deployment

- **Containers:** Start as a single backend container (agent embedded). Optional split later with shared base image.
- **SSE proxy:** Disable buffering on `/chat/send`.
- **Health checks:** `/healthz` for backend; OpenAI key test on boot.

---

## 16. Phase 2 Extension (non‑binding)

- Register calculation‑engine tools (factors/exposures/attribution/stress/Greeks).
- Add async job wrappers behind sync tool calls for long analytics (short internal wait; return partial or job\_id if not ready).
- Roll out eval harness + tracing; consider promoting agent to its own service.

---

## 17. Resolutions & Outstanding Items

- **Raw Data params**: Use **exact params from spec** (see §7.A). No currency/timezone params in P1; standardize times to **UTC ISO‑8601 **``.
- **Factor ETF universe**: **Resolved**. Canonical mapping confirmed (see §7.6); location: `backend/app/constants/factors.py` (`FACTOR_ETFS`); provider: **FMP** via backend.
- **Dates**: ✅ **COMPLETED** - Backend migrated to UTC ISO 8601 with Z suffix (Phase 3 completed 2025-08-27).
- **Auth cookie TTL**: 24h for MVP; no refresh token in P1.
- **Caps**: Adopt 5‑symbols & 180‑days policies (see §12); positions 200 rows; transactions 500 rows.
- **Model override**: Admin‑only per‑conversation toggle (GPT‑5 ⇄ gpt-5-mini). Note: GPT-5 now available per OpenAI docs.
- **Historical prices symbols filter**: **No change to APIs in P1**. Handlers will enforce caps and **post‑process** to top 5 symbols; we can revisit a server‑side filter or async job in Phase 2 if needed.

*No additional open items for Phase 1.*

---

## 18. Existing Backend Infrastructure (Project Context)

**This section documents what already exists in the backend that the agent implementation will build upon.**

### 18.1 Authentication System
- **JWT Bearer tokens** implemented in `app/api/v1/auth.py`
- **HTTPBearer security** scheme (not cookies initially - may need adaptation for SSE)
- **get_current_user** dependency in `app/core/dependencies.py`
- Token expiration: 30 minutes (ACCESS_TOKEN_EXPIRE_MINUTES)
- Returns `CurrentUser` schema with user_id, email, is_active

### 18.2 Database Infrastructure
- **Async SQLAlchemy** with PostgreSQL
- **Base class** in `app/database.py` with naming conventions
- **Dependency injection**: `get_db()` for FastAPI endpoints
- **Context manager**: `get_async_session()` for scripts/batch jobs
- **Alembic migrations** for schema management
- Models must be imported in `init_db()` for table creation (line ~85)

### 18.3 Configuration System
- **Pydantic Settings** with BaseSettings in `app/config.py`
- Environment variables auto-loaded with `Field(..., env="VAR_NAME")`
- Settings instance available as `app.config.settings`
- Existing market data provider configs (FMP, Polygon, etc.)

### 18.4 API Structure
- **Main router**: `/api/v1/` prefix
- **Router registration** in `app/api/v1/router.py`
- **CORS configured** for localhost:3000
- **FastAPI app** in `app/main.py` with middleware

### 18.5 Raw Data APIs (✅ 100% Complete)
All 6 Raw Data endpoints are **working with real data** as of 2025-08-26:
- `/api/v1/data/portfolio/{id}/complete` - Real portfolio data with 5% cash balance
- `/api/v1/data/portfolio/{id}/data-quality` - Real data quality assessments
- `/api/v1/data/positions/details` - Real positions from database
- `/api/v1/data/prices/historical/{id}` - 292 days of real OHLCV data
- `/api/v1/data/prices/quotes` - Real-time market quotes
- `/api/v1/data/factors/etf-prices` - All 7 ETFs with real prices

**Note**: These endpoints need parameter enhancements for agent tool requirements (caps, meta objects).

### 18.6 Logging Infrastructure
- **Structured loggers**: auth_logger, db_logger, api_logger
- **UTC timestamps** already standardized
- Log level configured via LOG_LEVEL env var

### 18.7 Datetime Standardization
- ✅ **UTC ISO 8601 format** implemented across all APIs
- All timestamps use Z suffix format
- Utility functions in `app/core/datetime_utils.py`
- Pydantic BaseSchema configured with proper json_encoders

### 18.8 Demo Data
- **3 demo portfolios** with 63 positions loaded
- Demo users: `demo_individual@sigmasight.com / demo12345`
- MarketDataCache with 292 days of historical prices
- All batch calculations completed with real data

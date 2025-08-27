# SigmaSight Agent PRD v1.0

**Date:** 2025-08-26


---

## 1) Summary

Ship a **chat interface** where an Agent answers portfolio questions by combining:

* **Phase 1 (this build):**

  * **Function calling (tools) to Raw Data APIs only** (see §6 Tools & Schemas; sourced from `API_SPECIFICATIONS_V1.4.4.md`).
  * **Code Interpreter ON by default** for ad‑hoc calculations (operates on **JSON** returned by tools; CSV optional in future).
  * **Modes:** **Analyst Blue** and **Analyst Green** (prompt variants for tone/strategy).
  * **Read‑only** (no write ops).
* **Phase 2:**

  * Add function tools for **calculation‑engine** endpoints (risk/exposures/attribution/stress tests, etc.).
  * Add eval harness & tracing; consider async wrappers where needed.

Users: 2 cofounders + \~10 beta testers. Target: functional prototype in \~2 weeks.

---

## 2) Goals & Non‑Goals (Phase 1)

**Goals**

* Ship a responsive **chat** with streaming.
* Implement **function calling** to **Raw Data** endpoints only.
* **Enable Code Interpreter** by default (JSON inputs) for calculations/aggregations.
* Provide **session memory** via Conversations and a small per‑user primer (cross‑session).
* Support **two prompt modes**: Analyst Blue, Analyst Green.

**Non‑Goals**

* Any writes/updates/trades.
* Calculation‑engine tools (Phase 2).
* File uploads, conversation sharing, full dashboard integration, or fancy UI polish.

**Success Metrics (P1)**

* Stream start ≤ **3s** p50; complete ≤ **8–10s** p95.
* ≥ **80%** pass rate on 15 golden tasks relying only on Raw Data.
* ≥ **70%** Good/Excellent usefulness rating; minimal hallucinated tickers/values.

---

## 3) Architecture

```
[Next.js Frontend]
   └── calls → [SigmaSight Backend /chat endpoints]
                  ├─ verifies JWT (HTTP-only cookie)
                  ├─ orchestrates OpenAI Responses (GPT‑5 default)
                  ├─ executes server-side tool handlers → Raw Data APIs (sync)
                  └─ streams events (SSE) → FE renders tokens, tool breadcrumbs, results
```

**Key decisions (locked):**

* OpenAI calls occur **only in our backend** (keys/auth centralized).
* **SSE** for streaming (not WebSockets).
* Auth via **POST** login; JWT stored in **HTTP‑only, SameSite=Lax** cookie (24h TTL for MVP).
* **Conversations** for session memory; DB stores `{conversation_id, user_id, mode}`.
* Tiny **per‑conversation cache** (5–10 min TTL) for read‑only slices.
* **JSON‑only** inputs to Code Interpreter in P1.

## Architecture Decision Summary (for AI coding agent)

* **Core stack:** OpenAI **Responses** + **Conversations**; **Agents SDK** for prompt modes and tool orchestration.
* **Backend-only OpenAI calls:** Frontend hits `/chat/*`; keys & rate-limits stay server-side.
* **Streaming:** **SSE** for token/tool events.
* **Tools (Phase 1):** Server-side handlers over **Raw Data** FastAPI services; **sync**, bounded responses, **no pagination**—enforce caps and return `meta.requested` vs `meta.applied`.
* **Model:** Default **GPT-5** (admin toggle to 4o-mini).
* **Code Interpreter:** **On by default**; JSON inputs only in P1.
* **Memory:** **Conversations** for session; small cross-session primer stored in DB.
* **Auth/Security:** **POST** login, JWT in **HTTP-only cookie**; no write endpoints in P1.

---

## 4) User Flows (Phase 1)

### 4.1 Authentication

1. FE → `POST /api/v1/auth/login` → set HTTP‑only cookie (JWT)
2. Redirect to `/agent`

### 4.2 Start Conversation

1. FE → `POST /chat/conversations`
2. BE creates OpenAI **Conversation** → returns `{ conversation_id }`
3. Persist `{ conversation_id, user_id, mode }` in DB

### 4.3 Ask Question (SSE streaming)

1. FE → `POST /chat/send` (SSE) `{ conversation_id, text }`
2. BE verifies JWT → composes system prompt (Blue/Green) → calls **Responses** with:

   * `model: gpt-5` (default; admin toggle to `gpt-4o-mini`)
   * `tools: [ code_interpreter, <RawData tools> ]`
   * `conversation_id`
   * streaming enabled
3. Model may call tools and/or use Code Interpreter
4. BE streams deltas + tool events; FE renders progressively

**SSE contract (sketch):**

```
POST /chat/send  →  Content-Type: text/event-stream

event: start
data: {}

data: {"delta":"..."}

event: tool_call
data: {"name":"get_prices_historical", "args":{...}}

event: tool_result
data: {"name":"get_prices_historical", "result_meta":{...}}

event: done
data: {}
```

---

## 5) Prompts & Modes

### 5.1 Analyst Blue (v001)

* Concise, quant‑forward; prefer tables and bullet rationales.
* Use tools for factual data; use Code Interpreter for math/aggregation.
* If data insufficient, **ask to narrow** (short, specific).

### 5.2 Analyst Green (v001)

* Explanatory/teaching tone; step‑by‑step justification.
* Same tool/CI rules; emphasize clarity over compactness.

**Shared guardrails**

* Never fabricate tickers/values; include “as‑of” when relevant.
* State uncertainty when data is missing or ambiguous.
* If caps are hit, propose narrower parameters.

---

## 6) Tools & Schemas (Phase 1 — Raw Data only)

All tools are **server-side handlers** that call our Raw Data service layer (in‑process when co‑located with backend; HTTP call with short‑lived tool token if agent becomes a separate service).

> **Caps (no pagination in P1):**
> Prices: `max_symbols=5`, `max_window=180d@1d` (or `5d@5m` intraday)
> Positions: `max_rows=200`
> Transactions (if applicable later): `max_rows=500`, default `window=30d`
> Always echo `meta.requested` vs `meta.applied`, `truncated`, and `suggested_params`.

### 6.1 Tool: **get\_portfolio\_complete**

**HTTP:** `GET /api/v1/data/portfolio/{portfolio_id}/complete`
**Inputs:**

* `portfolio_id` (string, UUID, required)
* `include_positions` (boolean, default: true)
* `include_cash` (boolean, default: true)
* `as_of_date` (ISO date, optional)
  **Result:** Comprehensive portfolio overview (positions, cash) with **no derived metrics**.

### 6.2 Tool: **get\_portfolio\_data\_quality**

**HTTP:** `GET /api/v1/data/portfolio/{portfolio_id}/data-quality`
**Inputs:**

* `portfolio_id` (string, UUID, required)
* `check_factors` (boolean, default: true)
* `check_correlations` (boolean, default: true)
  **Result:** Data availability assessment (which downstream analytics are feasible given current data).

### 6.3 Tool: **get\_positions\_details**

**HTTP:** `GET /api/v1/data/positions/details`
**Inputs:**

* `portfolio_id` (UUID, required unless `position_ids` provided)
* `position_ids` (string, optional; comma‑separated)
* `include_closed` (boolean, default: false)
  **Result:** Detailed position‑level rows + summary block (totals), raw/unprocessed.

### 6.4 Tool: **get\_prices\_historical**

**HTTP:** `GET /api/v1/data/prices/historical/{portfolio_id}`
**Inputs:**

* `portfolio_id` (UUID, required)
* `lookback_days` (int, default: 150)
* `include_factor_etfs` (boolean, default: true)
* `date_format` (string, default: `iso`, enum: `iso|unix`)
  **Result:** Time‑series by symbol (dates, OHLCV, adjusted\_close). Honors caps and returns applied parameters.

### 6.5 Tool: **get\_current\_quotes**

**HTTP:** `GET /api/v1/data/prices/quotes`
**Inputs:**

* `symbols` (string, required; comma‑separated tickers)
* `include_options` (boolean, default: false)
  **Result:** Current quotes, optional options chains.

### 6.6 Tool: **get\_factor\_etf\_prices**

**HTTP:** `GET /api/v1/data/factors/etf-prices`
**Inputs:**

* `lookback_days` (int, default: 150)
* `factors` (string, optional; comma‑separated factor names)
  **Result:** Historical prices for factor ETFs used by the 7‑factor model.

> **All tool outputs** include a `meta` object with: `requested`, `applied`, `limits`, `rows_returned`, `truncated` (bool), optional `suggested_params`, and `as_of` timestamp.

---

## 7) Backend APIs for Chat (new)

### 7.1 `POST /chat/conversations`

**Request:** `{}`
**Response:** `{ "conversation_id": "conv_..." }`
**Behavior:** Creates an OpenAI Conversation; persists `{conversation_id, user_id, mode}` in DB.

### 7.2 `POST /chat/send`  (SSE)

**Request:** `{ "conversation_id": "conv_...", "text": "What's my 30‑day P&L?" }`
**Response:** `text/event-stream` (see SSE contract in §4.3)
**Behavior:** Verifies JWT → composes prompt (mode) → calls Responses with tools + Code Interpreter → streams deltas + tool events → closes with `event: done`.

---

## 8) Code Interpreter (P1 behavior)

* **Enabled by default**.
* Operates on **JSON** returned by tools (and small JSON embedded in prompt).
* Typical uses: computing P\&L deltas, grouping/aggregating positions, generating small tables for FE charts.
* No external network from CI; all data must come from tools or attachments.
* (Phase 2 option) Allow CI to save small images for plots; in P1 prefer FE charts from tabular data.

---

## 9) Performance, Limits & Errors

* **Latency targets:** stream start ≤ 3s p50; completion ≤ 8–10s p95.
* **Sync only:** Raw Data tools are synchronous; keep p95 ≤ \~5–6s per call.
* **Caps (no pagination):** see §6; enforce caps and return `meta.applied` & `truncated` when we downsample/window.
* **Errors:** concise JSON with `retryable` (bool) and `suggested_params` when applicable (e.g., reduce window/symbols).

---

## 10) Security & Privacy

* OpenAI calls run **server‑side** only; keys never touch FE.
* JWT in **HTTP‑only** cookie; consider CSRF protection when we add writes (not in P1).
* Tool handlers execute under **user\_id** context; log inputs/outputs **metadata** (not raw payloads) to avoid PII retention.
* Optionally mask account IDs in tool outputs; omit emails.

---

## 11) Telemetry, Caching & Evals

* **Telemetry (P1 minimal):** log `run_id, user_id, conversation_id, mode, prompt_version, tool_calls[], latency, tokens, rating`.
* **Cache:** small per‑conversation TTL cache (5–10 min) keyed by `{user_id, params_hash}` for read‑only slices.
* **Evals/Tracing (Phase 2):** add golden set + tool‑use checks; instrument traces (Langfuse/OTel) when expanding features.

---

## 12) Phase 2 Preview

* Register function tools for **calculation‑engine** endpoints (risk factors, exposures, attribution, scenario/stress, Greeks, etc.).
* Add optional **async job wrappers** behind sync tool calls for long‑running analytics; still present a simple sync tool to the model.
* Roll out eval harness & tracing; consider splitting `agent/` to its own service if scaling diverges.

---

## 13) Implementation Plan (2 weeks)

**Week 1**

* Setup auth (POST login + HTTP‑only cookie), basic chat UI, SSE plumbing.
* Create `/chat/conversations`, `/chat/send` endpoints; store conversation state.
* Register the six Raw Data tools; wire server‑side handlers to service layer.
* Draft Analyst Blue/Green prompts (v001); end‑to‑end happy path.

**Week 2**

* Enable Code Interpreter by default; validate common calculations.
* Add simple charts (FE Recharts) + table formatting.
* Error handling; minimal telemetry & tiny cache; 15‑task golden set.
* Beta deployment; fix critical issues; measure latency/cost.

---

## 14) Appendix — Tool Mapping Table

| Tool Name                    | Method & Path                                            | Key Inputs                                                                      | Output Notes                                            |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `get_portfolio_complete`     | `GET /api/v1/data/portfolio/{portfolio_id}/complete`     | `portfolio_id` (UUID), `include_positions?`, `include_cash?`, `as_of_date?`     | Raw portfolio snapshot; no derived metrics              |
| `get_portfolio_data_quality` | `GET /api/v1/data/portfolio/{portfolio_id}/data-quality` | `portfolio_id` (UUID), `check_factors?`, `check_correlations?`                  | Feasibility/availability flags for downstream analytics |
| `get_positions_details`      | `GET /api/v1/data/positions/details`                     | `portfolio_id` or `position_ids`, `include_closed?`                             | Position-level rows + summary                           |
| `get_prices_historical`      | `GET /api/v1/data/prices/historical/{portfolio_id}`      | `portfolio_id` (UUID), `lookback_days?`, `include_factor_etfs?`, `date_format?` | Time-series per symbol (OHLCV, adjusted\_close)         |
| `get_current_quotes`         | `GET /api/v1/data/prices/quotes`                         | `symbols` (comma list), `include_options?`                                      | Real-time quotes; options chains optional               |
| `get_factor_etf_prices`      | `GET /api/v1/data/factors/etf-prices`                    | `lookback_days?`, `factors?`                                                    | Historical prices for factor ETFs                       |

---

## 15) FAQ & Notes

* **Are Raw Data tools sync?** Yes—keep them fast (p95 ≤ \~5–6s). If something is heavy, move it to Phase 2 with an async wrapper.
* **How does Agents SDK fit?** It orchestrates prompts/tools; you still implement endpoints in FastAPI. Start with server‑side handlers calling your service layer; if you split the agent into its own service later, call the same endpoints via HTTP.
* **Model default?** `gpt-5` default; admin can flip to `gpt-4o-mini` for cost/latency tests.

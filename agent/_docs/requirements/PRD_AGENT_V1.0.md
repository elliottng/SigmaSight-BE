# SigmaSight Agent PRD v1.0

**Date:** 2025-08-26


---

## 1) Summary

Ship a **chat interface** where an Agent answers portfolio questions by combining:

* **Phase 1 (this build):**

  * **Function calling (tools) to Raw Data APIs only** (see §6 Tools & Schemas; sourced from `API_SPECIFICATIONS_V1.4.4.md`).
  * **Code Interpreter ON by default** for ad‑hoc calculations (operates on **JSON** returned by tools; CSV optional in future).
  * **Modes:** **Green**, **Blue**, **Indigo**, **Violet** (four distinct analyst personalities).
  * **Read‑only** (no write ops).
* **Phase 2:**

  * Add function tools for **calculation‑engine** endpoints (risk/exposures/attribution/stress tests, etc.).
  * Implement **eval framework** for systematic prompt testing and user journey validation.
  * Add **RLHF feedback mechanisms** (thumbs up/down, corrections) for dynamic prompt improvement.
  * Deploy tracing & telemetry; consider async wrappers where needed.

* **Phase 3:**

  * **Multi-LLM testing platform**: Integrate Anthropic (Claude), Google (Gemini), and xAI (Grok) alongside OpenAI.
  * **Provider abstraction layer** for model-agnostic tool calling and streaming.
  * **Comprehensive A/B testing** to identify optimal model/prompt combinations for quant finance.
  * **Performance comparison** across dimensions: finance expertise, reasoning, tool usage, code interpretation.

Users: 2 cofounders + \~10 beta testers. Target: Phase 1 functional prototype in \~2 weeks.

---

## 2) Goals & Non‑Goals (Phase 1)

**Goals**

* Ship a responsive **chat** with streaming.
* Implement **function calling** to **Raw Data** endpoints only.
* **Enable Code Interpreter** by default (JSON inputs) for calculations/aggregations.
* Provide **session memory** via Conversations and a small per‑user primer (cross‑session).
* Support **four prompt modes**: Green, Blue, Indigo, Violet.

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

### 3.1 Service Separation Design

The Agent is designed as a **separable service** that can be deployed either:
1. **Co-located** (MVP): Runs within the main backend process
2. **Standalone** (Future): Independent microservice with its own deployment

```
# MVP: Co-located deployment
[Frontend] → [Backend + Agent Module] → [Database]
                    ↓
              [OpenAI API]

# Future: Separated microservice
[Frontend] → [Agent Service] → [Backend Raw Data APIs]
                    ↓              ↓
              [OpenAI API]     [Database]
```

### 3.2 Clean Separation Requirements

**Service Boundaries:**
* Agent communicates with backend ONLY through defined API contracts
* No direct database access from Agent code (uses backend APIs)
* No shared business logic or domain models
* Separate configuration and secrets management
* Independent logging and monitoring

**Interface Contracts:**
* Authentication: Standard JWT Bearer tokens or service-to-service auth
* Data Access: HTTP calls to Raw Data API endpoints
* Response Format: Standardized JSON schemas
* Error Handling: Consistent HTTP status codes and error formats

### 3.3 Current Architecture (Co-located MVP)

```
[Next.js Frontend]
   └── calls → [SigmaSight Backend]
                  ├─ /api/v1/auth/* (existing)
                  ├─ /api/v1/data/* (existing Raw Data APIs)
                  └─ /api/v1/chat/* (NEW Agent module)
                       ├─ verifies JWT (HTTP-only cookie)
                       ├─ orchestrates OpenAI Responses (GPT‑5 default)
                       ├─ executes tool handlers → calls Raw Data APIs
                       └─ streams events (SSE) → FE renders tokens
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

## 4) Frontend Requirements (MVP - Phase 1)

### 4.1 Minimal Viable Chat Interface

#### Essential Components Only
* **Message Display**
  * Simple scrollable message list
  * User messages (right-aligned)
  * Agent messages (left-aligned)
  * Basic markdown rendering (bold, lists, code blocks)
  * Timestamp per message

* **Message Input**
  * Single-line text input (or basic textarea)
  * Send button
  * Mode toggle (Green/Blue/Indigo/Violet)
  * Disabled state during streaming

* **Streaming**
  * Display text as it arrives (no smoothing required)
  * "Thinking..." indicator during tool calls
  * Basic connection error message

### 4.2 MVP Scope Limitations

* **No Conversation Management**
  * Single active conversation only
  * No history/sidebar
  * Page refresh = new conversation
  * No search, export, or archive

* **No Advanced Features**
  * No charts or visualizations
  * No sortable tables
  * No dark mode
  * No mobile optimization
  * No accessibility features
  * No user feedback collection

### 4.3 Simple Visual Design

* **Basic Layout**
  * Single column, centered
  * Fixed max-width (800px)
  * Desktop-only focus
  * Light theme only

* **Minimal Styling**
  * SigmaSight logo and brand colors
  * System fonts
  * Basic CSS, no animations
  * Standard HTML form controls

### 4.4 MVP Performance Targets

* **Relaxed Requirements**
  * Page load: < 5s acceptable
  * Stream start: < 5s acceptable
  * Handle 50-100 messages
  * Basic browser SSE support

* **Browser Support**
  * Latest Chrome (primary)
  * Latest Safari/Firefox/Edge (should work)
  * No polyfills or fallbacks

### 4.5 Implementation Priorities

**Week 1 Must-Haves:**
1. Working SSE connection
2. Display streaming text
3. Send messages
4. Show tool calls happening
5. Basic markdown for tables

**Nice-to-Haves (if time permits):**
* Copy button for responses
* Stop generation button
* Better error messages
* Code syntax highlighting

**Explicitly Deferred to Phase 2:**
* All conversation management
* Data visualizations
* Mobile responsive design
* Dark mode
* Accessibility
* User feedback/ratings
* Export functionality
* Advanced error recovery

---

## 5) User Flows (Phase 1)

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

Users can switch modes using `/mode <color>` command (e.g., `/mode green`, `/mode blue`).

### 5.1 Green Mode (v001)

* **Teaching-focused**: Step-by-step explanations with context
* **Beginner-friendly**: Defines financial terms, explains calculations
* **Verbose output**: Emphasizes clarity over brevity
* **Example**: "Let me explain VaR: Value at Risk measures..."

### 5.2 Blue Mode (v001)

* **Concise & technical**: Tables, numbers, minimal prose
* **Professional audience**: Assumes financial knowledge
* **Data-forward**: Bullet points, quick insights
* **Example**: "VaR(95%): $1.2M | CVaR: $1.5M | Sharpe: 1.34"

### 5.3 Indigo Mode (v001)

* **Big-picture analysis**: Market context, macro trends
* **Narrative style**: Tells the story behind the numbers
* **Forward-looking**: Emphasizes scenarios and implications
* **Example**: "Given current Fed policy and sector rotation..."

### 5.4 Violet Mode (v001)

* **Risk-focused**: Emphasizes downside, stress scenarios
* **Conservative tone**: Highlights concerns and hedges
* **Compliance-minded**: Includes disclaimers, assumptions
* **Example**: "WARNING: Concentration risk detected. Top 3 positions = 45% of portfolio"

**Shared Guardrails (All Modes)**

* Never fabricate tickers/values; include "as-of" timestamps
* State uncertainty when data is missing or ambiguous
* If caps are hit, propose narrower parameters
* Use tools for factual data; Code Interpreter for calculations

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
* **Evals/Tracing (Phase 2):** comprehensive eval framework with prompt testing, user journey validation, and RLHF integration.

---

## 12) Phase 2: Advanced Analytics & Evaluation (4-6 weeks post-MVP)

### Calculation Engine Integration
* Register function tools for **calculation‑engine** endpoints (risk factors, exposures, attribution, scenario/stress, Greeks, etc.).
* Add optional **async job wrappers** behind sync tool calls for long‑running analytics; still present a simple sync tool to the model.
* Consider splitting `agent/` to its own service if scaling diverges.

### Evaluation Framework
* **Prompt Testing Suite:** Automated tests for each prompt version against golden queries
* **User Journey Validation:** End-to-end testing of common workflows
* **Response Quality Metrics:** Accuracy, completeness, hallucination detection
* **A/B Testing Infrastructure:** Compare prompt versions systematically
* **Performance Benchmarks:** Latency, token usage, cost per query

### RLHF Feedback Mechanisms
* **User Feedback Collection:**
  * Thumbs up/down on responses
  * Correction suggestions
  * "This was helpful/not helpful" indicators
  * Optional text feedback for improvements
* **Dynamic Prompt Adjustment:**
  * Store feedback with conversation context
  * Identify patterns in negative feedback
  * Auto-adjust prompt templates based on feedback clusters
  * Version control for prompt iterations
* **Feedback Loop Implementation:**
  * Weekly prompt performance reviews
  * Automated alerts for degradation
  * Human-in-the-loop validation for significant changes

---

## 12.5) Phase 3: Multi-LLM Testing Platform (8-10 weeks post-MVP)

### Rationale
Rather than assuming which model works best for which task, Phase 3 implements comprehensive A/B testing across all major LLMs to empirically determine the optimal model/prompt combination for portfolio analysis. Different models may excel at different aspects critical to our use case: quantitative finance expertise, mathematical reasoning, tool usage accuracy, and code interpretation capabilities.

### Provider Integration
* **OpenAI GPT:**
  * GPT-4/5 variants
  * Baseline performance metrics
  * Existing tool integration
* **Anthropic Claude:**
  * Claude 3 Opus/Sonnet variants
  * Test for reasoning depth and accuracy
  * Native tool use implementation
* **Google Gemini:**
  * Gemini Pro/Ultra variants
  * Test multimodal and analytical capabilities
  * Function calling compatibility layer
* **xAI Grok:**
  * Grok-2 variants
  * Test for speed and market analysis
  * API integration and tool adaptation

### Provider Abstraction Layer
* **Unified Interface:**
  * Model-agnostic tool calling format
  * Standardized streaming protocol
  * Common error handling
  * Consistent token counting
* **Provider Capabilities Registry:**
  * Max tokens, context window
  * Tool calling support level
  * Streaming capabilities
  * Cost per token

### Testing Dimensions
* **Quantitative Finance Expertise:**
  * Understanding of financial metrics and terminology
  * Accuracy in interpreting portfolio data
  * Knowledge of market mechanics
* **Mathematical Reasoning:**
  * Correctness of calculations
  * Handling of complex formulas
  * Statistical analysis capabilities
* **Tool Usage Proficiency:**
  * Accuracy in tool selection
  * Parameter correctness
  * Efficient tool call sequences
* **Code Interpretation:**
  * Quality of generated Python code
  * Data manipulation accuracy
  * Visualization code generation

### A/B Testing Framework
* **Bucket Testing Strategy:**
  * Random user assignment to model/prompt combinations
  * Controlled experiments with identical queries
  * Statistical significance testing
* **Performance Metrics:**
  * Task completion accuracy
  * Response latency
  * Token efficiency
  * User satisfaction scores
  * Hallucination rates
* **Prompt Variations:**
  * Test same prompt across all models
  * Test model-optimized prompts
  * Iterate based on performance data

### Model Selection Outcome
* **Data-Driven Decision:**
  * Identify best overall performer for default model
  * Document model strengths/weaknesses
  * Create model selection matrix
* **Optimal Configuration:**
  * Best model/prompt combination for finance use case
  * Fallback strategies for model failures
  * Cost/performance trade-off analysis

---

## 13) Implementation Timeline

### Phase 1: MVP Chat Agent (1 week sprint)

**Backend (Days 1-3) - With Service Separation in Mind**
* ✅ Setup auth (POST login + HTTP‑only cookie) - COMPLETED
* Day 1: Create `/chat/conversations`, `/chat/send` endpoints
  * Place in separate `app/agent/` module, not mixed with core backend
  * Use dependency injection for Raw Data API clients
* Day 2: Register the six Raw Data tools; wire handlers  
  * Tool handlers make HTTP calls to Raw Data APIs (even when co-located)
  * No direct database access or model imports
* Day 3: Draft Green/Blue/Indigo/Violet prompts; test streaming
  * Separate configuration file for Agent-specific settings
  * Independent logging with "agent." prefix

**Frontend MVP (Days 4-5)**
* Day 4: Minimal chat UI (single HTML/JS file if needed)
  * SSE connection handling
  * Display streaming text
  * Send button and input field
* Day 5: Polish and testing
  * Mode switcher (Green/Blue/Indigo/Violet)
  * Basic markdown rendering
  * "Thinking..." during tool calls

**Integration & Testing (Days 6-7)**
* Day 6: End-to-end testing with real portfolios
* Day 7: Bug fixes and deployment preparation

### Phase 2: Advanced Analytics & Evaluation (Weeks 3-8)

**Weeks 3-4: Calculation Engine Tools**
* Integrate risk factors, exposures, attribution endpoints
* Implement async job wrappers for long-running calculations
* Add stress testing and Greeks calculations

**Weeks 5-6: Evaluation Framework**
* Build automated prompt testing suite
* Implement user journey validation
* Create response quality metrics and benchmarks
* Deploy comprehensive tracing (Langfuse/OpenTelemetry)

**Weeks 7-8: RLHF Implementation**
* Add feedback UI components (thumbs, corrections)
* Build feedback storage and analysis pipeline
* Implement dynamic prompt adjustment system
* Create prompt version control and rollback

### Phase 3: Multi-LLM Testing Platform (Weeks 9-16)

**Weeks 9-10: Provider Abstraction & Testing Framework**
* Design unified LLM interface
* Build provider capabilities registry
* Implement common tool calling format
* Create A/B testing infrastructure
* Design performance measurement system

**Weeks 11-12: Multi-Provider Integration**
* Integrate Anthropic Claude API
* Integrate Google Gemini API
* Integrate xAI Grok API
* Ensure all models work with existing tools
* Standardize streaming across providers

**Weeks 13-14: Comprehensive Testing**
* Deploy bucket testing with real users
* Test identical queries across all models
* Test model-specific optimized prompts
* Measure performance across all dimensions
* Collect user feedback and preferences

**Weeks 15-16: Analysis & Selection**
* Analyze test results for statistical significance
* Compare models on finance expertise
* Evaluate tool usage accuracy
* Assess code interpretation quality
* Select optimal model/prompt combination as default
* Document findings and create selection matrix

---

## 14) Technical Architecture Evolution

### Phase 1 Architecture (Current)
```
Backend → OpenAI API → Raw Data Tools → Response
```

### Phase 2 Architecture (Enhanced)
```
Backend → OpenAI API → [Raw Data + Calc Engine Tools]
    ↓
Eval Framework → Feedback DB → Prompt Optimizer
```

### Phase 3 Architecture (Multi-LLM Testing)
```
Backend → A/B Test Controller → [OpenAI | Anthropic | Gemini | Grok]
             ↓                        ↓
      Unified Tool Interface → All Tools
             ↓
      Performance Analytics → Model Selection
```

### Key Architectural Components by Phase

**Phase 1 (MVP):**
- Single provider (OpenAI)
- Direct API integration
- Simple conversation storage
- Basic SSE streaming

**Phase 2 (Advanced):**
- Eval framework with golden queries
- Feedback collection system
- Dynamic prompt templates
- Performance monitoring
- Async job queue for heavy calculations

**Phase 3 (Testing Platform):**
- Provider abstraction layer
- Unified tool calling interface
- A/B testing controller
- Performance measurement system
- Model comparison analytics
- Optimal model selection based on empirical data

---

## 15) Success Metrics by Phase

### Phase 1 Metrics (MVP)
- Stream start ≤ 3s p50
- Complete response ≤ 8-10s p95
- 80% pass rate on 15 golden queries
- 70% Good/Excellent usefulness rating

### Phase 2 Metrics (Advanced)
- 95% pass rate on expanded 50-query test suite
- <5% hallucination rate on factual queries
- 85% positive feedback rate
- 20% improvement in response quality from RLHF
- Full calculation engine coverage

### Phase 3 Metrics (Testing Platform)
- Complete testing across 4+ LLM providers
- Statistical significance in model performance differences
- Clear identification of best model for finance use case
- >90% accuracy in tool usage for selected model
- Optimal cost/performance ratio identified
- Comprehensive performance matrix across all testing dimensions

---

## 16) Appendix — Tool Mapping Table

| Tool Name                    | Method & Path                                            | Key Inputs                                                                      | Output Notes                                            |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `get_portfolio_complete`     | `GET /api/v1/data/portfolio/{portfolio_id}/complete`     | `portfolio_id` (UUID), `include_positions?`, `include_cash?`, `as_of_date?`     | Raw portfolio snapshot; no derived metrics              |
| `get_portfolio_data_quality` | `GET /api/v1/data/portfolio/{portfolio_id}/data-quality` | `portfolio_id` (UUID), `check_factors?`, `check_correlations?`                  | Feasibility/availability flags for downstream analytics |
| `get_positions_details`      | `GET /api/v1/data/positions/details`                     | `portfolio_id` or `position_ids`, `include_closed?`                             | Position-level rows + summary                           |
| `get_prices_historical`      | `GET /api/v1/data/prices/historical/{portfolio_id}`      | `portfolio_id` (UUID), `lookback_days?`, `include_factor_etfs?`, `date_format?` | Time-series per symbol (OHLCV, adjusted\_close)         |
| `get_current_quotes`         | `GET /api/v1/data/prices/quotes`                         | `symbols` (comma list), `include_options?`                                      | Real-time quotes; options chains optional               |
| `get_factor_etf_prices`      | `GET /api/v1/data/factors/etf-prices`                    | `lookback_days?`, `factors?`                                                    | Historical prices for factor ETFs                       |

---

## 17) FAQ & Notes

* **Are Raw Data tools sync?** Yes—keep them fast (p95 ≤ \~5–6s). If something is heavy, move it to Phase 2 with an async wrapper.
* **How does Agents SDK fit?** It orchestrates prompts/tools; you still implement endpoints in FastAPI. Start with server‑side handlers calling your service layer; if you split the agent into its own service later, call the same endpoints via HTTP.
* **Model default?** Phase 1: `gpt-5` default; Phase 3: Empirically determined best performer becomes default.
* **Why multi-LLM in Phase 3?** To empirically determine which model/prompt combination works best for quantitative finance use cases. We'll test across dimensions like finance expertise, mathematical reasoning, tool usage accuracy, and code interpretation to find the optimal configuration rather than making assumptions.
* **How will RLHF work?** Collect feedback → identify patterns → adjust prompts dynamically. Start with manual reviews, automate over time.

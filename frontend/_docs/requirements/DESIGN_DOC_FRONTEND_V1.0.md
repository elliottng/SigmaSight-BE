# DESIGN\_DOC\_FRONTEND\_V1.0.md — Frontend (Next.js) for SigmaSight Agent

**Date:** 2025-08-26
**Owners:** Frontend Engineering
**Audience:** AI coding agent
**Status:** Ready for implementation (revised)

---

## 1) Overview & Scope

**Goal:** Build a Next.js frontend that integrates with backend SSE chat to provide a professional portfolio-analysis chat powered by GPT‑5 with Raw Data tools and Code Interpreter.

**Scope (Phase 1):**

* **Two‑step SSE streaming**: `POST /chat/send` → `{ run_id }` then **`GET /chat/stream?run_id=…`** via EventSource
* HTTP‑only cookie authentication (24h TTL)
* Tool execution breadcrumbs + Code Interpreter results
* Analyst mode switching via **slash commands** (piggyback on next send)
* Same‑origin deployment (no CORS complexity)
* Mobile‑responsive UI

**Out of scope:** Conversation list/search/delete, dark mode, advanced viz, CSV exports, file uploads.

---

## 2) Architecture & Integration

```
Frontend (Next.js 15, same origin)
  ├─ POST /api/v1/auth/login  → sets HTTP‑only cookie (JWT)
  ├─ POST /chat/conversations → { conversation_id }
  ├─ POST /chat/send          → { run_id }   (starts run)
  └─ GET  /chat/stream?run_id=…  (EventSource SSE)
                                   │
                                   └─ Backend ↔ OpenAI Responses (GPT‑5)
                                        ├─ Raw Data tools
                                        └─ Code Interpreter
```

**Notes**

* **Same origin**: no CORS headers required; cookies sent automatically.
* **SSE infra**: Nginx must set `proxy_buffering off;` `X-Accel-Buffering: no` and extend read timeouts.
* **Security**: Frontend never calls OpenAI directly.

---

## 3) File Structure & Assets

```
frontend/
├── src/app/
│   ├── layout.tsx
│   ├── page.tsx                 # redirect to /chat
│   ├── login/page.tsx
│   └── chat/page.tsx            # main chat interface
├── src/components/
│   ├── auth/LoginForm.tsx
│   ├── chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   ├── ToolBreadcrumbs.tsx
│   │   └── CodeInterpreterResult.tsx
│   └── ui/{LoadingSpinner,ErrorDisplay}.tsx
├── src/hooks/
│   ├── useAuth.ts
│   ├── useSSEChat.ts            # two‑step EventSource flow
│   └── useSlashCommands.ts
├── src/lib/
│   ├── api.ts                   # login, conversations, send, telemetry
│   └── types.ts                 # ChatMessage, ToolExecution, CodeResult, SSE events
├── src/utils/
│   ├── sse.ts                   # multi‑line data frame parser
│   └── slashCommands.ts
├── public/assets/sigmasight-logo.png
├── globals.css  tailwind.config.js  postcss.config.js  tsconfig.json
└── package.json
```

---

## 4) Authentication (HTTP‑only cookie)

### 4.1 Login page (`/login`)

* **API:** `POST /api/v1/auth/login` with `{ username, password }`
* **Server:** sets **HTTP‑only**, SameSite=Lax cookie (TTL 24h)
* **Redirect:** `/chat` on success; show inline error on 401/400

### 4.2 Auth hook (`useAuth`)

* On mount: hit a lightweight `/me` or check a protected route; set `isAuthenticated`/`isLoading`
* On 401 from any API/SSE: redirect to `/login`
* **No token in JS** (cookie only)

### 4.3 Route protection

* `/chat` guards unauthenticated users → `/login`

---

## 5) Chat Flow (Two‑step SSE)

### 5.1 Contract

1. **Start run**: `POST /chat/send` body:
   `{ conversation_id, text, mode_override? }` → returns `{ run_id }`
2. **Stream**: `new EventSource(`/chat/stream?run\_id=\${runId}`)`

### 5.2 Hook: `useSSEChat`

Responsibilities:

* Manage **conversation\_id** (see §6) and **current EventSource** instance
* `sendMessage(text, opts?)` → POST send → open EventSource → parse events
* **Abort previous stream** on new send: `es?.close()` before opening another
* Track `messages`, `currentTool`, `connected`, `error`, `startTime`
* On `done`: emit **run summary** via `api.postRunTelemetry(...)`

**Event handlers (match backend TDD):**

* `start` → initialize accumulating assistant message
* default `message` → `{ delta }` append to current assistant content
* `tool_call` → push breadcrumb with `name`, `args`
* `tool_result` → update breadcrumb with `meta` and optional `preview`
* `error` → show toast; close stream; set `error`
* `done` → finalize message; close stream

**Parser:** Use `sse.ts` to handle **multi‑line ****`data:`**** frames**; JSON parse inside try/catch.

### 5.3 SSE auth & reliability

* Same origin: cookies attach automatically
* Keep‑alive: backend sends heartbeat `:\n` \~15s
* Reconnects: if network drops mid‑run, close stream, mark message as interrupted, allow manual **Retry**

---

## 6) Conversation & Mode

### 6.1 Conversation persistence

* Store `{ conversation_id }` in **`sessionStorage`** (per‑tab, survives refresh)
* If missing, create with `POST /chat/conversations`

### 6.2 Modes via slash commands (piggyback)

* Supported commands: `/mode analyst-blue`, `/mode analyst-green`
* `useSlashCommands` parses the input:

  * If `/mode …`: set `nextMode` state and **do not send** a user message
  * Next call to `sendMessage(...)` includes `{ mode_override: … }` in the **POST /chat/send** body
* UI: small header chip: “Mode: Analyst Blue/Green”

---

## 7) Rendering

### 7.1 Message model

```ts
export type ChatMessage = {
  id: string;
  sender: 'user' | 'assistant';
  content: string;           // streamed for assistant
  timestamp: string;         // ISO string
  toolExecutions?: ToolExecution[];
  codeResults?: CodeResult[];
};
```

### 7.2 Tool breadcrumbs

```ts
export type ToolExecution = {
  name: string;
  args: Record<string, unknown>;
  status: 'running' | 'completed' | 'error';
  startedAt?: number;
  endedAt?: number;
  meta?: {
    truncated?: boolean;
    suggested_params?: Record<string, unknown>;
    rows_returned?: number;
  };
};
```

* Default collapsed; expand to show `args`, `meta`, and timing

### 7.3 Code Interpreter results

```ts
export type CodeResult = {
  type: 'code' | 'result' | 'error';
  content: string;      // e.g., Python code or stdout
  table?: Array<Record<string, any>>; // if CI returns rows for FE charts
};
```

* Render code with syntax highlighting (readonly)
* Small tables: render HTML table (cap preview at 50 rows)
* Charts: FE renders simple line/bar from `table` when provided

### 7.4 Markdown safety

* Use `react-markdown` + `rehype-sanitize` (no inline HTML by default)

---

## 8) Error Handling

**Buckets & UX**

* **Auth (401)**: backend sends an `error` event `{ code: 401 }` then closes → redirect `/login`
* **Rate limit (429)**: show toast “Cooling down 10s…”, backoff on next send
* **Tool failure**: show toast with `suggested_params` if present; message remains but annotate with a warning
* **SSE connection**: show “Connection lost. Retry?” with a button; closing a run to send a new message is **not** an error (normal)

Developer logging: log type, original error, and request context to console (dev builds only)

---

## 9) Performance & UX

* **Connection start** < 3s p50; **answer complete** < 8–10s p95 (one or two tool calls)
* Only one live EventSource at a time (close previous on new send)
* Keyboard: `Enter` send, `Shift+Enter` newline
* Accessibility: streamed container has `aria-live="polite"`

---

## 10) API Layer (`src/lib/api.ts`)

* `login({ username, password })` → POST `/api/v1/auth/login`
* `createConversation()` → POST `/chat/conversations`
* `send({ conversation_id, text, mode_override? })` → POST `/chat/send` → `{ run_id }`
* `openStream(runId)` → `new EventSource(`/chat/stream?run\_id=\${runId}`)`
* `postRunTelemetry(payload)` → POST `/telemetry/runs`

---

## 11) Types (`src/lib/types.ts`)

* `SSEEvents`: `start`, default `{ delta }`, `tool_call`, `tool_result`, `error`, `done`
* `ChatMessage`, `ToolExecution`, `CodeResult` (see §7)

---

## 12) SSE Utils (`src/utils/sse.ts`)

* `parseEventStream(lineAppender)` that collects multi‑line frames until blank line, then yields `{ event?, data }`
* Helper to safely `JSON.parse` `data` with try/catch

---

## 13) Slash Commands (`src/utils/slashCommands.ts`)

* Recognize `/mode analyst-blue|analyst-green`
* Return `{ type: 'mode_change', mode, shouldSend: false }` or `{ type: 'message', content, shouldSend: true }`

---

## 14) Conversation Persistence

* On `/chat` load:

  1. read `sessionStorage.getItem('conversation_id')`
  2. if missing → `createConversation()` and store it
  3. pass `conversation_id` to `useSSEChat`

---

## 15) Telemetry (client‑side)

* After `done`, compute `duration_ms` and send:

```json
{
  "run_id":"run_…",
  "conversation_id":"conv_…",
  "mode":"analyst-blue",
  "duration_ms": 5120,
  "tool_calls": 2,
  "tool_names": ["get_positions_details","get_prices_historical"],
  "tokens_prompt": null,
  "tokens_completion": null,
  "model": "gpt-5",
  "cost_est_usd": null,
  "rating": null
}
```

* **Note:** if backend later includes token/cost in `done`, populate those fields.

---

## 16) Responsive Design (minimal)

* Use legacy `globals.css` breakpoints and spacing
* On mobile: input full width; breadcrumbs collapsed; header compact

---

## 17) Implementation Plan

**Week 1**

1. Project setup + legacy asset migration
2. Auth (login + guards)
3. Two‑step SSE plumbing (send → stream)
4. Basic chat with streaming and breadcrumbs

**Week 2**

1. Slash commands (mode piggyback)
2. Code Interpreter result rendering (tables/charts)
3. Error handling polish, accessibility
4. Telemetry POST + mobile refinements

---

## 18) Success Criteria

* ✅ Two‑step SSE chat (start <3s p50)
* ✅ Auth via HTTP‑only cookies
* ✅ Mode switching via slash commands (piggyback)
* ✅ Breadcrumbs & CI results render cleanly
* ✅ Same‑origin deployment; no CORS issues
* ✅ Telemetry POST after runs

---

## 3A) Legacy Frontend Reuse Strategy (how we reuse vs. re‑implement)

This section maps the **legacy implementation** to our new SSE architecture so an AI coding agent knows what to **copy**, what to **use as inspiration**, and what to **avoid**.

### A. High‑priority — **Direct Copy** (unchanged)

* **Branding assets**

  * `frontend/public/assets/sigmasight-logo.png` → same path
  * `frontend/src/assets/SigmaSight Logo.png` → same path (if used by any pages)
* **Styling system**

  * `frontend/src/app/globals.css`
  * `frontend/tailwind.config.js`
  * `frontend/postcss.config.js`
* **TypeScript config**

  * `frontend/tsconfig.json`
  * `frontend/next-env.d.ts`
* **Package config**

  * Start from new **curated `package.json`**; selectively carry over only vetted deps from legacy (do **not** copy lockfile). After install, let a fresh lockfile be generated.

> **Value:** preserves visual identity, responsive system, and known‑good TS/Next config without dragging in legacy runtime assumptions.

### B. Medium‑priority — **Extract Patterns** (design inspiration, not code)

* **Layout components**

  * Reuse **metadata/title/description** pattern from legacy `layout.tsx`
  * Keep `<body className="antialiased">` and general spacing rhythm
* **Chat UI patterns** (from legacy `chat/page.tsx`)
  **KEEP (structure only):**

  * Header with logo + connection status area
  * Message container column layout
  * Input area placement (textarea + send button, absolute‑positioned button on the right)
  * Responsive breakpoints/classes used in legacy CSS
    **DO NOT COPY:**
  * Any `fetch()` calls
  * Message state handling
  * Client‑side auth logic
  * Static request/response flows (we use **two‑step SSE**)

> **Why:** legacy logic is incompatible with SSE + cookie auth; but the visual/layout patterns are good.

### C. Low‑priority — **Reference Only**

* `frontend/next.config.js` — consult for ideas, but **do not** port blindly; SSE needs its own proxy/timeouts.
* Legacy docs (e.g., `frontend/frontendsetup.md`, `docs/ClaudeInstructions.md`) — archive as a reference, create a new `LEGACY_REFERENCE.md` summarizing what was reused.

### D. **Do Not Migrate** — incompatible with new architecture

* **Chat logic & API integration** from legacy `chat/page.tsx` (request/response, no streaming)
* **Authentication patterns** (client‑managed JWTs, bearer headers)

> **Reason:** New design uses **HTTP‑only cookies** and **two‑step EventSource SSE**; porting the logic would introduce bugs and security risks.

### E. Migration checklist & script (for humans/agents)

1. Create a **legacy branch & tag** to freeze the prior state (use your `git show`/`git tag` steps).
2. Copy assets/configs exactly as listed in **A**.
3. Create new curated `package.json`; install fresh to generate a new lockfile.
4. Build new app scaffolding per **§3 File Structure** of this FE design doc.
5. Add `LEGACY_REFERENCE.md` documenting what was copied vs. referenced.
6. Implement **SSE first** (two‑step flow), then auth guards, then chat UI.

> **Compatibility notes:**
>
> * Keep **Next 15.x**; React 18/19 both work but ensure versions match your dependencies.
> * Ensure **same‑origin** deployment so cookies attach automatically.
> * Configure proxy for SSE: `proxy_buffering off;` `X-Accel-Buffering: no` and longer read timeouts.
> * Use `react-markdown` + `rehype-sanitize` (do not render raw HTML from model).

### Appendix — Quick migration commands (adapt to your repo)
** Note: thes are not the actual legacy files, it's just an example **
```bash
# 1) Freeze legacy
git checkout -b legacy/frontend-gpt-agent-v1
git push origin legacy/frontend-gpt-agent-v1
git tag -a legacy-v1.0 -m "Legacy frontend implementation"
git push origin legacy-v1.0

# 2) Copy assets/configs (examples)
mkdir -p frontend/src/app frontend/public/assets frontend/src/assets
git show legacy-v1.0:frontend/src/app/globals.css > frontend/src/app/globals.css
git show legacy-v1.0:frontend/tailwind.config.js > frontend/tailwind.config.js
git show legacy-v1.0:frontend/postcss.config.js > frontend/postcss.config.js
git show legacy-v1.0:frontend/tsconfig.json > frontend/tsconfig.json
git show legacy-v1.0:frontend/next-env.d.ts > frontend/next-env.d.ts
git show legacy-v1.0:frontend/public/assets/sigmasight-logo.png > frontend/public/assets/sigmasight-logo.png

# 3) Create curated package.json; npm install
```

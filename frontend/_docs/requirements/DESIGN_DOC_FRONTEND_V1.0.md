# DESIGN\_DOC\_FRONTEND\_V1.0.md — Frontend (Next.js) for SigmaSight Agent

**Date:** 2025-08-28 (Revised)
**Owners:** Frontend Engineering
**Audience:** AI coding agent  
**Status:** Ready for implementation with complete backend integration

> **🚨 CRITICAL REFERENCES**: This document must be read alongside the comprehensive agent documentation:
> 
> **Primary Implementation Guides:**
> - `../../agent/_docs/FRONTEND_AI_GUIDE.md` - **START HERE** - Complete API reference for AI agents
> - `../../agent/_docs/API_CONTRACTS.md` - Full TypeScript interfaces and contracts
> - `../../agent/_docs/SSE_STREAMING_GUIDE.md` - Production-ready SSE implementation
> - `../../agent/_docs/FRONTEND_FEATURES.md` - Detailed UI/UX specifications
> - `../../agent/_docs/FRONTEND_DEV_SETUP.md` - Development environment setup
>
> **Backend Documentation:**
> - `../../backend/AI_AGENT_REFERENCE.md` - Backend patterns and architecture
> - `../../backend/API_IMPLEMENTATION_STATUS.md` - Current API status (100% complete)
> - `../../agent/TODO.md` - Implementation progress (Phases 0-8 complete)

---

## 1) Overview & Scope

**Goal:** Build a Next.js frontend that integrates with the fully-implemented SigmaSight chat backend to provide professional portfolio analysis powered by GPT-4o with Raw Data tools.

**✅ Backend Status (2025-08-28):**
- OpenAI integration complete with streaming SSE
- All Raw Data APIs working with real data
- Authentication system fully functional
- 6 portfolio analysis tools ready

**Scope (Phase 1):**

* **Single-step SSE streaming**: `POST /chat/send` → direct SSE stream (not two-step)
* JWT Bearer token authentication (stored in localStorage)
* Tool execution indicators + real-time streaming
* 4 conversation modes: green (educational), blue (quantitative), indigo (strategic), violet (risk-focused)
* Mode switching via `/mode` commands or UI selector
* CORS configured for localhost development
* Mobile‑responsive UI

**✅ Available Features:**
- Complete conversation management (create/delete/list/history)
- Real portfolio analysis with 6 working tools
- Message persistence and conversation history
- Error handling with retry logic

---

## 2) Architecture & Integration

```
Frontend (Next.js 15 + React)
  ├─ POST /api/v1/auth/login         → { access_token, user }
  ├─ GET  /api/v1/auth/me            → { user, portfolios }
  ├─ POST /api/v1/chat/conversations → { conversation_id }
  ├─ GET  /api/v1/chat/conversations → { conversations[] }
  ├─ DELETE /api/v1/chat/conversations/{id}
  ├─ GET  /api/v1/chat/conversations/{id}/messages → { messages[] }
  └─ POST /api/v1/chat/send          → SSE Stream (text/event-stream)
                                        │
                                        └─ Backend ↔ OpenAI GPT-4o
                                             ├─ 6 Portfolio Analysis Tools
                                             └─ Real-time streaming response
```

**✅ Current Implementation Notes:**

* **Authentication**: JWT Bearer tokens with `Authorization: Bearer ${token}` header
* **CORS**: Configured for `http://localhost:3000` and `http://localhost:5173` 
* **SSE Format**: Direct streaming from `/chat/send` (single-step, not two-step)
* **Tools Available**: `get_portfolio_complete`, `get_portfolio_data_quality`, `get_positions_details`, `get_prices_historical`, `get_current_quotes`, `get_factor_etf_prices`
* **Models**: Using `gpt-4o` (not gpt-5 due to org verification requirements)
* **Security**: All API keys secured on backend, frontend never calls OpenAI directly

**🔗 Reference**: See `../../agent/_docs/API_CONTRACTS.md` for complete TypeScript interfaces

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

## 4) Authentication (JWT Bearer Tokens)

### 4.1 Login page (`/login`)

* **API:** `POST /api/v1/auth/login` with `{ email, password }`
* **Response:** `{ access_token: "jwt...", token_type: "bearer", user: {...} }`
* **Storage:** Token stored in `localStorage` as `auth_token`
* **Redirect:** `/chat` on success; show inline error on 401/400

**✅ Test Credentials:**
```javascript
const TEST_USER = {
  email: "demo_growth@sigmasight.com", 
  password: "demo12345"
}
```

### 4.2 Auth hook (`useAuth`)

* **Token Management:** Load from localStorage on mount, set Authorization header
* **Current User:** `GET /api/v1/auth/me` returns user + portfolio info
* **401 Handling:** Redirect to `/login` and clear stored token
* **Logout:** `POST /api/v1/auth/logout` + clear localStorage

**🔗 Reference**: See `../../agent/_docs/FRONTEND_AI_GUIDE.md` for complete auth implementation

### 4.3 Route protection  

* `/chat` guards unauthenticated users → `/login`
* All API calls include `Authorization: Bearer ${token}` header
* SSE connections include auth header for streaming

---

## 5) Chat Flow (Single-step SSE Streaming)

### 5.1 ✅ Current Implementation Contract

**Single-step flow**: `POST /chat/send` → direct SSE stream response

```javascript
// Request
POST /api/v1/chat/send
Headers: {
  'Authorization': 'Bearer ${token}',
  'Content-Type': 'application/json',
  'Accept': 'text/event-stream'
}
Body: {
  conversation_id: "uuid",
  text: "What is my portfolio value?"
}

// Response: SSE stream with events
```

**🔗 Reference**: See `../../agent/_docs/SSE_STREAMING_GUIDE.md` for complete implementation

### 5.2 ✅ SSE Event Types (Already Working)

* **`start`** → `{ conversation_id, mode, model }` - Stream initialization  
* **`message`** → `{ delta, role }` - Text chunks from AI response
* **`tool_started`** → `{ tool_name, arguments }` - Tool execution begins
* **`tool_finished`** → `{ tool_name, result, duration_ms }` - Tool execution complete
* **`done`** → `{ tool_calls_count, latency_ms }` - Response complete
* **`error`** → `{ message, retryable }` - Error occurred
* **`heartbeat`** → `{ timestamp }` - Keep connection alive

### 5.3 Hook Implementation (`useChat`)

**✅ Reference Implementation Available**: `../../agent/_docs/SSE_STREAMING_GUIDE.md`

Key features:
* **Real-time streaming**: Parse SSE events and update UI progressively
* **Tool execution tracking**: Show when AI is using portfolio analysis tools
* **Error handling**: Reconnection logic with exponential backoff  
* **Message persistence**: Store conversations in database
* **Abort control**: Cancel streaming on new message send

### 5.4 Authentication & Reliability

* **JWT Headers**: Include `Authorization: Bearer ${token}` for SSE
* **Reconnection**: Automatic retry with backoff on connection loss
* **Heartbeats**: Server sends periodic keep-alive events
* **CORS**: Pre-configured for localhost development

---

## 6) Conversation & Mode Management

### 6.1 ✅ Conversation Management (Full CRUD Available)

**✅ Complete API Implementation:**
* **Create**: `POST /api/v1/chat/conversations` → `{ conversation_id, mode, created_at }`
* **List**: `GET /api/v1/chat/conversations` → `{ conversations[], total_count }`  
* **Delete**: `DELETE /api/v1/chat/conversations/{id}`
* **History**: `GET /api/v1/chat/conversations/{id}/messages` → `{ messages[] }`

**Storage Strategy:**
* Store current `conversation_id` in state management (Zustand/Context)
* Persist conversation list from API calls
* Auto-create new conversation if none selected

**🔗 Reference**: Complete conversation management in `../../agent/_docs/API_CONTRACTS.md`

### 6.2 ✅ Four Conversation Modes (Working)

**Available Modes:**
* **`green`** (default): 🟢 Educational - Explains concepts with context and teaching
* **`blue`**: 🔵 Quantitative - Focuses on numbers, metrics, and precise analysis  
* **`indigo`**: 🟣 Strategic - Provides big-picture insights and strategic narratives
* **`violet`**: 🟤 Risk-Focused - Emphasizes conservative analysis and risk assessment

**Mode Switching Options:**
1. **Slash Commands**: Send `/mode blue` message to switch modes
2. **UI Selector**: Dropdown/buttons in conversation interface
3. **Per-Conversation**: Each conversation maintains its own mode

**🔗 Reference**: See `../../agent/prompts/` for complete mode implementations

---

## 7) Rendering

### 7.1 ✅ Message Model (Complete TypeScript Definitions)

```ts
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;           // streamed for assistant
  timestamp: Date;           // Date object (convert from ISO)
  streaming?: boolean;       // indicates if message is still being streamed
  toolCalls?: ToolExecution[];
  metadata?: {
    model?: string;
    tokens?: number;
    cost_usd?: number;
  };
}
```

**🔗 Reference**: Complete message types in `../../agent/_docs/API_CONTRACTS.md`

### 7.2 ✅ Tool Breadcrumbs (Live Tool Execution Tracking)

```ts
export interface ToolExecution {
  tool_name: string;
  duration_ms?: number;
  status: 'running' | 'completed' | 'error';
  result?: any;
  metadata?: {
    rows_returned?: number;
    truncated?: boolean;
    suggested_params?: Record<string, unknown>;
  };
}
```

**Real-time Updates via SSE:**
- `tool_started` event: Tool begins execution
- `tool_finished` event: Tool completes with results and timing
- `error` event: Tool fails with error details

**🔗 Reference**: Complete tool execution patterns in `../../agent/_docs/SSE_STREAMING_GUIDE.md`

### 7.3 ✅ Portfolio Analysis Results

**Tool Results Display:**
- Portfolio data tables (positions, performance metrics)
- Market data visualizations (price charts, volatility)
- Risk analysis outputs (factor exposures, correlations)
- Financial calculations (returns, Sharpe ratios, drawdowns)

**Rendering Strategy:**
- JSON data tables: Responsive HTML tables
- Large datasets: Pagination or virtual scrolling
- Charts: Simple line/bar charts for key metrics
- Code blocks: Syntax highlighting for calculations

**🔗 Reference**: Complete data visualization patterns in `../../agent/_docs/FRONTEND_FEATURES.md`

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

## 10) ✅ API Layer Implementation (`src/lib/api.ts`)

**Working Endpoints:**
* `login({ email, password })` → POST `/api/v1/auth/login` → `{ access_token, user }`
* `createConversation({ mode })` → POST `/api/v1/chat/conversations` → `{ conversation_id }`
* `getConversations()` → GET `/api/v1/chat/conversations` → `{ conversations[] }`
* `deleteConversation(id)` → DELETE `/api/v1/chat/conversations/{id}`
* `sendMessage({ conversation_id, text })` → POST `/api/v1/chat/send` → SSE stream

**Single-Step SSE (No run_id needed):**
```typescript
// Direct streaming response from /chat/send
const response = await fetch('/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({ conversation_id, text })
});
```

**🔗 Reference**: Complete API client implementation in `../../agent/_docs/FRONTEND_DEV_SETUP.md`

---

## 11) ✅ Complete Type Definitions (`src/lib/types.ts`)

**SSE Event Types:**
```typescript
type SSEEventData = 
  | { event: "start"; data: { conversation_id: string; mode: string } }
  | { event: "message"; data: { delta: string; role: string } }
  | { event: "tool_started"; data: { tool_name: string } }
  | { event: "tool_finished"; data: { tool_name: string; duration_ms: number; result: any } }
  | { event: "error"; data: { code?: number; message: string } }
  | { event: "done"; data: { tool_calls_count: number; tokens?: number } }
```

**Core Types:**
* `ConversationMode`: `'green' | 'blue' | 'indigo' | 'violet'`
* `ConversationSummary`: Conversation list item
* `User`, `LoginResponse`, `CurrentUserResponse`: Auth types

**🔗 Reference**: All TypeScript interfaces in `../../agent/_docs/API_CONTRACTS.md`

---

## 12) ✅ SSE Implementation (`src/hooks/useSSE.ts`)

**Complete SSE Hook:**
```typescript
export function useSSE(options: UseSSEOptions = {}) {
  const { onMessage, onError, onOpen, onClose } = options;
  
  const connect = useCallback(async (url: string, headers: Record<string, string>) => {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Accept': 'text/event-stream', ...headers },
      signal: abortController.signal
    });
    
    await processSSEStream(response, onMessage, onError);
  }, []);
}
```

**Stream Processing:**
- Line-by-line parsing with buffering
- JSON parsing with error handling
- Automatic reconnection with exponential backoff
- AbortController for cleanup

**🔗 Reference**: Production-ready implementation in `../../agent/_docs/SSE_STREAMING_GUIDE.md`

---

## 13) ✅ Mode Switching (Multiple Methods)

**Option 1: Slash Commands**
```typescript
// Recognize /mode commands
if (text.startsWith('/mode ')) {
  const mode = text.replace('/mode ', '').trim();
  if (['green', 'blue', 'indigo', 'violet'].includes(mode)) {
    // Update conversation mode
    return { type: 'mode_change', mode, shouldSend: false };
  }
}
```

**Option 2: UI Mode Selector**
- Dropdown or button group in chat interface
- Visual indicators for each mode (colors/icons)
- Persistent per conversation

**Option 3: API Mode Override**
- Pass `mode` parameter to `/chat/send`
- Temporary mode switch for single message

**🔗 Reference**: Mode implementation details in `../../agent/_docs/FRONTEND_FEATURES.md`

---

## 14) ✅ Conversation State Management

**State Persistence Strategy:**
```typescript
// Use Zustand for conversation state
interface ChatState {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  messages: ChatMessage[];
  // ... other state
}

// Load conversations on app start
const loadConversations = async () => {
  const conversations = await api.getConversations();
  setConversations(conversations);
  
  // Auto-select or create conversation
  if (conversations.length === 0) {
    const newConv = await api.createConversation();
    selectConversation(newConv.conversation_id);
  }
};
```

**🔗 Reference**: Complete state management patterns in `../../agent/_docs/FRONTEND_DEV_SETUP.md`

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

## 17) ✅ Ready-to-Implement Architecture

**Phase 1: Core Setup (1-2 days)**
1. Next.js project with TypeScript + Tailwind
2. JWT authentication with login form
3. Basic routing and protected routes
4. API client with Bearer token handling

**Phase 2: Chat Implementation (2-3 days)**
1. SSE streaming hook implementation
2. Chat UI with message bubbles
3. Real-time streaming and tool execution display
4. Conversation management (create/list/delete)

**Phase 3: Polish & Features (1-2 days)**
1. Mode switching UI and slash commands
2. Error handling and reconnection logic
3. Mobile responsive design
4. Performance optimization

**🚀 Accelerated Development**: All backend APIs working, complete documentation available

**🔗 Reference**: Step-by-step setup in `../../agent/_docs/FRONTEND_DEV_SETUP.md`

---

## 18) ✅ Current Backend Status & Success Criteria

### ✅ Backend Implementation Complete (2025-08-28)

**All Required APIs Working:**
- Authentication system with JWT tokens ✅
- Complete conversation CRUD operations ✅  
- Real-time SSE streaming with OpenAI GPT-4o ✅
- 6 portfolio analysis tools functional ✅
- Error handling and reconnection logic ✅
- Message persistence and history ✅

**Performance Targets Met:**
- SSE stream start: < 3 seconds ✅
- Tool execution: Real portfolio data ✅
- OpenAI responses: GPT-4o streaming ✅

### Frontend Success Criteria

* ✅ **Single-step SSE streaming** (POST /chat/send → direct stream)
* ✅ **JWT Bearer token authentication** (localStorage + Authorization header)
* ✅ **Four conversation modes** (green/blue/indigo/violet) with mode switching
* ✅ **Complete conversation management** (create/list/delete/history)
* ✅ **Real portfolio analysis** with 6 working tools
* ✅ **CORS configuration** for localhost development
* ✅ **Mobile-responsive design** requirements

**🚀 Ready for Frontend Development**: All backend APIs documented and working

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
* **Legacy authentication patterns** (client‑managed JWTs, bearer headers) - Now using server-side JWT with localStorage

> **Reason:** New design uses **JWT Bearer tokens** and **single-step EventSource SSE**; porting the legacy logic would introduce bugs and security risks.

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

---

## 🚀 Implementation Status & Next Steps

### ✅ All Prerequisites Complete (2025-08-29)

**Backend Infrastructure Ready:**
- Authentication system with JWT tokens ✅
- Complete SSE streaming with OpenAI GPT-4o ✅  
- 6 portfolio analysis tools working with real data ✅
- CORS configuration for development ✅
- Error handling and reconnection logic ✅

**Complete Documentation Available:**
- `../../agent/_docs/FRONTEND_AI_GUIDE.md` - API endpoints and authentication
- `../../agent/_docs/API_CONTRACTS.md` - TypeScript interfaces and contracts  
- `../../agent/_docs/SSE_STREAMING_GUIDE.md` - Production SSE implementation
- `../../agent/_docs/FRONTEND_FEATURES.md` - UI/UX specifications
- `../../agent/_docs/FRONTEND_DEV_SETUP.md` - Next.js setup and configuration

### 🎯 AI Agent Implementation Guide

**Step 1: Project Setup**
```bash
npx create-next-app@latest sigmasight-frontend --typescript --tailwind --eslint --app --src-dir
cd sigmasight-frontend
```

**Step 2: Install Dependencies** (from FRONTEND_DEV_SETUP.md)
```bash
npm install @tanstack/react-query zustand react-hook-form zod lucide-react
```

**Step 3: Environment Configuration**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Step 4: Implement Core Features**
1. Authentication with JWT Bearer tokens
2. SSE chat implementation using provided hooks
3. Conversation management UI  
4. Mode switching (4 modes: green/blue/indigo/violet)

### 📋 Success Criteria Checklist

- [ ] User can login with demo credentials (demo_growth@sigmasight.com / demo12345)
- [ ] Chat interface streams responses in real-time
- [ ] Tool execution shows live progress indicators
- [ ] Mode switching works (slash commands + UI selector)
- [ ] Conversation management (create/list/delete)
- [ ] Mobile responsive design
- [ ] Error handling with reconnection logic

**🏁 Ready for Frontend Development**: All documentation complete, backend APIs working, test data available.

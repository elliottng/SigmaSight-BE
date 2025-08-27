# SigmaSight Agent Implementation TODO

**Created:** 2025-08-27  
**Status:** Planning  
**Target Completion:** 2 weeks  

---

## 📚 Requirements Documents Cross-Reference

### Primary Specifications
- **[PRD_AGENT_V1.0.md](../_docs/requirements/PRD_AGENT_V1.0.md)** - Product requirements, user flows, success metrics
- **[DESIGN_DOC_AGENT_V1.0.md](../_docs/requirements/DESIGN_DOC_AGENT_V1.0.md)** - Technical design, architecture, existing infrastructure (Section 18)
- **[DESIGN_DOC_FRONTEND_V1.0.md](../../frontend/_docs/requirements/DESIGN_DOC_FRONTEND_V1.0.md)** - Frontend specs (Phase 2)

### Backend Context
- **[API_IMPLEMENTATION_STATUS.md](../../backend/API_IMPLEMENTATION_STATUS.md)** - Current API completion status (23% overall, 100% Raw Data)
- **[TODO3.md](../../backend/TODO3.md)** - Backend Phase 3 status, UTC datetime standardization ✅
- **[AI_AGENT_REFERENCE.md](../../backend/AI_AGENT_REFERENCE.md)** - Codebase patterns, import paths, common errors

---

## 🎯 Overview

Implement a chat-based portfolio analysis agent that uses OpenAI's API with function calling to Raw Data endpoints and Code Interpreter for calculations. This requires new backend chat endpoints, enhancing Raw Data APIs, and tool handler implementations.

**Architecture Requirement:**
- **SERVICE SEPARATION**: Agent must be implemented as an isolated module that can be cleanly extracted into a standalone microservice. See PRD §3.1-3.2 and TDD §2.1 for separation requirements.

**Critical Issues to Address:**
- ✅ GPT-5 now available - use as default model (per OpenAI docs)
- ✅ Raw Data APIs (6/6) return real data - need parameter enhancements only
- Backend chat endpoints don't exist yet - need to implement
- ✅ UTC ISO 8601 standardization COMPLETED (Phase 3)
- ⚠️ Agent must use HTTP calls to Raw Data APIs (no direct DB access)

---

## 📋 Phase 0: Prerequisites & Fixes (Day 1-2)

> **Status Update (2025-08-27):**
> - ✅ Dual authentication (0.3) - COMPLETED and tested
> - ✅ GPT-5 configuration (0.1) - Model references updated
> - ⏳ Environment setup (0.2) - Ready to proceed
> - ⏳ Database schema (0.4) - Next priority

### 0.1 Configure GPT-5 Model Settings
- [ ] **Set up GPT-5 as default model** (ref: PRD §3, TDD §17)
  - [ ] Verify GPT-5 access in OpenAI account
  - [ ] Set MODEL_DEFAULT = "gpt-5"
  - [ ] Set MODEL_FALLBACK = "gpt-5-mini"
  - [ ] Update DESIGN_DOC_AGENT_V1.0.md to confirm GPT-5 usage
  - [ ] Update PRD_AGENT_V1.0.md model references

### 0.2 Environment Setup
- [ ] **Update backend/app/config.py with OpenAI settings**
  ```python
  # Add to Settings class (uses pydantic_settings pattern)
  OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
  OPENAI_ORG_ID: str = Field(default="", env="OPENAI_ORG_ID")  # Optional
  MODEL_DEFAULT: str = Field(default="gpt-5", env="MODEL_DEFAULT")
  MODEL_FALLBACK: str = Field(default="gpt-5-mini", env="MODEL_FALLBACK")
  AGENT_CACHE_TTL: int = Field(default=600, env="AGENT_CACHE_TTL")
  SSE_HEARTBEAT_INTERVAL_MS: int = Field(default=15000, env="SSE_HEARTBEAT_INTERVAL_MS")
  ```

- [ ] **Add to .env file**
  ```bash
  OPENAI_API_KEY=sk-...
  OPENAI_ORG_ID=org-... (if applicable)
  MODEL_DEFAULT=gpt-5
  MODEL_FALLBACK=gpt-5-mini
  AGENT_CACHE_TTL=600
  SSE_HEARTBEAT_INTERVAL_MS=15000
  ```

### 0.3 Implement Dual Authentication Support ✅ **COMPLETED**
> **See canonical implementation**: `backend/TODO3.md` Section 4.0.1 - Dual Authentication Strategy
> Implemented 2025-08-27 - Both Bearer tokens and cookies are now supported!

- [x] **Summary**: Implemented dual auth (Bearer + Cookie) per backend/TODO3.md §4.0.1
  - [x] Bearer tokens work for all REST APIs (preferred method)
  - [x] Cookies work as fallback (required for SSE)
  - [x] No breaking changes - both methods fully supported and tested

### 0.4 Database Schema Updates (via Alembic Migrations)
- [ ] **Create SQLAlchemy models for conversation tables** (ref: TDD §18.2 for patterns)
  - [ ] Create `backend/app/models/conversations.py`
  - [ ] Define `Conversation` model class
  - [ ] Define `ConversationMessage` model class
  - [ ] Import models in `app/models/__init__.py`

- [ ] **Conversation model schema**
  ```python
  class Conversation(Base):
      __tablename__ = "conversations"
      
      id = Column(UUID, primary_key=True, default=uuid4)  # Our canonical ID, returned as conversation_id
      user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
      mode = Column(String(50), default="green")
      
      # Provider tracking (vendor-agnostic)
      provider = Column(String(32), default="openai")
      provider_thread_id = Column(String(255), nullable=True)  # OpenAI thread ID if using Assistants
      provider_run_id = Column(String(255), nullable=True)     # OpenAI run ID if applicable
      
      created_at = Column(DateTime, default=utc_now)
      updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
      metadata = Column(JSONB, default={})  # For model version, settings, etc.
      
      # Relationships
      user = relationship("User", back_populates="conversations")
      messages = relationship("ConversationMessage", back_populates="conversation")
      
      # Indexes
      __table_args__ = (
          Index("idx_conversations_user_id", "user_id"),
          Index("idx_conversations_created_at", "created_at"),
          Index("idx_conversations_provider_thread_id", "provider_thread_id"),  # Non-unique for lookups
      )
  ```

- [ ] **ConversationMessage model schema**
  ```python
  class ConversationMessage(Base):
      __tablename__ = "conversation_messages"
      
      id = Column(UUID, primary_key=True, default=uuid4)
      conversation_id = Column(UUID, ForeignKey("conversations.id"))
      role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system', 'tool'
      content = Column(Text, nullable=True)  # Can be null for tool-only responses
      tool_calls = Column(JSONB, default=[])
      
      # Performance metrics
      first_token_ms = Column(Integer, nullable=True)  # Time to first SSE token (critical metric!)
      latency_ms = Column(Integer, nullable=True)      # Total response time
      
      # Token tracking
      prompt_tokens = Column(Integer, nullable=True)
      completion_tokens = Column(Integer, nullable=True)
      total_tokens = Column(Integer, nullable=True)
      
      # Provider tracking
      provider_message_id = Column(String(255), nullable=True)  # OpenAI message ID for debugging
      
      created_at = Column(DateTime, default=utc_now)
      error = Column(JSONB, nullable=True)
      
      # Relationships
      conversation = relationship("Conversation", back_populates="messages")
      
      # Indexes
      __table_args__ = (
          Index("idx_messages_conversation_id", "conversation_id"),
          Index("idx_messages_created_at", "created_at"),
      )
  ```

- [ ] **Generate and apply Alembic migration**
  - [ ] Generate migration: `cd backend && uv run alembic revision --autogenerate -m "Add conversation tables for agent"`
  - [ ] Review generated migration file in `backend/alembic/versions/`
  - [ ] Verify foreign keys and indexes are correct
  - [ ] Test migration: `uv run alembic upgrade head --sql` (dry run)
  - [ ] Apply migration: `uv run alembic upgrade head`
  - [ ] Verify tables created: `uv run python -c "from app.models.conversations import Conversation, ConversationMessage; print('✅ Models imported successfully')"`
  - [ ] Update `app/database.py` init_db() to import conversation models (line ~85)

- [ ] **Data retention considerations (for production)**
  - [ ] Plan for 30-60 day retention policy to prevent unbounded growth
  - [ ] Consider truncating large tool outputs (store preview only)
  - [ ] Note: Skip PII redaction for prototype phase


---

## 🏗️ Service Separation Architecture (Throughout All Phases)

### Isolation Requirements
- [ ] **Create isolated Agent module structure**
  ```
  backend/app/agent/
  ├── __init__.py
  ├── config.py           # Agent-specific settings (AGENT_ prefix)
  ├── router.py           # FastAPI router for /api/v1/chat/*
  ├── handlers/           # Request handlers
  ├── tools/              # Tool implementations
  ├── clients/            # HTTP client for Raw Data APIs
  ├── models.py           # Agent-specific Pydantic models
  └── logging.py          # Agent-specific logger
  ```

### Development Rules
- [ ] **NO direct database access**
  - [ ] No imports from `app.models.*` (SQLAlchemy models)
  - [ ] No imports from `app.database` (DB session)
  - [ ] No imports from `app.services.*` (business logic)
  - [ ] Use HTTP client for ALL data access

- [ ] **Independent configuration**
  - [ ] Create `AgentSettings` class with `AGENT_` prefix
  - [ ] Separate OpenAI keys and settings
  - [ ] Injectable backend API base URL

- [ ] **HTTP-only communication**
  - [ ] Create `RawDataClient` class using httpx
  - [ ] Include auth headers in all requests
  - [ ] Handle retries and timeouts

- [ ] **Testing isolation**
  - [ ] Unit tests mock all Raw Data API responses
  - [ ] Integration tests use actual HTTP calls
  - [ ] No database fixtures in Agent tests

---

## 📋 Phase 1: Enhance Data API Endpoints for Agent Use (Day 2-3)

> **ARCHITECTURE UPDATE**: Based on review feedback, we're enhancing existing data endpoints
> with agent-optimized parameters rather than having tool handlers apply business logic.
> 
> Enhanced endpoints at `/api/v1/data/*` will handle:
> - Symbol selection logic (top N by value/weight)
> - Token-aware response sizing
> - Pre-filtered, capped responses
> 
> Reference: TDD §7.0 for architectural decision, §7.1-7.6 for tool specifications

### 1.0 Enhanced Agent-Optimized Endpoints (Priority)
- [ ] **GET /api/v1/data/prices/historical/{portfolio_id}** - Add agent parameters
  - [ ] Add `max_symbols` parameter (default: 5, max: 5)
  - [ ] Add `selection_method` (top_by_value, top_by_weight, all)
  - [ ] Fetch portfolio positions internally when selection needed
  - [ ] Return max 5 symbols with price history
  - [ ] Include selection metadata in response
  - [ ] Token-aware response sizing (<2k tokens)

- [ ] **GET /api/v1/data/positions/top/{portfolio_id}** - New endpoint
  - [ ] Pre-filter to top 50 positions by value
  - [ ] Include aggregated statistics
  - [ ] Optimize response for LLM consumption

- [ ] **GET /api/v1/data/portfolio/{portfolio_id}/summary** - New endpoint
  - [ ] Condensed portfolio overview
  - [ ] Key metrics only
  - [ ] Designed for initial context setting

### 1.1 Existing Endpoints - Enhance with Parameters
- [x] **GET /api/v1/data/portfolio/{portfolio_id}/complete** 
  - ✅ Returns real portfolio data with positions
  - ✅ cash_balance calculated as 5% of portfolio
  - [ ] Add `as_of_date` parameter filtering
  - [ ] Add `include_positions` boolean parameter (default: true)
  - [ ] Add `include_cash` boolean parameter (default: true)
  - [ ] Enforce max_rows_positions=200 cap
  - [ ] Return proper meta object per agent spec

- [x] **GET /api/v1/data/portfolio/{portfolio_id}/data-quality**
  - ✅ Returns real data quality assessment
  - [ ] Add `check_factors` boolean parameter (default: true)
  - [ ] Add `check_correlations` boolean parameter (default: true)
  - [ ] Enhance feasibility flags for downstream analytics

### 1.2 Position Data Endpoints ✅ WORKING - Need Enhancements
- [x] **GET /api/v1/data/positions/details**
  - ✅ Returns real positions from database
  - [ ] Add support for position_ids comma-separated list (currently portfolio_id only)
  - [ ] Add `include_closed` boolean parameter (default: false)
  - [ ] Enforce max_rows=200 cap with truncation metadata
  - [ ] Add summary block to response
  - [ ] Return meta object with truncation info

### 1.3 Price Data Endpoints ✅ WORKING - Need Enhancements
- [x] **GET /api/v1/data/prices/historical/{portfolio_id}**
  - ✅ Returns 292 days of real OHLCV data from MarketDataCache
  - [ ] Add `lookback_days` parameter with max=180 enforcement
  - [ ] Add `include_factor_etfs` boolean parameter (default: true)
  - [ ] Add `date_format` parameter (iso/unix, default: iso)
  - [ ] Return meta object with applied limits

- [x] **GET /api/v1/data/prices/quotes**
  - ✅ Returns real-time quotes with volume
  - [ ] Add max_symbols=5 cap enforcement
  - [ ] Add `include_options` boolean parameter (default: false)
  - [ ] Handle invalid symbols gracefully
  - [ ] Add 60-second cache TTL

### 1.4 Factor Data Endpoints ✅ WORKING - Need Enhancements
- [x] **GET /api/v1/data/factors/etf-prices**
  - ✅ All 7 ETFs return real market prices
  - [ ] Add `lookback_days` parameter (default: 150)
  - [ ] Add `factors` parameter for filtering (comma-separated)
  - [ ] Map factor names to ETF symbols (e.g., "market" → "SPY")
  - [ ] Return meta object with resolved symbols

### 1.5 Testing & Validation
- [x] **Test scripts already exist**
  - ✅ `scripts/verify_mock_vs_real_data.py` - Confirms all return real data
  - ✅ `scripts/check_etf_mapping.py` - Verifies ETF data
  - ✅ `scripts/test_historical_prices.py` - Validates price data
  - [ ] Add tests for new parameters
  - [ ] Verify meta object format
  - [ ] Test truncation behavior

---

## 📋 Phase 2: Backend Chat Infrastructure (Day 4-6)

> Reference: TDD §5 (Chat Endpoints), §8 (SSE Protocol), §18.1 (Auth), §18.4 (API Structure)

### 2.1 Create Chat Module Structure
- [ ] **Create backend/app/api/v1/chat/ module** (ref: TDD §3 for structure)
  ```
  backend/app/api/v1/chat/
  ├── __init__.py
  ├── router.py           # FastAPI router setup (prefix /api/v1/chat)
  ├── conversations.py    # Conversation management
  ├── send.py            # SSE streaming endpoint
  ├── tools.py           # Tool handler implementations (registry + stubs)
  └── schemas.py         # Pydantic models
  ```

- [ ] **Register chat router in main API**
  - [ ] Import chat.router in `backend/app/api/v1/router.py`
  - [ ] Add `router.include_router(chat.router, prefix="/chat", tags=["chat"])`

### 2.2 Implement Conversation Management
- [ ] **POST /chat/conversations endpoint** (ref: TDD §5.1, PRD §7.1)
  - [x] ✅ Dual auth support already implemented in backend:
    - [x] Bearer token via HTTPBearer works
    - [x] JWT from HTTP-only cookie works
    - [x] Can use existing `get_current_user` dependency
  - [ ] Insert conversation row in database with our UUID as id
  - [ ] Return our UUID as conversation_id (canonical ID for frontend)
  - [ ] Store provider_thread_id if OpenAI creates one (optional)
  - [ ] Set provider = "openai", mode = "green" (default)
  - [ ] Response includes conversation_id and provider_thread_id in meta if created

- [ ] **Conversation schemas**
  ```python
  class ConversationCreate(BaseSchema):
      mode: Optional[str] = "green"  # green|blue|indigo|violet
  
  class ConversationResponse(BaseSchema):
      conversation_id: str
      mode: str
      created_at: datetime
  ```

### 2.3 Implement SSE Streaming Endpoint
- [ ] **POST /chat/send (SSE)** (ref: TDD §5.2, §8 for SSE protocol, PRD §4.3)
  - [ ] Implement dual auth for SSE:
    - [ ] Primary: JWT from HTTP-only cookie (best for SSE)
    - [ ] Fallback: Bearer token via query param if needed
  - [ ] Load conversation and mode from DB
  - [ ] Set up SSE response headers (text/event-stream)
  - [ ] Implement heartbeat mechanism (every 15s) - send ":\n"
  - [ ] Stream OpenAI responses
  - [ ] Wire error handling (rate limit, auth errors as SSE events)

- [ ] **SSE Event Types**
  ```python
  class SSEEvent:
      START = "start"
      MESSAGE = "message"  # default
      TOOL_CALL = "tool_call"
      TOOL_RESULT = "tool_result"
      ERROR = "error"
      DONE = "done"
  ```

- [ ] **Request/Response schemas**
  ```python
  class ChatSendRequest(BaseSchema):
      conversation_id: str
      text: str
      
  # Mode switching detection in handler:
  # if text.startswith("/mode "):
  #     new_mode = text[6:].strip()  # green|blue|indigo|violet
  #     update conversation.mode in DB
  #     return SSE event confirming mode change
  
  class SSEMessageEvent(BaseSchema):
      delta: str
  
  class SSEToolCallEvent(BaseSchema):
      name: str
      args: Dict[str, Any]
  
  class SSEToolResultEvent(BaseSchema):
      name: str
      meta: Dict[str, Any]
      preview: Optional[Dict[str, Any]]
  ```

### 2.4 OpenAI Integration
- [ ] **Create OpenAI service module**
  ```python
  backend/app/services/openai_service.py
  ```
  - [ ] Initialize OpenAI client with API key
  - [ ] Implement conversation creation
  - [ ] Implement message sending with streaming
  - [ ] Handle tool calls
  - [ ] Enable Code Interpreter

- [ ] **Error handling**
  - [ ] Rate limit handling with retry
  - [ ] Token limit management (GPT-5 has higher limits)
  - [ ] Connection error recovery
  - [ ] Graceful degradation
  - [ ] Handle GPT-5 specific response formats

---

## 📋 Phase 3: Tool Handlers Implementation (Day 6-8)

> Reference: TDD §7 (Tool Specifications), PRD §6 (Tool Schemas), TDD §7.A (Common Response Format)

### 3.1 Create Tool Registry
- [ ] **backend/app/api/v1/chat/tools.py**
  - [ ] Define tool schemas (OpenAI function format)
  - [ ] Create tool handler mapping
  - [ ] Implement parameter validation
  - [ ] Add response formatting

### 3.2 Implement Tool Handlers

- [ ] **get_portfolio_complete** (ref: TDD §7.1, PRD §6.1)
  ```python
  async def get_portfolio_complete(
      portfolio_id: str,
      include_positions: bool = True,
      include_cash: bool = True,
      as_of_date: Optional[str] = None
  ) -> Dict[str, Any]:
      # Call /api/v1/data/portfolio/{portfolio_id}/complete
      # Enforce max_rows_positions=200
      # Return standardized response with meta
  ```

- [ ] **get_portfolio_data_quality**
  ```python
  async def get_portfolio_data_quality(
      portfolio_id: str,
      check_factors: bool = True,
      check_correlations: bool = True
  ) -> Dict[str, Any]:
      # Call /api/v1/data/portfolio/{portfolio_id}/data-quality
      # Return feasibility assessment
  ```

- [ ] **get_positions_details**
  ```python
  async def get_positions_details(
      portfolio_id: Optional[str] = None,
      position_ids: Optional[str] = None,
      include_closed: bool = False
  ) -> Dict[str, Any]:
      # Validate: portfolio_id OR position_ids required
      # Call /api/v1/data/positions/details
      # Enforce max_rows=200 with truncation
  ```

- [ ] **get_prices_historical**
  ```python
  async def get_prices_historical(
      portfolio_id: str,
      lookback_days: int = 150,
      include_factor_etfs: bool = True,
      date_format: str = "iso"
  ) -> Dict[str, Any]:
      # Special handling: fetch positions first
      # Identify top 5 symbols by market value
      # Call /api/v1/data/prices/historical/{portfolio_id}
      # Post-process to filter symbols
      # Set truncated=true if filtering occurred
  ```

- [ ] **get_current_quotes**
  ```python
  async def get_current_quotes(
      symbols: str,
      include_options: bool = False
  ) -> Dict[str, Any]:
      # Parse comma-separated symbols
      # Enforce max_symbols=5
      # Call /api/v1/data/prices/quotes
  ```

- [ ] **get_factor_etf_prices**
  ```python
  async def get_factor_etf_prices(
      lookback_days: int = 150,
      factors: Optional[str] = None
  ) -> Dict[str, Any]:
      # Map factor names to ETF symbols
      # Call /api/v1/data/factors/etf-prices
      # Include resolved symbols in meta.applied
  ```

### 3.3 Tool Response Standardization
- [ ] **Implement common response envelope**
  ```python
  def format_tool_response(
      data: Any,
      requested_params: Dict,
      applied_params: Dict,
      limits: Dict,
      rows_returned: int,
      truncated: bool = False,
      suggested_params: Optional[Dict] = None
  ) -> Dict[str, Any]:
      return {
          "meta": {
              "as_of": utc_now().isoformat() + "Z",
              "requested": requested_params,
              "applied": applied_params,
              "limits": limits,
              "rows_returned": rows_returned,
              "truncated": truncated,
              "suggested_params": suggested_params
          },
          "data": data
      }
  ```

- [ ] **Implement error response format**
  ```python
  def format_tool_error(
      message: str,
      retryable: bool = True,
      suggested_params: Optional[Dict] = None,
      request_id: Optional[str] = None
  ) -> Dict[str, Any]:
      return {
          "error": {
              "message": message,
              "retryable": retryable,
              "suggested_params": suggested_params,
              "request_id": request_id or str(uuid4())
          }
      }
  ```

---

## 📋 Phase 4: Prompt Engineering (Day 8-9)

> Reference: TDD §9 (Prompt Library), PRD §5 (Prompt Modes)

### 4.1 Create Prompt Templates
- [ ] **agent/agent_pkg/prompts/**
  ```
  agent/agent_pkg/prompts/
  ├── green_v001.md       # Teaching-focused (default)
  ├── blue_v001.md        # Concise/quantitative
  ├── indigo_v001.md      # Strategic/narrative
  ├── violet_v001.md      # Risk-focused
  └── common_instructions.md
  ```

### 4.2 Green Mode
- [ ] **Create green_v001.md**
  ```yaml
  ---
  id: green
  version: v001
  mode: Green
  persona: Teaching-focused financial analyst
  token_budget: 2000
  ---
  
  # System Instructions
  - Educational, step-by-step explanations
  - Define financial terms for beginners
  - Use analogies and examples
  - Verbose but clear communication
  - Include "as of" timestamps
  ```

### 4.3 Blue Mode
- [ ] **Create blue_v001.md**
  ```yaml
  ---
  id: blue
  version: v001
  mode: Blue
  persona: Quantitative analyst
  token_budget: 1500
  ---
  
  # System Instructions
  - Concise, data-forward responses
  - Tables and numbers over prose
  - Assume professional audience
  - Technical terminology OK
  - Minimal explanations
  ```

### 4.4 Indigo Mode
- [ ] **Create indigo_v001.md**
  ```yaml
  ---
  id: indigo
  version: v001
  mode: Indigo
  persona: Strategic investment analyst
  token_budget: 1800
  ---
  
  # System Instructions
  - Focus on market context and trends
  - Narrative style with forward insights
  - Connect portfolio to macro themes
  - Scenario analysis and implications
  - Strategic recommendations
  ```

### 4.5 Violet Mode
- [ ] **Create violet_v001.md**
  ```yaml
  ---
  id: violet
  version: v001
  mode: Violet
  persona: Conservative risk analyst
  token_budget: 1700
  ---
  
  # System Instructions
  - Emphasize risks and stress scenarios
  - Conservative, cautious tone
  - Include compliance disclaimers
  - Focus on capital preservation
  - Highlight concentration risks
  ```

### 4.6 Prompt Loading System
- [ ] **Implement prompt loader**
  ```python
  class PromptManager:
      def load_prompt(mode: str) -> str
      def get_system_prompt(mode: str, user_context: Dict) -> str
      def inject_variables(prompt: str, variables: Dict) -> str
  ```

---

## 📋 Phase 5: Testing & Validation (Day 9-10)

> Reference: TDD §14 (Testing), PRD §9 (Performance Targets), §13 (Golden Set)

### 5.1 Unit Tests
- [ ] **Test conversation management**
  - [ ] Conversation creation
  - [ ] Mode switching
  - [ ] Database persistence

- [ ] **Test tool handlers**
  - [ ] Each tool with valid params
  - [ ] Cap enforcement
  - [ ] Truncation behavior
  - [ ] Error handling

- [ ] **Test SSE streaming**
  - [ ] Connection establishment
  - [ ] Event formatting
  - [ ] Heartbeat mechanism
  - [ ] Error recovery

### 5.2 Integration Tests
- [ ] **End-to-end chat flow**
  - [ ] Login → Create conversation → Send message
  - [ ] Tool execution → Response streaming
  - [ ] Code Interpreter execution

- [ ] **Golden Test Suite (15 queries)** (ref: PRD §13 for test cases)
  1. [ ] "What's my 30-day P&L?"
  2. [ ] "Show my biggest positions"
  3. [ ] "What's my delta exposure?"
  4. [ ] "Which positions expire this week?"
  5. [ ] "Calculate my portfolio beta"
  6. [ ] "Show factor exposures"
  7. [ ] "What's my cash balance?"
  8. [ ] "Compare this week vs last week performance"
  9. [ ] "Show me AAPL historical prices"
  10. [ ] "What's my portfolio value?"
  11. [ ] "Calculate position-level returns"
  12. [ ] "Show correlation matrix"
  13. [ ] "What's my largest loss today?"
  14. [ ] "Show options positions only"
  15. [ ] "Calculate Sharpe ratio"

### 5.3 Performance Testing
- [ ] **Latency measurements** (ref: TDD §12, PRD §3 Success Metrics)
  - [ ] Stream start ≤ 3s p50
  - [ ] Complete response ≤ 8-10s p95
  - [ ] Tool execution ≤ 5-6s p95

- [ ] **Load testing**
  - [ ] Concurrent conversations
  - [ ] Rate limit validation
  - [ ] Cache effectiveness

---

## 📋 Phase 6: Telemetry & Monitoring (Day 10-11)

### 6.1 Logging Implementation
- [ ] **Structured logging**
  ```python
  logger.info("conversation_started", extra={
      "conversation_id": conv_id,
      "user_id": user_id,
      "mode": mode
  })
  ```

- [ ] **Log points**
  - [ ] Conversation creation
  - [ ] Message received
  - [ ] Tool execution start/end
  - [ ] OpenAI API calls
  - [ ] Errors and retries

### 6.2 Metrics Collection
- [ ] **Per-conversation metrics**
  - [ ] Total messages
  - [ ] Tool calls count
  - [ ] Token usage
  - [ ] Total latency
  - [ ] Error rate

- [ ] **Aggregate metrics**
  - [ ] Daily active conversations
  - [ ] Most used tools
  - [ ] Average tokens per conversation
  - [ ] Success rate by query type

### 6.3 Error Tracking
- [ ] **Error categorization**
  - [ ] OpenAI API errors
  - [ ] Tool execution failures
  - [ ] Data availability issues
  - [ ] Token limit exceeded

---

## 📋 Phase 7: Documentation (Day 11-12)

### 7.1 API Documentation
- [ ] **Document chat endpoints**
  - [ ] OpenAPI/Swagger specs
  - [ ] Request/response examples
  - [ ] Error codes

- [ ] **Tool documentation**
  - [ ] Available tools list
  - [ ] Parameter descriptions
  - [ ] Response formats
  - [ ] Limitations and caps

### 7.2 Development Guide
- [ ] **Agent development guide**
  - [ ] Architecture overview
  - [ ] Adding new tools
  - [ ] Prompt engineering tips
  - [ ] Testing strategies

### 7.3 Deployment Guide
- [ ] **Deployment instructions**
  - [ ] Environment variables
  - [ ] Database setup
  - [ ] OpenAI configuration
  - [ ] Monitoring setup

---

## 📋 Phase 8: Deployment Preparation (Day 12-14)

### 8.1 Environment Configuration
- [ ] **Production environment variables**
  - [ ] Secure OpenAI API key storage
  - [ ] Production database credentials
  - [ ] Cache configuration
  - [ ] Rate limit settings

### 8.2 Security Review
- [ ] **Security checklist**
  - [ ] API key rotation plan
  - [ ] JWT validation
  - [ ] Rate limiting
  - [ ] Input sanitization
  - [ ] PII handling

### 8.3 Performance Optimization
- [ ] **Caching strategy**
  - [ ] Tool response caching
  - [ ] Prompt template caching
  - [ ] Conversation context caching

- [ ] **Database optimization**
  - [ ] Query optimization
  - [ ] Connection pooling
  - [ ] Index verification

---

## 🚀 Success Criteria

> Reference: PRD §3 (Success Metrics), TDD §12 (Performance Limits)

### Technical Requirements
- [ ] ✅ All Raw Data APIs return real data
- [ ] ✅ Chat endpoints fully functional
- [ ] ✅ SSE streaming working smoothly
- [ ] ✅ Tool execution with proper caps
- [ ] ✅ Code Interpreter integration
- [ ] ✅ Both analyst modes working
- [ ] ✅ UTC ISO 8601 timestamps everywhere

### Performance Targets
- [ ] ✅ Stream start ≤ 3s p50
- [ ] ✅ Complete response ≤ 8-10s p95
- [ ] ✅ Tool execution ≤ 5-6s p95
- [ ] ✅ 80% pass rate on golden queries

### Quality Metrics
- [ ] ✅ No hallucinated tickers/values
- [ ] ✅ Accurate calculations via Code Interpreter
- [ ] ✅ Proper error handling with suggestions
- [ ] ✅ 70% Good/Excellent usefulness rating

---

## 📝 Notes

1. **Critical Path**: Raw Data APIs → Chat Infrastructure → Tool Handlers → Testing
2. **Blocking Issues**: Must fix GPT-5 references and complete Raw Data APIs first
3. **Dependencies**: Requires OpenAI API key and properly configured backend
4. **Risk Areas**: Historical prices symbol filtering complexity, SSE connection stability
5. **Quick Wins**: UTC standardization already complete, some APIs already return real data

---

## 🔄 Daily Standup Checklist

- [ ] Update completion percentages
- [ ] Flag any blockers
- [ ] Note any scope changes
- [ ] Update time estimates
- [ ] Document decisions made
- [ ] Plan next day's priorities

---

**Last Updated:** 2025-08-27  
**Next Review:** Daily during implementation
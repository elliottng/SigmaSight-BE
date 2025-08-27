# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SigmaSight Agent - A backend chat API that connects OpenAI GPT-5 with portfolio analysis tools via SSE streaming. The agent answers portfolio questions using function calling to Raw Data APIs and Code Interpreter for calculations.

**Current Status**: Planning phase - backend chat infrastructure not yet implemented.

## Architecture

### High-Level Design
```
User → POST /chat/send → Backend Agent → OpenAI GPT-5 → Tools → Raw Data APIs
                              ↓
                        SSE Stream Response
```

The agent is a **backend-only** service that:
1. Receives chat messages via REST API
2. Authenticates using JWT Bearer tokens (from main backend)
3. Calls OpenAI with function tools mapped to Raw Data endpoints
4. Streams responses back via Server-Sent Events (SSE)

### Key Architectural Decisions
- **Vendor-agnostic conversation IDs**: Use our UUID as primary key, store provider IDs as metadata
- **No pagination**: Hard caps on tool responses (5 symbols, 180 days, 200 positions)
- **SSE streaming**: Not WebSockets, use text/event-stream with heartbeats
- **Backend-only OpenAI**: Never expose API keys to frontend
- **UTC ISO 8601**: All timestamps use Z suffix format

## Development Commands

### Backend Integration
```bash
# The agent runs as part of the main backend
cd ../backend
uv run python run.py              # Start development server with agent endpoints

# Database migrations for conversation tables
cd ../backend
uv run alembic revision --autogenerate -m "Add conversation tables for agent"
uv run alembic upgrade head

# Run tests (when implemented)
cd ../backend
uv run pytest tests/test_agent/
```

### Environment Setup
Required in backend/.env:
```
OPENAI_API_KEY=sk-...
MODEL_DEFAULT=gpt-5
MODEL_FALLBACK=gpt-5-mini
SSE_HEARTBEAT_INTERVAL_MS=15000
AGENT_CACHE_TTL=600
```

## File Structure & Implementation Path

### Phase 0: Prerequisites (Current)
1. Update `backend/app/config.py` with OpenAI settings
2. Create conversation models in `backend/app/models/conversations.py`
3. Run Alembic migration

### Phase 1: Chat Module
Create in `backend/app/api/v1/chat/`:
- `router.py` - FastAPI router registration
- `conversations.py` - POST /chat/conversations endpoint
- `send.py` - POST /chat/send SSE endpoint
- `tools.py` - Tool handler implementations
- `schemas.py` - Pydantic models

### Phase 2: Tool Handlers
Map 6 Raw Data endpoints to OpenAI function tools:
- `get_portfolio_complete` → `/api/v1/data/portfolio/{id}/complete`
- `get_portfolio_data_quality` → `/api/v1/data/portfolio/{id}/data-quality`
- `get_positions_details` → `/api/v1/data/positions/details`
- `get_prices_historical` → `/api/v1/data/prices/historical/{id}`
- `get_current_quotes` → `/api/v1/data/prices/quotes`
- `get_factor_etf_prices` → `/api/v1/data/factors/etf-prices`

### Phase 3: Prompts
Create in `agent/agent_pkg/prompts/`:
- `analyst_blue_v001.md` - Concise, quantitative mode
- `analyst_green_v001.md` - Educational, explanatory mode

## Critical Context

### What Already Exists (Don't Rebuild)
- **Authentication**: JWT Bearer tokens in `backend/app/core/dependencies.py`
- **Database patterns**: Async SQLAlchemy in `backend/app/database.py`
- **Raw Data APIs**: 100% working with real data (need parameter enhancements)
- **UTC datetime**: Already standardized with utilities in `backend/app/core/datetime_utils.py`

### What Needs Building
- Chat endpoints (`/chat/conversations`, `/chat/send`)
- SSE streaming implementation
- Tool handler wrappers with caps/truncation
- OpenAI integration
- Conversation state management

## Key Documents

### Requirements
- `TODO.md` - Comprehensive implementation plan with phases
- `_docs/requirements/PRD_AGENT_V1.0.md` - Product requirements
- `_docs/requirements/DESIGN_DOC_AGENT_V1.0.md` - Technical design (Section 18 has existing infrastructure)

### Backend Context
- `../backend/API_IMPLEMENTATION_STATUS.md` - Raw Data APIs are 100% complete
- `../backend/AI_AGENT_REFERENCE.md` - Backend patterns and common issues
- `../backend/TODO3.md` - Backend Phase 3 completion status

## Success Metrics
- Stream start ≤ 3s p50
- Complete response ≤ 8-10s p95
- 80% pass rate on 15 golden queries
- No hallucinated values

## Common Gotchas
1. **Auth uses dual support**: Both Bearer tokens (existing) AND cookies (for SSE). Login endpoint sets both
2. **Models need registration**: Add conversation models to `backend/app/database.py` init_db()
3. **Use pydantic_settings pattern**: Settings fields need `Field(..., env="VAR_NAME")`
4. **Raw Data APIs need enhancements**: Add caps, meta objects, parameter validation
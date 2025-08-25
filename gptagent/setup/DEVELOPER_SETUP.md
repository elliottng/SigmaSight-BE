# SigmaSight GPT Agent - Developer Setup Guide

**Date:** 2025-08-25  
**Version:** 2.0  
**Updated:** Added working ChatGPT integration configuration

## Overview

This guide helps developers set up the SigmaSight GPT Agent system that integrates with the existing SigmaSight backend application. The system includes both the original GPT agent service and a working direct ChatGPT integration implemented through the frontend.

## Current Working Configuration

⚠️ **IMPORTANT**: The fastest way to get GPT chat functionality working is through the direct ChatGPT integration, not the GPT agent service.

### Quick Start - Working ChatGPT Integration

**Step 1: Start Backend**
```bash
cd backend && uv run python run.py  # Port 8000
```

**Step 2: Start Frontend with ChatGPT Integration**
```bash
cd frontend 
export OPENAI_API_KEY="your-openai-api-key-here"
export PORT=4003
npm install && npm run dev
```

**Step 3: Access Chat Interface**
- Navigate to `http://localhost:4003/chat`
- Test with portfolio questions like "What's my portfolio risk?"
- Real portfolio data will be analyzed by GPT-4o-mini

### Working Configuration Details

**Architecture:**
- **Backend**: Port 8000 (existing SigmaSight backend)
- **Frontend**: Port 4003 (Next.js with direct OpenAI integration)
- **No GPT Agent Service**: Bypassed due to technical issues

**Key Files:**
- `frontend/pages/chat.tsx` - Chat interface
- `frontend/pages/api/gpt/analyze.ts` - Direct OpenAI integration with portfolio data
- Portfolio data fetched from: `http://localhost:8000/api/v1/reports/portfolio/{id}/content/json`

## Alternative: GPT Agent Service Setup

The original GPT agent service is preserved but currently has technical issues. Use this setup if you want to work on the service-based architecture:

## Prerequisites

### Required Software
- **Node.js** 18+ (for GPT agent)
- **pnpm** (package manager for workspace)
- **Python 3.10+** (for backend integration)
- **PostgreSQL** (shared database with backend)
- **Git** (version control)

### Required API Keys
- **OpenAI API Key** (for gpt-4o-mini model) - Format: `sk-proj-...`
- **SigmaSight Backend Access** (same API keys as backend)

### Backend Dependencies
⚠️ **CRITICAL**: The GPT agent requires the SigmaSight backend to be running

The backend provides:
- Database with portfolio and position data
- Pre-calculated analytics (Greeks, VaR, factor exposures)
- Authentication and authorization
- Market data integration

## Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd SigmaSight/gptagent
```

### 2. Install Dependencies
```bash
# Install all workspace dependencies
pnpm install

# Verify installation
pnpm run --help
```

### 3. Environment Configuration
Create `apps/api/.env` based on `.env.example`:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-5-thinking
OPENAI_TEMPERATURE=0

# Backend Integration  
BACKEND_API_URL=http://localhost:8000/api/v1
BACKEND_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/sigmasight

# Authentication (same as backend)
JWT_SECRET=your-jwt-secret-here
JWT_ALGORITHM=HS256

# Optional: Market Data APIs (inherit from backend)
POLYGON_API_KEY=your-polygon-key
FMP_API_KEY=your-fmp-key
FRED_API_KEY=your-fred-key
```

### 4. Backend Integration Setup

**Step 4.1: Start Backend Services**
```bash
# In separate terminal, navigate to backend
cd ../backend

# Start PostgreSQL
docker-compose up -d

# Start backend API server
uv run python run.py
```

**Step 4.2: Verify Backend Connection**
```bash
# Test backend API is running
curl http://localhost:8000/api/v1/reports/health

# Should return: {"status": "healthy", ...}
```

**Step 4.3: Verify Demo Data**
```bash
# In backend directory, verify demo portfolios exist
uv run python scripts/verify_demo_portfolios.py
```

### 5. Build and Start GPT Agent

```bash
# Build all packages
pnpm -w run build

# Start development server
pnpm -w run dev
```

The GPT agent API will be available at `http://localhost:8787`

### 6. Integration Testing

**Test Backend Connectivity:**
```bash
# Test GPT agent can reach backend
curl http://localhost:8787/tools/portfolio_snapshot?portfolio_id=a3209353-9ed5-4885-81e8-d4bbc995f96c

# Test analysis endpoint
curl -X POST http://localhost:8787/analyze \
  -H "Content-Type: application/json" \
  -d '{"portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"}'
```

## Development Workflow

### Project Structure
```
gptagent/
├── apps/api/              # Fastify API server
│   ├── src/
│   │   ├── index.ts       # Main server
│   │   └── routes/
│   │       ├── analyze.ts # GPT analysis endpoint
│   │       └── tools.ts   # Backend integration tools
│   └── .env              # Environment variables
├── packages/
│   ├── analysis-agent/    # GPT system prompt & logic
│   ├── schemas/          # Zod validation schemas
│   └── utils/            # Shared utilities
├── prompts/              # GPT prompt specifications
├── docs/                 # Implementation documentation
└── setup/               # This setup guide
```

### Backend Integration Points

**Database Models** (inherit from backend):
- `PortfolioSnapshot` - Daily portfolio metrics
- `Position` - Individual positions with Greeks  
- `PortfolioReport` - Generated analysis reports
- `User/Portfolio` - Authentication and ownership

**API Endpoints** (backend services):
- `/api/v1/reports/` - Portfolio reports  
- `/api/v1/portfolio/` - Portfolio data
- `/api/v1/positions/` - Position details
- `/api/v1/risk/` - Risk calculations

### Tool Development Pattern

Each GPT tool follows this pattern:
```typescript
// apps/api/src/routes/tools.ts
export async function get_portfolio_snapshot(portfolio_id: string, as_of?: string) {
  // 1. Validate inputs with Zod schema
  const input = portfolioSnapshotInputSchema.parse({ portfolio_id, as_of });
  
  // 2. Call backend API or database
  const response = await fetch(`${BACKEND_URL}/portfolio/${portfolio_id}/snapshot`);
  const data = await response.json();
  
  // 3. Validate outputs with Zod schema  
  const validated = portfolioSnapshotOutputSchema.parse(data);
  
  // 4. Return structured data for GPT
  return validated;
}
```

### Schema Development

Schemas must match backend SQLAlchemy models:

```typescript
// packages/schemas/src/index.ts
import { z } from 'zod';

// Matches backend/app/models/snapshots.py:PortfolioSnapshot
export const portfolioSnapshotSchema = z.object({
  portfolio_id: z.string().uuid(),
  snapshot_date: z.string().date(), 
  total_value: z.number(),
  gross_exposure: z.number(),
  net_exposure: z.number(),
  portfolio_delta: z.number().nullable(),
  portfolio_gamma: z.number().nullable(),
  // ... other fields from backend model
});
```

## Testing

### Unit Tests
```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test packages/utils/test/concentration.test.ts

# Watch mode for development
pnpm test --watch
```

### Integration Tests
```bash
# Test with backend integration
pnpm test:integration

# Test specific tool
pnpm test tools/portfolio_snapshot
```

### Demo Data Testing

**Available Demo Portfolios:**
- **Individual Investor**: `a3209353-9ed5-4885-81e8-d4bbc995f96c`
- **High Net Worth**: `14e7f420-b096-4e2e-8cc2-531caf434c05`  
- **Hedge Fund Style**: `cf890da7-7b74-4cb4-acba-2205fdd9dff4`

**Test Analysis:**
```bash
curl -X POST http://localhost:8787/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
    "analysis_type": "comprehensive"
  }'
```

## Common Issues & Solutions

### Backend Connection Issues

**Issue**: `ECONNREFUSED` when calling backend
```bash
# Solution: Verify backend is running
curl http://localhost:8000/health

# If not running, start backend:
cd ../backend && uv run python run.py
```

**Issue**: Database connection errors
```bash
# Solution: Verify PostgreSQL is running
docker ps | grep postgres

# If not running:
cd ../backend && docker-compose up -d
```

### Authentication Issues

**Issue**: `401 Unauthorized` from backend APIs
```bash
# Solution: Verify JWT secret matches backend
# Check backend/.env and gptagent/apps/api/.env
# Ensure JWT_SECRET is identical
```

### Schema Validation Errors

**Issue**: Zod validation failures
```bash
# Solution: Compare schemas with backend models
# 1. Check backend/app/models/*.py for field definitions
# 2. Update packages/schemas/src/index.ts to match
# 3. Ensure data type mappings: Decimal→number, UUID→string
```

### Performance Issues

**Issue**: Slow response times (>3s)
```bash
# Solutions:
# 1. Verify backend database queries are optimized
# 2. Check for missing database indexes
# 3. Monitor backend batch processing status
# 4. Use cached data when available
```

## Development Best Practices

### 1. Backend-First Development
- Always verify backend data availability before implementing GPT tools
- Use existing demo data for testing, don't create new test portfolios
- Respect backend calculation engine results, never recompute

### 2. Error Handling
- Handle missing backend data gracefully (gap detection)
- Follow backend's async/await patterns
- Implement retry logic for transient backend failures

### 3. Schema Synchronization  
- Keep Zod schemas aligned with backend SQLAlchemy models
- Update schemas when backend models change
- Validate both inputs and outputs rigorously

### 4. Testing Strategy
- Test with real backend data, not mocks
- Verify end-to-end integration regularly
- Use backend's existing demo portfolios for consistent testing

## Documentation Updates

When making changes:
1. Update `docs/IMPLEMENTATION_ACTIONS.md` with progress
2. Document new patterns in backend integration  
3. Update schema mappings when backend models change
4. Keep this setup guide current with new requirements

## Support & Troubleshooting

### Log Locations
- **GPT Agent Logs**: Console output from `pnpm -w run dev`
- **Backend Logs**: `../backend/logs/sigmasight.log`
- **Database Logs**: Docker logs for PostgreSQL container

### Diagnostic Commands
```bash
# Check GPT agent health
curl http://localhost:8787/health

# Check backend health  
curl http://localhost:8000/health

# Verify database connectivity
cd ../backend && uv run python scripts/check_database_content.py

# Test specific tool
curl "http://localhost:8787/tools/portfolio_snapshot?portfolio_id=a3209353-9ed5-4885-81e8-d4bbc995f96c"
```

### Getting Help
- Review `docs/IMPLEMENTATION_ACTIONS.md` for current status
- Check backend documentation in `../backend/AI_AGENT_REFERENCE.md`
- Verify backend setup using `../backend/CLAUDE.md` guide

---

**Next Steps**: After setup, see `docs/IMPLEMENTATION_ACTIONS.md` for implementation progress and next development tasks.
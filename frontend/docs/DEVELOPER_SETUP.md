# SigmaSight Frontend Developer Setup Guide

**Date:** 2025-08-25  
**Prerequisites:** Backend & GPT Agent Integration  

## Overview

This guide helps developers set up the SigmaSight frontend that integrates with the **existing backend system** and **GPT agent**. The frontend consumes data from backend database models and leverages the GPT agent for AI-powered portfolio insights.

⚠️ **CRITICAL**: The frontend requires both the SigmaSight backend AND GPT agent to be running.

## System Dependencies

### Required Services
1. **SigmaSight Backend** (FastAPI + PostgreSQL + Batch Processing)
2. **GPT Agent** (Node.js + OpenAI integration)  
3. **Frontend** (Next.js + TypeScript)

### Software Requirements
- **Node.js 18+** (for frontend and GPT agent)
- **pnpm** (for GPT agent workspace)
- **Python 3.10+** (for backend)
- **PostgreSQL** (shared database)
- **Git** (version control)

## Backend System Setup

### Step 1: Start Backend Services
```bash
# Navigate to backend directory
cd ../backend

# Start PostgreSQL
docker-compose up -d

# Verify database is running
docker ps | grep postgres

# Start backend API server
uv run python run.py

# Verify backend is healthy (separate terminal)
curl http://localhost:8000/health
```

### Step 2: Verify Demo Data
```bash
# In backend directory, verify demo portfolios exist
uv run python scripts/verify_demo_portfolios.py

# Should show 3 demo portfolios:
# - Individual Investor: a3209353-9ed5-4885-81e8-d4bbc995f96c
# - High Net Worth: 14e7f420-b096-4e2e-8cc2-531caf434c05  
# - Hedge Fund Style: cf890da7-7b74-4cb4-acba-2205fdd9dff4
```

### Step 3: Test Backend API Endpoints
```bash
# Test portfolio reports endpoint
curl http://localhost:8000/api/v1/reports/portfolios

# Test specific portfolio report
curl http://localhost:8000/api/v1/reports/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/content/json
```

## GPT Agent Setup

### Step 1: Configure GPT Agent
```bash
# Navigate to GPT agent directory
cd ../gptagent

# Install dependencies
pnpm install

# Verify installation
pnpm run --help
```

### Step 2: Environment Configuration
Create `gptagent/apps/api/.env`:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-5-thinking
OPENAI_TEMPERATURE=0

# Backend Integration (CRITICAL)
BACKEND_API_URL=http://localhost:8000/api/v1
BACKEND_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/sigmasight

# Authentication (must match backend)
JWT_SECRET=same-secret-as-backend
JWT_ALGORITHM=HS256
```

### Step 3: Start GPT Agent
```bash
# Build all packages
pnpm -w run build

# Start development server
pnpm -w run dev

# Verify GPT agent is running (separate terminal)
curl http://localhost:8787/health
```

### Step 4: Test GPT Agent Integration
```bash
# Test GPT agent can call backend tools
curl -X POST http://localhost:8787/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show portfolio summary",
    "context": {
      "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
    }
  }'

# Should return structured analysis with backend data
```

## Frontend Setup

### Step 1: Initialize Frontend Project
```bash
# Navigate to frontend directory  
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run --help
```

### Step 2: Environment Configuration
Create `frontend/.env.local`:
```env
# Backend Integration
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000/api/v1
BACKEND_API_URL=http://localhost:8000/api/v1

# GPT Agent Integration
NEXT_PUBLIC_GPT_AGENT_URL=http://localhost:8787
GPT_AGENT_URL=http://localhost:8787

# Authentication (must match backend & GPT agent)
NEXTAUTH_SECRET=your-nextauth-secret
JWT_SECRET=same-secret-as-backend

# Demo Portfolio IDs (from backend)
NEXT_PUBLIC_DEMO_INDIVIDUAL_PORTFOLIO=a3209353-9ed5-4885-81e8-d4bbc995f96c
NEXT_PUBLIC_DEMO_HIGH_NET_WORTH_PORTFOLIO=14e7f420-b096-4e2e-8cc2-531caf434c05
NEXT_PUBLIC_DEMO_HEDGE_FUND_PORTFOLIO=cf890da7-7b74-4cb4-acba-2205fdd9dff4

# Feature Flags
NEXT_PUBLIC_ENABLE_GPT_FEATURES=true
NEXT_PUBLIC_ENABLE_BACKEND_INTEGRATION=true
```

### Step 3: Start Frontend Development
```bash
# Start Next.js development server
npm run dev

# Verify frontend is running
curl http://localhost:3000/api/health
```

## Full System Integration Test

### Step 1: Verify All Services
```bash
# Check all services are running (in separate terminals)

# Terminal 1: Backend
cd backend && uv run python run.py
# Should show: "Server running on http://localhost:8000"

# Terminal 2: GPT Agent  
cd gptagent && pnpm -w run dev
# Should show: "Server running on http://localhost:8787"

# Terminal 3: Frontend
cd frontend && npm run dev
# Should show: "Ready on http://localhost:3000"
```

### Step 2: End-to-End Integration Test
```bash
# Test frontend → GPT agent → backend flow
curl -X POST http://localhost:3000/api/gpt/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me portfolio metrics",
    "portfolioId": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
  }'

# Should return GPT analysis with backend data
```

### Step 3: Browser Integration Test
1. Open browser to `http://localhost:3000`
2. Navigate to `/chat` page
3. Select demo portfolio from dropdown
4. Submit prompt: "Show portfolio summary"
5. Verify GPT response includes backend data

## Development Workflow

### Project Structure
```
SigmaSight/
├── backend/           # FastAPI + PostgreSQL (port 8000)
│   ├── app/models/    # Database models (PortfolioSnapshot, Position, etc.)
│   └── app/api/v1/    # REST endpoints
├── gptagent/          # GPT Agent (port 8787)
│   ├── apps/api/      # Fastify API server  
│   └── packages/      # Analysis agent, schemas, utils
└── frontend/          # Next.js frontend (port 3000)
    ├── app/           # App router pages
    └── docs/          # Implementation documentation
```

### Development Process
1. **Backend Changes**: Modify database models → run migrations → update API endpoints
2. **GPT Agent Changes**: Update system prompt → modify tools → rebuild packages  
3. **Frontend Changes**: Update TypeScript interfaces → modify components → test integration

### API Data Flow
```
Frontend Page → Next.js API Route → GPT Agent (8787) → Backend Tools → Database
     ↑                                    ↓
Browser UI ← Component State ← SWR Cache ← Structured Response ← JSON Data
```

## Common Issues & Solutions

### Backend Connection Issues
**Issue**: `ECONNREFUSED` when calling backend
```bash
# Solution: Verify backend is running and healthy
curl http://localhost:8000/health
cd backend && uv run python run.py
```

**Issue**: Database connection errors
```bash
# Solution: Verify PostgreSQL is running
docker ps | grep postgres
cd backend && docker-compose up -d
```

### GPT Agent Connection Issues  
**Issue**: GPT agent tools fail to call backend
```bash
# Solution: Check GPT agent environment variables
cat gptagent/apps/api/.env
# Ensure BACKEND_API_URL=http://localhost:8000/api/v1

# Test direct backend connection from GPT agent
curl -X POST http://localhost:8787/tools/get_portfolio_snapshot \
  -H "Content-Type: application/json" \
  -d '{"portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"}'
```

**Issue**: OpenAI API errors
```bash
# Solution: Verify OpenAI API key
echo $OPENAI_API_KEY
# Check GPT agent logs for specific error messages
```

### Frontend Integration Issues
**Issue**: Frontend can't reach backend/GPT agent
```bash
# Solution: Check environment variables
cat frontend/.env.local
# Test API routes
curl http://localhost:3000/api/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/summary
```

**Issue**: TypeScript type errors
```bash
# Solution: Regenerate types from backend schemas
npm run generate-types
# Or manually update interfaces in lib/types.ts
```

### Data Consistency Issues
**Issue**: Frontend displays incorrect data
```bash
# Solution: Verify backend data matches frontend types
curl http://localhost:8000/api/v1/reports/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/content/json | jq

# Compare with frontend type definitions
cat frontend/lib/types.ts
```

## Testing Strategy

### Unit Testing
```bash
# Frontend component tests
npm run test

# GPT agent tests  
cd gptagent && pnpm test

# Backend tests
cd backend && uv run pytest
```

### Integration Testing
```bash
# Test frontend → GPT agent → backend flow
npm run test:integration

# Test with mock backend data
npm run test:contracts
```

### Manual Testing Checklist
- [ ] All three services start successfully
- [ ] Backend returns demo portfolio data
- [ ] GPT agent can call all backend tools
- [ ] Frontend displays real backend data
- [ ] Chat page generates insights from backend data
- [ ] All pages load without errors

## Performance Optimization

### Backend Optimization
- Verify backend batch processing runs successfully
- Check database query performance with `EXPLAIN ANALYZE`
- Monitor backend API response times

### GPT Agent Optimization
- Cache GPT responses where appropriate
- Optimize tool call sequences
- Monitor OpenAI API usage and costs

### Frontend Optimization  
- Use SWR for efficient backend data caching
- Implement proper loading states
- Optimize bundle size with Next.js analyzer

## Deployment Considerations

### Environment Variables
Ensure all three systems use consistent environment variables:
- Same `JWT_SECRET` for authentication
- Same database connection for backend/GPT agent
- Matching API URLs for service communication

### Service Dependencies
Deploy in order:
1. **PostgreSQL database**
2. **Backend API** (with database migrations)
3. **GPT Agent** (with backend connectivity)  
4. **Frontend** (with both backend and GPT agent connectivity)

### Monitoring & Observability
- Backend: FastAPI logs and database monitoring
- GPT Agent: Tool call success rates and response times
- Frontend: User analytics and error tracking

## Support & Troubleshooting

### Log Locations
- **Backend**: `backend/logs/sigmasight.log`
- **GPT Agent**: Console output from `pnpm -w run dev`  
- **Frontend**: Console output from `npm run dev`

### Diagnostic Commands
```bash
# System health check
curl http://localhost:8000/health     # Backend
curl http://localhost:8787/health     # GPT Agent  
curl http://localhost:3000/api/health # Frontend

# Data verification
curl http://localhost:8000/api/v1/reports/portfolios
curl http://localhost:8787/analyze -X POST -d '{"prompt":"test"}'
curl http://localhost:3000/api/portfolio/a3209353-9ed5-4885-81e8-d4bbc995f96c/summary
```

### Getting Help
- Review `frontend/docs/IMPLEMENTATION_PLAN.md` for architecture details
- Check `backend/CLAUDE.md` for backend-specific guidance  
- See `gptagent/docs/IMPLEMENTATION_ACTIONS.md` for GPT agent details

---

**Next Steps**: After successful setup, follow `IMPLEMENTATION_PLAN.md` for detailed development guidance and feature implementation.
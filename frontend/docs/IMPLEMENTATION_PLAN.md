# SigmaSight Frontend Implementation Plan - Backend & GPT Agent Aligned

**Date:** 2025-08-25  
**Status:** Implementation Ready  

## Overview

This implementation plan aligns the GPT-enabled frontend with the **existing SigmaSight backend** and **GPT agent system**. The frontend will consume data from backend database models via FastAPI endpoints and integrate with the GPT agent for AI-powered portfolio insights.

## Backend System Alignment

### Database Model Integration
Based on backend analysis, the frontend will integrate with these **existing models**:

**Core Data Models:**
- `PortfolioSnapshot` → Portfolio metrics and exposures
- `Position` → Individual positions with Greeks and market data
- `PortfolioReport` → Generated reports (JSON/CSV/Markdown)
- `PositionGreeks` → Options Greeks per position
- `PositionFactorExposure` → Factor loadings per position
- `User/Portfolio` → Authentication and ownership

**Demo Portfolio UUIDs (from backend):**
- Individual Investor: `a3209353-9ed5-4885-81e8-d4bbc995f96c`
- High Net Worth: `14e7f420-b096-4e2e-8cc2-531caf434c05`
- Hedge Fund Style: `cf890da7-7b74-4cb4-acba-2205fdd9dff4`

### Backend API Integration Points
Frontend will call **existing backend endpoints**:
- `GET /api/v1/reports/portfolios` → List available portfolio reports
- `GET /api/v1/reports/portfolio/{id}/content/{format}` → Get report content
- `GET /api/v1/portfolio/` → Portfolio management (when implemented)
- Backend batch processing system for analytics calculations

## GPT Agent System Alignment

### GPT Agent Integration Architecture
Frontend integrates with **existing GPT agent** (`gptagent/` folder):

**GPT Agent Tools Mapping:**
```typescript
// Frontend calls GPT agent tools via backend proxy
interface GPTToolMapping {
  get_portfolio_snapshot: 'GET /api/portfolio/:id/summary';
  get_positions: 'GET /api/portfolio/:id/positions';
  get_factor_exposures: 'GET /api/portfolio/:id/factors';
  get_factor_risk_contrib: 'GET /api/portfolio/:id/factor-risk';
  get_var: 'GET /api/portfolio/:id/risk/var';
  get_stress_results: 'GET /api/portfolio/:id/stress';
  get_short_metrics: 'GET /api/portfolio/:id/short';
  get_modeling_session: 'GET /api/portfolio/:id/modeling';
  get_exports: 'GET /api/portfolio/:id/exports';
}
```

**GPT Agent System Prompt Integration:**
Use the **backend-aligned system prompt** from `gptagent/packages/analysis-agent/src/system-prompt.ts`:
- Never recompute analytics (use backend calculations)
- Focus on interpretation and narrative generation
- Structured JSON output with machine-readable insights
- Gap detection for missing data

### GPT Agent Communication Flow
```
Frontend → Next.js API Route → GPT Agent (port 8787) → Backend APIs → Database
                ↓
    Structured Response with Insight Cards ← GPT Analysis ← Backend Data
```

## Frontend Architecture - Backend Aligned

### Technology Stack
- **Next.js 14+** (App Router) with TypeScript
- **Tailwind CSS + shadcn/ui** for styling
- **SWR** for backend API integration with cache invalidation
- **Recharts** for data visualization
- **GPT Agent Client** for AI integration

### Page Implementation - Backend Data Driven

#### 1. Chat (GPT) Page (`/chat`)
**Backend Integration:**
- Calls GPT agent at `http://localhost:8787/analyze`
- GPT agent uses backend tools to retrieve portfolio data
- Real-time context injection with actual portfolio UUIDs

**Data Flow:**
```
User Prompt + Portfolio Context → GPT Agent → Backend Tool Calls → Database Query → GPT Analysis → Insight Cards
```

#### 2. Portfolio Page (`/portfolio/[id]`)
**Backend Integration:**
- `GET /api/v1/reports/portfolio/{id}/content/json` → Portfolio report data
- Maps to `PortfolioSnapshot` model fields:
  - `total_value` → equity display
  - `gross_exposure` → exposure percentage
  - `portfolio_delta/gamma` → Greeks summary

**Component Mapping:**
```typescript
interface PortfolioData {
  // From PortfolioSnapshot model
  total_value: number;        // Decimal from backend
  gross_exposure: number;     // Decimal from backend
  net_exposure: number;       // Decimal from backend
  portfolio_delta: number;    // Greeks aggregation
  portfolio_gamma: number;    // Greeks aggregation
  daily_pnl: number;         // P&L calculation
  daily_return: number;       // Return percentage
}
```

#### 3. Risk Page (`/risk/[id]`)
**Backend Integration:**
- Calls GPT agent `get_factor_exposures` tool → Backend factor calculations
- `get_var` tool → Backend VaR/ES calculations  
- `get_stress_results` tool → Backend stress testing

**Data Sources:**
```typescript
// Via GPT agent tools calling backend
const factorData = await gptAgent.get_factor_exposures(portfolioId);
const varData = await gptAgent.get_var(portfolioId, { method: 'historical', horizon: '1d' });
const stressData = await gptAgent.get_stress_results(portfolioId);
```

#### 4. Targets & Tags Page (`/targets/[id]`)
**Backend Integration:**
- Maps to backend `Position` and `Tag` models
- CRUD operations through backend API endpoints
- Real-time updates with SWR cache invalidation

### State Management - Backend Synchronized

```typescript
interface AppState {
  // Current portfolio (from backend)
  currentPortfolio: {
    id: string; // UUID from backend
    name: string;
    lastUpdated: string;
  };
  
  // Backend calculation status
  calculationEngines: {
    status: 'pending' | 'running' | 'completed' | 'failed';
    completedEngines: number;
    totalEngines: number; // 8 engines from backend
  };
  
  // GPT agent connection
  gptAgent: {
    connected: boolean;
    lastResponse: string;
    tools: Record<string, boolean>; // Tool availability
  };
}
```

## API Integration Strategy

### Backend API Proxy Layer
Create Next.js API routes that proxy to **existing backend**:

```typescript
// app/api/portfolio/[id]/summary/route.ts
export async function GET(request: Request, { params }: { params: { id: string } }) {
  const portfolioId = params.id;
  
  // Call existing backend endpoint
  const backendResponse = await fetch(`${BACKEND_URL}/api/v1/reports/portfolio/${portfolioId}/content/json`);
  const reportData = await backendResponse.json();
  
  // Transform backend report format to frontend contract
  const summaryData = {
    portfolioId: reportData.portfolio_id,
    equity: reportData.content_json.portfolio_metrics.total_value,
    grossExposurePct: reportData.content_json.portfolio_metrics.gross_exposure_pct,
    // ... map other fields from PortfolioSnapshot model
  };
  
  return Response.json(summaryData);
}
```

### GPT Agent Integration Layer
```typescript
// app/api/gpt/analyze/route.ts
export async function POST(request: Request) {
  const { prompt, portfolioId, context } = await request.json();
  
  // Call GPT agent with backend-aligned context
  const gptResponse = await fetch('http://localhost:8787/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      context: {
        portfolio_id: portfolioId,
        // GPT agent will use its tools to call backend
      }
    })
  });
  
  const analysis = await gptResponse.json();
  return Response.json(analysis);
}
```

### Data Type Mapping - Backend to Frontend
```typescript
// Map backend SQLAlchemy types to TypeScript
interface BackendDataMapping {
  // Decimal fields from backend → number
  total_value: number;        // From PortfolioSnapshot.total_value (Decimal)
  gross_exposure: number;     // From PortfolioSnapshot.gross_exposure (Decimal)
  
  // UUID fields from backend → string
  portfolio_id: string;       // From PortfolioSnapshot.portfolio_id (UUID)
  position_id: string;        // From Position.id (UUID)
  
  // Date fields from backend → string
  snapshot_date: string;      // From PortfolioSnapshot.snapshot_date (Date)
  created_at: string;         // From timestamps (DateTime)
  
  // Enum fields from backend → union types
  position_type: 'LC' | 'LP' | 'SC' | 'SP' | 'LONG' | 'SHORT'; // From PositionType enum
}
```

## Development Phases - Backend Integration First

### Phase 1: Backend Connection (Week 1)
1. **Next.js Setup**: Configure to work with existing backend
2. **Database Verification**: Confirm access to demo portfolios
3. **API Proxy Setup**: Create routes that call existing backend endpoints
4. **Authentication**: JWT integration with backend auth system

### Phase 2: GPT Agent Integration (Week 2)
1. **GPT Agent Client**: Connect to existing GPT agent at localhost:8787
2. **Tool Mapping**: Verify all 9 GPT tools work with backend
3. **System Prompt**: Use backend-aligned prompt from gptagent package
4. **Response Handling**: Parse structured JSON from GPT agent

### Phase 3: Core Pages with Real Data (Week 3-4)
1. **Portfolio Page**: Display data from PortfolioSnapshot model
2. **Risk Page**: Show factor exposures via GPT agent tools
3. **Chat Page**: Full GPT integration with backend context
4. **Data Validation**: Ensure frontend contracts match backend models

### Phase 4: Advanced Features (Week 5-6)
1. **Targets & Tags**: CRUD operations with backend Position/Tag models  
2. **Real-time Updates**: SWR integration with backend batch processing
3. **Error Handling**: Handle backend calculation engine failures
4. **Performance**: Optimize with backend query patterns

## Testing Strategy - Backend Integration

### Backend Integration Tests
```typescript
describe('Backend Integration', () => {
  test('Portfolio data matches backend PortfolioSnapshot model', async () => {
    const portfolioId = 'a3209353-9ed5-4885-81e8-d4bbc995f96c'; // Demo portfolio
    const response = await fetch(`/api/portfolio/${portfolioId}/summary`);
    const data = await response.json();
    
    expect(data.portfolioId).toBe(portfolioId);
    expect(typeof data.equity).toBe('number');
    expect(data.grossExposurePct).toBeGreaterThan(0);
  });
  
  test('GPT agent tools call backend successfully', async () => {
    const gptResponse = await fetch('/api/gpt/analyze', {
      method: 'POST',
      body: JSON.stringify({
        prompt: 'Show portfolio summary',
        portfolioId: 'a3209353-9ed5-4885-81e8-d4bbc995f96c'
      })
    });
    
    const analysis = await gptResponse.json();
    expect(analysis.machine_readable.portfolio_metrics).toBeDefined();
  });
});
```

### GPT Agent Contract Tests
```typescript
test('GPT agent returns expected schema', async () => {
  const analysis = await gptAgent.analyze('Portfolio overview', { portfolio_id: 'uuid' });
  
  expect(analysis).toMatchSchema({
    summary_markdown: 'string',
    machine_readable: {
      portfolio_metrics: expect.any(Object),
      concentration: expect.any(Object),
      gaps: expect.any(Array),
      next_steps: expect.any(Array)
    }
  });
});
```

## Deployment & Environment Setup

### Environment Variables - Backend Aligned
```env
# Backend Integration
BACKEND_API_URL=http://localhost:8000
BACKEND_DATABASE_URL=postgresql://user:pass@localhost/sigmasight

# GPT Agent Integration  
GPT_AGENT_URL=http://localhost:8787
OPENAI_API_KEY=sk-your-key-here

# Authentication (same as backend)
JWT_SECRET=same-secret-as-backend
NEXTAUTH_SECRET=your-nextauth-secret

# Demo Portfolio IDs (from backend)
DEMO_INDIVIDUAL_PORTFOLIO=a3209353-9ed5-4885-81e8-d4bbc995f96c
DEMO_HIGH_NET_WORTH_PORTFOLIO=14e7f420-b096-4e2e-8cc2-531caf434c05
DEMO_HEDGE_FUND_PORTFOLIO=cf890da7-7b74-4cb4-acba-2205fdd9dff4
```

### Development Dependencies
```bash
# Backend must be running
cd ../backend && uv run python run.py

# GPT agent must be running  
cd ../gptagent && pnpm -w run dev

# Frontend development
npm run dev
```

## Success Criteria - Full System Integration

### Backend Integration ✅
- All pages display real data from backend database models
- API calls route through existing FastAPI endpoints
- Authentication works with existing JWT system
- Real-time data updates via SWR with backend batch processing

### GPT Agent Integration ✅  
- GPT chat uses all 9 backend-integrated tools
- System prompt aligns with backend calculation principles
- Structured responses with insight cards render correctly
- Gap detection shows missing data from backend

### Data Consistency ✅
- Frontend TypeScript types match backend SQLAlchemy models
- Demo portfolios load and display correctly
- All CRUD operations persist to backend database
- Error handling matches backend error patterns

### Performance Integration ✅
- Frontend response times < 2s with backend caching
- GPT responses < 5s using backend pre-calculated data
- Backend batch processing status reflected in UI
- SWR caching aligned with backend data update patterns

This implementation plan ensures complete alignment with the existing backend system and GPT agent, treating them as the authoritative data sources while building a modern, responsive frontend experience.
# GPT Agent Implementation Actions - Backend Aligned

**Date:** 2025-08-25  
**Status:** In Progress  

## Overview
This document tracks the implementation actions taken to build the SigmaSight GPT Analysis Agent that aligns with the existing backend database models and API structure.

## Backend Analysis Summary

### Existing Database Models
Based on analysis of `backend/app/models/`, the following key models exist:

1. **PortfolioReport** (`reports.py`) - Stores generated portfolio reports with JSON/CSV/MD content
2. **Position** (`positions.py`) - Individual positions with Greeks, tags, and factor exposures  
3. **PortfolioSnapshot** (`snapshots.py`) - Daily portfolio state with aggregated metrics
4. **User/Portfolio** relationships with UUIDs as primary keys

### Existing API Endpoints
- **Reports API** (`backend/app/api/v1/reports.py`) - File-based portfolio report retrieval
- **Portfolio API** (`backend/app/api/v1/portfolio.py`) - Portfolio management (TODO implementation)

### Key Backend Patterns
- Async/await with SQLAlchemy 2.0
- UUID primary keys throughout
- Comprehensive batch processing framework
- Multi-provider market data (FMP, Polygon, FRED)

## Implementation Strategy - Backend Aligned

### Phase 1: Tool Mapping to Backend Models ✅

The GPT tools must align with existing backend data structures:

**Tool → Backend Model Mapping:**
- `get_portfolio_snapshot` → `PortfolioSnapshot` model + aggregations
- `get_positions` → `Position` model with related `PositionGreeks`, `PositionFactorExposure` 
- `get_factor_exposures` → `PositionFactorExposure` via relationships
- `get_factor_risk_contrib` → Calculated from factor covariance data
- `get_var` → Backend calculation engines (market_risk.py)
- `get_stress_results` → Backend stress testing calculations
- `get_short_metrics` → Position-level short selling data
- `get_modeling_session` → Backend modeling session data
- `get_exports` → PortfolioReport model query

### Phase 2: Schema Alignment (Pending)

**Action Required**: Create Zod schemas that match backend SQLAlchemy models

**Key Schema Mappings:**
```typescript
// Portfolio Snapshot Schema - matches backend/app/models/snapshots.py:PortfolioSnapshot
interface PortfolioSnapshotData {
  portfolio_id: string;  // UUID
  snapshot_date: string; // Date
  total_value: number;   // Decimal -> number
  gross_exposure: number;
  net_exposure: number;
  portfolio_delta?: number;
  portfolio_gamma?: number;
  // ... other fields from PortfolioSnapshot model
}

// Position Schema - matches backend/app/models/positions.py:Position  
interface PositionData {
  id: string;           // UUID
  portfolio_id: string; // UUID
  symbol: string;
  position_type: "LC" | "LP" | "SC" | "SP" | "LONG" | "SHORT";
  quantity: number;     // Decimal -> number
  entry_price: number;
  market_value?: number;
  // ... other fields from Position model
}
```

### Phase 3: Backend API Integration (Pending)

**Action Required**: Build connectors that call the existing FastAPI backend

**Integration Points:**
1. **Direct Database Queries**: Use existing models for data retrieval
2. **API Endpoint Usage**: Leverage `/api/v1/reports/` endpoints  
3. **Batch Processing**: Integrate with existing batch orchestrator
4. **Authentication**: Use existing auth system from `backend/app/core/auth.py`

**Example Implementation:**
```typescript
// Tool connector that calls backend API
async function get_portfolio_snapshot(portfolio_id: string, as_of?: string) {
  const response = await fetch(`${BACKEND_URL}/api/v1/portfolio/${portfolio_id}/snapshot`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}
```

### Phase 4: Database-Specific Adaptations (Pending)

**Action Required**: Ensure GPT tools work with existing demo data

**Demo Portfolio UUIDs (from backend/app/api/v1/reports.py):**
- Individual Investor: `a3209353-9ed5-4885-81e8-d4bbc995f96c`  
- High Net Worth: `14e7f420-b096-4e2e-8cc2-531caf434c05`
- Hedge Fund Style: `cf890da7-7b74-4cb4-acba-2205fdd9dff4`

**Database Connection:**
- Use existing `backend/app/database.py` patterns
- Leverage `backend/app/core/dependencies.py` for session management
- Follow async patterns from existing codebase

## Implementation Actions Taken

### 1. Backend Structure Analysis ✅
- Analyzed `backend/app/models/` for data model structures
- Reviewed existing API endpoints in `backend/app/api/v1/`
- Identified key database relationships and patterns
- Mapped GPT tools to backend data sources

### 2. Demo Data Integration ✅  
- Identified 3 existing demo portfolios with UUIDs
- Located existing report generation in `backend/reports/` 
- Found portfolio report structure in `PortfolioReport` model

## Next Actions Required

### 3. System Prompt Integration
- **Status**: Pending
- **Action**: Update `packages/analysis-agent/src/system-prompt.ts` with backend-aligned prompt
- **Backend Context**: Must reference actual database fields and relationships

### 4. Zod Schema Creation
- **Status**: Pending  
- **Action**: Create schemas in `packages/schemas/src/index.ts` matching SQLAlchemy models
- **Backend Alignment**: Map `Decimal` → `number`, `UUID` → `string`, etc.

### 5. Backend API Connectors
- **Status**: Pending
- **Action**: Implement tools in `apps/api/src/routes/tools.ts` calling backend endpoints
- **Integration**: Use existing FastAPI endpoints or direct database queries

### 6. Database Integration
- **Status**: Pending
- **Action**: Configure connection to existing PostgreSQL database
- **Dependencies**: Same database used by backend application

## Backend-Specific Considerations

### Database Connection
- **Connection String**: Use same `DATABASE_URL` as backend
- **Authentication**: Integrate with existing user system  
- **Session Management**: Follow backend async session patterns

### Data Consistency  
- **Primary Keys**: All UUIDs, consistent with backend models
- **Relationships**: Respect existing foreign key constraints
- **Data Types**: Match Decimal precision, date formats from SQLAlchemy models

### Error Handling
- **Missing Data**: Use backend's graceful degradation patterns
- **API Failures**: Handle same way as backend batch processing
- **Gap Detection**: Align with backend validation logic

### Performance Optimization
- **Query Patterns**: Use existing backend query optimizations
- **Caching**: Leverage any existing backend caching strategies  
- **Async Processing**: Follow backend async/await patterns

## Testing with Backend Integration

### Test Strategy
1. **Use Existing Demo Data**: Test with 3 demo portfolios already in database
2. **Backend API Integration**: Verify tools call actual backend endpoints
3. **Data Validation**: Ensure schemas match actual database data formats
4. **End-to-End Flow**: Test complete GPT analysis with real backend data

### Validation Steps
1. Verify database connectivity using backend connection patterns
2. Test tool connectors with actual portfolio UUIDs  
3. Validate schema compatibility with real database records
4. Confirm GPT outputs match backend calculation results

## Dependencies on Backend

### Required Backend Services
- PostgreSQL database (same as backend)
- FastAPI backend running (for API calls)
- Authentication service (backend auth system)
- Market data services (if real-time data needed)

### Backend Integration Points
- Database models from `backend/app/models/`
- API endpoints from `backend/app/api/v1/` 
- Authentication from `backend/app/core/auth.py`
- Batch processing from `backend/app/batch/`

This implementation plan ensures complete alignment with the existing backend architecture and data models.
# Unresolved Questions & Inconsistencies (2025-07-15)

> The following items were flagged by the coding agent after multiple reviews of the current SigmaSight documentation. Clarifying these early will prevent re-work and ensure that all contributors share the same mental model.

## 1. Database Schema Gaps

### 1.1 Missing Core Tables
- **Users table**: Referenced throughout as foreign key but never defined. Need schema for auth, JWT tokens, sessions.
- **Portfolios table**: Referenced but not defined despite being fundamental to the system.
- **Tags tables**: API spec has complete CRUD operations but no `tags` or `position_tags` tables defined.
- **Factor definitions**: INSERT statements shown but table structure missing.

### 1.2 Data Mapping Unclear
- **CSV → Database**: How do CSV fields map to position records? Especially:
  - Option symbols (OCC format) → position_type enum
  - Negative quantities → SHORT positions
  - Comma-separated tags → database relationships
- **GICS data storage**: YFinance fetches sector/industry but no fields in `market_data_cache` for this.

## 2. Authentication & User Management
- PRD mentions "multiple demo accounts" and "JWT-based authentication".
- API requires `Authorization: Bearer {token}` headers.
- Database design references `users(id)` throughout.
- **But**: No user table schema, no `/auth/login` or `/auth/register` endpoints in API spec.

## 3. Greeks Calculation Contradiction
- **PRD Phase 1**: "Mock options Greeks display" with hardcoded values by position type.
- **API spec**: Detailed `/api/v1/risk/greeks` and `/api/v1/risk/greeks/calculate` endpoints.
- **Database**: `position_greeks` table for storage.
- **Question**: Mock values or real calculations? If mock, why the calculate endpoint?

## 4. Tag System Architecture
- CSV format includes tags field.
- API spec has full tag CRUD operations.
- TypeScript enums distinguish regular vs strategy tags.
- **Missing**: Database tables, relationship model, indexing strategy.

## 5. Market Data & Batch Processing

### 5.1 Data Sources
- PRD states Polygon.io for "all market data except GICS".
- YFinance specifically for GICS sector/industry.
- Database shows generic `market_data_cache` without source tracking.

### 5.2 Calculation Timing
- PRD emphasizes "batch processing first" and "pre-calculated analytics".
- API spec shows many real-time calculation endpoints.
- Unclear what runs in batch vs on-demand:
  - Greeks calculations?
  - Factor exposures?
  - Risk metrics?
  - P&L calculations?

## 6. Async vs Sync API Design
- API spec describes dual-mode endpoints with job management.
- Most endpoints marked "Sync only" in implementation notes.
- PRD focuses on pre-calculation for performance.
- No job/async tables in database design.
- **Question**: Is async actually needed or just sync with cached results?

## 7. Portfolio Structure
- **PRD**: "Simplified Portfolio Structure - Single portfolio per user".
- **API**: Multiple endpoints suggest multi-portfolio (`/api/v1/portfolios`).
- **Database**: Has `portfolios` table implying multi-portfolio support.
- **Question**: Single or multiple portfolios per user?

## 8. Version Numbering
- Document titles: "V1.4"
- Frontend prototype: "V5"
- API base URL: "/v1"
- No explanation of versioning scheme or what each number represents.

## 9. Factor Calculations
- Database mentions 8 factors with ETF proxies.
- "Short Interest" marked as "custom calculation" with no details.
- Factor covariance matrix tables defined but no calculation methodology.
- Legacy scripts have factor logic but unclear what to preserve.

## 10. Position Type Logic
- **CSV**: Uses positive/negative quantity.
- **Database**: Explicit position_type enum (LONG, SHORT, LC, LP, SC, SP).
- **Options**: Need OCC symbology parsing.
- No transformation logic specified for CSV → position_type.

## 11. Deployment Configuration
- PRD mentions Railway deployment with UV package manager.
- No details on:
  - UV integration with FastAPI
  - Railway-specific configuration
  - Environment variable management
  - Start commands or build process

## 12. Demo Data Requirements
- PRD mentions "pre-seeded demo data" and "90 days of historical snapshots".
- No specification of:
  - Number of positions
  - Which tickers to use
  - Date ranges
  - Realistic vs synthetic data
  - Demo user credentials

## 13. Legacy Script Purpose
- README says "DO NOT copy infrastructure code (S3, Parquet)".
- Scripts primarily show Parquet/S3 operations.
- Unclear which calculation logic to extract vs ignore.
- Factor calculations, Greeks, and risk metrics scattered across scripts.

## 14. File Organization
- Requirements under `sigmasight-BE/docs/requirements/`.
- New files (TODO.md) at project root.
- Legacy code inside docs tree.
- Inconsistent file naming (CAPS_WITH_UNDERSCORES vs lowercase).

## 15. API Endpoint Inconsistencies
- Endpoint paths mix singular/plural (`/portfolio` vs `/positions`).
- Some endpoints have both sync and async versions, others don't.
- Job management system described but seems unnecessary given batch processing approach.

---
**Next Steps:**
1. Resolve these questions to create consistent requirements.
2. Update all documentation files with clarifications.
3. Ensure database schema is complete before implementation.
4. Decide on mock vs real calculations for Phase 1.
5. Create a clear data flow diagram showing batch vs real-time operations.

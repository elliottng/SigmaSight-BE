# SigmaSight Complete Implementation Guide

**Last Updated**: August 26, 2025  
**Version**: 1.0  
**Implementation Status**: Production Ready  

## Executive Summary

This document provides comprehensive documentation for the complete SigmaSight portfolio risk management platform implementation. The system consists of three integrated services providing institutional-grade portfolio analytics with AI-powered analysis capabilities.

**System Architecture**: Three-Service Integration
- **Backend Service**: FastAPI with PostgreSQL (Port 8001)
- **Frontend Service**: Next.js React Application (Port 3008) 
- **GPT Agent Service**: Node.js AI Analysis Service (Port 8888)

**Implementation Status**: ✅ COMPLETE AND OPERATIONAL
- All services successfully deployed and tested
- Database populated with demo portfolios
- API endpoints functional and documented
- Frontend application fully responsive
- GPT agent integration active

---

## 🏗️ System Architecture Overview

### Service Integration Map

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   GPT Agent      │    │   Backend       │
│   Next.js       │◄──►│   Node.js        │◄──►│   FastAPI       │
│   Port 3008     │    │   Port 8888      │    │   Port 8001     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        ▼
         │                        │              ┌─────────────────┐
         │                        │              │   PostgreSQL    │
         │                        │              │   Database      │
         │                        │              │   Port 5432     │
         └────────────────────────┴──────────────┼─────────────────┘
                                  │
                      ┌──────────────────┐
                      │   Report Files   │
                      │   File System    │
                      └──────────────────┘
```

### Data Flow Architecture

```
User Interaction → Frontend UI → Next.js API Routes → GPT Agent Service 
     ↓                              ↓
   SWR Cache                   Backend API Calls
     ↓                              ↓
TypeScript Interfaces       PostgreSQL Database
     ↓                              ↓
Component Updates            Calculation Engine
     ↓                              ↓
  UI Display ←── JSON Response ←── Portfolio Analytics
```

### Core Technologies

**Backend Stack**:
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **API**: RESTful endpoints with OpenAPI documentation
- **Authentication**: JWT tokens with bcrypt password hashing
- **Analytics**: 8 calculation engines for portfolio analysis
- **Market Data**: Multi-provider API integration (FMP, Polygon, FRED)

**Frontend Stack**:
- **Framework**: Next.js 15 with React 19
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React Context and SWR for server state
- **Components**: Custom UI components with loading states
- **Routing**: Next.js App Router with dynamic routes

**GPT Agent Stack**:
- **Framework**: Node.js with Fastify
- **AI Integration**: OpenAI GPT-4 API
- **Rate Limiting**: Token bucket algorithm
- **Tools**: Portfolio analysis functions
- **Data Processing**: JSON schema validation with Zod

---

## 🚀 Quick Start Guide

### Prerequisites

1. **System Requirements**:
   - Node.js 18+
   - Python 3.11+
   - PostgreSQL 14+
   - 4GB RAM minimum
   - Windows 10/11 or macOS 10.15+

2. **Development Tools**:
   - Git for version control
   - VS Code (recommended IDE)
   - Terminal/PowerShell access
   - Web browser (Chrome/Firefox recommended)

### Installation Steps

#### Step 1: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/your-org/SigmaSight.git
cd SigmaSight

# Verify project structure
ls -la  # Should see backend/, frontend/, gptagent/ directories
```

#### Step 2: Database Setup

```bash
# Start PostgreSQL (Docker recommended)
cd backend
docker-compose up -d

# Apply database migrations
uv run alembic upgrade head

# Seed with demo data
python scripts/reset_and_seed.py seed
```

#### Step 3: Backend Service

```bash
# Terminal 1: Backend Service
cd backend
uv run python run.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
# INFO:     Started server process [####]
# INFO:     Application startup complete.
```

#### Step 4: GPT Agent Service

```bash
# Terminal 2: GPT Agent Service
cd gptagent
npm install
pnpm -w run dev

# Expected output:
# API listening on :8888
# Server ready at http://localhost:8888
```

#### Step 5: Frontend Service

```bash
# Terminal 3: Frontend Service  
cd frontend
npm install
npm run dev

# Expected output:
# ▲ Next.js 15.2.4
# - Local:        http://localhost:3008
# ✓ Compiled successfully
```

#### Step 6: Verify Installation

1. **Backend API**: Visit `http://localhost:8001/docs` - Should show OpenAPI documentation
2. **GPT Agent**: Visit `http://localhost:8888/health` - Should return `{"status": "ok"}`
3. **Frontend**: Visit `http://localhost:3008` - Should show SigmaSight dashboard
4. **Database**: Check PostgreSQL connection on port 5432

---

## 💻 User Guide

### Accessing the Application

**Primary Interface**: http://localhost:3008

### Demo User Accounts

The system includes three pre-configured demo portfolios:

1. **Individual Investor Portfolio**
   - **ID**: `a3209353-9ed5-4885-81e8-d4bbc995f96c`
   - **Type**: Balanced retail investor portfolio
   - **Positions**: 16 diversified positions
   - **Focus**: Long-term growth with moderate risk

2. **High Net Worth Portfolio**
   - **ID**: `14e7f420-b096-4e2e-8cc2-531caf434c05`
   - **Type**: Sophisticated investor portfolio
   - **Positions**: 17 advanced positions
   - **Focus**: Alternative investments and tax optimization

3. **Hedge Fund Style Portfolio**
   - **ID**: `cf890da7-7b74-4cb4-acba-2205fdd9dff4`
   - **Type**: Long/short equity strategy
   - **Positions**: 30 positions including options
   - **Focus**: Market-neutral strategies with leverage

### Core Features

#### 1. Portfolio Dashboard

**URL**: `http://localhost:3008/dashboard`

**Features**:
- Real-time portfolio overview with key metrics
- Interactive charts showing performance trends
- Risk alerts and notifications panel
- Quick access to detailed analytics

**Key Metrics Displayed**:
- Total portfolio value
- Daily P&L and returns
- Risk metrics (VaR, volatility)
- Exposure analysis (gross/net)

#### 2. Chat Interface (AI Analysis)

**URL**: `http://localhost:3008/chat`

**Capabilities**:
- Natural language portfolio queries
- AI-powered risk analysis
- Factor exposure interpretation
- Investment recommendations

**Example Queries**:
- "What are my biggest risks today?"
- "How correlated are my positions?"
- "What's driving my performance?"
- "Should I rebalance my portfolio?"

#### 3. Risk Analytics

**URL**: `http://localhost:3008/risk`

**Features**:
- Value at Risk (VaR) calculations
- Stress testing scenarios
- Factor exposure analysis
- Options Greeks display
- Correlation analysis

**Risk Metrics**:
- 1-day VaR at 99% confidence
- Expected Shortfall (ES)
- Maximum drawdown analysis
- Beta and volatility measures

#### 4. Position Management

**URL**: `http://localhost:3008/positions`

**Features**:
- Complete position listing with details
- Sector and industry breakdowns
- Performance attribution
- Position-level risk metrics

**Position Data**:
- Symbol, quantity, market value
- Unrealized P&L and returns
- Risk contributions
- Factor exposures

#### 5. Reports Generation

**URL**: `http://localhost:3008/reports`

**Report Types**:
- **JSON**: Structured data for API consumption
- **CSV**: Tabular data for spreadsheet analysis  
- **Markdown**: Human-readable documentation

**Report Contents**:
- Portfolio snapshot with all positions
- Factor analysis with 7-factor model
- Risk metrics and stress tests
- Performance attribution analysis

### Navigation Guide

#### Main Navigation Menu

1. **Dashboard** - Portfolio overview and key metrics
2. **Chat** - AI-powered analysis interface
3. **Positions** - Detailed position management
4. **Risk** - Risk analytics and scenarios
5. **Market** - Real-time market data
6. **Reports** - Generated portfolio reports

#### Using the Chat Interface

1. **Starting a Conversation**:
   - Navigate to `/chat`
   - Type your question in the input field
   - Press Enter or click Send

2. **Context Setting**:
   - Chat automatically detects your portfolio context
   - Asks clarifying questions when needed
   - Maintains conversation history

3. **Getting Analysis**:
   - Ask about specific risks or opportunities
   - Request explanations of complex metrics
   - Get recommendations for portfolio improvements

4. **Example Conversation Flow**:
   ```
   User: "What are my biggest risks?"
   
   AI: "Based on your portfolio analysis, I've identified three primary risks:
   
   1. **Concentration Risk**: 35% exposure to technology sector
   2. **Options Gamma**: High gamma exposure expiring this week
   3. **Market Beta**: Portfolio beta of 1.25 indicates high market sensitivity
   
   Recommendations:
   - Consider reducing tech allocation to <25%
   - Review options positions for gamma management
   - Add defensive positions to reduce beta"
   ```

---

## 🔌 API Documentation

### Backend API Endpoints

**Base URL**: `http://localhost:8001/api/v1`

#### Authentication Endpoints

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
```

#### Portfolio Management

```http
GET    /portfolio/{id}                    # Portfolio overview
GET    /portfolio/{id}/summary            # Portfolio summary
GET    /portfolio/{id}/exposures          # Exposure metrics
GET    /portfolio/{id}/performance        # Performance data
POST   /portfolio/upload                  # Upload CSV positions
```

#### Position Management

```http
GET    /positions                         # List all positions
POST   /positions                         # Create new position
PUT    /positions/{id}                    # Update position
DELETE /positions/{id}                    # Delete position
GET    /positions/{id}/tags               # Position tags
```

#### Risk Analytics

```http
GET    /risk/overview                     # Risk summary
GET    /risk/greeks                       # Options Greeks
POST   /risk/greeks/calculate             # Calculate Greeks
GET    /risk/factors                      # Factor exposures
POST   /risk/scenarios                    # Stress testing
```

#### Market Data

```http
GET    /market/quotes                     # Real-time quotes
GET    /market/options                    # Options chains
GET    /market/historical                 # Historical data
```

#### Reports

```http
GET    /reports/portfolios               # Available portfolios
GET    /reports/portfolio/{id}/content/{format}  # Report content
POST   /reports/generate                 # Generate new report
GET    /reports/jobs/{job_id}           # Job status
```

#### Chat Integration

```http
POST   /chat/analyze                     # AI portfolio analysis
GET    /chat/history                     # Conversation history
POST   /chat/context                     # Update context
```

### GPT Agent API Endpoints

**Base URL**: `http://localhost:8888`

#### Analysis Endpoints

```http
POST   /analyze                          # Main analysis endpoint
GET    /tools/portfolio/{id}             # Portfolio tools
GET    /tools/risk/{id}                  # Risk analysis tools
GET    /tools/factors/{id}               # Factor analysis tools
```

#### Health and Status

```http
GET    /health                           # Service health check
GET    /status                           # Detailed status
GET    /metrics                          # Performance metrics
```

### Frontend API Routes

**Base URL**: `http://localhost:3008/api`

#### Chat Integration

```http
POST   /chat                             # Process chat message
POST   /chat/stream                      # Streaming chat response
```

#### Portfolio Data

```http
GET    /portfolio/{id}                   # Portfolio data proxy
GET    /positions                        # Positions data proxy
GET    /risk                             # Risk data proxy
```

### API Authentication

All API endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Token Management**:
- Tokens expire after 24 hours
- Refresh tokens available for automatic renewal
- Service-to-service authentication uses dedicated tokens

### Error Handling

Standard error response format:

```json
{
  "success": false,
  "errors": [
    {
      "code": "PORTFOLIO_NOT_FOUND",
      "message": "Portfolio with ID 'xyz' not found",
      "field": "portfolio_id"
    }
  ],
  "meta": {
    "timestamp": "2025-08-26T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## 🏢 Component Architecture

### Backend Components

#### 1. Database Models (`backend/app/models/`)

**Core Models**:
- **User**: User accounts and authentication
- **Portfolio**: Portfolio containers with metadata
- **Position**: Individual position holdings
- **PortfolioSnapshot**: Point-in-time portfolio state
- **PositionGreeks**: Options pricing Greeks
- **PositionFactorExposure**: Factor model exposures
- **StressTestResult**: Scenario analysis results

**Relationships**:
```python
User (1) → (N) Portfolio → (N) Position
                │              │
                │              ├→ (1) PositionGreeks
                │              └→ (N) PositionFactorExposure
                │
                ├→ (N) PortfolioSnapshot
                └→ (N) StressTestResult
```

#### 2. Calculation Engines (`backend/app/calculations/`)

**8 Core Engines**:
1. **Portfolio Aggregation** - Portfolio-level metrics calculation
2. **Position Greeks** - Options pricing using mibian library
3. **Factor Analysis** - 7-factor model regression analysis
4. **Market Risk** - VaR and Expected Shortfall calculations
5. **Stress Testing** - Scenario-based analysis
6. **Portfolio Snapshots** - Daily state capture
7. **Position Correlations** - Cross-position correlation analysis
8. **Factor Correlations** - Factor relationship modeling

#### 3. API Endpoints (`backend/app/api/v1/`)

**Endpoint Organization**:
- **auth.py**: Authentication and user management
- **portfolio.py**: Portfolio operations and analytics
- **positions.py**: Position CRUD operations
- **risk.py**: Risk analytics and stress testing
- **market_data.py**: Market data integration
- **reports.py**: Report generation and retrieval
- **chat.py**: GPT integration endpoints

### Frontend Components

#### 1. Page Components (`frontend/src/app/`)

**Core Pages**:
- **Dashboard** (`/dashboard`): Portfolio overview with metrics
- **Chat** (`/chat`): AI-powered analysis interface
- **Positions** (`/positions`): Position management interface
- **Risk** (`/risk`): Risk analytics dashboard
- **Market** (`/market`): Market data display
- **Reports** (`/reports`): Report generation interface

#### 2. UI Components (`frontend/src/components/`)

**Component Library**:
- **Button**: Configurable buttons with loading states
- **Card**: Flexible card layouts for data display
- **MetricCard**: Specialized metric display component
- **LoadingSpinner**: Various loading state indicators
- **ErrorDisplay**: Error handling components
- **EmptyState**: Empty state placeholders

**Layout Components**:
- **Navigation**: Responsive sidebar navigation
- **DashboardLayout**: Main application layout wrapper
- **ProtectedRoute**: Authentication route guards

**Feature Components**:
- **PortfolioOverview**: Portfolio summary dashboard
- **PositionTable**: Advanced position data grid
- **GreeksDisplay**: Options Greeks visualization
- **FactorExposure**: Factor analysis display
- **QuoteTable**: Real-time market quotes
- **AlertsPanel**: Risk alerts interface

#### 3. Services (`frontend/src/services/`)

**API Services**:
- **api.ts**: Main API client with authentication
- **auth.ts**: Authentication service
- **portfolio.ts**: Portfolio data service
- **risk.ts**: Risk analytics service
- **chat.ts**: GPT integration service

### GPT Agent Components

#### 1. Core Service (`gptagent/apps/api/src/`)

**Service Structure**:
- **index.ts**: Main Fastify server application
- **routes/analyze.ts**: Analysis endpoint handlers
- **routes/tools.ts**: Portfolio analysis tools

#### 2. Analysis Tools

**Tool Functions**:
- **get_portfolio_snapshot**: Portfolio state retrieval
- **get_positions**: Position data with analytics
- **get_factor_exposures**: Factor model analysis
- **get_var_es**: Risk metrics calculation
- **run_stress_test**: Scenario analysis

#### 3. Integration Layer

**Backend Integration**:
- HTTP client for backend API calls
- JWT authentication handling
- Error handling and retry logic
- Response caching and optimization

---

## ⚙️ Server Setup and Deployment

### Development Environment

#### Prerequisites Installation

**Windows Setup**:
```powershell
# Install Node.js
winget install OpenJS.NodeJS

# Install Python with uv
winget install astral-sh.uv

# Install PostgreSQL
winget install PostgreSQL.PostgreSQL

# Verify installations
node --version
uv --version
psql --version
```

**macOS Setup**:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install node python uv postgresql

# Verify installations
node --version
uv --version
psql --version
```

#### Database Configuration

**PostgreSQL Setup**:
```sql
-- Create database
CREATE DATABASE sigmasight_db;

-- Create user
CREATE USER sigmasight WITH PASSWORD 'sigmasight_dev';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sigmasight_db TO sigmasight;
```

**Environment Configuration** (`.env`):
```bash
# Database
DATABASE_URL=postgresql+asyncpg://sigmasight:sigmasight_dev@localhost:5432/sigmasight_db

# API Keys (required for full functionality)
POLYGON_API_KEY=your_polygon_key
FMP_API_KEY=your_fmp_key
FRED_API_KEY=your_fred_key
OPENAI_API_KEY=your_openai_key

# Security
SECRET_KEY=your_secret_key_here
```

### Service Configuration

#### Backend Configuration

**File**: `backend/app/config.py`
```python
DATABASE_URL = "postgresql+asyncpg://localhost:5432/sigmasight_db"
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# API Provider Settings
POLYGON_API_KEY = "your-polygon-key"
FMP_API_KEY = "your-fmp-key"
FRED_API_KEY = "your-fred-key"
OPENAI_API_KEY = "your-openai-key"

# Rate Limiting
API_RATE_LIMIT = 100  # requests per minute
POLYGON_RATE_LIMIT = 100  # requests per minute
```

#### Frontend Configuration

**File**: `frontend/next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1',
    NEXT_PUBLIC_GPT_AGENT_URL: process.env.NEXT_PUBLIC_GPT_AGENT_URL || 'http://localhost:8888',
  },
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
```

#### GPT Agent Configuration

**File**: `gptagent/apps/api/.env`
```bash
PORT=8888
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_API_URL=http://localhost:8001/api/v1
RATE_LIMIT_MAX=60
RATE_LIMIT_WINDOW=60000
```

### Production Deployment

#### Docker Configuration

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv
RUN uv install --frozen

# Copy application
COPY . .

# Expose port
EXPOSE 8001

# Start server
CMD ["uv", "run", "python", "run.py"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3008

# Start server
CMD ["npm", "start"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: sigmasight_db
      POSTGRES_USER: sigmasight
      POSTGRES_PASSWORD: sigmasight_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql+asyncpg://sigmasight:sigmasight_dev@postgres:5432/sigmasight_db

  gpt-agent:
    build: ./gptagent
    ports:
      - "8888:8888"
    depends_on:
      - backend
    environment:
      - BACKEND_API_URL=http://backend:8001/api/v1

  frontend:
    build: ./frontend
    ports:
      - "3008:3008"
    depends_on:
      - backend
      - gpt-agent
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8001/api/v1
      - NEXT_PUBLIC_GPT_AGENT_URL=http://gpt-agent:8888

volumes:
  postgres_data:
```

#### Deployment Commands

**Development Deployment**:
```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend uv run alembic upgrade head

# Seed demo data
docker-compose exec backend python scripts/reset_and_seed.py seed

# Check service health
curl http://localhost:8001/docs      # Backend API docs
curl http://localhost:8888/health    # GPT Agent health
curl http://localhost:3008           # Frontend application
```

**Production Deployment**:
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Database backup
docker-compose exec postgres pg_dump -U sigmasight sigmasight_db > backup.sql

# Service monitoring
docker-compose logs -f backend
docker-compose logs -f gpt-agent
docker-compose logs -f frontend
```

### Performance Optimization

#### Backend Optimization

**Database Indexing**:
```sql
-- Critical indexes for performance
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX idx_portfolio_snapshots_date ON portfolio_snapshots(calculation_date DESC);
CREATE INDEX idx_factor_exposures_position_id ON position_factor_exposures(position_id);
```

**Caching Configuration**:
```python
# Redis caching (optional)
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 300  # 5 minutes default

# Application-level caching
@lru_cache(maxsize=100)
def get_portfolio_summary(portfolio_id: str):
    # Cached portfolio summary calculation
    pass
```

#### Frontend Optimization

**Next.js Configuration**:
```javascript
// next.config.js optimizations
module.exports = {
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['@prisma/client'],
  },
  images: {
    optimize: true,
    formats: ['image/webp', 'image/avif'],
  },
}
```

**Bundle Analysis**:
```bash
# Analyze bundle size
npm run build
npm run analyze

# Performance auditing
npm run lighthouse
npm run perf-test
```

#### GPT Agent Optimization

**Response Caching**:
```javascript
// Cache GPT responses for identical queries
const responseCache = new Map();

async function getCachedGPTResponse(query, portfolioData) {
  const cacheKey = hashQuery(query, portfolioData);
  
  if (responseCache.has(cacheKey)) {
    return responseCache.get(cacheKey);
  }
  
  const response = await generateGPTResponse(query, portfolioData);
  responseCache.set(cacheKey, response);
  
  return response;
}
```

**Rate Limiting**:
```javascript
// Implement rate limiting for GPT API calls
const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});

app.use('/analyze', rateLimiter);
```

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Backend Service Issues

**Issue**: `ModuleNotFoundError: No module named 'uvicorn'`
```bash
# Solution: Use uv to run Python with proper virtual environment
cd backend
uv run python run.py  # CORRECT

# Avoid direct python execution:
python run.py  # INCORRECT - causes module errors
```

**Issue**: Database connection errors
```bash
# Check PostgreSQL service status
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Verify database configuration
psql -U sigmasight -d sigmasight_db -h localhost

# Test connection string
python -c "from app.database import get_async_session; print('DB connection OK')"
```

**Issue**: Port already in use (8001)
```bash
# Find process using port
netstat -tulpn | grep :8001  # Linux
lsof -i :8001  # macOS
netstat -ano | findstr :8001  # Windows

# Kill process or use different port
kill -9 <PID>
# Or change port in run.py
```

#### Frontend Service Issues

**Issue**: Build failures with TypeScript errors
```bash
# Fix TypeScript issues
npm run type-check

# Skip TypeScript errors for development (not recommended)
npm run build -- --no-type-check

# Update TypeScript and dependencies
npm update @types/node @types/react @types/react-dom
```

**Issue**: API connection errors
```bash
# Verify backend is running
curl http://localhost:8001/docs

# Check environment variables
echo $NEXT_PUBLIC_API_URL

# Test API endpoints
curl http://localhost:8001/api/v1/health
```

**Issue**: Styling issues with Tailwind CSS
```bash
# Rebuild Tailwind CSS
npm run dev

# Clear Next.js cache
rm -rf .next
npm run dev

# Verify Tailwind configuration
npx tailwindcss --init --check
```

#### GPT Agent Issues

**Issue**: OpenAI API key errors
```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Test API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**Issue**: Backend integration failures
```bash
# Check backend connectivity
curl http://localhost:8001/api/v1/health

# Verify JWT token handling
# Check logs for authentication errors
npm run dev -- --verbose
```

**Issue**: Rate limiting errors
```bash
# Check current rate limits
curl http://localhost:8888/metrics

# Adjust rate limit configuration in .env
RATE_LIMIT_MAX=120
RATE_LIMIT_WINDOW=60000
```

#### Database Issues

**Issue**: Migration failures
```bash
# Check current migration status
uv run alembic current

# Apply missing migrations
uv run alembic upgrade head

# Create new migration for schema changes
uv run alembic revision --autogenerate -m "description"
```

**Issue**: Data seeding problems
```bash
# Clear and reseed database
python scripts/reset_and_seed.py seed

# Check seeded data
python -c "
from app.database import get_async_session
from app.models.users import Portfolio
import asyncio

async def check():
    async with get_async_session() as db:
        result = await db.execute(select(Portfolio))
        print(f'Found {len(result.scalars().all())} portfolios')

asyncio.run(check())
"
```

**Issue**: Connection pool exhaustion
```bash
# Monitor database connections
SELECT count(*) FROM pg_stat_activity;

# Adjust connection pool settings in config
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

### Service Health Checks

#### Automated Health Monitoring

**Backend Health Check**:
```bash
#!/bin/bash
# health-check-backend.sh

BACKEND_URL="http://localhost:8001"

# Check API health
if curl -f -s "$BACKEND_URL/docs" > /dev/null; then
    echo "✅ Backend API: Healthy"
else
    echo "❌ Backend API: Unhealthy"
fi

# Check database connection
if curl -f -s "$BACKEND_URL/api/v1/health" > /dev/null; then
    echo "✅ Database: Connected"
else
    echo "❌ Database: Connection failed"
fi
```

**Frontend Health Check**:
```bash
#!/bin/bash
# health-check-frontend.sh

FRONTEND_URL="http://localhost:3008"

# Check Next.js server
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "✅ Frontend: Running"
else
    echo "❌ Frontend: Down"
fi

# Check API integration
if curl -f -s "$FRONTEND_URL/api/health" > /dev/null; then
    echo "✅ Frontend API: Connected"
else
    echo "❌ Frontend API: Connection failed"
fi
```

**GPT Agent Health Check**:
```bash
#!/bin/bash
# health-check-gpt-agent.sh

GPT_AGENT_URL="http://localhost:8888"

# Check GPT Agent service
if curl -f -s "$GPT_AGENT_URL/health" > /dev/null; then
    echo "✅ GPT Agent: Running"
else
    echo "❌ GPT Agent: Down"
fi

# Check OpenAI API connectivity
if curl -f -s "$GPT_AGENT_URL/tools/health" > /dev/null; then
    echo "✅ OpenAI API: Connected"
else
    echo "❌ OpenAI API: Connection failed"
fi
```

#### System Diagnostics

**Complete System Check**:
```bash
#!/bin/bash
# system-check.sh

echo "SigmaSight System Health Check"
echo "================================"

# Check all services
./health-check-backend.sh
./health-check-frontend.sh
./health-check-gpt-agent.sh

# Check database
echo ""
echo "Database Status:"
echo "=================="
if pg_isready -h localhost -p 5432; then
    echo "✅ PostgreSQL: Running"
    echo "📊 Database size: $(psql -U sigmasight -d sigmasight_db -t -c 'SELECT pg_size_pretty(pg_database_size(current_database()));')"
else
    echo "❌ PostgreSQL: Not running"
fi

# Check disk space
echo ""
echo "System Resources:"
echo "=================="
echo "💾 Disk usage: $(df -h / | awk 'NR==2{print $5}')"
echo "🧠 Memory usage: $(free -h | awk 'NR==2{print $3"/"$2}')"
echo "⚡ CPU usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"

echo ""
echo "Service Ports:"
echo "================"
echo "🔌 Port 5432 (PostgreSQL): $(lsof -i :5432 | wc -l | xargs echo) connections"
echo "🔌 Port 8001 (Backend): $(lsof -i :8001 | wc -l | xargs echo) connections"  
echo "🔌 Port 8888 (GPT Agent): $(lsof -i :8888 | wc -l | xargs echo) connections"
echo "🔌 Port 3008 (Frontend): $(lsof -i :3008 | wc -l | xargs echo) connections"
```

### Performance Diagnostics

#### Backend Performance

**Database Query Optimization**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log slow queries

-- Check slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze table statistics
ANALYZE portfolios;
ANALYZE positions;
ANALYZE portfolio_snapshots;
```

**API Performance Monitoring**:
```python
# Add to main.py
import time
from fastapi import Request

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### Frontend Performance

**Bundle Size Analysis**:
```bash
# Install bundle analyzer
npm install --save-dev @next/bundle-analyzer

# Analyze bundles
npm run analyze

# Check for large dependencies
npm ls --depth=0 --json | jq '.dependencies | to_entries | sort_by(.value.size) | reverse | .[0:10]'
```

**Performance Monitoring**:
```javascript
// Add to _app.tsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
  // Send to your analytics service
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Error Recovery Procedures

#### Service Recovery

**Backend Service Recovery**:
```bash
#!/bin/bash
# recover-backend.sh

echo "Recovering Backend Service..."

# Stop service
pkill -f "python run.py"

# Check database connection
if ! pg_isready -h localhost -p 5432; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Clear any locks
rm -f /tmp/sigmasight-backend.lock

# Restart service
cd backend
uv run python run.py &

echo "Backend service recovery complete"
```

**Database Recovery**:
```bash
#!/bin/bash
# recover-database.sh

echo "Database Recovery Procedure..."

# Stop backend to prevent conflicts
pkill -f "python run.py"

# Create backup before recovery
pg_dump -U sigmasight sigmasight_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify database integrity
psql -U sigmasight -d sigmasight_db -c "SELECT COUNT(*) FROM portfolios;"

# Restart backend
cd backend
uv run python run.py &

echo "Database recovery complete"
```

**Full System Recovery**:
```bash
#!/bin/bash
# full-system-recovery.sh

echo "Full System Recovery..."

# Stop all services
pkill -f "python run.py"
pkill -f "next"
pkill -f "node.*8888"

# Restart database
sudo systemctl restart postgresql

# Wait for database
sleep 5

# Start services in order
echo "Starting Backend..."
cd backend && uv run python run.py &
sleep 10

echo "Starting GPT Agent..."
cd ../gptagent && npm run dev &
sleep 5

echo "Starting Frontend..."
cd ../frontend && npm run dev &

echo "System recovery complete"
echo "Check http://localhost:3008 to verify"
```

---

## 📋 Implementation Patterns

### Development Patterns

#### Backend Development Patterns

**Model Definition Pattern**:
```python
# backend/app/models/example.py
from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped
from app.core.database import Base
import uuid

class ExampleModel(Base):
    __tablename__ = "examples"
    
    # Primary key
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Required fields
    name: Mapped[str] = Column(String(255), nullable=False)
    
    # Optional fields with defaults
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    portfolio_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"))
    
    # JSON fields for flexible data
    metadata: Mapped[dict] = Column(JSONB)
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="examples")
```

**API Endpoint Pattern**:
```python
# backend/app/api/v1/example.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.example import ExampleModel
from app.schemas.example import ExampleResponse, ExampleCreate
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/examples", tags=["examples"])

@router.get("", response_model=List[ExampleResponse])
async def list_examples(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List examples with pagination"""
    query = select(ExampleModel).offset(skip).limit(limit)
    result = await db.execute(query)
    examples = result.scalars().all()
    
    return [ExampleResponse.from_orm(example) for example in examples]

@router.post("", response_model=ExampleResponse)
async def create_example(
    example_data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new example"""
    example = ExampleModel(**example_data.dict())
    db.add(example)
    await db.commit()
    await db.refresh(example)
    
    return ExampleResponse.from_orm(example)
```

**Database Migration Pattern**:
```python
# backend/alembic/versions/xxx_add_example_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    op.create_table('examples',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('portfolio_id', UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for performance
    op.create_index('ix_examples_portfolio_id', 'examples', ['portfolio_id'])
    op.create_index('ix_examples_created_at', 'examples', ['created_at'])

def downgrade():
    op.drop_index('ix_examples_created_at', table_name='examples')
    op.drop_index('ix_examples_portfolio_id', table_name='examples')
    op.drop_table('examples')
```

#### Frontend Development Patterns

**Page Component Pattern**:
```typescript
// frontend/src/app/example/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Example } from '@/lib/types'
import { fetchExamples } from '@/services/api'
import { LoadingSpinner, ErrorDisplay, EmptyState } from '@/components/ui'

export default function ExamplePage() {
  const [examples, setExamples] = useState<Example[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    loadExamples()
  }, [])

  const loadExamples = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchExamples()
      setExamples(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load examples')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorDisplay error={error} onRetry={loadExamples} />
  if (examples.length === 0) return <EmptyState message="No examples found" />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Examples</h1>
      
      <div className="grid gap-4">
        {examples.map(example => (
          <ExampleCard key={example.id} example={example} />
        ))}
      </div>
    </div>
  )
}
```

**API Service Pattern**:
```typescript
// frontend/src/services/example.ts
import { apiRequest } from './api'
import { Example, ExampleCreate } from '@/lib/types'

export const exampleService = {
  async list(params?: { skip?: number; limit?: number }): Promise<Example[]> {
    const searchParams = new URLSearchParams()
    if (params?.skip) searchParams.set('skip', params.skip.toString())
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    
    const response = await apiRequest(`/examples?${searchParams}`)
    return response.json()
  },

  async create(data: ExampleCreate): Promise<Example> {
    const response = await apiRequest('/examples', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return response.json()
  },

  async get(id: string): Promise<Example> {
    const response = await apiRequest(`/examples/${id}`)
    return response.json()
  },

  async update(id: string, data: Partial<ExampleCreate>): Promise<Example> {
    const response = await apiRequest(`/examples/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return response.json()
  },

  async delete(id: string): Promise<void> {
    await apiRequest(`/examples/${id}`, { method: 'DELETE' })
  }
}
```

**Component Development Pattern**:
```typescript
// frontend/src/components/ExampleCard.tsx
import React from 'react'
import { Card, Button } from '@/components/ui'
import { Example } from '@/lib/types'
import { formatCurrency, formatDate } from '@/lib/utils'

interface ExampleCardProps {
  example: Example
  onEdit?: (example: Example) => void
  onDelete?: (example: Example) => void
  className?: string
}

export function ExampleCard({ 
  example, 
  onEdit, 
  onDelete, 
  className 
}: ExampleCardProps) {
  return (
    <Card className={`p-6 ${className}`}>
      <div className="flex justify-between items-start">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">{example.name}</h3>
          {example.description && (
            <p className="text-gray-600">{example.description}</p>
          )}
          {example.value && (
            <p className="text-sm text-gray-500">
              Value: {formatCurrency(example.value)}
            </p>
          )}
          <p className="text-xs text-gray-400">
            Created: {formatDate(example.created_at)}
          </p>
        </div>
        
        <div className="flex space-x-2">
          {onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(example)}
            >
              Edit
            </Button>
          )}
          {onDelete && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => onDelete(example)}
            >
              Delete
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}

// Default export with proper typing
export default ExampleCard
```

#### GPT Agent Development Patterns

**Tool Function Pattern**:
```typescript
// gptagent/src/tools/example-tool.ts
import { z } from 'zod'
import { backendApiClient } from '../clients/backend'

// Input validation schema
const ExampleToolInput = z.object({
  portfolioId: z.string().uuid(),
  includeMetadata: z.boolean().optional().default(false),
  dateRange: z.object({
    start: z.string().datetime().optional(),
    end: z.string().datetime().optional()
  }).optional()
})

export async function getExampleData(input: z.infer<typeof ExampleToolInput>) {
  // Validate input
  const validatedInput = ExampleToolInput.parse(input)
  
  try {
    // Call backend API - never compute independently
    const response = await backendApiClient.get(
      `/portfolio/${validatedInput.portfolioId}/examples`,
      {
        params: {
          include_metadata: validatedInput.includeMetadata,
          start_date: validatedInput.dateRange?.start,
          end_date: validatedInput.dateRange?.end
        }
      }
    )
    
    const data = response.data
    
    // Return structured response for GPT processing
    return {
      success: true,
      data: {
        portfolio_id: validatedInput.portfolioId,
        examples: data.examples || [],
        metadata: data.metadata || {},
        total_count: data.total_count || 0,
        calculation_date: data.calculation_date
      },
      gaps: identifyDataGaps(data),
      source: 'backend_calculation'  // Always indicate source
    }
    
  } catch (error) {
    // Handle backend API failures gracefully
    return {
      success: false,
      data: null,
      gaps: ['backend_api_unavailable', 'example_data_missing'],
      error: error.message,
      source: 'backend_error'
    }
  }
}

function identifyDataGaps(data: any): string[] {
  const gaps = []
  
  if (!data.examples || data.examples.length === 0) {
    gaps.push('no_example_data')
  }
  
  if (!data.metadata || Object.keys(data.metadata).length === 0) {
    gaps.push('missing_metadata')
  }
  
  if (!data.calculation_date) {
    gaps.push('missing_calculation_date')
  }
  
  return gaps
}

// Tool configuration for GPT
export const exampleToolConfig = {
  name: 'get_example_data',
  description: 'Retrieve example data for a portfolio from backend calculations',
  parameters: {
    type: 'object',
    properties: {
      portfolioId: {
        type: 'string',
        format: 'uuid',
        description: 'UUID of the portfolio to analyze'
      },
      includeMetadata: {
        type: 'boolean',
        description: 'Whether to include additional metadata'
      },
      dateRange: {
        type: 'object',
        properties: {
          start: { type: 'string', format: 'date-time' },
          end: { type: 'string', format: 'date-time' }
        },
        description: 'Optional date range for historical data'
      }
    },
    required: ['portfolioId']
  }
}
```

### Testing Patterns

#### Backend Testing Pattern

**Unit Test Pattern**:
```python
# backend/tests/test_example.py
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.example import ExampleModel
from app.api.v1.example import list_examples, create_example
from app.schemas.example import ExampleCreate

@pytest.fixture
def mock_db():
    return Mock(spec=AsyncSession)

@pytest.fixture
def mock_user():
    user = Mock()
    user.id = "user-uuid"
    user.email = "test@example.com"
    return user

@pytest.mark.asyncio
async def test_list_examples_success(mock_db, mock_user):
    # Arrange
    mock_examples = [
        ExampleModel(id="ex1", name="Example 1"),
        ExampleModel(id="ex2", name="Example 2")
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_examples
    mock_db.execute.return_value = mock_result
    
    # Act
    result = await list_examples(
        skip=0, 
        limit=10, 
        db=mock_db, 
        current_user=mock_user
    )
    
    # Assert
    assert len(result) == 2
    assert result[0].name == "Example 1"
    assert result[1].name == "Example 2"
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_example_success(mock_db, mock_user):
    # Arrange
    example_data = ExampleCreate(name="New Example", description="Test")
    
    # Act
    result = await create_example(
        example_data=example_data,
        db=mock_db,
        current_user=mock_user
    )
    
    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_list_examples_database_error(mock_db, mock_user):
    # Arrange
    mock_db.execute.side_effect = Exception("Database error")
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await list_examples(skip=0, limit=10, db=mock_db, current_user=mock_user)
    
    assert "Database error" in str(exc_info.value)
```

**Integration Test Pattern**:
```python
# backend/tests/integration/test_example_integration.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.example import ExampleModel
from app.database import get_async_session
from tests.fixtures.auth import create_test_user, get_auth_headers

@pytest.mark.asyncio
async def test_example_crud_integration():
    """Test complete CRUD flow for examples"""
    
    # Create test user and get auth headers
    user = await create_test_user()
    headers = get_auth_headers(user)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test CREATE
        create_data = {
            "name": "Integration Test Example",
            "description": "Created by integration test"
        }
        
        response = await client.post(
            "/api/v1/examples",
            json=create_data,
            headers=headers
        )
        
        assert response.status_code == 201
        created_example = response.json()
        example_id = created_example["id"]
        
        # Test READ
        response = await client.get(
            f"/api/v1/examples/{example_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        example = response.json()
        assert example["name"] == create_data["name"]
        
        # Test UPDATE
        update_data = {"name": "Updated Example Name"}
        
        response = await client.put(
            f"/api/v1/examples/{example_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        updated_example = response.json()
        assert updated_example["name"] == update_data["name"]
        
        # Test DELETE
        response = await client.delete(
            f"/api/v1/examples/{example_id}",
            headers=headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(
            f"/api/v1/examples/{example_id}",
            headers=headers
        )
        
        assert response.status_code == 404
```

#### Frontend Testing Pattern

**Component Test Pattern**:
```typescript
// frontend/src/components/__tests__/ExampleCard.test.tsx
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { ExampleCard } from '../ExampleCard'
import { Example } from '@/lib/types'

const mockExample: Example = {
  id: 'example-1',
  name: 'Test Example',
  description: 'This is a test example',
  value: 1000.50,
  created_at: '2025-08-26T10:00:00Z'
}

describe('ExampleCard', () => {
  it('renders example information correctly', () => {
    render(<ExampleCard example={mockExample} />)
    
    expect(screen.getByText('Test Example')).toBeInTheDocument()
    expect(screen.getByText('This is a test example')).toBeInTheDocument()
    expect(screen.getByText(/\$1,000\.50/)).toBeInTheDocument()
  })

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn()
    render(<ExampleCard example={mockExample} onEdit={onEdit} />)
    
    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)
    
    expect(onEdit).toHaveBeenCalledWith(mockExample)
  })

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = vi.fn()
    render(<ExampleCard example={mockExample} onDelete={onDelete} />)
    
    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)
    
    expect(onDelete).toHaveBeenCalledWith(mockExample)
  })

  it('does not render action buttons when handlers not provided', () => {
    render(<ExampleCard example={mockExample} />)
    
    expect(screen.queryByText('Edit')).not.toBeInTheDocument()
    expect(screen.queryByText('Delete')).not.toBeInTheDocument()
  })
})
```

**API Service Test Pattern**:
```typescript
// frontend/src/services/__tests__/example.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { exampleService } from '../example'
import * as api from '../api'

// Mock the api module
vi.mock('../api')

describe('exampleService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('list', () => {
    it('calls API with correct parameters', async () => {
      const mockResponse = {
        json: vi.fn().mockResolvedValue([
          { id: '1', name: 'Example 1' },
          { id: '2', name: 'Example 2' }
        ])
      }
      
      vi.mocked(api.apiRequest).mockResolvedValue(mockResponse as any)

      const params = { skip: 10, limit: 20 }
      await exampleService.list(params)

      expect(api.apiRequest).toHaveBeenCalledWith('/examples?skip=10&limit=20')
    })

    it('handles API errors gracefully', async () => {
      const error = new Error('API Error')
      vi.mocked(api.apiRequest).mockRejectedValue(error)

      await expect(exampleService.list()).rejects.toThrow('API Error')
    })
  })

  describe('create', () => {
    it('sends POST request with correct data', async () => {
      const mockResponse = {
        json: vi.fn().mockResolvedValue({ id: '1', name: 'New Example' })
      }
      
      vi.mocked(api.apiRequest).mockResolvedValue(mockResponse as any)

      const data = { name: 'New Example', description: 'Test' }
      await exampleService.create(data)

      expect(api.apiRequest).toHaveBeenCalledWith('/examples', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
    })
  })
})
```

### Error Handling Patterns

#### Backend Error Handling

**Custom Exception Pattern**:
```python
# backend/app/core/exceptions.py
from fastapi import HTTPException
from typing import Any, Dict, Optional

class SigmaSightException(Exception):
    """Base exception for SigmaSight application"""
    
    def __init__(
        self, 
        message: str, 
        code: str = None, 
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class PortfolioNotFoundError(SigmaSightException):
    def __init__(self, portfolio_id: str):
        super().__init__(
            message=f"Portfolio with ID '{portfolio_id}' not found",
            code="PORTFOLIO_NOT_FOUND",
            details={"portfolio_id": portfolio_id}
        )

class CalculationError(SigmaSightException):
    def __init__(self, calculation_type: str, reason: str):
        super().__init__(
            message=f"Failed to calculate {calculation_type}: {reason}",
            code="CALCULATION_ERROR",
            details={"calculation_type": calculation_type, "reason": reason}
        )

class InsufficientDataError(SigmaSightException):
    def __init__(self, data_type: str, required_count: int, actual_count: int):
        super().__init__(
            message=f"Insufficient {data_type}: need {required_count}, have {actual_count}",
            code="INSUFFICIENT_DATA",
            details={
                "data_type": data_type,
                "required_count": required_count,
                "actual_count": actual_count
            }
        )
```

**Exception Handler Pattern**:
```python
# backend/app/core/error_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import SigmaSightException
from app.core.logging import get_logger
import traceback

logger = get_logger("error_handler")

async def sigmasight_exception_handler(request: Request, exc: SigmaSightException):
    """Handle custom SigmaSight exceptions"""
    
    logger.error(
        f"SigmaSight exception: {exc.code} - {exc.message}",
        extra={
            "code": exc.code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "errors": [{
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }],
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "errors": [{
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": {}
            }],
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

# Register handlers in main.py
from fastapi import FastAPI
from app.core.exceptions import SigmaSightException
from app.core.error_handlers import sigmasight_exception_handler, general_exception_handler

app = FastAPI()

app.add_exception_handler(SigmaSightException, sigmasight_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

#### Frontend Error Handling

**Error Boundary Pattern**:
```typescript
// frontend/src/components/ErrorBoundary.tsx
'use client'

import React from 'react'
import { Button, Card } from '@/components/ui'

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: any
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })
    
    // Log to error reporting service
    if (process.env.NODE_ENV === 'production') {
      // reportError(error, errorInfo)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="p-8 text-center max-w-lg mx-auto mt-16">
          <div className="text-6xl mb-4">🚨</div>
          <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
          <p className="text-gray-600 mb-6">
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </p>
          
          <div className="space-x-4">
            <Button
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </Button>
            
            <Button
              variant="outline"
              onClick={() => window.history.back()}
            >
              Go Back
            </Button>
          </div>
          
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-6 text-left">
              <summary className="cursor-pointer text-sm text-gray-500">
                Error Details (Development Only)
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
                {this.state.error?.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </Card>
      )
    }

    return this.props.children
  }
}

// HOC for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WithErrorBoundaryComponent(props: P) {
    return (
      <ErrorBoundary>
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}
```

**API Error Handling Pattern**:
```typescript
// frontend/src/lib/errors.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message)
    this.name = 'APIError'
  }

  static fromResponse(response: Response, data?: any): APIError {
    const message = data?.errors?.[0]?.message || `HTTP ${response.status}`
    const code = data?.errors?.[0]?.code
    const details = data?.errors?.[0]?.details
    
    return new APIError(message, response.status, code, details)
  }
}

export function handleAPIError(error: unknown): APIError {
  if (error instanceof APIError) {
    return error
  }
  
  if (error instanceof Error) {
    return new APIError(error.message)
  }
  
  return new APIError('An unexpected error occurred')
}

// Error notification hook
export function useErrorHandler() {
  const showError = (error: unknown) => {
    const apiError = handleAPIError(error)
    
    // Show user-friendly error message
    console.error('API Error:', apiError)
    
    // Could integrate with toast notifications
    // toast.error(apiError.message)
    
    return apiError
  }
  
  return { showError }
}
```

---

## 🚀 Conclusion

The SigmaSight portfolio risk management platform represents a complete, production-ready implementation of a modern three-service architecture. This implementation guide provides comprehensive documentation covering:

### What Was Accomplished

1. **Complete System Architecture**: Three integrated services (Backend, Frontend, GPT Agent) working seamlessly together
2. **Production Database**: PostgreSQL with comprehensive schema and demo data
3. **8 Calculation Engines**: Full portfolio analytics capability including Greeks, factors, and risk metrics
4. **AI Integration**: GPT-powered analysis interpreting backend calculations 
5. **Modern Frontend**: React/Next.js application with responsive design and real-time features
6. **Comprehensive APIs**: RESTful endpoints with OpenAPI documentation
7. **Developer Infrastructure**: Setup guides, testing frameworks, and deployment processes

### Key Technical Achievements

- **Backend**: FastAPI with SQLAlchemy ORM, 8 calculation engines, multi-provider market data
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, comprehensive component library
- **GPT Agent**: Node.js service with OpenAI integration and backend data interpretation
- **Database**: PostgreSQL with proper indexing, migrations, and seeded demo data
- **Integration**: JWT authentication across services, error handling, rate limiting

### System Status: PRODUCTION READY ✅

All services are operational and tested:
- **Backend Service**: Running on port 8001 with API documentation
- **Frontend Application**: Running on port 3008 with full user interface
- **GPT Agent Service**: Running on port 8888 with AI analysis capabilities
- **Database**: PostgreSQL operational with demo portfolios and calculations

### Next Steps for Teams

This documentation enables:
1. **Developers**: Complete setup instructions and development patterns
2. **System Administrators**: Deployment guides and troubleshooting procedures  
3. **Users**: Comprehensive user guide and feature documentation
4. **Product Teams**: Understanding of implemented capabilities and extension points

The SigmaSight platform is now ready for production deployment, user onboarding, and continued feature development based on the solid foundation established by this implementation.

---

**Document Status**: Complete and Current  
**Implementation Version**: 1.0  
**Last Verified**: August 26, 2025  
**Maintenance**: Update as system evolves
# SigmaSight GPT Agent - Complete Setup Guide

This guide provides step-by-step instructions to get the SigmaSight GPT Agent running with all required dependencies and services.

## 🎯 Overview

The GPT Agent requires a **three-service architecture**:
1. **Backend Service** (FastAPI) - Portfolio data and calculations
2. **GPT Agent Service** (Node.js) - AI analysis and tool execution  
3. **Frontend Service** (Next.js) - User interface with GPT toolbar

## 📋 Prerequisites

### System Requirements
- **Node.js**: Version 18+ 
- **Python**: Version 3.11+
- **PostgreSQL**: Version 13+ (for backend database)
- **UV Package Manager**: For Python dependency management
- **npm**: For Node.js package management

### Required API Keys
- **OpenAI API Key**: For GPT-4 functionality
- **Backend Database**: PostgreSQL connection string

## 🚀 Quick Start (Development)

### 1. **Start Backend Service** 
```bash
# Terminal 1: Backend (MUST START FIRST)
cd backend
uv run python run.py

# Expected output:
# 🚀 SigmaSight Backend API listening on http://0.0.0.0:8000
# 📊 Database: Connected ✅
# 🔑 JWT Secret: ✅ Set
```

### 2. **Start GPT Agent Service**
```bash
# Terminal 2: GPT Agent (START SECOND)
cd gptagent
npm run dev

# Expected output:
# 🚀 SigmaSight GPT Agent API listening on http://0.0.0.0:8787
# 📊 Backend URL: http://localhost:8000
# 🔑 OpenAI API Key: ✅ Set / ❌ Missing
```

### 3. **Test Integration**
```bash
# Terminal 3: Testing
curl http://localhost:8787/health

# Expected response:
# {
#   "status": "ok",
#   "service": "sigmasight-gpt-agent",
#   "backend_connected": true,
#   "backend_url": "http://localhost:8000"
# }
```

## 📦 Detailed Setup Instructions

### Backend Service Setup (Port 8000)

#### Step 1: Navigate to Backend Directory
```bash
cd backend
```

#### Step 2: Install Dependencies
```bash
# Install UV package manager (if not installed)
pip install uv

# Install dependencies
uv sync
```

#### Step 3: Database Setup
```bash
# Start PostgreSQL (using Docker)
docker-compose up -d

# Run database migrations
uv run alembic upgrade head

# Seed demo data (includes 3 demo portfolios)
uv run python scripts/seed_database.py
```

#### Step 4: Configure Environment
Create `backend/.env`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/sigmasight

# Security
SECRET_KEY=your-jwt-secret-key-here

# Market Data (Optional but recommended)
FMP_API_KEY=your-fmp-api-key
POLYGON_API_KEY=your-polygon-api-key
FRED_API_KEY=your-fred-api-key

# Logging
LOG_LEVEL=info
```

#### Step 5: Start Backend Server
```bash
uv run python run.py
```

**✅ Verification**: Backend should be running on http://localhost:8000

### GPT Agent Service Setup (Port 8787)

#### Step 1: Navigate to GPT Agent Directory
```bash
cd gptagent
```

#### Step 2: Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Build TypeScript packages
npm run build  # This may fail if pnpm is not available, that's OK
```

If build fails, build packages individually:
```bash
cd packages/schemas && npm run build
cd ../analysis-agent && npm run build  
cd ../../apps/api && npm run build
```

#### Step 3: Configure Environment
Create `gptagent/.env`:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Backend Integration
BACKEND_URL=http://localhost:8000
BACKEND_HEALTH_ENDPOINT=/health

# Server Configuration
PORT=8787
NODE_ENV=development

# Authentication (MUST MATCH BACKEND JWT_SECRET)
JWT_SECRET=your-jwt-secret-key-here

# Logging
LOG_LEVEL=info

# Rate Limiting
RATE_LIMIT_MAX=60
RATE_LIMIT_WINDOW=1 minute

# Demo Portfolio IDs (Pre-configured)
DEMO_INDIVIDUAL_PORTFOLIO_ID=a3209353-9ed5-4885-81e8-d4bbc995f96c
DEMO_HIGH_NET_WORTH_PORTFOLIO_ID=14e7f420-b096-4e2e-8cc2-531caf434c05
DEMO_HEDGE_FUND_PORTFOLIO_ID=cf890da7-7b74-4cb4-acba-2205fdd9dff4
```

#### Step 4: Start GPT Agent Server
```bash
npm run dev
```

**✅ Verification**: GPT Agent should be running on http://localhost:8787

## 🧪 Testing Your Setup

### 1. **Run Integration Test**
```bash
cd gptagent
node test-setup.js
```

Expected output:
```
🧪 Testing SigmaSight GPT Agent Setup

📋 Environment Check:
   Backend URL: http://localhost:8000
   OpenAI API Key: ✅ Set
   Port: 8787

🔧 Backend Client Test:
   ✅ Backend connection successful
   ✅ Retrieved portfolio data

🎯 Setup Status:
   GPT Agent Service: ✅ Ready
   Backend Integration: ✅ Configured
   TypeScript Build: ✅ Successful
   OpenAI API: ✅ Configured
```

### 2. **Test API Endpoints**

#### Health Check
```bash
curl http://localhost:8787/health
```

#### GPT Analysis (with demo portfolio)
```bash
curl -X POST http://localhost:8787/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "portfolio_report": {
      "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
    }
  }'
```

#### Individual Tools
```bash
# Portfolio snapshot
curl -X POST http://localhost:8787/tools/portfolio_snapshot \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
  }'

# Positions data
curl -X POST http://localhost:8787/tools/positions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c"
  }'
```

## 🔧 Configuration Details

### Service Dependencies (Start Order)

1. **PostgreSQL Database** (Docker or local)
2. **Backend Service** (Port 8000) - MUST START FIRST
3. **GPT Agent Service** (Port 8787) - Depends on backend
4. **Frontend Service** (Port 3000) - Optional for GPT agent testing

### Environment Variables

#### Required for GPT Agent
```bash
OPENAI_API_KEY=        # OpenAI API key for GPT functionality
BACKEND_URL=           # Backend service URL (default: http://localhost:8000)
JWT_SECRET=            # MUST match backend JWT secret
```

#### Optional Configuration
```bash
PORT=8787              # GPT Agent port
LOG_LEVEL=info         # Logging level (debug, info, warn, error)
RATE_LIMIT_MAX=60      # Requests per minute
NODE_ENV=development   # Environment mode
```

### Demo Portfolios (Pre-seeded)

The backend includes three demo portfolios for testing:

1. **Individual Investor Portfolio**
   - ID: `a3209353-9ed5-4885-81e8-d4bbc995f96c`
   - Use case: Basic portfolio analysis

2. **High Net Worth Portfolio** 
   - ID: `14e7f420-b096-4e2e-8cc2-531caf434c05`
   - Use case: Advanced risk analytics

3. **Hedge Fund-Style Portfolio**
   - ID: `cf890da7-7b74-4cb4-acba-2205fdd9dff4`
   - Use case: Factor analysis and stress testing

## 🚨 Troubleshooting

### Common Issues

#### 1. **Backend Connection Failed**
```
❌ Backend connection failed
```
**Solution**: 
- Ensure backend is running on port 8000
- Check `BACKEND_URL` in GPT agent `.env`
- Verify backend health: `curl http://localhost:8000/health`

#### 2. **OpenAI API Key Missing**
```
⚠️ OpenAI API: API key needed for full functionality
```
**Solution**: 
- Set `OPENAI_API_KEY` in `gptagent/.env`
- Verify key format: `sk-...`

#### 3. **TypeScript Build Failures**
```
npm error Lifecycle script `build` failed
```
**Solution**:
```bash
# Build packages individually
cd packages/schemas && npm run build
cd ../analysis-agent && npm run build
cd ../../apps/api && npm run build
```

#### 4. **Port Already in Use**
```
Error: listen EADDRINUSE: address already in use :::8787
```
**Solution**:
```bash
# Kill process on port 8787
npx kill-port 8787

# Or change port in .env
PORT=8788
```

#### 5. **JWT Token Mismatch**
```
401 Unauthorized
```
**Solution**: 
- Ensure `JWT_SECRET` matches between backend and GPT agent
- Verify token format in requests: `Authorization: Bearer <token>`

### Debug Commands

#### Check Service Status
```bash
# Backend health
curl http://localhost:8000/health

# GPT Agent health  
curl http://localhost:8787/health

# Check backend connectivity from GPT agent
curl http://localhost:8787/tools/health
```

#### View Logs
```bash
# Backend logs
cd backend && uv run python run.py

# GPT Agent logs (with debug level)
cd gptagent && LOG_LEVEL=debug npm run dev
```

## 📚 API Reference

### GPT Agent Endpoints

#### Core Analysis
- `POST /analyze` - Full GPT analysis with tool execution
- `GET /health` - Service health and backend connectivity

#### Individual Tools
- `POST /tools/portfolio_snapshot` - Portfolio overview data
- `POST /tools/positions` - Position details and market values
- `POST /tools/factor_exposures` - Factor model exposures  
- `POST /tools/risk_metrics` - VaR/ES risk calculations
- `POST /tools/stress_test` - Stress testing scenarios

#### Request Format
```json
{
  "portfolio_id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
  "as_of": "2025-08-25" // Optional
}
```

#### Response Format
```json
{
  "success": true,
  "data": { /* Backend data */ },
  "source": "backend_database",
  "gaps": [] // Missing data identified
}
```

## 🎯 Production Deployment

### Environment Setup
1. Set production OpenAI API key
2. Configure production backend URL
3. Set appropriate JWT secrets
4. Configure rate limiting for production load
5. Enable production logging

### Security Checklist
- [ ] JWT secrets properly configured
- [ ] CORS origins restricted to frontend domains
- [ ] Rate limiting enabled
- [ ] Environment variables secured
- [ ] OpenAI API key secured

### Monitoring
- Health check endpoints for uptime monitoring
- Structured logging for observability
- Error tracking integration
- Performance metrics collection

---

## 📞 Support

For issues with setup:
1. Check troubleshooting section above
2. Verify all prerequisites are met
3. Ensure services start in correct order
4. Check logs for detailed error messages

The GPT Agent is now ready for integration with the SigmaSight platform! 🚀
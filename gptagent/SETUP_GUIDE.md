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

### 🎯 Two Setup Options Available:

#### **Option A: Direct ChatGPT Integration (Recommended for Quick Setup)**
✅ **Fastest setup** - Bypass GPT agent service complexities  
✅ **Production-ready** - Real OpenAI API with portfolio data  
✅ **Windows-compatible** - No build issues or dependency conflicts  

#### **Option B: Full GPT Agent Service (Advanced Setup)**
🔧 **Complete architecture** - Full three-service integration  
⚠️ **Windows complexity** - Requires individual package builds  
🛠️ **Development focus** - For GPT agent service development  

---

### ⚡ **Option A: Direct ChatGPT Integration Setup**

**Perfect for**: Quick testing, immediate functionality, production demos

```bash
# Terminal 1: Start Backend (REQUIRED)
cd backend
uv run python run.py  # Port 8000

# Terminal 2: Start Frontend with Direct Integration
cd frontend
PORT=4003 OPENAI_API_KEY="sk-proj-your-key-here" npm run dev  # Port 4003

# 🎉 Ready! Visit: http://localhost:4003/chat
```

**What you get:**
- ✅ Real-time chat interface with GPT-4o-mini
- ✅ Actual portfolio data integration from backend
- ✅ Professional portfolio analysis and insights
- ✅ No complex service dependencies

---

### ⚙️ **Option B: Full GPT Agent Service Setup**

**Perfect for**: GPT agent development, service architecture testing

#### ⚠️ Windows Users - Read This First!

If you're on Windows, the standard `npm run dev` from root **will fail** because it requires `pnpm`. Follow these steps instead:

1. **Build packages individually** (required first-time setup)
2. **Start from API directory** (not root)
3. **Install dependencies in each package**

See "Full GPT Agent Service Setup" section below for detailed steps.

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

# IMPORTANT: If using Windows, build packages individually first:
cd packages/schemas && npm run build
cd ../analysis-agent && npm run build
cd ../../apps/api

# Then start the service:
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

### **Option A: Direct ChatGPT Integration - Complete Guide**

This approach bypasses the GPT agent service and connects the frontend directly to OpenAI's API while pulling real portfolio data from the SigmaSight backend.

#### Prerequisites
- Backend service running (PostgreSQL + FastAPI)
- OpenAI API key (`sk-proj-...` format)
- Node.js 18+ for frontend

#### Step-by-Step Setup

##### 1. Backend Service (Same as Option B)
```bash
cd backend

# Start database
docker-compose up -d

# Start backend API
uv run python run.py  # Port 8000
```

##### 2. Frontend Service with Direct Integration
```bash
cd frontend

# Install dependencies (if needed)
npm install

# Set environment variables and start
export OPENAI_API_KEY="sk-proj-your-openai-api-key-here"
export PORT=4003
npm run dev

# OR in one command:
PORT=4003 OPENAI_API_KEY="sk-proj-your-key-here" npm run dev
```

##### 3. Verify Setup
```bash
# Test frontend
curl http://localhost:4003

# Test GPT integration
curl -X POST http://localhost:4003/api/gpt/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my portfolio risk profile?"}'
```

#### How It Works
1. **Frontend** (`localhost:4003/chat`) - Clean chat interface
2. **API Route** (`/api/gpt/analyze`) - Fetches portfolio data from backend
3. **OpenAI API** - Processes portfolio context + user question
4. **Response** - Real portfolio insights with GPT analysis

#### Advantages of Direct Integration
- ✅ **No build complexity** - Standard Next.js setup
- ✅ **Real portfolio data** - Live backend integration
- ✅ **Production OpenAI** - gpt-4o-mini model
- ✅ **Windows compatible** - No pnpm/build issues
- ✅ **Fast iteration** - Direct API calls, easy debugging
- ✅ **Immediate results** - Working chat in minutes

---

### **Option B: Full GPT Agent Service Setup**

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
# Install Node.js dependencies in root
npm install

# Install dependencies in API directory
cd apps/api && npm install
cd ../..

# Install dependencies in packages
cd packages/schemas && npm install
cd ../analysis-agent && npm install
cd ../..

# Build TypeScript packages (REQUIRED STEP)
npm run build  # This will fail if pnpm is not available
```

**⚠️ IMPORTANT**: If build fails (common on Windows), build packages individually:
```bash
# Build packages in correct order
cd packages/schemas && npm run build
cd ../analysis-agent && npm run build
cd ../../apps/api && npm run build
cd ..
```

#### Step 3: Configure Environment
Create `gptagent/.env`:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

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
# Option 1: From root directory (may fail without pnpm)
npm run dev

# Option 2: Direct from API directory (RECOMMENDED for Windows)
cd apps/api
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
- Verify key format: `sk-proj-...` or `sk-...`

#### 3. **TypeScript Build Failures (MOST COMMON)**
```
npm error Lifecycle script `build` failed
'pnpm' is not recognized as an internal or external command
```
**Root Cause**: The project uses `pnpm` but most systems have `npm` installed.

**Solution (REQUIRED for Windows)**:
```bash
# Build packages individually in correct order
cd packages/schemas && npm install && npm run build
cd ../analysis-agent && npm install && npm run build
cd ../../apps/api && npm install
```

#### 4. **Service Won't Start After Build**
```
npm error Lifecycle script `dev` failed
```
**Solution**: Start from API directory directly:
```bash
cd apps/api
npm run dev
```

#### 5. **Port Already in Use**
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

#### 6. **JWT Token Mismatch**
```
401 Unauthorized
```
**Solution**: 
- Ensure `JWT_SECRET` matches between backend and GPT agent
- Verify token format in requests: `Authorization: Bearer <token>`

#### 7. **Windows PowerShell Command Hanging**
**Issue**: Commands hang or don't complete on Windows PowerShell

**Solution**: 
- Use individual commands instead of chained commands
- Navigate to specific directories before running commands
- Use `cd apps/api` then `npm run dev` instead of root-level scripts

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
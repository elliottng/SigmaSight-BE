# 🎨 Frontend Setup Guide for SigmaSight

This guide covers setting up and running the Next.js frontend with user-based authentication, personalized portfolio dashboards, and flexible GPT integration.

## 📋 Overview

- **Frontend**: Next.js 15.2.4 with TypeScript + Tailwind CSS
- **Backend**: FastAPI at `http://localhost:8000` 
- **Frontend URL**: `http://localhost:4003` (updated port)
- **Architecture**: User-based authentication with personalized portfolio access
- **GPT Integration**: Flexible direct/agent mode with portfolio context
- **Authentication**: Demo users with secure login flow

## ✨ New Features (Session 5)

### 🔐 User Authentication System
- **Demo User Profiles**: 3 distinct investor types (Individual, High Net Worth, Hedge Fund)
- **Secure Login**: Backend authentication with demo mode fallback
- **Personalized Dashboards**: User-specific portfolio access and analytics
- **Session Management**: Secure token storage and user context

### 🤖 Flexible GPT Integration
- **Dual Mode Support**: Direct OpenAI integration (current) + GPT Agent (future)
- **Portfolio Context**: Real-time portfolio data injection into GPT prompts
- **User-Specific Analysis**: GPT responses tailored to user's investment profile
- **Environment Switching**: Easy toggle between integration modes

### 📊 Enhanced Portfolio Analytics
- **User-Specific Data**: Each user sees only their portfolio
- **Real-Time Analytics**: Factor exposures, risk metrics, attribution analysis
- **Interactive Visualizations**: Dynamic charts and data displays
- **Comprehensive Context**: Full portfolio context for GPT analysis

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18.0.0 or higher) - Download from https://nodejs.org/
- **npm** (comes with Node.js) - Verify: `npm --version`
- **Backend server running** on http://localhost:8000 (see backend setup guides)
- **OpenAI API Key** (optional, for GPT integration)

### 1. Navigate to Frontend Directory

```bash
# From project root
cd frontend
```

### 2. Install Frontend Dependencies

```bash
npm install
```

*This creates `node_modules/` directory with all required packages (not committed to git)*

### 3. Start Development Servers

**Terminal 1 - Backend:**
```bash
# From project root
cd backend
uv run python run.py
```

**Terminal 2 - Frontend:**
```bash  
# From project root
cd frontend
PORT=4003 npm run dev

# Optional: Set OpenAI API key for GPT integration
PORT=4003 OPENAI_API_KEY="sk-proj-your-key-here" npm run dev
```

### 4. Access Applications

- **Frontend**: http://localhost:4003 (main application)
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. User Login & Demo Accounts

**Demo Users Available:**
| User Type | Email | Password | Portfolio Focus |
|-----------|--------|----------|----------------|
| **Individual Investor** | `demo_individual@sigmasight.com` | `demo12345` | Diversified ETFs & stocks |
| **High Net Worth** | `demo_hnw@sigmasight.com` | `demo12345` | Advanced strategies |
| **Hedge Fund Manager** | `demo_hedgefundstyle@sigmasight.com` | `demo12345` | Long/short complex |

**Usage Flow:**
1. Visit http://localhost:4003
2. Click "Login to Your Portfolio"
3. Select a demo user profile
4. Use password `demo12345`
5. Access personalized dashboard and portfolio analytics

## 🔗 API Integration

### Current API Endpoints

The frontend integrates with these backend and internal APIs:

**Backend APIs:**
- **Portfolio Reports**: `GET /api/v1/reports/portfolios`
- **Report Content**: `GET /api/v1/reports/portfolio/{id}/content/{format}`
- **Authentication**: `POST /api/v1/auth/login`
- **Health Check**: `GET /health`
- **API Base**: `http://localhost:8000`

**Internal APIs (Frontend):**
- **Authentication**: `POST /api/auth/login`
- **GPT Analysis**: `POST /api/gpt/analyze`
- **GPT Health**: `GET /api/gpt/health`

### Implemented Features

✅ **User Authentication System**
- Demo user profile selection with distinct investor types
- Secure login with backend integration and demo mode fallback
- Session management with JWT tokens and user context
- Automatic redirection to personalized dashboards

✅ **User-Specific Portfolio Dashboard**
- Personalized welcome and user profile integration
- User-specific portfolio access (no cross-user data leakage)
- Professional navigation with logout functionality
- Feature roadmap with current/future capabilities

✅ **Comprehensive Portfolio Analytics**
- Real-time portfolio data from backend reports API
- Interactive factor exposure visualizations
- Risk metrics display (VaR, Expected Shortfall)
- Performance attribution analysis
- Date range controls and portfolio context

✅ **Flexible GPT Integration**
- Dual-mode architecture (direct OpenAI + GPT Agent)
- Portfolio context injection with real backend data
- User-specific GPT analysis and recommendations
- Fallback handling and error recovery

✅ **Enhanced User Experience**
- Backend connectivity monitoring with health checks
- Professional UI design suitable for financial professionals
- Responsive design for desktop and mobile
- Loading states and error handling throughout

### Example Usage

```typescript
// User Authentication
import { useRouter } from 'next/router';

const handleLogin = async (email: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
};

// GPT Integration with Portfolio Context
import { useGPTService } from '@/hooks/useGPTService';

const { analyzePortfolio, isLoading } = useGPTService({ 
  mode: 'direct', 
  defaultPortfolioId: user.portfolioId 
});

const analysis = await analyzePortfolio(
  portfolioId, 
  "Analyze my portfolio's risk profile and factor exposures"
);

// Portfolio Context Integration
import { usePortfolioContext } from '@/hooks/usePortfolioContext';

const {
  summary,
  attribution, 
  factors,
  generateContextString
} = usePortfolioContext(portfolioId);

const contextForGPT = generateContextString();
```

### Environment Variables

The frontend supports these environment variables:

```bash
# GPT Integration (optional)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Backend URL (defaults to localhost:8000)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# GPT Service Mode (defaults to 'direct')
NEXT_PUBLIC_GPT_MODE=direct  # or 'agent'
```

### CORS Configuration

CORS is configured in the FastAPI backend to allow:
- `http://localhost:4003` (Next.js dev server - current)
- `http://localhost:3000` and `http://localhost:3001` (alternate ports)
- Production domains

## 📁 Project Structure

```
SigmaSight/
├── backend/                    # FastAPI backend
│   ├── app/                   # FastAPI application
│   ├── setup-guides/          # Backend setup documentation
│   └── ...
├── frontend/                   # Next.js frontend
│   ├── pages/                 # Next.js Pages Router
│   │   ├── api/              # API routes
│   │   │   ├── auth/         # Authentication endpoints
│   │   │   │   └── login.ts  # Login API with demo fallback
│   │   │   └── gpt/          # GPT integration endpoints
│   │   │       ├── analyze.ts # GPT analysis with portfolio context
│   │   │       └── health.ts # GPT service health check
│   │   ├── portfolio/        # Portfolio pages
│   │   │   └── [id].tsx     # Dynamic portfolio dashboard
│   │   ├── chat.tsx          # GPT chat interface
│   │   ├── dashboard.tsx     # User-specific dashboard
│   │   ├── login.tsx         # User authentication page
│   │   └── index.tsx         # Homepage with user profiles
│   ├── src/
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useGPTService.ts      # Flexible GPT integration
│   │   │   └── usePortfolioContext.ts # Portfolio data management
│   │   └── types/            # TypeScript definitions
│   │       └── portfolio.ts  # Portfolio and user types
│   ├── docs/                 # Frontend documentation
│   ├── package.json          # Dependencies (commit this)
│   ├── package-lock.json     # Lock file (commit this)
│   ├── next.config.js        # Next.js config
│   └── tailwind.config.ts    # Tailwind config
└── changelogs/                # Change documentation
    └── FRONTEND_CHANGELOG.md  # Updated with Session 5 changes
```

**Important**: `node_modules/` and `.next/` are not committed to git and must be generated locally.

## 🛠️ Development Workflow

### Frontend Commands

```powershell
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Backend Commands

```powershell
# Start backend server
uv run python run.py

# Run with specific environment
$env:ENVIRONMENT="development"; uv run python run.py

# Database migrations
uv run alembic upgrade head

# Seed demo data
$env:PYTHONIOENCODING="utf-8"; uv run python scripts/setup_minimal_demo.py
```

## 🔧 Configuration

### Environment Variables

The backend uses environment variables from `.env`:
- `DATABASE_URL`: PostgreSQL connection
- `POLYGON_API_KEY`: Market data API key
- `FMP_API_KEY`: Financial data API key
- `SECRET_KEY`: JWT secret key

### Frontend Configuration

Next.js configuration is in `next.config.js`:
- TypeScript support enabled
- Tailwind CSS configured
- API proxy settings (if needed)

## 🚨 Troubleshooting

### Frontend Won't Start
- Check Node.js version: `node --version`
- Install dependencies: `npm install`
- Clear cache: `npm cache clean --force`

### API Calls Failing
- Ensure backend is running on port 8000
- Check CORS configuration in `app/config.py`
- Verify API endpoints in FastAPI docs: http://localhost:8000/docs

### Port Conflicts
- Frontend default: 3000 (Next.js will auto-increment if busy)
- Backend default: 8000
- Change ports in respective config files if needed

## 📝 Daily Development

1. **Start backend**: `cd backend && uv run python run.py`
2. **Start frontend**: `cd frontend && PORT=4003 npm run dev`
3. **Access frontend**: http://localhost:4003
4. **View API docs**: http://localhost:8000/docs
5. **Login**: Use any demo user with password `demo12345`

### Quick Demo Flow
1. **Homepage**: http://localhost:4003 → Click "Login to Your Portfolio"
2. **Login**: Select "Demo Individual Investor" → Use password `demo12345`  
3. **Dashboard**: Personalized user dashboard → Click "Portfolio Dashboard"
4. **Analytics**: View portfolio analytics → Click "AI Portfolio Assistant"
5. **Chat**: GPT analysis with full portfolio context

## 🔄 Git Workflow

Both frontend and backend are tracked in the same repository:
- Work on `frontendtest` branch for frontend changes
- Commit both frontend and backend changes together
- Push to GitHub: `git push origin frontendtest`

## 📞 Need Help?

- Check FastAPI docs: http://localhost:8000/docs
- Review Next.js documentation: https://nextjs.org/docs
- Check console logs in browser developer tools
- Review backend logs in terminal

---

## 💡 Tips

- Use browser developer tools to debug API calls
- Check Network tab for failed requests
- Backend logs show detailed error information
- Both servers support hot reload for development

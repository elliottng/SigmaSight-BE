# 🎨 Frontend Setup Guide for SigmaSight

This guide covers setting up and running the Next.js frontend with integrated portfolio dashboard and backend API connectivity.

## 📋 Overview

- **Frontend**: Next.js 15.2.4 with TypeScript + Tailwind CSS
- **Backend**: FastAPI at `http://localhost:8000` 
- **Frontend URL**: `http://localhost:3001` (updated port to avoid conflicts)
- **Integration**: CORS configured, Portfolio Reports API integrated

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18.0.0 or higher) - Download from https://nodejs.org/
- **npm** (comes with Node.js) - Verify: `npm --version`
- **Backend server running** on http://localhost:8000 (see backend setup guides)

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
npm run dev
```

### 4. Access Applications

- **Frontend Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔗 API Integration

### Current API Endpoints

The frontend integrates with these backend APIs:
- **Portfolio Reports**: `GET /api/v1/reports/portfolios`
- **Report Content**: `GET /api/v1/reports/portfolio/{id}/content/{format}`
- **Health Check**: `GET /health`
- **API Base**: `http://localhost:8000`

### Implemented Features

✅ **Portfolio Dashboard**
- Real-time portfolio listing from backend
- Portfolio metrics and metadata display
- Connection status monitoring

✅ **Report Viewer**
- Multi-format report display (JSON, CSV, MD)
- Interactive format switching
- Navigation between dashboard and reports

✅ **API Client**
- Centralized API calling in `src/lib/api.ts`
- Error handling and loading states
- CORS properly configured for localhost:3001

### Example Usage

```typescript
// Portfolio fetching (implemented)
import { fetchPortfolios } from '@/lib/api';

const portfolios = await fetchPortfolios();
// Returns: Portfolio[] with id, name, formats_available, etc.

// Report content fetching (implemented)
import { fetchReportContent } from '@/lib/api';

const content = await fetchReportContent(portfolioId, 'json');
// Returns: string with report content
```

### CORS Configuration

CORS is configured in the FastAPI backend to allow:
- `http://localhost:3001` (Next.js dev server - current)
- `http://localhost:3000` (alternate port)
- Production domains

## 📁 Project Structure

```
SigmaSight/
├── backend/                    # FastAPI backend
│   ├── app/                   # FastAPI application
│   ├── setup-guides/          # Backend setup documentation
│   └── ...
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   │   ├── globals.css   # Global styles
│   │   │   ├── layout.tsx    # Root layout
│   │   │   └── page.tsx      # Dashboard page
│   │   ├── components/       # React components
│   │   │   ├── ui/           # Basic UI components
│   │   │   └── layout/       # Layout components
│   │   ├── lib/              # Utilities
│   │   │   ├── api.ts        # Backend API client
│   │   │   └── utils.ts      # Helper functions
│   │   ├── hooks/            # Custom React hooks
│   │   └── types/            # TypeScript definitions
│   ├── docs/                 # Frontend documentation
│   ├── package.json          # Dependencies (commit this)
│   ├── package-lock.json     # Lock file (commit this)
│   ├── next.config.js        # Next.js config
│   └── tailwind.config.ts    # Tailwind config
└── changelogs/                # Change documentation
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

1. **Start backend**: `uv run python run.py`
2. **Start frontend**: `npm run dev`
3. **Access frontend**: http://localhost:3000
4. **View API docs**: http://localhost:8000/docs

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

# 🎨 Frontend Setup Guide for SigmaSight

This guide covers setting up and running the React frontend with the FastAPI backend.

## 📋 Overview

- **Frontend**: Next.js with TypeScript + Tailwind CSS
- **Backend**: FastAPI at `http://localhost:8000`
- **Frontend URL**: `http://localhost:3000`
- **Integration**: CORS already configured

## 🚀 Quick Start

### Prerequisites
- Node.js installed (v18 or higher)
- Backend already running (see Windows Setup Guide)

### 1. Install Frontend Dependencies

```powershell
cd C:\Users\BenBalbale\CascadeProjects\SigmaSight-BE\sigmasight-backend\frontend
npm install
```

### 2. Start Development Servers

**Terminal 1 - Backend:**
```powershell
cd C:\Users\BenBalbale\CascadeProjects\SigmaSight-BE\sigmasight-backend
uv run python run.py
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\BenBalbale\CascadeProjects\SigmaSight-BE\sigmasight-backend\frontend
npm run dev
```

### 3. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔗 API Integration

### Base Configuration

Your React frontend can make API calls to:
- **Base URL**: `http://localhost:8000`
- **API Endpoints**: `http://localhost:8000/api/*`
- **Health Check**: `http://localhost:8000/health`

### Example API Call

```typescript
// Example API call in your React components
const fetchData = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/portfolios');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
  }
};
```

### CORS Configuration

CORS is already configured in the FastAPI backend to allow:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- Production domains

## 📁 Project Structure

```
sigmasight-backend/
├── app/                    # FastAPI backend
├── frontend/              # Next.js React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── types/         # TypeScript types
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.ts
└── docs/                  # Documentation
```

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

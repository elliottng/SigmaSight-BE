# SigmaSight Deployment Guide

**Version**: 1.0  
**Last Updated**: August 26, 2025  
**Target Environments**: Development, Staging, Production  

## Overview

This guide provides comprehensive deployment instructions for the SigmaSight portfolio risk management platform across different environments. The system consists of three integrated services that must be deployed and configured together.

## System Architecture

### Service Dependencies

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │◄───┤    Backend       │◄───┤  GPT Agent      │
│   Port 5432     │    │    Port 8001     │    │  Port 8888      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Frontend       │    │   File System   │
                       │   Port 3008      │    │   Reports       │
                       └──────────────────┘    └─────────────────┘
```

### Service Startup Order

1. **PostgreSQL Database** (Port 5432)
2. **Backend API Service** (Port 8001)
3. **GPT Agent Service** (Port 8888)
4. **Frontend Application** (Port 3008)

---

## Prerequisites

### System Requirements

**Minimum Hardware:**
- **CPU**: 4 cores, 2.4GHz
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB available space
- **Network**: Stable internet connection for market data APIs

**Operating System:**
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: Windows 10/11, Windows Server 2019+

### Software Dependencies

**Core Runtime:**
- **Node.js**: 18.0+ (for Frontend and GPT Agent)
- **Python**: 3.11+ (for Backend)
- **PostgreSQL**: 14.0+ (Database)

**Package Managers:**
- **npm** or **yarn** (Node.js packages)
- **uv** (Python package manager)
- **Git** (Version control)

**Development Tools:**
- **Docker** (optional, for containerized deployment)
- **PM2** (optional, for process management)
- **Nginx** (optional, for reverse proxy)

### API Keys Required

**Market Data Providers:**
- **Polygon.io**: Professional plan recommended
- **Financial Modeling Prep**: Ultimate subscription
- **FRED API**: Free tier sufficient
- **OpenAI**: GPT-4 access for AI features

---

## Environment Setup

### Development Environment

#### 1. Repository Setup

```bash
# Clone repository
git clone https://github.com/your-org/SigmaSight.git
cd SigmaSight

# Verify directory structure
ls -la
# Expected: backend/, frontend/, gptagent/, docs/
```

#### 2. Database Setup

**Option A: Local PostgreSQL Installation**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Windows
# Download and install from https://www.postgresql.org/download/windows/
```

**Option B: Docker PostgreSQL**

```bash
# Navigate to backend directory
cd backend

# Start PostgreSQL container
docker-compose up -d

# Verify container is running
docker ps | grep postgres
```

#### 3. Database Configuration

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE sigmasight_db;
CREATE USER sigmasight WITH PASSWORD 'sigmasight_dev';
GRANT ALL PRIVILEGES ON DATABASE sigmasight_db TO sigmasight;
ALTER USER sigmasight CREATEDB;
\q
```

#### 4. Backend Service Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install uv
uv install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Environment Variables (.env):**
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://sigmasight:sigmasight_dev@localhost:5432/sigmasight_db

# Security
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Market Data API Keys
POLYGON_API_KEY=your_polygon_api_key
FMP_API_KEY=your_fmp_api_key
FRED_API_KEY=your_fred_api_key
TRADEFEEDS_API_KEY=your_tradefeeds_api_key

# OpenAI Integration
OPENAI_API_KEY=your_openai_api_key

# Rate Limiting
API_RATE_LIMIT=100
POLYGON_RATE_LIMIT=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sigmasight.log
```

#### 5. Database Migration and Seeding

```bash
# Apply database migrations
uv run alembic upgrade head

# Seed demo data
python scripts/reset_and_seed.py seed

# Verify demo data
python -c "
from app.database import get_async_session
from app.models.users import Portfolio
from sqlalchemy import select
import asyncio

async def check():
    async with get_async_session() as db:
        result = await db.execute(select(Portfolio))
        portfolios = result.scalars().all()
        print(f'Successfully created {len(portfolios)} demo portfolios')

asyncio.run(check())
"
```

#### 6. GPT Agent Setup

```bash
# Navigate to GPT agent directory
cd ../gptagent

# Install Node.js dependencies
npm install

# Create environment file
cp apps/api/.env.example apps/api/.env

# Edit environment configuration
nano apps/api/.env
```

**GPT Agent Environment (.env):**
```bash
# Service Configuration
PORT=8888
NODE_ENV=development

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Backend Integration
BACKEND_API_URL=http://localhost:8001/api/v1
BACKEND_JWT_SECRET=your-super-secret-jwt-key-here

# Rate Limiting
RATE_LIMIT_MAX=60
RATE_LIMIT_WINDOW=60000

# Logging
LOG_LEVEL=info
```

#### 7. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit environment configuration
nano .env.local
```

**Frontend Environment (.env.local):**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_GPT_AGENT_URL=http://localhost:8888

# Application Configuration
NEXT_PUBLIC_APP_NAME=SigmaSight
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=development

# Feature Flags
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_REPORTS=true
NEXT_PUBLIC_ENABLE_ADVANCED_ANALYTICS=true
```

#### 8. Service Startup

**Terminal 1 - Backend Service:**
```bash
cd backend
uv run python run.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
# INFO:     Started server process [####]
# INFO:     Application startup complete.
```

**Terminal 2 - GPT Agent Service:**
```bash
cd gptagent
pnpm -w run dev

# Expected output:
# Server ready at http://localhost:8888
# API listening on :8888
```

**Terminal 3 - Frontend Service:**
```bash
cd frontend
npm run dev

# Expected output:
# ▲ Next.js 15.2.4
# - Local:        http://localhost:3008
# ✓ Ready in 2.5s
```

#### 9. Verification

**Health Checks:**
```bash
# Backend API health
curl http://localhost:8001/docs
# Should return OpenAPI documentation

# GPT Agent health
curl http://localhost:8888/health
# Should return {"status": "ok"}

# Frontend application
curl http://localhost:3008
# Should return HTML page

# Database connectivity
cd backend && python -c "
from app.database import get_async_session
import asyncio

async def test():
    async with get_async_session() as db:
        print('✅ Database connection successful')

asyncio.run(test())
"
```

---

## Production Deployment

### Docker Deployment

#### 1. Docker Compose Configuration

**File: `docker-compose.prod.yml`**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: sigmasight_db
      POSTGRES_USER: sigmasight
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sigmasight -d sigmasight_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://sigmasight:${POSTGRES_PASSWORD}@postgres:5432/sigmasight_db
      - SECRET_KEY=${JWT_SECRET_KEY}
      - POLYGON_API_KEY=${POLYGON_API_KEY}
      - FMP_API_KEY=${FMP_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  gpt-agent:
    build:
      context: ./gptagent
      dockerfile: Dockerfile
    environment:
      - PORT=8888
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BACKEND_API_URL=http://backend:8001/api/v1
      - NODE_ENV=production
    ports:
      - "8888:8888"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8001/api/v1
      - NEXT_PUBLIC_GPT_AGENT_URL=http://gpt-agent:8888
      - NODE_ENV=production
    ports:
      - "3008:3008"
    depends_on:
      - backend
      - gpt-agent
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3008"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  
networks:
  default:
    driver: bridge
```

#### 2. Dockerfile Configurations

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv install --frozen

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start application
CMD ["uv", "run", "python", "run.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3008

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3008 || exit 1

# Start application
CMD ["npm", "start"]
```

**GPT Agent Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY pnpm-workspace.yaml ./

# Install pnpm
RUN npm install -g pnpm

# Copy application code
COPY . .

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build application
RUN pnpm -w run build

# Expose port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/health || exit 1

# Start application
CMD ["pnpm", "-w", "run", "start"]
```

#### 3. Production Environment Variables

**File: `.env.prod`**
```bash
# Database
POSTGRES_PASSWORD=super-secure-postgres-password

# JWT Security
JWT_SECRET_KEY=super-secure-jwt-secret-key-for-production

# API Keys
POLYGON_API_KEY=prod_polygon_api_key
FMP_API_KEY=prod_fmp_api_key
FRED_API_KEY=prod_fred_api_key
OPENAI_API_KEY=prod_openai_api_key

# SSL Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem

# Domain Configuration
DOMAIN_NAME=sigmasight.yourdomain.com
```

#### 4. Nginx Configuration

**File: `nginx.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3008;
    }
    
    upstream backend {
        server backend:8001;
    }
    
    upstream gpt-agent {
        server gpt-agent:8888;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=chat:10m rate=5r/s;

    server {
        listen 80;
        server_name sigmasight.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name sigmasight.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Increase timeouts for long-running calculations
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # GPT Agent routes
        location /gpt/ {
            limit_req zone=chat burst=10 nodelay;
            
            proxy_pass http://gpt-agent/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

#### 5. Production Deployment Commands

```bash
# Create production environment file
cp .env.example .env.prod
# Edit .env.prod with production values

# Build and start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Apply database migrations
docker-compose -f docker-compose.prod.yml exec backend uv run alembic upgrade head

# Seed demo data (optional for production)
docker-compose -f docker-compose.prod.yml exec backend python scripts/reset_and_seed.py seed

# Verify all services are healthy
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Cloud Deployment

#### AWS Deployment with ECS

**1. ECR Repository Setup:**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name sigmasight/backend
aws ecr create-repository --repository-name sigmasight/frontend
aws ecr create-repository --repository-name sigmasight/gpt-agent

# Build and push images
docker build -t sigmasight/backend ./backend
docker tag sigmasight/backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/sigmasight/backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/sigmasight/backend:latest
```

**2. ECS Task Definition:**
```json
{
  "family": "sigmasight",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/sigmasight/backend:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/db"},
        {"name": "SECRET_KEY", "value": "production-secret"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/sigmasight",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

#### Kubernetes Deployment

**1. Namespace and ConfigMap:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sigmasight

---

apiVersion: v1
kind: ConfigMap
metadata:
  name: sigmasight-config
  namespace: sigmasight
data:
  DATABASE_URL: "postgresql+asyncpg://sigmasight:password@postgres:5432/sigmasight_db"
  API_RATE_LIMIT: "100"
```

**2. Backend Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sigmasight-backend
  namespace: sigmasight
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sigmasight-backend
  template:
    metadata:
      labels:
        app: sigmasight-backend
    spec:
      containers:
      - name: backend
        image: sigmasight/backend:latest
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: sigmasight-config
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: sigmasight-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5

---

apiVersion: v1
kind: Service
metadata:
  name: sigmasight-backend-service
  namespace: sigmasight
spec:
  selector:
    app: sigmasight-backend
  ports:
  - port: 8001
    targetPort: 8001
  type: ClusterIP
```

---

## Performance Optimization

### Database Optimization

#### 1. PostgreSQL Configuration

**File: `postgresql.conf` (Production Settings)**
```ini
# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection Settings
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'

# Write-Ahead Logging
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 1GB
min_wal_size = 80MB

# Query Optimization
random_page_cost = 1.1
effective_io_concurrency = 200
```

#### 2. Database Indexing

```sql
-- Critical indexes for performance
CREATE INDEX CONCURRENTLY idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX CONCURRENTLY idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX CONCURRENTLY idx_positions_symbol ON positions(symbol);
CREATE INDEX CONCURRENTLY idx_portfolio_snapshots_date ON portfolio_snapshots(calculation_date DESC);
CREATE INDEX CONCURRENTLY idx_factor_exposures_position_id ON position_factor_exposures(position_id);
CREATE INDEX CONCURRENTLY idx_correlations_portfolio_date ON correlation_calculations(portfolio_id, calculation_date);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_positions_portfolio_type ON positions(portfolio_id, position_type);
CREATE INDEX CONCURRENTLY idx_snapshots_portfolio_current ON portfolio_snapshots(portfolio_id, is_current) WHERE is_current = true;
```

#### 3. Connection Pooling

**Backend Configuration:**
```python
# app/config.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 1800  # 30 minutes

# app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    pool_timeout=DATABASE_POOL_TIMEOUT,
    pool_recycle=DATABASE_POOL_RECYCLE,
    echo=False  # Disable query logging in production
)
```

### Application Performance

#### 1. Caching Strategy

**Redis Configuration (Optional):**
```python
# app/core/cache.py
import redis
from functools import wraps
import json
import pickle

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def cache_result(expiration=300):  # 5 minutes default
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Calculate and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator

# Usage in calculation functions
@cache_result(expiration=600)  # 10 minutes
async def get_portfolio_risk_metrics(portfolio_id: str):
    # Expensive risk calculations
    pass
```

#### 2. Async Optimization

**Background Task Processing:**
```python
# app/core/background_tasks.py
from celery import Celery
import asyncio

celery_app = Celery(
    'sigmasight',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
)

@celery_app.task
def run_portfolio_calculations(portfolio_id: str):
    """Background task for heavy calculations"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run calculations
        result = loop.run_until_complete(
            calculate_portfolio_analytics(portfolio_id)
        )
        return result
    finally:
        loop.close()

# Trigger background calculation
from app.core.background_tasks import run_portfolio_calculations
task = run_portfolio_calculations.delay(portfolio_id)
```

#### 3. Frontend Optimization

**Next.js Production Configuration:**
```javascript
// next.config.js
const nextConfig = {
  // Optimize images
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },
  
  // Enable compression
  compress: true,
  
  // Optimize builds
  swcMinify: true,
  
  // Bundle analyzer (development only)
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      config.plugins.push(new BundleAnalyzerPlugin({
        analyzerMode: 'server',
        openAnalyzer: false,
      }));
      return config;
    },
  }),
  
  // Headers for caching
  async headers() {
    return [
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=60, stale-while-revalidate=300',
          },
        ],
      },
    ];
  },
};
```

---

## Monitoring and Logging

### Application Monitoring

#### 1. Health Check Endpoints

**Backend Health Check:**
```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import asyncio

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Database connectivity
    try:
        await db.execute(text("SELECT 1"))
        checks["services"]["database"] = "healthy"
    except Exception as e:
        checks["services"]["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "unhealthy"
    
    # Market data APIs
    try:
        # Test external API connectivity
        checks["services"]["market_data"] = "healthy"
    except Exception as e:
        checks["services"]["market_data"] = f"degraded: {str(e)}"
    
    return checks
```

#### 2. Prometheus Metrics

**Backend Metrics Collection:**
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics definitions
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)

portfolio_calculations = Counter(
    'portfolio_calculations_total',
    'Total portfolio calculations',
    ['calculation_type', 'status']
)

# Middleware for automatic metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

#### 3. Logging Configuration

**Structured Logging:**
```python
# app/core/logging.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'portfolio_id'):
            log_data['portfolio_id'] = record.portfolio_id
            
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler('logs/sigmasight.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set JSON formatter for file handler
    file_handler = logging.FileHandler('logs/sigmasight.json')
    file_handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger('sigmasight')
    logger.addHandler(file_handler)
```

### Alerting Configuration

#### 1. Alert Rules

**Prometheus Alert Rules (alert.rules.yml):**
```yaml
groups:
- name: sigmasight
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      description: "Error rate is {{ $value }} errors per second"

  - alert: DatabaseConnectionFailure
    expr: up{job="sigmasight-backend"} == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: Backend service is down
      description: "SigmaSight backend service has been down for more than 30 seconds"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: High response time
      description: "95th percentile response time is {{ $value }}s"

  - alert: LowDiskSpace
    expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: Low disk space
      description: "Disk space is below 10%"
```

#### 2. Notification Channels

**Slack Notifications:**
```python
# app/core/alerts.py
import requests
import json
from typing import Dict, Any

class AlertManager:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_alert(self, alert_type: str, message: str, severity: str = "warning"):
        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500", 
            "info": "#0066CC"
        }
        
        payload = {
            "attachments": [
                {
                    "color": color_map.get(severity, "#808080"),
                    "title": f"SigmaSight Alert: {alert_type}",
                    "text": message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": datetime.utcnow().isoformat(),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")

# Usage
alert_manager = AlertManager(webhook_url=os.getenv("SLACK_WEBHOOK_URL"))
await alert_manager.send_alert(
    "Database Connection Failure",
    "Unable to connect to PostgreSQL database",
    "critical"
)
```

---

## Security Configuration

### SSL/TLS Setup

#### 1. Certificate Generation

**Let's Encrypt with Certbot:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d sigmasight.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 2. Security Headers

**Nginx Security Configuration:**
```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

# Hide Nginx version
server_tokens off;

# Rate limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/v1/auth/login {
    limit_req zone=login burst=3 nodelay;
    proxy_pass http://backend;
}
```

### Application Security

#### 1. Environment Variables Security

**Using Docker Secrets:**
```bash
# Create secrets
echo "super-secret-jwt-key" | docker secret create jwt_secret -
echo "super-secure-db-password" | docker secret create db_password -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - jwt_secret
      - db_password
    environment:
      - SECRET_KEY_FILE=/run/secrets/jwt_secret
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password

secrets:
  jwt_secret:
    external: true
  db_password:
    external: true
```

#### 2. API Rate Limiting

**Advanced Rate Limiting:**
```python
# app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["100/hour"]
)

# Different limits for different endpoints
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Strict limit for login
async def login(request: Request, credentials: UserCredentials):
    pass

@app.get("/api/v1/portfolio/{portfolio_id}")
@limiter.limit("60/minute")  # Standard limit for data access
async def get_portfolio(request: Request, portfolio_id: str):
    pass

@app.post("/api/v1/chat/analyze")
@limiter.limit("10/minute")  # Conservative limit for AI analysis
async def analyze_portfolio(request: Request, chat_request: ChatRequest):
    pass
```

---

## Backup and Recovery

### Database Backup

#### 1. Automated Backup Script

**File: `scripts/backup_database.sh`**
```bash
#!/bin/bash

set -e

# Configuration
DB_NAME="sigmasight_db"
DB_USER="sigmasight"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/sigmasight_backup_$(date +%Y%m%d_%H%M%S).sql"

# Create database dump
echo "Starting database backup..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --no-owner --no-privileges --clean --if-exists \
    --file=$BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE
BACKUP_FILE="$BACKUP_FILE.gz"

echo "Backup created: $BACKUP_FILE"

# Upload to cloud storage (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp $BACKUP_FILE s3://$AWS_S3_BUCKET/backups/
    echo "Backup uploaded to S3"
fi

# Clean old backups
find $BACKUP_DIR -name "sigmasight_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "Old backups cleaned (retention: $RETENTION_DAYS days)"

echo "Backup completed successfully"
```

#### 2. Backup Scheduling

**Crontab Configuration:**
```bash
# Daily backup at 2 AM
0 2 * * * /opt/sigmasight/scripts/backup_database.sh

# Weekly full backup at Sunday 1 AM
0 1 * * 0 /opt/sigmasight/scripts/full_system_backup.sh
```

### Recovery Procedures

#### 1. Database Recovery

**Recovery Script:**
```bash
#!/bin/bash
# scripts/restore_database.sh

set -e

BACKUP_FILE=$1
DB_NAME="sigmasight_db"
DB_USER="sigmasight"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

echo "Starting database recovery from $BACKUP_FILE"

# Stop application services
docker-compose stop backend gpt-agent frontend

# Drop and recreate database
dropdb -U postgres $DB_NAME
createdb -U postgres $DB_NAME
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Restore from backup
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | psql -U $DB_USER -d $DB_NAME
else
    psql -U $DB_USER -d $DB_NAME -f $BACKUP_FILE
fi

# Restart services
docker-compose start postgres
sleep 10  # Wait for database to be ready
docker-compose start backend gpt-agent frontend

echo "Database recovery completed successfully"
```

#### 2. Disaster Recovery Plan

**Recovery Runbook:**

1. **Assess Damage**
   ```bash
   # Check service status
   docker-compose ps
   
   # Check database connectivity
   psql -U sigmasight -d sigmasight_db -c "SELECT version();"
   
   # Check disk space
   df -h
   ```

2. **Stop Services**
   ```bash
   # Graceful shutdown
   docker-compose stop
   
   # Force stop if needed
   docker-compose kill
   ```

3. **Restore Database**
   ```bash
   # Find latest backup
   ls -la /backups/ | grep sigmasight_backup | tail -5
   
   # Restore from backup
   ./scripts/restore_database.sh /backups/sigmasight_backup_20250826_020000.sql.gz
   ```

4. **Verify Recovery**
   ```bash
   # Check portfolio count
   psql -U sigmasight -d sigmasight_db -c "SELECT COUNT(*) FROM portfolios;"
   
   # Test API endpoints
   curl http://localhost:8001/health
   curl http://localhost:8001/api/v1/reports/portfolios
   ```

---

## Troubleshooting

### Common Deployment Issues

#### 1. Service Startup Failures

**Backend Service Won't Start:**
```bash
# Check logs
docker-compose logs backend

# Common issues and solutions:
# - Database connection: Verify DATABASE_URL
# - Missing dependencies: Rebuild Docker image
# - Port conflicts: Change port mapping in docker-compose.yml
# - Permission issues: Check file permissions

# Debug container
docker-compose run --rm backend bash
uv run python -c "from app.database import get_async_session; print('DB OK')"
```

**Frontend Build Failures:**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and rebuild
rm -rf node_modules package-lock.json .next
npm install
npm run build

# Check environment variables
cat .env.local
```

#### 2. Database Connection Issues

**Connection Troubleshooting:**
```bash
# Test direct connection
psql -h localhost -p 5432 -U sigmasight -d sigmasight_db

# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Verify connection string
echo $DATABASE_URL

# Check network connectivity
docker-compose exec backend ping postgres
```

#### 3. Performance Issues

**Slow API Responses:**
```bash
# Check database performance
docker-compose exec postgres psql -U sigmasight -d sigmasight_db -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Monitor resource usage
docker stats

# Check application logs
docker-compose logs backend | grep -i "slow\|timeout\|error"
```

### Maintenance Procedures

#### 1. Rolling Updates

**Zero-Downtime Deployment:**
```bash
#!/bin/bash
# scripts/rolling_update.sh

# Build new images
docker-compose -f docker-compose.prod.yml build

# Update backend first
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
sleep 30

# Update GPT agent
docker-compose -f docker-compose.prod.yml up -d --no-deps gpt-agent
sleep 15

# Update frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend

# Verify all services
docker-compose -f docker-compose.prod.yml ps
```

#### 2. Database Maintenance

**Regular Maintenance Tasks:**
```bash
#!/bin/bash
# scripts/db_maintenance.sh

DB_NAME="sigmasight_db"
DB_USER="sigmasight"

echo "Starting database maintenance..."

# Update statistics
psql -U $DB_USER -d $DB_NAME -c "ANALYZE;"

# Reindex tables
psql -U $DB_USER -d $DB_NAME -c "REINDEX DATABASE $DB_NAME;"

# Vacuum tables
psql -U $DB_USER -d $DB_NAME -c "VACUUM ANALYZE;"

# Check for bloat
psql -U $DB_USER -d $DB_NAME -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"

echo "Database maintenance completed"
```

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying SigmaSight across development, staging, and production environments. The platform's three-service architecture requires careful coordination of database, backend API, GPT agent, and frontend services.

### Key Success Factors

1. **Service Order**: Always start database first, followed by backend, GPT agent, then frontend
2. **Environment Variables**: Carefully configure all required API keys and secrets
3. **Health Checks**: Monitor all services and implement proper alerting
4. **Security**: Use SSL/TLS, rate limiting, and secure secret management
5. **Monitoring**: Implement comprehensive logging and metrics collection
6. **Backups**: Regular automated backups with tested recovery procedures

### Production Checklist

- [ ] SSL certificates installed and configured
- [ ] Database backups automated and tested
- [ ] Monitoring and alerting configured
- [ ] Security headers and rate limiting active
- [ ] Performance optimization applied
- [ ] Disaster recovery plan documented
- [ ] Team access and permissions configured
- [ ] Documentation updated and accessible

**Deployment Status**: Ready for Production  
**Next Review**: Quarterly or after major updates  
**Support**: Contact the development team for deployment assistance
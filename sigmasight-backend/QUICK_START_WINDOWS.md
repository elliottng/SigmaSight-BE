# 🚀 SigmaSight Windows Quick Start

## First Time Setup (30 minutes)

### 1. Install Required Software
Download and install in this order:
1. **Python 3.11**: https://python.org/downloads/ (✅ Check "Add to PATH")
2. **Git**: https://git-scm.com/download/win (use all defaults)
3. **Docker Desktop**: https://docker.com/products/docker-desktop/ (restart required)
4. **UV** (in PowerShell Admin): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

### 2. Get the Code
```bash
cd C:\
mkdir Projects
cd Projects
git clone https://github.com/elliottng/SigmaSight-BE.git
cd SigmaSight-BE\sigmasight-backend
```

### 3. Setup Project
```bash
uv venv
uv pip install -r requirements.txt
copy .env.example .env
```

### 4. Start Database
```bash
docker-compose up -d
uv run alembic upgrade head
```

### 5. Run SigmaSight
```bash
uv run python run.py
```
Open browser to: http://localhost:8000/docs

---

## Daily Start/Stop

### Morning - Start Everything
1. Start Docker Desktop (wait for whale icon)
2. Open Command Prompt
3. Run:
```bash
cd C:\Projects\SigmaSight-BE\sigmasight-backend
docker-compose up -d
uv run python run.py
```

### Evening - Stop Everything
1. Press `Ctrl + C` in Command Prompt
2. Run: `docker-compose down`
3. Close Docker Desktop (optional)

---

## Common Issues

| Problem | Solution |
|---------|----------|
| "python not recognized" | Reinstall Python with "Add to PATH" checked |
| "docker not recognized" | Start Docker Desktop and wait for it to fully load |
| "port 8000 in use" | Stop with Ctrl+C and try again |
| Database errors | Run: `docker-compose down` then `docker-compose up -d` |

---

## Important URLs
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

💡 **Tip**: Save this file to your desktop for quick reference!

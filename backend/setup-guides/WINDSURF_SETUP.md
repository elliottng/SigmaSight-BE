# 🌊 Windsurf Setup Guide for SigmaSight Backend

This guide is specifically for setting up the SigmaSight Backend using Windsurf IDE with Cascade AI assistance.

## 🚀 Quick Start with Windsurf

### Step 1: Clone the Repository in Windsurf

1. **Open Windsurf**
2. **Clone Repository:**
   - Use `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Git: Clone"
   - Enter: `https://github.com/elliottng/SigmaSight-BE.git`
   - Choose a local folder to clone into

3. **Open the Backend Project:**
   - Navigate to the cloned folder
   - Open the `backend` folder in Windsurf

### Step 2: Let Cascade AI Help You Set Up

Once you have the project open in Windsurf, you can ask Cascade to help with setup:

**Ask Cascade:**
```
"Please help me set up the SigmaSight backend project for local development. I need to install dependencies and get the server running."
```

**Cascade will help you:**
- Install UV package manager if needed
- Run `uv sync` to install dependencies
- Set up the `.env` file
- Start the development server
- Run verification tests

### Step 3: Automated Setup (Alternative)

If you prefer to run setup manually, use the terminal in Windsurf:

**Mac/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

### Step 4: Verify Everything Works

Ask Cascade to run the verification:
```
"Please run the setup verification script to make sure everything is working correctly."
```

Or run manually:
```bash
uv run python scripts/verify_setup.py
```

## 🤖 Working with Cascade AI

### Useful Cascade Commands for This Project:

**Initial Setup:**
- "Help me set up the SigmaSight backend development environment"
- "Run the verification script to check if everything is working"
- "Start the FastAPI development server"

**Development Tasks:**
- "Show me the current API endpoints and their status"
- "Help me understand the project structure"
- "Run the test suite and show me the results"
- "Generate sample data for testing"

**Troubleshooting:**
- "The server won't start, help me debug the issue"
- "Check if all dependencies are properly installed"
- "Help me fix any configuration issues"

### Project-Specific Context for Cascade:

When working with Cascade, you can reference:
- **Documentation:** All project docs are in `_docs/` folder
- **API Endpoints:** 15 endpoints across 6 modules in `app/api/v1/`
- **Configuration:** Settings in `app/config.py` and `.env` file
- **Testing:** Test suite in `tests/` folder
- **Scripts:** Utility scripts in `scripts/` folder

## 📋 Expected Results

After successful setup, you should have:

✅ **Server Running:** http://localhost:8000  
✅ **API Documentation:** http://localhost:8000/docs  
✅ **Health Check:** http://localhost:8000/health  
✅ **All Tests Passing:** 5/5 tests in the test suite  
✅ **Sample Data Generated:** CSV files and mock data  

## 🔧 Key Files to Know

- **`run.py`** - Start the development server
- **`app/main.py`** - Main FastAPI application
- **`app/config.py`** - Configuration settings
- **`pyproject.toml`** - Dependencies and project metadata
- **`TODO.md`** - Project roadmap and progress
- **`README.md`** - Comprehensive setup guide

## 🐛 Common Issues & Solutions

**Issue: "uv: command not found"**
- Ask Cascade: "Help me install UV package manager"
- Or follow the installation guide in README.md

**Issue: "Port 8000 already in use"**
- Ask Cascade: "Help me find what's using port 8000 and fix it"
- Or change the port in `run.py`

**Issue: Dependencies won't install**
- Ask Cascade: "Help me troubleshoot dependency installation issues"
- Or try: `uv sync --reinstall`

## 🎯 Next Steps

Once setup is complete, you can:

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Run Tests:** Ask Cascade to run the test suite
3. **Generate Data:** Use the sample data generator
4. **Start Development:** Begin implementing Phase 1 features

## 💡 Pro Tips for Windsurf

- **Use Cascade extensively** - It knows the project structure and can help with any task
- **Ask for explanations** - Cascade can explain any part of the codebase
- **Request code reviews** - Cascade can review your changes before committing
- **Get help with debugging** - Cascade can help troubleshoot issues quickly

---

**Need Help?** Just ask Cascade! It has full context of the SigmaSight project and can assist with any development task.

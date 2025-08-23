@echo off
REM SigmaSight Backend Setup Script for Windows
REM This script automates the setup process for new developers

echo 🚀 SigmaSight Backend Setup Script
echo ==================================

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ UV package manager not found
    echo Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo ✅ UV installed successfully
    echo Please restart your command prompt and run this script again
    pause
    exit /b 1
) else (
    echo ✅ UV package manager found
)

REM Install dependencies
echo 📦 Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Set up environment file
if not exist ".env" (
    echo ⚙️  Setting up environment file...
    copy .env.example .env
    echo ✅ Environment file created
) else (
    echo ✅ Environment file already exists
)

REM Run verification
echo 🔍 Running setup verification...
uv run python scripts/verify_setup.py
if %errorlevel% neq 0 (
    echo ❌ Setup verification failed
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo To start the server, run: uv run python run.py
echo API will be available at: http://localhost:8000
pause

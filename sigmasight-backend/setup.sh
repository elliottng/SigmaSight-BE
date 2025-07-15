#!/bin/bash
# SigmaSight Backend Setup Script
# This script automates the setup process for new developers

set -e  # Exit on any error

echo "🚀 SigmaSight Backend Setup Script"
echo "=================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV package manager not found"
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
    echo "✅ UV installed successfully"
else
    echo "✅ UV package manager found"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Set up environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment file..."
    cp .env.example .env
    echo "✅ Environment file created"
else
    echo "✅ Environment file already exists"
fi

# Run verification
echo "🔍 Running setup verification..."
uv run python scripts/verify_setup.py

echo ""
echo "🎉 Setup complete!"
echo "To start the server, run: uv run python run.py"
echo "API will be available at: http://localhost:8000"

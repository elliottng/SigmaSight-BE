#!/usr/bin/env python3
"""
Development server runner for SigmaSight Backend
"""
import os
import sys
import uvicorn

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the backend directory
os.chdir(script_dir)

# Add the backend directory to Python path
sys.path.insert(0, script_dir)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

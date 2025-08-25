#!/usr/bin/env python3
"""
Development server runner for SigmaSight Backend
"""
import os
import sys
import logging
import uvicorn
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the backend directory
os.chdir(script_dir)

# Add the backend directory to Python path
sys.path.insert(0, script_dir)

if __name__ == "__main__":
    try:
        logger.info("Starting server from directory: %s", script_dir)
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        logger.error("Error starting server: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        sys.exit(1)

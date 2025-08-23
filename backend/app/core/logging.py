"""
Logging configuration for SigmaSight Backend
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any

from app.config import settings


def setup_logging() -> None:
    """Configure application logging based on environment"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove default handlers
    root_logger.handlers = []
    
    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "sigmasight.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    
    # Formatters
    if settings.ENVIRONMENT == "production":
        # JSON format for production (easier to parse)
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        formatter = JsonFormatter()
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": logging.INFO,
        "uvicorn.error": logging.INFO,
        "uvicorn.access": logging.WARNING,  # Reduce noise
        "sqlalchemy.engine": logging.WARNING,  # Set to INFO for query logging
        "sigmasight": log_level,
    }
    
    for logger_name, logger_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
    
    # Log startup
    logger = logging.getLogger("sigmasight.startup")
    logger.info(
        f"Logging configured - Environment: {settings.ENVIRONMENT}, Level: {settings.LOG_LEVEL}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with consistent naming"""
    return logging.getLogger(f"sigmasight.{name}")


# Module-specific loggers
api_logger = get_logger("api")
db_logger = get_logger("database")
auth_logger = get_logger("auth")
batch_logger = get_logger("batch")
market_data_logger = get_logger("market_data")

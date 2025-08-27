"""
Configuration settings for SigmaSight Backend
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "SigmaSight Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Market data API keys
    POLYGON_API_KEY: str = Field(..., env="POLYGON_API_KEY")
    POLYGON_PLAN: str = Field(default="free", env="POLYGON_PLAN")  # free, starter, developer, advanced
    FRED_API_KEY: str = Field(default="", env="FRED_API_KEY")  # Optional for Treasury data
    
    # New market data providers (Section 1.4.9)
    FMP_API_KEY: str = Field(default="", env="FMP_API_KEY")  # Financial Modeling Prep
    TRADEFEEDS_API_KEY: str = Field(default="", env="TRADEFEEDS_API_KEY")  # TradeFeeds backup
    
    # Provider selection flags
    USE_FMP_FOR_STOCKS: bool = Field(default=True, env="USE_FMP_FOR_STOCKS")
    USE_FMP_FOR_FUNDS: bool = Field(default=True, env="USE_FMP_FOR_FUNDS") 
    USE_POLYGON_FOR_OPTIONS: bool = Field(default=True, env="USE_POLYGON_FOR_OPTIONS")  # Always true
    
    # Provider-specific settings
    FMP_TIMEOUT_SECONDS: int = Field(default=30, env="FMP_TIMEOUT_SECONDS")
    FMP_MAX_RETRIES: int = Field(default=3, env="FMP_MAX_RETRIES")
    TRADEFEEDS_TIMEOUT_SECONDS: int = Field(default=30, env="TRADEFEEDS_TIMEOUT_SECONDS")
    TRADEFEEDS_MAX_RETRIES: int = Field(default=3, env="TRADEFEEDS_MAX_RETRIES")
    TRADEFEEDS_RATE_LIMIT: int = Field(default=30, env="TRADEFEEDS_RATE_LIMIT")  # calls per minute
    
    
    # JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Next.js dev server (alternate)
        "http://localhost:3002",  # Next.js dev server (current)
        "http://localhost:3008",  # Next.js dev server (current port)
        "http://localhost:5173",  # Vite dev server
        "https://sigmasight-frontend.vercel.app",  # Production frontend
    ]
    
    # Batch processing settings
    BATCH_PROCESSING_ENABLED: bool = True
    MARKET_DATA_UPDATE_INTERVAL: int = 3600  # 1 hour in seconds
    
    # OpenAI integration (optional)
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

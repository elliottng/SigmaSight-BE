"""
Configuration settings for SigmaSight Backend
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "SigmaSight Backend"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Market data API keys
    POLYGON_API_KEY: str = Field(..., env="POLYGON_API_KEY")
    
    # JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://sigmasight-frontend.vercel.app",  # Production frontend
    ]
    
    # Batch processing settings
    BATCH_PROCESSING_ENABLED: bool = True
    MARKET_DATA_UPDATE_INTERVAL: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
